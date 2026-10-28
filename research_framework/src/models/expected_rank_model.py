import pandas as pd
import numpy as np
import os
import json
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class ExpectedRankModel:
    def __init__(self, random_state=42):
        self.random_state = random_state
        # Regularized ensemble trained on query-relative position target y_rel in [0, 1]
        self.model = RandomForestRegressor(
            n_estimators=300,
            max_depth=6,
            min_samples_leaf=4,
            max_features='sqrt',
            random_state=self.random_state,
            n_jobs=-1
        )
        self.features_used = []

    def prepare_data(self, df):
        # Programmatic verification to strictly enforce leakage rules
        self.features_used = [col for col in df.columns if col.startswith('feat_')]
        
        # Explicit forbidden columns check
        forbidden_in_x = ['amazon_rank', 'is_amazon_top6', 'query', 'category', 'asin', 'url', 'thumbnail', 'currency']
        for forbidden in forbidden_in_x:
            if forbidden in self.features_used:
                raise ValueError(f"Leakage detected: {forbidden} found in predictive features!")
                
        X = df[self.features_used]
        y = df['amazon_rank']
        groups = df['query']
        return X, y, groups

    def split_data(self, X, y, groups):
        # 80/20 Group-Aware Split on 'query' to prevent data leakage between overlapping queries
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=self.random_state)
        train_idx, test_idx = next(gss.split(X, y, groups))
        return train_idx, test_idx

    def _compute_query_sizes(self, groups, fallback_size=None):
        if groups is not None:
            group_series = pd.Series(groups)
            group_counts = group_series.value_counts().to_dict()
            return np.array([float(group_counts.get(g, 1.0)) for g in groups])
        if fallback_size is not None:
            return np.full(fallback_size, max(1.0, float(fallback_size)))
        return np.array([1.0])

    def fit(self, X_train, y_train, groups=None):
        """
        Fits the regularized regression model on query-relative normalized position:
        y_rel = (y - 1) / (N_q - 1) for N_q > 1, or 0.5 if N_q == 1.
        """
        if groups is not None:
            nq = self._compute_query_sizes(groups)
            y_vals = y_train.values if hasattr(y_train, 'values') else np.asarray(y_train)
            denom = np.maximum(1.0, nq - 1.0)
            y_rel = np.where(nq > 1.0, (y_vals - 1.0) / denom, 0.5)
        else:
            n_samples = float(len(X_train))
            y_vals = y_train.values if hasattr(y_train, 'values') else np.asarray(y_train)
            denom = max(1.0, n_samples - 1.0)
            y_rel = np.where(n_samples > 1.0, (y_vals - 1.0) / denom, 0.5)
            
        y_rel = np.clip(y_rel, 0.0, 1.0)
        self.model.fit(X_train, y_rel)

    def predict_relative(self, X):
        """Returns relative rank prediction in [0.0, 1.0]."""
        return np.clip(self.model.predict(X), 0.0, 1.0)

    def predict(self, X, groups=None, query_sizes=None):
        """
        Predicts expected absolute rank.
        Maps predicted relative placement in [0, 1] back to absolute rank:
        r_hat = 1.0 + y_hat * (N_q - 1.0), clipped to [1.0, N_q].
        """
        preds_rel = self.predict_relative(X)
        if query_sizes is not None:
            nq = np.asarray(query_sizes, dtype=float)
        elif groups is not None:
            nq = self._compute_query_sizes(groups)
        else:
            # Fallback when query grouping is not provided
            nq = np.full(len(X), max(1.0, float(len(X))))
            
        expected_rank = np.where(nq > 1.0, 1.0 + preds_rel * (nq - 1.0), 1.0)
        return np.clip(expected_rank, 1.0, np.maximum(1.0, nq))

    def generate_oof_predictions(self, X, y, groups, n_splits=5):
        """Generates Out-Of-Fold predictions using query-grouped GroupKFold."""
        gkf = GroupKFold(n_splits=n_splits)
        oof_preds = np.zeros(len(X))
        fold_assignments = np.zeros(len(X), dtype=int)
        
        for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
            # Validate leakage directly
            train_groups = set(groups.iloc[train_idx])
            val_groups = set(groups.iloc[val_idx])
            overlap = train_groups.intersection(val_groups)
            if overlap:
                raise ValueError(f"Group leakage detected in fold {fold}: {overlap}")
                
            X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
            g_train = groups.iloc[train_idx]
            X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
            g_val = groups.iloc[val_idx]
            
            fold_model = ExpectedRankModel(random_state=self.random_state)
            fold_model.fit(X_train, y_train, groups=g_train)
            oof_preds[val_idx] = fold_model.predict(X_val, groups=g_val)
            fold_assignments[val_idx] = fold
            
        return oof_preds, fold_assignments

