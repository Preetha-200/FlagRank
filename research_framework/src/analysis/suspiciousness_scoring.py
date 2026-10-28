import pandas as pd
import numpy as np
import os

def safe_percentile_rank(series):
    """
    Computes empirical CDF percentile rank [0.0, 1.0].
    Safely maps an all-zero or empty series to 0.0 to prevent 
    un-anomalous baseline records from receiving default non-zero ranks.
    """
    if series.empty:
        return series
    if (series == 0).all():
        return pd.Series(0.0, index=series.index)
    return series.rank(pct=True)

def calculate_suspiciousness_score(inconsistency_path, output_path, report_path):
    df = pd.read_csv(inconsistency_path)
    
    # 2. Absolute Rank Inconsistency Z-Score
    df['absolute_rank_inconsistency_z'] = df['rank_inconsistency_z'].abs()
    
    # 3. Absolute Relative Rank Gap
    df['absolute_relative_rank_gap'] = df['relative_rank_gap'].abs()
    
    # 4. Absolute Rank Deviation
    df['absolute_rank_deviation'] = df['rank_deviation'].abs()
    
    # Normalization methodology: Robust Percentile-Based Normalization (Empirical CDF)
    # Using rank(pct=True) maps the absolute magnitude of the evidence into a perfect [0,1] scale 
    # relative to the entire evaluation dataset. This prevents a single extreme outlier 
    # from compressing the scale, and automatically adapts to any query density.
    df['norm_inconsistency_z'] = safe_percentile_rank(df['absolute_rank_inconsistency_z'])
    df['norm_relative_gap'] = safe_percentile_rank(df['absolute_relative_rank_gap'])
    df['norm_rank_deviation'] = safe_percentile_rank(df['absolute_rank_deviation'])
    
    # 5. Continuous Suspiciousness Score [0, 100]
    # Weighting:
    # 50% Standardized Query-Relative Inconsistency (most important)
    # 30% Relative Rank Displacement (contextual percentile gap)
    # 20% Absolute Rank Deviation (raw positions moved)
    df['suspiciousness_score'] = 100.0 * (
        (0.50 * df['norm_inconsistency_z']) +
        (0.30 * df['norm_relative_gap']) +
        (0.20 * df['norm_rank_deviation'])
    )
    
    # Enforce safe bounds just in case of floating point quirks
    df['suspiciousness_score'] = df['suspiciousness_score'].clip(lower=0.0, upper=100.0)
    
    # Reorder output to preserve evidence and surface scores
    evidence_cols = [
        'query', 'category', 'amazon_rank', 'expected_rank', 
        'rank_deviation', 'absolute_rank_deviation',
        'rank_inconsistency_z', 'absolute_rank_inconsistency_z',
        'relative_rank_gap', 'absolute_relative_rank_gap',
        'norm_inconsistency_z', 'norm_relative_gap', 'norm_rank_deviation',
        'suspiciousness_score'
    ]
    # Add sponsored if available, plus other existing columns
    if 'feat_sponsored' in df.columns:
        evidence_cols.insert(2, 'feat_sponsored')
    
    other_cols = [c for c in df.columns if c not in evidence_cols]
    output_df = df[evidence_cols + other_cols]
    
    # Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_df.to_csv(output_path, index=False)
    
    # Calculate top 10 candidates
    # Required columns: query, amazon_rank, expected_rank, rank_deviation, rank_inconsistency_z, relative_rank_gap, sponsored, suspiciousness_score
    disp_cols = ['query', 'amazon_rank', 'expected_rank', 'rank_deviation', 'rank_inconsistency_z', 'relative_rank_gap', 'suspiciousness_score']
    if 'feat_sponsored' in df.columns:
        disp_cols.insert(6, 'feat_sponsored')
        
    top_10 = output_df.sort_values(by='suspiciousness_score', ascending=False).head(10)[disp_cols]
    
    # Save report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    report_content = generate_report(df, top_10)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    return output_df, top_10

def generate_report(df, top_10):
    desc = df['suspiciousness_score'].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    
    report = f"""# Full-Dataset Suspiciousness Scoring Framework Report

## 1. Objective
Construct a continuous suspiciousness score from the already-established ranking inconsistency evidence. This score ranks products by how strongly their observed ranking deviates from the expected baseline relative to their query-level peers, evaluated across the entire dataset using OOF predictions.

## 2. Why a Continuous Score?
A continuous score `[0, 100]` ranks products by anomaly severity without asserting an arbitrary ground-truth manipulation label. E-commerce platforms contain natural noise; a continuous score allows investigators to audit the most extreme anomalies ("highest-scoring ranking inconsistency candidates") without classifying them as definitively fraudulent. 

## 3. Evidence Components
Because deviation direction is symmetric (unexpectedly high or unexpectedly low are both anomalous), we extract the magnitude:
1. `absolute_rank_inconsistency_z` = `abs(rank_inconsistency_z)`
2. `absolute_relative_rank_gap` = `abs(relative_rank_gap)`
3. `absolute_rank_deviation` = `abs(rank_deviation)`

## 4. Normalization Methodology
We use robust **Percentile-Based Normalization (Empirical CDF)** for all three components:
- `normalized_value = rank(pct=True)`
- **Rationale:** Dividing by a global maximum is highly vulnerable to single extreme outliers compressing the entire scale. Percentile normalization maps the absolute magnitude of the evidence into a robust `[0,1]` scale based on its severity relative to the entire dataset.

## 5. Explicit Formula & Weights
The components are aggregated into a single `[0, 100]` score using explicit weights prioritizing query-relative anomalies:
- **50%:** Standardized query-relative inconsistency (`norm_inconsistency_z`)
- **30%:** Relative rank displacement (`norm_relative_gap`)
- **20%:** Absolute rank deviation (`norm_rank_deviation`)

`suspiciousness_score = 100 × (0.50 × norm_inconsistency_z + 0.30 × norm_relative_gap + 0.20 × norm_rank_deviation)`

## 6. Important Limitations and Caveats
- **Not Causality:** This score establishes *inconsistency*, not intent. A high score means the product's rank is severely unexplained by the observable signals (price, reviews, text-match). This could be caused by manipulation (e.g., brushing), but could also be caused by unobserved organic variables (e.g., off-platform virality, superior click-through-rates not in the dataset).
- **No Direct Penalties:** `sponsored` products are not structurally penalized by the score. The score is strictly derived from the magnitude of the model's prediction error.

## 7. Score Distribution
- **Range:** [{desc['min']:.2f}, {desc['max']:.2f}]
- **Mean:** {desc['mean']:.2f}
- **Median (50th):** {desc['50%']:.2f}
- **Standard Deviation:** {desc['std']:.2f}
- **25th Percentile:** {desc['25%']:.2f}
- **75th Percentile:** {desc['75%']:.2f}
- **90th Percentile:** {desc['90%']:.2f}
- **95th Percentile:** {desc['95%']:.2f}
- **99th Percentile:** {desc['99%']:.2f}

## 8. Top 10 Highest-Scoring Ranking Inconsistency Candidates
```text
{top_10.to_string(index=False)}
```
"""
    return report
