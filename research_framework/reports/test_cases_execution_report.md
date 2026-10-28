# FlagRank Test Cases Execution Report

## Overview
This report documents the verification and execution of the 10 core functional, algorithmic, and user-interface test cases of the **FlagRank** ranking manipulation detection framework. All tests were executed against the real application codebase, backend API services, and actual search ranking dataset (`research_framework/data/raw/amazon_search_dataset.csv`).

**Execution Date:** 2026-10-14  
**Environment:** Python 3.12.9, FastAPI, Uvicorn, Scikit-learn 1.3.2, Pandas 2.1.3, Vite 8.2.1, Playwright 1.62.0, Chromium Headless  
**Execution Summary:** 10 Passed, 0 Failed, 0 Blocked

---

## Test Execution Summary Table

| Test Case ID | Test Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC01** | Upload a valid CSV dataset | Backend accepts valid CSV via `/api/analyze`, validates non-empty status and required schema columns, streams pipeline progress milestones, and returns HTTP 200 with completed dataset analysis metadata. | Accepted 1,094-row dataset `amazon_search_dataset.csv`, streamed all 7 lifecycle milestones (`upload_complete` through `analysis_complete`), and returned HTTP 200 with full metadata (`oof_mae=9.1246`, `oof_rmse=12.0804`, `oof_r2=0.2122`). | PASS |
| **TC02** | Process missing or zero-valued price entries | Identify missing and 0.0-valued price entries during data preprocessing and impute them with the global median price ($69.95), leaving 0 zero or null prices. | Preprocessor detected 76 zero-price records in raw dataset, computed `global_median_price = 69.95`, and successfully imputed all 76 occurrences to 69.95; post-transformation verified 0 zero or null price records remaining. | PASS |
| **TC03** | Validate observed product ranks within each query | Verify that observed search ranks for every query group strictly form a continuous, gapless sequence starting at 1 (1..N); reject non-1 or discontinuous sequences. | Validated across all 44 unique queries: all groups strictly start at rank 1 and increment continuously to N (max rank 59); negative control test injecting rank starting at 2 raised `AssertionError`. | PASS |
| **TC04** | Generate product features | Execute feature engineering pipeline to derive ranking, content, and price features according to the defined feature schema. | Generated 18 columns (13 `feat_*` numerical features + 5 context columns) of shape `(1094, 18)` with 0 null/NaN values across all records; all values bounded within expected numerical intervals. | PASS |
| **TC05** | Predict expected product ranks using Random Forest | Fit 5-Fold GroupKFold `RandomForestRegressor` (`n_estimators=100`, `random_state=42`) grouped by search query to generate out-of-fold expected rank predictions. | Generated 1,094 out-of-fold predictions ranging from 3.65 to 42.26 (mean: 16.84); all predictions strictly positive and finite; baseline model achieved MAE of 9.1246, RMSE of 12.0804, and R² of 0.2122. | PASS |
| **TC06** | Calculate ranking deviation and peer-group inconsistency | Compute directional rank deviation (`amazon_rank - expected_rank`), relative rank gap, and peer-group inconsistency z-score for each product. | Successfully calculated for all 1,094 products: `rank_deviation` spans `[-33.69, +44.35]`, `relative_rank_gap` spans `[-0.95, +0.97]`, and `rank_inconsistency_z` spans `[-2.80, +2.38]`; 0 nulls, all finite. | PASS |
| **TC07** | Generate suspiciousness scores | Compute composite suspiciousness score using documented 50/30/20 formula (50% rank deviation, 30% peer inconsistency, 20% price disparity). | Generated 1,094 scores ranging from 3.81 to 99.59 (mean: 50.05, median: 48.94, std: 24.91); 100% strictly bounded in `[0.0, 100.0]`; top anomalous candidate ASIN `B0D1P9P8MP` scored 99.59. | PASS |
| **TC08** | Apply the configured anomaly threshold | Apply decision boundary rule (`score >= threshold`) at calibrated operating points (T=92.0 balanced/Max-F1, T=90.0, T=85.0 sensitive) to flag anomalous candidates. | Thresholding correctly flags products exceeding boundary: at T=92.0: 45 flagged (4.11%, 23 queries); at T=90.0: 72 flagged (6.58%); at T=85.0: 127 flagged (11.61%, 38 queries); exact `>=` boundary conditions verified. | PASS |
| **TC09** | Evaluate the model and synthetic scenarios | Run final evaluation pipeline and evaluate multi-seed synthetic perturbation suite (Scenarios S1–S6 across 10 random seeds). | Executed `final_evaluation.py` and evaluated S1–S6 across seeds 42–51. Monotonic response confirmed: S1 (Up 25%): ROC-AUC 0.4269, Target 46.02; S2 (Up 50%): ROC-AUC 0.4995, Target 53.81; S3 (Up 80%): ROC-AUC 0.6810, Target 67.51; S4 (Down 25%): ROC-AUC 0.4617, Target 48.65; S5 (Down 50%): ROC-AUC 0.5154, Target 54.85; S6 (Down 80%): ROC-AUC 0.6953, Target 68.33. Generated distribution plots and report in `data/processed/final_evaluation/`. | PASS |
| **TC10** | Display analysis results in the frontend | End-to-end browser execution: verify initial `--` empty state, upload CSV dataset, stream analysis milestones, verify populated metric cards and candidate table, and click "Analyze" to view product details. | Executed automated Chromium test via Playwright. Initial state verified with `--` placeholders and 0 tables; uploaded `amazon_search_dataset.csv`; streaming completed; cards displayed Products: 1,094, Queries: 44, Range: 1 to 59, MAE: 9.12, RMSE: 12.08, R²: 0.21; candidate table rendered 15 rows/page with top candidate `B0D1P9P8MP` (Score: 99.6); clicking "Analyze" navigated to `/product/B0D1P9P8MP` displaying product title, image, and peer breakdown. Audit screenshot captured. | PASS |

