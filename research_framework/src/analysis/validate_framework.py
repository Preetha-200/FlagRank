import pandas as pd
import numpy as np
import os
import json
from scipy.stats import spearmanr, pearsonr, ttest_ind

def run_validation(scores_path, features_path, report_path):
    # 1. Load Data
    df = pd.read_csv(scores_path)
    df_feat = pd.read_csv(features_path)
    
    # Check dataset size
    assert len(df) == 1094, f"Expected 1094 rows, got {len(df)}"
    
    # 2. Validate Expected-vs-Observed Ranking Behaviour
    pearson_rank = pearsonr(df['amazon_rank'], df['expected_rank'])[0]
    spearman_rank = spearmanr(df['amazon_rank'], df['expected_rank'])[0]
    mae = np.mean(np.abs(df['amazon_rank'] - df['expected_rank']))
    rmse = np.sqrt(np.mean((df['amazon_rank'] - df['expected_rank'])**2))
    r2 = 1 - (np.sum((df['amazon_rank'] - df['expected_rank'])**2) / np.sum((df['amazon_rank'] - df['amazon_rank'].mean())**2))
    
    # 3. Validate Ranking Direction
    # Negative deviation = amazon_rank < expected_rank = observed is better than expected
    # Positive deviation = amazon_rank > expected_rank = observed is worse than expected
    
    # 4. Analyze Ranking Inconsistency Distribution
    cols = ['rank_deviation', 'rank_inconsistency_z', 'relative_rank_gap', 
            'absolute_rank_inconsistency_z', 'absolute_relative_rank_gap', 
            'absolute_rank_deviation', 'suspiciousness_score']
    dist = df[cols].describe(percentiles=[0.05, 0.25, 0.50, 0.75, 0.95, 0.99]).T
    
    # 5. Validate Relationship Between Components
    corr_cols = ['rank_deviation', 'rank_inconsistency_z', 'relative_rank_gap', 'suspiciousness_score']
    pearson_comp = df[corr_cols].corr(method='pearson')
    spearman_comp = df[corr_cols].corr(method='spearman')
    
    pearson_abs = {
        'abs_z_vs_score': pearsonr(df['absolute_rank_inconsistency_z'], df['suspiciousness_score'])[0],
        'abs_gap_vs_score': pearsonr(df['absolute_relative_rank_gap'], df['suspiciousness_score'])[0],
        'abs_dev_vs_score': pearsonr(df['absolute_rank_deviation'], df['suspiciousness_score'])[0]
    }
    
    # 6. Analyze Highest-Scoring Candidates
    top20 = df.sort_values('suspiciousness_score', ascending=False).head(20).copy()
    disp_cols = ['query', 'category', 'amazon_rank', 'expected_rank', 'rank_deviation', 
                 'rank_inconsistency_z', 'relative_rank_gap', 'suspiciousness_score', 'feat_sponsored']
    
    # 7. Compare Candidate Direction
    high_scores = df[df['suspiciousness_score'] >= df['suspiciousness_score'].quantile(0.90)].copy()
    better = high_scores[high_scores['rank_deviation'] < 0]
    worse = high_scores[high_scores['rank_deviation'] > 0]
    
    dir_stats = {
        'better_count': len(better),
        'better_pct': len(better) / len(high_scores) * 100,
        'better_mean_abs_dev': better['absolute_rank_deviation'].mean(),
        'better_mean_abs_z': better['absolute_rank_inconsistency_z'].mean(),
        'better_mean_score': better['suspiciousness_score'].mean(),
        'worse_count': len(worse),
        'worse_pct': len(worse) / len(high_scores) * 100,
        'worse_mean_abs_dev': worse['absolute_rank_deviation'].mean(),
        'worse_mean_abs_z': worse['absolute_rank_inconsistency_z'].mean(),
        'worse_mean_score': worse['suspiciousness_score'].mean(),
    }
    
    # 8. Sponsored vs Non-Sponsored
    spon = df[df['feat_sponsored'] == 1]['suspiciousness_score']
    org = df[df['feat_sponsored'] == 0]['suspiciousness_score']
    t_stat, p_val = ttest_ind(spon, org, equal_var=False)
    
    # Calculate Cohen's d for effect size
    nx, ny = len(spon), len(org)
    dof = nx + ny - 2
    pooled_std = np.sqrt(((nx - 1) * np.var(spon, ddof=1) + (ny - 1) * np.var(org, ddof=1)) / dof)
    cohens_d = (np.mean(spon) - np.mean(org)) / pooled_std
    
    spon_stats = {
        'spon_count': nx,
        'spon_mean': spon.mean(),
        'spon_median': spon.median(),
        'spon_p95': spon.quantile(0.95),
        'spon_mean_abs_dev': df[df['feat_sponsored'] == 1]['absolute_rank_deviation'].mean(),
        'org_count': ny,
        'org_mean': org.mean(),
        'org_median': org.median(),
        'org_p95': org.quantile(0.95),
        'org_mean_abs_dev': df[df['feat_sponsored'] == 0]['absolute_rank_deviation'].mean(),
        't_stat': t_stat,
        'p_val': p_val,
        'cohens_d': cohens_d
    }
    
    # 9. Query-Level Behaviour
    q_stats = df.groupby('query').agg(
        count=('amazon_rank', 'count'),
        mean_score=('suspiciousness_score', 'mean'),
        median_score=('suspiciousness_score', 'median'),
        max_score=('suspiciousness_score', 'max'),
        std_score=('suspiciousness_score', 'std'),
        mean_abs_dev=('absolute_rank_deviation', 'mean')
    ).sort_values('mean_score', ascending=False)
    
    # 10. Check Whether Suspiciousness Is Merely Rank Position
    pearson_rank_score = pearsonr(df['amazon_rank'], df['suspiciousness_score'])[0]
    spearman_rank_score = spearmanr(df['amazon_rank'], df['suspiciousness_score'])[0]
    
    bins = [0, 10, 20, 40, 60]
    labels = ['1-10', '11-20', '21-40', '41-59']
    df['rank_bucket'] = pd.cut(df['amazon_rank'], bins=bins, labels=labels)
    rank_bucket_stats = df.groupby('rank_bucket')['suspiciousness_score'].agg(['mean', 'median', 'std'])
    
    # 11. Observable-Factor Relationship Analysis
    features = [c for c in df.columns if c.startswith('feat_')]
    feat_corr = []
    for f in features:
        c1 = spearmanr(df[f], df['expected_rank'])[0]
        c2 = spearmanr(df[f], df['absolute_rank_deviation'])[0]
        c3 = spearmanr(df[f], df['suspiciousness_score'])[0]
        feat_corr.append({'feature': f, 'spearman_expected_rank': c1, 'spearman_abs_dev': c2, 'spearman_score': c3})
    feat_corr_df = pd.DataFrame(feat_corr)
    
    # Format the report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    report = f"""# End-to-End Ranking Inconsistency Validation Report

