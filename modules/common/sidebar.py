import streamlit as st

from config.settings import APP_NAME


NAV_ITEMS = [
    ("Management Insights", "Management Insights"),
    ("Credit Risk Prediction", "Credit Risk Prediction"),
    ("Fraud Detection Prediction", "Fraud Prediction"),
    ("Logout", "Logout"),
]


def render_sidebar(employee: dict) -> str:
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <span>{APP_NAME}</span>
        </div>
        <div class="sidebar-user">Signed in as<br><strong>{employee["employee_name"]}</strong></div>
        """,
        unsafe_allow_html=True,
    )

    valid_pages = {page_key for page_key, _ in NAV_ITEMS}
    if st.session_state.get("active_page") not in valid_pages:
        st.session_state["active_page"] = "Management Insights"

    for page_key, label in NAV_ITEMS:
        button_type = "primary" if st.session_state["active_page"] == page_key else "secondary"
        if st.sidebar.button(label, key=f"nav_{page_key}", type=button_type, use_container_width=True):
            st.session_state["active_page"] = page_key
            st.rerun()

    return st.session_state["active_page"]
