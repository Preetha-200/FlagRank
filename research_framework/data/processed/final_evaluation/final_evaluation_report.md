# Final Evaluation Framework Report

## Part A: Real Marketplace Observational Evaluation

### 1. Ranking-Level Statistics
- **Total Products:** 1094
- **Total Queries:** 44
- **Observed Rank Range:** [1, 59]
- **Mean Observed Rank:** 16.84
- **Median Observed Rank:** 13.00

### 2. Suspiciousness Distribution
- **Mean:** 50.05
- **Median:** 48.83
- **Standard Deviation:** 23.20
- **Min / Max:** [2.44, 99.86]
- **Percentiles:** 
  - 50th: 48.83
  - 75th: 67.62
  - 90th: 83.41
  - 95th: 89.73
  - 99th: 96.42

### 3. Suspiciousness by Rank Region
- **Top 10:** 52.27
- **11-20:** 46.76
- **21-30:** 39.35
- **31-40:** 42.70
- **41-50:** 68.22
- **51+:** 71.46

*(Observation: Suspiciousness is distributed broadly and does not strictly correlate with being highly ranked. Products at all positions can be structurally anomalous relative to their expected rank.)*

### 4. Query-Level Analysis
- **Products per query (mean):** 24.86
- **Query mean suspiciousness (avg):** 48.33
- **Queries with max score >= 92:** 19

## Part B: Threshold Application
Applying calibrated synthetic thresholds to the real marketplace data. These items are "potentially suspicious" and "flagged by the framework" for investigation, not definitively manipulated.

### Threshold 85 (Sensitivity-Oriented)
- **Flagged Products:** 94 (8.59%)
- **Affected Queries:** 37 (84.09%)
- **Flagged Mean Rank:** 16.80
- **Flagged Median Rank:** 6.00

### Threshold 92 (Balanced Calibration)
- **Flagged Products:** 40 (3.66%)
- **Affected Queries:** 19 (43.18%)
- **Flagged Mean Rank:** 19.57
- **Flagged Median Rank:** 4.00

### Threshold 99 (Conservative)
- **Flagged Products:** 4 (0.37%)
- **Affected Queries:** 3 (6.82%)
- **Flagged Mean Rank:** 16.25
- **Flagged Median Rank:** 2.50

## Part C: Synthetic Validation Summary
*Note: These are controlled synthetic validation results derived from simulated rank permutations.*

- **Perturbation Sensitivity:** Mean target score scales monotonically with magnitude (Small ~47, Medium ~54, Large ~68).
- **Directional Robustness:** Both 80% upward promotions and 80% downward demotions produce highly similar anomaly separability (ROC-AUC 0.68 vs 0.69).
- **Metric Performance (Large Shift):** ROC-AUC ~0.68. PR-AUC ~0.057 (vs a 0.015 random baseline prevalence).
- **Seed Stability:** Variance across 10 random permutations was extremely low for AUC metrics and FPR.
- **Detector Performance at Threshold 92 (Large Shifts):**
  - **Recall:** ~22%
  - **Precision:** ~6.3%
  - **F1:** ~9.7%
  - **Control FPR:** ~4.7%
  - **Collateral FPR:** ~1.8% (Displaced neighbours are largely insulated from being falsely flagged).

## Part D: Comparative Interpretation

| Evidence Source | What it demonstrates | What it does NOT demonstrate |
|---|---|---|
| **Real marketplace data** | Behaviour of the framework on observed ranking data | Actual manipulation ground truth |
| **Synthetic perturbation** | Sensitivity to controlled rank changes | Real adversarial manipulation |
| **Threshold calibration** | Candidate operating points | Universal threshold |
| **Robustness analysis** | Internal stability under tested variations | General real-world robustness |

## Part E: Final Research Findings
1. The framework successfully identifies products exhibiting unusually large discrepancies between expected and observed ranking, flagging approximately 3.7% of the marketplace dataset at the balanced T=92 threshold.
2. Controlled synthetic experiments demonstrate strictly increasing detector response mathematically mirroring increasing perturbation magnitude.
3. The detector exhibits highly symmetric behaviour for upward and downward synthetic perturbations of equivalent relative severity.
4. Small rank perturbations (~25% shift) overlap substantially with the normal score distribution in the evaluated dataset, meaning minor anomalies are empirically indistinguishable from organic marketplace noise.
5. The selected thresholds represent mathematical calibration points optimized for the isolated experimental environment rather than universally valid or proven manipulation bounds.
