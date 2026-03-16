---
title: "Paraphrase Ablation — Normalization Alone Is Not Sufficient"
date: 2026-03-16
tags: [ablation, paraphrase, mechanism, compression, primary]
---

## Question

Is the improvement from **normalization** (rewriting noisy text clearly) or **compression** (forcing the LLM to select what matters)? Or both?

## Design

Three conditions on Fire TV Stick (BGE-base-en-v1.5):

- **Raw text**: Original review (mean 66 words)
- **Paraphrase**: "Rewrite in clear plain English, keep all information, don't shorten" (mean 47 words)
- **LLM summary**: "Summarize the core complaint in max 20 words" (mean 10 words)

## Results

| Condition | Avg words | V-measure | ARI | vs Raw |
|---|---|---|---|---|
| Raw text | 66 | 0.257 | 0.146 | — |
| Paraphrase (full-length) | 47 | 0.240 | 0.129 | -0.018 (n.s.) |
| LLM summary (compressed) | 10 | 0.438 | 0.350 | +0.181 (p<0.001) |

Bootstrap: Paraphrase vs raw p=0.43 (not significant). Summary vs raw p<0.001.

## Key Finding

**Normalization without compression does not improve clustering.** A full-length rewrite that cleans grammar, removes emotion, and states everything plainly produces no improvement over raw text. The paraphrase captures -10% of the summary improvement — effectively zero.

## Combined with extractive baselines

| What it does | Selection? | Normalization? | Result |
|---|---|---|---|
| Extractive (TF-IDF sentence) | Yes | No | Worse than raw |
| Paraphrase | No | Yes | No change |
| LLM summary | Yes | Yes | +0.181 V-measure |

Neither selection nor normalization alone is sufficient. The improvement requires **both**: the LLM must select what to keep AND normalize it into canonical language. The compression forces salience selection; the rewriting normalizes surface expression. Together they produce a representation that is geometrically clusterable.

## Implication for the Paper

This refines the mechanism claim. "Semantic normalization" is necessary but not sufficient — it must be paired with **information compression** that forces the LLM to make salience judgments. The 10-word constraint is not incidental; it's load-bearing. It forces the LLM to choose one thing to say about the review, and that forced choice is what creates discriminative cluster structure.

This also explains why the prompt ablation showed only 15% difference between neutral and complaint-focused summaries — the compression constraint already forces salience selection even without explicit steering.
