import os
import tempfile
import json
import sys
import logging
import asyncio
from typing import List
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("flagrank-api")

# Add project root and research_framework to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
rf_dir = os.path.join(root_dir, 'research_framework')
if rf_dir not in sys.path:
    sys.path.insert(0, rf_dir)

from src.preprocessing.preprocessor import run_pipeline
from src.features.engineer import run_feature_engineering
from src.models.expected_rank_model import run_modeling_pipeline
from src.analysis.peer_group_analysis import calculate_inconsistency
from src.analysis.suspiciousness_scoring import calculate_suspiciousness_score

app = FastAPI(
    title="FlagRank Research API",
    description="Backend API for empirical search ranking anomaly detection",
    version="1.0.0"
)

# Configurable CORS
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True if allow_origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload limits
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

REQUIRED_COLUMNS = [
    'query', 'amazon_rank', 'price', 'original_price', 'rating', 
    'total_reviews', 'brand', 'product_type', 'color', 'title', 
    'description', 'discounted', 'savings_percent', 'sponsored'
]

@app.get("/")
async def root():
    return {
        "service": "FlagRank Research API",
        "status": "operational",
        "health_check": "/api/health",
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "flagrank-api",
        "version": "1.0.0"
    }

@app.post("/api/analyze")
async def analyze_dataset(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are supported.")
        
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413, 
            detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE_MB}MB."
        )

    async def run_analysis():
        temp_dir_obj = tempfile.TemporaryDirectory()
        try:
            temp_dir = temp_dir_obj.name
            raw_path = os.path.join(temp_dir, 'raw.csv')
            processed_path = os.path.join(temp_dir, 'processed.csv')
            features_path = os.path.join(temp_dir, 'features.csv')
            predictions_path = os.path.join(temp_dir, 'predictions.csv')
            model_report_path = os.path.join(temp_dir, 'model_report.md')
            inconsistency_path = os.path.join(temp_dir, 'inconsistency.csv')
            inconsistency_report_path = os.path.join(temp_dir, 'inconsistency_report.md')
            scores_path = os.path.join(temp_dir, 'scores.csv')
            scores_report_path = os.path.join(temp_dir, 'scores_report.md')
            
            with open(raw_path, 'wb') as f:
                f.write(content)
                
            yield json.dumps({"status": "Validating dataset"}) + "\n"
            await asyncio.sleep(0.05)
            
            try:
                df = pd.read_csv(raw_path)
            except Exception as e:
                yield json.dumps({"error": f"Invalid CSV format: {str(e)}"}) + "\n"
                return
                
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                yield json.dumps({"error": f"Missing required columns: {', '.join(missing_cols)}"}) + "\n"
                return
                
            if len(df) == 0:
                yield json.dumps({"error": "Dataset is empty."}) + "\n"
                return
                
            if 'asin' not in df.columns:
                df['asin'] = [f"ASIN_{i}" for i in range(len(df))]
                df.to_csv(raw_path, index=False)
            
            yield json.dumps({"status": "Preprocessing data"}) + "\n"
            await asyncio.sleep(0.05)
            df_raw, df_clean = run_pipeline(raw_path, processed_path)
            
            unique_queries = df_clean['query'].nunique()
            if unique_queries < 5:
                yield json.dumps({
                    "error": f"Insufficient unique queries ({unique_queries}) for 5-fold cross-validation. At least 5 unique queries are required."
                }) + "\n"
                return
            
            yield json.dumps({"status": "Building features"}) + "\n"
            await asyncio.sleep(0.05)
            df_clean, features_df = run_feature_engineering(processed_path, features_path)
            
            yield json.dumps({"status": "Training/evaluating ranking model"}) + "\n"
            await asyncio.sleep(0.05)
            metrics, output_df = run_modeling_pipeline(features_path, predictions_path, model_report_path)
            
            yield json.dumps({"status": "Calculating ranking inconsistency"}) + "\n"
            await asyncio.sleep(0.05)
            stats, inconsistency_df = calculate_inconsistency(predictions_path, inconsistency_path, inconsistency_report_path)
            
            yield json.dumps({"status": "Generating suspiciousness scores"}) + "\n"
            await asyncio.sleep(0.05)
            scores_df, top_10 = calculate_suspiciousness_score(inconsistency_path, scores_path, scores_report_path)
            
            yield json.dumps({"status": "Analysis complete"}) + "\n"
            
            df_final = pd.read_csv(scores_path)
            df_final = df_final.replace([float('inf'), float('-inf')], None)
            df_final = df_final.where(pd.notnull(df_final), None)

            # Merge original product metadata back (title, thumbnail, brand, url, product_type, color)
            # These are explanatory and presentation attributes needed by the frontend
            meta_cols = ['asin', 'query', 'title', 'thumbnail', 'brand', 'url', 'product_type', 'color']
            df_processed = pd.read_csv(processed_path)
            available_meta = [c for c in meta_cols if c in df_processed.columns]
            df_meta = df_processed[available_meta].drop_duplicates(subset=['asin', 'query'])

            if 'asin' in df_final.columns and 'query' in df_final.columns:
                cols_to_drop = [c for c in available_meta if c not in ('asin', 'query') and c in df_final.columns]
                df_final = df_final.drop(columns=cols_to_drop, errors='ignore')
                df_final = df_final.merge(df_meta, on=['asin', 'query'], how='left')

            data = df_final.to_dict(orient='records')

            metadata = {
                'total_products': len(df_final),
                'unique_queries': int(df_final['query'].nunique()),
                'unique_asins': int(df_final['asin'].nunique()),
                'rank_min': float(df_final['amazon_rank'].min()),
                'rank_max': float(df_final['amazon_rank'].max()),
                'oof_mae': float(metrics['oof']['mae']),
                'oof_rmse': float(metrics['oof']['rmse']),
                'oof_r2': float(metrics['oof']['r2'])
            }
            
            yield json.dumps({"result": {"data": data, "metadata": metadata}}) + "\n"
            
        except Exception as e:
            logger.exception("Pipeline execution failed")
            yield json.dumps({"error": f"Internal pipeline error: {str(e)}"}) + "\n"
        finally:
            temp_dir_obj.cleanup()

    return StreamingResponse(run_analysis(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
