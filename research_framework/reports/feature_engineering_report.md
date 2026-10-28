# Feature Engineering Report

## 1. Input Columns
The pipeline consumes the cleaned dataset from `data/processed/amazon_search_dataset.csv`, referencing the variables authorized in `src/features/signal_specification.py` (Explanatory Signals).

## 2. Output Feature Columns
The following engineered features are generated (all prefixed with `feat_`):
- `feat_price`, `feat_original_price`, `feat_savings_percent`, `feat_rating`
- `feat_total_reviews_log`
- `feat_discounted`, `feat_sponsored`
- `feat_brand_freq`, `feat_product_type_freq`, `feat_color_freq`
- `feat_title_length`, `feat_title_query_overlap`, `feat_desc_length`

## 3. Transformations Applied
| Feature | Source | Signal Type | Transformation | Reason |
|---------|--------|-------------|----------------|--------|
| `feat_total_reviews_log` | `total_reviews` | Numeric | Log1p (`log(x+1)`) | Review counts exhibit extreme right-skew. Log scaling linearizes this distribution. |
| `feat_price`, etc. | `price`, etc. | Numeric | Float Cast | Direct continuous signal. |
| `feat_discounted` | `discounted` | Boolean | Int Cast (0/1) | Required for numerical models. |
| `feat_sponsored` | `sponsored` | Boolean | Int Cast (0/1) | Required for numerical models. |

## 4. Treatment of Categorical Variables
- Variables: `brand`, `product_type`, `color`
- **Transformation:** Frequency Encoding (mapping category string to its normalized occurrence frequency in the training data).
- **Reason:** One-hot encoding `brand` or `product_type` across a small dataset (1094 rows) creates extreme high-dimensionality and sparsity, leading to overfitting. Frequency encoding captures the "popularity" of the category directly in a single continuous dimension without target leakage.

## 5. Treatment of Text Variables
- Variables: `title`, `description`
- **Transformation:** Lightweight feature extraction (`length` and `title_query_overlap_ratio`).
- **Reason:** Large pretrained LLMs or TF-IDF matrices overfit heavily on small datasets. E-commerce rank relevance is heavily tied to exact keyword matches. Thus, calculating the overlap of query unigrams in the title string captures core semantic relevance cleanly and robustly.

## 6. Treatment of Boolean Variables
- Simply cast from `bool` to `int` (`0` or `1`).

## 7. Explicit Leakage Safeguards
- The engineering script strictly iterates over predefined `EXPLANATORY_SIGNALS`.
- It dynamically strips out ANY column not prefixed with `feat_` except for explicit context/outcome preservation (`query`, `category`, `amazon_rank`, `is_amazon_top6`, `asin`).
- It runs a final mathematical assertion ensuring `amazon_rank` and `is_amazon_top6` do not appear in the pool of predictive features.

## 8. Limitations Caused by the Small Dataset
- Frequency encoding lumps all rare brands together at low probabilities, losing brand-specific cachet (e.g., Apple vs generic).
- Text embeddings were skipped to prevent overfitting, meaning synonymous words in the query and title might not be recognized as overlapping.
