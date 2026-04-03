import pandas as pd
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
            mask = X_df[col].isna().astype(int)
            mask.name = f"{col}_is_missing"
            X_df[col] = X_df[col].fillna(self.sentinel_value)
            new_features.append(X_df[col])
            new_features.append(mask)
            
        return pd.concat(new_features, axis=1).values
