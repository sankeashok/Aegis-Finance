import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from .schemas import LoanApplication, RiskResponse, RiskDriver
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
    version="1.2.0",
    lifespan=lifespan
)

# --- CORS Configuration ---
# Allow all origins for unified production deployment (frontend served from same container)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prometheus Metrics Instrumentation ---
# Exposes /metrics endpoint with HTTP request counts, latency histograms, etc.
Instrumentator().instrument(app).expose(app, endpoint="/metrics")



@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "Online", "engine_version": "1.3.8"}

def calculate_risk_drivers(data: dict) -> list:
    """
    Heuristic-based risk driver analysis.
    In V2.0, this would use SHAP values.
    """
    drivers = []
    
    # 1. Income Analysis
    income = data.get("income", 0)
    if income > 120000:
        drivers.append(RiskDriver(feature="Income", impact="Positive", score=0.8, description="Elite-tier annual earnings reduces default probability."))
    elif income < 45000:
        drivers.append(RiskDriver(feature="Income", impact="Negative", score=-0.6, description="Low income-to-debt ratio increases financial pressure."))

    # 2. Credit Score Analysis
    cs = data.get("credit_score", 0)
    if cs >= 750:
        drivers.append(RiskDriver(feature="Credit Score", impact="Positive", score=0.9, description="Super-prime credit history demonstrates superior repayment discipline."))
    elif cs < 620:
        drivers.append(RiskDriver(feature="Credit Score", impact="Negative", score=-0.8, description="Sub-prime credit score indicates historical repayment challenges."))

    # 3. Delinquency (D_39)
    d39 = data.get("D_39", 0)
    if d39 and d39 > 1.0:
        drivers.append(RiskDriver(feature="Delinquency Marker", impact="Negative", score=-0.7, description="Recent delinquency events (D_39) are high-risk indicators."))

    # 4. Categorical Stability (D_114)
    d114 = data.get("D_114")
    if d114 == 1.0:
        drivers.append(RiskDriver(feature="Stability Factor", impact="Positive", score=0.4, description="Consistent behavioral markers (D_114) suggest lower volatility."))

    return drivers


@app.post("/api/predict", response_model=RiskResponse, tags=["Inference"])
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

        # 3. Risk Intelligence (New Phase 2 Layer)
        risk_drivers = calculate_risk_drivers(data_dict)

        # 4. Business Tiering Logic
        if prob_default > 0.5:
            return RiskResponse(
                status="High Risk",
                probability=round(prob_default, 4),
                action="Manual Review Required",
                drivers=risk_drivers
            )
        else:
            return RiskResponse(
                status="Safe",
                probability=round(prob_default, 4),
                action="Approve",
                drivers=risk_drivers
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Failure: {str(e)}")


# --- Unified Static UI Hosting ---
# Mount the compiled React frontend (must exist in frontend/dist at runtime)
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

    # Catch-all for React Router navigation (returns index.html for all unnamed routes)
    @app.get("/{full_path:path}", tags=["UI"])
    async def serve_react_app(full_path: str):
        return FileResponse("frontend/dist/index.html")
