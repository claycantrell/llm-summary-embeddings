---
title: "LLM Rewriting as Geometric Transformation: How Summarization Reshapes Embedding Space for Improved Clustering"
author:
  - name: "Clay Cantrell"
    affiliation: "Independent Researcher"
    email: "clay.cantrell@me.com"
date: "March 2026"
abstract: |
  Embedding models map text to fixed-dimensional vectors, but noisy informal text---such as product reviews, social media posts, and customer feedback---produces embedding spaces where semantically equivalent documents are scattered by surface-level variation in writing style, emotional tone, and narrative structure. We show that a single LLM abstractive summarization step substantially improves embedding-based cluster quality on such text, improving V-measure by 0.08--0.28 (49--115\% relative improvement) across three consumer product review datasets and three embedding models spanning short to long context windows (9 of 9 tests, $p < 0.05$). We identify a two-part mechanism: the compression constraint forces prioritization among candidate aspects of the text, while the rewriting normalizes surface expression into canonical form. In our experiments, neither full-length paraphrasing nor extractive selection alone reproduced the gains. Direct geometric analysis shows the effect operates primarily through increased inter-class centroid separation rather than within-class compaction. The effect has clear boundary conditions: it does not improve clustering on structured text (consumer financial complaints), where fine-grained surface details carry discriminative signal. These results are independently corroborated on a dataset with human-created labels and validated through cross-model labeling with GPT-5-mini (Cohen's $\kappa = 0.75$).
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

Text embedding models compress documents into fixed-dimensional vector representations, enabling downstream tasks such as retrieval, classification, and clustering through geometric operations in the embedding space. However, when applied to noisy informal text---product reviews, social media posts, customer feedback, forum discussions---these models face a fundamental challenge: semantically equivalent documents can produce distant embeddings due to variation in writing style, emotional tone, narrative structure, and incidental detail.

Consider two one-star Amazon reviews about the same product defect. One reviewer writes a three-paragraph narrative about their frustration, mentioning the defect in passing; the other states the problem in a single blunt sentence. Despite describing the same complaint, these reviews may land in different regions of the embedding space because the embedding model encodes everything---the emotion, the narrative, the complaint---into a single vector. The semantic signal (what went wrong) is diluted by surface-level variation (how it was expressed).

Prior work has explored LLM-based text rewriting as a preprocessing step for improving retrieval and classification. RAPTOR [@sarthi2024raptor] recursively summarizes and clusters text chunks into a hierarchical tree for retrieval. HyDE [@gao2023hyde] generates hypothetical answer documents from queries to improve zero-shot dense retrieval. LLM-Augmented Retrieval [@wu2024llmaugmented] enriches documents with synthetic queries and titles for doc-level embeddings. Text enrichment approaches [@enrichment2024] use LLMs to rewrite text before embedding to improve benchmark performance. These approaches treat rewriting as a way to improve supervised downstream matching, evaluating in terms of retrieval recall, NDCG, or classification accuracy.

We are not aware of prior work that directly evaluates whether LLM rewriting systematically changes the *geometry* of embedding space---whether it makes unsupervised structure more or less recoverable---or that establishes boundary conditions for when such transformations help versus destroy discriminative signal. This paper connects the LLM rewriting literature with the embedding space geometry literature, two domains usually studied independently.

We show that a single LLM summarization step improves V-measure by +0.08 to +0.28 (49--115% relative improvement) on informal product reviews, reaching significance across three products and three embedding models spanning short to long context windows (9 of 9 tests, $p < 0.05$). We trace the effect to two co-occurring operations: the compression constraint encourages aspect prioritization, while the rewriting normalizes varied surface forms into canonical language. Neither paraphrasing nor extractive selection alone reproduced the gains. Geometric analysis of the embedding space shows the improvement manifests as increased distance between class centroids, not tighter clusters. On structured text, where fine-grained details carry discriminative signal, the same transformation degrades performance.

This paper makes three contributions:

1. We show that abstractive summarization consistently improves clustering of noisy informal text across three products and three embedding models.
2. We identify a two-part mechanism: compression forces aspect prioritization while rewriting normalizes expression, with the geometric effect manifesting primarily as increased centroid separation.
3. We establish a boundary condition: the same transformation degrades clustering on structured text where specifics rather than semantics distinguish categories.

# Related Work

## LLM Rewriting for Retrieval

Several recent approaches use LLMs to transform text before or during retrieval. RAPTOR [@sarthi2024raptor] recursively clusters and summarizes text chunks, building a tree of abstractions for multi-level retrieval. This is the closest prior work to ours, but it targets retrieval accuracy on long documents rather than cluster quality on short noisy text. HyDE [@gao2023hyde] takes a complementary approach, transforming the *query* rather than the document: it generates hypothetical answer documents and embeds those for zero-shot retrieval. LLM-Augmented Retrieval [@wu2024llmaugmented] generates synthetic queries and titles from documents, assembling them into enriched doc-level embeddings that improve performance on LoTTE and BEIR benchmarks. Text enrichment and rewriting approaches [@enrichment2024] use LLMs to add context and correct inaccuracies before embedding, showing gains on selected MTEB tasks.

## Retrieval Granularity

Dense X Retrieval [@chen2024densex] examines what unit of text should be embedded for retrieval, comparing passage-level, sentence-level, and proposition-level representations. They find that finer-grained proposition-level embeddings outperform passage-level for downstream QA tasks. Our work explores the opposite direction on the granularity axis: rather than decomposing documents into finer units, we compress them into coarser summaries, and rather than measuring retrieval, we measure clustering.

## Gap

The work above evaluates LLM rewriting in terms of supervised downstream accuracy (retrieval recall, NDCG, classification). This paper asks a different question: does rewriting change the *geometry* of embedding space in ways that make unsupervised structure more or less recoverable, and when does that transformation help versus destroy signal?

# Method

## Datasets

### Amazon Product Reviews (Primary)

We constructed labeled datasets from Amazon product reviews (McAuley Lab, 2023) for three consumer electronics products: Fire TV Stick with Alexa Voice Remote (859 reviews, 9 complaint categories), Fitbit Charge activity tracker (454 reviews, 7 categories), and Senso Bluetooth headphones (813 reviews, 10 categories). Reviews were filtered to 1--3 star ratings with narrative text of at least 40 characters.

Complaint category labels were generated through a three-phase pipeline designed to avoid circularity between labeling and summarization:

**Phase 1: Taxonomy Discovery.** A held-out sample of 200 reviews was sent to Claude Haiku in batches of 50 with the instruction to identify 8--15 distinct complaint categories. Raw categories from multiple batches were merged into a final taxonomy of 9--11 categories per product.

**Phase 2: Labeling.** The remaining reviews were labeled against the fixed taxonomy in batches of 50 using structured outputs (tool use). Each review received a category assignment and a confidence rating (high, medium, or low). Low-confidence labels were excluded.

**Phase 3: Balancing.** Categories with fewer than 30 reviews were dropped. Remaining categories were capped at 100 reviews each.

The labeling prompt and the summarization prompt are independent: the labeling prompt references the taxonomy and asks for a category assignment; the summarization prompt asks only "what specifically went wrong with the product?" with no mention of categories.

**Cross-model validation.** To assess label quality, we independently re-labeled the Fire TV Stick reviews using GPT-5-mini (OpenAI). The two models agreed on 77.2% of labels (Cohen's $\kappa = 0.747$, indicating substantial agreement). The clustering improvement persisted with GPT-5-mini labels (V-measure $\Delta$ = +0.17, compared to +0.22 with Haiku labels).

**Qualitative audit.** A targeted audit of 121 reviews (50 consensus cases, 71 disagreement cases) found that labels assigned by both models were generally consistent with review content. Model disagreements arose from reviews expressing multiple complaint types rather than from labeling errors, suggesting that the taxonomy captures real structure in the data but that a single-label assumption cannot fully represent multi-faceted reviews.

### App Reviews (Human-Labeled Corroboration)

We used the app review classification dataset from Maalej et al., containing 5,081 reviews from Google Play and Apple App Store with human-assigned labels: problem discovery, feature request, user experience, and rating. We sampled 400 reviews per category (1,600 total) for evaluation.

### CFPB Consumer Complaints (Negative Control)

We sampled 1,000 complaints from the Consumer Financial Protection Bureau database, selecting 500 mortgage complaints and 500 checking/savings account complaints, each spanning 5 issue categories. These complaints are structured, factual, and legalistic---the opposite of noisy informal text.

## Experimental Design

For each dataset, we compared two conditions:

- **Raw text embeddings**: Embed the original review text, cluster with KMeans ($k$ = number of ground truth categories), evaluate against ground truth labels.
- **Summary embeddings**: Summarize each review with Claude Haiku (system prompt: "produce a single concise sentence, max 20 words, summarizing the core complaint"), embed the summary, cluster, evaluate.

We tested three embedding models spanning a range of architectures, dimensionalities, and context windows:

- **all-MiniLM-L6-v2** (384 dimensions, 256 token context): A widely-used small model.
- **BGE-base-en-v1.5** (768 dimensions, 512 token context): A mid-range model with strong MTEB performance.
- **nomic-embed-text-v1.5** (768 dimensions, 8,192 token context): A long-context model whose context window comfortably exceeds the length of all reviews.

Statistical significance was assessed via bootstrap resampling (100 iterations, 80% subsample per iteration). We report one-sided $p$-values testing whether summary embeddings produce higher V-measure than raw embeddings.

## Ablations and Controls

**Prompt ablation.** We compared a complaint-focused summary prompt ("what specifically went wrong with the product?") against a neutral prompt ("summarize this review in one sentence") to measure how much of the improvement is prompt-dependent versus inherent to summarization.

**Paraphrase control.** We generated full-length rewrites using the instruction "rewrite this review in clear, plain English; keep all information; do not shorten." This isolates normalization from compression: if normalization alone drives the improvement, the paraphrase should also improve clustering.

**Extractive baselines.** We tested TF-IDF best-sentence selection and longest-sentence extraction---methods that read the full review and select content without LLM rewriting.

**Clustering robustness.** We verified all primary results with agglomerative clustering (Ward linkage) in addition to KMeans.

## Representation Analysis

To directly assess changes in embedding space geometry, we computed:

- **Intra-class cosine similarity**: Average pairwise cosine similarity among documents within each class.
- **Inter-centroid cosine similarity**: Average cosine similarity between class centroids.
- **Within/between distance ratio**: $(1 - \text{intra-class similarity}) / (1 - \text{inter-centroid similarity})$. Lower values indicate a more clusterable representation.

# Results

## Summaries Improve Clustering on Informal Text

Across all three Amazon product review datasets and all three embedding models, summary embeddings produced higher V-measure and Adjusted Rand Index (ARI) scores than raw text embeddings. All 9 model-product combinations reached statistical significance on V-measure ($p < 0.05$), with 7 of 9 at $p < 0.001$. ARI improvements were of similar magnitude (+0.08 to +0.32). By using reviews of a single product per dataset, we eliminate product-type confounds: the only way to cluster correctly is to understand the complaint type, which is buried in emotional, narrative, and varied language.

| Product | Model | Raw V | Sum V | $\Delta$ | 95% CI | $p$ |
|---|---|---|---|---|---|---|
| Fire TV Stick | MiniLM | 0.267 | 0.411 | +0.144 | [+0.114, +0.223] | <0.001 |
| Fire TV Stick | BGE | 0.257 | 0.438 | +0.181 | [+0.134, +0.270] | <0.001 |
| Fire TV Stick | Nomic | 0.254 | 0.440 | +0.187 | [+0.095, +0.232] | <0.001 |
| Fitbit Charge | MiniLM | 0.239 | 0.514 | +0.276 | [+0.131, +0.340] | <0.001 |
| Fitbit Charge | BGE | 0.303 | 0.565 | +0.262 | [+0.093, +0.300] | <0.001 |
| Fitbit Charge | Nomic | 0.349 | 0.519 | +0.170 | [+0.064, +0.274] | <0.001 |
| Senso Headphones | MiniLM | 0.274 | 0.431 | +0.157 | [+0.086, +0.218] | <0.001 |
| Senso Headphones | BGE | 0.310 | 0.498 | +0.189 | [+0.083, +0.240] | <0.001 |
| Senso Headphones | Nomic | 0.362 | 0.445 | +0.083 | [+0.022, +0.167] | 0.020 |

Table 1: V-measure comparison across products and embedding models. All differences are statistically significant via bootstrap resampling.

The largest improvements appeared on Fitbit Charge (deltas of +0.17 to +0.28), where reviews tend to be particularly narrative-heavy and emotionally varied, suggesting that noisier text benefits more from normalization. The mid-range model (BGE-base-en-v1.5) showed the most consistent improvements across products.

Agglomerative clustering (Ward linkage) confirmed the same pattern: summary embeddings outperformed raw embeddings in all 9 conditions, with deltas ranging from +0.044 to +0.267, confirming the effect is not specific to KMeans' spherical cluster assumption.

## Compression and Normalization Jointly Produce the Observed Gains

To isolate the mechanism, we tested conditions that separate compression from normalization on the Fire TV Stick dataset (BGE-base-en-v1.5):

| Condition | Avg Words | V-measure | vs Raw |
|---|---|---|---|
| Raw text | 65 | 0.257 | --- |
| Paraphrase (full-length rewrite) | 47 | 0.240 | -0.018 ($p$ = 0.43) |
| TF-IDF best sentence (extractive) | 20 | 0.183 | -0.074 |
| LLM summary (abstractive) | 10 | 0.438 | +0.181 ($p$ < 0.001) |

Table 2: Mechanism ablation. Neither normalization without compression (paraphrase) nor selection without normalization (extractive) reproduced the gains.

Full-length paraphrasing---rewriting the review in plain English without shortening---produced no improvement over raw text ($\Delta$ = -0.018, $p$ = 0.43). Extractive selection, which reads the full review and selects the most informative sentence, performed below raw text. Only abstractive summarization, which jointly compresses and normalizes, produced the observed gains. These results suggest that the observed gains depend on the combination of forced prioritization among candidate aspects and expression normalization.

To illustrate, consider a raw review (56 words): *"I am ready to throw this thing away. In the middle of watching shows, it completely stops working. I can sometimes disconnect and reconnect to the internet but most of the time I have to unplug it, plug it back in, wait 30 minutes and then it will work for a short time."* The LLM summary (8 words): *"Device frequently disconnects from internet requiring physical reboot."* The paraphrase (full-length) preserves the narrative structure and emotional tone; the extractive baseline selects a single original sentence with its idiosyncratic phrasing. The abstractive summary strips the narrative, normalizes the vocabulary ("disconnect," "reboot"), and foregrounds the complaint type---producing an embedding that clusters with other WiFi-related complaints regardless of how those complaints were originally expressed.

A prompt ablation further clarified the role of compression: a neutral summary prompt ("summarize this review in one sentence") captured 85% of the improvement achieved by the complaint-focused prompt ("what specifically went wrong?"). This is consistent with the compression constraint effectively encouraging aspect prioritization even without explicit task steering---the word limit alone forces the LLM to select what matters.

## The Geometric Effect Is Centroid Separation

Direct analysis of embedding space geometry reveals that the improvement operates through increased inter-class separation rather than tighter within-class compaction.

| Product | Condition | Intra-class sim | Inter-centroid sim | W/B ratio |
|---|---|---|---|---|
| Fire TV Stick | Raw | 0.638 | 0.930 | 5.18 |
| Fire TV Stick | Summary | 0.641 | 0.873 | 2.83 |
| Fitbit Charge | Raw | 0.671 | 0.921 | 4.15 |
| Fitbit Charge | Summary | 0.659 | 0.847 | 2.23 |
| Senso Headphones | Raw | 0.647 | 0.923 | 4.59 |
| Senso Headphones | Summary | 0.643 | 0.858 | 2.51 |

Table 3: Embedding space geometry (BGE-base-en-v1.5). Intra-class similarity is approximately unchanged; inter-centroid similarity decreases; within/between ratio approximately halves. Pattern confirmed across all three embedding models (see Appendix).

Intra-class cosine similarity remains approximately constant (deltas of -0.01 to +0.003), indicating that summaries do not substantially pull same-class documents closer together. In contrast, inter-centroid cosine similarity drops by 0.06--0.07, indicating that class centroids move apart. The within/between distance ratio approximately halves across all three products, consistent with summarization normalizing each category's reviews into more characteristic, less overlapping language.

To assess the contribution of vocabulary normalization specifically, we computed TF-IDF bag-of-words clustering on both raw and summary text. TF-IDF clustering on summaries (V = 0.32) substantially outperforms TF-IDF on raw text (V = 0.15), indicating that the LLM produces lexically normalized output---converging on canonical terms like "crashes," "freezes," "reboots" for stability complaints and "subscription," "paid," "free" for content complaints. However, embedding-based clustering of summaries (V = 0.44) exceeds TF-IDF on summaries (V = 0.32), confirming that the benefit is not purely lexical---the embedding model captures semantic similarity in the normalized text beyond shared vocabulary.

## Long-Context Models

The persistence of the effect with nomic-embed-text-v1.5 (8,192 token context window, comfortably exceeding review length) suggests the gains are not primarily explained by input truncation and are more consistent with representational transformation than capacity recovery. On the Fire TV Stick dataset, the improvement is slightly larger on the long-context model ($\Delta$ = +0.187) than on the short-context model ($\Delta$ = +0.144), a pattern that would not be expected if the gains were primarily explained by truncation.

## Boundary Condition: Structured Text

On the CFPB consumer complaints dataset, summaries consistently degraded clustering performance. In within-category experiments (500 mortgage complaints and 500 checking account complaints, each clustered by issue type), V-measure deltas were negative across all three embedding models (e.g., BGE: -0.036 on mortgage, -0.031 on checking). In across-category experiments with 10 product types, summaries again underperformed raw text (BGE: -0.100 V-measure). This pattern held for both KMeans and agglomerative clustering. No CFPB condition reached significance in favor of summaries.

CFPB complaints are structured, factual, and legalistic. Complainants state their issue directly, and the distinguishing details---specific dollar amounts, company names, regulatory citations, procedural descriptions---carry discriminative signal. One-sentence summaries like "mortgage servicer failed to process payment" are too generic: they collapse distinct issue types (payment processing, escrow disputes, loan modification) that differ only in specifics. Notably, the degradation is most pronounced on the long-context model (Nomic: -0.127 on mortgage), whose ability to process fine-grained details is an advantage that summarization removes.

This establishes a clear boundary condition: abstractive summarization improves clustering when the semantic signal is obscured by surface variation, but degrades it when surface details carry discriminative signal.

## Corroboration with Human Labels

On the app reviews dataset [@maalej2016], which contains human-assigned labels for four review types (problem discovery, feature request, user experience, rating), summary embeddings significantly improved clustering on the BGE model (V-measure $\Delta$ = +0.049, $p$ = 0.02). This result validates the effect independently of LLM-generated labels.

# Discussion

## Mechanism: Compression-Forced Aspect Selection and Expression Normalization

Our ablation results suggest that the clustering improvement depends on two co-occurring operations. The compression constraint---a word limit that forces the LLM to produce a concise output---encourages prioritization among candidate aspects of the text. A review that mentions WiFi problems, a broken remote, and general disappointment must be distilled to one or two salient points. This forced choice creates discriminative structure: reviews about WiFi problems converge on WiFi-related summaries while reviews about remote issues converge on remote-related summaries. Expression normalization---the rewriting that translates varied surface forms into canonical language---ensures that two different phrasings of the same complaint produce similar output.

In our experiments, neither operation alone reproduced the gains. Full-length paraphrasing normalizes expression but, without compression, preserves the full mixture of aspects, leaving the embedding as diffuse as before. Extractive selection compresses by choosing a single sentence but, without normalization, preserves the original author's idiosyncratic phrasing. Abstractive summarization does both.

The geometric signature of this process is centroid separation rather than cluster compaction. Summarization does not make same-category documents much more similar to each other---intra-class cosine similarity is approximately unchanged. This pattern is consistent with summarization making categories more distinguishable by normalizing reviews into more characteristic, less overlapping language. The category centroids move apart in embedding space while cluster spread remains stable.

Per-class analysis reveals further nuance. Categories with highly specific, distinctive complaints---such as voice recognition problems (+0.034 intra-class similarity delta) and remote control malfunction (+0.031)---show the largest within-class tightening, as summaries converge these reviews onto canonical descriptions. Broader categories such as content availability issues (-0.040) and WiFi connectivity (-0.019) show slight decreases in intra-class similarity, suggesting that summaries may normalize away distinguishing nuance within categories that encompass a wider range of specific complaints. This per-class variation does not undermine the overall effect but suggests that the benefit is largest for well-defined, specific complaint types.

## When It Works and When It Doesn't

The effect depends on the relationship between surface variation and semantic signal in the text:

- **Informal, noisy text** (product reviews, app feedback): Surface variation---emotional language, narrative tangents, sarcasm, varied phrasing---obscures the underlying semantic structure. Summarization strips this variation, revealing the latent category structure.
- **Structured, factual text** (financial complaints): Surface details---company names, dollar amounts, regulatory language, procedural descriptions---are themselves the discriminative signal. Summarization removes these details, collapsing distinct categories.

The key variable is the signal-to-noise ratio relative to the clustering target. When the target dimension (complaint type) is buried in surface noise, summarization helps by extracting it. When the target dimension is expressed through surface detail, summarization hurts by removing it.

## Limitations

**Label validity.** Amazon review labels are LLM-generated. This concern is mitigated by cross-model validation (GPT-5-mini independently confirms the effect with $\kappa = 0.75$), human-labeled app reviews corroboration ($p = 0.02$), and author review suggesting consensus labels are generally accurate, with disagreements reflecting multi-label ambiguity. However, LLM-derived taxonomies may underrepresent categories requiring pragmatic or contextual reasoning beyond current model capabilities.

**Single-label assumption.** Manual review revealed that some reviews express multiple complaint types. The single-label taxonomy places a ceiling on clustering performance, likely contributing to the V-measure plateau in the 0.4--0.5 range observed across both raw and summary conditions.

**Same-LLM bias.** Claude Haiku was used for both labeling and summarization of the Amazon review datasets. Its internal biases could create artificial alignment between labels and summaries. This concern is mitigated by four converging lines of evidence: (1) the effect holds with human-created labels on app reviews ($p = 0.02$); (2) the effect persists with independent GPT-5-mini labels ($\Delta$ = +0.17); (3) the effect fails on CFPB data, which would not be expected if same-model alignment were the primary driver; and (4) a neutral summary prompt with no task awareness captures 85% of the improvement. We verified that only 0.6% of summaries contain exact taxonomy phrases, reflecting natural language overlap rather than prompt leakage. Nevertheless, full resolution would require testing with a second summarization model.

**Single summarization model.** Only Claude Haiku was tested for summarization. The effect with other LLMs or open-source models is unknown.

**Paraphrase control sensitivity.** The paraphrase result may depend on the specific instruction used. Alternative formulations could yield different results.

**Embedding model recency.** Our experiments used embedding models from 2021--2023. Whether the effect persists with more recent architectures (e.g., Gemini Embedding, Qwen3-Embedding) remains an open question.

**Prompt ablation scope.** The prompt ablation was tested only when the clustering target aligns with the primary content of the text---in product reviews, the complaint type IS the primary content. We expect the ratio of generic to prompt-specific benefit to shift substantially when the clustering target is peripheral to the main content. For example, clustering academic abstracts by methodology rather than topic, support emails by product version rather than issue type, or medical notes by patient affect rather than diagnosis. In these cases, a generic summary would foreground the primary content and lose the target dimension, making prompt design critical rather than optional.

## Practical Implications

For practitioners clustering customer feedback, support tickets, reviews, or social media: summarize each document before embedding. Generic summarization (no task-specific prompt engineering) captures the majority of the benefit. The approach works across all three tested embedding models, including a small model suitable for resource-constrained settings. The cost is one LLM call per document at index time; retrieval and clustering operations are unchanged.

# Conclusion

We have shown that LLM abstractive summarization improves embedding-based clustering of noisy informal text by jointly performing aspect selection and expression normalization, yielding embeddings with greater inter-class separation. The effect is observed across three consumer product review datasets, three embedding models spanning short to long context windows, and 9 of 9 model-product combinations reaching statistical significance ($p < 0.05$), with independent corroboration on human-labeled data and cross-model label validation.

The improvement has a clear geometric signature: category centroids move apart while within-class spread remains stable, with the within/between distance ratio approximately halving across all tested products. The compression constraint appears critical: full-length normalization without compression does not reproduce the gains, suggesting that forced prioritization among candidate aspects is an important component of the mechanism in our setting.

The effect has equally clear boundaries. On structured text where fine-grained specifics distinguish categories, summarization collapses rather than clarifies the underlying structure. This asymmetry---the same operation that reveals latent structure in noisy text destroys it in precise text---grounds the contribution in a concrete, falsifiable characterization of when rewriting helps.

Several directions remain for future work. First, we hypothesize that the ratio of generic to prompt-specific benefit shifts substantially when the clustering target is peripheral to the text's primary content---for example, clustering academic abstracts by methodology rather than topic, or medical notes by patient affect rather than diagnosis. In such cases, a generic summary would foreground the primary content and lose the target dimension, making prompt design critical rather than optional. Second, extending the evaluation to multi-label assignment could better capture the complexity of real-world text and raise the performance ceiling. Third, the interaction between pre-embedding rewriting and instruction-tuned embedding models presents an open question: if the embedding model can itself be directed to focus on specific aspects, does LLM rewriting remain beneficial, or does instruction-tuning make it redundant? Finally, testing with current state-of-the-art embedding models would establish whether the effect persists or diminishes as encoders become more capable.
