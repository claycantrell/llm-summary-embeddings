---
title: "Cross-Model Validation — GPT-5-mini Labels Confirm Effect"
date: 2026-03-16
tags: [validation, cross-model, gpt-5-mini, same-llm-bias, primary]
---

## Question

Is the clustering improvement an artifact of same-LLM bias (Claude Haiku labels + Claude Haiku summaries)?

## Test

Re-labeled Fire TV Stick reviews using GPT-5-mini (OpenAI) — a completely independent model from a different provider. Used the same taxonomy but independent labeling. Then evaluated clustering with GPT-5-mini labels as ground truth.

## Inter-Model Agreement

- Valid comparisons: 312 reviews
- Exact agreement: 241/312 (77.2%)
- Cohen's kappa: 0.747 (substantial agreement)

The two models largely agree on category assignments, suggesting the taxonomy captures real structure in the data rather than model-specific artifacts.

## Clustering Results (BGE-base-en-v1.5)

| Ground Truth Labels | Raw V | Summary V | Delta |
|---|---|---|---|
| Haiku (same model) | 0.245 | 0.463 | +0.218 |
| GPT-5-mini (independent) | 0.288 | 0.453 | **+0.166** |

## Finding

**The effect holds with independent labels.** Summaries improve clustering by +0.166 V-measure even when evaluated against labels from a completely different LLM (different model, different provider, different architecture).

The delta is slightly smaller with GPT labels (+0.17 vs +0.22), which is expected — some of the Haiku-label improvement likely reflected same-model alignment. But the core effect persists clearly.

## What This Rules Out

- Same-LLM bias as the primary explanation
- Taxonomy reflecting only Haiku's worldview (GPT-5-mini agrees 77% on the labels)
- The improvement being an artifact of label-summary alignment within one model

## What Remains

Human validation would still strengthen the paper, but this cross-model check substantially reduces the label validity concern. Two independent models from different providers agree on the labels AND both show the same clustering improvement with summaries.
