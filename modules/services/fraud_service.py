import pandas as pd

from config.settings import FRAUD_DATASET
from database.connection import engine


FRAUD_DISPLAY_COLUMNS = {
    "transaction_id": "Case ID",
    "age": "Age",
    "age_group": "Age Group",
    "account_type": "Account Type",
    "city_tier": "City Tier",
    "account_balance": "Balance",
    "txn_type": "Transaction Type",
    "txn_amount": "Amount",
    "txn_hour": "Hour",
    "txn_day_of_week": "Day Of Week",
    "amount_to_avg_ratio": "Amount vs Avg",
    "balance_drain_pct": "Balance Drain %",
    "velocity_24hr": "24H Velocity",
    "fraud_type": "Fraud Type",
    "is_fraud": "Fraud Flag",
}


def _with_dashboard_labels(frame: pd.DataFrame) -> pd.DataFrame:
    labeled = frame.copy()
    if "fraud_type" in labeled.columns:
        labeled["fraud_type"] = labeled["fraud_type"].fillna("Legitimate")
    return labeled


def get_fraud_data() -> pd.DataFrame:
    query = """
        SELECT
            transaction_id,
            age,
            account_type,
            account_type_enc,
            city_tier,
            tenure_days,
            account_balance,
            avg_monthly_spend,
            avg_txn_amount,
            avg_txn_per_day,
            usual_txn_hour,
            txn_type,
            txn_type_enc,
            txn_amount,
            txn_hour,
            txn_day_of_week,
            is_weekend,
            amount_to_avg_ratio,
            balance_drain_pct,
            hour_anomaly,
            velocity_24hr,
            new_txn_type_flag,
            large_round_amt_flag,
            days_since_last_txn,
            prior_fraud_complaint,
            fraud_type,
            is_fraud,
            age_group
        FROM fraud_detection_data
        ORDER BY id DESC
    """
    try:
        frame = pd.read_sql_query(query, con=engine)
    except Exception:
        frame = pd.DataFrame()

    if frame.empty and FRAUD_DATASET.exists():
        frame = pd.read_csv(FRAUD_DATASET)
        frame["transaction_id"] = [f"FRD-{index + 1:06d}" for index in range(len(frame))]

    if frame.empty:
        return frame

    return _with_dashboard_labels(frame)


def apply_fraud_filters(
    frame: pd.DataFrame,
    txn_types: list[str],
    fraud_types: list[str],
    risk_flags: list[str],
) -> pd.DataFrame:
    filtered = frame.copy()
    if txn_types:
        filtered = filtered[filtered["txn_type"].isin(txn_types)]
    if fraud_types:
        filtered = filtered[filtered["fraud_type"].isin(fraud_types)]
    if risk_flags:
        flag_map = {"Fraud": 1, "Legitimate": 0}
        filtered = filtered[filtered["is_fraud"].astype(int).isin([flag_map[item] for item in risk_flags])]
    return filtered
