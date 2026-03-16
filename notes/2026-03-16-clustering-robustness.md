---
title: "Clustering Robustness — KMeans vs Agglomerative"
date: 2026-03-16
tags: [robustness, clustering, methodology]
---

## Question

Is the improvement specific to KMeans (which prefers compact spherical clusters), or does it hold with a different clustering algorithm?

## Test

Ran agglomerative clustering (Ward linkage) alongside KMeans on all cached embeddings. Same data, same embeddings, different clustering algorithm. No additional API calls needed.

## Results

**9 of 9 product-model combinations show summary > raw on BOTH methods.**

### V-measure deltas (Summary - Raw)

| Product | Model | KMeans | Agglomerative |
|---|---|---|---|
| Fire TV Stick | MiniLM | +0.144 | +0.156 |
| Fire TV Stick | BGE | +0.181 | +0.133 |
| Fire TV Stick | Nomic | +0.187 | +0.160 |
| Fitbit Charge | MiniLM | +0.276 | +0.267 |
| Fitbit Charge | BGE | +0.262 | +0.141 |
| Fitbit Charge | Nomic | +0.170 | +0.095 |
| Senso Headphones | MiniLM | +0.157 | +0.176 |
| Senso Headphones | BGE | +0.189 | +0.145 |
| Senso Headphones | Nomic | +0.083 | +0.044 |

## Conclusion

The effect is not an artifact of KMeans. Agglomerative clustering with Ward linkage (which makes no spherical cluster assumption) shows the same consistent improvement. Deltas are sometimes smaller but direction is unanimous across all 9 conditions.
