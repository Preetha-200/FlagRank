import io
import json
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from api.server import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert data.get("service") == "flagrank-api"

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "operational"
    assert "/api/health" in data.get("health_check", "")

def test_analyze_rejects_non_csv(client):
    response = client.post(
        "/api/analyze",
        files={"file": ("test.txt", io.BytesIO(b"hello world"), "text/plain")}
    )
    assert response.status_code == 400
    assert "Only CSV files" in response.json().get("detail", "")

def test_analyze_rejects_empty_file(client):
    response = client.post(
        "/api/analyze",
        files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    )
    assert response.status_code == 400
    assert "empty" in response.json().get("detail", "").lower()

def test_analyze_valid_dataset_streaming(client):
    # Load 5 queries from the real dataset to validate the full pipeline execution
    df = pd.read_csv("research_framework/data/raw/amazon_search_dataset.csv")
    sample_queries = df["query"].unique()[:5]
    df_sample = df[df["query"].isin(sample_queries)]
    csv_bytes = df_sample.to_csv(index=False).encode("utf-8")

    response = client.post(
        "/api/analyze",
        files={"file": ("sample.csv", io.BytesIO(csv_bytes), "text/csv")}
    )
    assert response.status_code == 200
    
    # Verify NDJSON streaming messages
    lines = [json.loads(line) for line in response.text.strip().split("\n") if line]
    assert len(lines) >= 2
    
    # Check that intermediate status messages were streamed
    statuses = [msg.get("status") for msg in lines if "status" in msg]
    assert "Preprocessing data" in statuses
    assert "Generating suspiciousness scores" in statuses
    
    # Check that final message contains the result payload
    final_message = lines[-1]
    assert "result" in final_message
    result = final_message["result"]
    assert "data" in result
    assert "metadata" in result
    assert len(result["data"]) == len(df_sample)
    
    # Verify product metadata retention for display
    sample_row = result["data"][0]
    assert "expected_rank" in sample_row
    assert "suspiciousness_score" in sample_row
    assert "title" in sample_row
    assert "thumbnail" in sample_row
    assert "brand" in sample_row
