import os
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_curve, auc, recall_score
from xgboost import XGBClassifier
from sklearn.base import BaseEstimator, TransformerMixin

# Transformer definition must be present for joblib to load the preprocessor correctly
class SparseSentinelTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, sentinel_value=-999):
        self.sentinel_value = sentinel_value
        self.feature_names_in_ = None
        
    def fit(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            self.feature_names_in_ = X.columns.tolist()
        return self
        
    def transform(self, X, y=None):
        X_df = pd.DataFrame(X, columns=self.feature_names_in_).copy()
        cols = X_df.columns
        new_features = []
        for col in cols:
            mask = X_df[col].isna().astype(int)
            mask.name = f"{col}_is_missing"
            X_df[col] = X_df[col].fillna(self.sentinel_value)
            new_features.append(X_df[col])
            new_features.append(mask)
        return pd.concat(new_features, axis=1).values

def main():
    print("--- Mission: Phase 3 \u2013 Risk Engine Training ---\n")
    
    # 1. Paths
    data_path = os.path.join('data', 'raw', 'train_data.parquet')
    preprocessor_path = os.path.join('models', 'aegis_preprocessor.pkl')
    model_output_path = os.path.join('models', 'aegis_xgboost_v1.pkl')
    temp_dir = '_temp'
    os.makedirs(temp_dir, exist_ok=True)

    # 2. Load Data & Preprocessor
    print(f"Loading data from {data_path}...")
    df = next(pq.ParquetFile(data_path).iter_batches(batch_size=100000)).to_pandas()
    X = df.drop(columns=['target', 'customer_id'])
    y = df['target']
    
    print(f"Loading preprocessor from {preprocessor_path}...")
    preprocessor = joblib.load(preprocessor_path)
    X_processed = preprocessor.transform(X)
    
    # 3. Split Data (80/20)
    X_train, X_val, y_train, y_val = train_test_split(X_processed, y, test_size=0.2, random_state=42, stratify=y)

    # 4. Train Risk Engine (XGBoost)
    # Target: Maximize Recall, scale_pos_weight=11.6
    print("\nTraining XGBoost Risk Engine (scale_pos_weight=11.6)...")
    risk_engine = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        scale_pos_weight=11.6, 
        random_state=42,
        eval_metric='logloss'
    )
    risk_engine.fit(X_train, y_train)
    
    # 5. Evaluation
    y_pred = risk_engine.predict(X_val)
    y_prob = risk_engine.predict_proba(X_val)[:, 1]
    
    recall = recall_score(y_val, y_pred)
    print("\n===========================================")
    print(f"   PROJECT AEGIS RECALL SCORE: {recall:.4f}")
    print("===========================================\n")
    
    # 6. Artifacts (Plots)
    # Confusion Matrix
    cm = confusion_matrix(y_val, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['No Default', 'Default'], yticklabels=['No Default', 'Default'])
    plt.title('Aegis-Finance: Risk Confusion Matrix')
    plt.ylabel('Actual Relationship')
    plt.xlabel('Predicted Risk')
    plt.savefig(os.path.join(temp_dir, 'confusion_matrix_v1.png'), bbox_inches='tight')
    plt.close()
    
    # ROC-AUC
    fpr, tpr, _ = roc_curve(y_val, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(6,5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Aegis-Finance: Risk ROC-AUC')
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(temp_dir, 'roc_auc_v1.png'), bbox_inches='tight')
    plt.close()
    
    # 7. Save Model
    joblib.dump(risk_engine, model_output_path)
    print(f"[Success] Saved Risk Model to: {model_output_path}")

if __name__ == '__main__':
    main()