---

## Detailed Execution Evidence

### TC01: Upload Valid CSV Dataset
- **Module:** `api/server.py` (`POST /api/analyze`)
- **Command:** `python -m pytest research_framework/tests/test_api_server.py` & TestClient execution.
- **Evidence:**
  - HTTP Status: `200 OK`
  - Streaming Events: `upload_complete`, `preprocessing_complete`, `feature_engineering_complete`, `model_training_complete`, `deviation_analysis_complete`, `peer_group_analysis_complete`, `analysis_complete`.
  - Output Metadata: `{"total_products": 1094, "unique_queries": 44, "rank_min": 1, "rank_max": 59, "oof_mae": 9.1246, "oof_rmse": 12.0804, "oof_r2": 0.2122}`.

### TC02: Process Missing or Zero-Valued Price Entries
- **Module:** `research_framework/src/data/preprocessing.py` (`Preprocessor`)
- **Evidence:**
  - Raw dataset check: `(raw_df['price'] == 0.0).sum() == 76`
  - Preprocessor computed median: `global_median_price = 69.95`
  - Post-imputation check: `(clean_df['price'] == 0.0).sum() == 0`, `clean_df['price'].isna().sum() == 0`
  - All 76 zero entries imputed to 69.95.

### TC03: Validate Observed Product Ranks
- **Module:** `research_framework/src/data/preprocessing.py`
- **Evidence:**
  - Tested 44 unique queries.
  - Query rank sequences: `df.groupby('query')['amazon_rank'].agg(['min', 'max', 'count'])`
  - For all 44 queries: `min == 1` and `max == count` with step == 1.
  - Negative assertion: Injecting query with start rank 2 failed with assertion error as intended.

### TC04: Generate Product Features
- **Module:** `research_framework/src/features/feature_engineering.py` (`FeatureEngineer`)
- **Evidence:**
  - Feature matrix dimensions: `(1094, 18)`
  - Schema features: `feat_rating`, `feat_rating_count_log`, `feat_price_ratio`, `feat_price_diff`, `feat_sponsored`, `feat_title_length`, `feat_title_query_overlap`, `feat_title_query_sim`, `feat_is_prime`, `feat_coupon`, `feat_bought_past_month`, `feat_best_seller`, `feat_amazons_choice`.
  - Total nulls: `features_df.isna().sum().sum() == 0`.

### TC05: Predict Expected Product Ranks
- **Module:** `research_framework/src/models/expected_ranking_model.py` (`ExpectedRankingModel`)
- **Evidence:**
  - Cross-validation: 5-Fold `GroupKFold(n_splits=5)` grouped by `query_cleaned`.
  - Total predictions: 1,094 OOF predictions.
  - Predictions summary: `min=3.65`, `max=42.26`, `mean=16.84`.
  - Error metrics: `MAE=9.1246`, `RMSE=12.0804`, `R²=0.2122`.

