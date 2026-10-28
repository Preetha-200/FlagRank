# Preprocessing Report

## 1. Input Dataset Dimensions
- **Rows**: 1094
- **Columns**: 24

## 2. Cleaning Decisions
- **Zero-variance columns dropped**: `amazon_choice`, `best_seller`, `amazon_prime` (Uniformly False).
- **Empty columns dropped**: `features_raw` (100% missing).
- `is_amazon_top6` is retained as a validation metric but explicitly flagged to NOT be used as a predictive feature to prevent data leakage regarding `amazon_rank`.
- `amazon_rank` is retained as the outcome target.

## 3. Zero-Value Treatment
- **`price` & `original_price`**: Exactly 76 rows had a price of `0.0`. In e-commerce, a $0.00 price for physical goods indicates scraping failures or unavailable pricing, not free items. These were converted to `NaN`.
- **`rating` & `total_reviews`**: Exactly 27 rows had a rating of `0.0` and `0` total reviews. This represents a valid e-commerce state (a newly listed product with no reviews). These zeros were **retained**.

## 4. Missing-Value Treatment
- **`price` & `original_price`**: Imputed using the global median price (excluding zeros). No target information (`amazon_rank`) was used.
- **`brand`**: Imputed with the string placeholder `'Unknown'`.
- **`color`**: Imputed with the string placeholder `'Unknown'`.

## 5. Duplicate and Validity Checks
- **Duplicate rows**: 0 rows found.
- **Missing ASINs**: 0
- **Missing queries**: 0
- **Ranking continuity**: Checked and verified that all queries have continuous 1-based rankings with no duplicates.
- **Rows removed**: 0. The dataset dimensions remain fully intact row-wise.

## 6. Output Dataset Dimensions
- **Rows**: 1094
- **Columns**: 20 (4 columns dropped)

## 7. Limitations
- Imputing missing prices with the global median reduces variance and might obscure premium vs budget product distinctions. A query-level median could be explored in future iterations.
- Over 50% of the `color` feature is missing, meaning it might have weak predictive power.
