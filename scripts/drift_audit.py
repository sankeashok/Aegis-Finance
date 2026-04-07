import pandas as pd
import numpy as np
import mlflow
import dagshub
import os
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset

# --- 🛰️ 1. DagsHub Initialization ---
print("Handshaking with DagsHub for Drift Monitoring...")
dagshub.init(repo_owner='sankeashok', repo_name='Aegis-Finance', mlflow=True)

# --- 🧬 2. Synthetic Data Generation (Reference vs Current) ---
def generate_synthetic_data(n_samples=2000, drift=False):
    np.random.seed(42 if not drift else 24)
    
    # Feature: Income
    income_mean = 60000 if not drift else 48000  # 20% drop in drifted data
    income = np.random.normal(income_mean, 15000, n_samples)
    
    # Feature: Delinquency (D_39)
    d39_mean = 0.3 if not drift else 0.55        # Significant shift in delinquency
    d39 = np.random.normal(d39_mean, 0.2, n_samples)
    
    # Target: Risk Score (Simulated)
    # Reference has lower risk; Drifted has higher risk
    base_risk = 0.2 if not drift else 0.45
    target = (base_risk + (0.3 * d39) - (0.1 * (income/100000))) + np.random.normal(0, 0.05, n_samples)
    target = np.clip(target, 0, 1)
    
    df = pd.DataFrame({
        'income': income,
        'D_39': d39,
        'target': target
    })
    return df

print("Generating Reference (Training) and Current (Production) datasets...")
reference_data = generate_synthetic_data(n_samples=2000, drift=False)
current_data = generate_synthetic_data(n_samples=2000, drift=True)

# --- 📊 3. Evidently Drift Audit ---
print("Executing Automated Drift Audit (Evidently AI)...")
drift_report = Report(metrics=[
    DataDriftPreset(),
    TargetDriftPreset()
])

drift_report.run(reference_data=reference_data, current_data=current_data)

# --- 🛰️ 4. MLflow Logging ---
report_html_path = "drift_report.html"
drift_report.save_html(report_html_path)

print(f"\n🚀 Logging Drift Audit to DagsHub...")
with mlflow.start_run(run_name="Production_Drift_Audit_V1"):
    # Log summary tags
    mlflow.set_tag("module", "Monitoring")
    mlflow.set_tag("audit_type", "Data_and_Target_Drift")
    mlflow.set_tag("status", "Drift_Detected") # We purposefully drifted the data
    
    # Log the interactive report
    mlflow.log_artifact(report_html_path, artifact_path="reports")
    
    print(f"   [SUCCESS] Drift report logged to DagsHub!")
    print(f"   View it in artifacts -> reports/drift_report.html")

# Cleanup local file
if os.path.exists(report_html_path):
    os.remove(report_html_path)

print("\n" + "="*50)
print("🔥 AUTOMATED DRIFT DETECTION COMPLETED!")
print("="*50)
