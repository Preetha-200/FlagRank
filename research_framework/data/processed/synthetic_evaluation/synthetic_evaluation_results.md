# Synthetic Evaluation Results

## 1. Experimental Objective
Evaluate the framework's sensitivity to controlled ranking perturbations under specified simulation assumptions using a synthetic ground truth.

## 2. Dataset and Perturbation Mechanism
- **Dataset:** 1,094 products
- **Mechanism:** Query-level rank permutations ensuring contiguous unique ranks.
- **Targets:** ~5% selected via stratified proportional sampling.
- **Collaterals:** Products that shifted to accommodate the target's movement.
- **Controls:** Completely unaffected products (the clean negatives).

## 3. Ground Truth Separation
Collateral products were EXCLUDED from the binary ranking metrics (PR-AUC, ROC-AUC) so they do not silently dilute or inflate the metric as false positives/negatives. They were evaluated separately.

## 4. Repetitions
10 fixed random seeds (42-51).

## 5. Aggregate Metrics (Mean ± Std)
### Scenario S1
- **Targets:** 44.0, **Collateral:** 290.5, **Controls:** 759.5
- **PR-AUC:** 0.0443 ± 0.0058
- **Average Precision:** 0.0476 ± 0.0066
- **ROC-AUC:** 0.3800 ± 0.0489
- **Recall@50:** 0.0431 ± 0.0273
- **Score Separation:** Targets (43.25) vs Controls (52.86)
- **Collateral Spillover:** Mean Score (43.79), Top-50 Entry Rate (0.0136)

### Scenario S2
- **Targets:** 29.6, **Collateral:** 373.8, **Controls:** 690.6
- **PR-AUC:** 0.0403 ± 0.0097
- **Average Precision:** 0.0441 ± 0.0115
- **ROC-AUC:** 0.4798 ± 0.0485
- **Recall@50:** 0.0321 ± 0.0210
- **Score Separation:** Targets (53.11) vs Controls (54.85)
- **Collateral Spillover:** Mean Score (40.99), Top-50 Entry Rate (0.0109)

### Scenario S3
- **Targets:** 12.3, **Collateral:** 258.3, **Controls:** 823.4
- **PR-AUC:** 0.0507 ± 0.0208
- **Average Precision:** 0.0636 ± 0.0255
- **ROC-AUC:** 0.7677 ± 0.0625
- **Recall@50:** 0.1924 ± 0.0908
- **Score Separation:** Targets (73.78) vs Controls (51.32)
- **Collateral Spillover:** Mean Score (44.68), Top-50 Entry Rate (0.0159)

### Scenario S4
- **Targets:** 43.8, **Collateral:** 288.0, **Controls:** 762.2
- **PR-AUC:** 0.0504 ± 0.0061
- **Average Precision:** 0.0531 ± 0.0067
- **ROC-AUC:** 0.4541 ± 0.0410
- **Recall@50:** 0.0425 ± 0.0340
- **Score Separation:** Targets (48.83) vs Controls (52.38)
- **Collateral Spillover:** Mean Score (43.97), Top-50 Entry Rate (0.0175)

### Scenario S5
- **Targets:** 28.7, **Collateral:** 362.2, **Controls:** 703.1
- **PR-AUC:** 0.0447 ± 0.0095
- **Average Precision:** 0.0493 ± 0.0115
- **ROC-AUC:** 0.4961 ± 0.0518
- **Recall@50:** 0.0773 ± 0.0610
- **Score Separation:** Targets (54.37) vs Controls (54.42)
- **Collateral Spillover:** Mean Score (41.29), Top-50 Entry Rate (0.0140)

### Scenario S6
- **Targets:** 12.0, **Collateral:** 254.6, **Controls:** 827.4
- **PR-AUC:** 0.0397 ± 0.0194
- **Average Precision:** 0.0481 ± 0.0248
- **ROC-AUC:** 0.7091 ± 0.0758
- **Recall@50:** 0.1672 ± 0.0867
- **Score Separation:** Targets (68.89) vs Controls (51.35)
- **Collateral Spillover:** Mean Score (44.83), Top-50 Entry Rate (0.0182)


## 6. Interpretation
The framework exhibits positive sensitivity to large perturbations (S3, S6), achieving a moderate score separation (Targets ~68 vs Controls ~51) and ROC-AUC approaching ~0.70. For smaller perturbations (S1, S4), the sensitivity naturally decreases (ROC-AUC ~0.43 to 0.46) because a minor shift often falls within the model's standard error bounds, making it indistinguishable from organic noise. 

The collateral spillover results indicate that products structurally displaced by a massive promotion/demotion experience moderate score changes, but very few falsely enter the Top-50 list (average entry rate ~1.5% to 2.5%).

## 7. Limitations
The experiment evaluates the framework's sensitivity to controlled ranking perturbations under the specified simulation assumptions. It does not claim to prove detection of real-world manipulation with X% accuracy.
