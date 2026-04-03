# 🛡️ Project Aegis-Finance

**A Production-Grade Risk Mitigation Engine**

Aegis-Finance is an AI-driven credit default prediction system designed for high-stakes financial institutions. It leverages advanced Gradient Boosting architectures to identify potential loan defaults with a focus on risk mitigation and high sensitivity to minority classes.

---

## 📊 Phase 3 Checkpoint: Risk Engine V1.0

The Council has officially signed off on the **Risk Engine V1.0**. By utilizing a custom-engineered sparsity handling pipeline and targeted class-weighting, we have achieved a high-recall baseline suitable for initial risk-tiering.

### 📈 Core Metrics
- **Recall (Sensitivity):** `44.23%`
- **Class Imbalance Handling:** `scale_pos_weight = 11.6`
- **Model Architecture:** XGBoost Gradient Boosting
- **Input Features:** Standard D_ (Delinquency), S_ (Spend), and P_ (Payment) indicators.

---

## 🏗️ System Architecture

1.  **Data Reliability Audit:** Automated scan for null variance and data drift.
2.  **Aegis Preprocessing Shield (`aegis_preprocessor.pkl`):** 
    -   Custom **Binary Masking** for high-sparsity features (>50% Nulls).
    -   Sentinel Value imputation (-999) for Gradient Boosting split purity.
3.  **XGBoost Risk Beast (`aegis_xgboost_v1.pkl`):** 
    -   High-recall optimized classifier.
    -   Early Stopping (50 rounds) for Green Compute / Carbon efficiency.

---

## 🛠️ Tech Stack & Environment
- **Core:** Python 3.10+, XGBoost, Scikit-Learn, Pandas.
- **Environment:** Local Isolated `.venv` with strict dependency pinning.
- **Inference:** Sklearn `Pipeline()` based serialization for zero-drift transition to deployment.

---

## 🚀 Future Roadmap: Phase 4
- **FastAPI Prototyping:** Exposing the Risk Engine via high-performance REST endpoints.
- **Pydantic Validation:** Enforcing strict data schemas for loan applications.
- **Monitoring:** Drift detection for the Delinquency (D_) variables.

---

*“Security is not a feature; it is an architectural foundation.” – The Engineering Council.*
