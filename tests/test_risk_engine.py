import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

# --- Risk Engine Quality Gates ---

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_risk_integrity_gate(client):
    """
    MISSION SPEC: Integrity Test
    Ensure a payload with 'zero income' and 'high delinquency' triggers a 'High Risk' status.
    """
    # Using a case specifically identified in the model's high-risk distribution
    payload = {
        "income": 0.0,
        "credit_score": 300,
        "D_39": 25.0,   # Extreme delinquency
        "D_42": 1.0, 
        "D_43": 1.0, 
        "D_114": 0.0
    }
    
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # We assert High Risk. If this fails, the model is not properly distinguishing extremal risk cases.
    assert data["status"] == "High Risk", f"INTEGRITY FAIL: Extreme risk payload returned {data['status']} (Prob: {data['probability']})"

def test_risk_latency_gate(client):
    """
    MISSION SPEC: Latency Test
    Verify that the /predict response is under 200ms using precise timers.
    """
    payload = {
        "income": 85000.0,
        "credit_score": 720,
        "D_39": 1.0,
        "D_42": None,
        "D_43": None,
        "D_114": 1.0
    }
    
    # Measure latency over 5 iterations to get a stable average
    latencies = []
    for _ in range(5):
        start = time.perf_counter()
        client.post("/api/predict", json=payload)
        latencies.append((time.perf_counter() - start) * 1000) # ms
        
    avg_latency = sum(latencies) / len(latencies)
    print(f"\nAverage Inference Latency: {avg_latency:.2f}ms")
    
    assert avg_latency < 200, f"LATENCY FAIL: Average response time ({avg_latency:.2f}ms) exceeds 200ms SLA."

def test_model_artifact_loading(client):
    """
    Confirms the server successfully context-loaded models/aegis_*.pkl artifacts.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["engine_version"] == "1.3.8"
    assert response.json()["status"] == "Online"
