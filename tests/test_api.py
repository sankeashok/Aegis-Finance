import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

# --- API Test Suite Configuration ---

@pytest.fixture
def client():
    """
    Fixture to provide a TestClient that correctly triggers the FastAPI lifespan (model loading).
    """
    with TestClient(app) as c:
        yield c

# --- Unit Tests: Schema Validation ---

def test_health_check(client):
    """
    Verifies that the API gateway is online.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Online"

def test_predict_invalid_schema(client):
    """
    Verifies that the API correctly rejects malformed JSON payloads (422 Unprocessed Entity).
    """
    # Missing 'income' field
    payload = {
        "credit_score": 720,
        "D_39": 1.0,
        "D_42": None,
        "D_43": None,
        "D_114": 1.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

# --- Integration Tests: Business Risk Logic ---

@pytest.mark.parametrize("income, credit_score, D_39, D_42, D_43, D_114, expected_status", [
    # Scenario A: Safe (Baseline test case)
    (85000.0, 720, 1.0, None, None, 1.0, "Safe"),
    # Scenario B: High Risk (Aligned with gen_robust logic: income < 40k AND credit < 500)
    (25000.0, 450, 6.0, 0.8, 0.8, 0.0, "High Risk")
])
def test_predict_risk_logic(client, income, credit_score, D_39, D_42, D_43, D_114, expected_status):
    """
    Validates that the inference engine correctly tiers applications based on the XGBoost model.
    """
    payload = {
        "income": income,
        "credit_score": credit_score,
        "D_39": D_39,
        "D_42": D_42,
        "D_43": D_43,
        "D_114": D_114
    }
    
    # Measure Latency (SLA Check)
    start_time = time.perf_counter()
    response = client.post("/predict", json=payload)
    latency = (time.perf_counter() - start_time) * 1000  # ms
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == expected_status, f"Expected {expected_status} for {payload}, but got {data['status']} (Prob: {data['probability']})"
    
    # Financial SLA Constraint: Every inference must be < 200ms
    assert latency < 200, f"Inference Latency ({latency:.2f}ms) exceeds SLA of 200ms"

# --- Edge Cases ---

def test_predict_empty_optional_fields(client):
    """
    Verifies that the API handles applications with null optional delinquency markers.
    """
    payload = {
        "income": 85000.0,
        "credit_score": 700
        # Other D_ fields are optional and default to None/NaN
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "status" in response.json()
