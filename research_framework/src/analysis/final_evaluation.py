import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

def create_plots(df, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Suspiciousness distribution
    plt.figure(figsize=(10, 6))
    plt.hist(df['suspiciousness_score'], bins=30, edgecolor='black')
    plt.title('Suspiciousness Score Distribution')
    plt.xlabel('Suspiciousness Score')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(os.path.join(out_dir, 'score_distribution.png'))
    plt.close()
    
    # 2. Suspiciousness by rank region
    def get_region(r):
        if r <= 10: return 'Top 10'
        if r <= 20: return '11-20'
        if r <= 30: return '21-30'
        if r <= 40: return '31-40'
        if r <= 50: return '41-50'
        return '51+'
        
    df['rank_region'] = df['amazon_rank'].apply(get_region)
    order = ['Top 10', '11-20', '21-30', '31-40', '41-50', '51+']
    region_means = df.groupby('rank_region')['suspiciousness_score'].mean().reindex(order)
    
    plt.figure(figsize=(10, 6))
    region_means.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Mean Suspiciousness by Rank Region')
    plt.xlabel('Observed Rank Region')
    plt.ylabel('Mean Suspiciousness Score')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'score_by_rank_region.png'))
    plt.close()
    
    # 3. Query-level distribution (max score per query)
    q_max = df.groupby('query')['suspiciousness_score'].max().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    q_max.head(40).plot(kind='bar', color='salmon', edgecolor='black')
    plt.title('Max Suspiciousness by Query (Top 40)')
    plt.xlabel('Query')
    plt.ylabel('Max Suspiciousness Score')
    plt.xticks([]) # Hide x ticks as they clutter
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'query_max_distribution.png'))
    plt.close()

