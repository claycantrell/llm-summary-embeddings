#!/usr/bin/env python3
"""
Main experiment: Compare clustering quality of raw complaint embeddings
vs. LLM-summarized complaint embeddings.

Conditions:
  A) Embed raw complaint text -> cluster -> measure quality
  B) Summarize each complaint with Claude -> embed summary -> cluster -> measure quality

Metrics: V-measure, Adjusted Rand Index, Silhouette Score
Clustering: KMeans with k = number of ground truth product categories

Usage:
    python scripts/run_experiment.py
"""

import os
import sys
import json
import time
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import (
    v_measure_score,
    adjusted_rand_score,
    silhouette_score,
)
from sklearn.preprocessing import LabelEncoder

# ── Paths ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
CACHE_DIR = REPO_ROOT / "cache"
SAMPLE_CSV = DATA_DIR / "amazon_dataset.csv"

# Cache files
SUMMARIES_CACHE = CACHE_DIR / "summaries.json"

# ── Config ───────────────────────────────────────────────────────────────
SUMMARY_MODEL = "claude-haiku-4-5-20251001"

EMBEDDING_MODELS = [
    {
        "name": "all-MiniLM-L6-v2",
        "hf_name": "sentence-transformers/all-MiniLM-L6-v2",
        "dims": 384,
        "max_tokens": 256,
        "trust_remote_code": False,
    },
    {
        "name": "bge-base-en-v1.5",
        "hf_name": "BAAI/bge-base-en-v1.5",
        "dims": 768,
        "max_tokens": 512,
        "trust_remote_code": False,
    },
    {
        "name": "nomic-embed-text-v1.5",
        "hf_name": "nomic-ai/nomic-embed-text-v1.5",
        "dims": 768,
        "max_tokens": 8192,
        "trust_remote_code": True,
    },
]

EMBEDDING_BATCH_SIZE = 64
SUMMARY_BATCH_SIZE = 20  # complaints per API call
KMEANS_RANDOM_STATE = 42
MAX_RETRIES = 5
BASE_DELAY = 1.0  # seconds, for exponential backoff

# Truncate very long complaints to stay within token limits
MAX_COMPLAINT_CHARS = 8000  # ~2000 tokens


def load_env():
    """Load environment variables from .env file."""
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found.")
        print(f"Set it in your environment or create a .env file at {env_path} with:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    return api_key


def compute_texts_hash(texts: list[str]) -> str:
    """Compute a hash of a list of texts for cache validation."""
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8"))
    return h.hexdigest()


def api_call_with_retry(func, *args, **kwargs):
    """Call an API function with exponential backoff on rate limit errors."""
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = "rate" in error_str or "429" in error_str or "too many" in error_str
            is_server_error = "500" in error_str or "502" in error_str or "503" in error_str or "overloaded" in error_str

            if is_rate_limit or is_server_error:
                delay = BASE_DELAY * (2 ** attempt)
                print(f"  Rate limit/server error (attempt {attempt + 1}/{MAX_RETRIES}). "
                      f"Retrying in {delay:.1f}s...")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError(f"Failed after {MAX_RETRIES} retries")


# ── Summarization ────────────────────────────────────────────────────────

SUMMARY_TOOL = {
    "name": "submit_summaries",
    "description": "Submit one-line summaries for a batch of consumer complaints.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summaries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "integer",
                            "description": "The complaint number (matching the input order)",
                        },
                        "summary": {
                            "type": "string",
                            "description": "One-sentence summary of the core issue (max 30 words)",
                        },
                    },
                    "required": ["index", "summary"],
                },
            },
        },
        "required": ["summaries"],
    },
}


