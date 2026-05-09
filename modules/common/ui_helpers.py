import math

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --fp-teal: #1f7a7a;
            --fp-teal-dark: #176568;
            --fp-navy: #1f3444;
            --fp-bg: #f6f8fa;
            --fp-card: #ffffff;
            --fp-line: #d9e2ea;
            --fp-muted: #6b7a86;
            --fp-danger: #d85b5b;
            --fp-warning: #b7791f;
            --fp-success: #218568;
        }

        .stApp {
            background: var(--fp-bg);
            color: #1f2937;
            font-family: Inter, "Segoe UI", sans-serif;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #223746 0%, #172938 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #eef6f7;
        }

        [data-testid="stSidebar"] .stButton > button {
            justify-content: flex-start;
            border: 0;
            border-radius: 7px;
            padding: 0.62rem 0.75rem;
            font-weight: 600;
        }

        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background: transparent;
        }

        [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.09);
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"],
        .stFormSubmitButton > button {
            background: linear-gradient(180deg, #2b8f93 0%, #1f7a7a 100%);
            border: 1px solid #176568;
            color: #ffffff;
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            font-size: 1.45rem;
            font-weight: 800;
            padding: 0.55rem 0 1rem;
        }

        .brand-pulse {
            color: #50c3c6;
            font-size: 1.45rem;
            font-weight: 900;
        }

        .sidebar-user {
            color: #cfe0e6;
            font-size: 0.82rem;
            padding-bottom: 1.2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.10);
            margin-bottom: 1rem;
        }

        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            padding: 0.25rem 0 1.1rem;
            border-bottom: 1px solid var(--fp-line);
            margin-bottom: 1.2rem;
        }

        .page-title {
            font-size: 1.55rem;
            font-weight: 800;
            margin: 0;
            color: #17212b;
        }

        .page-subtitle {
            color: var(--fp-muted);
            margin-top: 0.25rem;
            font-size: 0.93rem;
        }

        .kpi-card {
            background: #ffffff;
            border: 1px solid var(--fp-line);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 12px 28px rgba(31, 52, 68, 0.05);
            min-height: 116px;
        }

        .kpi-label {
            color: var(--fp-muted);
            font-size: 0.76rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0;
        }

        .kpi-value {
            color: #17212b;
            font-size: 1.55rem;
            font-weight: 850;
            margin-top: 0.35rem;
        }

        .kpi-note {
            color: var(--fp-muted);
            font-size: 0.82rem;
            margin-top: 0.35rem;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 22% 22%, rgba(31, 122, 122, 0.10), transparent 28%),
                linear-gradient(135deg, #f7fbfc 0%, #eef5f7 100%);
        }

        .login-page-spacer {
            height: 18vh;
        }

        .login-panel-header {
            background: #ffffff;
            border: 1px solid var(--fp-line);
            border-bottom: 0;
            border-radius: 8px 8px 0 0;
            padding: 1.65rem 1.65rem 0.55rem;
            box-shadow: 0 18px 48px rgba(23, 43, 60, 0.12);
        }

        div[data-testid="stForm"] {
            background: #ffffff;
            border: 1px solid var(--fp-line);
            border-top: 0;
            border-radius: 0 0 8px 8px;
            padding: 0.35rem 1.65rem 1.65rem;
            box-shadow: 0 18px 48px rgba(23, 43, 60, 0.12);
        }

        .login-brand {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.55rem;
            font-size: 2.15rem;
            font-weight: 900;
            color: #22313e;
            line-height: 1.1;
        }

        .login-copy {
            color: var(--fp-muted);
            margin: 0.4rem 0 0.15rem;
            line-height: 1.45;
            text-align: center;
            font-weight: 650;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <h1 class="page-title">{title}</h1>
                <div class="page-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_currency(value: float | int | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "Rs. 0"
    return f"Rs. {value:,.0f}"


def format_number(value: float | int | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "0"
    return f"{value:,.0f}"


def format_years_from_months(value: float | int | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "0.0 yrs"
    return f"{value / 12:.1f} yrs"
