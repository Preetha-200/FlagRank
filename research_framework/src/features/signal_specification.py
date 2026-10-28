"""
Signal Specification Module

This module serves as the single source of truth for feature-role classification 
prior to any feature engineering or model development.
"""

EXPLANATORY_SIGNALS = [
    'title',
    'description',
    'brand',
    'product_type',
    'price',
    'discounted',
    'original_price',
    'savings_percent',
    'rating',
    'total_reviews',
    'sponsored',
    'color'
]

RANKING_CONTEXT = [
    'query',
    'category'
]

OBSERVED_OUTCOME = [
    'amazon_rank'
]

VALIDATION_ONLY = [
    'is_amazon_top6'
]

EXCLUDED = [
    'asin',
    'currency',
    'url',
    'thumbnail'
]

def verify_signal_roles(df_columns):
    """
    Utility function to verify that every column in the dataframe 
    is assigned exactly one role, and no overlap exists.
    """
    all_roles = EXPLANATORY_SIGNALS + RANKING_CONTEXT + OBSERVED_OUTCOME + VALIDATION_ONLY + EXCLUDED
    
    # Check for overlaps
    assert len(all_roles) == len(set(all_roles)), "Overlap detected in signal specifications!"
    
    # Check coverage
    missing_from_spec = [col for col in df_columns if col not in all_roles]
    missing_from_df = [col for col in all_roles if col not in df_columns]
    
    return missing_from_spec, missing_from_df