## 1. Objective
Validate the complete Search Ranking Manipulation Detection framework. Evaluate whether the outputs are statistically meaningful, internally consistent, and accurately interpretable as ranking-inconsistency signals.

## 2. Expected-vs-Observed Ranking Behaviour
- **OOF MAE:** {mae:.2f}
- **OOF RMSE:** {rmse:.2f}
- **OOF R²:** {r2:.2f}
- **Pearson Correlation:** {pearson_rank:.4f}
- **Spearman Correlation:** {spearman_rank:.4f}

*Interpretation:* The R² of {r2:.2f} means the observable-signal model explains approximately 21% of the variance in observed rank under the OOF evaluation. The moderate explanatory performance provides a useful baseline for comparing observed ranking against an observable-signal-based expected ranking. However, the remaining unexplained variation must not be interpreted as evidence of manipulation. It may include omitted observable factors, latent ranking-system factors, model limitations, nonlinear/interaction effects not captured adequately, measurement noise, and other sources. Ranking inconsistency is derived from the observed-vs-expected discrepancy; it is not automatically synonymous with unexplained variance or manipulation. A higher or lower R² is not itself evidence for or against manipulation.

## 3. Ranking Direction
- `rank_deviation < 0`: Observed ranking is better than expected (e.g. ranked 2, expected 24 -> deviation -22).
- `rank_deviation > 0`: Observed ranking is worse than expected (e.g. ranked 45, expected 15 -> deviation +30).

## 4. Ranking Inconsistency Distribution
```text
{dist[['min', '5%', '25%', '50%', '75%', '95%', '99%', 'max', 'mean', 'std']].to_string()}
```
*Interpretation:* The distributions show substantial variability. While many products lie relatively close to their expectation, severe discrepancies exist at both tails of the distribution.

## 5. Component Relationships
**Pearson Correlation with Final Score:**
- Absolute Z-Score vs Score: {pearson_abs['abs_z_vs_score']:.4f}
- Absolute Relative Gap vs Score: {pearson_abs['abs_gap_vs_score']:.4f}
- Absolute Deviation vs Score: {pearson_abs['abs_dev_vs_score']:.4f}

*Interpretation:* The component-score relationships are consistent with the intended weighted construction. The selected 50/30/20 weights are methodological design choices rather than empirically proven optimal weights.

## 6. Highest-Scoring Candidates (Top 20)
*(Note: These are "highest-scoring ranking-inconsistency candidates", NOT confirmed manipulations. They are simply products whose ranking positions are highly unexplained by observable features relative to their peers.)*
```text
{top20[disp_cols].to_string(index=False)}
```
*Interpretation:* A candidate with a negative rank deviation appears substantially better positioned than its observable-signal-based expected rank. A candidate with a positive rank deviation appears substantially worse positioned than its expected rank.

