"""
=============================================================
  Aegis-Finance — Drift Monitor
  PSI-based feature drift detection
  
  Detects when incoming loan application data drifts
  away from the training distribution — a signal that
  the model may need retraining.

  Drift thresholds (industry standard):
    PSI < 0.10  → No significant drift   ✅ STABLE
    PSI 0.10–0.20 → Moderate drift      ⚠️  MONITOR
    PSI > 0.20  → Significant drift     🔴 RETRAIN
=============================================================
"""

import numpy as np
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

# ── Baseline Training Distribution ──────────────────────────
# These stats represent your TRAINING data distribution.
# In production you'd compute these from your actual training set
# and save to a JSON file. Here we define them directly based
# on your Aegis-Finance loan dataset characteristics.

TRAINING_BASELINE = {
    "income": {
        "mean": 65000.0,
        "std":  28000.0,
        "min":  10000.0,
        "max":  200000.0,
        "percentiles": [25000, 50000, 85000, 120000]  # p25, p50, p75, p90
    },
    "credit_score": {
        "mean": 670.0,
        "std":  85.0,
        "min":  300.0,
        "max":  850.0,
        "percentiles": [580, 670, 740, 790]
    },
    "D_39": {
        "mean": 0.15,   # ~15% delinquency rate in training data
        "std":  0.36,
        "null_rate": 0.25
    },
    "D_42": {
        "mean": 0.08,
        "std":  0.27,
        "null_rate": 0.40
    },
    "D_43": {
        "mean": 0.12,
        "std":  0.33,
        "null_rate": 0.35
    },
    "D_114": {
        "mean": 0.10,
        "std":  0.30,
        "null_rate": 0.30
    }
}

# ── In-memory rolling window of recent predictions ───────────
# Stores last N prediction inputs for drift calculation
# In production: use Redis or a database

MAX_WINDOW_SIZE = 500  # keep last 500 predictions

_prediction_window: list = []


def record_prediction(features: dict) -> None:
    """
    Store incoming prediction features in rolling window.
    Called on every POST /api/predict request.
    """
    global _prediction_window

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "income":       features.get("income"),
        "credit_score": features.get("credit_score"),
        "D_39":         features.get("D_39"),
        "D_42":         features.get("D_42"),
        "D_43":         features.get("D_43"),
        "D_114":        features.get("D_114"),
    }

    _prediction_window.append(record)

    # Keep only last MAX_WINDOW_SIZE records
    if len(_prediction_window) > MAX_WINDOW_SIZE:
        _prediction_window = _prediction_window[-MAX_WINDOW_SIZE:]


def get_window_size() -> int:
    """Return current number of predictions in window."""
    return len(_prediction_window)


def calculate_psi_numeric(
    baseline_mean: float,
    baseline_std: float,
    current_values: list,
    n_bins: int = 10
) -> float:
    """
    Calculate PSI for a numeric feature using binning.

    PSI = Σ (current_pct - baseline_pct) × ln(current_pct / baseline_pct)

    Args:
        baseline_mean: Mean from training data
        baseline_std:  Std from training data
        current_values: List of recent values from production
        n_bins: Number of bins for histogram comparison

    Returns:
        PSI score (float)
    """
    if len(current_values) < 10:
        return 0.0  # not enough data for meaningful PSI

    current_arr = np.array([v for v in current_values if v is not None])
    if len(current_arr) == 0:
        return 0.0

    # Create bins based on baseline distribution (±3 sigma)
    bin_min = baseline_mean - 3 * baseline_std
    bin_max = baseline_mean + 3 * baseline_std
    bins = np.linspace(bin_min, bin_max, n_bins + 1)

    # Simulate baseline distribution (normal approximation)
    baseline_sim = np.random.normal(baseline_mean, baseline_std, 10000)
    baseline_hist, _ = np.histogram(baseline_sim, bins=bins)
    current_hist,  _ = np.histogram(current_arr,  bins=bins)

    # Add epsilon for stability and avoid log(0)
    # Using 1e-4 (conservative) instead of 1e-6 to prevent large swings
    epsilon = 1e-4
    b_sum = baseline_hist.sum()
    c_sum = current_hist.sum()

    # Safety: If no data fits bins (extreme drift), return a high but finite PSI
    if b_sum == 0 or c_sum == 0:
        return 3.0  # Caps drift at a significant value for JSON safety

    baseline_pct = (baseline_hist + epsilon) / (b_sum + epsilon * n_bins)
    current_pct  = (current_hist  + epsilon) / (c_sum + epsilon * n_bins)

    # Compute PSI components and handle any residuals (abs)
    psi_values = (current_pct - baseline_pct) * np.log(current_pct / baseline_pct)
    psi = float(np.sum(psi_values))
    
    return round(float(np.nan_to_num(abs(psi), nan=0.0, posinf=3.0, neginf=0.0)), 4)


def calculate_null_rate_drift(
    baseline_null_rate: float,
    current_values: list
) -> dict:
    """
    For sparse D_ features, track null rate drift.
    If null rate changes significantly, the data pipeline may have issues.
    """
    if not current_values:
        return {"current_null_rate": 0.0, "baseline_null_rate": baseline_null_rate, "drift": 0.0}

    current_null_rate = sum(1 for v in current_values if v is None) / len(current_values)
    drift = abs(current_null_rate - baseline_null_rate)

    return {
        "current_null_rate": round(current_null_rate, 4),
        "baseline_null_rate": round(baseline_null_rate, 4),
        "null_rate_shift": round(drift, 4)
    }


