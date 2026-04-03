"""
Project Aegis-Finance: Clean Data Generation (Leakage-Free)
============================================================
Root Cause of Leakage: gen_robust() injected deterministic extreme blocks
(e.g., rows 0-10000 ALL had income=0, credit=300, D_39=25), making the
target trivially computable. The model memorized these blocks.

Fix:
  - Continuous, noisy feature distributions across ALL rows (no hardcoded blocks)
  - Target derived from a probabilistic model with added Gaussian noise
  - Class imbalance set to realistic ~8% default rate (not 50/50)
  - Features are correlated with target, but NOT deterministic
"""
import pandas as pd
import numpy as np
import os

np.random.seed(42)  # Reproducibility

def gen_clean(n):
    """
    Generate realistic, leakage-free credit risk data.
    Each feature influences default probability, but there is no
    1-to-1 mapping between features and the target.
    """
    # ── Feature Distributions ───────────────────────────────────────────────
    income        = np.random.lognormal(mean=11.0, sigma=0.6, size=n)   # Lognormal income ~$60k median
    credit_score  = np.clip(np.random.normal(680, 80, n), 300, 850)     # Normal centred at 680
    D_39          = np.where(np.random.rand(n) < 0.3,                   # 70% have 0 delinquency
                             np.random.exponential(2, n), 0.0)
    D_42          = np.where(np.random.rand(n) < 0.5, np.random.beta(1, 5, n), np.nan)  # sparse
    D_43          = np.where(np.random.rand(n) < 0.5, np.random.beta(1, 5, n), np.nan)  # sparse
    D_114         = np.random.randint(0, 2, n).astype(float)

    df = pd.DataFrame({
        'income':       income,
        'credit_score': credit_score.astype(int),
        'D_39':         D_39,
        'D_42':         pd.array(D_42, dtype='object'),
        'D_43':         pd.array(D_43, dtype='object'),
        'D_114':        D_114,
        'customer_id':  np.arange(n),
    })
    # Cast sparse back to float (some NaN rows)
    df['D_42'] = pd.to_numeric(df['D_42'], errors='coerce')
    df['D_43'] = pd.to_numeric(df['D_43'], errors='coerce')

    # ── Probabilistic Target ─────────────────────────────────────────────────
    # Log-odds model: each feature pushes default probability up/down
    # This gives a smooth, realistic boundary rather than a step function
    log_odds = (
        +0.5                                        # Baseline (~12% prior default)
        - 0.000015 * income                         # Higher income → safer
        - 0.006    * credit_score                   # Higher score → safer
        + 0.25     * D_39                           # More delinquency → riskier
        + 1.8      * np.nan_to_num(D_42, nan=0.0)  # D_42 present → riskier
        + 1.8      * np.nan_to_num(D_43, nan=0.0)  # D_43 present → riskier
        + 0.6      * D_114                          # D_114=1 → slight risk bump
        + np.random.normal(0, 0.8, n)              # Irreducible noise
    )
    prob_default = 1 / (1 + np.exp(-log_odds))
    df['target'] = (np.random.rand(n) < prob_default).astype(int)

    return df


if __name__ == "__main__":
    os.makedirs('data/raw', exist_ok=True)

    train_df = gen_clean(100000)
    test_df  = gen_clean(5000)

    train_df.to_parquet('data/raw/train_data.parquet')
    test_df.to_parquet('data/raw/test.parquet')

    default_rate = train_df['target'].mean()
    print(f"[Success] Clean data generated.")
    print(f"  Train: {len(train_df):,} rows | Default Rate: {default_rate:.1%}")
    print(f"  Test : {len(test_df):,} rows")
    print(f"  Features: {[c for c in train_df.columns if c not in ['target','customer_id']]}")
