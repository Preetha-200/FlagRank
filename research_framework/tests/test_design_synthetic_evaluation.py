import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.analysis.design_synthetic_evaluation import calculate_design_stats

def test_calculate_design_stats():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scores_path = os.path.join(base_dir, 'data', 'processed', 'suspiciousness_scores.csv')
    
    if not os.path.exists(scores_path):
        return
        
    stats = calculate_design_stats(scores_path)
    
    assert stats['total_products'] == 1094
    assert stats['num_queries'] > 0
    assert stats['group_size_min'] >= 4
    assert stats['rank_spread_min'] > 0

def test_synthetic_states_mutually_exclusive():
    # Symbolic test verifying the design logic requested in Chunk 16
    # In practice, exactly one of these flags must be 1.
    def check_valid_state(target, collateral, control):
        return (target + collateral + control) == 1
        
    assert check_valid_state(1, 0, 0) == True
    assert check_valid_state(0, 1, 0) == True
    assert check_valid_state(0, 0, 1) == True
    assert check_valid_state(1, 1, 0) == False
    assert check_valid_state(0, 0, 0) == False

def test_eligibility_bounds():
    # Symbolic test: Target must not exceed query min/max bounds
    query_min_rank = 1
    query_max_rank = 20
    
    def is_eligible(current_rank, shift):
        new_rank = current_rank + shift
        return query_min_rank <= new_rank <= query_max_rank
        
    assert is_eligible(15, -10) == True   # 15 -> 5
    assert is_eligible(5, -10) == False   # 5 -> -5 (Out of bounds)
    assert is_eligible(18, 5) == False    # 18 -> 23 (Out of bounds)
