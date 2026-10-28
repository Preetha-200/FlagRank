import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.features.engineer import FeatureEngineer

def test_feature_engineering_transforms():
    df = pd.DataFrame({
        'query': ['laptop', 'laptop', 'mouse'],
        'amazon_rank': [1, 2, 1],
        'is_amazon_top6': [True, True, True],
        'asin': ['A', 'B', 'C'],
        'title': ['Gaming laptop 15 inch', 'Office laptop', 'wireless mouse'],
        'description': ['A fast laptop.', None, 'A good mouse.'],
        'brand': ['Dell', 'HP', 'Dell'],
        'product_type': ['PC', 'PC', 'Accessory'],
        'color': ['Black', 'Black', 'White'],
        'price': [1000.0, 500.0, 20.0],
        'original_price': [1200.0, 500.0, 25.0],
        'savings_percent': [20.0, 0.0, 20.0],
        'rating': [4.5, 4.0, 4.8],
        'total_reviews': [100, 50, 0],
        'sponsored': [True, False, False],
        'discounted': [True, False, True]
    })
    
    eng = FeatureEngineer()
    eng.fit(df)
    features_df = eng.transform(df)
    
    # Check outputs exist
    assert 'feat_price' in features_df.columns
    assert 'feat_total_reviews_log' in features_df.columns
    assert 'feat_sponsored' in features_df.columns
    assert 'feat_brand_freq' in features_df.columns
    assert 'feat_title_length' in features_df.columns
    assert 'feat_title_query_overlap' in features_df.columns
    
    # Check transformations
    # total_reviews for index 0 is 100 -> log1p(100)
    assert np.isclose(features_df.loc[0, 'feat_total_reviews_log'], np.log1p(100))
    # brand 'Dell' appears 2 out of 3 times -> freq = 0.666
    assert np.isclose(features_df.loc[0, 'feat_brand_freq'], 2/3)
    # query 'laptop' and title 'Gaming laptop 15 inch'. overlap is 1 / 1
    assert features_df.loc[0, 'feat_title_query_overlap'] == 1.0

def test_feature_leakage_safeguards():
    df = pd.DataFrame({
        'query': ['laptop'],
        'amazon_rank': [1],
        'is_amazon_top6': [True],
        'asin': ['A'],
        'title': ['Gaming laptop'],
        'price': [1000.0]
    })
    
    eng = FeatureEngineer()
    eng.fit(df)
    features_df = eng.transform(df)
    
    predictive_feats = [c for c in features_df.columns if c.startswith('feat_')]
    # No target should be prefixed with feat_
    assert 'amazon_rank' not in predictive_feats
    assert 'is_amazon_top6' not in predictive_feats
    assert 'feat_amazon_rank' not in predictive_feats
    assert 'asin' not in predictive_feats
    
    # Targets/Context should be preserved exactly
    assert 'amazon_rank' in features_df.columns
    assert 'query' in features_df.columns
    assert 'is_amazon_top6' in features_df.columns
