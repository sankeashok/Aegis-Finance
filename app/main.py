import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from .schemas import LoanApplication, RiskResponse
from .transformers import SparseSentinelTransformer

# --- Lifecycle Management ---
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load artifacts on startup
    preprocessor_path = os.path.join("models", "aegis_preprocessor.pkl")
    model_path = os.path.join("models", "aegis_xgboost_v1.pkl")

    if not os.path.exists(preprocessor_path) or not os.path.exists(model_path):
        raise RuntimeError("Critical Error: Risk Engine artifacts (.pkl) missing from models/ directory.")

    models["preprocessor"] = joblib.load(preprocessor_path)
    models["risk_engine"] = joblib.load(model_path)
    print("--- Aegis-Finance Risk Engine: V1.0 Loaded and Online ---")

    yield
    # Clean up on shutdown
    models.clear()

# --- API Initialization ---
app = FastAPI(
    title="🛡️ Aegis-Finance Risk Gateway",
    description="Production API for real-time credit default risk tiering.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Prometheus Metrics Instrumentation ---
# Exposes /metrics endpoint with HTTP request counts, latency histograms, etc.
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "Online", "engine_version": "1.0.0"}


@app.post("/predict", response_model=RiskResponse, tags=["Inference"])
async def predict_risk(application: LoanApplication):
    """
    Evaluates a loan application and returns a risk-based status.

    - **Safe**: Probability of default < 0.50 → Approved
    - **High Risk**: Probability of default ≥ 0.50 → Manual Review Required
    """
    try:
        # Convert Pydantic model to DataFrame for transformation
        data_dict = application.model_dump()
        input_df = pd.DataFrame([data_dict])

        # 1. Pipeline Transformation
        processed_data = models["preprocessor"].transform(input_df)

        # 2. Risk Inference
        prob_default = float(models["risk_engine"].predict_proba(processed_data)[0][1])

        # 3. Business Tiering Logic
        if prob_default > 0.5:
            return RiskResponse(
                status="High Risk",
                probability=round(prob_default, 4),
                action="Manual Review Required"
            )
        else:
            return RiskResponse(
                status="Safe",
                probability=round(prob_default, 4),
                action="Approve"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Failure: {str(e)}")
