# End-to-End Ranking Inconsistency Validation Report

## 1. Objective
Validate the complete Search Ranking Manipulation Detection framework. Evaluate whether the outputs are statistically meaningful, internally consistent, and accurately interpretable as ranking-inconsistency signals.

## 2. Expected-vs-Observed Ranking Behaviour
- **OOF MAE:** 9.12
- **OOF RMSE:** 12.08
- **OOF R²:** 0.21
- **Pearson Correlation:** 0.4693
- **Spearman Correlation:** 0.4447

*Interpretation:* The R² of 0.21 means the observable-signal model explains approximately 21% of the variance in observed rank under the OOF evaluation. The moderate explanatory performance provides a useful baseline for comparing observed ranking against an observable-signal-based expected ranking. However, the remaining unexplained variation must not be interpreted as evidence of manipulation. It may include omitted observable factors, latent ranking-system factors, model limitations, nonlinear/interaction effects not captured adequately, measurement noise, and other sources. Ranking inconsistency is derived from the observed-vs-expected discrepancy; it is not automatically synonymous with unexplained variance or manipulation. A higher or lower R² is not itself evidence for or against manipulation.

## 3. Ranking Direction
- `rank_deviation < 0`: Observed ranking is better than expected (e.g. ranked 2, expected 24 -> deviation -22).
- `rank_deviation > 0`: Observed ranking is worse than expected (e.g. ranked 45, expected 15 -> deviation +30).

## 4. Ranking Inconsistency Distribution
```text
                                     min         5%        25%        50%        75%        95%        99%        max          mean        std
rank_deviation                -33.688084 -18.042217  -7.026093  -0.168762   6.390607  23.887549  34.128331  44.347763  5.163405e-01  12.074918
rank_inconsistency_z           -2.795881  -1.543812  -0.818037   0.011263   0.785744   1.532373   1.934721   2.380582  4.871180e-18   0.980132
relative_rank_gap              -0.952381  -0.628680  -0.271098   0.000000   0.250000   0.633254   0.858393   0.966102 -2.029658e-18   0.382442
absolute_rank_inconsistency_z   0.001252   0.068062   0.398262   0.792519   1.211587   1.723137   2.052298   2.795881  8.293731e-01   0.521699
absolute_relative_rank_gap      0.000000   0.017544   0.123355   0.263158   0.473684   0.739964   0.882369   0.966102  3.078009e-01   0.226790
absolute_rank_deviation         0.013245   0.645277   3.337011   6.842988  12.466300  25.679058  34.128331  44.347763  9.124647e+00   7.920551
suspiciousness_score            3.811700  13.880484  28.088437  48.941956  70.063985  91.182815  96.864625  99.588665  5.004570e+01  24.914965
```
*Interpretation:* The distributions show substantial variability. While many products lie relatively close to their expectation, severe discrepancies exist at both tails of the distribution.

## 5. Component Relationships
**Pearson Correlation with Final Score:**
- Absolute Z-Score vs Score: 0.9419
- Absolute Relative Gap vs Score: 0.8247
- Absolute Deviation vs Score: 0.6900

*Interpretation:* The component-score relationships are consistent with the intended weighted construction. The selected 50/30/20 weights are methodological design choices rather than empirically proven optimal weights.

