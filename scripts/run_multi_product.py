#!/usr/bin/env python3
"""
Run the full pipeline for multiple products:
  1. Discover taxonomy
  2. Label reviews
  3. Build dataset
  4. Summarize
  5. Embed (all 3 models)
  6. Cluster + bootstrap
"""

import os
import sys
import json
import time
import hashlib
import random
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import v_measure_score, adjusted_rand_score, silhouette_score
from sklearn.preprocessing import LabelEncoder

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
CACHE_DIR = REPO_ROOT / "cache"

SUMMARY_MODEL = "claude-haiku-4-5-20251001"
MAX_RETRIES = 5
BASE_DELAY = 1.0
RANDOM_SEED = 42
N_BOOTSTRAP = 100
BOOTSTRAP_FRAC = 0.8
KMEANS_SEED = 42
MAX_PER_CAT = 100
MIN_PER_CAT = 30

EMBEDDING_MODELS = [
    {"name": "all-MiniLM-L6-v2", "hf_name": "sentence-transformers/all-MiniLM-L6-v2",
     "dims": 384, "max_tokens": 256, "trust_remote_code": False},
    {"name": "bge-base-en-v1.5", "hf_name": "BAAI/bge-base-en-v1.5",
     "dims": 768, "max_tokens": 512, "trust_remote_code": False},
    {"name": "nomic-embed-text-v1.5", "hf_name": "nomic-ai/nomic-embed-text-v1.5",
     "dims": 768, "max_tokens": 8192, "trust_remote_code": True},
]

PRODUCTS = [
    {"name": "Fitbit Charge", "slug": "fitbit_charge", "pool": "fitbit_charge_pool.json"},
    {"name": "Senso Bluetooth Headphones", "slug": "senso_bt", "pool": "senso_bluetooth_headphones_pool.json"},
]

SUMMARY_TOOL = {
    "name": "submit_summaries",
    "description": "Submit summaries for a batch of reviews.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summaries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "summary": {"type": "string"},
                    },
                    "required": ["index", "summary"],
                },
            },
        },
        "required": ["summaries"],
    },
}

LABEL_TOOL = {
    "name": "submit_labels",
    "description": "Submit category labels for a batch of reviews.",
    "input_schema": {
        "type": "object",
        "properties": {
            "labels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "category": {"type": "string"},
                        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    },
                    "required": ["index", "category", "confidence"],
                },
            },
        },
        "required": ["labels"],
    },
}


def load_env():
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found.")
        sys.exit(1)
    return api_key


