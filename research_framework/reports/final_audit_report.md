# Final Audit Report: Search Ranking Manipulation Detection

## A. VERIFIED AND COMPLETE
* **Dataset:** Correctly established at 1,094 rows across 44 queries with ranks bounding 1–59.
* **Feature Engineering:** 13 deterministic predictive features (`feat_*`) were cleanly isolated. Defensive checks explicitly crash execution if target-leakage fields (`amazon_rank`, `is_amazon_top6`, etc.) enter the predictive matrix.
* **Expected-Rank Model:** Properly implemented a Random Forest Regressor trained under a strict 5-Fold GroupKFold methodology (grouped by query) guaranteeing exactly one unbiased OOF prediction per product. Validation metrics (MAE 9.12, RMSE 12.08, R² 0.21) match the output.
* **Peer-Group Analysis:** Correctly executed within query environments. Edge cases like zero variance (query standard deviation = 0) are handled gracefully (defaulting z-score to 0.0). The directionality of rank deviation (negative = better than expected) is mathematically sound and correctly interpreted.
* **Suspiciousness Score:** The 50/30/20 empirical weighting is mathematically bounded [0, 100] using percentile normalization. It correctly maintains the stance of measuring *relative structural inconsistency*, completely stripped of probabilistic or causal claims.
* **Synthetic Evaluation:** Evaluated S1-S6 adequately. Methodologically strong isolation: collateral products (innocent bystanders shifted by synthetic targets) are explicitly removed from the clean `(targets + controls)` binary classification metrics (PR-AUC, ROC-AUC) so they don't skew the results.

## B. ISSUES FOUND
* **Artifact Consistency (Frontend Typo):** The frontend application (`src/pages/ResearchEvaluation.tsx`) currently displays the Internal OOF Spearman Correlation as **0.4497**. However, the `framework_validation_report.md` and the raw data output correctly identify the Spearman correlation as **0.4447**. This is a minor copy-paste typo in the UI.

## C. METHODOLOGICAL CAVEATS
The following are not bugs, but inherent structural limitations that must simply remain well-documented in the final research release:
1. **Self-Inclusion:** Peer-group normalization (calculating the query mean/std) includes the target product itself. This slightly dilutes the Z-score for extreme anomalies compared to a rigorous leave-one-out standardisation.
2. **List-wise Calibration:** The Random Forest acts as an absolute regressor; it does not perfectly calibrate list-wise integer ranks natively, which the downstream percentile-gap normalizations handle.
3. **Synthetic Limitations:** Good sensitivity to synthetic block permutations does not mathematically guarantee precision against sophisticated, multivariate real-world adversarial fraud.
4. **Varying Baselines:** Large synthetic permutations restrict target eligibility, dropping target prevalence to ~1.5%. Consequently, PR-AUC random baselines vary dramatically between scenarios.
5. **Score Weightings:** The 50/30/20 weights are an empirical design choice, not mathematically learned/optimal parameters.

## D. CLAIMS THAT MUST BE REWORDED
**Zero issues found.** 
A comprehensive audit of the backend, reports, and frontend confirms the complete absence of inappropriate claims. The framework successfully avoids "manipulation probability," "confidence," "fraud," and "causal proof". It explicitly disclaims real-world manipulation detection. 

## E. REQUIRED CORRECTIONS BEFORE FINALIZATION
1. Update `src/pages/ResearchEvaluation.tsx` to display `0.4447` for the Spearman correlation instead of `0.4497`.

## F. SAFE TO PROCEED WITH FINAL RESEARCH DOCUMENTATION: YES
The research framework is highly robust, tightly bound to observable evidence, and scientifically cautious. The data flow from preprocessing to synthetic evaluation is internally consistent. Once the single minor UI typo is corrected, the project is completely ready for final documentation.
