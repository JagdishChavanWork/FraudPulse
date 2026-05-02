import pandas as pd
import plotly.express as px
import streamlit as st

from ml.fraud.predict import IMPORTANCE_PATH
from modules.common.charts import COLOR_SEQUENCE, apply_chart_theme
from modules.common.ui_helpers import format_currency, format_number, kpi_card, page_header
from modules.services.fraud_service import FRAUD_DISPLAY_COLUMNS, apply_fraud_filters, get_fraud_data


def _safe_rate(numerator: pd.Series, denominator: pd.Series | int) -> float:
    if isinstance(denominator, int):
        return 0.0 if denominator == 0 else float(numerator.sum() / denominator)
    total = denominator.sum()
    return 0.0 if total == 0 else float(numerator.sum() / total)


def _render_filters(frame: pd.DataFrame) -> pd.DataFrame:
    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        txn_types = col1.multiselect("Transaction type", sorted(frame["txn_type"].dropna().unique()))
        fraud_types = col2.multiselect("Fraud pattern", sorted(frame["fraud_type"].dropna().unique()))
        risk_flags = col3.multiselect("Case status", ["Fraud", "Legitimate"], default=["Fraud", "Legitimate"])
    return apply_fraud_filters(frame, txn_types, fraud_types, risk_flags)


def _render_kpis(frame: pd.DataFrame) -> None:
    fraud = frame[frame["is_fraud"].astype(int).eq(1)]
    fraud_rate = 0.0 if frame.empty else frame["is_fraud"].astype(int).mean() * 100
    avg_fraud_amount = fraud["txn_amount"].mean() if not fraud.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Cases", format_number(len(frame)), "Historical transaction checks")
    with col2:
        kpi_card("Fraud Cases", format_number(len(fraud)), "Confirmed suspicious activity")
    with col3:
        kpi_card("Fraud Rate", f"{fraud_rate:.1f}%", "Fraud share in selected cases")
    with col4:
        kpi_card("Avg Fraud Amount", format_currency(avg_fraud_amount), "Average confirmed loss exposure")


def _fraud_vs_legit_by_type(frame: pd.DataFrame):
    grouped = (
        frame.assign(case_status=frame["is_fraud"].astype(int).map({1: "Fraud", 0: "Legitimate"}))
        .groupby(["txn_type", "case_status"])
        .size()
        .reset_index(name="records")
    )
    fig = px.bar(
        grouped,
        x="txn_type",
        y="records",
        color="case_status",
        barmode="group",
        title="Fraud vs legitimate cases by transaction type",
        color_discrete_map={"Fraud": "#d85b5b", "Legitimate": "#1f7a7a"},
    )
    return apply_chart_theme(fig)


def _fraud_rate_by_hour(frame: pd.DataFrame):
    grouped = frame.groupby("txn_hour")["is_fraud"].mean().reset_index()
    grouped["fraud_rate"] = grouped["is_fraud"] * 100
    fig = px.line(grouped, x="txn_hour", y="fraud_rate", markers=True, title="Fraud rate by hour of day")
    fig.update_traces(line_color="#d85b5b")
    return apply_chart_theme(fig)


def _fraud_rate_by_city(frame: pd.DataFrame):
    grouped = frame.groupby("city_tier")["is_fraud"].mean().reset_index()
    grouped["fraud_rate"] = grouped["is_fraud"] * 100
    fig = px.bar(grouped, x="city_tier", y="fraud_rate", title="Fraud rate by city tier", color_discrete_sequence=["#f2b84b"])
    return apply_chart_theme(fig)


def _account_txn_heatmap(frame: pd.DataFrame):
    grouped = frame.groupby(["account_type", "txn_type"])["is_fraud"].mean().reset_index()
    grouped["fraud_rate"] = grouped["is_fraud"] * 100
    matrix = grouped.pivot(index="account_type", columns="txn_type", values="fraud_rate").fillna(0)
    fig = px.imshow(
        matrix,
        text_auto=".1f",
        aspect="auto",
        title="Fraud rate heatmap: account type vs transaction type",
        color_continuous_scale=["#eef5f7", "#f2b84b", "#d85b5b"],
    )
    return apply_chart_theme(fig, height=360)


def _render_overview(frame: pd.DataFrame) -> None:
    _render_kpis(frame)
    st.write("")

    col1, col2 = st.columns([1.35, 0.65])
    with col1:
        st.plotly_chart(_fraud_vs_legit_by_type(frame), use_container_width=True)
    with col2:
        fraud_only = frame[frame["is_fraud"].astype(int).eq(1)]
        fig = px.pie(fraud_only, names="age_group", title="Fraud distribution by age group", color_discrete_sequence=COLOR_SEQUENCE)
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(_fraud_rate_by_hour(frame), use_container_width=True)
    with col4:
        st.plotly_chart(_fraud_rate_by_city(frame), use_container_width=True)

    st.plotly_chart(_account_txn_heatmap(frame), use_container_width=True)


