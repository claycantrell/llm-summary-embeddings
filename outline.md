# Research Outline

## Working Title
LLM Rewriting as Geometric Transformation: How Summarization Reshapes Embedding Space for Improved Clustering

## Research Question
Does LLM rewriting systematically change the geometry of embedding space in ways that improve unsupervised structure, and when does that transformation help versus destroy signal?

## Thesis Statement
Abstractive summarization improves clustering of noisy informal text because it jointly performs aspect selection and expression normalization, yielding embeddings with greater inter-class separation. The mechanism requires both compression (forcing prioritization among candidate aspects) and normalization (rewriting selected content into canonical language) — in our experiments, neither full-length paraphrasing nor extractive selection reproduced the gains from abstractive summarization. This interaction between LLM rewriting and embedding space geometry is observed across three embedding models spanning short to long context windows and across three consumer product domains, and has clear boundary conditions: it improves clustering on noisy informal text but degrades it on structured text where surface details carry discriminative signal.

## I. Introduction
- Embedding models compress text into fixed-dimensional vectors, but noisy informal text (reviews, feedback, social media) produces scattered embedding spaces where semantically similar documents land far apart
- Motivating example: two Amazon reviews about the same product defect, written in completely different styles, produce distant embeddings despite identical complaint types
- Prior work studies LLM rewriting as a way to improve downstream matching or retrieval, but does not analyze whether rewriting systematically changes the geometry of embedding space in ways that improve unsupervised structure, nor when that transformation helps versus destroys signal
- The novelty is the interaction between LLM rewriting and embedding space geometry: the LLM re-expresses existing document meaning into a form that embedding models can organize more effectively, without adding external information
- Our finding: a single LLM summarization step improves V-measure by +0.08 to +0.28 (49–115% relative improvement) on informal product reviews, reaching significance across 3 products and 3 embedding models spanning short to long context windows (9 of 9 tests, p < 0.05)
- The effect requires both compression and normalization: a full-length paraphrase control did not reproduce the gains, nor did extractive selection without rewriting
- The compression constraint appears to encourage prioritization among candidate aspects even without explicit task steering (neutral prompt captures 85% of the improvement)
- The effect does NOT hold on structured/factual text (CFPB complaints) — the transformation can also destroy discriminative signal, establishing a clear boundary condition
- **Contributions**: (1) We show that abstractive summarization consistently improves clustering of noisy informal text across three products and three embedding models. (2) We identify a mechanism: summarization jointly performs aspect selection and expression normalization, increasing inter-class separation more than within-class compaction. (3) We establish a boundary condition: the same transformation degrades clustering on structured text where fine-grained details carry discriminative signal

## II. Related Work
- **Summarization for retrieval**: RAPTOR (Sarthi et al., 2024) — recursive summarization for tree-organized retrieval. Closest to our work but focused on retrieval accuracy over long documents, not cluster quality on short noisy text
- **Query-side generation**: HyDE (Gao et al., 2023) — generates hypothetical documents from queries. Complementary approach (they transform the query, we transform the document)
- **Retrieval granularity**: Dense X Retrieval (Chen et al., 2024) — proposition-level embeddings. Explores finer granularity; our approach goes coarser via summarization
- **Text enrichment**: LLM-based text enrichment and rewriting for embeddings (2024) — directly tests LLM rewriting but measures retrieval benchmarks, not clustering
- **LLM-augmented retrieval**: Doc-level embedding via LLM augmentation (Wu & Cao, 2024) — generates synthetic queries/titles. Similar spirit but different mechanism
- **Gap**: Prior work treats LLM rewriting as a preprocessing step for supervised matching tasks (retrieval, classification) and evaluates it in terms of downstream task accuracy. We are not aware of prior work that directly evaluates whether LLM rewriting systematically changes the geometry of embedding space — whether it makes unsupervised structure more or less recoverable — or that establishes boundary conditions for when the geometric transformation helps versus destroys discriminative signal. This paper connects the LLM rewriting literature with the embedding space geometry literature, two domains usually evaluated independently

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
- **Paraphrase control**: "Rewrite clearly in plain English, keep all information, don't shorten" — isolates normalization from compression
- **Extractive baselines**: TF-IDF best sentence, longest sentence — tests whether content selection without LLM rewriting is sufficient
- **Clustering robustness**: Agglomerative clustering (Ward linkage) alongside KMeans to show the effect is not algorithm-specific

