# Appendix

## A. Prompts

### A.1 Summarization Prompt (Complaint-Focused)

```
System: You are a product review analyst. For each numbered one-star review,
produce a single concise sentence (max 20 words) summarizing the core complaint.
Focus on: what specifically went wrong with the product? Use the submit_summaries
tool to return all summaries at once.
```

### A.2 Summarization Prompt (Neutral)

```
System: You are a product review analyst. For each numbered one-star review,
produce a single concise sentence (max 20 words) summarizing the review.
Use the submit_summaries tool to return all summaries at once.
```

### A.3 Paraphrase Prompt

```
System: For each numbered review, rewrite it in clear, plain English. Keep ALL
the information and roughly the same length — do not shorten or summarize. Just
clean up the grammar, remove emotional language, and state everything plainly.
Use the submit_summaries tool to return all rewrites.
```

### A.4 Taxonomy Discovery Prompt

```
System: You are analyzing one-star Amazon product reviews to discover the main
types of complaints. Read all the reviews and identify 8-15 distinct complaint
CATEGORIES. Each category should describe WHY the customer is unhappy — the root
cause of the complaint, not the product type. Categories should be mutually
exclusive and collectively exhaustive. Return ONLY a JSON array of category names
as short labels (2-5 words each).
```

### A.5 Labeling Prompt

```
System: Label each review with exactly one category from this taxonomy:
  - [category list]
Choose the category that best describes the ROOT CAUSE of the complaint. If a
review doesn't fit any category well, use the closest match and mark confidence
as 'low'. Use the submit_labels tool to return all labels.
```

## B. Taxonomies

### B.1 Fire TV Stick (9 categories)

| Category | Count |
|---|---|
| Device Freezing and Crashes | 100 |
| WiFi and Connectivity Issues | 100 |
| Remote Control Malfunction | 100 |
| Hardware Failure or Defects | 100 |
| Content Availability Issues | 100 |
| Difficult Setup and Configuration | 100 |
| Inadequate Performance and Power | 100 |
| Streaming Quality and Buffering | 88 |
| Voice Recognition Problems | 71 |

### B.2 Fitbit Charge (7 categories)

| Category | Count |
|---|---|
| Band/Strap Defects | 100 |
| Battery Performance | 100 |
| Device Build Quality and Durability | 100 |
| Fit, Comfort and Wearability | 46 |
| Tracking Accuracy | 40 |
| Connectivity and Syncing Problems | 38 |
| Water Resistance and Environmental Damage | 30 |

### B.3 Senso Bluetooth Headphones (10 categories)

| Category | Count |
|---|---|
| Fit and Comfort Issues | 100 |
| Battery and Charging Problems | 100 |
| Audio Quality and Sound Issues | 100 |
| Hardware Defects and Durability | 100 |
| Bluetooth Connectivity Issues | 100 |
| Control Button and Port Malfunctions | 96 |
| Product Quality Degradation | 81 |
| Water and Environmental Damage | 56 |
| Microphone and Call Quality Issues | 41 |
| Customer Service and Warranty Issues | 39 |

## C. Cross-Model Label Agreement

### C.1 Fire TV Stick: Claude Haiku vs GPT-5-mini

| Metric | Value |
|---|---|
| Valid comparisons | 312 |
| Exact agreement | 241 (77.2%) |
| Cohen's kappa | 0.747 |

### C.2 Top Disagreement Pairs

After applying the same category merges used in the final dataset (see Section B.1), most disagreements occurred between semantically adjacent categories, consistent with genuine ambiguity rather than random noise:

| Category Pair | Disagreements |
|---|---|
| Content Availability Issues / Inadequate Performance and Power | 5 |
| Content Availability Issues / Voice Recognition Problems | 5 |
| Content Availability Issues / Device Freezing and Crashes | 5 |
| Device Freezing and Crashes / Inadequate Performance and Power | 4 |
| Device Freezing and Crashes / Hardware Failure or Defects | 4 |

### C.3 Disagreement Examples

**Example 1.** *"My old one is faster. This one is slow and freezes and for some reason the Hulu app refuses to load, which is weird since my old one was purchased in 2014 I believe."*
Haiku: Inadequate Performance and Power. GPT-5-mini: Device Freezing and Crashes. Both labels are defensible---the review describes both slowness (performance) and freezing (crashes), with an app-loading failure that could be attributed to either.

