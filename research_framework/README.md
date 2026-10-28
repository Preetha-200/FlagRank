# Platform-Independent E-Commerce Ranking Anomaly Detector

## Research Objective
This research project aims to develop a platform-independent framework for identifying potentially unexplained e-commerce ranking behaviour using observable marketplace signals.

## Platform-Independent Framework
The system relies exclusively on publicly observable signals (such as price, ratings, review velocity, etc.) and does not attempt to reverse-engineer proprietary algorithms. This makes the framework theoretically applicable to any e-commerce marketplace.

## Amazon Dataset Role
While the framework is platform-independent, we utilize the Amazon Search Dataset as our primary experimental dataset and case study to validate the approach through empirical evaluation and controlled synthetic simulation.

## Implemented Research Pipeline
1. **Data Ingestion & Preprocessing**: Cleans zero-variance columns, imputes missing price values using median baselines, and validates query continuous ranks.
2. **Observable Signal Feature Engineering**: Extracts 13 numerical, boolean, text, and frequency-encoded features while blocking search outcome variables to prevent leakage.
3. **Expected-Ranking Baseline Modeling**: Trains a Random Forest Regressor using isolated 5-fold GroupKFold Out-of-Fold (OOF) cross-validation grouped by search query.
4. **Ranking Deviation Calculation**: Computes raw displacement between observed rank and OOF expected rank ($\Delta_{\text{rank}} = R_{\text{obs}} - R_{\text{exp}}$).
5. **Peer-Group Inconsistency Analysis**: Standardizes ranking deviations relative to competing query cohorts via query-level $Z$-scores and relative percentile displacement gaps.
6. **Continuous Suspiciousness Scoring**: Produces an empirical 0–100 ranking-inconsistency measure using robust percentile-based CDF normalization ($50\%$ standardized inconsistency $Z$-score, $30\%$ relative percentile rank gap, $20\%$ absolute rank deviation).
7. **Threshold Calibration & Flagging**: Evaluates candidate isolation across top-percentile cutoffs to identify prominent anomalies.
8. **Synthetic Perturbation Evaluation**: Validates detector sensitivity through controlled synthetic rank displacement simulations ($\delta \in \{5, 10, 20\}$) across multiple random seeds.
9. **Interactive Visualisation**: Explores query distributions, model accuracy, candidate tables, and product-level peer comparisons.

## Proposed Future Work
The following capabilities represent valuable research extensions beyond the current baseline implementation:
- **Localized Feature Attribution (SHAP / TreeExplainer)**: Decomposing expected-ranking predictions into individual feature contributions for localized audit reports.
- **Dynamic Marketplace Ingestion**: Streaming API connectors for real-time temporal ranking trajectory tracking.

## Important Disclaimer & Methodological Boundary
This system calculates a **dataset-relative Suspiciousness Score**, which is an empirical measure of ranking inconsistency compared to an observable baseline. 

- A high score indicates that a product's observed ranking is difficult to explain from its observable marketplace attributes alone relative to its peer group.
- It is **NOT** a probability, confidence interval, or definitive proof of fraudulent manipulation or algorithmic abuse.
- Correlation or ranking inconsistency does not establish causation.
