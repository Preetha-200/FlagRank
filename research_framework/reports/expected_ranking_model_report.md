# Expected-Ranking ML Model Report

## 1. Modelling Objective
To build a reproducible ML baseline that estimates the expected Amazon search rank of a product exclusively from its observable explanatory signals, without learning from the observed ranking itself.

## 2. Target Representation: Query-Relative Normalized Position
In e-commerce search, ranking competition takes place strictly within the retrieved query candidate set ($N_q \in [4, 59]$).
To avoid query result length heterogeneity skewing absolute rank scales, the model predicts the query-relative normalized position:
$$y_i = \frac{r_i - 1}{N_q - 1} \in [0, 1]$$
At inference time, the predicted relative position is mapped back to the expected absolute rank within the query result list:
$$\hat{r}_i = 1 + \hat{y}_i (N_q - 1)$$
bounded strictly within $[1, N_q]$.

## 3. Input Features
Used exactly 12 explanatory features (pruned redundant `feat_desc_length` which duplicated `feat_title_length`):
feat_discounted, feat_sponsored, feat_price, feat_original_price, feat_savings_percent, feat_rating, feat_total_reviews_log, feat_brand_freq, feat_product_type_freq, feat_color_freq, feat_title_length, feat_title_query_overlap

## 4. Excluded Fields (Leakage Prevention)
Explicitly blocked: `amazon_rank`, `is_amazon_top6`, `query`, `category`, `asin`, `url`, `thumbnail`, `currency`.

## 5. Grouping Strategy & Folds
- **Group Variable:** `query`
- **Folds:** 5
- **Methodology:** `GroupKFold` ensures that all products for a given search query belong entirely to a single fold. Queries never cross between train and validation within the same fold, ensuring true generalization context.

## 6. Random Forest Configuration
- `n_estimators`: 300
- `max_depth`: 6
- `min_samples_leaf`: 4
- `max_features`: 'sqrt'
- `random_state`: 42

## 7. Model Performance Metrics
*(Note: These metrics strictly assess how well the baseline model maps organic signals to rank.)*

### Full-Dataset OOF Performance
- **OOF MAE:** 8.0502
- **OOF RMSE:** 10.4947
- **OOF R²:** 0.4055
- **OOF Spearman Correlation:** 0.5553

### Previous Grouped 80/20 Test Performance (For Historical Comparison)
- **Test MAE:** 7.8927
- **Test RMSE:** 9.8449
- **Test R²:** 0.3066
- **Test Spearman Correlation:** 0.4495

## 8. Limitations & Reproducibility
- **Limitations:** Query size $N_q$ is an inference-time context parameter representing the size of the retrieved search list.
- **Reproducibility:** Seed fixed at 42. `GroupKFold` provides deterministic indices for a static dataset.
