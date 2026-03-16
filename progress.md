# Progress

## Status
Experiments complete. Ready to begin writing.

## Experiments Done
- [x] CFPB across-category clustering (negative result)
- [x] CFPB within-category clustering (negative result)
- [x] App reviews — human-labeled, 4 categories (positive, p=0.02)
- [x] Amazon appliances — 11 then 7 categories (positive direction, not significant)
- [x] Fire TV Stick — 9 categories, 3 models (positive, p<0.001 all)
- [x] Fitbit Charge — 7 categories, 3 models (positive, p<0.001 all)
- [x] Senso BT Headphones — 10 categories, 3 models (positive, p<0.001 all)
- [x] Prompt ablation — complaint-focused vs neutral (85% is noise removal)
- [x] Data integrity / leakage checks
- [x] UMAP visualizations (single + 3-product panel)

## TODO Before / During Writing

### Highest priority (needed for credible submission)
- [ ] Human validation of ~100-200 Amazon review labels — single biggest vulnerability
- [ ] Re-label Fire TV Stick reviews with a different LLM (GPT-4o-mini) to rule out same-LLM bias
- [x] Non-KMeans robustness check — agglomerative (Ward) confirms 9/9 consistent
- [x] Representation analysis — within/between ratio halves across all products; effect is centroid separation, not cluster compaction

### Important (strengthens the paper)
- [x] Length-control baselines — truncation makes clustering WORSE; LLM summary at same word count is 3x better
- [x] Paraphrase baseline — normalization alone does nothing; compression is load-bearing
- [ ] Second summarization model (GPT-4o-mini or local model) — shows effect isn't model-specific
- [ ] Cost/benefit analysis (cost per document, latency)

### Nice to have
- [ ] Summary length ablation (5 vs 15 vs 50 words)
- [ ] Writing tone cleanup (academic register throughout)

### Writing
- [x] Outline the paper
- [ ] Literature review — position against RAPTOR, HyDE, Dense X, text enrichment
- [ ] Write manuscript
- [ ] Abstract

## Sources Collected
- RAPTOR (Sarthi et al., ICLR 2024) — recursive summarization for retrieval
- HyDE (Gao et al., ACL 2023) — hypothetical document embeddings
- Dense X Retrieval (Chen et al., EMNLP 2024) — proposition-level granularity
- LLM-Augmented Retrieval (Wu & Cao, 2024) — doc-level embedding via LLM
- Enhancing Embedding via Text Enrichment (2024) — LLM rewriting before embedding
- Improving Text Embeddings with LLMs (2024) — synthetic training data

### Still Needed
- Embedding model papers (MiniLM, BGE, Nomic)
- Clustering methodology references (KMeans, V-measure, bootstrap)
- Qualitative coding / grounded theory methodology references
- Any papers on noise in embedding spaces

## Where We Left Off
All experiments complete with strong results. Three products, three models, all significant. Prompt ablation shows effect is primarily noise removal. Data integrity checks passed with same-LLM bias flagged as limitation (mitigated by human-labeled app reviews result). Next step: outline the paper and start writing.
