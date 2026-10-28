import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.analysis.synthetic_evaluation import run_synthetic_evaluation, perform_permutation, setup_directories

def test_perform_permutation():
    # Setup dummy dataframe
    df = pd.DataFrame({
        'query': ['q1', 'q1', 'q1', 'q1', 'q1', 'q2'],
        'synthetic_amazon_rank': [1, 2, 3, 4, 5, 1],
        'synthetic_target': [0, 0, 0, 0, 0, 0],
        'synthetic_collateral': [0, 0, 0, 0, 0, 0]
    })
    
    # Target index 3 (rank 4). Move up to rank 2 (shift = -2)
    new_df = perform_permutation(df, 3, -2)
    
    assert new_df.loc[3, 'synthetic_amazon_rank'] == 2
    assert new_df.loc[3, 'synthetic_target'] == 1
    
    # Collateral: rank 2 and 3 should shift down by 1 -> 3 and 4
    assert new_df.loc[1, 'synthetic_amazon_rank'] == 3
    assert new_df.loc[2, 'synthetic_amazon_rank'] == 4
    assert new_df.loc[1, 'synthetic_collateral'] == 1
    assert new_df.loc[2, 'synthetic_collateral'] == 1
    
    # Others unaffected
    assert new_df.loc[0, 'synthetic_amazon_rank'] == 1
    assert new_df.loc[0, 'synthetic_collateral'] == 0
    assert new_df.loc[4, 'synthetic_amazon_rank'] == 5
    assert new_df.loc[4, 'synthetic_collateral'] == 0
    
    # Query 2 unaffected
    assert new_df.loc[5, 'synthetic_amazon_rank'] == 1

def test_synthetic_evaluation_outputs():
    # Only test if files exist after running
    synth_dir, _ = setup_directories()
    metrics_path = os.path.join(synth_dir, 'synthetic_evaluation_metrics.csv')
    report_path = os.path.join(synth_dir, 'synthetic_evaluation_results.md')
    
    assert os.path.exists(metrics_path)
    assert os.path.exists(report_path)
    
    metrics = pd.read_csv(metrics_path)
    # 6 scenarios * 10 seeds = 60 rows
    assert len(metrics) == 60
    
    # Ensure mutually exclusive target/collateral/control counts sum to 1094
    total = metrics['n_targets'] + metrics['n_collateral'] + metrics['n_controls']
    assert (total == 1094).all()
