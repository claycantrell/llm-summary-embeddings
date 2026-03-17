---
title: "How Abstractive Summarization Reshapes Embedding Space for Clustering Noisy Informal Text"
author: "Clay Cantrell (Independent Researcher, clay.cantrell@me.com)"
date: "March 2026"
abstract: |
  Embedding models map text to fixed-dimensional vectors, but noisy informal text produces embedding spaces where semantically equivalent documents are scattered by surface-level variation in style, tone, and narrative. We show that a single LLM abstractive summarization step improves V-measure by 0.08--0.28 (49--115\% relative) across three consumer product review datasets and three embedding models (9 of 9 tests, $p < 0.01$; 1,000-iteration bootstrap). The mechanism requires both compression and normalization: neither paraphrasing (two variants) nor extractive selection (four methods) reproduced the gains. Geometric analysis shows the effect operates through increased inter-class centroid separation rather than within-class compaction. On structured factual text, summarization degrades clustering. The findings are corroborated on a human-labeled dataset and validated through cross-model relabeling ($\kappa = 0.75$).
keywords:
  - text embeddings
  - clustering
  - LLM summarization
  - embedding geometry
  - semantic normalization
bibliography: ../bibliography/references.bib
csl: ../bibliography/citation-style.csl
link-citations: true
reference-section-title: References
---

# Introduction

Text embedding models compress documents into fixed-dimensional vectors, but they encode everything in the text---content, emotion, narrative, style---into a single representation. On noisy informal text such as product reviews and customer feedback, the task-relevant signal is buried inside stylistic and narrative variation that the embedding model cannot distinguish from meaning. Two reviews about the same product defect, written in different styles, may land far apart in embedding space simply because one is a three-paragraph rant and the other is a blunt sentence.

This work is motivated by a common practical problem: teams analyzing customer feedback at scale need to cluster reviews by complaint type, but standard embedding-based clustering produces noisy results because reviews about the same issue are written in wildly different styles. Our core finding is simple. In noisy informal reviews, much of the text outside the main complaint behaves like noise for clustering: emotional language, narrative tangents, repetition, and idiosyncratic phrasing obscure the target category. Summarization helps by compressing each review to its most salient aspect and rewriting that aspect in more consistent language. In structured factual complaints, by contrast, many of the details are themselves useful signals for distinguishing categories---specific entities, dollar amounts, procedural descriptions, and regulatory citations. In that setting, summarization removes information the embedding model would otherwise use, and clustering degrades.

We show that a single LLM summarization step improves V-measure by +0.08 to +0.28 on informal product reviews, reaching significance across three consumer electronics products and three embedding models spanning short to long context windows (9 of 9 tests, $p < 0.01$; 1,000-iteration bootstrap). Our ablations suggest the effect depends on two co-occurring operations: compression encourages aspect prioritization while rewriting normalizes surface expression. Neither paraphrasing (two variants) nor extractive selection (four methods) reproduced the gains. Geometric analysis shows the improvement manifests as increased distance between class centroids, not tighter clusters.

Prior work has explored LLM-based rewriting for retrieval [@sarthi2024raptor; @gao2023hyde; @wu2024llmaugmented], embedding quality [@enrichment2024], and controllable clustering [@controllable2025], and has tested summarization in clustering pipelines with mixed results [@textclustering2024]. Our contribution is distinct in isolating generic abstractive summarization as a pre-embedding transformation and analyzing its effect on clustering through direct geometric evidence together with a clear boundary condition on structured text.

This paper contributes: (1) evidence that abstractive summarization consistently improves clustering of noisy informal text across three products and three embedding models; (2) a two-part mechanism---compression forces aspect prioritization while rewriting normalizes expression---supported by ablations and geometric analysis showing primarily centroid separation; and (3) a boundary condition showing that the same transformation degrades clustering on structured factual text where fine-grained details distinguish categories.

# Related Work

## LLM Rewriting for Retrieval and Embedding Quality

Several recent approaches use LLMs to transform text before or during retrieval. RAPTOR [@sarthi2024raptor] recursively clusters and summarizes text chunks for multi-level retrieval. HyDE [@gao2023hyde] transforms the *query* side, generating hypothetical answer documents for zero-shot retrieval. LLM-Augmented Retrieval [@wu2024llmaugmented] generates synthetic queries and titles from documents for enriched doc-level embeddings. Text enrichment approaches [@enrichment2024] use LLMs to normalize terminology and correct inaccuracies before embedding. These study rewriting for retrieval or broad embedding performance, not for its effect on unsupervised clustering structure.