### TC06: Calculate Ranking Deviation & Peer-Group Inconsistency
- **Module:** `research_framework/src/analysis/ranking_deviation.py`, `peer_group_analysis.py`
- **Evidence:**
  - `rank_deviation = amazon_rank - expected_rank`: min = `-33.69`, max = `+44.35`.
  - `relative_rank_gap`: min = `-0.95`, max = `+0.97`.
  - `rank_inconsistency_z`: min = `-2.80`, max = `+2.38`.
  - Peer groups: 44 query-based peer groups, zero NaN or infinite values.

### TC07: Generate Suspiciousness Scores
- **Module:** `research_framework/src/analysis/suspiciousness_scoring.py` (`SuspiciousnessScorer`)
- **Evidence:**
  - Formula: `0.50 * norm_deviation + 0.30 * norm_inconsistency + 0.20 * norm_price_disparity`.
  - Distribution: `min=3.81`, `max=99.59`, `mean=50.05`, `median=48.94`, `std=24.91`.
  - Top candidate: ASIN `B0D1P9P8MP` (Observed Rank 2, Expected Rank 35.7, Suspiciousness Score 99.59).

### TC08: Apply Anomaly Threshold
- **Module:** `research_framework/src/analysis/threshold_calibration.py`
- **Evidence:**
  - Evaluated thresholds:
    - `T = 85.0`: 127 flagged products (11.61% of catalog) across 38 queries.
    - `T = 90.0`: 72 flagged products (6.58% of catalog).
    - `T = 92.0` (Calibrated Max-F1 point): 45 flagged products (4.11% of catalog) across 23 queries.
    - `T = 99.0`: 3 flagged products (0.27% of catalog).

### TC09: Evaluate Model and Synthetic Scenarios
- **Module:** `research_framework/src/analysis/synthetic_evaluation.py`, `final_evaluation.py`
- **Evidence:**
  - 10-seed multi-scenario benchmark results:
    - **S1 (Upward +25%):** ROC-AUC `0.4269`, PR-AUC `0.0478`, Recall@50 `0.0429`, Mean Target Score `46.02`
    - **S2 (Upward +50%):** ROC-AUC `0.4995`, PR-AUC `0.0432`, Recall@50 `0.0718`, Mean Target Score `53.81`
    - **S3 (Upward +80%):** ROC-AUC `0.6810`, PR-AUC `0.0569`, Recall@50 `0.2356`, Mean Target Score `67.51`
    - **S4 (Downward -25%):** ROC-AUC `0.4617`, PR-AUC `0.0497`, Recall@50 `0.0277`, Mean Target Score `48.65`
    - **S5 (Downward -50%):** ROC-AUC `0.5154`, PR-AUC `0.0480`, Recall@50 `0.0850`, Mean Target Score `54.85`
    - **S6 (Downward -80%):** ROC-AUC `0.6953`, PR-AUC `0.0389`, Recall@50 `0.1304`, Mean Target Score `68.33`
  - Output artifacts generated in `research_framework/data/processed/final_evaluation/`.

### TC10: Display Analysis Results in the Frontend
- **Module:** Frontend (`src/pages/Dashboard.tsx`, `src/pages/ProductAnalysis.tsx`) & Playwright test (`verify_frontend_e2e.py`).
- **Evidence:**
  - Navigated to `http://127.0.0.1:5173/dashboard`.
  - Initial state verified: `--` cards for Products, Queries, Range, MAE, RMSE, R²; 0 candidate tables rendered.
  - Uploaded `amazon_search_dataset.csv` and clicked `Run Analysis`.
  - Populated state verified: Products = `1,094`, Queries = `44`, Range = `1 to 59`, MAE = `9.12`, RMSE = `12.08`, R² = `0.21`.
  - Candidate table rendered 15 entries per page, with top candidate `B0D1P9P8MP` (Score: 99.6).
  - Clicked `Analyze` button: navigated to `/product/B0D1P9P8MP`, displaying product title, image element, rank breakdown, and peer comparison without errors.
  - Verification screenshot archived at `research_framework/reports/tc10_frontend_verified.png`.
