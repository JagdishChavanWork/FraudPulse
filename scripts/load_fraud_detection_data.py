from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import FRAUD_DATASET
from database.connection import create_session, engine
from database.models import Base, FraudDetectionData


NUMERIC_COLUMNS = [
    "age",
    "city_tier",
    "tenure_days",
    "account_balance",
    "avg_monthly_spend",
    "avg_txn_amount",
    "avg_txn_per_day",
    "usual_txn_hour",
    "txn_amount",
    "txn_hour",
    "txn_day_of_week",
    "amount_to_avg_ratio",
    "balance_drain_pct",
    "velocity_24hr",
    "days_since_last_txn",
    "account_type_enc",
    "txn_type_enc",
]

BOOLEAN_COLUMNS = [
    "is_weekend",
    "hour_anomaly",
    "new_txn_type_flag",
    "large_round_amt_flag",
    "prior_fraud_complaint",
    "is_fraud",
]


def normalize_fraud_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    normalized = frame.copy()

    normalized["transaction_id"] = [f"FRD-{index + 1:06d}" for index in range(len(normalized))]
    normalized["transaction_type"] = normalized["txn_type"]
    normalized["amount"] = normalized["txn_amount"]
    normalized["risk_score"] = normalized["is_fraud"].astype(float)
    normalized["risk_band"] = normalized["is_fraud"].map({1: "Confirmed Fraud", 0: "Legitimate"})
    normalized["fraud_type"] = normalized["fraud_type"].fillna("Legitimate")
    normalized["source_file"] = path.name

    for column in NUMERIC_COLUMNS:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    for column in BOOLEAN_COLUMNS:
        normalized[column] = normalized[column].astype(bool)

    text_columns = ["account_type", "txn_type", "transaction_type", "fraud_type", "age_group", "risk_band"]
    for column in text_columns:
        normalized[column] = normalized[column].astype("string").str.strip()

    model_columns = [
        "transaction_id",
        "transaction_type",
        "amount",
        "age",
        "account_type",
        "account_type_enc",
        "city_tier",
        "tenure_days",
        "account_balance",
        "avg_monthly_spend",
        "avg_txn_amount",
        "avg_txn_per_day",
        "usual_txn_hour",
        "txn_type",
        "txn_type_enc",
        "txn_amount",
        "txn_hour",
        "txn_day_of_week",
        "is_weekend",
        "amount_to_avg_ratio",
        "balance_drain_pct",
        "hour_anomaly",
        "velocity_24hr",
        "new_txn_type_flag",
        "large_round_amt_flag",
        "days_since_last_txn",
        "prior_fraud_complaint",
        "fraud_type",
        "is_fraud",
        "age_group",
        "risk_score",
        "risk_band",
        "source_file",
    ]
    return normalized[model_columns].where(pd.notna(normalized), None)


def load_fraud_detection_data(path: Path = FRAUD_DATASET, replace: bool = True) -> int:
    if not path.exists():
        raise FileNotFoundError(f"Fraud dataset not found: {path}")

    if replace:
        FraudDetectionData.__table__.drop(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    frame = normalize_fraud_frame(path)

    with create_session() as session:
        records = [FraudDetectionData(**row) for row in frame.to_dict(orient="records")]
        session.add_all(records)
        session.commit()

    return len(frame)


if __name__ == "__main__":
    loaded_count = load_fraud_detection_data()
    print(f"Loaded {loaded_count:,} fraud detection records into SQLite.")