**Example 2.** *"if your buying this to 'jailbreak' and watch movies on... DONT.. its not worth $50. its more of a pain in the ass to setup every other month due to new kodi changes... your lucky if you can get 1 movie to run out of 10."*
Haiku: Streaming Quality and Buffering. GPT-5-mini: Difficult Setup and Configuration. The review describes both repeated setup difficulty and poor streaming success rates---a genuinely multi-faceted complaint.

**Example 3.** *"We bought two of these sticks and 1 is working okay still but the other is constantly shutting down just minutes after starting a program or updating over and over and over again. It's frustrating because it's not that old either."*
Haiku: Device Freezing and Crashes. GPT-5-mini: Hardware Failure or Defects. The constant shutdowns could reflect either a software stability issue (crashes) or a hardware defect (failing unit). Both interpretations are plausible.

**Example 4.** *"I am not impressed. You cannot really tell what programs are free and it's easy to inadvertently select a movie that is not free. If it incorporated TV shows it might be helpful and some voice requests it does not grasp."*
Haiku: Voice Recognition Problems. GPT-5-mini: Content Availability Issues. The review mentions both content confusion (free vs paid, missing TV shows) and voice command failures---two distinct complaints in one review.

### C.4 Clustering with Independent Labels (BGE-base-en-v1.5)

| Ground Truth Labels | Raw V | Summary V | Delta |
|---|---|---|---|
| Claude Haiku | 0.245 | 0.463 | +0.218 |
| GPT-5-mini | 0.288 | 0.453 | +0.166 |

The effect persists with independent labels, though the delta is slightly smaller, consistent with some reduction in same-model alignment.

## D. Agglomerative Clustering Results

V-measure deltas (Summary - Raw) for agglomerative clustering (Ward linkage):

| Product | MiniLM | BGE | Nomic |
|---|---|---|---|
| Fire TV Stick | +0.156 | +0.133 | +0.160 |
| Fitbit Charge | +0.267 | +0.141 | +0.095 |
| Senso Headphones | +0.176 | +0.145 | +0.044 |

All 9 conditions show positive deltas, confirming the effect is not specific to KMeans.

## E. Geometry Analysis Across All Embedding Models

Within/between distance ratio (lower = more clusterable):

| Product | Model | Raw W/B | Summary W/B | Change |
|---|---|---|---|---|
| Fire TV Stick | MiniLM | 2.53 | 1.58 | -38% |
| Fire TV Stick | BGE | 5.18 | 2.83 | -45% |
| Fire TV Stick | Nomic | 4.00 | 2.79 | -30% |
| Fitbit Charge | MiniLM | 2.30 | 1.36 | -41% |
| Fitbit Charge | BGE | 4.15 | 2.23 | -46% |
| Fitbit Charge | Nomic | 3.33 | 2.13 | -36% |
| Senso Headphones | MiniLM | 2.62 | 1.50 | -43% |
| Senso Headphones | BGE | 4.59 | 2.51 | -45% |
| Senso Headphones | Nomic | 3.41 | 2.38 | -30% |

The within/between ratio decreases by 30--46% across all 9 conditions. Inter-centroid cosine similarity drops by 0.04--0.17 (mean -0.08), while intra-class cosine similarity deltas range from -0.02 to +0.03 (mean -0.003), confirming that the effect is driven almost entirely by increased centroid separation rather than within-class compaction.

## F. Per-Class Intra-Class Similarity (Fire TV Stick, BGE)

| Category | Raw Intra | Summary Intra | Delta |
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

Specific complaint types (voice recognition, remote control) show the largest intra-class improvement. Broader categories (content availability, WiFi) show slight decreases, consistent with summaries normalizing away within-category variation for diffuse complaint types.

## G. CFPB Results (Negative Control)

### G.1 Within-Category Clustering (V-measure)

| Product | Model | Raw V | Summary V | Delta |
|---|---|---|---|---|
| Mortgage | MiniLM | 0.145 | 0.073 | -0.072 |
| Mortgage | BGE | 0.101 | 0.066 | -0.036 |
| Mortgage | Nomic | 0.207 | 0.080 | -0.127 |
| Checking/Savings | MiniLM | 0.249 | 0.237 | -0.012 |
| Checking/Savings | BGE | 0.253 | 0.222 | -0.031 |
| Checking/Savings | Nomic | 0.237 | 0.262 | +0.025 |

### G.2 Across-Category Clustering (V-measure, BGE)

| Evaluation | Raw V | Summary V | Delta |
|---|---|---|---|
| By issue type (10 categories) | 0.628 | 0.528 | -0.100 |
| By product type (9 categories) | 0.567 | 0.518 | -0.049 |