def run_modeling_pipeline(features_path, predictions_path, report_path):
    df = pd.read_csv(features_path)
    
    model = ExpectedRankModel(random_state=42)
    X, y, groups = model.prepare_data(df)
    
    # 1. Evaluate traditional 80/20 Grouped Test Split
    train_idx, test_idx = model.split_data(X, y, groups)
    model.fit(X.iloc[train_idx], y.iloc[train_idx], groups=groups.iloc[train_idx])
    test_preds = model.predict(X.iloc[test_idx], groups=groups.iloc[test_idx])
    
    metrics_8020 = {
        'mae': mean_absolute_error(y.iloc[test_idx], test_preds),
        'rmse': np.sqrt(mean_squared_error(y.iloc[test_idx], test_preds)),
        'r2': r2_score(y.iloc[test_idx], test_preds),
        'spearman': spearmanr(y.iloc[test_idx], test_preds)[0]
    }
    
    # 2. Generate Full-Dataset OOF Predictions
    n_splits = 5
    oof_preds, fold_assignments = model.generate_oof_predictions(X, y, groups, n_splits=n_splits)
    
    metrics_oof = {
        'mae': mean_absolute_error(y, oof_preds),
        'rmse': np.sqrt(mean_squared_error(y, oof_preds)),
        'r2': r2_score(y, oof_preds),
        'spearman': spearmanr(y, oof_preds)[0]
    }
    
    metrics = {
        '80_20': metrics_8020,
        'oof': metrics_oof,
        'unique_queries_total': df['query'].nunique(),
        'n_splits': n_splits,
        'features_count': len(model.features_used)
    }
    
    # Compile output OOF predictions dataframe
    output_df = df.copy()
    output_df['expected_rank'] = oof_preds
    output_df['oof_fold'] = fold_assignments
    
    os.makedirs(os.path.dirname(predictions_path), exist_ok=True)
    
    front_cols = ['query', 'category', 'amazon_rank', 'expected_rank', 'oof_fold']
    other_cols = [c for c in output_df.columns if c not in front_cols]
    output_df = output_df[front_cols + other_cols]
    
    output_df.to_csv(predictions_path, index=False)
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    report_content = f"""# Expected-Ranking ML Model Report

## 1. Modelling Objective
To build a reproducible ML baseline that estimates the expected Amazon search rank of a product exclusively from its observable explanatory signals, without learning from the observed ranking itself.

## 2. Target Representation: Query-Relative Normalized Position
In e-commerce search, ranking competition takes place strictly within the retrieved query candidate set ($N_q \\in [4, 59]$).
To avoid query result length heterogeneity skewing absolute rank scales, the model predicts the query-relative normalized position:
$$y_i = \\frac{{r_i - 1}}{{N_q - 1}} \\in [0, 1]$$
At inference time, the predicted relative position is mapped back to the expected absolute rank within the query result list:
$$\\hat{{r}}_i = 1 + \\hat{{y}}_i (N_q - 1)$$
bounded strictly within $[1, N_q]$.

## 3. Input Features
Used exactly {metrics['features_count']} explanatory features (pruned redundant `feat_desc_length` which duplicated `feat_title_length`):
{', '.join(model.features_used)}

## 4. Excluded Fields (Leakage Prevention)
Explicitly blocked: `amazon_rank`, `is_amazon_top6`, `query`, `category`, `asin`, `url`, `thumbnail`, `currency`.

## 5. Grouping Strategy & Folds
- **Group Variable:** `query`
- **Folds:** {metrics['n_splits']}
- **Methodology:** `GroupKFold` ensures that all products for a given search query belong entirely to a single fold. Queries never cross between train and validation within the same fold, ensuring true generalization context.

## 6. Random Forest Configuration
- `n_estimators`: 300
- `max_depth`: 6
- `min_samples_leaf`: 4
- `max_features`: 'sqrt'
- `random_state`: 42

## 7. Model Performance Metrics
*(Note: These metrics strictly assess how well the baseline model maps organic signals to rank.)*

### Full-Dataset OOF Performance
- **OOF MAE:** {metrics_oof['mae']:.4f}
- **OOF RMSE:** {metrics_oof['rmse']:.4f}
- **OOF R²:** {metrics_oof['r2']:.4f}
- **OOF Spearman Correlation:** {metrics_oof['spearman']:.4f}

### Previous Grouped 80/20 Test Performance (For Historical Comparison)
- **Test MAE:** {metrics_8020['mae']:.4f}
- **Test RMSE:** {metrics_8020['rmse']:.4f}
- **Test R²:** {metrics_8020['r2']:.4f}
- **Test Spearman Correlation:** {metrics_8020['spearman']:.4f}

## 8. Limitations & Reproducibility
- **Limitations:** Query size $N_q$ is an inference-time context parameter representing the size of the retrieved search list.
- **Reproducibility:** Seed fixed at 42. `GroupKFold` provides deterministic indices for a static dataset.
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    return metrics, output_df