def generate_summaries(client: Anthropic, texts: list[str]) -> list[str]:
    """
    Generate one-line summaries in batches of SUMMARY_BATCH_SIZE using Claude
    with structured tool-use output. Results cached to disk with resume support.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Check cache — supports resuming from partial progress
    summaries = []
    if SUMMARIES_CACHE.exists():
        with open(SUMMARIES_CACHE, "r") as f:
            cached = json.load(f)
        if len(cached) == len(texts):
            print(f"[CACHE] Loaded {len(cached)} summaries from cache.")
            return cached
        elif len(cached) < len(texts):
            summaries = cached
            print(f"[CACHE] Resuming from {len(cached)}/{len(texts)} cached summaries.")

    remaining = len(texts) - len(summaries)
    n_batches = (remaining + SUMMARY_BATCH_SIZE - 1) // SUMMARY_BATCH_SIZE
    print(f"\nGenerating summaries for {remaining} complaints using {SUMMARY_MODEL}...")
    print(f"  ({n_batches} batched API calls, {SUMMARY_BATCH_SIZE} complaints per call)")

    system_prompt = (
        "You are a product review analyst. For each numbered one-star review, produce a single "
        "concise sentence (max 20 words) summarizing the core complaint. Focus on: what specifically "
        "went wrong with the product? Use the submit_summaries tool to return all summaries at once."
    )

    start_idx = len(summaries)
    for batch_start in range(start_idx, len(texts), SUMMARY_BATCH_SIZE):
        batch_end = min(batch_start + SUMMARY_BATCH_SIZE, len(texts))
        batch_texts = texts[batch_start:batch_end]

        # Format the batch as numbered complaints
        numbered = []
        for j, text in enumerate(batch_texts):
            truncated = text[:MAX_COMPLAINT_CHARS] if len(text) > MAX_COMPLAINT_CHARS else text
            numbered.append(f"COMPLAINT {j + 1}:\n{truncated}")
        user_message = "\n\n---\n\n".join(numbered)

        response = api_call_with_retry(
            client.messages.create,
            model=SUMMARY_MODEL,
            max_tokens=2048,
            system=system_prompt,
            tools=[SUMMARY_TOOL],
            tool_choice={"type": "tool", "name": "submit_summaries"},
            messages=[
                {"role": "user", "content": user_message},
            ],
        )

        # Extract structured summaries from tool use response
        tool_block = next(
            (block for block in response.content if block.type == "tool_use"),
            None,
        )
        if tool_block is None:
            raise RuntimeError(f"No tool_use block in response for batch starting at {batch_start}")

        batch_summaries_raw = tool_block.input.get("summaries", [])

        # Handle case where model returns unexpected format
        if isinstance(batch_summaries_raw, str):
            # Model returned a string instead of array — skip this batch
            print(f"  WARNING: Got string instead of array at batch {batch_start}, using raw texts")
            batch_summaries = [t[:100] for t in batch_texts]
        else:
            # Sort by index and extract summary text
            batch_summaries_raw.sort(key=lambda x: x.get("index", 0) if isinstance(x, dict) else 0)
            batch_summaries = [
                item["summary"] if isinstance(item, dict) else str(item)
                for item in batch_summaries_raw
            ]

        # Sanity check: if we got fewer than expected, pad with fallback
        if len(batch_summaries) < len(batch_texts):
            print(f"  WARNING: Expected {len(batch_texts)} summaries, got {len(batch_summaries)}. "
                  f"Padding with empty strings.")
            batch_summaries.extend(["[summary unavailable]"] * (len(batch_texts) - len(batch_summaries)))

        summaries.extend(batch_summaries[:len(batch_texts)])

        print(f"  Summarized {min(batch_end, len(texts))}/{len(texts)}")

        # Save incrementally after each batch
        with open(SUMMARIES_CACHE, "w") as f:
            json.dump(summaries, f)

    print(f"[OK] Generated and cached {len(summaries)} summaries.")
    return summaries


# ── Embeddings ───────────────────────────────────────────────────────────

def load_embedding_model(model_config: dict) -> SentenceTransformer:
    """Load a sentence-transformers embedding model."""
    name = model_config["hf_name"]
    print(f"\nLoading embedding model: {name}...")
    model = SentenceTransformer(name, trust_remote_code=model_config.get("trust_remote_code", False))
    print(f"  Loaded. dim={model.get_sentence_embedding_dimension()}, max_seq={model.max_seq_length}")
    return model


def generate_embeddings(
    model: SentenceTransformer,
    texts: list[str],
    cache_path: Path,
    hash_cache_path: Path,
    label: str,
) -> np.ndarray:
    """
    Generate embeddings using a local sentence-transformer model.
    Results are cached to disk with hash validation.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    texts_hash = compute_texts_hash(texts)

    # Check cache
    if cache_path.exists() and hash_cache_path.exists():
        cached_hash = hash_cache_path.read_text().strip()
        if cached_hash == texts_hash:
            embeddings = np.load(cache_path)
            if embeddings.shape[0] == len(texts):
                print(f"[CACHE] Loaded {label} embeddings from cache ({embeddings.shape}).")
                return embeddings

    print(f"\nGenerating {label} embeddings for {len(texts)} texts...")

    processed = [t[:MAX_COMPLAINT_CHARS] if len(t) > MAX_COMPLAINT_CHARS else t for t in texts]

    # Use smaller batches for long texts to avoid OOM
    max_text_len = max(len(t) for t in processed)
    batch_size = EMBEDDING_BATCH_SIZE if max_text_len < 1000 else 8

    embeddings = model.encode(
        processed,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    embeddings = embeddings.astype(np.float32)

    np.save(cache_path, embeddings)
    hash_cache_path.write_text(texts_hash)

    print(f"[OK] Generated and cached {label} embeddings ({embeddings.shape}).")
    return embeddings


# ── Clustering & Evaluation ──────────────────────────────────────────────

N_BOOTSTRAP = 100
BOOTSTRAP_SAMPLE_FRAC = 0.8  # 80% subsample each iteration


def cluster_and_evaluate(
    embeddings: np.ndarray,
    true_labels: np.ndarray,
    n_clusters: int,
    condition_name: str,
) -> dict:
    """
    Run KMeans clustering and evaluate against ground truth labels.
    Returns a dict of metrics and the cluster assignments.
    """
    print(f"\nClustering: {condition_name}")
    print(f"  KMeans with k={n_clusters}, data shape={embeddings.shape}")

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=KMEANS_RANDOM_STATE,
        n_init=10,
        max_iter=300,
    )
    cluster_labels = kmeans.fit_predict(embeddings)

    v_measure = v_measure_score(true_labels, cluster_labels)
    ari = adjusted_rand_score(true_labels, cluster_labels)
    silhouette = silhouette_score(embeddings, cluster_labels, sample_size=min(1000, len(embeddings)))

    metrics = {
        "condition": condition_name,
        "v_measure": v_measure,
        "adjusted_rand_index": ari,
        "silhouette_score": silhouette,
    }

    print(f"  V-measure:            {v_measure:.4f}")
    print(f"  Adjusted Rand Index:  {ari:.4f}")
    print(f"  Silhouette Score:     {silhouette:.4f}")

    return metrics, cluster_labels


