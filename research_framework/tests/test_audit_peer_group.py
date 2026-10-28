import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.analysis.audit_peer_group import calculate_loo_zscore

def test_calculate_loo_zscore_basic():
    # Group of 4 items
    df = pd.DataFrame({
        'query': ['q1', 'q1', 'q1', 'q1'],
        'amazon_rank': [1, 2, 3, 4],
        'rank_deviation': [10.0, 20.0, 30.0, 40.0]
    })
    
    res = calculate_loo_zscore(df)
    
    # For item 0 (dev=10):
    # others = [20, 30, 40] -> mean = 30, std = 10
    # loo_z = (10 - 30) / 10 = -2.0
    assert np.isclose(res.loc[0, 'loo_rank_inconsistency_z'], -2.0)
    
    # For item 1 (dev=20):
    # others = [10, 30, 40] -> mean = 26.666..., std = 15.27525...
    # loo_z = (20 - 26.666) / 15.27525 = -0.436435...
    expected_std = np.std([10, 30, 40], ddof=1)
    expected_z = (20 - np.mean([10, 30, 40])) / expected_std
    assert np.isclose(res.loc[1, 'loo_rank_inconsistency_z'], expected_z)

def test_calculate_loo_zscore_small_groups():
    # Groups of size 1 and 2
    df = pd.DataFrame({
        'query': ['single', 'double', 'double'],
        'amazon_rank': [1, 1, 2],
        'rank_deviation': [5.0, 10.0, 20.0]
    })
    
    res = calculate_loo_zscore(df)
    
    # Should safely fallback to 0.0
    assert np.all(res['loo_rank_inconsistency_z'] == 0.0)

def test_calculate_loo_zscore_zero_variance():
    # Group of 4 items with identical deviations
    df = pd.DataFrame({
        'query': ['q1', 'q1', 'q1', 'q1'],
        'amazon_rank': [1, 2, 3, 4],
        'rank_deviation': [10.0, 10.0, 10.0, 10.0]
    })
    
    res = calculate_loo_zscore(df)
    
    # Should safely fallback to 0.0 due to zero std
    assert np.all(res['loo_rank_inconsistency_z'] == 0.0)

def test_deterministic_behavior():
    df1 = pd.DataFrame({
        'query': ['q1', 'q1', 'q1', 'q1'],
        'amazon_rank': [4, 2, 1, 3],
        'rank_deviation': [40.0, 20.0, 10.0, 30.0]
    })
    
    df2 = pd.DataFrame({
        'query': ['q1', 'q1', 'q1', 'q1'],
        'amazon_rank': [1, 2, 3, 4],
        'rank_deviation': [10.0, 20.0, 30.0, 40.0]
    })
    
    res1 = calculate_loo_zscore(df1).sort_values('amazon_rank').reset_index(drop=True)
    res2 = calculate_loo_zscore(df2).sort_values('amazon_rank').reset_index(drop=True)
    
    pd.testing.assert_series_equal(res1['loo_rank_inconsistency_z'], res2['loo_rank_inconsistency_z'])
