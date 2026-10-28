import pandas as pd
import numpy as np
import os
import json

def calculate_inconsistency(predictions_path, output_path, report_path):
    df = pd.read_csv(predictions_path)
    
    # 2. Peer Group Stats
    query_sizes = df.groupby('query').size()
    stats = {
        'unique_queries': int(query_sizes.count()),
        'min_peer_group_size': int(query_sizes.min()),
        'max_peer_group_size': int(query_sizes.max()),
        'median_peer_group_size': float(query_sizes.median())
    }
    
    # 3. Raw ranking deviation
    # amazon_rank = 1 means top position. 
    # expected_rank = 1 means model expects top position.
    df['rank_deviation'] = df['amazon_rank'] - df['expected_rank']
    
    # 4. Query-relative normalization (Z-score)
    df['query_deviation_mean'] = df.groupby('query')['rank_deviation'].transform('mean')
    df['query_deviation_std'] = df.groupby('query')['rank_deviation'].transform('std')
    
    # Handle zero std dev safely by falling back to 0.0 for the z-score
    def safe_zscore(row):
        std = row['query_deviation_std']
        if pd.isna(std) or std == 0.0:
            return 0.0
        return (row['rank_deviation'] - row['query_deviation_mean']) / std
        
    df['rank_inconsistency_z'] = df.apply(safe_zscore, axis=1)
    
    # 5. Relative rank comparison (Percentiles)
    # Higher rank value means lower on page. 
    # rank(pct=True) assigns 1.0 to the highest value (lowest on page).
    # This is consistent: 0.1 percentile means top of page, 0.9 means bottom.
    df['observed_rank_percentile'] = df.groupby('query')['amazon_rank'].rank(pct=True)
    df['expected_rank_percentile'] = df.groupby('query')['expected_rank'].rank(pct=True)
    
    df['relative_rank_gap'] = df['observed_rank_percentile'] - df['expected_rank_percentile']
    
    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Organize columns logically
    core_cols = [
        'query', 'category', 'amazon_rank', 'expected_rank', 
        'rank_deviation', 'query_deviation_mean', 'query_deviation_std', 'rank_inconsistency_z',
        'observed_rank_percentile', 'expected_rank_percentile', 'relative_rank_gap'
    ]
    other_cols = [c for c in df.columns if c not in core_cols]
    output_df = df[core_cols + other_cols]
    
    output_df.to_csv(output_path, index=False)
    
    # Descriptive statistics for report
    desc_stats = df[['rank_deviation', 'rank_inconsistency_z', 'relative_rank_gap']].describe().to_dict()
    
    # Write report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    report_content = f"""# Full-Dataset OOF Peer-Group Analysis and Ranking Inconsistency Report

## 1. Definition of Peer Group
A peer group is defined strictly as **all products belonging to the same search query**. Categories are not used as peer groups because ranking competition occurs locally within a specific user search intent, not globally across an entire category.
This analysis evaluates the **full dataset** using Out-Of-Fold expected ranks.

## 2. Peer Group Statistics
- **Unique queries:** {stats['unique_queries']}
- **Minimum peer-group size:** {stats['min_peer_group_size']} products
- **Maximum peer-group size:** {stats['max_peer_group_size']} products
- **Median peer-group size:** {stats['median_peer_group_size']} products

## 3. Rank Deviation
**Formula:** `rank_deviation = amazon_rank - expected_rank`
- **Positive value:** The product appeared *lower* in the search results (e.g. rank 10) than the model expected (e.g. rank 2).
- **Negative value:** The product appeared *higher* in the search results (e.g. rank 2) than the model expected (e.g. rank 10). A highly negative value is a candidate signal for unexplained rank inflation.

## 4. Query-Relative Z-Score
**Formula:** `rank_inconsistency_z = (rank_deviation - query_deviation_mean) / query_deviation_std`
Absolute deviation values can be misleading depending on the variance of the model within a specific query. The Z-score measures how unusual a product's deviation is *relative to other products in the exact same search query*.
- **Edge Case Handling:** If `query_deviation_std` is 0.0 or NaN (e.g., only one product in query, or model predicts identical deviations), the Z-score explicitly defaults to `0.0`.

## 5. Percentile Methodology & Relative Rank Gap
**Formula:** `relative_rank_gap = observed_rank_percentile - expected_rank_percentile`
We calculate percentiles for both `amazon_rank` and `expected_rank` within each query. 
- A lower percentile (e.g., 0.1) means the product is at the top of the search page.
- A negative `relative_rank_gap` means the product occupies a *better* (top) percentile position observed in reality compared to what its organic explanatory features suggest.

## 6. Descriptive Statistics of Inconsistency Measures
```text
Rank Deviation: Mean {desc_stats['rank_deviation']['mean']:.2f}, Min {desc_stats['rank_deviation']['min']:.2f}, Max {desc_stats['rank_deviation']['max']:.2f}
Rank Inconsistency Z-Score: Mean {desc_stats['rank_inconsistency_z']['mean']:.2f}, Min {desc_stats['rank_inconsistency_z']['min']:.2f}, Max {desc_stats['rank_inconsistency_z']['max']:.2f}
Relative Rank Gap: Mean {desc_stats['relative_rank_gap']['mean']:.2f}, Min {desc_stats['relative_rank_gap']['min']:.2f}, Max {desc_stats['relative_rank_gap']['max']:.2f}
```

## 7. Limitations
- Percentile resolution is limited by peer group sizes (e.g., if a query only has 5 products, percentiles move in increments of 0.2).
- The baseline expected model is not perfectly calibrated list-wise, meaning `expected_rank` can theoretically produce decimals or out-of-bound bounds. The within-query percentiling and Z-score calculations mitigate this structurally.
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    return stats, output_df
