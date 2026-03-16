#!/usr/bin/env python3
"""
Generate UMAP scatter plots comparing raw vs. summary embeddings.

Produces four plots:
  1. Raw embeddings colored by true product label
  2. Raw embeddings colored by KMeans cluster assignment
  3. Summary embeddings colored by true product label
  4. Summary embeddings colored by KMeans cluster assignment

Also produces a combined 2x2 panel figure for easy comparison.

Usage:
    python scripts/visualize.py
"""

import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for saving figures
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path

try:
    import umap
except ImportError:
    print("ERROR: umap-learn is required for visualization.")
    print("Install it with: pip install umap-learn")
    sys.exit(1)

# ── Paths ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
CACHE_DIR = REPO_ROOT / "cache"
FIGURES_DIR = REPO_ROOT / "figures"

SAMPLE_CSV = DATA_DIR / "cfpb_sample.csv"
RAW_EMBEDDINGS_CACHE = CACHE_DIR / "embeddings_raw.npy"
SUMMARY_EMBEDDINGS_CACHE = CACHE_DIR / "embeddings_summary.npy"
CLUSTER_LABELS_PATH = DATA_DIR / "cluster_labels.npz"
RESULTS_PATH = DATA_DIR / "experiment_results.json"

# UMAP caches
UMAP_RAW_CACHE = CACHE_DIR / "umap_raw.npy"
UMAP_SUMMARY_CACHE = CACHE_DIR / "umap_summary.npy"

UMAP_RANDOM_STATE = 42
UMAP_N_NEIGHBORS = 15
UMAP_MIN_DIST = 0.1


def load_data():
    """Load embeddings, labels, and results."""
    # Check that all required files exist
    required = [RAW_EMBEDDINGS_CACHE, SUMMARY_EMBEDDINGS_CACHE, CLUSTER_LABELS_PATH, RESULTS_PATH]
    missing = [p for p in required if not p.exists()]
    if missing:
        print("ERROR: Missing required files. Run the experiment first:")
        print("  python scripts/run_experiment.py")
        for p in missing:
            print(f"  Missing: {p}")
        sys.exit(1)

    raw_embeddings = np.load(RAW_EMBEDDINGS_CACHE)
    summary_embeddings = np.load(SUMMARY_EMBEDDINGS_CACHE)

    labels_data = np.load(CLUSTER_LABELS_PATH, allow_pickle=True)
    true_labels = labels_data["true_labels"]
    raw_cluster_labels = labels_data["raw_cluster_labels"]
    summary_cluster_labels = labels_data["summary_cluster_labels"]
    label_names = labels_data["label_names"]

    with open(RESULTS_PATH, "r") as f:
        results = json.load(f)

    return {
        "raw_embeddings": raw_embeddings,
        "summary_embeddings": summary_embeddings,
        "true_labels": true_labels,
        "raw_cluster_labels": raw_cluster_labels,
        "summary_cluster_labels": summary_cluster_labels,
        "label_names": label_names,
        "results": results,
    }


def compute_umap(embeddings: np.ndarray, cache_path: Path, label: str) -> np.ndarray:
    """Compute 2D UMAP projection, caching the result."""
    if cache_path.exists():
        projected = np.load(cache_path)
        if projected.shape[0] == embeddings.shape[0]:
            print(f"[CACHE] Loaded {label} UMAP projection from cache.")
            return projected

    print(f"Computing UMAP projection for {label} embeddings ({embeddings.shape})...")
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=UMAP_N_NEIGHBORS,
        min_dist=UMAP_MIN_DIST,
        random_state=UMAP_RANDOM_STATE,
        metric="cosine",
    )
    projected = reducer.fit_transform(embeddings)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(cache_path, projected)
    print(f"[OK] Saved {label} UMAP projection to cache.")

    return projected


def make_scatter(ax, xy, labels, label_names, title, is_cluster=False):
    """
    Draw a scatter plot on the given axes.
    """
    n_labels = len(np.unique(labels))
    cmap = cm.get_cmap("tab10" if n_labels <= 10 else "tab20", n_labels)

    for i in range(n_labels):
        mask = labels == i
        name = label_names[i] if i < len(label_names) else f"Cluster {i}"
        # Shorten long label names for the legend
        if len(name) > 30:
            name = name[:27] + "..."
        ax.scatter(
            xy[mask, 0], xy[mask, 1],
            c=[cmap(i)],
            label=name,
            s=8,
            alpha=0.6,
            edgecolors="none",
        )

    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("UMAP 1", fontsize=9)
    ax.set_ylabel("UMAP 2", fontsize=9)


