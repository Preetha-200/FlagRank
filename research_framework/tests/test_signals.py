import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.features.signal_specification import (
    EXPLANATORY_SIGNALS, RANKING_CONTEXT, OBSERVED_OUTCOME, 
    VALIDATION_ONLY, EXCLUDED, verify_signal_roles
)
from src.config.settings import DATA_DIR

def test_signal_specification_coverage():
    processed_path = os.path.join(DATA_DIR, 'processed', 'amazon_search_dataset.csv')
    df = pd.read_csv(processed_path)
    
    missing_from_spec, missing_from_df = verify_signal_roles(df.columns)
    
    # All columns in the dataframe must have a role assigned
    assert len(missing_from_spec) == 0, f"Columns missing from specification: {missing_from_spec}"
    # The specification shouldn't include completely phantom columns (though excluded might have them, we check the active ones)
    for col in EXPLANATORY_SIGNALS + RANKING_CONTEXT + OBSERVED_OUTCOME + VALIDATION_ONLY:
        assert col in df.columns, f"Specified column {col} not found in processed dataframe"

def test_target_leakage_prevention():
    assert 'amazon_rank' in OBSERVED_OUTCOME
    assert 'amazon_rank' not in EXPLANATORY_SIGNALS
    
    assert 'is_amazon_top6' in VALIDATION_ONLY
    assert 'is_amazon_top6' not in EXPLANATORY_SIGNALS

def test_context_separation():
    assert 'query' in RANKING_CONTEXT
    assert 'query' not in EXPLANATORY_SIGNALS
    
    assert 'category' in RANKING_CONTEXT
    assert 'category' not in EXPLANATORY_SIGNALS
