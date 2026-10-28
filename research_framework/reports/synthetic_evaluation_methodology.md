# Controlled Synthetic Manipulation Evaluation Methodology

## 1. Evaluation Objective
The objective of this controlled synthetic evaluation is to scientifically determine whether the Search Ranking Manipulation Detection framework can detect ranking perturbations when the locations and magnitudes of those perturbations are known as ground truth. 

Because the real-world dataset lacks independently verified labels identifying manipulated search rankings, the synthetic experiment creates a controlled ground truth. This evaluates the framework's sensitivity to structural ranking inconsistencies, but does not establish real-world manipulation detection accuracy.

## 2. Target, Collateral, and Control States
When a product's rank is synthetically moved (e.g., Rank 35 to Rank 5), the intermediate products (Ranks 5–34) must shift to accommodate the unique, contiguous ranking structure. These products must be strictly distinguished. 

Every product in the evaluation dataset will be classified into exactly one of three mutually exclusive states:

- **A. Direct synthetic positive (`synthetic_target = 1`):** The product intentionally selected as the perturbation target.
- **B. Collateral displacement (`synthetic_collateral = 1`):** A product whose rank changed only because another product was moved.
- **C. Unaffected control (`synthetic_control = 1`):** A product whose observed rank remains completely unchanged.

## 3. Dataset Basis & Leakage Safeguards
The experiment will be conducted using the processed dataset (1,094 rows) preserving all original observable product attributes.
- The expected-ranking model predictions (OOF) remain completely unchanged.
- The original ranking (`amazon_rank`) will be retained in a separate reference field `original_amazon_rank`.
- The evaluation input will be `synthetic_amazon_rank`.
- Target selection must be entirely independent of expected rank, original observed-vs-expected deviation, or the original suspiciousness score.
- The `is_amazon_top6` field is isolated and not used as a manipulation label.

## 4. Perturbation Mechanism (Query-Level Rank Permutation)
Products will NOT have their rank changed independently. Instead, the simulation will perform a **ranking permutation** within the same query group, preserving rank uniqueness, valid bounds, and preventing cross-query contamination.

## 5. Eligibility Rules and Perturbation Magnitudes
Because query group sizes range from 4 to 59, perturbations will be defined using magnitudes proportional to the specific query's rank spread.
- **Small (~25% of query spread)**
- **Medium (~50% of query spread)**
- **Large (~80% of query spread)**

**Eligibility Rules:**
- A product is only eligible for a specific perturbation scenario if its target destination rank remains within the query's existing min/max rank bounds.
- If a query is too small to accommodate a specific magnitude shift (e.g., an 80% shift in a 4-item query might equal a 25% shift due to integer rounding, creating collisions or identical experiments), that scenario is marked infeasible for that specific target.
- No duplicate target selection within the same query during a single repetition unless explicitly justified by exhaustion of candidates.

## 6. Target Selection Strategy
Approximately 5% of products will be selected as direct synthetic targets (`synthetic_target = 1`).
- Selection will use **stratified proportional sampling** by query group to ensure perturbations are distributed across different search contexts. 
- Forcing a perfectly equal sponsored/non-sponsored split is unnecessary and could introduce selection bias; proportional sampling naturally represents the dataset's composition.
- The selection is fully deterministic via random seeding and remains completely blind to the detector's outputs.

## 7. Collateral Displacement Treatment
Collateral products are NOT automatically counted as false positives, nor are they discarded. Because their ranks were structurally altered, they are expected to have altered suspiciousness scores. 

We will evaluate them separately by reporting:
- Mean suspiciousness score of direct targets vs collateral products vs unaffected controls.
- Proportion of collateral products vs direct targets entering the Top-K candidates list.

## 8. Defining the Clean Negative Control
For computing hard binary detection metrics, the clean negative control population will consist ONLY of the **unaffected controls** (`synthetic_control = 1`). 
- Direct targets = Positives
- Unaffected products = Clean Negatives
- Collateral products = Excluded from the binary confusion matrix to prevent muddying the False Positive Rate (FPR).

## 9. Simulation Repetitions
To ensure robustness, the evaluation will run **10 distinct simulation repetitions** using fixed random seeds (`42–51`). 
The final evaluation metrics will be reported as:
- Mean
- Standard Deviation
- Minimum
- Maximum
across the 10 runs.

## 10. Evaluation Metrics
The framework outputs a continuous score. Threshold calibration is postponed to a future stage and will not be cherry-picked.

**Primary Metrics (Ranking Quality):**
- **PR-AUC (Primary):** Highly appropriate for imbalanced classes (5% targets).
- **Average Precision (AP):** Summarizes the PR curve.
- **ROC-AUC (Secondary):** Evaluates overall ranking but can be overly optimistic on imbalanced data.

**Secondary Metrics (Post-Thresholding / Top-K):**
- Precision@K and Recall@K (e.g., Top 10%, Top 20%)
- Precision, Recall, F1, and FPR (only computable once a threshold methodology is independently justified).

## 11. Detection Lead Time Limitation
The current real dataset is a static snapshot, not a longitudinal time-series ranking dataset. Therefore, **detection lead time** cannot be meaningfully calculated in this synthetic evaluation. Do not invent temporal information. This metric is explicitly marked as: *Not applicable to the current synthetic static-ranking evaluation.*

## 12. Experiment Matrix
We evaluate both upward promotion (better-than-expected) and downward demotion (worse-than-expected).

| Scenario | Direction | Magnitude | Purpose |
|----------|-----------|-----------|---------|
| S1 | Upward | Small (~25%) | Sensitivity to minor promotions |
| S2 | Upward | Medium (~50%) | Detection of standard promotions |
| S3 | Upward | Large (~80%) | Detection of aggressive promotions |
| S4 | Downward | Small (~25%) | Sensitivity to minor demotions |
| S5 | Downward | Medium (~50%) | Detection of standard demotions |
| S6 | Downward | Large (~80%) | Detection of aggressive demotions |

## 13. Synthetic vs Real-World Validity Boundary
This evaluation is fundamentally limited by its synthetic nature. 
- **It CAN establish:** "The framework successfully detects and ranks controlled ranking perturbations under the tested simulation assumptions."
- **It CANNOT establish:** "The framework detects real-world manipulation with X% accuracy." 

Real-world manipulation involves complex, often subtle, multi-variate tactics that simple rank-shifting may not perfectly emulate. This limitation bounds all future interpretations of the evaluation metrics.