def bootstrap_compare(
    raw_embeddings: np.ndarray,
    summary_embeddings: np.ndarray,
    true_labels: np.ndarray,
    n_clusters: int,
    label_name: str,
) -> dict:
    """
    Bootstrap significance test: resample data N_BOOTSTRAP times,
    cluster both conditions on each subsample, compute paired deltas.
    Returns distributions and p-values.
    """
    n = len(true_labels)
    sample_size = int(n * BOOTSTRAP_SAMPLE_FRAC)
    rng = np.random.RandomState(42)

    deltas_v = []
    deltas_ari = []
    raw_vs = []
    sum_vs = []
    raw_aris = []
    sum_aris = []

    print(f"\n  Bootstrap ({N_BOOTSTRAP} iterations, {sample_size}/{n} samples each)...")

    for i in range(N_BOOTSTRAP):
        idx = rng.choice(n, size=sample_size, replace=True)
        raw_sub = raw_embeddings[idx]
        sum_sub = summary_embeddings[idx]
        labels_sub = true_labels[idx]

        # Check we have enough unique labels for k clusters
        n_unique = len(np.unique(labels_sub))
        k = min(n_clusters, n_unique)

        km_raw = KMeans(n_clusters=k, random_state=i, n_init=5, max_iter=200)
        km_sum = KMeans(n_clusters=k, random_state=i, n_init=5, max_iter=200)

        raw_cl = km_raw.fit_predict(raw_sub)
        sum_cl = km_sum.fit_predict(sum_sub)

        rv = v_measure_score(labels_sub, raw_cl)
        sv = v_measure_score(labels_sub, sum_cl)
        ra = adjusted_rand_score(labels_sub, raw_cl)
        sa = adjusted_rand_score(labels_sub, sum_cl)

        raw_vs.append(rv)
        sum_vs.append(sv)
        raw_aris.append(ra)
        sum_aris.append(sa)
        deltas_v.append(sv - rv)
        deltas_ari.append(sa - ra)

    deltas_v = np.array(deltas_v)
    deltas_ari = np.array(deltas_ari)

    # p-value: fraction of bootstrap iterations where delta <= 0
    # (one-sided test: is summary significantly BETTER?)
    p_v = np.mean(deltas_v <= 0)
    p_ari = np.mean(deltas_ari <= 0)

    # Confidence intervals (95%)
    ci_v = (np.percentile(deltas_v, 2.5), np.percentile(deltas_v, 97.5))
    ci_ari = (np.percentile(deltas_ari, 2.5), np.percentile(deltas_ari, 97.5))

    print(f"  V-measure delta:  mean={np.mean(deltas_v):+.4f}  "
          f"95% CI=[{ci_v[0]:+.4f}, {ci_v[1]:+.4f}]  p={p_v:.4f}")
    print(f"  ARI delta:        mean={np.mean(deltas_ari):+.4f}  "
          f"95% CI=[{ci_ari[0]:+.4f}, {ci_ari[1]:+.4f}]  p={p_ari:.4f}")

    sig_v = "YES" if p_v < 0.05 else "no"
    sig_ari = "YES" if p_ari < 0.05 else "no"
    print(f"  Significant at p<0.05?  V-measure: {sig_v}   ARI: {sig_ari}")

    return {
        "label_type": label_name,
        "n_bootstrap": N_BOOTSTRAP,
        "sample_frac": BOOTSTRAP_SAMPLE_FRAC,
        "v_measure": {
            "mean_delta": float(np.mean(deltas_v)),
            "ci_95": [float(ci_v[0]), float(ci_v[1])],
            "p_value": float(p_v),
            "significant": bool(p_v < 0.05),
            "raw_mean": float(np.mean(raw_vs)),
            "summary_mean": float(np.mean(sum_vs)),
        },
        "ari": {
            "mean_delta": float(np.mean(deltas_ari)),
            "ci_95": [float(ci_ari[0]), float(ci_ari[1])],
            "p_value": float(p_ari),
            "significant": bool(p_ari < 0.05),
            "raw_mean": float(np.mean(raw_aris)),
            "summary_mean": float(np.mean(sum_aris)),
        },
    }