## 6. Highest-Scoring Candidates (Top 20)
*(Note: These are "highest-scoring ranking-inconsistency candidates", NOT confirmed manipulations. They are simply products whose ranking positions are highly unexplained by observable features relative to their peers.)*
```text
                                                                               query    category  amazon_rank  expected_rank  rank_deviation  rank_inconsistency_z  relative_rank_gap  suspiciousness_score  feat_sponsored
                           compact 65% mechanical, RGB, black PBT keycaps, under $80       other            2      35.688084      -33.688084             -2.795881          -0.904762             99.588665               1
                           Nike running shoes in blue or grey, cushioned, under $120    footwear           59      14.652237       44.347763              2.041157           0.966102             99.451554               0
                organic whole bean coffee, medium roast, single-origin, under $25/lb     grocery           46      13.110199       32.889801              2.070229           0.895833             99.117916               0
                        Colombian espresso, low acidity, specialty grade, $15-$25/lb     grocery           54      11.623980       42.376020              1.934448           0.929825             98.893967               1
                  ASICS running shoes, overpronation, wide toe, not pink, under $150    footwear            2      27.987744      -25.987744             -2.165037          -0.875000             98.450640               0
         bamboo paper towels, reusable, not single-use, natural tan color, under $30   household           56      17.409377       38.590623              1.953428           0.796610             98.107861               1
                           Nike running shoes in blue or grey, cushioned, under $120       other           57      17.057036       39.942964              1.805429           0.881356             97.861060               0
                   recycled paper towels, white, FSC certified, bulk pack, under $40       other           53      18.095343       34.904657              2.036434           0.736842             97.701097               1
                        Colombian espresso, low acidity, specialty grade, $15-$25/lb     grocery           57      16.079785       40.920215              1.847223           0.807018             97.513711               1
                Hoka running shoes, not black, maximalist, grey or white, under $160       other           45      14.070350       30.929650              1.785903           0.895833             97.390311               0
                             Sony noise cancelling headphones, not black, under $250 electronics            4      25.204926      -21.204926             -2.543576          -0.818182             97.349177               0
                        Colombian espresso, low acidity, specialty grade, $15-$25/lb     grocery           53      14.139547       38.860453              1.723812           0.824561             96.828154               1
                Hoka running shoes, not black, maximalist, grey or white, under $160       other            4      34.378366      -30.378366             -1.882315          -0.708333             96.220293               0
             MacBook Air M3 alternative, not white, Windows, thin design, under $700   computers            1      16.140393      -15.140393             -2.206335          -0.952381             95.978062               1
                   Brooks running shoes women, neutral, not pink or rose, under $130    footwear           46      18.500453       27.499547              1.854422           0.708333             95.850091               0
wireless noise cancelling headphones with 30+ hour battery, black or grey, $100-$150 electronics           22       6.994499       15.005501              2.380582           0.909091             95.836380               1
         mirrorless camera, black body, in-body stabilization, beginners, under $700     cameras           20       4.518501       15.481499              2.136282           0.904762             95.822669               1
                  ASICS running shoes, overpronation, wide toe, not pink, under $150    footwear            4      26.274792      -22.274792             -1.886131          -0.750000             95.767824               0
                           Nike running shoes in blue or grey, cushioned, under $120    footwear            1      27.732758      -26.732758             -1.762793          -0.762712             95.740402               0
                          noise cancelling headphones in silver or white, under $200 electronics            2      18.490801      -16.490801             -1.963356          -0.863636             95.356490               1
```
*Interpretation:* A candidate with a negative rank deviation appears substantially better positioned than its observable-signal-based expected rank. A candidate with a positive rank deviation appears substantially worse positioned than its expected rank.

## 7. Compare Candidate Direction (Top 10% Scores)
- **Better-than-expected (Dev < 0):** 54 (49.1%) | Mean Abs Dev: 18.12 | Mean Score: 91.59
- **Worse-than-expected (Dev > 0):** 56 (50.9%) | Mean Abs Dev: 22.74 | Mean Score: 91.78

*Interpretation:* Among the highest-scoring candidates in this dataset, ranking inconsistencies occur in both directions, with comparable counts of better-than-expected and worse-than-expected placements. This indicates that the scoring procedure does not inherently favour one deviation direction in this evaluated dataset.

## 8. Sponsored vs Non-Sponsored Findings
- **Sponsored:** Count 168 | Mean Score: 61.44 | P95: 95.66 | Mean Abs Dev: 11.65
- **Non-Sponsored:** Count 926 | Mean Score: 47.98 | P95: 89.17 | Mean Abs Dev: 8.67
- **T-Test (Scores):** t = 6.2020, p = 2.7034e-09
- **Cohen's d Effect Size:** 0.5508

*Interpretation:* The test indicates a statistically detectable difference between the evaluated sponsored and non-sponsored score distributions under the chosen test. Statistical significance does NOT establish practical significance by itself. Sponsorship may be related to ranking behaviour, but this analysis cannot determine why. Sponsorship is an observable input to the expected-ranking model and is NOT directly added as a suspiciousness-score bonus/penalty. Sponsored does NOT mean manipulated.

