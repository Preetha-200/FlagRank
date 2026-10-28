import pandas as pd
import numpy as np
import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def audit_results():
    metrics_path = os.path.join(base_dir, 'data', 'processed', 'synthetic_evaluation', 'synthetic_evaluation_metrics.csv')
    df = pd.read_csv(metrics_path)
    
    # 1. Prevalence & Baseline
    df['clean_population'] = df['n_targets'] + df['n_controls']
    df['positive_prevalence'] = df['n_targets'] / df['clean_population']
    
    # Recall@50 baseline is min(1.0, 50 / clean_population) ... wait, Recall is fraction of targets found.
    # If we pick 50 items randomly from (Targets + Controls), the expected number of targets we pick is 50 * positive_prevalence
    # Recall is (expected targets found) / total targets
    # So Random Recall@50 = (50 * (n_targets / clean_pop)) / n_targets = 50 / clean_pop
    df['random_recall_50'] = 50 / df['clean_population']
    df['recall_50_ratio'] = df['recall_at_50'] / df['random_recall_50']
    
    # PR-AUC baseline is just the positive prevalence
    df['pr_auc_baseline'] = df['positive_prevalence']
    
    # Effect size (Cohen's d) for target vs control scores
    # Since we only have means and we don't have standard deviations of scores in the aggregated csv...
    # We can't perfectly compute Cohen's d from the CSV. 
    # But we can report the mean difference.
    df['mean_diff'] = df['mean_target'] - df['mean_control']
    
    scenarios = df['scenario'].unique()
    audit_report = {}
    
    for sc in scenarios:
        sc_df = df[df['scenario'] == sc]
        audit_report[sc] = {
            'target_count_mean': sc_df['n_targets'].mean(),
            'target_count_std': sc_df['n_targets'].std(),
            'target_count_min': sc_df['n_targets'].min(),
            'target_count_max': sc_df['n_targets'].max(),
            'positive_prevalence_mean': sc_df['positive_prevalence'].mean(),
            'pr_auc_mean': sc_df['pr_auc'].mean(),
            'pr_auc_baseline_mean': sc_df['pr_auc_baseline'].mean(),
            'roc_auc_mean': sc_df['roc_auc'].mean(),
            'roc_auc_std': sc_df['roc_auc'].std(),
            'recall_50_mean': sc_df['recall_at_50'].mean(),
            'random_recall_50_mean': sc_df['random_recall_50'].mean(),
            'recall_50_ratio_mean': sc_df['recall_50_ratio'].mean(),
            'mean_diff': sc_df['mean_diff'].mean()
        }
        
    for sc, stats in audit_report.items():
        print(f"--- {sc} ---")
        for k, v in stats.items():
            print(f"{k}: {v}")
        print()
if __name__ == '__main__':
    audit_results()
