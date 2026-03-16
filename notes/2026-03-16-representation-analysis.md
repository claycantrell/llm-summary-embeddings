---
title: "Representation Analysis — Embedding Space Geometry"
date: 2026-03-16
tags: [geometry, analysis, cosine-similarity, centroids, primary]
---

## Question

How does LLM summarization change the geometry of embedding space? Is the improvement from tighter clusters (compaction) or more separated centroids (separation)?

## Metrics

- **Intra-class cosine similarity**: Average pairwise cosine similarity within each class. Higher = tighter clusters.
- **Inter-centroid cosine similarity**: Average cosine similarity between class centroids. Lower = better separation.
- **Within/between distance ratio**: (1 - intra_sim) / (1 - inter_sim). Lower = more clusterable. This is the key metric — it captures both dimensions simultaneously.

## Results (BGE-base-en-v1.5)

| Product | Condition | Intra-class sim | Inter-centroid sim | W/B ratio |
|---|---|---|---|---|
| Fire TV Stick | Raw | 0.638 | 0.930 | 5.18 |
| Fire TV Stick | Summary | 0.641 | 0.873 | **2.83** |
| Fitbit Charge | Raw | 0.671 | 0.921 | 4.15 |
| Fitbit Charge | Summary | 0.659 | 0.847 | **2.23** |
| Senso Headphones | Raw | 0.647 | 0.923 | 4.59 |
| Senso Headphones | Summary | 0.643 | 0.858 | **2.51** |

## Key Finding: Separation, Not Compaction

**Intra-class similarity barely changes** (deltas of -0.01 to +0.003). Summaries do not substantially pull same-class documents closer together in embedding space.

**Inter-centroid similarity drops substantially** (deltas of -0.06 to -0.07). Class centroids move apart. Summarization makes different categories more distinguishable.

**Within/between ratio nearly halves** across all three products (5.2→2.8, 4.1→2.2, 4.6→2.5). The embedding space becomes approximately twice as clusterable.

## Interpretation

The LLM is not making similar reviews more similar — they were already reasonably close in embedding space. What it's doing is making different categories more **distinct** by normalizing each category's reviews into more characteristic vocabulary. A WiFi complaint and a remote control complaint, when summarized, use more differentiated language than the raw reviews do. This increases centroid separation without significantly changing intra-class spread.

This is direct geometric evidence for the "semantic normalization" mechanism. The normalization doesn't compress clusters — it separates them by making each cluster's representation more canonical and less overlapping with adjacent clusters.

## Per-Class Detail (Fire TV Stick)

| Category | Raw Intra | Sum Intra | Delta |
|---|---|---|---|
| Voice Recognition Problems | 0.652 | 0.686 | +0.034 |
| Remote Control Malfunction | 0.658 | 0.689 | +0.031 |
| Hardware Failure or Defects | 0.594 | 0.621 | +0.027 |
| Streaming Quality and Buffering | 0.660 | 0.663 | +0.003 |
| Device Freezing and Crashes | 0.637 | 0.647 | +0.010 |
| Difficult Setup and Configuration | 0.598 | 0.595 | -0.003 |
| Inadequate Performance and Power | 0.648 | 0.631 | -0.016 |
| WiFi and Connectivity Issues | 0.665 | 0.646 | -0.019 |
| Content Availability Issues | 0.630 | 0.589 | -0.040 |

Categories with the most specific/distinctive complaints (voice, remote, hardware) show the biggest intra-class improvement. Categories with more diffuse complaints (content, WiFi, performance) show slight decreases — the summary may be normalizing away distinguishing nuance within these broader categories.
