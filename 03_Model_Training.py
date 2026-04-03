import os
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import confusion_matrix, roc_curve, auc, recall_score, precision_score
from xgboost import XGBClassifier
from sklearn.base import BaseEstimator, TransformerMixin

# Define transformer here so joblib loader resolves the definition exactly where it expects module __main__
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
    print("--- Phase 3: Model Training & Risk Evaluation ---\n")
    
    # 1. Load Data
    data_path = os.path.join('data', 'raw', 'train_data.parquet')
    df = next(pq.ParquetFile(data_path).iter_batches(batch_size=100000)).to_pandas()
    X = df.drop(columns=['target', 'customer_id'])
    y = df['target']
    
    # 2. Load Preprocessor
    preprocessor_path = os.path.join('models', 'aegis_preprocessor.pkl')
    preprocessor = joblib.load(preprocessor_path)
    X_processed = preprocessor.transform(X)
    
    # 3. Train-Test Split (80/20)
    X_train, X_val, y_train, y_val = train_test_split(X_processed, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Training Matrix: {X_train.shape}")
    print(f"Validation Matrix: {X_val.shape}")
    
    # 4. Baseline Model
    scale_pos_weight = 11
    baseline_xgb = XGBClassifier(
        n_estimators=100, 
        scale_pos_weight=scale_pos_weight, 
        random_state=42, 
        eval_metric='logloss',
        early_stopping_rounds=50
    )
    print("\nTraining Baseline XGBoost...")
    baseline_xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    
    y_pred_base = baseline_xgb.predict(X_val)
    recall_base = recall_score(y_val, y_pred_base)
    
    # 5. Hyperparameter Tuning
    print("\nRunning RandomizedSearchCV for Green Champion...")
    param_distributions = {
        'max_depth': [3, 4, 5, 6, 7],
        'learning_rate': [0.01, 0.05, 0.1]
    }
    
    xgb_tune = XGBClassifier(
        n_estimators=100, 
        scale_pos_weight=scale_pos_weight, 
        random_state=42, 
        eval_metric='logloss'
    )
    
    rs = RandomizedSearchCV(xgb_tune, param_distributions, cv=3, scoring='recall', n_iter=5, random_state=42)
    rs.fit(X_train, y_train)
    
    best_params = rs.best_params_
    print(f"Optimal Parameters: max_depth={best_params['max_depth']}, learning_rate={best_params['learning_rate']}")
    
    # 6. Green Champion with Early Stopping
    print(f"\nTraining Tuned XGBoost (Green Champion) to convergence...")
    tuned_xgb = XGBClassifier(
        n_estimators=1000, 
        max_depth=best_params['max_depth'],
        learning_rate=best_params['learning_rate'],
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric='logloss',
        early_stopping_rounds=50
    )
    tuned_xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    
    best_iteration = tuned_xgb.best_iteration
    print(f"Early Stopping Triggered: Converged at round {best_iteration}")
    
    y_pred_tuned = tuned_xgb.predict(X_val)
    y_prob_tuned = tuned_xgb.predict_proba(X_val)[:, 1]
    
    recall_tuned = recall_score(y_val, y_pred_tuned)
    precision_tuned = precision_score(y_val, y_pred_tuned)
    
    # Table Output
    print("\n===========================================")
    print("       BASELINE VS TUNED RECALL TABLE     ")
    print("===========================================")
    print(f" Baseline XGBoost Recall:     {recall_base:.4f}")
    print(f" Tuned Champion XGB Recall:   {recall_tuned:.4f} (with precision {precision_tuned:.4f})")
    print("===========================================\n")
    
    # 7. Artifact Generation
    output_dir = '_temp'
    os.makedirs(output_dir, exist_ok=True)
    
    # Confusion Matrix
    cm = confusion_matrix(y_val, y_pred_tuned)
    plt.figure(figsize=(6,4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Reds', xticklabels=['No Default', 'Default'], yticklabels=['No Default', 'Default'])
    plt.title('Tuned XGBoost: Risk Confusion Matrix')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Alert')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), bbox_inches='tight', dpi=150)
    plt.close()
    
    # ROC-AUC
    fpr, tpr, _ = roc_curve(y_val, y_prob_tuned)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(6,4))
    plt.plot(fpr, tpr, color='darkred', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Tuned XGBoost: ROC-AUC')
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(output_dir, 'roc_auc.png'), bbox_inches='tight', dpi=150)
    plt.close()
    
    # Save Model
    joblib.dump(tuned_xgb, os.path.join('models', 'aegis_champion_xgb.pkl'))
    print("Artifacts successfully generated: confusion_matrix.png, roc_auc.png, aegis_champion_xgb.pkl")

if __name__ == '__main__':
    main()