def api_call(client, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return client.messages.create(**kwargs)
        except Exception as e:
            err = str(e).lower()
            if any(x in err for x in ["rate", "429", "500", "502", "503", "overloaded"]):
                delay = BASE_DELAY * (2 ** attempt)
                print(f"    Retry in {delay:.0f}s...")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError("Max retries exceeded")


def discover_taxonomy(client, reviews, cache_path):
    if cache_path.exists():
        with open(cache_path) as f:
            tax = json.load(f)
        print(f"  [CACHE] Taxonomy: {len(tax)} categories")
        return tax

    random.seed(RANDOM_SEED)
    sample = random.sample(reviews, min(200, len(reviews)))

    all_cats = []
    for i in range(0, len(sample), 50):
        batch = sample[i:i+50]
        numbered = "\n\n".join(f"REVIEW {j+1}: {r['text'][:500]}" for j, r in enumerate(batch))
        resp = api_call(client, model=SUMMARY_MODEL, max_tokens=1024,
            system="Analyze these product reviews and identify 8-15 distinct complaint categories. "
                   "Each describes WHY the customer is unhappy. Return ONLY a JSON array of short labels.",
            messages=[{"role": "user", "content": numbered}])
        text = resp.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        try:
            all_cats.extend(json.loads(text))
        except:
            pass

    # Merge duplicates
    resp = api_call(client, model=SUMMARY_MODEL, max_tokens=1024,
        system="Merge these complaint categories into 8-12 clean, distinct categories. "
               "Return ONLY a JSON array.",
        messages=[{"role": "user", "content": json.dumps(all_cats)}])
    text = resp.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    taxonomy = json.loads(text)

    with open(cache_path, "w") as f:
        json.dump(taxonomy, f, indent=2)
    print(f"  Taxonomy: {len(taxonomy)} categories")
    for c in taxonomy:
        print(f"    - {c}")
    return taxonomy


def label_reviews(client, reviews, taxonomy, cache_path):
    if cache_path.exists():
        with open(cache_path) as f:
            labeled = json.load(f)
        print(f"  [CACHE] {len(labeled)} labeled reviews")
        return labeled

    random.seed(RANDOM_SEED + 1)
    pool = random.sample(reviews, min(len(reviews), len(reviews)))
    tax_str = "\n".join(f"  - {c}" for c in taxonomy)
    labeled = []

    for i in range(0, len(pool), 50):
        batch = pool[i:i+50]
        numbered = "\n\n".join(f"REVIEW {j+1}: {r['text'][:500]}" for j, r in enumerate(batch))
        resp = api_call(client, model=SUMMARY_MODEL, max_tokens=4096,
            system=f"Label each review with one category:\n{tax_str}\nUse submit_labels tool.",
            tools=[LABEL_TOOL], tool_choice={"type": "tool", "name": "submit_labels"},
            messages=[{"role": "user", "content": numbered}])
        tb = next((b for b in resp.content if b.type == "tool_use"), None)
        if not tb:
            continue
        batch_labels = tb.input.get("labels", [])
        if isinstance(batch_labels, str):
            continue
        batch_labels.sort(key=lambda x: x.get("index", 0) if isinstance(x, dict) else 0)
        for j, r in enumerate(batch):
            entry = next((l for l in batch_labels if isinstance(l, dict) and l.get("index") == j+1), None)
            if entry:
                labeled.append({"text": r["text"], "category": entry["category"],
                                "confidence": entry.get("confidence", "medium")})
        if (i + 50) % 200 == 0:
            print(f"    Labeled {min(i+50, len(pool))}/{len(pool)}")

    with open(cache_path, "w") as f:
        json.dump(labeled, f)
    print(f"  Labeled {len(labeled)} reviews")
    return labeled


def build_dataset(labeled, taxonomy):
    df = pd.DataFrame(labeled)
    df = df[df["confidence"].isin(["high", "medium"])]
    df = df[df["category"] != "unknown"]
    df = df.rename(columns={"category": "label"})

    counts = df["label"].value_counts()
    keep = counts[counts >= MIN_PER_CAT].index.tolist()

    sampled = []
    for cat in keep:
        subset = df[df["label"] == cat]
        n = min(MAX_PER_CAT, len(subset))
        sampled.append(subset.sample(n=n, random_state=RANDOM_SEED))

    final = pd.concat(sampled, ignore_index=True)
    final = final.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    final = final[["text", "label"]]
    return final


def summarize_batch(client, texts, cache_path):
    if cache_path.exists():
        with open(cache_path) as f:
            cached = json.load(f)
        if len(cached) == len(texts):
            print(f"  [CACHE] {len(cached)} summaries")
            return cached

    summaries = []
    for i in range(0, len(texts), 20):
        batch = texts[i:i+20]
        numbered = "\n\n---\n\n".join(f"REVIEW {j+1}: {t[:500]}" for j, t in enumerate(batch))
        resp = api_call(client, model=SUMMARY_MODEL, max_tokens=2048,
            system="For each review, produce a single sentence (max 20 words) summarizing the core complaint. "
                   "Use the submit_summaries tool.",
            tools=[SUMMARY_TOOL], tool_choice={"type": "tool", "name": "submit_summaries"},
            messages=[{"role": "user", "content": numbered}])
        tb = next((b for b in resp.content if b.type == "tool_use"), None)
        if tb:
            raw = tb.input.get("summaries", [])
            if isinstance(raw, list):
                raw.sort(key=lambda x: x.get("index", 0) if isinstance(x, dict) else 0)
                for item in raw:
                    summaries.append(item["summary"] if isinstance(item, dict) else str(item))
            else:
                summaries.extend([t[:80] for t in batch])
        else:
            summaries.extend([t[:80] for t in batch])

    # Pad if needed
    while len(summaries) < len(texts):
        summaries.append("[unavailable]")
    summaries = summaries[:len(texts)]

    with open(cache_path, "w") as f:
        json.dump(summaries, f)
    print(f"  Generated {len(summaries)} summaries")
    return summaries


def embed(model, texts, cache_path):
    if cache_path.exists():
        emb = np.load(cache_path)
        if emb.shape[0] == len(texts):
            return emb
    max_len = max(len(t) for t in texts)
    bs = 64 if max_len < 1000 else 8
    emb = model.encode(texts, batch_size=bs, show_progress_bar=False, convert_to_numpy=True).astype(np.float32)
    np.save(cache_path, emb)
    return emb


def bootstrap(raw_emb, sum_emb, labels, k):
    n = len(labels)
    ss = int(n * BOOTSTRAP_FRAC)
    rng = np.random.RandomState(42)
    deltas_v, deltas_a = [], []
    for i in range(N_BOOTSTRAP):
        idx = rng.choice(n, size=ss, replace=True)
        ku = min(k, len(np.unique(labels[idx])))
        rc = KMeans(n_clusters=ku, random_state=i, n_init=5, max_iter=200).fit_predict(raw_emb[idx])
        sc = KMeans(n_clusters=ku, random_state=i, n_init=5, max_iter=200).fit_predict(sum_emb[idx])
        deltas_v.append(v_measure_score(labels[idx], sc) - v_measure_score(labels[idx], rc))
        deltas_a.append(adjusted_rand_score(labels[idx], sc) - adjusted_rand_score(labels[idx], rc))
    dv, da = np.array(deltas_v), np.array(deltas_a)
    return {
        "v_mean_delta": float(np.mean(dv)),
        "v_ci": [float(np.percentile(dv, 2.5)), float(np.percentile(dv, 97.5))],
        "v_p": float(np.mean(dv <= 0)),
        "ari_mean_delta": float(np.mean(da)),
        "ari_p": float(np.mean(da <= 0)),
    }


def run_product(client, product):
    name = product["name"]
    slug = product["slug"]
    pool_path = DATA_DIR / product["pool"]

    print(f"\n{'#'*70}")
    print(f"  PRODUCT: {name}")
    print(f"{'#'*70}")

    with open(pool_path) as f:
        reviews = json.load(f)
    print(f"  Pool: {len(reviews)} reviews")

    # Phase 1: Taxonomy
    tax_path = DATA_DIR / f"{slug}_taxonomy.json"
    taxonomy = discover_taxonomy(client, reviews, tax_path)

    # Phase 2: Label
    label_path = DATA_DIR / f"{slug}_labeled.json"
    labeled = label_reviews(client, reviews, taxonomy, label_path)

    # Phase 3: Build dataset
    df = build_dataset(labeled, taxonomy)
    csv_path = DATA_DIR / f"{slug}_dataset.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  Dataset: {len(df)} reviews, {df['label'].nunique()} categories")
    print(df["label"].value_counts().to_string())

    # Phase 4: Summarize
    texts = df["text"].tolist()
    sum_cache = CACHE_DIR / f"{slug}_summaries.json"
    summaries = summarize_batch(client, texts, sum_cache)

    # Phase 5-6: Embed + Cluster for each model
    le = LabelEncoder()
    labels = le.fit_transform(df["label"].tolist())
    k = len(le.classes_)

    results = []
    for mc in EMBEDDING_MODELS:
        mn = mc["name"]
        print(f"\n  Model: {mn}")
        model = SentenceTransformer(mc["hf_name"], trust_remote_code=mc.get("trust_remote_code", False))

        raw_emb = embed(model, texts, CACHE_DIR / f"{slug}_raw_{mn}.npy")
        sum_emb = embed(model, summaries, CACHE_DIR / f"{slug}_sum_{mn}.npy")
        del model

        raw_cl = KMeans(n_clusters=k, random_state=KMEANS_SEED, n_init=10).fit_predict(raw_emb)
        sum_cl = KMeans(n_clusters=k, random_state=KMEANS_SEED, n_init=10).fit_predict(sum_emb)

        rv = v_measure_score(labels, raw_cl)
        sv = v_measure_score(labels, sum_cl)
        ra = adjusted_rand_score(labels, raw_cl)
        sa = adjusted_rand_score(labels, sum_cl)

        boot = bootstrap(raw_emb, sum_emb, labels, k)

        print(f"    Raw V={rv:.4f}  Sum V={sv:.4f}  Delta={sv-rv:+.4f}  p={boot['v_p']:.4f}")
        results.append({"model": mn, "raw_v": rv, "sum_v": sv, "raw_ari": ra, "sum_ari": sa, "boot": boot})

    return {"product": name, "n_reviews": len(df), "n_categories": k,
            "categories": le.classes_.tolist(), "results": results}


