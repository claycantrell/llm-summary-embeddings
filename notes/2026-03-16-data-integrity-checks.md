---
title: "Data Integrity and Leakage Checks"
date: 2026-03-16
tags: [methodology, leakage, limitations, integrity]
---

## Checks Performed

### 1. Taxonomy leakage into summaries — CLEAN
Only 0.6% of summaries contain an exact taxonomy phrase, and these are natural language overlap ("remote control malfunction" is both a category name and a normal description). The summary prompt has zero reference to the taxonomy.

### 2. Prompt independence — CLEAN
The summary prompt ("what specifically went wrong with the product?") never mentions categories, taxonomy, or labeling. Verified by inspecting the source code.

### 3. Vocabulary normalization — PARTIAL CONCERN
TF-IDF clustering on summaries (V=0.32) substantially outperforms TF-IDF on raw text (V=0.15). This means the LLM converges on stereotyped keywords per complaint type — "crashes/freezes/reboots" for freezing issues, "subscription/paid/free" for content issues. Part of the embedding improvement is this vocabulary normalization, not just semantic understanding. However, embedding-based clustering (V=0.44) exceeds TF-IDF (V=0.32), confirming that semantic similarity contributes beyond keywords. Should be disclosed in paper.

### 4. Discovery/evaluation overlap — LOW SEVERITY
125 of 859 reviews in the final dataset were also in the 200-review taxonomy discovery sample. The taxonomy would be similar regardless of which 200 reviews were used — discovery finds category types, not individual review properties.

### 5. Same-LLM bias — PRIMARY CONCERN
The same model (Claude Haiku) labels reviews AND summarizes them. Its internal biases could create artificial alignment that inflates the apparent clustering improvement.

**How this could happen:** When Haiku labels a review as "WiFi and Connectivity Issues," it processes the text and forms an internal representation. When Haiku later summarizes the same review, it processes the same text through the same weights and may emphasize WiFi in a similar way — not because WiFi is the most salient thing a human would extract, but because that's how Haiku's attention patterns work on that text. Two ambiguous reviews that a human might label differently could get the same Haiku label AND similar Haiku summaries, because Haiku interprets ambiguous text consistently. The V-measure would look great but would be measuring Haiku-consistency, not actual cluster quality.

**Why this probably doesn't explain our results:**

1. **Human-labeled app reviews still showed the effect (p=0.02).** Haiku never touched those labels. If same-LLM bias were the primary driver, this experiment should have shown nothing. It didn't — the effect held with fully independent labels.

2. **The CFPB experiment failed.** If same-LLM bias creates artificial alignment, it should work regardless of text type. But summaries consistently hurt clustering on CFPB data. The effect is clearly data-dependent, which points to a real phenomenon in the text, not a model artifact.

3. **The neutral prompt ablation worked.** A different prompt — a different internal processing path through the model — still produced 85% of the improvement. If the effect were driven by Haiku's specific way of encoding complaint categories, changing the prompt should have disrupted the alignment more.

4. **Three different embedding models all show the effect.** The LLM bias would need to produce text that happens to cluster well on MiniLM AND BGE AND Nomic — three models with different architectures, training data, and embedding strategies. Possible but unlikely to be coincidence.

**Conclusion:** Legitimate concern, worth disclosing, but converging evidence from four independent angles makes it unlikely to be the primary explanation. The human-labeled app reviews result is the strongest rebuttal. To fully resolve: re-label a sample using a different LLM (GPT-4o, Gemini) and/or human annotators. Flag as limitation in the paper.

## Verdict

No smoking gun leakage. The results are credible but the same-LLM bias should be disclosed as a limitation. The human-labeled app reviews experiment is the critical corroboration that validates the effect independently of LLM labeling.
