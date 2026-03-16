---
title: "Human Review of Labels — Ambiguity, Not Error"
date: 2026-03-16
tags: [validation, labels, human-review, limitations]
---

## Process

The first author manually reviewed 121 Fire TV Stick reviews selected for human validation: 50 spot-checks where both models (Claude Haiku and GPT-5-mini) agreed, and 71 tiebreaker cases where the models disagreed.

## Findings

1. **Where models agree, the labels are correct.** Across the 50 spot-checked consensus labels, the author agreed with the assigned category in all cases.

2. **Where models disagree, the reviews are genuinely multi-label.** The disagreements do not reflect labeling errors by either model. Instead, they reflect reviews that express multiple complaint types — for example, a review that describes both WiFi connectivity issues and device freezing. Both models identify a real complaint in the review; they simply foreground different aspects.

3. **The taxonomy assumes single-label assignment, but some reviews are inherently multi-label.** This is a property of the data, not a flaw in the labeling process.

## Implication

The LLM-generated labels appear to be valid where the models agree, and the disagreements reflect genuine ambiguity in the source text rather than labeling errors. This observation is consistent with the high inter-model agreement (Cohen's kappa = 0.747).

The single-label assumption places a ceiling on clustering performance — reviews with multiple complaint types cannot be perfectly assigned to one cluster. This likely explains why V-measure scores plateau in the 0.4–0.5 range rather than approaching 1.0, for both raw and summary embeddings.

## For the Paper

Mention in limitations: the taxonomy assumes single-label assignment, but manual review revealed that a meaningful fraction of reviews express multiple complaint types. A multi-label approach could improve both labeling and clustering evaluation in future work.
