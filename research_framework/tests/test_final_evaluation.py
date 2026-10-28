import os
import pandas as pd
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

def test_final_evaluation_outputs():
    final_dir = os.path.join(base_dir, 'data', 'processed', 'final_evaluation')
    results_csv = os.path.join(final_dir, 'final_evaluation_results.csv')
    results_md = os.path.join(final_dir, 'final_evaluation_report.md')
    plots_dir = os.path.join(final_dir, 'plots')
    
    assert os.path.exists(results_csv)
    assert os.path.exists(results_md)
    assert os.path.exists(plots_dir)
    
    df = pd.read_csv(results_csv)
    assert not df.empty
    
    # Check that required columns exist
    required_cols = [
        'num_products', 'num_queries', 'mean_rank', 'median_rank',
        'mean_score', 'median_score', 'std_score',
        'flagged_85', 'flagged_92', 'flagged_99'
    ]
    for c in required_cols:
        assert c in df.columns
        
    assert len(os.listdir(plots_dir)) >= 3
