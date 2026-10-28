import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_final_framework_outputs():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scores_path = os.path.join(base_dir, 'data', 'processed', 'suspiciousness_scores.csv')
    
    if not os.path.exists(scores_path):
        return
        
    df = pd.read_csv(scores_path)
    
    # 1. Dataset size
    assert len(df) == 1094
    
    # 2. No missing expected ranks or scores
    assert df['expected_rank'].isna().sum() == 0
    assert df['suspiciousness_score'].isna().sum() == 0
    
    # 3. Score bounds
    assert df['suspiciousness_score'].min() >= 0.0
    assert df['suspiciousness_score'].max() <= 100.0
    
    # 4. Correct rank-deviation direction
    # amazon_rank = 10, expected_rank = 20 -> deviation = -10
    calc_dev = df['amazon_rank'] - df['expected_rank']
    np.testing.assert_allclose(df['rank_deviation'], calc_dev)
    
    # 5. Required columns exist
    required = ['query', 'amazon_rank', 'expected_rank', 'rank_deviation', 
                'rank_inconsistency_z', 'relative_rank_gap', 'suspiciousness_score']
    for c in required:
        assert c in df.columns