Most CFPB conditions were negative, and none significantly favored summaries.

## H. Text Length Statistics (Fire TV Stick)

| Condition | Mean | Median | SD | Q1 | Q3 | Min | Max |
|---|---|---|---|---|---|---|---|
| Raw text | 65.8 | 43 | 69.3 | 22 | 83 | 4 | 685 |
| Paraphrase | 47.0 | 43 | 25.7 | 24 | 68 | 7 | 107 |
| LLM summary | 9.7 | 10 | 1.9 | 8 | 11 | 4 | 17 |

Word counts. No summaries exceeded the 20-word limit (0 of 859). Paraphrases are shorter than raw text on average (47 vs 66 words) despite the instruction to preserve length, reflecting the LLM's tendency to omit repetition and filler even when asked not to shorten.

## I. Summary Failure Modes

While summaries generally captured the primary complaint, we observed three recurring failure patterns:

**Overgeneralization.** Some summaries collapse specific complaints into generic language. A review describing a precise hardware defect ("the HDMI connector snapped off inside the TV port") may be summarized as "device has hardware defect," losing the specific failure mode that would distinguish it from other hardware complaints.

**Loss of secondary complaints.** Reviews expressing multiple issues are reduced to one. A review complaining about both WiFi disconnection and an unresponsive remote is summarized as only the WiFi problem. This is by design (the compression constraint forces selection) but means the summary representation is incomplete for multi-faceted reviews.

**Category boundary collapse.** Semantically adjacent categories (e.g., "device freezing" vs "inadequate performance") can produce near-identical summaries. "Device freezes frequently" and "device runs very slowly" are distinct complaints but may produce overlapping embeddings after summarization. This likely contributes to residual cluster overlap and limits the achievable V-measure.

## J. Note on the Paraphrase Prompt

The paraphrase prompt includes the instruction "remove emotional language." A reviewer may note that this is not a pure paraphrase---it is a meaning-modifying operation that strips affect. We acknowledge this. However, the paraphrase still produced no clustering improvement ($\Delta$ = -0.018, $p$ = 0.43), suggesting that even with affect removal, full-length normalization without compression is insufficient. A stricter paraphrase control ("rewrite for clarity only, preserving tone") would further isolate the compression mechanism, and we note this as a direction for future work.

## K. Sample Summaries and Paraphrases

### K.1 Fire TV Stick Examples

**Example 1** (WiFi and Connectivity Issues)

- *Raw (56 words)*: "I am ready to throw this thing away. In the middle of watching shows, it completely stops working. I can sometimes disconnect and reconnect to the internet but most of the time I have to unplug it, plug it back in, wait 30 minutes and then it will work for a short time."
- *Summary (8 words)*: "Device frequently disconnects from internet requiring physical reboot."
- *Paraphrase (42 words)*: "The device frequently stops working while streaming. Sometimes reconnecting to the internet resolves the issue, but usually the device must be physically unplugged and restarted, requiring approximately 30 minutes before it functions again for a short period."

**Example 2** (Hardware Failure or Defects)

- *Raw (19 words)*: "Stopped working 3 mo after buying. Very disappointed. It was so wonerful at first. To late to return now!"
- *Summary (7 words)*: "Device stopped working three months after purchase."
- *Paraphrase (28 words)*: "The device stopped working three months after I bought it. I am very disappointed because it worked wonderfully at first. It is too late to return it now."

**Example 3** (Voice Recognition Problems)

- *Raw (34 words)*: "The device is wonderful until Lexi says 'I don't know how to respond to that'. Not major but iritatating to an older tech challenged person that wants to watch something."
- *Summary (11 words)*: "Voice recognition frequently fails without clear guidance on its limitations."
- *Paraphrase (30 words)*: "The device works well except when the voice assistant responds with 'I don't know how to respond to that,' which is frustrating for older users with limited technical experience."

### K.2 Extractive Baselines (Fire TV Stick, BGE)

| Method | Avg Words | V-measure | vs Raw |
|---|---|---|---|
| Raw text | 65 | 0.257 | --- |
| TF-IDF best sentence | 20 | 0.183 | -0.074 |
| Longest sentence | 21 | 0.182 | -0.075 |
| Middle sentence | 14 | 0.138 | -0.119 |
| Last sentence | 14 | 0.084 | -0.173 |
| LLM summary | 10 | 0.438 | +0.181 |
