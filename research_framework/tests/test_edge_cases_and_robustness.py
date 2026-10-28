import os
import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocessing.preprocessor import Preprocessor
from src.features.engineer import FeatureEngineer
from src.models.expected_rank_model import ExpectedRankModel
from src.analysis.peer_group_analysis import calculate_inconsistency
from src.analysis.suspiciousness_scoring import calculate_suspiciousness_score, safe_percentile_rank
from src.analysis.synthetic_evaluation import perform_permutation

def test_safe_percentile_rank_all_zeros():
    s = pd.Series([0.0, 0.0, 0.0, 0.0])
    res = safe_percentile_rank(s)
    assert (res == 0.0).all()

def test_safe_percentile_rank_ties_and_extremes():
    s = pd.Series([1.0, 2.0, 2.0, 5.0, 100.0])
    res = safe_percentile_rank(s)
    assert res.is_monotonic_increasing
    assert res.min() > 0.0
    assert res.max() == 1.0
    # Ties should share identical rank
    assert res.iloc[1] == res.iloc[2]

def test_peer_group_analysis_small_and_single_queries(tmp_path):
    df = pd.DataFrame({
        'query': ['q_single', 'q_pair', 'q_pair', 'q_normal', 'q_normal', 'q_normal', 'q_normal'],
        'category': ['c1'] * 7,
        'amazon_rank': [1, 1, 2, 1, 2, 3, 4],
        'expected_rank': [1.0, 1.5, 1.5, 2.0, 2.0, 2.5, 3.0],
        'feat_price': [10.0] * 7
    })
    in_path = os.path.join(tmp_path, 'small_queries.csv')
    out_path = os.path.join(tmp_path, 'small_out.csv')
    rep_path = os.path.join(tmp_path, 'small_rep.md')
    df.to_csv(in_path, index=False)
    
    stats, res_df = calculate_inconsistency(in_path, out_path, rep_path)
    
    assert len(res_df) == 7
    # Single item query has NaN std -> safe Z fallback to 0.0
    single_row = res_df[res_df['query'] == 'q_single'].iloc[0]
    assert single_row['rank_inconsistency_z'] == 0.0
    assert single_row['relative_rank_gap'] == 0.0
    
    # All scores should be finite
    assert np.isfinite(res_df['rank_inconsistency_z']).all()
    assert np.isfinite(res_df['relative_rank_gap']).all()

def test_scoring_boundedness_on_extreme_ranks(tmp_path):
    df = pd.DataFrame({
        'query': ['q1', 'q1', 'q1'],
        'category': ['c1', 'c1', 'c1'],
        'amazon_rank': [1, 50, 100],
        'expected_rank': [100.0, 2.0, 50.0],
        'rank_deviation': [-99.0, 48.0, 50.0],
        'rank_inconsistency_z': [-2.5, 1.2, 1.3],
        'relative_rank_gap': [-0.9, 0.4, 0.5],
        'feat_sponsored': [0, 1, 0]
    })
    in_path = os.path.join(tmp_path, 'extreme_inc.csv')
    out_path = os.path.join(tmp_path, 'extreme_scores.csv')
    rep_path = os.path.join(tmp_path, 'extreme_rep.md')
    df.to_csv(in_path, index=False)
    
    res_df, _ = calculate_suspiciousness_score(in_path, out_path, rep_path)
    
    assert res_df['suspiciousness_score'].min() >= 0.0
    assert res_df['suspiciousness_score'].max() <= 100.0
    assert np.isfinite(res_df['suspiciousness_score']).all()

def test_feature_engineering_unseen_categories():
    train_df = pd.DataFrame({
        'query': ['q1', 'q1'], 'amazon_rank': [1, 2], 'asin': ['a1', 'a2'],
        'title': ['phone case', 'screen protector'], 'description': ['case', 'glass'],
        'brand': ['Anker', 'Spigen'], 'product_type': ['Electronics', 'Electronics'],
        'color': ['Black', 'Clear'], 'price': [15.0, 10.0], 'original_price': [20.0, 12.0],
        'rating': [4.5, 4.2], 'total_reviews': [100, 50], 'discounted': [True, False],
        'sponsored': [False, True], 'savings_percent': [25.0, 0.0]
    })
    test_df = pd.DataFrame({
        'query': ['q2'], 'amazon_rank': [1], 'asin': ['a3'],
        'title': ['novel book'], 'description': ['paperback'],
        'brand': ['NewBrand'], 'product_type': ['Book'],
        'color': ['UnknownColor'], 'price': [25.0], 'original_price': [25.0],
        'rating': [5.0], 'total_reviews': [10], 'discounted': [False],
        'sponsored': [False], 'savings_percent': [0.0]
    })
    
    fe = FeatureEngineer()
    fe.fit(train_df)
    res = fe.transform(test_df)
    
    # Unseen frequency encoded categories safely map to 0.0
    assert res.loc[0, 'feat_brand_freq'] == 0.0
    assert res.loc[0, 'feat_product_type_freq'] == 0.0
    assert res.loc[0, 'feat_color_freq'] == 0.0
    # No nulls
    assert res.isna().sum().sum() == 0

def test_synthetic_permutation_preserves_unaffected_controls():
    df = pd.DataFrame({
        'query': ['q1', 'q1', 'q1', 'q1', 'q1'],
        'amazon_rank': [1, 2, 3, 4, 5],
        'synthetic_amazon_rank': [1, 2, 3, 4, 5],
        'synthetic_target': [0, 0, 0, 0, 0],
        'synthetic_collateral': [0, 0, 0, 0, 0]
    })
    
    # Promote product at index 3 (rank 4) by -2 positions -> new rank 2
    res = perform_permutation(df, target_idx=3, shift=-2)
    
    # Target product (index 3) should now be rank 2
    assert res.loc[3, 'synthetic_amazon_rank'] == 2
    assert res.loc[3, 'synthetic_target'] == 1
    
    # Ranks 2 and 3 should be shifted down to 3 and 4 as collaterals
    assert res.loc[1, 'synthetic_collateral'] == 1
    assert res.loc[2, 'synthetic_collateral'] == 1
    assert res.loc[1, 'synthetic_amazon_rank'] == 3
    assert res.loc[2, 'synthetic_amazon_rank'] == 4
    
    # Rank 1 (index 0) and Rank 5 (index 4) should be unaffected controls
    assert res.loc[0, 'synthetic_target'] == 0
    assert res.loc[0, 'synthetic_collateral'] == 0
    assert res.loc[0, 'synthetic_amazon_rank'] == 1
    
    assert res.loc[4, 'synthetic_target'] == 0
    assert res.loc[4, 'synthetic_collateral'] == 0
    assert res.loc[4, 'synthetic_amazon_rank'] == 5
