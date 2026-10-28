import pandas as pd
import numpy as np
import os
import json

def calculate_design_stats(scores_path):
    df = pd.read_csv(scores_path)
    
    # 1. Query Group Sizes
    group_sizes = df.groupby('query').size()
    
    # 2. Rank ranges per query
    rank_ranges = df.groupby('query')['amazon_rank'].agg(['min', 'max', lambda x: x.max() - x.min()])
    rank_ranges.columns = ['min_rank', 'max_rank', 'rank_spread']
    
    # Calculate some percentile-based displacements
    # If we want small (e.g. 10%), medium (25%), large (50%) of the query's rank spread
    
    stats = {
        'total_products': len(df),
        'num_queries': len(group_sizes),
        'group_size_min': int(group_sizes.min()),
        'group_size_median': int(group_sizes.median()),
        'group_size_max': int(group_sizes.max()),
        'group_size_mean': float(group_sizes.mean()),
        'rank_spread_min': int(rank_ranges['rank_spread'].min()),
        'rank_spread_median': int(rank_ranges['rank_spread'].median()),
        'rank_spread_max': int(rank_ranges['rank_spread'].max()),
    }
    
    return stats

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    scores_path = os.path.join(base_dir, 'data', 'processed', 'suspiciousness_scores.csv')
    
    stats = calculate_design_stats(scores_path)
    print(json.dumps(stats, indent=2))
