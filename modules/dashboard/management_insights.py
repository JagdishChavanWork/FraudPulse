import streamlit as st

from modules.dashboard.credit_dashboard import render_credit_dashboard
from modules.dashboard.fraud_dashboard import render_fraud_dashboard


def render_management_insights() -> None:
    credit_tab, fraud_tab = st.tabs(["Credit Risk Dashboard", "Fraud Dashboard"])

    with credit_tab:
        render_credit_dashboard(show_header=True)

    with fraud_tab:
        render_fraud_dashboard(show_header=True)