# ── Results Display ──────────────────────────────────────────────────────

def print_comparison(label_type: str, n_categories: int, raw_metrics: dict, summary_metrics: dict):
    """Print a comparison table for one label type."""
    print(f"\n  --- Evaluated against: {label_type} ({n_categories} categories) ---")
    print()
    header = f"  {'Metric':<28} {'Raw Text':<15} {'Summary':<15} {'Delta':<15}"
    print(header)
    print("  " + "-" * 68)

    metric_names = {
        "v_measure": "V-Measure",
        "adjusted_rand_index": "Adjusted Rand Index",
        "silhouette_score": "Silhouette Score",
    }

    for key, display_name in metric_names.items():
        raw_val = raw_metrics[key]
        sum_val = summary_metrics[key]
        delta = sum_val - raw_val
        delta_str = f"{delta:+.4f}"
        if delta > 0.005:
            delta_str += " !!!"
        elif delta < -0.005:
            delta_str += ""
        print(f"  {display_name:<28} {raw_val:<15.4f} {sum_val:<15.4f} {delta_str}")

    print("  " + "-" * 68)


# ── Main ─────────────────────────────────────────────────────────────────

def run_model_experiment(
    model_config: dict,
    raw_texts: list[str],
    summaries: list[str],
    issue_labels: np.ndarray,
    product_labels: np.ndarray,
    n_issues: int,
    n_products: int,
) -> dict:
    """Run the full experiment for a single embedding model."""
    model_name = model_config["name"]
    print("\n" + "#" * 70)
    print(f"  EMBEDDING MODEL: {model_name}")
    print(f"  dims={model_config['dims']}, max_tokens={model_config['max_tokens']}")
    print("#" * 70)

    embed_model = load_embedding_model(model_config)

    # Cache paths per model
    raw_cache = CACHE_DIR / f"embeddings_raw_{model_name}.npy"
    raw_hash = CACHE_DIR / f"raw_texts_hash_{model_name}.txt"
    sum_cache = CACHE_DIR / f"embeddings_summary_{model_name}.npy"
    sum_hash = CACHE_DIR / f"summary_texts_hash_{model_name}.txt"

    raw_embeddings = generate_embeddings(
        embed_model, raw_texts, raw_cache, raw_hash, f"raw ({model_name})")
    summary_embeddings = generate_embeddings(
        embed_model, summaries, sum_cache, sum_hash, f"summary ({model_name})")

    # Free model memory
    del embed_model

    # Cluster and evaluate against both label schemes
    raw_issue, _ = cluster_and_evaluate(
        raw_embeddings, issue_labels, n_issues, f"Raw-issue ({model_name})")
    sum_issue, _ = cluster_and_evaluate(
        summary_embeddings, issue_labels, n_issues, f"Sum-issue ({model_name})")

    raw_prod, _ = cluster_and_evaluate(
        raw_embeddings, product_labels, n_products, f"Raw-prod ({model_name})")
    sum_prod, _ = cluster_and_evaluate(
        summary_embeddings, product_labels, n_products, f"Sum-prod ({model_name})")

    # Bootstrap significance
    print(f"\n  Bootstrap — Issue labels:")
    boot_issue = bootstrap_compare(
        raw_embeddings, summary_embeddings, issue_labels, n_issues, "issue")
    print(f"\n  Bootstrap — Product labels:")
    boot_product = bootstrap_compare(
        raw_embeddings, summary_embeddings, product_labels, n_products, "product")

    return {
        "model": model_name,
        "max_tokens": model_config["max_tokens"],
        "dims": model_config["dims"],
        "issue": {"raw": raw_issue, "summary": sum_issue, "bootstrap": boot_issue},
        "product": {"raw": raw_prod, "summary": sum_prod, "bootstrap": boot_product},
    }


