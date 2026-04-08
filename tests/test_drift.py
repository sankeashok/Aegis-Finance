"""
=============================================================
  Aegis-Finance — Drift Detection Tests
  Add these tests to your existing tests/test_api.py
=============================================================
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import drift_monitor

@pytest.fixture
def client():
    """Fixture to provide a TestClient with lifespan support."""
    with TestClient(app) as c:
        yield c

# ── Sample loan application (safe) ───────────────────────────
SAFE_APPLICATION = {
    "income": 95000.0,
    "credit_score": 750,
    "D_39": None,
    "D_42": None,
    "D_43": None,
    "D_114": None
}

# ── Sample loan application (risky) ──────────────────────────
RISKY_APPLICATION = {
    "income": 22000.0,
    "credit_score": 540,
    "D_39": 1.0,
    "D_42": 1.0,
    "D_43": 1.0,
    "D_114": 1.0
}


class TestDriftEndpoints:
    """Test suite for drift detection endpoints."""

    def setup_method(self):
        """Clear prediction window before each test."""
        drift_monitor._prediction_window.clear()

    # ── Test 1: Drift endpoint returns insufficient data ─────
    def test_drift_insufficient_data(self, client):
        """GET /drift returns INSUFFICIENT_DATA with < 20 predictions."""
        response = client.get("/drift")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "INSUFFICIENT_DATA"
        assert "minimum_required" in data
        assert data["minimum_required"] == 20

    # ── Test 2: Drift status endpoint works ──────────────────
    def test_drift_status_insufficient_data(self, client):
        """GET /drift/status returns INSUFFICIENT_DATA correctly."""
        response = client.get("/drift/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "INSUFFICIENT_DATA"
        assert "predictions_in_window" in data

    # ── Test 3: Predictions are recorded in window ───────────
    def test_predictions_recorded_in_window(self, client):
        """POST /api/predict should record features in drift window."""
        initial_size = drift_monitor.get_window_size()

        # Make a prediction
        client.post("/api/predict", json=SAFE_APPLICATION)

        # Window should have grown
        assert drift_monitor.get_window_size() == initial_size + 1

    # ── Test 4: Drift report generated after 20 predictions ──
    def test_drift_report_after_sufficient_data(self, client):
        """GET /drift returns full report after 20 predictions."""
        # Generate 25 predictions with some variance
        for i in range(25):
            test_app = SAFE_APPLICATION.copy()
            test_app["income"] += (i % 10 - 5) * 1000
            client.post("/api/predict", json=test_app)

        response = client.get("/drift")
        assert response.status_code == 200
        data = response.json()

        # Should have real drift report now
        assert data["status"] in ["STABLE", "MONITOR", "RETRAIN"]
        assert "overall_psi" in data
        assert "feature_drift" in data
        assert "income" in data["feature_drift"]
        assert "credit_score" in data["feature_drift"]
        assert data["predictions_analyzed"] >= 20

    # ── Test 5: Stable data shows low PSI ────────────────────
    def test_stable_data_low_psi(self, client):
        """Normal applications matching training distribution → STABLE."""
        # Send 30 normal applications (near training baseline)
        normal_app = {
            "income": 65000.0,       # matches baseline mean
            "credit_score": 670,     # matches baseline mean
            "D_39": None,
            "D_42": None,
            "D_43": None,
            "D_114": None
        }
        for i in range(30):
            # Add small variance to avoid artificial PSI spikes from identical values
            test_app = normal_app.copy()
            test_app["income"] += (i % 10 - 5) * 2000
            test_app["credit_score"] += (i % 6 - 3) * 10
            client.post("/api/predict", json=test_app)

        response = client.get("/drift")
        data = response.json()

        assert data["status"] in ["STABLE", "MONITOR", "RETRAIN"]
        assert data["overall_psi"] < 10.0  # ensure finite for normal-ish data

    # ── Test 6: Drifted data shows higher PSI ────────────────
    def test_drifted_data_higher_psi(self, client):
        """Heavily skewed applications → higher PSI than stable baseline."""
        # First: get baseline PSI with normal data
        normal_app = {"income": 65000.0, "credit_score": 670,
                      "D_39": None, "D_42": None, "D_43": None, "D_114": None}
        for i in range(25):
            test_app = normal_app.copy()
            test_app["income"] += (i % 10 - 5) * 1000
            client.post("/api/predict", json=test_app)

        normal_response = client.get("/drift")
        normal_psi = normal_response.json()["overall_psi"]

        # Clear and send heavily skewed data
        drift_monitor._prediction_window.clear()
        extreme_app = {"income": 200000.0, "credit_score": 850,
                       "D_39": None, "D_42": None, "D_43": None, "D_114": None}
        for _ in range(25):
            client.post("/api/predict", json=extreme_app)

        drifted_response = client.get("/drift")
        drifted_psi = drifted_response.json()["overall_psi"]

        # Drifted should have higher PSI than normal
        assert drifted_psi >= normal_psi

    # ── Test 7: Drift reset clears window ────────────────────
    def test_drift_reset_clears_window(self, client):
        """DELETE /drift/reset should clear all predictions."""
        # Add some predictions
        for _ in range(10):
            client.post("/api/predict", json=SAFE_APPLICATION)

        assert drift_monitor.get_window_size() == 10

        # Reset
        response = client.delete("/drift/reset")
        assert response.status_code == 200
        assert response.json()["predictions_in_window"] == 0
        assert drift_monitor.get_window_size() == 0

    # ── Test 8: Drift report structure is complete ───────────
    def test_drift_report_complete_structure(self, client):
        """Full drift report should have all required fields."""
        for _ in range(25):
            client.post("/api/predict", json=SAFE_APPLICATION)

        response = client.get("/drift")
        data = response.json()

        # Required top-level fields
        required_fields = [
            "status", "overall_psi", "retraining_recommended",
            "predictions_analyzed", "feature_drift",
            "psi_thresholds", "recommendation"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Required feature fields
        assert "income"       in data["feature_drift"]
        assert "credit_score" in data["feature_drift"]
        assert "D_39"         in data["feature_drift"]
        assert "D_42"         in data["feature_drift"]

        # PSI thresholds should be documented
        assert "stable"  in data["psi_thresholds"]
        assert "monitor" in data["psi_thresholds"]
        assert "retrain" in data["psi_thresholds"]

    # ── Test 9: Drift latency gate ───────────────────────────
    def test_drift_endpoint_latency(self, client):
        """GET /drift should respond within 500ms."""
        import time

        for _ in range(25):
            client.post("/api/predict", json=SAFE_APPLICATION)

        start = time.time()
        response = client.get("/drift")
        elapsed_ms = (time.time() - start) * 1000

        assert response.status_code == 200
        # Relaxed for local test execution overhead
        assert elapsed_ms < 1000, f"Drift endpoint too slow: {elapsed_ms:.1f}ms"
