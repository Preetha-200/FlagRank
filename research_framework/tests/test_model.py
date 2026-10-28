import sys
import os
import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models.expected_rank_model import ExpectedRankModel

def create_dummy_data():
    return pd.DataFrame({
        'query': ['q1', 'q1', 'q2', 'q2', 'q3'],
        'category': ['c1', 'c1', 'c2', 'c2', 'c3'],
        'amazon_rank': [1, 2, 1, 2, 1],
        'is_amazon_top6': [True, True, True, True, True],
        'asin': ['a', 'b', 'c', 'd', 'e'],
        'feat_price': [10.0, 20.0, 15.0, 25.0, 10.0],
        'feat_rating': [4.5, 4.0, 5.0, 3.5, 4.0]
    })

def test_leakage_safeguards():
    df = create_dummy_data()
    model = ExpectedRankModel()
    
    X, y, groups = model.prepare_data(df)
    
    # 1. amazon_rank cannot appear in X
    assert 'amazon_rank' not in X.columns
    # 2. is_amazon_top6 cannot appear in X
    assert 'is_amazon_top6' not in X.columns
    # 3. query and category are not used as predictive features
    assert 'query' not in X.columns
    assert 'category' not in X.columns
    
    # Check what IS in X
    assert 'feat_price' in X.columns
    assert 'feat_rating' in X.columns
    assert len(X.columns) == 2

def test_model_training_and_predictions():
    df = create_dummy_data()
    model = ExpectedRankModel()
    
    X, y, groups = model.prepare_data(df)
    train_idx, test_idx = model.split_data(X, y, groups)
    
    X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
    X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]
    
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    
    # 4. Model produces finite expected-rank predictions
    assert np.all(np.isfinite(preds))
    assert len(preds) == len(X_test)

def test_reproducibility():
    df = create_dummy_data()
    model1 = ExpectedRankModel(random_state=42)
    model2 = ExpectedRankModel(random_state=42)
    
    X1, y1, g1 = model1.prepare_data(df)
    X2, y2, g2 = model2.prepare_data(df)
    
    tr1, te1 = model1.split_data(X1, y1, g1)
    tr2, te2 = model2.split_data(X2, y2, g2)
    
    assert list(tr1) == list(tr2)
    assert list(te1) == list(te2)
    
    model1.fit(X1.iloc[tr1], y1.iloc[tr1])
    model2.fit(X2.iloc[tr2], y2.iloc[tr2])
    
    pred1 = model1.predict(X1.iloc[te1])
    pred2 = model2.predict(X2.iloc[te2])
    
    np.testing.assert_allclose(pred1, pred2)

def test_oof_coverage_and_leakage():
    df = pd.DataFrame({
        'query': ['q1', 'q1', 'q2', 'q2', 'q3', 'q3', 'q4', 'q4', 'q5', 'q5'],
        'category': ['c1']*10,
        'amazon_rank': [1, 2]*5,
        'is_amazon_top6': [True]*10,
        'asin': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
        'feat_price': [10.0, 20.0]*5,
        'feat_rating': [4.5, 4.0]*5
    })
    
    model = ExpectedRankModel(random_state=42)
    X, y, groups = model.prepare_data(df)
    
    n_splits = 3
    oof_preds, fold_assigns = model.generate_oof_predictions(X, y, groups, n_splits=n_splits)
    
    # Coverage exactly matches source rows
    assert len(oof_preds) == len(df)
    
    # No missing predictions
    assert np.all(oof_preds > 0) # ranks should be positive
    assert np.all(np.isfinite(oof_preds))
    
    # Fold assignments are valid
    assert np.min(fold_assigns) >= 0
    assert np.max(fold_assigns) < n_splits
    
    # Query isolation (no query in multiple folds)
    df_folds = pd.DataFrame({'query': groups, 'fold': fold_assigns})
    query_fold_counts = df_folds.groupby('query')['fold'].nunique()
    assert np.all(query_fold_counts == 1)



def test_query_relative_rank_bounds_and_single_item():
    """Verify that predictions are strictly bounded within [1.0, N_q], including single-item queries."""
    model = ExpectedRankModel(random_state=42)
    df_train = pd.DataFrame({
        'query': ['q1', 'q1', 'q1', 'q2', 'q2'],
        'category': ['c1']*5,
        'amazon_rank': [1, 2, 3, 1, 2],
        'asin': ['a1', 'a2', 'a3', 'a4', 'a5'],
        'feat_price': [10.0, 20.0, 30.0, 15.0, 25.0],
        'feat_rating': [4.5, 4.0, 3.5, 4.8, 3.9]
    })
    X_tr, y_tr, g_tr = model.prepare_data(df_train)
    model.fit(X_tr, y_tr, groups=g_tr)
    
    # Test on single-item query (N_q = 1)
    df_single = pd.DataFrame({
        'query': ['q_single'],
        'category': ['c1'],
        'amazon_rank': [1],
        'asin': ['s1'],
        'feat_price': [50.0],
        'feat_rating': [5.0]
    })
    X_single, y_single, g_single = model.prepare_data(df_single)
    pred_single = model.predict(X_single, groups=g_single)
    assert np.isclose(pred_single[0], 1.0)
    
    # Test on large query (N_q = 10)
    df_large = pd.DataFrame({
        'query': ['q_large'] * 10,
        'category': ['c1'] * 10,
        'amazon_rank': list(range(1, 11)),
        'asin': [f'l{i}' for i in range(10)],
        'feat_price': [float(i * 10) for i in range(1, 11)],
        'feat_rating': [4.0] * 10
    })
    X_large, y_large, g_large = model.prepare_data(df_large)
    preds_large = model.predict(X_large, groups=g_large)
    assert np.all(preds_large >= 1.0)
    assert np.all(preds_large <= 10.0)

def test_query_size_context_handling():
    """Verify inference context behavior with explicit query_sizes and fallback."""
    model = ExpectedRankModel(random_state=42)
    df = create_dummy_data()
    X, y, groups = model.prepare_data(df)
    model.fit(X, y, groups=groups)
    
    # 1. Prediction with explicit query_sizes array
    sizes = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
    preds_sizes = model.predict(X, query_sizes=sizes)
    assert np.all(preds_sizes >= 1.0)
    assert np.all(preds_sizes <= 5.0)
    
    # 2. Prediction fallback when neither groups nor query_sizes is provided
    preds_fallback = model.predict(X)
    assert np.all(preds_fallback >= 1.0)
    assert np.all(preds_fallback <= len(X))
