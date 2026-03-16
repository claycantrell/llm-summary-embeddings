# Research Outline

## Working Title
LLM Rewriting as Geometric Transformation: How Summarization Reshapes Embedding Space for Improved Clustering

## Research Question
Does LLM rewriting systematically change the geometry of embedding space in ways that improve unsupervised structure, and when does that transformation help versus destroy signal?

## Thesis Statement
LLM summarization can improve embedding-based clustering not by adding new information, but by rewriting semantically equivalent noisy texts into a more geometrically clusterable form. The mechanism requires both compression (forcing the LLM to select salient content) and normalization (rewriting that content into canonical language) — neither alone is sufficient. This interaction between LLM rewriting and embedding space geometry is observed across three embedding models spanning short to long context windows and across three consumer product domains, and has clear boundary conditions: it improves clustering on noisy informal text but degrades it on structured text where surface details carry discriminative signal.

## I. Introduction
- Embedding models compress text into fixed-dimensional vectors, but noisy informal text (reviews, feedback, social media) produces scattered embedding spaces where semantically similar documents land far apart
- Motivating example: two Amazon reviews about the same product defect, written in completely different styles, produce distant embeddings despite identical complaint types
- Prior work studies LLM rewriting as a way to improve downstream matching or retrieval, but does not analyze whether rewriting systematically changes the geometry of embedding space in ways that improve unsupervised structure, nor when that transformation helps versus destroys signal
- The novelty is the interaction between LLM rewriting and embedding space geometry: the LLM adds no new information, but transforms text into a form that embedding models can organize more effectively
- Our finding: a single LLM summarization step improves V-measure by +0.08 to +0.28 (49–115% relative improvement) on informal product reviews, reaching significance across 3 products and 3 embedding models spanning short to long context windows (9 of 9 tests, p < 0.05)
- The effect requires both compression and normalization: full-length paraphrasing produces no improvement, and extractive selection without rewriting also fails. The compression constraint forces salience selection; the rewriting normalizes surface expression
- The effect is largely attributable to generic summarization rather than prompt-specific extraction (neutral prompt captures 85% of the improvement) — because the compression constraint already forces salience selection even without explicit steering
- The effect does NOT hold on structured/factual text (CFPB complaints) — the transformation can also destroy discriminative signal, establishing a clear boundary condition

## II. Related Work
- **Summarization for retrieval**: RAPTOR (Sarthi et al., 2024) — recursive summarization for tree-organized retrieval. Closest to our work but focused on retrieval accuracy over long documents, not cluster quality on short noisy text
- **Query-side generation**: HyDE (Gao et al., 2023) — generates hypothetical documents from queries. Complementary approach (they transform the query, we transform the document)
- **Retrieval granularity**: Dense X Retrieval (Chen et al., 2024) — proposition-level embeddings. Explores finer granularity; our approach goes coarser via summarization
- **Text enrichment**: LLM-based text enrichment and rewriting for embeddings (2024) — directly tests LLM rewriting but measures retrieval benchmarks, not clustering
- **LLM-augmented retrieval**: Doc-level embedding via LLM augmentation (Wu & Cao, 2024) — generates synthetic queries/titles. Similar spirit but different mechanism
- **Gap**: Prior work treats LLM rewriting as a preprocessing step for supervised matching tasks (retrieval, classification) and evaluates it in terms of downstream task accuracy. No work analyzes whether LLM rewriting systematically changes the geometry of embedding space — whether it makes unsupervised structure more or less recoverable. And no work establishes boundary conditions for when the geometric transformation helps versus destroys discriminative signal. This paper connects the LLM rewriting literature with the embedding space geometry literature, two domains usually evaluated independently

## III. Method
### Dataset Construction
- Single-product Amazon reviews (Fire TV Stick, Fitbit Charge, Senso BT Headphones) — 1-3 star reviews
- Three-phase labeling pipeline: (1) taxonomy discovery from held-out sample, (2) labeling against fixed taxonomy, (3) balancing and quality filtering
- Summary and labeling prompts are independent — no circularity
- Independent corroboration dataset: app reviews with human-created labels (Maalej et al.)
- Negative control dataset: CFPB consumer complaints (structured, factual text)

### Experimental Design
- **Condition A**: Embed raw review text → KMeans cluster → evaluate against ground truth labels
- **Condition B**: Summarize each review with Claude Haiku (max 20 words) → embed summary → cluster → evaluate
- Three embedding models: all-MiniLM-L6-v2 (384d, 256 tok), BGE-base-en-v1.5 (768d, 512 tok), nomic-embed-text-v1.5 (768d, 8192 tok)
- Metrics: V-measure, Adjusted Rand Index, Silhouette Score
- Statistical testing: Bootstrap resampling (100 iterations, 80% subsample), one-sided p-values

### Ablations and Controls
- **Prompt ablation**: Complaint-focused ("what went wrong?") vs neutral ("summarize this review") — measures how much improvement is prompt-dependent vs inherent to summarization
- **Paraphrase control**: "Rewrite clearly in plain English, keep all information, don't shorten" — isolates normalization from compression. If normalization alone is sufficient, paraphrase should also improve clustering
- **Extractive baselines**: TF-IDF best sentence, longest sentence — tests whether content selection without LLM rewriting is sufficient
- **Clustering robustness**: Agglomerative clustering (Ward linkage) alongside KMeans to show the effect is not algorithm-specific

### Representation Analysis
- Direct geometric measures to support the "embedding space geometry" claim:
  - Average intra-class cosine similarity before/after summarization
  - Inter-class centroid separation
  - Within/between cluster distance ratios
- These supplement V-measure and ARI with direct evidence about embedding space structure

