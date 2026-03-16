---
title: "Prompt Ablation — Noise Removal vs Semantic Extraction"
date: 2026-03-15
tags: [ablation, prompt, noise-removal, significant]
---

## Question

Is the clustering improvement from **noise removal** (LLM strips emotion/narrative) or **semantic extraction** (the prompt steers toward complaint type)?

## Design

Same dataset (Fire TV Stick, 859 reviews, 9 categories), same embedding model (BGE-base-en-v1.5). Two summary prompts:

- **Complaint-focused**: "What specifically went wrong with the product?" (max 20 words)
- **Neutral**: "Summarize this review in one sentence." (max 20 words, no steering)

## Results

| Condition | V-measure | Delta vs Raw | % of max improvement | p |
|---|---|---|---|---|
| Raw text | 0.257 | — | 0% | — |
| Neutral summary | 0.436 | +0.179 | **85%** | < 0.001 |
| Complaint-focused | 0.468 | +0.211 | 100% | < 0.001 |

## Finding

**It's mostly noise removal.** The neutral prompt captures 85% of the complaint-focused prompt's improvement. The LLM doesn't need to be told what to extract — any summarization step that restates the review in clean language produces the effect.

## Example

Raw review: "It lags quite a bit more then I expected. I like it but can randomly be slow."

- Complaint summary: "Device lags and randomly becomes slow during use."
- Neutral summary: "Device lags and randomly becomes slow, but user likes it overall."

The neutral version retains sentiment ("but user likes it overall") that the complaint version strips. But both remove the casual tone, normalize the language, and surface the core content. That normalization — not the complaint extraction — drives the clustering improvement.

## Implication for the Paper

The finding is more general than "use a complaint-focused prompt." It's: **any LLM summarization step normalizes noisy text into a representation that embedding models can cluster more effectively.** The prompt gives a small additional bonus (~15% of the improvement) but is not required. This makes the approach more practical — practitioners don't need prompt engineering, just summarization.

## What This Rules Out

This rules out the explanation that our complaint-focused prompt was "cheating" by encoding category information into the summary. A neutral prompt with zero task awareness produces nearly the same improvement.

## Important Caveat: Primary vs Peripheral Content

Our test was the easy case. In 1-star product reviews, the complaint IS the primary content — any summary will naturally surface it. The 85% overlap between neutral and complaint-focused prompts reflects this: summarization and complaint extraction converge when the complaint is the whole point of the text.

We hypothesize the prompt matters much more when the clustering target is **peripheral to the text's main content** — information that's present but not the focus:

- Clustering support emails by **product version** (mentioned in passing, email is about the problem)
- Clustering academic papers by **methodology** (one section, paper is about findings)
- Clustering job postings by **company culture signals** (implicit, posting is about requirements)
- Clustering medical notes by **patient anxiety level** (subtext, note is about diagnosis)

In these cases, a generic summary would focus on the primary content and miss the target dimension entirely. A targeted prompt would extract it. The gap between neutral and targeted should flip from small (15% in our case) to dominant.

This is a limitation of our current experiments and an important direction for future work. The full "semantic lens" argument — that the prompt controls what the embedding space organizes around — likely holds strongest when the target dimension diverges from what a default summary would capture.
