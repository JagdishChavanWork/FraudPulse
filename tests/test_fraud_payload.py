from ml.fraud.predict import build_prediction_payload, risk_level


def test_fraud_payload_calculates_derived_features():
    payload = build_prediction_payload(
        {
            "age": 35,
            "account_type": "Savings",
            "city_tier": 1,
            "tenure_days": 1800,
            "account_balance": 10000,
            "avg_monthly_spend": 25000,
            "avg_txn_amount": 1000,
            "avg_txn_per_day": 2,
            "usual_txn_hour": 10,
            "txn_type": "UPI",
            "txn_amount": 25000,
            "txn_hour": 23,
            "txn_day_of_week": 6,
            "velocity_24hr": 6,
            "new_txn_type_flag": True,
            "large_round_amt_flag": True,
            "days_since_last_txn": 1,
            "prior_fraud_complaint": False,
        }
    )

    assert payload["account_type_enc"] == 2
    assert payload["txn_type_enc"] == 6
    assert payload["is_weekend"] == 1
    assert payload["amount_to_avg_ratio"] == 25
    assert payload["balance_drain_pct"] == 100
    assert payload["hour_anomaly"] == 1


def test_risk_level_thresholds():
    assert risk_level(0.39) == "LOW"
    assert risk_level(0.40) == "MEDIUM"
    assert risk_level(0.71) == "HIGH"
