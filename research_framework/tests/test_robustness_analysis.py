import os
import pandas as pd
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.analysis.synthetic_evaluation import setup_directories

def test_robustness_analysis_outputs():
    synth_dir, _ = setup_directories()
    results_csv = os.path.join(synth_dir, 'robustness_analysis_results.csv')
    results_md = os.path.join(synth_dir, 'robustness_analysis_results.md')
    
    assert os.path.exists(results_csv)
    assert os.path.exists(results_md)
    
    df = pd.read_csv(results_csv)
    assert not df.empty
    
    # Check that required columns exist
    required_cols = [
        'Population', 'Mean', 'Median', 'Std', 'P25', 'P75', 'P95', 'P99'
    ]
    for c in required_cols:
        assert c in df.columns
        
    assert 'Control' in df['Population'].values
    assert 'Collateral' in df['Population'].values
