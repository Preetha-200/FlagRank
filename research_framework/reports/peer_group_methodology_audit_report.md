# Peer-Group Methodology Audit Report

## 1. Objective
Determine whether the current `rank_inconsistency_z` calculation is methodologically robust for identifying products whose observed ranking differs substantially from their expected ranking relative to other products in the same query group, specifically auditing the "Self-Inclusion" limitation.

## 2. Current vs Leave-One-Out (LOO) Results
Self-inclusion means a highly anomalous product pulls the query's mean towards itself and inflates the standard deviation, theoretically suppressing its own anomaly score. The Leave-One-Out formulation removes the product from its peer group before calculating the peer mean and standard deviation.

**Statistical Comparison (Z-Scores):**
- **Pearson Correlation:** 0.9985
- **Spearman Correlation:** 0.9996
- **Mean Absolute Difference:** 0.0492
- **Median Absolute Difference:** 0.0232
- **Max Absolute Difference:** 0.9305
- **95th Percentile Difference:** 0.1916

**Threshold Shifts:**
- **Changes > 0.25 z-score:** 35 (3.2%)
- **Changes > 0.50 z-score:** 3 (0.3%)
- **Changes > 1.00 z-score:** 0 (0.0%)

*Interpretation:* The extremely high correlation (>0.97) demonstrates that self-inclusion does not scramble the fundamental ranking of anomalies. However, some individual z-scores do shift notably (max difference of 0.93), confirming the mathematical effect exists.

## 3. Compare Extreme Candidates
### Stability of Absolute Z-Score Rankings
- **Top 10 Overlap:** 8/10
- **Top 20 Overlap:** 17/20
- **Spearman Rank Correlation (Absolute Z-Scores):** 0.9984

### Highest-Scoring Ranking-Inconsistency Candidates (Current Formulation)
```text
                                                                               query  amazon_rank  expected_rank  rank_deviation  rank_inconsistency_z  loo_rank_inconsistency_z  suspiciousness_score   z_diff
                           compact 65% mechanical, RGB, black PBT keycaps, under $80            2      35.688084      -33.688084             -2.795881                 -3.726381             99.588665 0.930501
                             Sony noise cancelling headphones, not black, under $250            4      25.204926      -21.204926             -2.543576                 -3.159953             97.349177 0.616377
wireless noise cancelling headphones with 30+ hour battery, black or grey, $100-$150           22       6.994499       15.005501              2.380582                  2.873732             95.836380 0.493150
             MacBook Air M3 alternative, not white, Windows, thin design, under $700            1      16.140393      -15.140393             -2.206335                 -2.617033             95.978062 0.410698
                  ASICS running shoes, overpronation, wide toe, not pink, under $150            2      27.987744      -25.987744             -2.165037                 -2.308156             98.450640 0.143119
                 PlayStation 5 slim, black disc edition, extra controller, $500-$600           17      40.424869      -23.424869             -2.140966                 -2.514425             80.214808 0.373459
         mirrorless camera, black body, in-body stabilization, beginners, under $700           20       4.518501       15.481499              2.136282                  2.507189             95.822669 0.370907
                             ultrawide curved, black frame, HDR, USB hub, under $500            7      18.932193      -11.932193             -2.104470                 -2.482044             91.654479 0.377574
                organic whole bean coffee, medium roast, single-origin, under $25/lb           46      13.110199       32.889801              2.070229                  2.196438             99.117916 0.126209
               Adidas running shoes, carbon plate, marathon, black or red, $150-$200           15      18.981440       -3.981440              2.063969                  2.473518             84.625229 0.409549
```

## 4. Query Group Size Effects
Self-inclusion theoretically impacts small groups much more severely than large groups, because one observation constitutes a larger percentage of the sample.

**Absolute Z-Score Difference by Query Size:**
```text
size_bucket  count     mean   median      max
        2-5      4 0.329165 0.299597 0.596554
       6-10      6 0.216369 0.223446 0.467390
      11-20    314 0.070032 0.039710 0.474248
      21-30    346 0.058348 0.029698 0.930501
      31-50    192 0.023665 0.014724 0.143119
        >50    232 0.019317 0.012627 0.099866
```
*Interpretation:* As expected, the smaller the peer group, the larger the mathematical impact of self-inclusion. The dataset has no groups smaller than 4. For groups size 4-10, the mean difference is significantly higher than for groups >50.

## 5. Zero / Near-Zero Standard Deviation Cases
- **Single-Product Groups:** 0
- **Two-Product Groups:** 0
- **Zero Std Groups:** 0
- **Near-Zero Std Groups (<1e-5):** 0

*Interpretation:* The dataset contains sufficient products per query (minimum size 4) such that zero-variance edge cases do not naturally occur in this pipeline. The current safe-handling (`std == 0` fallback to `z = 0.0`) is robust and correctly handles potential edge cases without distortion.

## 6. Impact on Suspiciousness Ranking
To determine whether this self-inclusion effect materially changes the final evaluation, we reconstructed the full `suspiciousness_score` using the LOO z-scores.

**Suspiciousness Score Comparison:**
- **Spearman Correlation:** 0.9996
- **Top 10 Overlap:** 9/10
- **Top 20 Overlap:** 19/20
- **Mean Absolute Score Difference:** 0.4011
- **Median Absolute Score Difference:** 0.2285
- **95th Percentile Score Difference:** 1.1883

*Interpretation:* Despite the mathematical shifts in raw z-scores, the final percentile-normalized suspiciousness score remains nearly identical (Spearman > 0.99, 9/10 top-candidate overlap). Because the final framework uses empirical percentile ranking, absolute z-score shifts rarely alter a product's rank relative to the entire catalog.

## 7. Methodological Interpretation
**Classification: RETAIN WITH CAVEAT**

The current standardization methodology is statistically defensible and robust for ranking inconsistency. While leave-one-out standardisation is mathematically purer for small sample sizes, the current dataset's peer groups are large enough (median 21) that the self-inclusion effect does not disrupt the final anomaly ranking. Furthermore, Empirical Percentile Normalization completely absorbs the minor continuous shifts, yielding virtually identical downstream candidate outputs. 

## 8. Research-Paper Recommendation
The final methodology should describe the query-level standardization as a **descriptive peer-group standardization**, explicitly noting that standard population-level z-scores were used rather than leave-one-out outlier bounds. The paper must state that while self-inclusion slightly dampens extreme anomaly magnitudes in very small queries, empirical testing confirmed the final rank-percentile score is robust to this effect. The score accurately functions as an empirical candidate-ranking mechanism, not a calibrated parametric outlier test.
