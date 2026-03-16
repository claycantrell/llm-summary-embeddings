#!/usr/bin/env python3
"""
Build a labeled Amazon 1-star reviews dataset in three phases:

Phase 1: DISCOVER categories from a held-out sample
Phase 2: LABEL reviews using the discovered taxonomy
Phase 3: Save the final dataset for the embedding experiment

This creates ground truth labels for informal, noisy text where
the complaint type is latent — not obvious from surface keywords.
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
CACHE_DIR = REPO_ROOT / "cache"

POOL_PATH = DATA_DIR / "amazon_1star_pool.json"
TAXONOMY_PATH = DATA_DIR / "amazon_taxonomy.json"
LABELED_PATH = DATA_DIR / "amazon_labeled.json"
FINAL_PATH = DATA_DIR / "amazon_dataset.csv"

MODEL = "claude-haiku-4-5-20251001"
MAX_RETRIES = 5
BASE_DELAY = 1.0
RANDOM_SEED = 42


def load_env():
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found.")
        sys.exit(1)
    return api_key


def api_call_with_retry(func, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_str = str(e).lower()
            if any(x in error_str for x in ["rate", "429", "too many", "500", "502", "503", "overloaded"]):
                delay = BASE_DELAY * (2 ** attempt)
                print(f"  Retrying in {delay:.1f}s (attempt {attempt + 1})...")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError(f"Failed after {MAX_RETRIES} retries")


# ── Phase 1: Discover Taxonomy ──────────────────────────────────────────

def phase1_discover(client: Anthropic, reviews: list[dict]) -> list[str]:
    """Send batches of 50 reviews to discover complaint categories."""
    if TAXONOMY_PATH.exists():
        with open(TAXONOMY_PATH) as f:
            taxonomy = json.load(f)
        print(f"[CACHE] Loaded taxonomy: {len(taxonomy)} categories")
        for cat in taxonomy:
            print(f"  - {cat}")
        return taxonomy

    print("\n" + "=" * 60)
    print("PHASE 1: Discovering complaint categories")
    print("=" * 60)

    # Use a held-out sample of 200 reviews for discovery
    random.seed(RANDOM_SEED)
    discovery_sample = random.sample(reviews, min(200, len(reviews)))

    # Send in batches of 50
    all_categories = []
    for batch_start in range(0, len(discovery_sample), 50):
        batch = discovery_sample[batch_start:batch_start + 50]
        numbered = []
        for j, r in enumerate(batch):
            numbered.append(f"REVIEW {j+1}: {r['text'][:500]}")
        user_msg = "\n\n".join(numbered)

        response = api_call_with_retry(
            client.messages.create,
            model=MODEL,
            max_tokens=1024,
            system=(
                "You are analyzing one-star Amazon product reviews to discover the main types of complaints. "
                "Read all the reviews and identify 8-15 distinct complaint CATEGORIES. "
                "Each category should describe WHY the customer is unhappy — the root cause of the complaint, "
                "not the product type. Categories should be mutually exclusive and collectively exhaustive. "
                "Return ONLY a JSON array of category names as short labels (2-5 words each). "
                "Example: [\"Product arrived damaged\", \"Does not work as described\", \"Poor build quality\"]"
            ),
            messages=[{"role": "user", "content": user_msg}],
        )

        text = response.content[0].text.strip()
        # Parse JSON array from response
        try:
            # Handle markdown code blocks
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            cats = json.loads(text)
            all_categories.extend(cats)
            print(f"  Batch {batch_start//50 + 1}: found {len(cats)} categories")
        except json.JSONDecodeError:
            print(f"  Batch {batch_start//50 + 1}: failed to parse, raw: {text[:200]}")

    # Now merge/deduplicate across batches
    print(f"\n  Raw categories from all batches ({len(all_categories)}):")
    for c in all_categories:
        print(f"    - {c}")

    # Use Claude to merge duplicates into a final taxonomy
    response = api_call_with_retry(
        client.messages.create,
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are creating a final taxonomy of complaint categories for one-star Amazon reviews. "
            "Given a raw list of categories discovered from different batches of reviews, "
            "merge duplicates and near-duplicates into 8-12 clean, distinct categories. "
            "Each category should be a short label (2-5 words) describing the ROOT CAUSE of the complaint. "
            "Categories should be mutually exclusive. Drop any category that's too vague or overlaps heavily. "
            "Return ONLY a JSON array of the final category names."
        ),
        messages=[{"role": "user", "content": json.dumps(all_categories)}],
    )

    text = response.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    taxonomy = json.loads(text)

    print(f"\n  Final taxonomy ({len(taxonomy)} categories):")
    for cat in taxonomy:
        print(f"    - {cat}")

    with open(TAXONOMY_PATH, "w") as f:
        json.dump(taxonomy, f, indent=2)
    print(f"\n  Saved to {TAXONOMY_PATH}")

    return taxonomy


# ── Phase 2: Label Reviews ──────────────────────────────────────────────

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
                        "confidence": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                        },
                    },
                    "required": ["index", "category", "confidence"],
                },
            },
        },
        "required": ["labels"],
    },
}


def phase2_label(client: Anthropic, reviews: list[dict], taxonomy: list[str]) -> list[dict]:
    """Label reviews using the discovered taxonomy. Batches of 50."""
    if LABELED_PATH.exists():
        with open(LABELED_PATH) as f:
            labeled = json.load(f)
        print(f"[CACHE] Loaded {len(labeled)} labeled reviews")
        return labeled

    print("\n" + "=" * 60)
    print("PHASE 2: Labeling reviews with discovered taxonomy")
    print("=" * 60)

    # Use a separate sample from the pool (not the discovery sample)
    random.seed(RANDOM_SEED + 1)  # different seed than discovery
    label_pool = random.sample(reviews, min(2000, len(reviews)))

    taxonomy_str = "\n".join(f"  - {cat}" for cat in taxonomy)
    labeled = []

    for batch_start in range(0, len(label_pool), 50):
        batch = label_pool[batch_start:batch_start + 50]
        numbered = []
        for j, r in enumerate(batch):
            numbered.append(f"REVIEW {j+1}: {r['text'][:500]}")
        user_msg = "\n\n".join(numbered)

        response = api_call_with_retry(
            client.messages.create,
            model=MODEL,
            max_tokens=4096,
            system=(
                f"You are labeling one-star Amazon product reviews. For each review, assign exactly one "
                f"category from this taxonomy:\n{taxonomy_str}\n\n"
                f"Choose the category that best describes the ROOT CAUSE of the complaint. "
                f"If a review doesn't fit any category well, use the closest match and mark confidence as 'low'. "
                f"Use the submit_labels tool to return all labels."
            ),
            tools=[LABEL_TOOL],
            tool_choice={"type": "tool", "name": "submit_labels"},
            messages=[{"role": "user", "content": user_msg}],
        )

        tool_block = next(
            (b for b in response.content if b.type == "tool_use"), None
        )
        if tool_block is None:
            print(f"  WARNING: No tool response at batch {batch_start}")
            continue

        batch_labels = tool_block.input.get("labels", [])
        batch_labels.sort(key=lambda x: x.get("index", 0))

        for j, r in enumerate(batch):
            label_entry = next((l for l in batch_labels if l["index"] == j + 1), None)
            if label_entry:
                labeled.append({
                    "text": r["text"],
                    "title": r["title"],
                    "asin": r.get("asin", ""),
                    "category": label_entry["category"],
                    "confidence": label_entry["confidence"],
                })
            else:
                labeled.append({
                    "text": r["text"],
                    "title": r["title"],
                    "asin": r.get("asin", ""),
                    "category": "unknown",
                    "confidence": "low",
                })

        print(f"  Labeled {min(batch_start + 50, len(label_pool))}/{len(label_pool)}")

        # Save incrementally
        if (batch_start + 50) % 200 == 0:
            with open(LABELED_PATH, "w") as f:
                json.dump(labeled, f)

    with open(LABELED_PATH, "w") as f:
        json.dump(labeled, f)
    print(f"\n  Saved {len(labeled)} labeled reviews to {LABELED_PATH}")

    return labeled


# ── Phase 3: Build Final Dataset ────────────────────────────────────────

def phase3_build(labeled: list[dict], taxonomy: list[str]):
    """Build the final balanced CSV dataset."""
    import pandas as pd

    print("\n" + "=" * 60)
    print("PHASE 3: Building final dataset")
    print("=" * 60)

    df = pd.DataFrame(labeled)

    # Drop unknowns and low-confidence labels
    before = len(df)
    df = df[df["category"] != "unknown"]
    df = df[df["confidence"].isin(["high", "medium"])]
    print(f"  Dropped {before - len(df)} low-confidence/unknown labels")

    # Normalize categories — some labels might not exactly match taxonomy
    # Map each assigned category to the closest taxonomy entry
    valid_cats = set(taxonomy)
    df["category_clean"] = df["category"].apply(
        lambda c: c if c in valid_cats else None
    )
    unmapped = df[df["category_clean"].isna()]
    if len(unmapped) > 0:
        print(f"  {len(unmapped)} reviews with non-matching categories:")
        print(f"    {unmapped['category'].value_counts().head(10).to_dict()}")
        # Try case-insensitive match
        tax_lower = {t.lower(): t for t in taxonomy}
        df["category_clean"] = df["category"].apply(
            lambda c: tax_lower.get(c.lower(), c) if c.lower() in tax_lower else c
        )

    df = df.dropna(subset=["category_clean"])
    df["label"] = df["category_clean"]

    print(f"\n  Category distribution:")
    cat_counts = df["label"].value_counts()
    for cat, count in cat_counts.items():
        print(f"    {cat}: {count}")

    # Balance: take up to 100 per category, minimum 30 to include
    min_per_cat = 30
    max_per_cat = 100
    good_cats = cat_counts[cat_counts >= min_per_cat].index.tolist()
    print(f"\n  Categories with >= {min_per_cat} reviews: {len(good_cats)}")

    sampled = []
    for cat in good_cats:
        subset = df[df["label"] == cat]
        n = min(max_per_cat, len(subset))
        sampled.append(subset.sample(n=n, random_state=RANDOM_SEED))

    final = pd.concat(sampled, ignore_index=True)
    final = final.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    final = final[["text", "label"]]

    final.to_csv(FINAL_PATH, index=False)
    print(f"\n  Final dataset: {FINAL_PATH}")
    print(f"  {len(final)} reviews, {final['label'].nunique()} categories")
    print(f"\n  Distribution:")
    for cat, count in final["label"].value_counts().items():
        print(f"    {cat}: {count}")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Amazon 1-Star Reviews — Dataset Builder")
    print("=" * 60)

    api_key = load_env()
    client = Anthropic(api_key=api_key)

    # Load review pool
    if not POOL_PATH.exists():
        print(f"ERROR: Review pool not found at {POOL_PATH}")
        print("Run download_data.py first or the streaming script.")
        sys.exit(1)

    with open(POOL_PATH) as f:
        reviews = json.load(f)
    print(f"\nLoaded {len(reviews)} one-star reviews from pool")

    # Phase 1: Discover taxonomy
    taxonomy = phase1_discover(client, reviews)

    # Phase 2: Label reviews
    labeled = phase2_label(client, reviews, taxonomy)

    # Phase 3: Build dataset
    phase3_build(labeled, taxonomy)

    print("\n" + "=" * 60)
    print("Done! Dataset ready for experiment.")
    print("=" * 60)


if __name__ == "__main__":
    main()