def get_drift_label(psi: float) -> str:
    """Convert PSI score to human-readable label."""
    if psi < 0.10:
        return "STABLE"
    elif psi < 0.20:
        return "MONITOR"
    else:
        return "RETRAIN"


def get_drift_emoji(psi: float) -> str:
    """Emoji for drift status."""
    if psi < 0.10:
        return "✅"
    elif psi < 0.20:
        return "⚠️"
    else:
        return "🔴"


def compute_full_drift_report() -> dict:
    """
    Compute complete drift report for all features.
    Called by GET /drift endpoint.

    Returns:
        Full drift report with per-feature PSI scores,
        null rate shifts, and overall drift status.
    """
    if len(_prediction_window) < 20:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": f"Need at least 20 predictions for drift analysis. Current: {len(_prediction_window)}",
            "predictions_in_window": len(_prediction_window),
            "minimum_required": 20
        }

    # Extract feature values from window
    incomes       = [r["income"]       for r in _prediction_window]
    credit_scores = [r["credit_score"] for r in _prediction_window]
    d39_values    = [r["D_39"]         for r in _prediction_window]
    d42_values    = [r["D_42"]         for r in _prediction_window]
    d43_values    = [r["D_43"]         for r in _prediction_window]
    d114_values   = [r["D_114"]        for r in _prediction_window]

    # ── Calculate PSI for numeric features ──────────────────
    income_psi = calculate_psi_numeric(
        TRAINING_BASELINE["income"]["mean"],
        TRAINING_BASELINE["income"]["std"],
        incomes
    )

    credit_psi = calculate_psi_numeric(
        TRAINING_BASELINE["credit_score"]["mean"],
        TRAINING_BASELINE["credit_score"]["std"],
        credit_scores
    )

    # ── Calculate null rate drift for D_ features ───────────
    d39_null  = calculate_null_rate_drift(TRAINING_BASELINE["D_39"]["null_rate"],  d39_values)
    d42_null  = calculate_null_rate_drift(TRAINING_BASELINE["D_42"]["null_rate"],  d42_values)
    d43_null  = calculate_null_rate_drift(TRAINING_BASELINE["D_43"]["null_rate"],  d43_values)
    d114_null = calculate_null_rate_drift(TRAINING_BASELINE["D_114"]["null_rate"], d114_values)

    # ── Overall PSI (average of numeric features) ───────────
    overall_psi = round((income_psi + credit_psi) / 2, 4)
    overall_label = get_drift_label(overall_psi)

    # ── Current window statistics ────────────────────────────
    valid_incomes = [v for v in incomes if v is not None]
    valid_credits = [v for v in credit_scores if v is not None]

    current_stats = {}
    if valid_incomes:
        current_stats["income"] = {
            "mean": round(float(np.mean(valid_incomes)), 2),
            "std":  round(float(np.std(valid_incomes)),  2),
            "min":  round(float(np.min(valid_incomes)),  2),
            "max":  round(float(np.max(valid_incomes)),  2),
        }
    if valid_credits:
        current_stats["credit_score"] = {
            "mean": round(float(np.mean(valid_credits)), 2),
            "std":  round(float(np.std(valid_credits)),  2),
            "min":  round(float(np.min(valid_credits)),  2),
            "max":  round(float(np.max(valid_credits)),  2),
        }

    # ── Build full report ────────────────────────────────────
    return {
        "status":                 overall_label,
        "overall_psi":            overall_psi,
        "drift_emoji":            get_drift_emoji(overall_psi),
        "retraining_recommended": overall_psi > 0.20,
        "predictions_analyzed":   len(_prediction_window),
        "analysis_timestamp":     datetime.utcnow().isoformat(),

        "feature_drift": {
            "income": {
                "psi":           income_psi,
                "status":        get_drift_label(income_psi),
                "emoji":         get_drift_emoji(income_psi),
                "baseline_mean": TRAINING_BASELINE["income"]["mean"],
                "current_mean":  current_stats.get("income", {}).get("mean", "N/A"),
            },
            "credit_score": {
                "psi":           credit_psi,
                "status":        get_drift_label(credit_psi),
                "emoji":         get_drift_emoji(credit_psi),
                "baseline_mean": TRAINING_BASELINE["credit_score"]["mean"],
                "current_mean":  current_stats.get("credit_score", {}).get("mean", "N/A"),
            },
            "D_39":  {"null_rate_drift": d39_null,  "feature_type": "sparse_delinquency"},
            "D_42":  {"null_rate_drift": d42_null,  "feature_type": "sparse_delinquency"},
            "D_43":  {"null_rate_drift": d43_null,  "feature_type": "sparse_delinquency"},
            "D_114": {"null_rate_drift": d114_null, "feature_type": "sparse_delinquency"},
        },

        "current_window_stats": current_stats,
        "baseline_stats": {
            "income":       {"mean": TRAINING_BASELINE["income"]["mean"],       "std": TRAINING_BASELINE["income"]["std"]},
            "credit_score": {"mean": TRAINING_BASELINE["credit_score"]["mean"], "std": TRAINING_BASELINE["credit_score"]["std"]},
        },

        "psi_thresholds": {
            "stable":  "PSI < 0.10",
            "monitor": "PSI 0.10 – 0.20",
            "retrain": "PSI > 0.20"
        },

        "recommendation": (
            "🔴 RETRAIN: Significant drift detected. Schedule model retraining."
            if overall_psi > 0.20 else
            "⚠️  MONITOR: Moderate drift. Increase monitoring frequency."
            if overall_psi > 0.10 else
            "✅ STABLE: No significant drift. Model performing as expected."
        )
    }
