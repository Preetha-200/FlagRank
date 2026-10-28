# Full-Dataset Suspiciousness Scoring Framework Report

## 1. Objective
Construct a continuous suspiciousness score from the already-established ranking inconsistency evidence. This score ranks products by how strongly their observed ranking deviates from the expected baseline relative to their query-level peers, evaluated across the entire dataset using OOF predictions.

## 2. Why a Continuous Score?
A continuous score `[0, 100]` ranks products by anomaly severity without asserting an arbitrary ground-truth manipulation label. E-commerce platforms contain natural noise; a continuous score allows investigators to audit the most extreme anomalies ("highest-scoring ranking inconsistency candidates") without classifying them as definitively fraudulent. 

## 3. Evidence Components
Because deviation direction is symmetric (unexpectedly high or unexpectedly low are both anomalous), we extract the magnitude:
1. `absolute_rank_inconsistency_z` = `abs(rank_inconsistency_z)`
2. `absolute_relative_rank_gap` = `abs(relative_rank_gap)`
3. `absolute_rank_deviation` = `abs(rank_deviation)`

## 4. Normalization Methodology
We use robust **Percentile-Based Normalization (Empirical CDF)** for all three components:
- `normalized_value = rank(pct=True)`
- **Rationale:** Dividing by a global maximum is highly vulnerable to single extreme outliers compressing the entire scale. Percentile normalization maps the absolute magnitude of the evidence into a robust `[0,1]` scale based on its severity relative to the entire dataset.

## 5. Explicit Formula & Weights
The components are aggregated into a single `[0, 100]` score using explicit weights prioritizing query-relative anomalies:
- **50%:** Standardized query-relative inconsistency (`norm_inconsistency_z`)
- **30%:** Relative rank displacement (`norm_relative_gap`)
- **20%:** Absolute rank deviation (`norm_rank_deviation`)

`suspiciousness_score = 100 × (0.50 × norm_inconsistency_z + 0.30 × norm_relative_gap + 0.20 × norm_rank_deviation)`

## 6. Important Limitations and Caveats
- **Not Causality:** This score establishes *inconsistency*, not intent. A high score means the product's rank is severely unexplained by the observable signals (price, reviews, text-match). This could be caused by manipulation (e.g., brushing), but could also be caused by unobserved organic variables (e.g., off-platform virality, superior click-through-rates not in the dataset).
- **No Direct Penalties:** `sponsored` products are not structurally penalized by the score. The score is strictly derived from the magnitude of the model's prediction error.

## 7. Score Distribution
- **Range:** [2.44, 99.86]
- **Mean:** 50.05
- **Median (50th):** 48.83
- **Standard Deviation:** 23.20
- **25th Percentile:** 31.17
- **75th Percentile:** 67.62
- **90th Percentile:** 83.41
- **95th Percentile:** 89.73
- **99th Percentile:** 96.42

## 8. Top 10 Highest-Scoring Ranking Inconsistency Candidates
```text
                                                                               query  amazon_rank  expected_rank  rank_deviation  rank_inconsistency_z  relative_rank_gap  feat_sponsored  suspiciousness_score
                           Nike running shoes in blue or grey, cushioned, under $120           59      23.790475       35.209525              1.992420           0.983051               0             99.862888
                   recycled paper towels, white, FSC certified, bulk pack, under $40            1      33.204718      -32.204718             -2.100232          -0.859649               1             99.588665
                        Colombian espresso, low acidity, specialty grade, $15-$25/lb            4      35.526595      -31.526595             -1.797130          -0.894737               1             99.159049
                        Colombian espresso, low acidity, specialty grade, $15-$25/lb            1      33.831804      -32.831804             -1.876918          -0.807018               0             99.031079
                organic whole bean coffee, medium roast, single-origin, under $25/lb           46      20.964691       25.035309              1.714372           0.895833               0             98.254113
                Hoka running shoes, not black, maximalist, grey or white, under $160           47      24.817315       22.182685              1.862528           0.854167               0             98.153565
                  ASICS running shoes, overpronation, wide toe, not pink, under $150            2      24.928600      -22.928600             -1.736835          -0.875000               0             97.838208
         bamboo paper towels, reusable, not single-use, natural tan color, under $30            1      30.412137      -29.412137             -1.882276          -0.644068               1             97.111517
                organic whole bean coffee, medium roast, single-origin, under $25/lb           47      22.428424       24.571576              1.680858           0.750000               0             96.969835
wireless noise cancelling headphones with 30+ hour battery, black or grey, $100-$150           22       7.066001       14.933999              2.161082           0.909091               1             96.723035
```
