# Suspiciousness Scoring Methodology Audit Report

## 1. Objective
Audit the mathematical behavior of the existing Chunk 8 suspiciousness scoring framework after the dataset expanded to 1,094 rows. The purpose is to empirically evaluate the score distribution, component contributions, and normalization robustness using precise mathematical descriptions.

## 2. Reconstructed Components & Exact Normalizations
- **Component A:** `absolute_rank_inconsistency_z` = `abs(rank_inconsistency_z)` normalized via `rank(pct=True)`
- **Component B:** `absolute_relative_rank_gap` = `abs(relative_rank_gap)` normalized via `rank(pct=True)`
- **Component C:** `absolute_rank_deviation` = `abs(rank_deviation)` normalized via `rank(pct=True)`

### Empirical Percentile Normalization
Applying `rank(pct=True)` converts observations to empirical percentile ranks. With no ties, the resulting values are approximately evenly distributed over the empirical percentile positions. With ties, repeated percentile values occur. Therefore, the resulting distribution is an **empirical percentile-rank distribution**, not a theoretically perfect continuous `U(0,1)` distribution. The exact shape depends strictly on sample size and the ranking convention for ties.
Unique value proportions:
- `norm_inconsistency_z`: 1094 unique / 1094 total (100.0%)
- `norm_relative_gap`: 280 unique / 1094 total (25.6%)
- `norm_rank_deviation`: 1094 unique / 1094 total (100.0%)

## 3. Empirical Distribution of Final Score
The final suspiciousness score is a weighted sum of three empirical percentile-rank components. Its resulting distribution is determined by both the marginal distributions and the empirical correlation structure among those components. In this dataset, the final score happens to be approximately percentile-spread. This near-uniformity is an **empirical characteristic of this dataset and normalization procedure**.

**Distribution Statistics:**
```text
      suspiciousness_score
min               3.811700
1%                8.365356
5%               13.880484
10%              17.790219
25%              28.088437
50%              48.941956
75%              70.063985
90%              86.370658
95%              91.182815
99%              96.864625
max              99.588665
mean             50.045704
std              24.914965
```
**Empirical Proportions by Range:**
- `[0,20)`: 12.2%
- `[20,40)`: 28.1%
- `[40,60)`: 23.5%
- `[60,80)`: 20.4%
- `[80,100]`: 15.8%

## 4. Component Relationships
**Spearman Rank Correlation:**
```text
                      norm_inconsistency_z  norm_relative_gap  norm_rank_deviation  suspiciousness_score
norm_inconsistency_z              1.000000           0.622158             0.643760              0.945771
norm_relative_gap                 0.622158           1.000000             0.407256              0.794288
norm_rank_deviation               0.643760           0.407256             1.000000              0.747660
suspiciousness_score              0.945771           0.794288             0.747660              1.000000
```
*Interpretation:* The components are positively associated. None of the pairwise Spearman correlations is close to 1.0. Therefore, they are not exact monotonic duplicates of one another. However, correlation alone does not establish that each component contributes entirely independent information. The weighting framework intentionally gives each component a distinct methodological role.

## 5. Component Contributions
The final score uses fixed theoretical weights (50/30/20). The actual observed contribution across the dataset depends on the empirical observations.

**Observed Average Contribution (Absolute Scale [0,1]):**
```text
                 mean       50%       std       25%       75%       95%  max
contrib_z    0.250229  0.250229  0.144404  0.125343  0.375114  0.475023  0.5
contrib_gap  0.150137  0.150137  0.086633  0.075206  0.224589  0.284925  0.3
contrib_dev  0.100091  0.100091  0.057761  0.050137  0.150046  0.190009  0.2
```
*Note: Max theoretical possible contributions remain exactly 0.50, 0.30, and 0.20 respectively.*

**Observed Average Contribution (Percentage of Total Score):**
```text
             mean       50%       std
pct_z    0.476580  0.500464  0.153673
pct_gap  0.315245  0.310869  0.160162
pct_dev  0.208176  0.194631  0.117153
```

## 6. Robustness to Normalization Alternatives
Two mathematical alternatives were audited offline:
- **Alt A (Min-Max):** Vulnerable to outliers compressing the scale.
- **Alt B (Robust 95th Percentile Clip + Min-Max):** Controls extreme outliers but caps maximum values.

### Candidate Ranking Overlap
- **Top 10 Overlap:** Prod vs Alt A (8/10), Prod vs Alt B (9/10)
- **Top 20 Overlap:** Prod vs Alt A (17/20), Prod vs Alt B (16/20)
- **Spearman Correlation (Full Dataset):** Prod vs Alt A (0.9972), Prod vs Alt B (0.9978)

*Interpretation:* The high rank correlation and substantial top-candidate overlap indicate that the highest-ranking inconsistency candidates are relatively stable across the tested normalization alternatives.

## 7. Edge Cases
- `NaN`s, Infs: 0
- Scores outside `[0, 100]`: 0

## 8. Explicit Interpretation Statement
> The suspiciousness score is an empirical, relative ranking-inconsistency measure. A score indicates how extreme a product's observed-versus-expected ranking discrepancy is relative to the evaluated dataset under the selected normalization and weighting scheme. It is not a probability, confidence value, or proof of ranking manipulation.

## 9. Final Classification
**RETAIN WITH CAVEAT**

The percentile normalization (`rank(pct=True)`) is empirically stable and mathematically acceptable for creating a relative candidate list. However, it must be explicitly caveated that the score represents a relative empirical ranking-inconsistency severity within this specific dataset. It should not be interpreted as an absolute manipulation probability, and scores cannot be directly compared across unrelated datasets without recalibration.