## Rewriting for Clustering Control

Controllable Clustering with LLM-driven Embeddings [@controllable2025] studies whether embeddings can be reshaped toward user-specified clustering perspectives through prompt-based and preprocessing-based transformations. Unlike that work, our main summarization condition does not inject a target perspective or desired clustering axis; it uses a generic summary prompt. We provide a mechanistic account together with direct geometric analysis and a structured-text failure case.

## Summarization in Clustering Pipelines

Viswanathan et al. [@textclustering2024] test summarization as a dimensionality-reduction step in LLM-embedding clustering pipelines and report mixed results. Rather than testing summarization as a general-purpose preprocessing step, we identify a specific text regime where it helps and another where it degrades performance, and we provide a mechanism that explains the difference. Their mixed results are consistent with our boundary-condition finding.

## Retrieval Granularity

Dense X Retrieval [@chen2024densex] examines what unit of text should be embedded. Our work explores the opposite direction: rather than decomposing documents into finer units, we compress them into coarser summaries, and rather than measuring retrieval, we measure clustering geometry.

# Method

## Datasets

### Amazon Product Reviews (Primary)

We constructed labeled datasets from Amazon product reviews (McAuley Lab, 2023) for three consumer electronics products: Fire TV Stick with Alexa Voice Remote (859 reviews, 9 complaint categories), Fitbit Charge activity tracker (454 reviews, 7 categories), and Senso Bluetooth headphones (813 reviews, 10 categories). All reviews are for a single product per dataset, eliminating product-type confounds: the only way to cluster correctly is to understand the complaint type, which is buried in varied, emotional language. Reviews were filtered to 1--3 star ratings with narrative text of at least 40 characters.

Complaint category labels were generated through a three-phase pipeline designed to avoid circularity between labeling and summarization:

**Phase 1: Taxonomy Discovery.** A held-out sample of 200 reviews was sent to Claude Haiku in batches of 50 with the instruction to identify 8--15 distinct complaint categories. Raw categories from multiple batches were merged into a final taxonomy of 9--11 categories per product.

**Phase 2: Labeling.** The remaining reviews were labeled against the fixed taxonomy in batches of 50 using structured outputs (tool use). Each review received a category assignment and a confidence rating (high, medium, or low). Low-confidence labels were excluded.

**Phase 3: Balancing.** Categories with fewer than 30 reviews were dropped. Remaining categories were capped at 100 reviews each.

The labeling prompt and the summarization prompt are independent: the labeling prompt references the taxonomy and asks for a category assignment; the summarization prompt asks only "what specifically went wrong with the product?" with no mention of categories.

### Label Validity

