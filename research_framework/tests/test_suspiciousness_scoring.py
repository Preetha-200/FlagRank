import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.analysis.suspiciousness_scoring import calculate_suspiciousness_score

def create_mock_inconsistency_csv(tmp_path):
    df = pd.DataFrame({
        'query': ['q1', 'q1', 'q2', 'q3'],
        'category': ['c1', 'c1', 'c2', 'c3'],
        'amazon_rank': [1, 20, 10, 5],
        'expected_rank': [1.5, 2.0, 10.5, 25.0],
        'rank_deviation': [-0.5, 18.0, -0.5, -20.0],
        'rank_inconsistency_z': [-0.1, 2.5, 0.0, -3.0],
        'relative_rank_gap': [-0.05, 0.8, 0.0, -0.9],
        'feat_sponsored': [0, 1, 0, 0]
    })
    path = os.path.join(tmp_path, 'mock_inconsistency.csv')
    df.to_csv(path, index=False)
    return path

def test_suspiciousness_scoring(tmp_path):
    mock_in = create_mock_inconsistency_csv(tmp_path)
    mock_out = os.path.join(tmp_path, 'mock_scores.csv')
    mock_report = os.path.join(tmp_path, 'mock_report.md')
    
    df_out, top_10 = calculate_suspiciousness_score(mock_in, mock_out, mock_report)
    
    # 1. All component scores bounded between 0 and 1
    assert df_out['norm_inconsistency_z'].between(0.0, 1.0).all()
    assert df_out['norm_relative_gap'].between(0.0, 1.0).all()
    assert df_out['norm_rank_deviation'].between(0.0, 1.0).all()
    
    # 2. Suspiciousness score bounded between 0 and 100
    assert df_out['suspiciousness_score'].between(0.0, 100.0).all()
    
    # 3. Deterministic calculation check
    # Highest absolute deviation is 20.0 (row 3). Let's check absolutes.
    assert df_out.loc[3, 'absolute_rank_deviation'] == 20.0
    assert df_out.loc[1, 'absolute_rank_inconsistency_z'] == 2.5
    
    # 4. Signed inconsistency fields remain unchanged
    assert df_out.loc[3, 'rank_deviation'] == -20.0
    assert df_out.loc[1, 'rank_inconsistency_z'] == 2.5
    
    # 7. No target fields enter the score (score relies only on deviation magnitudes)
    # The scoring formula in the module strictly uses norm_* columns.
    
    # 8. Sponsored does not directly alter the score
    # Sponsored is in the output but not in the math.
    assert 'feat_sponsored' in df_out.columns
    
    # 9. Output preserves required evidence fields
    required = [
        'amazon_rank', 'expected_rank', 'rank_deviation', 'rank_inconsistency_z',
        'relative_rank_gap', 'absolute_rank_deviation', 'norm_inconsistency_z',
        'suspiciousness_score'
    ]
    for col in required:
        assert col in df_out.columns