def _render_pattern_analysis(frame: pd.DataFrame) -> None:
    labeled = frame.assign(case_status=frame["is_fraud"].astype(int).map({1: "Fraud", 0: "Legitimate"}))
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(
            labeled,
            x="txn_amount",
            color="case_status",
            nbins=45,
            barmode="overlay",
            title="Transaction amount distribution",
            color_discrete_map={"Fraud": "#d85b5b", "Legitimate": "#1f7a7a"},
        )
        fig.update_traces(opacity=0.64)
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)
    with col2:
        fig = px.histogram(
            labeled,
            x="amount_to_avg_ratio",
            color="case_status",
            nbins=45,
            barmode="overlay",
            title="Amount-to-average ratio distribution",
            color_discrete_map={"Fraud": "#d85b5b", "Legitimate": "#1f7a7a"},
        )
        fig.update_traces(opacity=0.64)
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

    fraud_only = frame[frame["is_fraud"].astype(int).eq(1)]
    col3, col4 = st.columns(2)
    with col3:
        fig = px.box(
            fraud_only,
            x="fraud_type",
            y="balance_drain_pct",
            color="fraud_type",
            title="Balance drain by fraud pattern",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)
    with col4:
        velocity = fraud_only["velocity_24hr"].value_counts().sort_index().reset_index()
        velocity.columns = ["velocity_24hr", "records"]
        fig = px.bar(velocity, x="velocity_24hr", y="records", title="Fraud velocity distribution", color_discrete_sequence=["#6c8fac"])
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

    col5, col6 = st.columns([0.75, 1.25])
    with col5:
        fig = px.pie(fraud_only, names="fraud_type", title="Fraud type breakdown", color_discrete_sequence=COLOR_SEQUENCE)
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)
    with col6:
        st.subheader("Model Feature Importance")
        if IMPORTANCE_PATH.exists():
            importance = pd.read_csv(IMPORTANCE_PATH).head(12)
            st.dataframe(importance, use_container_width=True, hide_index=True)
        else:
            st.info("Train the fraud model to show feature importance: python ml\\fraud\\train.py")


def _render_case_lookup(frame: pd.DataFrame) -> None:
    st.subheader("Customer Risk Profile")
    lookup = st.text_input("Search by generated case ID", value=str(frame["transaction_id"].iloc[0]) if not frame.empty else "")
    record = frame[frame["transaction_id"].astype(str).str.contains(lookup, case=False, na=False)].head(1)
    if record.empty:
        st.info("No matching case found.")
        return

    row = record.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Account Type", str(row["account_type"]), f"Age {int(row['age'])}, {row['age_group']}")
    with col2:
        kpi_card("Balance", format_currency(row["account_balance"]), f"Tenure {int(row['tenure_days'])} days")
    with col3:
        kpi_card("Latest Amount", format_currency(row["txn_amount"]), f"{row['txn_type']} at hour {int(row['txn_hour'])}")
    with col4:
        status = "Fraud" if int(row["is_fraud"]) == 1 else "Legitimate"
        kpi_card("Case Status", status, str(row["fraud_type"]))

    flags = {
        "Hour anomaly": bool(row["hour_anomaly"]),
        "New transaction type": bool(row["new_txn_type_flag"]),
        "Large round amount": bool(row["large_round_amt_flag"]),
        "Prior fraud complaint": bool(row["prior_fraud_complaint"]),
    }
    active_flags = [name for name, active in flags.items() if active]
    if active_flags:
        st.warning("Active anomaly flags: " + ", ".join(active_flags))
    else:
        st.success("No anomaly flags are active for this selected case.")

    display = record.rename(columns=FRAUD_DISPLAY_COLUMNS)
    st.dataframe(display[list(FRAUD_DISPLAY_COLUMNS.values())], use_container_width=True, hide_index=True)


def render_fraud_dashboard() -> None:
    page_header(
        "Fraud Detection Dashboard",
        "Operational story of suspicious transfers, account behavior shifts, velocity spikes, and verified fraud patterns.",
    )

    frame = get_fraud_data()
    if frame.empty:
        st.warning("No fraud data found. Run: python scripts\\load_fraud_detection_data.py")
        return

    filtered = _render_filters(frame)
    if filtered.empty:
        st.info("No fraud records match the current filters.")
        return

    overview_tab, pattern_tab, profile_tab, records_tab = st.tabs(
        ["Overview", "Pattern Analysis", "Customer Risk Profile", "Records"]
    )

    with overview_tab:
        _render_overview(filtered)
    with pattern_tab:
        _render_pattern_analysis(filtered)
    with profile_tab:
        _render_case_lookup(filtered)
    with records_tab:
        display = filtered.rename(columns=FRAUD_DISPLAY_COLUMNS)
        st.dataframe(display[list(FRAUD_DISPLAY_COLUMNS.values())], use_container_width=True, hide_index=True)