## IV. Results

### 4.1 Primary effect: summaries improve clustering on informal text
- Fire TV Stick (859 reviews, 9 categories): V-measure improves by +0.14 to +0.19 across three models (all p < 0.001)
- Fitbit Charge (454 reviews, 7 categories): V-measure improves by +0.17 to +0.28 across three models (all p < 0.001)
- Senso Headphones (813 reviews, 10 categories): V-measure improves by +0.08 to +0.19 across three models (all p < 0.05)
- 9 of 9 model-product combinations reach significance
- Confirmed with agglomerative clustering: 9 of 9 consistent

### 4.2 Mechanism ablations: compression and normalization jointly produce the observed gains
- **Paraphrase (full-length rewrite)**: V=0.240 vs raw V=0.257, p=0.43. Full-length normalization does not reproduce the gains
- **Extractive selection (TF-IDF best sentence)**: V=0.183, below raw. Content selection without rewriting does not reproduce the gains
- **LLM summary**: V=0.438, p<0.001. Abstractive summarization — which jointly compresses and normalizes — produces the effect
- These results suggest that the observed gains require both compression and normalization in our setting: the compression constraint encourages prioritization among candidate aspects; the rewriting normalizes surface expression into canonical form
- Prompt ablation: neutral prompt captures 85% of complaint-focused improvement, consistent with the compression constraint effectively encouraging aspect prioritization without explicit steering

### 4.3 Geometry analysis: the effect is centroid separation
- Direct geometric measures on embedding space (shown here for BGE-base-en-v1.5; appendix confirms pattern across all three models and datasets):
  - Intra-class cosine similarity: approximately unchanged (0.64 raw → 0.64 summary)
  - Inter-centroid cosine similarity: decreases substantially (0.93 → 0.87)
  - Within/between distance ratio: approximately halves (5.2 → 2.8 on Fire TV Stick; similar on other products)
- The improvement is primarily **increased inter-class separation**, not tighter within-class compaction
- Consistent with summarization normalizing reviews into more characteristic, less overlapping language across categories
- The embedding improvement (V=0.44) exceeds keyword-only improvement (TF-IDF V=0.32), confirming the benefit is not purely lexical

### 4.4 Long-context models
- The persistence of the effect with nomic-embed-text-v1.5 (8192 token context window, comfortably exceeding review length) suggests the gains are not primarily explained by input truncation, and are more consistent with representational transformation than capacity recovery
- On Fire TV Stick, the effect is slightly larger on the long-context model, suggesting larger models may encode more surface variation rather than less

### 4.5 Boundary condition: structured text
- CFPB consumer complaints: summaries consistently hurt clustering (both across-category and within-category)
- Structured text contains distinguishing factual details that summaries strip away
- Summaries improve clustering when signal is obscured by surface variation; they degrade it when surface details carry discriminative signal

### 4.6 Corroboration with human labels
- App reviews dataset (Maalej et al.): human-labeled categories, 4 classes
- Summaries improve clustering (p = 0.02 on BGE)
- Validates the effect independently of LLM-generated labels
- UMAP visualizations illustrate the geometric shift (used as illustration, not primary evidence)

## V. Discussion

### Mechanism: compression-forced aspect selection + expression normalization
- The LLM summary jointly performs two operations:
  - **Aspect selection via compression**: The word limit forces prioritization among candidate aspects of the review. This forced choice creates discriminative structure that embedding models can exploit
  - **Expression normalization**: The rewriting translates diverse surface forms into canonical language — converting implicit meaning to explicit statements, normalizing vocabulary, regularizing syntax
