---
title: "Length-Control Baselines — Shorter Text Does Not Explain the Effect"
date: 2026-03-16
tags: [baselines, length, ablation, methodology]
---

## Question

Is the clustering improvement simply because summaries are shorter? Shorter text = less noise = better embeddings?

## Test

Compared LLM summaries against naive length-reduction baselines on Fire TV Stick (BGE-base-en-v1.5):

| Condition | Avg words | V-measure | ARI | vs Raw |
|---|---|---|---|---|
| Raw text | 65 | 0.257 | 0.146 | — |
| First 20 words | 18 | 0.198 | 0.117 | -0.059 |
| First sentence | 13 | 0.172 | 0.090 | -0.085 |
| First 10 words | 9 | 0.137 | 0.069 | -0.120 |
| **LLM summary** | **9** | **0.438** | **0.350** | **+0.181** |

## Key Finding

**Naive truncation makes clustering worse, not better.** Every length-reduction baseline scores below raw text. Shorter text without intelligent selection loses discriminative information.

**LLM summaries at the same word count are 3x better.** The summary and "first 10 words" both average 10 words, but the summary achieves V=0.438 vs V=0.137. The difference is entirely in WHAT is selected, not how much.

This rules out the explanation that the improvement comes from text shortening. The LLM is performing semantic normalization — selecting, translating, and canonicalizing the most relevant content — not merely compressing.

## Follow-up: Fair Extractive Baselines

The naive truncation baselines above are strawmen — reviews start with emotional noise, so first-N-words is unfairly bad. Fairer test: extractive methods that read the whole review and select the best part.

| Condition | Avg words | V-measure | vs Raw |
|---|---|---|---|
| Raw text | 65 | 0.257 | — |
| TF-IDF best sentence | 20 | 0.183 | -0.074 |
| Longest sentence | 21 | 0.182 | -0.075 |
| Middle sentence | 14 | 0.138 | -0.119 |
| Last sentence | 14 | 0.084 | -0.173 |
| First 10 words | 9 | 0.137 | -0.120 |
| **LLM summary** | **9** | **0.438** | **+0.181** |

**Every extractive method scores below raw text**, even TF-IDF sentence selection which reads the whole review and picks the most informative sentence. The LLM summary at half the word count of the best extractive method outperforms by 0.255 V-measure.

This is the key evidence: the improvement is not from **selecting** the right content — extractive methods select well but don't normalize. It's from **rewriting** — translating the selected content into canonical, consistent language. Selection without normalization hurts. Normalization without selection (generic summarization) helps. The LLM does both.

## Implication

The improvement is not a length artifact, nor a content-selection artifact. It is attributable specifically to the LLM's rewriting — its ability to translate diverse surface expressions into normalized canonical forms. This is the strongest evidence that the mechanism is semantic normalization rather than information reduction or extractive selection.
