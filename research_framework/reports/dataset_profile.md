# Dataset Inspection Report: Amazon Search Dataset

## 1. Dataset Facts Directly Observed from the Data

### Dimensions & Structure
- **Format:** CSV
- **Rows:** 1094
- **Columns:** 24
- **Unique Search Queries:** 44
- **Unique Products (ASINs):** 1046
- **Duplicate Rows:** 0

### Column Specifications
The dataset contains the following 24 columns:
`query`, `amazon_rank`, `is_amazon_top6`, `asin`, `title`, `description`, `brand`, `product_type`, `price`, `currency`, `discounted`, `original_price`, `savings_percent`, `rating`, `total_reviews`, `amazon_choice`, `best_seller`, `amazon_prime`, `sponsored`, `color`, `features_raw`, `category`, `url`, `thumbnail`.

### Missing Values
- **`features_raw`**: 100.0% missing (completely null)
- **`color`**: 52.65% missing
- **`brand`**: 4.75% missing
- All other columns have 0% missing values.

### Ranking Architecture (`amazon_rank`)
- **Range:** 1 to 59
- **1-based:** Yes (Starts at 1)
- **Duplication within query:** False (No two products share the exact same rank for a single query).
- **Continuity within query:** True (Ranking increments cleanly by 1 without gaps).

### Numerical Field Distributions
- **`price`**: Range 0.0 to 2922.08 (Mean: 156.76)
- **`original_price`**: Range 0.0 to 2922.08 (Mean: 171.03)
- **`savings_percent`**: Range 0.0 to 90.0 (Mean: 8.11%)
- **`rating`**: Range 0.0 to 5.0 (Mean: 4.25)
- **`total_reviews`**: Range 0.0 to 102,800 (Mean: 3152.98)

### Categorical / Boolean Value Counts
- **`sponsored`**: 168 True, 926 False
- **`is_amazon_top6`**: 262 True, 832 False
- **`amazon_choice`**: 1094 False, 0 True
- **`best_seller`**: 1094 False, 0 True
- **`amazon_prime`**: 1094 False, 0 True

---

## 2. Initial Observations & Issues Requiring Attention Later

### Fields Encoding Visibility
- `amazon_rank`: The primary target representing the observed ranking outcome. Must **not** be used as a predictive feature.
- `is_amazon_top6`: Directly encodes visibility (whether the rank is 1-6). Strongly correlated with `amazon_rank` and likely represents data leakage if used as a predictive feature.

### Data Quality Anomalies
1. **Uniform Boolean Fields:** `amazon_choice`, `best_seller`, and `amazon_prime` contain *only* `False` values across the entire dataset. This severely limits their utility as observable signals for the expected-ranking model, as they offer zero variance.
2. **Empty Columns:** `features_raw` is completely empty and will provide no value.
3. **Price/Rating Floors:** The minimum values for `price`, `original_price`, `rating`, and `total_reviews` are all `0.0`. A price of $0.00 might indicate missing data masked as zero, which will need investigation during preprocessing.

*Note: No data has been transformed or modified. This report reflects the raw dataset state.*
