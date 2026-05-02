from __future__ import annotations

import json
from pathlib import Path
import sys

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


ARTIFACT_DIR = PROJECT_ROOT / "models" / "fraud"
MODEL_PATH = ARTIFACT_DIR / "fraud_xgb_classifier.joblib"
SCALER_PATH = ARTIFACT_DIR / "fraud_scaler.joblib"
FEATURES_PATH = ARTIFACT_DIR / "fraud_feature_columns.json"
THRESHOLD_PATH = ARTIFACT_DIR / "fraud_threshold.json"
IMPORTANCE_PATH = ARTIFACT_DIR / "fraud_feature_importance.csv"

ACCOUNT_TYPE_MAP = {"Current": 0, "Salary": 1, "Savings": 2}
TXN_TYPE_MAP = {"BILL_PAY": 0, "CASH_IN": 1, "CASH_OUT": 2, "DEBIT_CARD": 3, "IMPS": 4, "NEFT": 5, "UPI": 6}


def load_artifacts() -> dict:
    missing = [path for path in [MODEL_PATH, SCALER_PATH, FEATURES_PATH, THRESHOLD_PATH] if not path.exists()]
    if missing:
        raise FileNotFoundError("Fraud model artifacts not found. Run: python ml\\fraud\\train.py")

    return {
        "model": joblib.load(MODEL_PATH),
        "scaler": joblib.load(SCALER_PATH),
        "feature_columns": json.loads(FEATURES_PATH.read_text(encoding="utf-8")),
        "threshold": json.loads(THRESHOLD_PATH.read_text(encoding="utf-8"))["threshold"],
    }


def build_prediction_payload(values: dict) -> dict:
    account_balance = max(float(values["account_balance"]), 1.0)
    avg_txn_amount = max(float(values["avg_txn_amount"]), 1.0)
    txn_amount = float(values["txn_amount"])
    txn_hour = int(values["txn_hour"])
    usual_txn_hour = int(values["usual_txn_hour"])
    txn_day_of_week = int(values["txn_day_of_week"])

    payload = {
        "age": int(values["age"]),
        "account_type_enc": ACCOUNT_TYPE_MAP[values["account_type"]],
        "city_tier": int(values["city_tier"]),
        "tenure_days": int(values["tenure_days"]),
        "account_balance": float(values["account_balance"]),
        "avg_monthly_spend": float(values["avg_monthly_spend"]),
        "avg_txn_amount": float(values["avg_txn_amount"]),
        "avg_txn_per_day": int(values["avg_txn_per_day"]),
        "usual_txn_hour": usual_txn_hour,
        "txn_type_enc": TXN_TYPE_MAP[values["txn_type"]],
        "txn_amount": txn_amount,
        "txn_hour": txn_hour,
        "txn_day_of_week": txn_day_of_week,
        "is_weekend": 1 if txn_day_of_week in {5, 6} else 0,
        "amount_to_avg_ratio": min(txn_amount / avg_txn_amount, 50.0),
        "balance_drain_pct": min((txn_amount / account_balance) * 100, 100.0),
        "hour_anomaly": 1 if abs(txn_hour - usual_txn_hour) > 4 else 0,
        "velocity_24hr": int(values["velocity_24hr"]),
        "new_txn_type_flag": int(values["new_txn_type_flag"]),
        "large_round_amt_flag": int(values["large_round_amt_flag"]),
        "days_since_last_txn": int(values["days_since_last_txn"]),
        "prior_fraud_complaint": int(values["prior_fraud_complaint"]),
    }
    return payload


def risk_level(probability: float) -> str:
    if probability > 0.70:
        return "HIGH"
    if probability >= 0.40:
        return "MEDIUM"
    return "LOW"


def predict_fraud(values: dict) -> dict:
    artifacts = load_artifacts()
    payload = build_prediction_payload(values)
    frame = pd.DataFrame([payload]).reindex(columns=artifacts["feature_columns"])
    scaled = artifacts["scaler"].transform(frame)
    probability = float(artifacts["model"].predict_proba(scaled)[0][1])
    threshold = float(artifacts["threshold"])
    predicted_flag = int(probability >= threshold)
    level = risk_level(probability)

    top_features = []
    if IMPORTANCE_PATH.exists():
        importance = pd.read_csv(IMPORTANCE_PATH).head(3)
        top_features = importance["feature"].tolist()

    return {
        "fraud_probability": probability,
        "threshold": threshold,
        "predicted_flag": predicted_flag,
        "risk_level": level,
        "verdict": "FRAUD VERIFIED" if predicted_flag else "TRANSACTION APPEARS GENUINE",
        "payload": payload,
        "top_features": top_features,
    }
