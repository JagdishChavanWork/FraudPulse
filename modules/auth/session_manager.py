import streamlit as st


def login_employee(employee: dict) -> None:
    st.session_state["employee"] = employee
    st.session_state.setdefault("active_page", "Credit Risk Dashboard")


def logout_employee() -> None:
    st.session_state.pop("employee", None)
    st.session_state.pop("active_page", None)


def get_current_employee() -> dict | None:
    return st.session_state.get("employee")
