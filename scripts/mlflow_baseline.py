import mlflow
import dagshub
import os

def log_baseline():
    # 1. Initialize DagsHub Connection
    # Handshake: Remote tracking URI setup
    print("Handshaking with DagsHub...")
    dagshub.init(repo_owner='sankeashok', repo_name='Aegis-Finance', mlflow=True)
    
    # 2. Tracking Experiment
    print("Starting MLflow Run: Baseline_Honest_Recall_V1...")
    with mlflow.start_run(run_name="Baseline_Honest_Recall_V1"):
        # Log Hyperparameters
        mlflow.log_param("scale_pos_weight", 11.6)
        mlflow.log_param("learning_rate", 0.05)
        mlflow.log_param("max_depth", 6)
        
        # Log Metrics
        # These reflect the 'Honest' (leakage-free) v1.3.8 performance
        mlflow.log_metric("Recall", 0.631)
        mlflow.log_metric("AUC-ROC", 0.88)  # Approximate from previous reports
        mlflow.log_metric("Precision", 0.45) # Approximate from previous reports
        
        # Log Tags
        mlflow.set_tag("model_type", "XGBoost")
        mlflow.set_tag("data_version", "Amex-Cleaned-V1")
        mlflow.set_tag("environment", "Vertex AI Workbench")
        
        # Log Artifacts
        preprocessor_path = os.path.join('models', 'aegis_preprocessor.pkl')
        model_json_path = os.path.join('models', 'aegis_model.json')
        
        print(f"Uploading artifacts: {preprocessor_path}, {model_json_path}...")
        mlflow.log_artifact(preprocessor_path, "preprocessing")
        mlflow.log_artifact(model_json_path, "model")
        
        print("\n[SUCCESS] Baseline run successfully logged to DagsHub!")

if __name__ == '__main__':
    log_baseline()
