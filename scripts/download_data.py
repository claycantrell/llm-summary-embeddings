#!/usr/bin/env python3
"""
Download and preprocess datasets for the LLM summary embeddings experiment.

Two datasets:
1. App Reviews — informal, noisy text with human-labeled complaint types
   (problem discovery, feature request, user experience, rating)
2. CFPB Consumer Complaints — structured, factual text (negative control)
"""

import os
import sys
import zipfile
import io
import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")

SAMPLE_PER_CATEGORY = 400  # use more data for statistical power
MIN_REVIEW_LENGTH = 20  # characters
RANDOM_SEED = 42

# ── App Reviews Dataset ──────────────────────────────────────────────────

APP_REVIEWS_URL = "https://raw.githubusercontent.com/mohammadzaeem/classification_of_app_reviews/master/data/app_reviews.csv"
APP_REVIEWS_PATH = os.path.join(DATA_DIR, "app_reviews_sample.csv")


def download_app_reviews():
    """Download and preprocess the app reviews classification dataset."""
    if os.path.exists(APP_REVIEWS_PATH):
        df = pd.read_csv(APP_REVIEWS_PATH)
        print(f"[OK] App reviews already exist at {APP_REVIEWS_PATH}")
        print(f"     {len(df)} rows, {df['label'].nunique()} categories")
        return

    os.makedirs(DATA_DIR, exist_ok=True)

    print("Downloading app reviews dataset...")
    resp = requests.get(APP_REVIEWS_URL, timeout=60)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))

    print(f"  Raw: {len(df)} reviews")
    print(f"  Classes: {df['class'].value_counts().to_dict()}")

    # Keep the 4 main classes
    keep_classes = ["problem discovery", "feature request", "user experience", "rating"]
    df = df[df["class"].isin(keep_classes)].copy()

    # Drop empty/very short reviews
    df = df.dropna(subset=["review"])
    df = df[df["review"].str.len() >= MIN_REVIEW_LENGTH]

    # Rename columns
    df = df.rename(columns={"review": "text", "class": "label"})
    df = df[["text", "label"]].reset_index(drop=True)

    print(f"\n  After filtering:")
    print(f"  {df['label'].value_counts().to_string()}")

    # Balance: sample SAMPLE_PER_CATEGORY per class (or all if fewer)
    sampled = []
    for label in keep_classes:
        subset = df[df["label"] == label]
        n = min(SAMPLE_PER_CATEGORY, len(subset))
        sampled.append(subset.sample(n=n, random_state=RANDOM_SEED))
        print(f"    {label}: sampled {n}")

    sample_df = pd.concat(sampled, ignore_index=True)
    sample_df = sample_df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    sample_df.to_csv(APP_REVIEWS_PATH, index=False)
    print(f"\n[OK] Saved: {APP_REVIEWS_PATH}")
    print(f"     {len(sample_df)} rows, {sample_df['label'].nunique()} categories")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Data Download & Preprocessing")
    print("=" * 60)

    download_app_reviews()

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
