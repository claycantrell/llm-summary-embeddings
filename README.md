# How Abstractive Summarization Reshapes Embedding Space for Clustering Noisy Informal Text

Code and data for the paper: *How Abstractive Summarization Reshapes Embedding Space for Clustering Noisy Informal Text* (Cantrell, 2026).

## Key Finding

LLM abstractive summarization improves embedding-based clustering of noisy informal text by 49-115% (V-measure), significant across 3 products, 3 embedding models, and 9/9 tests (p < 0.05). The effect operates through increased inter-class centroid separation and requires both compression and normalization — neither paraphrasing (2 variants) nor extractive selection (4 methods) reproduces the gains. On structured factual text, the same transformation degrades clustering.

## Repository Structure

```
manuscript/
  main.md                    # Paper (Pandoc Markdown)
  appendix.md                # Appendix (prompts, tables, examples)
scripts/
  download_data.py           # Download app reviews dataset
  build_amazon_dataset.py    # 3-phase Amazon dataset builder (discover, label, build)
  run_experiment.py          # Main experiment: summarize, embed, cluster, bootstrap
  run_multi_product.py       # Run pipeline across multiple products
  visualize.py               # UMAP figure generation
figures/
  umap_comparison_bge.png    # Fire TV Stick raw vs summary (Figure 1)
  umap_all_products.png      # All 3 products comparison (Figure 2)
notes/                       # Research notes documenting all experiments
data/                        # Generated datasets (gitignored, rebuild with scripts)
cache/                       # Cached embeddings and summaries (gitignored)
```

## Reproduction

### Requirements

```bash
pip install -r requirements.txt
```

Dependencies: `anthropic`, `openai`, `sentence-transformers`, `scikit-learn`, `pandas`, `numpy`, `matplotlib`, `umap-learn`, `sumy`

### API Keys

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...    # Only needed for GPT-5-mini cross-validation
```

### Step 1: Build Datasets

```bash
# Fire TV Stick (primary dataset, ~860 reviews, 9 complaint categories)
python scripts/build_amazon_dataset.py

# Fitbit Charge + Senso Bluetooth Headphones (generalization)
python scripts/run_multi_product.py

# App reviews with human labels (corroboration)
python scripts/download_data.py
```

Reviews are streamed from [Amazon Reviews 2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) on HuggingFace. Taxonomy discovery and labeling require Anthropic API calls (~$1-2 total).

### Step 2: Run Experiments

```bash
python scripts/run_experiment.py
```

Generates summaries, embeds with 3 models (all-MiniLM-L6-v2, BGE-base-en-v1.5, nomic-embed-text-v1.5), clusters, and runs bootstrap significance tests. All outputs are cached after first run.

### Step 3: Generate Figures

```bash
python scripts/visualize.py
```

## Reproducing Specific Tables

| Table | Script | Notes |
|-------|--------|-------|
| Table 1 (primary results) | `run_experiment.py` + `run_multi_product.py` | 3 products x 3 models |
| Table 2 (mechanism ablation) | `run_experiment.py` | Paraphrase, extractive, summary |
| Table 3 (geometry) | `run_experiment.py` | Cosine similarity analysis |
| Appendix D (agglomerative) | `run_experiment.py` | Ward linkage robustness |
| Appendix E (geometry, all models) | `run_multi_product.py` | 9-condition table |

## Prompts

All prompts are documented in `manuscript/appendix.md` (Appendix A) and embedded in the scripts.

## Datasets

| Dataset | Source | Labels | Role |
|---------|--------|--------|------|
| Fire TV Stick reviews | [Amazon Reviews 2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | LLM-generated, 9 categories | Primary |
| Fitbit Charge reviews | Amazon Reviews 2023 | LLM-generated, 7 categories | Generalization |
| Senso BT Headphones | Amazon Reviews 2023 | LLM-generated, 10 categories | Generalization |
| App reviews | [Maalej et al.](https://github.com/mohammadzaeem/classification_of_app_reviews) | Human-labeled, 4 categories | Corroboration |
| CFPB complaints | [data.gov](https://files.consumerfinance.gov/ccdb/complaints.csv.zip) | CFPB taxonomy | Negative control |

## Caching

All LLM outputs and embeddings are cached locally after first computation. Re-runs use cached data and cost nothing. Delete `cache/` to force recomputation.

## Citation

```bibtex
@article{cantrell2026summarization,
  title={How Abstractive Summarization Reshapes Embedding Space
         for Clustering Noisy Informal Text},
  author={Cantrell, Clay},
  year={2026},
  journal={arXiv preprint}
}
```

## License

MIT
