---
title: "CFPB Experiment — Negative Results"
date: 2026-03-15
tags: [cfpb, negative-result, embedding, clustering, summarization]
---

## Summary

LLM-generated summaries of CFPB consumer complaints do NOT improve embedding cluster quality compared to raw text embeddings. This held across three embedding models, two experimental designs, and both within-category and across-category clustering.

## Experiment 1: Across-Category Clustering

**Design:** 1000 complaints, 10 issue categories, 9 product categories. Cluster embeddings of raw text vs. LLM summaries. Evaluate against both issue labels (what went wrong) and product labels (what product type).

**Hypothesis:** Summaries should improve issue-based clustering (by extracting "what went wrong") while hurting product-based clustering (by stripping product keywords).

**Results (V-measure, higher is better):**

| Model | Max Tokens | Raw (issue) | Summary (issue) | Delta |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | 256 | 0.490 | 0.501 | +0.011 |
| bge-base-en-v1.5 | 512 | 0.628 | 0.528 | -0.100 |
| nomic-embed-text-v1.5 | 8192 | 0.591 | 0.516 | -0.076 |

| Model | Max Tokens | Raw (product) | Summary (product) | Delta |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | 256 | 0.513 | 0.493 | -0.020 |
| bge-base-en-v1.5 | 512 | 0.567 | 0.518 | -0.049 |
| nomic-embed-text-v1.5 | 8192 | 0.589 | 0.469 | -0.120 |

**No results were statistically significant** (bootstrap, 100 iterations, p > 0.05 for all).

**Key observation:** The only model where summaries slightly helped on issue clustering was the smallest model (MiniLM, 256 token limit) — which truncates most raw complaints. Better models with longer contexts consistently favored raw text.

## Experiment 2: Within-Category Clustering

**Design:** 500 mortgage complaints (5 issue types) + 500 checking account complaints (5 issue types). This mirrors the original Amazon review experiment — finding latent complaint types within a homogeneous document set.

**Hypothesis:** Within a single product category, all docs use similar surface language (e.g., all mention "mortgage"). Summaries should help the embedding model look past shared surface features to find the actual issue type.

**Results (V-measure):**

### Checking or savings account (500 docs, 5 issues)
| Model | Raw V | Summary V | Delta |
|---|---|---|---|
| all-MiniLM-L6-v2 | 0.249 | 0.237 | -0.012 |
| bge-base-en-v1.5 | 0.253 | 0.222 | -0.031 |
| nomic-embed-text-v1.5 | 0.237 | 0.262 | +0.025 |

### Mortgage (500 docs, 5 issues)
| Model | Raw V | Summary V | Delta |
|---|---|---|---|
| all-MiniLM-L6-v2 | 0.145 | 0.073 | -0.072 |
| bge-base-en-v1.5 | 0.101 | 0.066 | -0.036 |
| nomic-embed-text-v1.5 | 0.207 | 0.080 | -0.127 |

**No results were statistically significant.** Mortgage clustering was particularly bad for summaries.

## Why It Failed

1. **CFPB complaints are already structured and factual.** Unlike informal product reviews, complainants state their issue relatively directly. The "noise" (company names, dollar amounts, regulatory citations, specific processes like "escrow" or "foreclosure") is actually signal that helps the embedding model distinguish complaint types.

2. **Summaries over-compress.** A one-sentence summary like "mortgage servicer failed to process payment correctly" is too generic — different issue types collapse into similar-sounding summaries. The specifics that distinguish "trouble during payment" from "struggling to pay mortgage" from "loan modification" get lost.

3. **Better models need less help.** The pattern across models is clear: the more capable the embedding model (longer context, higher dimensionality), the WORSE summaries perform relative to raw text. Modern embedding models already handle long, noisy input well.

4. **The task was wrong for this dataset.** CFPB category labels are broad and distinguishable from surface features. The Amazon review experiment worked because the task was harder — finding the specific product defect within reviews that all look similar (one-star, same product, emotional language). CFPB complaints within a product category still contain plenty of distinguishing factual detail.

## What This Means for the Paper

This is a valuable negative result that constrains the hypothesis. The claim is NOT "summaries always improve embedding clusters." The claim should be:

- LLM summaries improve clustering **when the source text is noisy/informal and the latent structure is obscured by surface-level variation** (e.g., Amazon reviews where the complaint is buried in emotional language)
- LLM summaries **hurt** clustering when the source text is already relatively structured/factual and the distinguishing details are in the specifics that summaries strip away
- The effect **diminishes with better embedding models** — suggesting it's a workaround for limited model capacity, not a fundamental improvement

## Technical Details

- Summary model: Claude Haiku (claude-haiku-4-5-20251001)
- Summary prompt: "Produce a single concise sentence (max 30 words) summarizing the core issue"
- Batched 20 complaints per API call with structured outputs (tool use)
- Embedding models: all-MiniLM-L6-v2 (384d), bge-base-en-v1.5 (768d), nomic-embed-text-v1.5 (768d)
- Clustering: KMeans (k = number of ground truth categories)
- Metrics: V-measure, Adjusted Rand Index, Silhouette Score
- Statistical testing: Bootstrap resampling (100 iterations, 80% subsample)
- All summaries and embeddings cached to disk for reproducibility
- Full results in `data/experiment_results.json`
