from src.config.settings import DATA_DIR, RAW_DATA_PATH, BASE_DIR
import os
from src.preprocessing.preprocessor import run_pipeline

def main():
    print('=================================================================')
    print('Platform-Independent E-Commerce Ranking Anomaly Detector')
    print('=================================================================')
    print('Initializing project environment...')
    print(f'Configured Data Directory: {DATA_DIR}')
    
    processed_path = os.path.join(DATA_DIR, 'processed', 'amazon_search_dataset.csv')
    print('Running preprocessing pipeline...')
    df_raw, df_clean = run_pipeline(RAW_DATA_PATH, processed_path)
    
    print(f'Raw data shape: {df_raw.shape}')
    print(f'Processed data shape: {df_clean.shape}')
    print(f'Processed data saved to: {processed_path}')
    
    from src.features.engineer import run_feature_engineering
    features_path = os.path.join(DATA_DIR, 'processed', 'features_dataset.csv')
    print('Running feature engineering pipeline...')
    df_clean, features_df = run_feature_engineering(processed_path, features_path)
    
    print(f'Features data shape: {features_df.shape}')
    print(f'Features dataset saved to: {features_path}')
    
    from src.models.expected_rank_model import run_modeling_pipeline
    predictions_path = os.path.join(DATA_DIR, 'processed', 'expected_rank_predictions_oof.csv')
    model_report_path = os.path.join(BASE_DIR, 'reports', 'expected_ranking_model_report.md')
    print('Running full-dataset grouped OOF expected-ranking ML model...')
    metrics, output_df = run_modeling_pipeline(features_path, predictions_path, model_report_path)
    
    print(f"OOF Baseline Metrics -> MAE: {metrics['oof']['mae']:.2f}, RMSE: {metrics['oof']['rmse']:.2f}, R2: {metrics['oof']['r2']:.2f}")
    print(f"Full-Dataset OOF predictions saved to: {predictions_path}")
    
    from src.analysis.peer_group_analysis import calculate_inconsistency
    inconsistency_path = os.path.join(DATA_DIR, 'processed', 'ranking_inconsistency.csv')
    inconsistency_report_path = os.path.join(BASE_DIR, 'reports', 'peer_group_analysis_report.md')
    print('Running peer-group analysis and calculating ranking inconsistency delta...')
    stats, inconsistency_df = calculate_inconsistency(predictions_path, inconsistency_path, inconsistency_report_path)
    
    print(f"Unique queries analyzed: {stats['unique_queries']}")
    print(f"Peer-group size -> Min: {stats['min_peer_group_size']}, Median: {stats['median_peer_group_size']}, Max: {stats['max_peer_group_size']}")
    print(f"Ranking Inconsistency dataset saved to: {inconsistency_path}")
    
    from src.analysis.suspiciousness_scoring import calculate_suspiciousness_score
    scores_path = os.path.join(DATA_DIR, 'processed', 'suspiciousness_scores.csv')
    scores_report_path = os.path.join(BASE_DIR, 'reports', 'suspiciousness_scoring_report.md')
    print('Running continuous suspiciousness scoring framework...')
    scores_df, top_10 = calculate_suspiciousness_score(inconsistency_path, scores_path, scores_report_path)
    
    print("Top 3 Highest-Scoring Inconsistency Candidates:")
    print(top_10.head(3)[['amazon_rank', 'expected_rank', 'rank_deviation', 'suspiciousness_score']].to_string(index=False))
    print(f"Suspiciousness Scores dataset saved to: {scores_path}")
    print('Status: SUCCESS - Modules and configurations are loading properly.')

if __name__ == '__main__':
    main()
