import os
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import joblib

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from app.transformers import SparseSentinelTransformer

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