def main():
    print("=" * 70)
    print("Multi-Product Experiment")
    print("=" * 70)

    api_key = load_env()
    client = Anthropic(api_key=api_key)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    all_products = []
    for product in PRODUCTS:
        result = run_product(client, product)
        all_products.append(result)

    # Combined table
    print("\n" + "=" * 90)
    print("COMBINED RESULTS — ALL PRODUCTS")
    print("=" * 90)

    for pr in all_products:
        print(f"\n  {pr['product']} ({pr['n_reviews']} reviews, {pr['n_categories']} categories)")
        header = f"    {'Model':<25} {'Raw V':<8} {'Sum V':<8} {'Delta':<10} {'95% CI':<22} {'p':<8} {'Sig?'}"
        print(header)
        print("    " + "-" * 80)
        for r in pr["results"]:
            d = r["sum_v"] - r["raw_v"]
            ci = r["boot"]["v_ci"]
            p = r["boot"]["v_p"]
            sig = "YES" if p < 0.05 else "no"
            print(f"    {r['model']:<25} {r['raw_v']:<8.4f} {r['sum_v']:<8.4f} {d:<+10.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}]  {p:<8.4f} {sig}")

    # Save
    out_path = DATA_DIR / "multi_product_results.json"
    with open(out_path, "w") as f:
        json.dump(all_products, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
