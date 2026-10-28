import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.preprocessing.preprocessor import Preprocessor, run_pipeline

def test_preprocessor_drops_zero_variance():
    df = pd.DataFrame({
        'query': ['a'], 'amazon_rank': [1], 'asin': ['123'],
        'amazon_choice': [False], 'best_seller': [False], 'amazon_prime': [False],
        'features_raw': [None], 'price': [10.0], 'original_price': [10.0],
        'rating': [4.5], 'total_reviews': [100], 'brand': ['BrandX'], 'color': ['Red'], 'is_amazon_top6': [True]
    })
    
    p = Preprocessor()
    p.fit(df)
    df_clean = p.transform(df)
    
    assert 'amazon_choice' not in df_clean.columns
    assert 'best_seller' not in df_clean.columns
    assert 'amazon_prime' not in df_clean.columns
    assert 'features_raw' not in df_clean.columns
    # Amazon rank must be retained
    assert 'amazon_rank' in df_clean.columns
    assert 'is_amazon_top6' in df_clean.columns

def test_preprocessor_handles_zeros():
    df = pd.DataFrame({
        'query': ['a', 'a'], 'amazon_rank': [1, 2], 'asin': ['123', '124'],
        'price': [0.0, 20.0], 'original_price': [0.0, 25.0],
        'rating': [0.0, 4.5], 'total_reviews': [0, 100],
        'brand': [None, 'BrandX'], 'color': [None, 'Red']
    })
    p = Preprocessor()
    p.fit(df)
    df_clean = p.transform(df)
    
    # Prices should be imputed with the median of non-zeros (20.0 and 25.0)
    assert df_clean.loc[0, 'price'] == 20.0
    assert df_clean.loc[0, 'original_price'] == 25.0
    
    # Ratings should stay 0.0
    assert df_clean.loc[0, 'rating'] == 0.0
    assert df_clean.loc[0, 'total_reviews'] == 0
    
    # Missing categorical should be Unknown
    assert df_clean.loc[0, 'brand'] == 'Unknown'
    assert df_clean.loc[0, 'color'] == 'Unknown'

def test_rank_continuity_check():
    df = pd.DataFrame({
        'query': ['a', 'a'], 'amazon_rank': [1, 3], 'asin': ['123', '124'],
        'price': [10.0, 20.0], 'original_price': [10.0, 25.0]
    })
    p = Preprocessor()
    p.fit(df)
    with pytest.raises(AssertionError):
        p.transform(df)
