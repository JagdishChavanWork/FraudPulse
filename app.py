import streamlit as st

from config.settings import APP_NAME
from database.init_db import initialize_database
from modules.auth.login import render_login_page
from modules.auth.session_manager import get_current_employee, logout_employee
from modules.common.sidebar import render_sidebar
from modules.common.ui_helpers import inject_global_styles
from modules.dashboard.management_insights import render_management_insights
from modules.prediction.credit_risk import render_credit_prediction
from modules.prediction.fraud_detection import render_fraud_prediction


st.set_page_config(
    page_title=APP_NAME,
    page_icon="FP",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGE_RENDERERS = {
    "Management Insights": render_management_insights,
    "Credit Risk Prediction": render_credit_prediction,
    "Fraud Detection Prediction": render_fraud_prediction,
}


def main() -> None:
    initialize_database()
    inject_global_styles()

    employee = get_current_employee()
    if not employee:
        render_login_page()
        return

    selected_page = render_sidebar(employee)
    if selected_page == "Logout":
        logout_employee()
        st.rerun()

    PAGE_RENDERERS[selected_page]()


if __name__ == "__main__":
    main()
