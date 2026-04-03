import os
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import joblib

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin

class SparseSentinelTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer for highly sparse features.
    Creates a binary mask (1 if missing, 0 if present)
    and fills original NaNs with a sentinel value (-999).
    """
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
            # 1: mask = missing (1), present (0)
            mask = X_df[col].isna().astype(int)
            mask.name = f"{col}_is_missing"
            
            # 2: fill with sentinel
            X_df[col] = X_df[col].fillna(self.sentinel_value)
            
            new_features.append(X_df[col])
            new_features.append(mask)
            
        return pd.concat(new_features, axis=1).values

def main():
    print("--- Project Aegis: Phase 2 Feature Engineering ---\n")
    
    # 1. Load Data
    data_path = os.path.join('data', 'raw', 'train_data.parquet')
    print(f"Loading data from {data_path}...")
    parquet_file = pq.ParquetFile(data_path)
    df = next(parquet_file.iter_batches(batch_size=100000)).to_pandas()
    
    X = df.drop(columns=['target', 'customer_id'])
    
    print(f"\n[Before] Shape of X: {X.shape}")
    
    # Feature mappings
    sparse_cols = ['D_42', 'D_43']
    categorical_cols = ['D_114'] 
    num_cols = [c for c in X.columns if c not in sparse_cols + categorical_cols]
    
    print(f"  Numerical Features: {len(num_cols)}")
    print(f"  Sparse Features: {len(sparse_cols)} (D_42, D_43)")
    print(f"  Categorical Features: {len(categorical_cols)} (D_114)")

    # 2. Architect Pipelines
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    sparse_pipeline = Pipeline([
        ('sentinel_masker', SparseSentinelTransformer(sentinel_value=-999))
    ])
    
    cat_pipeline = Pipeline([
        ('cat_imputer', SimpleImputer(strategy='most_frequent')), 
        ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # 3. Assemble ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, num_cols),
            ('sparse', sparse_pipeline, sparse_cols),
            ('cat', cat_pipeline, categorical_cols)
        ],
        remainder='passthrough' 
    )
    
    # 4. Execute Pipeline
    print("\nFitting and transforming pipeline...")
    X_processed = preprocessor.fit_transform(X)
    
    print(f"\n[After] Shape of X_processed: {X_processed.shape}")
    
    # 5. Persist Pipeline for Inference
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)
    
    pipeline_path = os.path.join(models_dir, 'aegis_preprocessor.pkl')
    joblib.dump(preprocessor, pipeline_path)
    print(f"\n[Success] Sklearn Preprocessor saved to {pipeline_path}")

if __name__ == "__main__":
    main()
