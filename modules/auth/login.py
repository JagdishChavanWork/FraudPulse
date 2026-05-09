import bcrypt
import streamlit as st

from database.connection import create_session
from database.queries import get_active_employee_by_id
from modules.auth.session_manager import login_employee


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def authenticate_employee(employee_id: str, password: str) -> dict | None:
    if not employee_id or not password:
        return None

    with create_session() as session:
        employee = get_active_employee_by_id(session, employee_id)
        if not employee or not verify_password(password, employee.employee_password_hash):
            return None

        return {
            "employee_id": employee.employee_id,
            "employee_name": employee.employee_name,
        }


def render_login_page() -> None:
    st.markdown('<div class="login-page-spacer"></div>', unsafe_allow_html=True)

    left, center, right = st.columns([1.3, 1, 1.3])
    with center:
        st.markdown(
            """
            <div class="login-panel-header">
                <div class="login-brand">
                    <span>FraudPulse</span>
                </div>
                <div class="login-copy">Analyst login</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            employee_id = st.text_input("Employee ID", placeholder="ANL001")
            password = st.text_input("Password", type="password", placeholder="Password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        employee = authenticate_employee(employee_id.strip(), password)
        if employee:
            login_employee(employee)
            st.rerun()
        st.error("Invalid employee ID or password.")
