import pandas as pd
import numpy as np
import os
import json

from src.features.signal_specification import (
    EXPLANATORY_SIGNALS, RANKING_CONTEXT, OBSERVED_OUTCOME, 
    VALIDATION_ONLY, EXCLUDED
)

class FeatureEngineer:
    def __init__(self):
        self.brand_freq = None
        self.product_type_freq = None
        self.color_freq = None
        
    def fit(self, df):
        # Fit frequency encodings for categoricals
        self.brand_freq = df['brand'].value_counts(normalize=True).to_dict() if 'brand' in df.columns else {}
        self.product_type_freq = df['product_type'].value_counts(normalize=True).to_dict() if 'product_type' in df.columns else {}
        self.color_freq = df['color'].value_counts(normalize=True).to_dict() if 'color' in df.columns else {}
        return self

    def transform(self, df):
        features_df = pd.DataFrame()
        
        # 1. Preserve Context and Targets explicitly (not as predictive features)
        for col in RANKING_CONTEXT + OBSERVED_OUTCOME + VALIDATION_ONLY:
            if col in df.columns:
                features_df[col] = df[col]
                
        # Also preserve unique identifier for tracing, even if excluded from features
        if 'asin' in df.columns:
            features_df['asin'] = df['asin']
            
        # 2. Boolean Signals (0 or 1)
        if 'discounted' in df.columns:
            features_df['feat_discounted'] = df['discounted'].astype(int)
        if 'sponsored' in df.columns:
            features_df['feat_sponsored'] = df['sponsored'].astype(int)
            
        # 3. Numeric Signals
        if 'price' in df.columns:
            features_df['feat_price'] = df['price'].astype(float)
        if 'original_price' in df.columns:
            features_df['feat_original_price'] = df['original_price'].astype(float)
        if 'savings_percent' in df.columns:
            features_df['feat_savings_percent'] = df['savings_percent'].astype(float)
        if 'rating' in df.columns:
            features_df['feat_rating'] = df['rating'].astype(float)
            
        # Log transform highly skewed total_reviews (adding 1 to handle 0)
        if 'total_reviews' in df.columns:
            features_df['feat_total_reviews_log'] = np.log1p(df['total_reviews'].astype(float))
            
        # 4. Categorical Signals (Frequency Encoding)
        # We use frequency encoding to prevent high dimensionality in a small dataset.
        if 'brand' in df.columns:
            features_df['feat_brand_freq'] = df['brand'].map(self.brand_freq).fillna(0.0)
        if 'product_type' in df.columns:
            features_df['feat_product_type_freq'] = df['product_type'].map(self.product_type_freq).fillna(0.0)
        if 'color' in df.columns:
            features_df['feat_color_freq'] = df['color'].map(self.color_freq).fillna(0.0)
            
        # 5. Text Signals (Lightweight Representation)
        # Instead of heavy LLMs or sparse TF-IDF, we extract length and query-relevance overlap.
        if 'title' in df.columns:
            features_df['feat_title_length'] = df['title'].fillna('').astype(str).str.len()
            # Calculate token overlap between title and query if query exists
            if 'query' in df.columns:
                def overlap_ratio(row):
                    if not isinstance(row['title'], str) or not isinstance(row['query'], str):
                        return 0.0
                    title_tokens = set(row['title'].lower().split())
                    query_tokens = set(row['query'].lower().split())
                    if len(query_tokens) == 0: return 0.0
                    return len(title_tokens.intersection(query_tokens)) / len(query_tokens)
                features_df['feat_title_query_overlap'] = df.apply(overlap_ratio, axis=1)
                
        # Note: 'description' is 100% identical to 'title' in raw data; 
        # feat_desc_length is omitted to prevent exact feature multicollinearity.
            
        # LEAKAGE SAFEGUARDS: Explicitly strip out any non-feat prefix columns except explicit context/outcomes
        allowed_non_features = set(RANKING_CONTEXT + OBSERVED_OUTCOME + VALIDATION_ONLY + ['asin'])
        for col in features_df.columns:
            if not col.startswith('feat_') and col not in allowed_non_features:
                raise ValueError(f"Leakage Safeguard Triggered: Column '{col}' is not permitted in output.")
                
        # Final safety check against observed outcomes
        predictive_features = [c for c in features_df.columns if c.startswith('feat_')]
        if 'amazon_rank' in predictive_features or 'is_amazon_top6' in predictive_features:
             raise ValueError("Target leakage detected in predictive features.")
             
        return features_df

def run_feature_engineering(clean_path, features_path):
    df = pd.read_csv(clean_path)
    engineer = FeatureEngineer()
    engineer.fit(df)
    features_df = engineer.transform(df)
    
    os.makedirs(os.path.dirname(features_path), exist_ok=True)
    features_df.to_csv(features_path, index=False)
    
    # Generate feature schema
    feature_schema = []
    for col in features_df.columns:
        if col.startswith('feat_'):
            schema_entry = {
                'feature_name': col,
                'is_predictive': True
            }
            if 'price' in col or 'savings' in col or 'rating' in col or 'reviews' in col:
                schema_entry['signal_type'] = 'numeric'
            elif 'discounted' in col or 'sponsored' in col:
                schema_entry['signal_type'] = 'boolean'
            elif 'freq' in col:
                schema_entry['signal_type'] = 'categorical'
            elif 'length' in col or 'overlap' in col:
                schema_entry['signal_type'] = 'text'
            else:
                schema_entry['signal_type'] = 'unknown'
            feature_schema.append(schema_entry)
            
    with open(os.path.join(os.path.dirname(features_path), 'feature_schema.json'), 'w') as f:
        json.dump(feature_schema, f, indent=2)
        
    return df, features_df