def create_individual_plots(data, umap_raw, umap_summary):
    """Create four individual scatter plot files."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    plots = [
        (umap_raw, data["true_labels"], data["label_names"],
         "Raw Embeddings — True Labels", "raw_true_labels.png"),
        (umap_raw, data["raw_cluster_labels"],
         [f"Cluster {i}" for i in range(len(np.unique(data["raw_cluster_labels"])))],
         "Raw Embeddings — KMeans Clusters", "raw_clusters.png"),
        (umap_summary, data["true_labels"], data["label_names"],
         "Summary Embeddings — True Labels", "summary_true_labels.png"),
        (umap_summary, data["summary_cluster_labels"],
         [f"Cluster {i}" for i in range(len(np.unique(data["summary_cluster_labels"])))],
         "Summary Embeddings — KMeans Clusters", "summary_clusters.png"),
    ]

    for xy, labels, names, title, filename in plots:
        fig, ax = plt.subplots(figsize=(10, 8))
        make_scatter(ax, xy, labels, names, title)
        ax.legend(
            loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=7,
            markerscale=2, frameon=True,
        )
        fig.tight_layout()
        path = FIGURES_DIR / filename
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {path}")


def create_combined_plot(data, umap_raw, umap_summary):
    """Create a 2x2 combined panel figure."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    # Top-left: raw + true labels
    make_scatter(
        axes[0, 0], umap_raw, data["true_labels"], data["label_names"],
        "Raw Embeddings — True Labels",
    )

    # Top-right: summary + true labels
    make_scatter(
        axes[0, 1], umap_summary, data["true_labels"], data["label_names"],
        "Summary Embeddings — True Labels",
    )

    # Bottom-left: raw + clusters
    raw_cluster_names = [f"Cluster {i}" for i in range(len(np.unique(data["raw_cluster_labels"])))]
    make_scatter(
        axes[1, 0], umap_raw, data["raw_cluster_labels"], raw_cluster_names,
        "Raw Embeddings — KMeans Clusters",
        is_cluster=True,
    )

    # Bottom-right: summary + clusters
    summary_cluster_names = [f"Cluster {i}" for i in range(len(np.unique(data["summary_cluster_labels"])))]
    make_scatter(
        axes[1, 1], umap_summary, data["summary_cluster_labels"], summary_cluster_names,
        "Summary Embeddings — KMeans Clusters",
        is_cluster=True,
    )

    # Add legends
    for ax in axes.flat:
        ax.legend(
            loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=6,
            markerscale=2, frameon=True,
        )

    # Add metrics as text annotation
    results = data["results"]
    raw_m = results["raw_metrics"]
    sum_m = results["summary_metrics"]
    metrics_text = (
        f"V-Measure:  Raw={raw_m['v_measure']:.3f}  Summary={sum_m['v_measure']:.3f}\n"
        f"ARI:        Raw={raw_m['adjusted_rand_index']:.3f}  Summary={sum_m['adjusted_rand_index']:.3f}\n"
        f"Silhouette: Raw={raw_m['silhouette_score']:.3f}  Summary={sum_m['silhouette_score']:.3f}"
    )
    fig.text(
        0.5, 0.01, metrics_text,
        ha="center", va="bottom", fontsize=10,
        fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", edgecolor="gray"),
    )

    fig.suptitle(
        "CFPB Complaints: Raw vs. LLM-Summary Embeddings",
        fontsize=14, fontweight="bold", y=0.98,
    )
    fig.tight_layout(rect=[0, 0.05, 1, 0.96])

    path = FIGURES_DIR / "comparison_panel.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    print("=" * 60)
    print("UMAP Visualization — Raw vs. Summary Embeddings")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    data = load_data()

    print(f"  Raw embeddings:     {data['raw_embeddings'].shape}")
    print(f"  Summary embeddings: {data['summary_embeddings'].shape}")
    print(f"  Categories:         {len(data['label_names'])}")

    # Compute UMAP projections
    print()
    umap_raw = compute_umap(data["raw_embeddings"], UMAP_RAW_CACHE, "raw")
    umap_summary = compute_umap(data["summary_embeddings"], UMAP_SUMMARY_CACHE, "summary")

    # Generate plots
    print("\nGenerating individual plots...")
    create_individual_plots(data, umap_raw, umap_summary)

    print("\nGenerating combined panel plot...")
    create_combined_plot(data, umap_raw, umap_summary)

    print("\n" + "=" * 60)
    print("Done! Figures saved to figures/")
    print("  - figures/raw_true_labels.png")
    print("  - figures/raw_clusters.png")
    print("  - figures/summary_true_labels.png")
    print("  - figures/summary_clusters.png")
    print("  - figures/comparison_panel.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
