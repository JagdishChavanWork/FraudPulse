import streamlit as st

from modules.common.ui_helpers import page_header


def render_fraud_dashboard() -> None:
    page_header(
        "Fraud Detection Dashboard",
        "Phase 3 placeholder for transaction intelligence from fraud_detection_data.",
    )
    st.info(
        "Fraud BI will be connected after the credit risk dashboard and prediction scaffold. "
        "The database table is already reserved for transaction-level dashboard data."
    )
