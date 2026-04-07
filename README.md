# 🛡️ Project Aegis-Finance

<div align="center">

![CI/CD](https://github.com/sankeashok/Aegis-Finance/actions/workflows/ci-cd.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![XGBoost](https://img.shields.io/badge/XGBoost-2.1.4-orange)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.3.9-brightgreen)

**🛡️ Aegis-Finance: Premium Risk Gateway**

*Real-time loan risk tiering powered by XGBoost, served via a unified Vite-React + FastAPI production container.*

🔗 **[Live Production Dashboard](https://aegis-finance-api-yryvmgxkoq-uc.a.run.app)**

---

## 🎬 Visual Showreel

<div align="center">
  <p><b>Animated Dashboard Demo (Vite-React + FastAPI)</b></p>
  <img src="docs/assets/dashboard_demo.webp" width="800px" alt="Dashboard Demo">
</div>

<br/>

<div align="center">
  <table border="0">
    <tr>
      <td align="center"><b>Experiment Tracking (DagsHub)</b></td>
      <td align="center"><b>Production Metrics (Prometheus)</b></td>
    </tr>
    <tr>
      <td><img src="docs/assets/dagshub_experiments.png" width="400px" alt="DagsHub Tracking"></td>
      <td><img src="docs/assets/prometheus_metrics.png" width="400px" alt="Prometheus Metrics"></td>
    </tr>
  </table>
</div>

---

## 📋 Overview

**Aegis-Finance** is a production-grade MLOps ecosystem. It features a high-performance XGBoost inference engine and a **Premium React Frontend ("Obsidian Emerald")** designed for real-time risk assessment and loan tiering.

The system is engineered for **financial-grade standards**:
- 🎨 **Premium UI**: Dual-theme (Dark/Light) React dashboard with animated risk gauges.
- ⚡ **Unified Gateway**: Single-container architecture serving both UI and API.
- ✅ **Sub-200ms inference**: Scalable XGBoost inference via FastAPI.
- ✅ **Automated CI/CD**: 3-stage GitHub Actions → GAR → Cloud Run pipeline.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Aegis-Finance MLOps Pipeline                  │
├──────────────┬───────────────┬───────────────┬───────────────────┤
│  Phase 1-2   │   Phase 3     │   Phase 4     │   Phase 5-7       │
│  Data +      │   XGBoost     │   FastAPI     │   Docker + CI/CD  │
│  Features    │   Training    │   Gateway     │   + Monitoring    │
└──────┬───────┴──────┬────────┴──────┬────────┴─────────┬─────────┘
       │              │               │                  │
 raw parquet   aegis_xgboost    POST /predict      Prometheus
  + EDA        _v1.pkl          JSON → Risk        /metrics
               + preprocessor   tier + prob        + GHCR image
```

### Request Lifecycle
```
Client POST /predict (LoanApplication JSON)
       │
       ▼
┌─────────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│ Pydantic Schema │───▶│ SparseSentinel        │───▶│ XGBoost Predict  │
│ Validation      │    │ Transformer + Scaler  │    │ prob_default →   │
│ (422 on fail)   │    │ (aegis_preprocessor)  │    │ Safe / High Risk │
└─────────────────┘    └──────────────────────┘    └──────────────────┘
```

---

## 📊 Model Performance & Integrity

### ⚖️ The Versioning Story
To demonstrate professional model governance, Aegis-Finance maintains a clear lineage between early research and production stability:

| Version | Status | Recall | Note |
|---|---|---|---|
| **v0.1** | 🛑 Retired | 99.9% | **Leaked**: Deterministic injected extremes identified during audit. |
| **v1.0 (Current)** | ✅ Production | **63.1%** | **Honest Baseline**: Leakage-free probabilistic log-odds generator. |

### 📈 Current Engine Benchmarks (v1.3.9)
| Metric | Value |
|---|---|
| **Model** | XGBoost Gradient Boosting |
| **Recall** | **63.1%** |
| **Inference Latency** | **~12ms** per request |
| **Throughput (batch)** | ~53 req/sec |
| **Training Default Rate** | ~3.9% (realistic imbalance) |
| **Scale Pos Weight** | Auto-computed from class ratio |

> **Integrity Guarantee:** The V1.0 model was recalibrated to prioritize **System Integrity** over "vanity metrics." By auditing the structural data leak in the v0.1 prototype, we established a reliability-first baseline suitable for financial risk scoring.

---

## 🚀 Quick Start

### Option A: Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/sankeashok/Aegis-Finance.git
cd Aegis-Finance

# Start the Risk Gateway
docker-compose up -d

# Verify it's running
curl http://localhost:8000/
# → {"status":"Online","engine_version":"1.3.9"}
```

### Option B: Local Python
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📡 API Reference

### `GET /`
Health check — confirms the Risk Engine is loaded and online.

**Response:**
```json
{"status": "Online", "engine_version": "1.3.9"}
```

### `POST /api/predict`
Evaluates a loan application and returns a risk tier.

**Request Body:**
```json
{
  "income": 85000.0,
  "credit_score": 720,
  "D_39": 1.0,
  "D_42": null,
  "D_43": null,
  "D_114": 1.0
}
```

**Response:**
```json
{
  "status": "Safe",
  "probability": 0.3862,
  "action": "Approve"
}
```

| Status | Threshold | Action |
|---|---|---|
| `Safe` | prob < 0.50 | `Approve` |
| `High Risk` | prob ≥ 0.50 | `Manual Review Required` |

### `GET /metrics`
Prometheus metrics endpoint — exposes request counts, latency histograms, and process metrics.

### `GET /docs`
Interactive Swagger UI for the full API specification.

---

## 🔬 Running Tests

```bash
# Run full Quality Gate suite
pytest tests/ -v

# With coverage report
pytest --cov=app --cov-report=term-missing tests/
```

**Test Suite (8/8 Pass):**
| Test | Description |
|---|---|
| `test_health_check` | API gateway is online |
| `test_predict_invalid_schema` | 422 rejection of malformed payloads |
| `test_predict_risk_logic[Safe]` | High-income applicant → Safe |
| `test_predict_risk_logic[High Risk]` | Low-income + delinquency → High Risk |
| `test_predict_empty_optional_fields` | Handles null D_ features gracefully |
| `test_risk_integrity_gate` | Extreme risk profile → High Risk |
| `test_risk_latency_gate` | Inference < 200ms SLA |
| `test_model_artifact_loading` | Both `.pkl` artifacts loaded on startup |

---

## 🐳 Docker

```bash
# Build image
docker build -t aegis-finance-api:latest .

# Run container (with model volume)
docker-compose up -d

# Check container health
docker ps --filter "name=aegis-risk-gateway"

# Tail logs
docker logs aegis-risk-gateway -f

# Tear down
docker-compose down
```

**Image details:**
- Base: `python:3.11-slim` (multi-stage build)
- Runtime user: `appuser` (non-root, security best practice)
- Health check: pings `/` every 30s
- Published to: `us-central1-docker.pkg.dev` (Google Artifact Registry)

---

## ⚙️ CI/CD Pipeline

Every push to `main` triggers the GitHub Actions pipeline:

```
Push to main
    │
    ▼
🔬 Quality Gate (pytest)       ~1 min
    • Python 3.11 setup
    • Verify .pkl artifacts exist
    • Run pytest (8 tests, must all pass)
    │
    ▼ (only on pass)
🐳 Build & Push Docker Image   ~5 min
    • Multi-stage docker build
    • Tag: latest + sha-<commit>
    • Push to Google Artifact Registry (GAR)
    │
    ▼
🚀 Automated Deployment        ~3 min
    • Deploy to Google Cloud Run
    • Native OIDC Authentication

---

## 🧪 Experiment Tracking & Drift Monitoring (DagsHub + MLflow)

Aegis-Finance utilizes **DagsHub** and **MLflow** for robust experiment tracking and **proactive drift detection**. This ensures full lineage from training research to production observability.

### 🕵️‍♂️ Automated Drift Detection (Evidently AI)
To prevent model decay, Aegis-Finance implements automated Data and Target drift audits using **Evidently AI**. This monitors shifts in input distributions (e.g., changing delinquency patterns) vs. the training baseline.

- **Reports**: Interactive HTML dashboards showing P-values and drift scores.
- **Lineage**: Drift reports are automatically logged to **MLflow** as artifacts.
- **Experiment Board**: [View Latest Monitoring Runs](https://dagshub.com/sankeashok/Aegis-Finance.mlflow/#/experiments/0)

### 📈 Primary Baseline (v1.3.9)
- **Run Name**: `Baseline_Honest_Recall_V1`
- **Recall (Honest)**: `0.631`
- **Hyperparams**: `scale_pos_weight=11.6`, `learning_rate=0.05`, `max_depth=6`

---

## 📁 Project Structure

```
Aegis-Finance/
├── app/
│   ├── main.py              # FastAPI app + Prometheus instrumentation
│   ├── schemas.py           # Pydantic request/response models
│   ├── transformers.py      # SparseSentinelTransformer (custom sklearn)
│   └── batch_processor.py   # Parallel batch inference via httpx
├── models/
│   ├── aegis_xgboost_v1.pkl    # Trained XGBoost classifier
│   └── aegis_preprocessor.pkl  # Fitted sklearn ColumnTransformer
├── tests/
│   ├── test_api.py          # Schema validation + integration tests
│   └── test_risk_engine.py  # Integrity gate + latency SLA tests
├── .github/workflows/
│   └── ci-cd.yml            # GitHub Actions: pytest → Docker → GAR → Cloud Run
├── Dockerfile               # Multi-stage production image
├── docker-compose.yml       # Local orchestration
├── recalibrate_data.py      # Probabilistic data generator (leakage-free)
├── 02_Feature_Engineering.py
├── 03_Risk_Engine_Training.py
└── scripts/
    └── mlflow_baseline.py   # Remote DagsHub experiment tracking
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **ML Model** | XGBoost 2.1.4 |
| **Preprocessing** | Scikit-Learn 1.6.1 (ColumnTransformer) |
| **API** | FastAPI 0.115 + Uvicorn |
| **Validation** | Pydantic V2 |
| **Monitoring** | Prometheus FastAPI Instrumentator |
| **Testing** | Pytest + pytest-cov |
| **Batch Inference** | httpx AsyncClient |
| **Container** | Docker (multi-stage, python:3.11-slim) |
| **Orchestration** | Docker Compose |
| **CI/CD** | GitHub Actions → GAR → Cloud Run |
| **Tracking** | MLflow → DagsHub |
| **Language** | Python 3.11 |

---

## 🌱 Green Champion

By parallelizing batch inference requests via `httpx.AsyncClient`, Aegis-Finance reduces the total active-compute window by **~81%** compared to sequential processing — minimizing idle CPU cycles and energy consumption per inference.

---

*"Security is not a feature; it is an architectural foundation." – The Engineering Council.*