- In our experiments, neither operation alone reproduced the gains from their combination
- The geometric signature is centroid separation rather than cluster compaction: summarization makes different categories more distinguishable without substantially changing within-category similarity

### When it works vs when it doesn't
- Works: informal, noisy, emotional text where the latent structure is obscured by writing style variation
- Doesn't work: structured, factual text where surface details carry discriminative signal
- The key variable is signal-to-noise ratio in the text relative to the clustering target

### Limitations
- **Label validity**: Amazon labels are LLM-generated. Mitigated by cross-model validation (GPT-5-mini labels independently confirm the effect, kappa=0.75), human-labeled app reviews corroboration (p=0.02), and author review confirming consensus labels are correct and disagreements reflect genuine multi-label ambiguity. The taxonomy was validated by cross-model agreement and author review, though LLM-derived taxonomies may underrepresent categories that require pragmatic or contextual reasoning beyond current model capabilities
- **Single-label assumption**: Manual review revealed some reviews express multiple complaint types. The taxonomy assumes single-label assignment, placing a ceiling on clustering performance. Multi-label evaluation could be explored in future work
- **Same-LLM bias**: Claude Haiku labels and summarizes. Mitigated by four converging lines of evidence (human labels, CFPB failure, prompt ablation, multiple embedding models) but not fully resolved. Testing with a second summarization model would help
- **Single summarization model**: Only Claude Haiku tested. Effect with other LLMs (GPT-4o-mini, open-source models) unknown
- **Paraphrase control sensitivity**: The paraphrase result may depend on the specific instruction used; alternative paraphrase formulations could yield different results
- **Cost**: Requires one LLM call per document at index time
- **Prompt ablation scope**: Tested only when clustering target aligns with primary content. The ratio of generic vs prompt-specific benefit may differ for peripheral targets

### Practical implications
- For clustering customer feedback, support tickets, reviews, or social media: summarize first, then embed
- Generic summarization is sufficient — no prompt engineering required
- Works across all three tested embedding models, including a small model
- Index-time cost only — retrieval/clustering is unchanged

## VI. Conclusion
- Abstractive summarization improves embedding-based clustering of noisy informal text by jointly performing aspect selection and expression normalization, yielding embeddings with greater inter-class separation
- The effect is observed across 3 products, 3 embedding models spanning short to long context windows, and 9 of 9 tests reaching significance, with independent corroboration on human-labeled data
- The effect has clear boundaries: it does not help on structured text where surface details carry discriminative signal
- The compression constraint appears critical: full-length normalization without compression does not reproduce the gains, suggesting that forced prioritization among candidate aspects is a necessary component
- Future work:
  - **Peripheral-target hypothesis**: In our experiments, the clustering target (complaint type) aligned with the primary content of the text, and generic summarization captured 85% of the improvement. We hypothesize this ratio shifts substantially when the clustering target is peripheral to the text's main content — for example, clustering academic abstracts by methodology rather than topic, clustering support emails by product version rather than reported issue, or clustering medical notes by patient affect rather than diagnosis. In these cases, a generic summary would foreground the primary content and lose the target dimension, making prompt design critical rather than optional. Testing this hypothesis requires datasets where the clustering target is present in the text but not its central focus, and would extend the current work from a noise-removal finding to a more general theory of prompt-controlled embedding geometry
  - **Multi-label evaluation**: Manual review revealed that some documents express multiple complaint types. Extending the framework to multi-label assignment and evaluation could better capture the complexity of real-world text and raise the performance ceiling
  - **Cross-domain generalization**: Testing on other informal text domains (social media, support chat, forum posts) and non-English languages
  - **Alternative summarization models**: Validating with open-source LLMs to establish that the effect is model-independent and to assess the minimum model capability required

---
**Target venue:** arXiv preprint (initially), then EMNLP or ACL Findings
**Target length:** 6000-8000 words
**Key deadlines:** None — move at our pace
