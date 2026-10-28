import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.analysis.peer_group_analysis import calculate_inconsistency
from src.config.settings import DATA_DIR, BASE_DIR

def create_mock_predictions_csv(tmp_path):
    df = pd.DataFrame({
        'query': ['q1', 'q1', 'q1', 'q2'],
        'category': ['c1', 'c1', 'c1', 'c2'],
        'amazon_rank': [1, 2, 3, 1],
        'expected_rank': [3.0, 2.0, 1.0, 1.0],
        'feat_price': [10, 20, 30, 40]
    })
    path = os.path.join(tmp_path, 'mock_predictions.csv')
    df.to_csv(path, index=False)
    return path

def test_peer_group_analysis(tmp_path):
    mock_in = create_mock_predictions_csv(tmp_path)
    mock_out = os.path.join(tmp_path, 'mock_inconsistency.csv')
    mock_report = os.path.join(tmp_path, 'mock_report.md')
    
    stats, df_out = calculate_inconsistency(mock_in, mock_out, mock_report)
    
    # 1. Output contains all required fields
    required_cols = [
        'rank_deviation', 'query_deviation_mean', 'query_deviation_std', 
        'rank_inconsistency_z', 'observed_rank_percentile', 
        'expected_rank_percentile', 'relative_rank_gap'
    ]
    for col in required_cols:
        assert col in df_out.columns
        
    # 2. rank_deviation calculation check
    # Row 0: amz=1, exp=3.0 -> dev=-2.0
    assert df_out.loc[0, 'rank_deviation'] == -2.0
    
    # 3. Query-level isolation
    q1_df = df_out[df_out['query'] == 'q1']
    assert len(q1_df) == 3
    # deviations: -2.0, 0.0, 2.0
    assert q1_df['query_deviation_mean'].iloc[0] == 0.0
    
    # 4. Zero standard deviation handling
    # q2 only has 1 row, so std is NaN -> Z-score should be safely 0.0
    q2_df = df_out[df_out['query'] == 'q2']
    assert pd.isna(q2_df['query_deviation_std'].iloc[0])
    assert q2_df['rank_inconsistency_z'].iloc[0] == 0.0
    
    # 5. Percentiles remain in valid range and respect rank order
    assert df_out['observed_rank_percentile'].max() <= 1.0
    assert df_out['observed_rank_percentile'].min() > 0.0
    
    # Row 0 (rank 1 in q1) should have lowest percentile vs Row 2 (rank 3 in q1)
    assert df_out.loc[0, 'observed_rank_percentile'] < df_out.loc[2, 'observed_rank_percentile']
    
    # 6. amazon_rank and expected_rank remain unmodified
    assert df_out.loc[0, 'amazon_rank'] == 1
    assert df_out.loc[0, 'expected_rank'] == 3.0
    
    # 7. Check relative rank gap
    # Row 0: obs_pct = 1/3, exp_pct = 3/3 -> gap = -2/3
    assert np.isclose(df_out.loc[0, 'relative_rank_gap'], -2/3)