**Cross-model validation.** We independently re-labeled the Fire TV Stick reviews using GPT-5-mini (OpenAI). The two models agreed on 77.2% of labels (Cohen's $\kappa = 0.747$). The clustering improvement persisted with GPT-5-mini labels (V-measure $\Delta$ = +0.17, compared to +0.22 with Haiku labels).

**Human-labeled corroboration.** On the app reviews dataset from Maalej et al. [@maalej2016], which contains human-assigned labels for four review types (problem discovery, feature request, user experience, rating; 1,600 reviews), summary embeddings significantly improved clustering across all three models (MiniLM: $\Delta$ = +0.086, $p$ < 0.001; BGE: $\Delta$ = +0.059, $p$ < 0.001; Nomic: $\Delta$ = +0.022, $p$ = 0.03). This validates the effect with labels the summarization model never saw.

**Qualitative audit.** An audit of 121 Fire TV Stick reviews (50 consensus cases, 71 disagreement cases) found that labels assigned by both models were generally consistent with review content. Model disagreements arose from reviews expressing multiple complaint types rather than from labeling errors.

### CFPB Consumer Complaints (Negative Control)

We sampled 1,000 complaints from the Consumer Financial Protection Bureau database, selecting 500 mortgage complaints and 500 checking/savings account complaints, each spanning 5 issue categories. These complaints are structured, factual, and legalistic.

## Experimental Design

For each dataset, we compared two conditions:

- **Raw text embeddings**: Embed the original review text, cluster with KMeans ($k$ = number of ground truth categories), evaluate against ground truth labels.
- **Summary embeddings**: Summarize each review with Claude Haiku (system prompt: "produce a single concise sentence, max 20 words, summarizing the core complaint"), embed the summary, cluster, evaluate.

We tested three embedding models:

- **all-MiniLM-L6-v2** (384 dimensions, 256 token context).
- **BGE-base-en-v1.5** (768 dimensions, 512 token context).
- **nomic-embed-text-v1.5** (768 dimensions, 8,192 token context).

Statistical significance was assessed via bootstrap resampling (1,000 iterations, 80% subsample per iteration). We report one-sided $p$-values testing whether summary embeddings produce higher V-measure than raw embeddings. A one-sided test is appropriate because our hypothesis is directional: we predict summaries improve clustering on noisy text, and we separately test the negative direction on structured text.

## Ablations and Controls

**Prompt ablation.** Complaint-focused versus neutral summary prompt, measuring how much improvement is prompt-dependent versus inherent to summarization.

**Paraphrase control.** Two full-length rewrite variants (one removing emotional language, one preserving tone), isolating normalization from compression.

**Extractive baselines.** Four methods (TF-IDF, TextRank, LexRank, LSA) that select the most informative sentence without LLM rewriting.

**Clustering robustness.** Agglomerative clustering (Ward linkage) in addition to KMeans.

# Results

## Summaries Improve Clustering on Noisy Informal Reviews

| Product | Model | Raw V | Sum V | $\Delta$ | 95% CI | $p$ |
|---|---|---|---|---|---|---|
| Fire TV Stick | MiniLM | 0.267 | 0.411 | +0.143 | [+0.113, +0.241] | <0.001 |
| Fire TV Stick | BGE | 0.257 | 0.438 | +0.181 | [+0.137, +0.266] | <0.001 |
| Fire TV Stick | Nomic | 0.254 | 0.440 | +0.187 | [+0.085, +0.241] | <0.001 |
| Fitbit Charge | MiniLM | 0.239 | 0.514 | +0.275 | [+0.153, +0.331] | <0.001 |
| Fitbit Charge | BGE | 0.303 | 0.565 | +0.261 | [+0.083, +0.312] | <0.001 |
| Fitbit Charge | Nomic | 0.349 | 0.519 | +0.170 | [+0.065, +0.269] | <0.001 |
| Senso Headphones | MiniLM | 0.274 | 0.431 | +0.157 | [+0.081, +0.226] | <0.001 |
| Senso Headphones | BGE | 0.310 | 0.498 | +0.189 | [+0.079, +0.243] | <0.001 |
| Senso Headphones | Nomic | 0.362 | 0.445 | +0.083 | [+0.025, +0.178] | 0.009 |

Table 1: V-measure comparison (1,000-iteration bootstrap). All 9 conditions are significant.

ARI improvements were of similar magnitude (+0.10 to +0.35; see Appendix). The largest improvements appeared on Fitbit Charge, where reviews tend to be particularly narrative-heavy. Agglomerative clustering (Ward linkage) confirmed the same pattern in all 9 conditions (deltas +0.044 to +0.267).

![**Figure 1.** UMAP projections of raw review embeddings (left) versus LLM summary embeddings (right) for Fire TV Stick reviews, colored by complaint type (BGE-base-en-v1.5). Raw embeddings exhibit diffuse, overlapping structure; summary embeddings show visible regional clustering by category.](figures/umap_comparison_bge.png)

Figure 1 illustrates the geometric shift. Figure 2 shows the same pattern across all three products. Note that UMAP's nonlinear scaling can make clusters appear visually tighter when centroids separate, even when within-class distances are unchanged in the original high-dimensional space; the direct cosine similarity measurements in Table 3 are the primary geometric evidence.

![**Figure 2.** UMAP projections across all three products, raw versus summary embeddings, BGE-base-en-v1.5. All p < 0.001.](figures/umap_all_products.png)

## Mechanism Ablations

To isolate the mechanism, we tested conditions that separate compression from normalization on the Fire TV Stick dataset (BGE-base-en-v1.5):

| Condition | Words | V-measure | vs Raw |
|---|---|---|---|
| Raw text | 65 | 0.257 | --- |
| Paraphrase (remove emotion) | 46 | 0.240 | -0.018 |
| Paraphrase (preserve tone) | 50 | 0.226 | -0.032 |
| TextRank (extractive) | 21 | 0.164 | -0.093 |
| LexRank (extractive) | 15 | 0.172 | -0.085 |
| LSA (extractive) | 17 | 0.166 | -0.091 |
| TF-IDF best sentence | 20 | 0.173 | -0.084 |
| LLM summary (abstractive) | 9 | 0.438 | +0.181 |

Table 2: Mechanism ablation. Neither normalization without compression nor selection without normalization reproduced the gains.

Full-length paraphrasing produced no improvement under either formulation ($p$ = 0.43 and 0.44). Extractive sentence selection performed consistently below raw text across all four methods (V = 0.16--0.17). These methods preserve the original author's phrasing; even when they identify the right content, the idiosyncratic wording prevents embedding convergence across reviews describing the same complaint type.

To illustrate: a raw review (61 words)---*"I bought this three weeks ago and it has already froze up. I googled it and it seems everybody has the same problem. You have to power down to reboot. We used to laugh at equipment that needed a 'MASTER' reset when I was in the Navy. Come on Amazon, you can do better than this!"*---becomes an 8-word summary: *"Device freezes frequently; requires power resets to reboot."* The summary strips the anecdote, normalizes vocabulary, and foregrounds the complaint type.

A prompt ablation showed that a neutral prompt ("summarize this review") captured 85% of the improvement achieved by the complaint-focused prompt, consistent with the compression constraint encouraging aspect prioritization even without explicit task steering.

## Geometric Effect: Centroid Separation

| Product | Condition | Intra-class sim | Inter-centroid sim | W/B ratio |
|---|---|---|---|---|
| Fire TV Stick | Raw | 0.638 | 0.930 | 5.18 |
| Fire TV Stick | Summary | 0.641 | 0.873 | 2.83 |
| Fitbit Charge | Raw | 0.671 | 0.921 | 4.15 |
| Fitbit Charge | Summary | 0.659 | 0.847 | 2.23 |
| Senso Headphones | Raw | 0.647 | 0.923 | 4.59 |
| Senso Headphones | Summary | 0.643 | 0.858 | 2.51 |

Table 3: Embedding space geometry (BGE-base-en-v1.5). Pattern confirmed across all three embedding models (Appendix E).

Intra-class cosine similarity remains approximately constant (deltas -0.01 to +0.003). Inter-centroid cosine similarity drops by 0.06--0.07. The within/between distance ratio approximately halves across all products.

TF-IDF bag-of-words clustering on summaries (V = 0.32) outperforms TF-IDF on raw text (V = 0.15), indicating vocabulary normalization. However, embedding-based clustering of summaries (V = 0.44) exceeds TF-IDF on summaries, confirming the benefit extends beyond shared vocabulary.

## Long-Context Models

The persistence of the effect with nomic-embed-text-v1.5 (8,192 token context, comfortably exceeding review length) suggests the gains are not primarily explained by input truncation. The improvement is slightly larger on the long-context model ($\Delta$ = +0.187) than on the short-context model ($\Delta$ = +0.143), a pattern inconsistent with a truncation-only explanation.

## Boundary Condition: Structured Text

On the CFPB consumer complaints dataset, summaries consistently degraded clustering. V-measure deltas were negative across all three embedding models (e.g., BGE: -0.036 on mortgage, -0.031 on checking; Nomic: -0.127 on mortgage). Most conditions were negative, and none significantly favored summaries.

CFPB complaints are structured and factual. Complainants state their issue directly, and distinguishing details---dollar amounts, company names, regulatory citations---carry discriminative signal. One-sentence summaries collapse distinct issue types that differ only in specifics.

# Discussion

## Mechanism

Our ablations suggest the clustering improvement depends on two co-occurring operations. Compression forces prioritization among candidate aspects: a review mentioning WiFi problems, a broken remote, and general disappointment must be distilled to one or two points. Expression normalization ensures that two different phrasings of the same complaint produce similar output. In our experiments, neither operation alone reproduced the gains.

The geometric signature is centroid separation rather than cluster compaction. Summarization does not substantially change within-class similarity but makes different categories more distinguishable. Per-class analysis reveals that specific complaint types (voice recognition: +0.034 intra-class delta; remote control: +0.031) show the largest within-class tightening, while broader categories (content availability: -0.040) show slight decreases, suggesting the benefit is largest for well-defined complaint types.

## Scope and Boundary Conditions

Our evidence supports a pattern for noisy informal complaint-like text---product reviews where the clustering target (complaint type) is the primary content. We expect the effect to generalize to similar informal feedback domains (app reviews, support tickets, social media), but our experiments do not test all informal text or all clustering settings.

The coarse-graining tradeoff deserves attention. Summarization may improve global separability while reducing local resolution within clusters. Inside "WiFi and Connectivity Issues," raw text may preserve distinctions among intermittent disconnects, router compatibility problems, and authentication errors that a short summary collapses. One direction for future work is embedding the summary and raw text together---the summary as a semantic anchor, the raw text preserving fine-grained detail.

## Limitations

**Label validity.** Amazon labels are LLM-generated. Mitigated by cross-model validation ($\kappa = 0.75$), significant improvement on human-labeled app reviews ($p < 0.05$ on all three models), and qualitative audit. LLM-derived taxonomies may underrepresent categories requiring pragmatic reasoning.

**Same-LLM bias.** Claude Haiku labels and summarizes. Mitigated by human-label corroboration, GPT-5-mini relabeling, CFPB failure, neutral prompt ablation, and multiple embedding models.

**Single summarization model.** Only Claude Haiku tested.

**Embedding model recency.** Models from 2021--2023.

**Single-label assumption.** Some reviews express multiple complaint types, placing a ceiling on achievable V-measure (plateau at 0.4--0.5 for both conditions).

**Prompt ablation scope.** Tested only when the clustering target aligns with primary content. When the target is peripheral (e.g., clustering abstracts by methodology), prompt specificity may matter more.

## Deployment Considerations

In a production feedback-analysis pipeline, summarization-before-embedding slots in as a preprocessing step between ingestion and indexing. When new reviews or support tickets arrive, each document is summarized (one LLM call per document, batched for efficiency), then embedded and added to the vector index. Downstream clustering, topic discovery, and issue-triage workflows operate on the summary embeddings without modification.

The operational cost is modest. Using Claude Haiku at current pricing, summarizing 1,000 documents costs approximately \$0.05 and takes roughly 2 minutes.[^cost] At 100,000 documents the cost is under \$5 and completes in approximately 3.5 hours; this can be parallelized across batches. Embedding with a local model adds roughly 10 seconds per 1,000 documents. The summarization step is index-time only---retrieval and clustering latency are unchanged.

[^cost]: Cost and timing estimates assume reviews averaging 66 words (~90 tokens), batched 20 per API call with ~2,300 input tokens and ~300 output tokens per batch, at $0.25/M input and $1.25/M output tokens. Timing was measured on our Fire TV Stick dataset (859 reviews, 43 batches, ~2.5 seconds per call).

The practical payoff is improved issue discovery. Product teams clustering customer feedback to identify recurring complaints, support organizations triaging incoming tickets by issue type, or analysts grouping app store reviews for trend analysis would benefit from cleaner cluster boundaries. The approach is most valuable when the input text is informal and varied---the exact regime where embedding models struggle most with unsupervised organization.

Practitioners should not apply this to structured or semi-structured text (e.g., financial complaints, medical records, legal documents) where fine-grained details carry discriminative signal, as our CFPB experiments show degradation in that regime.

# Conclusion

Abstractive summarization improves embedding-based clustering of noisy informal text through compression-forced aspect selection and expression normalization, yielding embeddings with greater inter-class separation. The intervention is low-complexity---a single summarization call per document at index time, with no changes to downstream clustering infrastructure. The effect reaches significance across three products, three models, and 9 of 9 conditions, with corroboration on human-labeled data. On structured text, the same transformation degrades clustering---a boundary condition that distinguishes this contribution from a generic claim about LLM preprocessing.

Future work should test whether the effect holds when the clustering target is peripheral to primary content, whether combining summary and raw embeddings preserves both global separability and local resolution, and whether the effect persists with instruction-tuned or newer embedding architectures.

# Code Availability

We release code for dataset construction, summarization, embedding, clustering, evaluation, and figure generation, together with prompts and taxonomy files, at https://github.com/claycantrell/llm-summary-embeddings.
