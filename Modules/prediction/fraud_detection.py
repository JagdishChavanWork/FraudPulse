import streamlit as st

from modules.common.ui_helpers import page_header


def render_fraud_prediction() -> None:
    page_header(
        "Fraud Detection Prediction",
        "Phase 4 placeholder for transaction-level fraud risk scoring.",
    )

    with st.form("fraud_prediction_form"):
        col1, col2 = st.columns(2)
        col1.selectbox("Transaction type", ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"])
        col2.number_input("Amount", min_value=0.0, value=5000.0, step=500.0)
        col1.number_input("Old origin balance", min_value=0.0, value=10000.0)
        col2.number_input("New origin balance", min_value=0.0, value=5000.0)
        submitted = st.form_submit_button("Analyze for Fraud", use_container_width=True)

    if submitted:
        st.info("Fraud model integration is pending. The page is scaffolded for future inference.")
