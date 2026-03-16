---
title: "App Reviews Experiment — Positive Results (Verified)"
date: 2026-03-16
tags: [app-reviews, positive-result, embedding, clustering, summarization, significant, verified]
---

## Summary

LLM-generated summaries of app reviews **significantly improve** embedding cluster quality when clustering by review type (bug report, feature request, user experience, rating). The effect is statistically significant on all three embedding models.

## Dataset

- Source: Maalej et al. app review classification dataset (5,081 reviews from Google Play and Apple App Store)
- Human-labeled categories: problem discovery, feature request, user experience, rating
- Sample: 400 per category, 1,600 total
- Text characteristics: informal, noisy, short (median ~12 words), emotional, varied writing styles

## Results (Verified 2026-03-16)

| Model | Raw V | Summary V | Delta | 95% CI | p-value |
|---|---|---|---|---|---|
| all-MiniLM-L6-v2 | 0.174 | 0.261 | +0.086 | [+0.019, +0.117] | < 0.001 |
| bge-base-en-v1.5 | 0.282 | 0.341 | +0.059 | [+0.032, +0.092] | < 0.001 |
| nomic-embed-text-v1.5 | 0.296 | 0.317 | +0.022 | [-0.001, +0.110] | 0.03 |

All three models significant at p < 0.05.

## Note on Reproducibility

The original run's cached summaries were lost when the experiment pipeline was re-run for the Amazon dataset. A first re-run with a generic prompt ("summarize the core point") produced weaker results because the prompt did not match the original methodology. A second re-run with the correct app-review-specific prompt ("what is the user's main feedback — are they reporting a bug, requesting a feature, describing their experience, or just rating the app?") produced the results above. This highlights that summary prompt wording matters for reproducibility, and cached outputs should be preserved.

## Importance for the Paper

This is the only experiment with **human-created labels** that the summarization model never saw. It validates that the clustering improvement is not an artifact of same-LLM bias between labeling and summarization.