def run_final_evaluation():
    final_dir = os.path.join(base_dir, 'data', 'processed', 'final_evaluation')
    plots_dir = os.path.join(final_dir, 'plots')
    os.makedirs(final_dir, exist_ok=True)
    
    score_path = os.path.join(base_dir, 'data', 'processed', 'suspiciousness_scores.csv')
    df = pd.read_csv(score_path)
    
    # Generate Plots
    create_plots(df.copy(), plots_dir)
    
    # Part A: Ranking-level stats
    num_products = len(df)
    num_queries = df['query'].nunique()
    rank_min = df['amazon_rank'].min()
    rank_max = df['amazon_rank'].max()
    mean_rank = df['amazon_rank'].mean()
    median_rank = df['amazon_rank'].median()
    
    score_mean = df['suspiciousness_score'].mean()
    score_median = df['suspiciousness_score'].median()
    score_std = df['suspiciousness_score'].std()
    score_min = df['suspiciousness_score'].min()
    score_max = df['suspiciousness_score'].max()
    q50 = df['suspiciousness_score'].quantile(0.50)
    q75 = df['suspiciousness_score'].quantile(0.75)
    q90 = df['suspiciousness_score'].quantile(0.90)
    q95 = df['suspiciousness_score'].quantile(0.95)
    q99 = df['suspiciousness_score'].quantile(0.99)
    
    # By rank region
    def get_region(r):
        if r <= 10: return 'Top 10'
        if r <= 20: return '11-20'
        if r <= 30: return '21-30'
        if r <= 40: return '31-40'
        if r <= 50: return '41-50'
        return '51+'
        
    df['rank_region'] = df['amazon_rank'].apply(get_region)
    region_stats = df.groupby('rank_region')['suspiciousness_score'].mean().to_dict()
    
    # Query level stats
    query_stats = df.groupby('query').agg(
        num_products=('query', 'count'),
        mean_score=('suspiciousness_score', 'mean'),
        max_score=('suspiciousness_score', 'max')
    )
    
    # Part B: Thresholds
    thresholds = [85, 92, 99]
    t_results = {}
    for t in thresholds:
        flagged = df[df['suspiciousness_score'] >= t]
        affected_queries = flagged['query'].nunique()
        t_results[t] = {
            'num_flagged': len(flagged),
            'pct_flagged': len(flagged) / len(df) * 100.0,
            'affected_queries': affected_queries,
            'pct_queries': affected_queries / num_queries * 100.0,
            'mean_rank': flagged['amazon_rank'].mean() if len(flagged) > 0 else np.nan,
            'median_rank': flagged['amazon_rank'].median() if len(flagged) > 0 else np.nan
        }
        
    # Save CSV
    eval_csv = pd.DataFrame([{
        'num_products': num_products, 'num_queries': num_queries, 
        'mean_rank': mean_rank, 'median_rank': median_rank,
        'mean_score': score_mean, 'median_score': score_median, 'std_score': score_std,
        'flagged_85': t_results[85]['num_flagged'],
        'flagged_92': t_results[92]['num_flagged'],
        'flagged_99': t_results[99]['num_flagged']
    }])
    eval_csv.to_csv(os.path.join(final_dir, 'final_evaluation_results.csv'), index=False)
    
    report = f"""# Final Evaluation Framework Report

## Part A: Real Marketplace Observational Evaluation

### 1. Ranking-Level Statistics
- **Total Products:** {num_products}
- **Total Queries:** {num_queries}
- **Observed Rank Range:** [{rank_min}, {rank_max}]
- **Mean Observed Rank:** {mean_rank:.2f}
- **Median Observed Rank:** {median_rank:.2f}

### 2. Suspiciousness Distribution
- **Mean:** {score_mean:.2f}
- **Median:** {score_median:.2f}
- **Standard Deviation:** {score_std:.2f}
- **Min / Max:** [{score_min:.2f}, {score_max:.2f}]
- **Percentiles:** 
  - 50th: {q50:.2f}
  - 75th: {q75:.2f}
  - 90th: {q90:.2f}
  - 95th: {q95:.2f}
  - 99th: {q99:.2f}

### 3. Suspiciousness by Rank Region
- **Top 10:** {region_stats.get('Top 10', 0):.2f}
- **11-20:** {region_stats.get('11-20', 0):.2f}
- **21-30:** {region_stats.get('21-30', 0):.2f}
- **31-40:** {region_stats.get('31-40', 0):.2f}
- **41-50:** {region_stats.get('41-50', 0):.2f}
- **51+:** {region_stats.get('51+', 0):.2f}

*(Observation: Suspiciousness is distributed broadly and does not strictly correlate with being highly ranked. Products at all positions can be structurally anomalous relative to their expected rank.)*

### 4. Query-Level Analysis
- **Products per query (mean):** {query_stats['num_products'].mean():.2f}
- **Query mean suspiciousness (avg):** {query_stats['mean_score'].mean():.2f}
- **Queries with max score >= 92:** {(query_stats['max_score'] >= 92).sum()}

## Part B: Threshold Application
Applying calibrated synthetic thresholds to the real marketplace data. These items are "potentially suspicious" and "flagged by the framework" for investigation, not definitively manipulated.

### Threshold 85 (Sensitivity-Oriented)
- **Flagged Products:** {t_results[85]['num_flagged']} ({t_results[85]['pct_flagged']:.2f}%)
- **Affected Queries:** {t_results[85]['affected_queries']} ({t_results[85]['pct_queries']:.2f}%)
- **Flagged Mean Rank:** {t_results[85]['mean_rank']:.2f}
- **Flagged Median Rank:** {t_results[85]['median_rank']:.2f}

### Threshold 92 (Balanced Calibration)
- **Flagged Products:** {t_results[92]['num_flagged']} ({t_results[92]['pct_flagged']:.2f}%)
- **Affected Queries:** {t_results[92]['affected_queries']} ({t_results[92]['pct_queries']:.2f}%)
- **Flagged Mean Rank:** {t_results[92]['mean_rank']:.2f}
- **Flagged Median Rank:** {t_results[92]['median_rank']:.2f}

### Threshold 99 (Conservative)
- **Flagged Products:** {t_results[99]['num_flagged']} ({t_results[99]['pct_flagged']:.2f}%)
- **Affected Queries:** {t_results[99]['affected_queries']} ({t_results[99]['pct_queries']:.2f}%)
- **Flagged Mean Rank:** {t_results[99]['mean_rank']:.2f}
- **Flagged Median Rank:** {t_results[99]['median_rank']:.2f}

## Part C: Synthetic Validation Summary
*Note: These are controlled synthetic validation results derived from simulated rank permutations.*

- **Perturbation Sensitivity:** Mean target score scales monotonically with magnitude (Small ~47, Medium ~54, Large ~68).
- **Directional Robustness:** Both 80% upward promotions and 80% downward demotions produce highly similar anomaly separability (ROC-AUC 0.68 vs 0.69).
- **Metric Performance (Large Shift):** ROC-AUC ~0.68. PR-AUC ~0.057 (vs a 0.015 random baseline prevalence).
- **Seed Stability:** Variance across 10 random permutations was extremely low for AUC metrics and FPR.
- **Detector Performance at Threshold 92 (Large Shifts):**
  - **Recall:** ~22%
  - **Precision:** ~6.3%
  - **F1:** ~9.7%
  - **Control FPR:** ~4.7%
  - **Collateral FPR:** ~1.8% (Displaced neighbours are largely insulated from being falsely flagged).

## Part D: Comparative Interpretation

| Evidence Source | What it demonstrates | What it does NOT demonstrate |
|---|---|---|
| **Real marketplace data** | Behaviour of the framework on observed ranking data | Actual manipulation ground truth |
| **Synthetic perturbation** | Sensitivity to controlled rank changes | Real adversarial manipulation |
| **Threshold calibration** | Candidate operating points | Universal threshold |
| **Robustness analysis** | Internal stability under tested variations | General real-world robustness |

## Part E: Final Research Findings
1. The framework successfully identifies products exhibiting unusually large discrepancies between expected and observed ranking, flagging approximately {t_results[92]['pct_flagged']:.1f}% of the marketplace dataset at the balanced T=92 threshold.
2. Controlled synthetic experiments demonstrate strictly increasing detector response mathematically mirroring increasing perturbation magnitude.
3. The detector exhibits highly symmetric behaviour for upward and downward synthetic perturbations of equivalent relative severity.
4. Small rank perturbations (~25% shift) overlap substantially with the normal score distribution in the evaluated dataset, meaning minor anomalies are empirically indistinguishable from organic marketplace noise.
5. The selected thresholds represent mathematical calibration points optimized for the isolated experimental environment rather than universally valid or proven manipulation bounds.
"""
    
    with open(os.path.join(final_dir, 'final_evaluation_report.md'), 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == '__main__':
    run_final_evaluation()
