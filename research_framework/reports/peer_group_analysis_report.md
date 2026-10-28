# Full-Dataset OOF Peer-Group Analysis and Ranking Inconsistency Report

## 1. Definition of Peer Group
A peer group is defined strictly as **all products belonging to the same search query**. Categories are not used as peer groups because ranking competition occurs locally within a specific user search intent, not globally across an entire category.
This analysis evaluates the **full dataset** using Out-Of-Fold expected ranks.

## 2. Peer Group Statistics
- **Unique queries:** 44
- **Minimum peer-group size:** 4 products
- **Maximum peer-group size:** 59 products
- **Median peer-group size:** 21.0 products

## 3. Rank Deviation
**Formula:** `rank_deviation = amazon_rank - expected_rank`
- **Positive value:** The product appeared *lower* in the search results (e.g. rank 10) than the model expected (e.g. rank 2).
- **Negative value:** The product appeared *higher* in the search results (e.g. rank 2) than the model expected (e.g. rank 10). A highly negative value is a candidate signal for unexplained rank inflation.

## 4. Query-Relative Z-Score
**Formula:** `rank_inconsistency_z = (rank_deviation - query_deviation_mean) / query_deviation_std`
Absolute deviation values can be misleading depending on the variance of the model within a specific query. The Z-score measures how unusual a product's deviation is *relative to other products in the exact same search query*.
- **Edge Case Handling:** If `query_deviation_std` is 0.0 or NaN (e.g., only one product in query, or model predicts identical deviations), the Z-score explicitly defaults to `0.0`.

## 5. Percentile Methodology & Relative Rank Gap
**Formula:** `relative_rank_gap = observed_rank_percentile - expected_rank_percentile`
We calculate percentiles for both `amazon_rank` and `expected_rank` within each query. 
- A lower percentile (e.g., 0.1) means the product is at the top of the search page.
- A negative `relative_rank_gap` means the product occupies a *better* (top) percentile position observed in reality compared to what its organic explanatory features suggest.

## 6. Descriptive Statistics of Inconsistency Measures
```text
Rank Deviation: Mean -0.24, Min -32.83, Max 35.21
Rank Inconsistency Z-Score: Mean -0.00, Min -2.10, Max 2.16
Relative Rank Gap: Mean -0.00, Min -0.91, Max 0.98
```

## 7. Limitations
- Percentile resolution is limited by peer group sizes (e.g., if a query only has 5 products, percentiles move in increments of 0.2).
- The baseline expected model is not perfectly calibrated list-wise, meaning `expected_rank` can theoretically produce decimals or out-of-bound bounds. The within-query percentiling and Z-score calculations mitigate this structurally.