def main():
    print("=" * 70)
    print("LLM Summary Embeddings — App Reviews Experiment")
    print("Can summaries surface the review type from noisy informal text?")
    print("=" * 70)

    # Load API key
    api_key = load_env()
    client = Anthropic(api_key=api_key)

    # Load data
    if not SAMPLE_CSV.exists():
        print(f"\nSample data not found at {SAMPLE_CSV}")
        print("Run the download script first:")
        print("  python scripts/download_data.py")
        sys.exit(1)

    print(f"\nLoading sample data from {SAMPLE_CSV}...")
    df = pd.read_csv(SAMPLE_CSV)
    print(f"  Loaded {len(df)} reviews, {df['label'].nunique()} categories")

    raw_texts = df["text"].tolist()

    # Encode labels
    le = LabelEncoder()
    true_labels = le.fit_transform(df["label"].tolist())
    n_categories = len(le.classes_)

    print(f"\nCategories ({n_categories}):")
    for i, cat in enumerate(le.classes_):
        count = sum(1 for l in true_labels if l == i)
        print(f"  {i}: {cat} ({count})")

    # Generate summaries (shared across all embedding models)
    summaries = generate_summaries(client, raw_texts)

    print("\nExample summaries (first 5):")
    for i in range(min(5, len(summaries))):
        print(f"  [{df.iloc[i]['label']}]")
        print(f"    Raw:     {raw_texts[i][:120]}...")
        print(f"    Summary: {summaries[i]}")
        print()

    # Single evaluation slice — all reviews, cluster by label
    slices = [{
        "name": "All Reviews",
        "indices": list(range(len(df))),
        "labels": true_labels,
        "n_clusters": n_categories,
        "label_names": le.classes_.tolist(),
    }]

    # ── Run for each embedding model ─────────────────────────────────
    all_results = []

    for model_config in EMBEDDING_MODELS:
        model_name = model_config["name"]
        print("\n" + "#" * 70)
        print(f"  EMBEDDING MODEL: {model_name}")
        print(f"  dims={model_config['dims']}, max_tokens={model_config['max_tokens']}")
        print("#" * 70)

        embed_model = load_embedding_model(model_config)

        raw_cache = CACHE_DIR / f"embeddings_raw_{model_name}.npy"
        raw_hash = CACHE_DIR / f"raw_texts_hash_{model_name}.txt"
        sum_cache = CACHE_DIR / f"embeddings_summary_{model_name}.npy"
        sum_hash = CACHE_DIR / f"summary_texts_hash_{model_name}.txt"

        raw_embeddings = generate_embeddings(
            embed_model, raw_texts, raw_cache, raw_hash, f"raw ({model_name})")
        summary_embeddings = generate_embeddings(
            embed_model, summaries, sum_cache, sum_hash, f"summary ({model_name})")

        del embed_model

        model_results = {"model": model_name, "max_tokens": model_config["max_tokens"],
                         "dims": model_config["dims"], "slices": []}

        for sl in slices:
            idx = sl["indices"]
            raw_sub = raw_embeddings[idx]
            sum_sub = summary_embeddings[idx]
            labels = sl["labels"]
            k = sl["n_clusters"]

            print(f"\n  --- {sl['name']} ({len(idx)} docs, {k} issue clusters) ---")

            raw_m, _ = cluster_and_evaluate(raw_sub, labels, k, f"Raw")
            sum_m, _ = cluster_and_evaluate(sum_sub, labels, k, f"Summary")

            boot = bootstrap_compare(raw_sub, sum_sub, labels, k, sl["name"])

            model_results["slices"].append({
                "name": sl["name"],
                "n_docs": len(idx),
                "n_clusters": k,
                "raw": raw_m,
                "summary": sum_m,
                "bootstrap": boot,
            })

        all_results.append(model_results)

    # ── Combined results table ───────────────────────────────────────
    print("\n" + "=" * 90)
    print("COMBINED RESULTS — WITHIN-CATEGORY ISSUE CLUSTERING")
    print("=" * 90)
    print()
    print(f"  Task: Find latent complaint type within same-product complaints")
    print(f"  Summary model: {SUMMARY_MODEL}")
    print(f"  Bootstrap: {N_BOOTSTRAP} iterations, {BOOTSTRAP_SAMPLE_FRAC:.0%} subsample")
    print()

    for sl_idx, sl in enumerate(slices):
        print(f"  {sl['name']} ({len(sl['indices'])} docs, {sl['n_clusters']} issues)")
        print()
        header = f"    {'Model':<25} {'Raw V':<8} {'Sum V':<8} {'Delta':<10} {'95% CI':<22} {'p':<8} {'Sig?':<5}"
        print(header)
        print("    " + "-" * 80)
        for mr in all_results:
            s = mr["slices"][sl_idx]
            rv = s["raw"]["v_measure"]
            sv = s["summary"]["v_measure"]
            d = sv - rv
            ci = s["bootstrap"]["v_measure"]["ci_95"]
            p = s["bootstrap"]["v_measure"]["p_value"]
            sig = "YES" if s["bootstrap"]["v_measure"]["significant"] else "no"
            print(f"    {mr['model']:<25} {rv:<8.4f} {sv:<8.4f} {d:<+10.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}]  {p:<8.4f} {sig}")
        print()

    print("=" * 90)

    # ── Save results ─────────────────────────────────────────────────
    results_path = DATA_DIR / "experiment_results.json"
    with open(results_path, "w") as f:
        json.dump({"models": all_results, "config": {
            "summary_model": SUMMARY_MODEL,
            "n_bootstrap": N_BOOTSTRAP,
            "bootstrap_sample_frac": BOOTSTRAP_SAMPLE_FRAC,
        }}, f, indent=2)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