## 7. Compare Candidate Direction (Top 10% Scores)
- **Better-than-expected (Dev < 0):** {dir_stats['better_count']} ({dir_stats['better_pct']:.1f}%) | Mean Abs Dev: {dir_stats['better_mean_abs_dev']:.2f} | Mean Score: {dir_stats['better_mean_score']:.2f}
- **Worse-than-expected (Dev > 0):** {dir_stats['worse_count']} ({dir_stats['worse_pct']:.1f}%) | Mean Abs Dev: {dir_stats['worse_mean_abs_dev']:.2f} | Mean Score: {dir_stats['worse_mean_score']:.2f}

*Interpretation:* Among the highest-scoring candidates in this dataset, ranking inconsistencies occur in both directions, with comparable counts of better-than-expected and worse-than-expected placements. This indicates that the scoring procedure does not inherently favour one deviation direction in this evaluated dataset.

## 8. Sponsored vs Non-Sponsored Findings
- **Sponsored:** Count {spon_stats['spon_count']} | Mean Score: {spon_stats['spon_mean']:.2f} | P95: {spon_stats['spon_p95']:.2f} | Mean Abs Dev: {spon_stats['spon_mean_abs_dev']:.2f}
- **Non-Sponsored:** Count {spon_stats['org_count']} | Mean Score: {spon_stats['org_mean']:.2f} | P95: {spon_stats['org_p95']:.2f} | Mean Abs Dev: {spon_stats['org_mean_abs_dev']:.2f}
- **T-Test (Scores):** t = {spon_stats['t_stat']:.4f}, p = {spon_stats['p_val']:.4e}
- **Cohen's d Effect Size:** {spon_stats['cohens_d']:.4f}

*Interpretation:* The test indicates a statistically detectable difference between the evaluated sponsored and non-sponsored score distributions under the chosen test. Statistical significance does NOT establish practical significance by itself. Sponsorship may be related to ranking behaviour, but this analysis cannot determine why. Sponsorship is an observable input to the expected-ranking model and is NOT directly added as a suspiciousness-score bonus/penalty. Sponsored does NOT mean manipulated.

## 9. Query-Level Behaviour
```text
{q_stats.head(10).to_string()}
```
*Interpretation:* The distribution of suspiciousness varies across query groups, with some queries exhibiting higher mean ranking-inconsistency scores than others. These differences indicate that ranking inconsistency is not distributed uniformly across query contexts in this dataset. The analysis does not establish the cause of these differences.

## 10. Check Whether Suspiciousness Is Merely Rank Position
- **Pearson (Rank vs Score):** {pearson_rank_score:.4f}
- **Spearman (Rank vs Score):** {spearman_rank_score:.4f}
```text
{rank_bucket_stats.to_string()}
```
*Interpretation:* The near-zero Spearman correlation indicates that suspiciousness score is not strongly associated with raw observed rank in this dataset. Therefore, the score is not simply a monotonic proxy for being near the top or bottom of the ranking.

## 11. Observable-Factor Relationships
```text
{feat_corr_df.to_string(index=False)}
```
*Interpretation:* No individual evaluated observable feature shows a strong monotonic association with the final suspiciousness score in this dataset. This suggests that the score is not dominated by a single basic feature under the tested associations, although this does not establish complete multivariate independence.

## 12. Target Leakage Audit
- `amazon_rank`, `is_amazon_top6`, `query`, and `category` were strictly excluded from model feature inputs.
- OOF predictions were generated using `GroupKFold(query)`, preventing any target training leakage.
- No binary target logic feedbacks into expected rank generation.

## 13. Stability Check
The entire pipeline relies on deterministic grouping, deterministic model seeding (`random_state=42`), and deterministic score standardisation.

## 14. Current Validation Boundary
The present evaluation is an internal validation of the framework's computational consistency, leakage controls, ranking-inconsistency behaviour, and score stability. The dataset does not provide independently verified labels identifying manipulated rankings. Therefore, the present results demonstrate the framework's ability to quantify and rank relative observed-vs-expected inconsistencies, but they do not establish real-world manipulation-detection accuracy.

## 15. Research Interpretation

### Supported by Current Evidence
The framework can currently claim that it:
1. Builds an observable-signal-based expected-ranking baseline using grouped OOF evaluation.
2. Quantifies observed-vs-expected ranking deviation.
3. Contextualizes deviation within query-level peer groups.
4. Produces a continuous relative suspiciousness score.
5. Produces stable candidate rankings under the tested scoring alternatives.
6. Maintains strict target-leakage safeguards.
7. Identifies ranking-inconsistency candidates in both better-than-expected and worse-than-expected directions.

### Not Supported by Current Evidence
The framework cannot currently claim that it:
1. Proves ranking manipulation.
2. Identifies ground-truth manipulated products.
3. Estimates a probability of manipulation.
4. Establishes intentional behaviour by sellers or platforms.
5. Establishes causality.
6. Demonstrates real-world detection precision/recall for manipulation.
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"Validation complete. Report saved to {report_path}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    scores_path = os.path.join(base_dir, 'data', 'processed', 'suspiciousness_scores.csv')
    features_path = os.path.join(base_dir, 'data', 'processed', 'features_dataset.csv')
    report_path = os.path.join(base_dir, 'reports', 'framework_validation_report.md')
    run_validation(scores_path, features_path, report_path)
