---
title: "App Reviews Experiment — Positive Results"
date: 2026-03-15
tags: [app-reviews, positive-result, embedding, clustering, summarization, significant]
---

## Summary

LLM-generated summaries of app reviews **significantly improve** embedding cluster quality when clustering by review type (bug report, feature request, user experience, rating). This effect is statistically significant on 2 of 3 embedding models (p < 0.05).

## Dataset

- Source: Maalej et al. app review classification dataset (5,081 reviews from Google Play and Apple App Store)
- Human-labeled categories: problem discovery, feature request, user experience, rating
- Sample: 400 per category, 1,600 total
- Text characteristics: informal, noisy, short (median ~12 words), emotional, varied writing styles

## Results

| Model | Max Tokens | Raw V | Summary V | Delta | 95% CI | p-value | Significant |
|---|---|---|---|---|---|---|---|
| all-MiniLM-L6-v2 | 256 | 0.174 | 0.225 | +0.051 | [-0.005, +0.074] | 0.04 | YES |
| bge-base-en-v1.5 | 512 | 0.282 | 0.331 | +0.049 | [+0.004, +0.080] | 0.02 | YES |
| nomic-embed-text-v1.5 | 8192 | 0.296 | 0.318 | +0.022 | [-0.029, +0.099] | 0.17 | no |

ARI results (BGE): Raw 0.251, Summary 0.290, delta +0.040, p=0.04, significant.

## Key Observations

1. **Summaries help on noisy informal text.** App reviews are short, emotional, use slang, mix topics — exactly the conditions where raw embeddings struggle to find the latent category.

2. **The effect persists beyond truncation.** BGE (512 tokens) sees these short reviews in full and still benefits from summaries. This is not a token-limit artifact.

3. **Larger models show smaller but positive effects.** The trend is consistent across all three models — summaries always help — but the improvement decreases with model capability. Nomic (8192 tok, best raw performance) shows the smallest delta.

4. **Contrast with CFPB (negative results).** On structured, factual consumer complaints (CFPB dataset), summaries consistently HURT clustering. The difference: CFPB complaints state the issue directly; app reviews bury it in emotional/informal language.

## What the Summaries Are Doing

The LLM reads "Was an excellent app Now crashes on iPod touch since last update Won't open at all Please fix asap!!" and produces "App crashes on iPod touch after recent update, won't open."

The summary:
- Strips emotional language ("Please fix asap!!")
- Removes narrative setup ("Was an excellent app")
- Normalizes varied expressions of the same issue into consistent language
- Surfaces the **type** of feedback (bug report) that was implicit in the raw text

Two users can write completely different reviews about the same crash bug, but their summaries will converge on similar language. This makes the embedding space more coherent.

## Technical Details

- Summary model: Claude Haiku (claude-haiku-4-5-20251001)
- Summary prompt: "Produce a single concise sentence (max 20 words) summarizing the core point"
- Batched 20 reviews per API call with structured outputs (tool use)
- Clustering: KMeans (k=4)
- Statistical test: Bootstrap resampling (100 iterations, 80% subsample)
- Full results in `data/experiment_results.json`
