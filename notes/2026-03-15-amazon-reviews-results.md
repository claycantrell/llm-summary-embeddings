---
title: "Amazon 1-Star Reviews Experiment — Marginal Results"
date: 2026-03-15
tags: [amazon, reviews, embedding, clustering, summarization, emergent-taxonomy]
---

## Summary

LLM-generated summaries of Amazon 1-star reviews show a consistent positive trend for clustering by complaint type across all three embedding models, but do not reach statistical significance. The effect is strongest on the smallest model (MiniLM, p=0.05).

## Dataset Construction (Novel)

Built a labeled dataset from scratch using a three-phase approach:

1. **Discovery**: Sent 200 random 1-star Appliances reviews to Claude in batches of 50. Discovered raw complaint categories, then merged into a final taxonomy of 12 categories.
2. **Labeling**: Labeled 2,000 reviews against the fixed taxonomy using structured outputs. Dropped low-confidence labels.
3. **Balancing**: Kept categories with 30+ reviews, capped at 100 per category.

Final taxonomy (11 categories): Product fails prematurely, Poor build quality, Incompatible with specs, Leaks/sealing defects, Difficult installation, Arrives damaged, Missing/incorrect parts, Misleading description, Inadequate customer service, Unpleasant taste/odor, Poor design.

Final dataset: 914 reviews, 11 categories, unbalanced (38-100 per category).

## Results

| Model | Raw V | Summary V | Delta | 95% CI | p-value |
|---|---|---|---|---|---|
| all-MiniLM-L6-v2 | 0.137 | 0.223 | +0.086 | [-0.008, +0.082] | 0.05 |
| bge-base-en-v1.5 | 0.252 | 0.260 | +0.007 | [-0.043, +0.059] | 0.28 |
| nomic-embed-text-v1.5 | 0.249 | 0.257 | +0.007 | [-0.036, +0.083] | 0.32 |

## Why Marginal

1. **Too many categories (11) for too few docs (914).** KMeans k=11 with ~83 docs per cluster is noisy. The app reviews experiment got significance with k=4 and 400 per cluster.
2. **Some categories are semantically close.** "Poor build quality" vs "Product fails prematurely" vs "Poor design" — these overlap significantly. A review about a cheap plastic part that broke could be any of the three.
3. **Unbalanced classes** (38-100 per category) hurt KMeans which assumes roughly equal cluster sizes.
4. **LLM-generated labels may be noisy.** No human validation of the labels. Labeling agreement is unknown.

## What's Valuable Here

The **dataset construction methodology** is the contribution, even if this specific run didn't reach significance:
- Emergent taxonomy discovery from data (not pre-defined)
- Independent labeling and summarization prompts (not circular)
- Reproducible pipeline

The consistent positive direction across all models, combined with the significant results on the app reviews dataset, supports the hypothesis. The Amazon dataset just needs either fewer, more distinct categories or more reviews per category.

## Follow-up: Merged Categories (7 categories, 585 reviews)

Merged overlapping categories: "Poor build quality" + "Product fails prematurely" + "Poor design" → "Defective or poor quality". Dropped customer service (meta-complaint). Merged installation issues with incompatibility.

| Model | Raw V | Summary V | Delta | p |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | 0.122 | 0.149 | +0.027 | 0.18 |
| bge-base-en-v1.5 | 0.274 | 0.299 | +0.025 | 0.31 |
| nomic-embed-text-v1.5 | 0.265 | 0.227 | -0.038 | 0.17 |

Still not significant. Direction positive on 2/3 models. Underpowered at 585 samples — app reviews got significance with 1600 samples and fewer categories.