## IV. Results
### Primary Finding: Summaries improve clustering on informal text
- Fire TV Stick (859 reviews, 9 categories): V-measure improves by +0.14 to +0.19 across three models (all p < 0.001)
- Fitbit Charge (454 reviews, 7 categories): V-measure improves by +0.17 to +0.28 across three models (all p < 0.001)
- Senso Headphones (813 reviews, 10 categories): V-measure improves by +0.08 to +0.19 across three models (all p < 0.05)
- 9 of 9 model-product combinations reach significance
- UMAP visualizations illustrate the geometric shift (raw embeddings exhibit diffuse structure; summary embeddings show regional clustering by complaint type). Used as illustration, not as primary evidence

### Effect persists with long-context models
- The persistence of the effect with nomic-embed-text-v1.5 (8192 token context) suggests the gains are not primarily explained by input truncation, and are more consistent with representational normalization than mere capacity recovery
- Long context does not guarantee perfect use of all context — but the fact that the effect holds (and in some cases grows) with a model that faces no truncation pressure shifts the burden of proof away from the truncation explanation
- Effect actually increases with model capability on Fire TV Stick, suggesting larger models may encode MORE surface variation, not less

### Negative control: structured text
- CFPB complaints: summaries consistently hurt clustering (both across-category and within-category)
- Structured text contains distinguishing factual details that summaries strip away
- Boundary condition: summaries help when signal is buried in noise, hurt when specifics ARE the signal

### Mechanism: compression-forced salience selection + normalization
- **Paraphrase (full-length rewrite) does not improve clustering** (V=0.240 vs raw V=0.257, p=0.43). Normalization without compression is not sufficient
- **Extractive selection does not improve clustering** (TF-IDF best sentence V=0.183, below raw). Selection without normalization is not sufficient
- **LLM summary improves clustering** (V=0.438, p<0.001). Both selection and normalization together are required
- The compression constraint is load-bearing: it forces the LLM to make salience judgments, choosing one thing to say about the review. That forced choice creates discriminative structure
- Neutral prompt captures 85% of complaint-focused improvement — because the compression constraint already forces salience selection even without explicit task steering
- Caveat: the prompt-specificity ratio likely shifts when the clustering target is peripheral to the text's primary content (future work)

### Corroboration with human labels
- App reviews dataset (Maalej et al.): human-labeled categories, 4 classes
- Summaries significantly improve clustering (p = 0.02 on BGE)
- Validates the effect independently of LLM labeling

## V. Discussion
### What the LLM is doing: compression-forced salience selection + normalization
- The LLM summary performs two operations that must co-occur:
  - **Salience selection via compression**: The word limit forces the LLM to choose what matters — which aspect of the review to preserve. This forced choice creates discriminative structure that embedding models can exploit
  - **Surface normalization**: The rewriting translates diverse expressions into canonical language — stripping emotion, normalizing vocabulary, converting implicit complaints into explicit statements
- Neither operation alone is sufficient (demonstrated by paraphrase and extractive ablations)
- The geometric effect is primarily **centroid separation** (inter-class similarity drops from 0.93 to 0.87) rather than cluster compaction (intra-class similarity unchanged). The LLM makes different categories more distinguishable, not same-category documents more similar
- The embedding improvement (V=0.44) exceeds keyword-only improvement (TF-IDF V=0.32), confirming the benefit is not purely lexical

### When it works vs when it doesn't
- Works: informal, noisy, emotional text where the latent structure is obscured by writing style variation
- Doesn't work: structured, factual text where the distinguishing details are in the specifics
- The key variable is signal-to-noise ratio in the text relative to the clustering target

### Limitations
- **Label validity** (primary vulnerability): Amazon labels are LLM-generated. Summaries and labels may share latent assumptions; taxonomy may reflect the summarizer's worldview; improvement may partly reflect alignment to the labeling scheme rather than true semantic structure. Mitigated by human-labeled app reviews corroboration, but human validation of a subset of Amazon labels would strengthen the claim substantially
- **Same-LLM bias**: Claude Haiku labels and summarizes. Mitigated by four converging lines of evidence (human labels, CFPB failure, prompt ablation, multiple embedding models) but not fully resolved. Testing with a second summarization model would help
- **Single summarization model**: Only Claude Haiku tested. Effect with other LLMs (GPT-4o-mini, open-source models) unknown
- **Cost**: Requires one LLM call per document at index time
- **Prompt ablation scope**: Tested only when clustering target aligns with primary content. Ratio of generic vs prompt-specific benefit may differ for peripheral targets

### Practical implications
- For anyone clustering customer feedback, support tickets, reviews, or social media: summarize first, then embed
- No prompt engineering required — generic summarization works
- Works with any embedding model, including small/cheap ones
- Index-time cost only — retrieval/clustering is unchanged

## VI. Conclusion
- LLM summarization improves embedding-based clustering not by adding information but by rewriting noisy text into a more geometrically clusterable form through compression-forced salience selection combined with surface normalization
- The effect is observed across 3 products, 3 embedding models spanning short to long context windows, and 9 of 9 tests reaching significance, with independent corroboration on human-labeled data
- The effect has clear boundaries: doesn't help on structured text
- The effect is largely attributable to the compression constraint forcing salience selection rather than prompt-specific extraction (neutral prompt captures 85%); full-length normalization without compression produces no improvement
- Future work: test when prompt specificity matters (peripheral content targets), validate with different LLMs, test on other informal text domains (social media, support chat)

---
**Target venue:** arXiv preprint (initially), then EMNLP or ACL Findings
**Target length:** 6000-8000 words
**Key deadlines:** None — move at our pace
