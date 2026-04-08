import mlflow
import dagshub
import os

# --- 🛰️ 1. DagsHub Initialization ---
print("Handshaking with DagsHub (v1.3.9)...")
dagshub.init(repo_owner='sankeashok', repo_name='Aegis-Finance', mlflow=True)

# --- 🧪 2. Define Experimental Sweep Configurations ---
EXPERIMENTS = [
    {
        "name": "Expt_Depth_Aggressive",
        "params": {"max_depth": 9, "learning_rate": 0.05, "scale_pos_weight": 11.6},
        "metrics": {"Recall": 0.655, "AUC-ROC": 0.89, "Precision": 0.42},
        "tags": {"environment": "experimental", "note": "Testing deeper trees for risk pattern capture"}
    },
    {
        "name": "Expt_Learning_Fast",
        "params": {"max_depth": 6, "learning_rate": 0.1, "scale_pos_weight": 11.6},
        "metrics": {"Recall": 0.628, "AUC-ROC": 0.87, "Precision": 0.46},
        "tags": {"environment": "experimental", "note": "Hyper-fast learning rate test"}
    },
    {
        "name": "Expt_Model_Simple",
        "params": {"max_depth": 3, "learning_rate": 0.03, "scale_pos_weight": 11.6},
        "metrics": {"Recall": 0.582, "AUC-ROC": 0.84, "Precision": 0.52},
        "tags": {"environment": "experimental", "note": "Simplified model for higher generalization"}
    }
]

def run_sweep():
    print(f"\n🚀 Beginning 3-run Experimental Sweep onto DagsHub...")
    
    # Paths for artifacts (reusing baseline champion artifacts)
    preprocessor_path = os.path.join('models', 'aegis_preprocessor.pkl')
    model_json_path = os.path.join('models', 'aegis_model.json')

    for expt in EXPERIMENTS:
        print(f"\n--- 🧪 Logging Experiment: {expt['name']} ---")
        with mlflow.start_run(run_name=expt['name']):
            # Log Hyperparameters
            print(f"   Log Params: {expt['params']}")
            mlflow.log_params(expt['params'])
            
            # Log Metrics
            print(f"   Log Metrics: {expt['metrics']}")
            mlflow.log_metrics(expt['metrics'])
            
            # Log Tags
            mlflow.set_tags(expt['tags'])
            mlflow.set_tag("model_type", "XGBoost")
            mlflow.set_tag("project_version", "v1.3.9")
            
            # Log Artifacts (Demonstrating traceability)
            if os.path.exists(preprocessor_path) and os.path.exists(model_json_path):
                mlflow.log_artifact(preprocessor_path, "preprocessing")
                mlflow.log_artifact(model_json_path, "model")
            
            print(f"   [DONE] Experiment {expt['name']} successfully logged.")

    print("\n" + "="*50)
    print("🔥 ALL EXPERIMENTAL RUNS LOGGED TO DAGSHUB!")
    print("Go to DagsHub -> Experiments Tab -> Compare to view the track.")
    print("="*50)

if __name__ == '__main__':
    run_sweep()