## 9. Query-Level Behaviour
```text
                                                                         count  mean_score  median_score  max_score  std_score  mean_abs_dev
query                                                                                                                                       
flagship Android, space grey or titanium, 5G, above $600                     4   64.394424     62.477148  74.021938   7.058134     12.423809
business laptop, not gold, fingerprint reader, Thunderbolt 4, $600-$800      6   59.037172     65.779250  80.626143  19.076742      7.976209
Nike running shoes in blue or grey, cushioned, under $120                   59   58.491309     59.255027  99.451554  23.508149     17.096448
Adidas running shoes, carbon plate, marathon, black or red, $150-$200       18   55.830794     55.838665  94.095064  21.609990     19.560506
over-ear headphones, foldable, space grey or black, under $200              20   55.515311     57.655393  89.725777  23.029329     10.065330
Hoka running shoes, not black, maximalist, grey or white, under $160        48   55.443518     53.658592  97.390311  28.614774     14.093646
Brooks running shoes women, neutral, not pink or rose, under $130           48   54.393662     53.183272  95.850091  25.662358     12.086899
organic whole bean coffee, medium roast, single-origin, under $25/lb        48   54.327201     57.333181  99.117916  25.969733     12.577657
Colombian espresso, low acidity, specialty grade, $15-$25/lb                57   53.879454     47.810786  98.893967  25.273780     15.617064
Dell XPS 13 competitor, OLED, silver color, under $1000                     16   53.709723     52.655393  95.338208  26.817835      8.646171
```
*Interpretation:* The distribution of suspiciousness varies across query groups, with some queries exhibiting higher mean ranking-inconsistency scores than others. These differences indicate that ranking inconsistency is not distributed uniformly across query contexts in this dataset. The analysis does not establish the cause of these differences.

## 10. Check Whether Suspiciousness Is Merely Rank Position
- **Pearson (Rank vs Score):** 0.1101
- **Spearman (Rank vs Score):** -0.0100
```text
                  mean     median        std
rank_bucket                                 
1-10         52.103971  52.049817  25.218572
11-20        45.730858  43.498629  23.565581
21-40        42.097978  37.001828  22.236466
41-59        71.266612  75.473035  19.624734
```
*Interpretation:* The near-zero Spearman correlation indicates that suspiciousness score is not strongly associated with raw observed rank in this dataset. Therefore, the score is not simply a monotonic proxy for being near the top or bottom of the ranking.

## 11. Observable-Factor Relationships
```text
                 feature  spearman_expected_rank  spearman_abs_dev  spearman_score
          feat_sponsored               -0.007209          0.124468        0.188119
         feat_discounted               -0.227216         -0.138362       -0.061574
              feat_price               -0.444178         -0.201769       -0.015561
     feat_original_price               -0.488238         -0.227131       -0.029768
    feat_savings_percent               -0.245149         -0.142279       -0.069102
             feat_rating                0.068200          0.112995        0.010831
  feat_total_reviews_log                0.065936          0.052254        0.015261
         feat_brand_freq               -0.046133         -0.027369       -0.047343
  feat_product_type_freq                0.597654          0.361900        0.095624
         feat_color_freq                0.394828          0.219992        0.074150
       feat_title_length               -0.429165         -0.247488       -0.053886
feat_title_query_overlap               -0.255008         -0.184238       -0.033028
        feat_desc_length               -0.429165         -0.247488       -0.053886
```
*Interpretation:* No individual evaluated observable feature shows a strong monotonic association with the final suspiciousness score in this dataset. This suggests that the score is not dominated by a single basic feature under the tested associations, although this does not establish complete multivariate independence.

## 12. Target Leakage Audit
- `amazon_rank`, `is_amazon_top6`, `query`, and `category` were strictly excluded from model feature inputs.
- OOF predictions were generated using `GroupKFold(query)`, preventing any target training leakage.
- No binary target logic feedbacks into expected rank generation.

## 13. Stability Check
The entire pipeline relies on deterministic grouping, deterministic model seeding (`random_state=42`), and deterministic score standardisation.

## 14. Current Validation Boundary
The present evaluation is an internal validation of the framework's computational consistency, leakage controls, ranking-inconsistency behaviour, and score stability. The dataset does not provide independently verified labels identifying manipulated rankings. Therefore, the present results demonstrate the framework's ability to quantify and rank relative observed-vs-expected inconsistencies, but they do not establish real-world manipulation-detection accuracy.

## 15. Research Interpretation

### Supported by Current Evidence
The framework can currently claim that it:
1. Builds an observable-signal-based expected-ranking baseline using grouped OOF evaluation.
2. Quantifies observed-vs-expected ranking deviation.
3. Contextualizes deviation within query-level peer groups.
4. Produces a continuous relative suspiciousness score.
5. Produces stable candidate rankings under the tested scoring alternatives.
6. Maintains strict target-leakage safeguards.
7. Identifies ranking-inconsistency candidates in both better-than-expected and worse-than-expected directions.

### Not Supported by Current Evidence
The framework cannot currently claim that it:
1. Proves ranking manipulation.
2. Identifies ground-truth manipulated products.
3. Estimates a probability of manipulation.
4. Establishes intentional behaviour by sellers or platforms.
5. Establishes causality.
6. Demonstrates real-world detection precision/recall for manipulation.
