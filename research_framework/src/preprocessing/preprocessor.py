import pandas as pd
import numpy as np
import os

class Preprocessor:
    def __init__(self):
        self.global_median_price = 0.0
        self.global_median_orig_price = 0.0
        
    def fit(self, df):
        # Calculate medians for imputation, excluding 0.0
        prices = df[df['price'] > 0]['price']
        orig_prices = df[df['original_price'] > 0]['original_price']
        
        self.global_median_price = prices.median() if not prices.empty else 0.0
        self.global_median_orig_price = orig_prices.median() if not orig_prices.empty else 0.0
        
        return self
        
    def transform(self, df):
        df_clean = df.copy()
        
        # 1. Drop zero variance and completely null columns
        cols_to_drop = ['amazon_choice', 'best_seller', 'amazon_prime', 'features_raw']
        df_clean = df_clean.drop(columns=[col for col in cols_to_drop if col in df_clean.columns])
        
        # 2. Handle zero values based on investigation
        # Price = 0.0 means missing/unscraped. Rating = 0.0 means no reviews yet (valid).
        if 'price' in df_clean.columns:
            df_clean.loc[df_clean['price'] == 0.0, 'price'] = np.nan
        if 'original_price' in df_clean.columns:
            df_clean.loc[df_clean['original_price'] == 0.0, 'original_price'] = np.nan
        
        # 3. Handle missing values
        # Categorical
        if 'brand' in df_clean.columns:
            df_clean['brand'] = df_clean['brand'].fillna('Unknown')
        if 'color' in df_clean.columns:
            df_clean['color'] = df_clean['color'].fillna('Unknown')
        
        # Numerical - Impute with global median (query-level could be added later, but global is robust for now)
        if 'price' in df_clean.columns:
            df_clean['price'] = df_clean['price'].fillna(self.global_median_price)
        if 'original_price' in df_clean.columns:
            df_clean['original_price'] = df_clean['original_price'].fillna(self.global_median_orig_price)
        
        # 4. Validity checks (ensure no missing criticals)
        assert df_clean['asin'].isnull().sum() == 0, 'Missing ASINs found'
        assert df_clean['query'].isnull().sum() == 0, 'Missing queries found'
        assert df_clean['amazon_rank'].isnull().sum() == 0, 'Missing amazon_rank found'
        
        # Ensure amazon_rank is 1-based and continuous within query
        for q, group in df_clean.groupby('query'):
            ranks = sorted(group['amazon_rank'].tolist())
            assert ranks[0] == 1, f"Ranks for query '{q}' do not start at 1"
            assert all(ranks[i+1] - ranks[i] == 1 for i in range(len(ranks)-1)), f"Ranks for query '{q}' are not continuous"
        
        return df_clean

def run_pipeline(raw_path, processed_path):
    df = pd.read_csv(raw_path)
    preprocessor = Preprocessor()
    preprocessor.fit(df)
    df_clean = preprocessor.transform(df)
    
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df_clean.to_csv(processed_path, index=False)
    return df, df_clean
