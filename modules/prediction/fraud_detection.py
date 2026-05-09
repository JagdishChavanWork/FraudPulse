import streamlit as st

from ml.fraud.predict import ACCOUNT_TYPE_MAP, TXN_TYPE_MAP, predict_fraud
from modules.auth.session_manager import get_current_employee
from modules.common.ui_helpers import format_currency, kpi_card, page_header
from modules.services.prediction_log_service import log_prediction


USE_CASES = {
    "Likely genuine bill payment": "Savings account, UPI/BILL_PAY, amount close to customer average, daytime transaction, low velocity, no new transaction type.",
    "Account takeover pattern": "NEFT or IMPS at late night, high balance drain, velocity above normal, new transaction type enabled.",
    "SIM swap pattern": "UPI or IMPS, night transaction, very high 24-hour velocity, high balance drain, new transaction type.",
    "Card skimming pattern": "CASH_OUT or DEBIT_CARD, large round amount, night transaction, repeated attempts within 24 hours.",
}


def _risk_badge(level: str) -> None:
    colors = {
        "HIGH": ("#d85b5b", "#fff5f5"),
        "MEDIUM": ("#b7791f", "#fff8e6"),
        "LOW": ("#218568", "#effaf5"),
    }
    border, background = colors[level]
    st.markdown(
        f"""
        <div style="border:1px solid {border};background:{background};border-radius:8px;padding:0.9rem 1rem;margin:0.6rem 0;">
            <div style="font-size:0.75rem;font-weight:800;color:#6b7a86;text-transform:uppercase;">Risk Level</div>
            <div style="font-size:1.9rem;font-weight:900;color:{border};line-height:1.1;">{level}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_fraud_prediction() -> None:
    page_header(
        "Fraud Detection Prediction",
        "Live transaction verification for customer calls, with derived anomaly signals calculated automatically.",
    )
    with st.expander("Example use cases for demo and testing", expanded=False):
        for title, detail in USE_CASES.items():
            st.markdown(f"**{title}**")
            st.write(detail)

    left, right = st.columns([1.25, 0.75])
    with left:
        with st.form("fraud_prediction_form"):
            st.subheader("Customer Profile")
            col1, col2, col3 = st.columns(3)
            age = col1.number_input("Customer age", min_value=18, max_value=90, value=35)
            account_type = col2.selectbox("Account type", list(ACCOUNT_TYPE_MAP.keys()), index=2)
            city_tier = col3.selectbox("City tier", [1, 2, 3])

            col4, col5 = st.columns(2)
            tenure_days = col4.number_input("Account tenure days", min_value=0, value=1800, step=30)
            account_balance = col5.number_input("Account balance", min_value=1.0, value=75000.0, step=1000.0)

            st.subheader("Normal Spending Baseline")
            col6, col7, col8, col9 = st.columns(4)
            avg_monthly_spend = col6.number_input("Avg monthly spend", min_value=0.0, value=25000.0, step=1000.0)
            avg_txn_amount = col7.number_input("Avg transaction amount", min_value=1.0, value=2500.0, step=100.0)
            avg_txn_per_day = col8.number_input("Avg txns per day", min_value=0, value=2)
            usual_txn_hour = col9.slider("Usual txn hour", 0, 23, 11)

            st.subheader("Reported Transaction")
            col10, col11, col12 = st.columns(3)
            txn_type = col10.selectbox("Transaction type", list(TXN_TYPE_MAP.keys()), index=6)
            txn_amount = col11.number_input("Transaction amount", min_value=0.0, value=15000.0, step=500.0)
            txn_hour = col12.slider("Transaction hour", 0, 23, 23)

            col13, col14, col15 = st.columns(3)
            txn_day_of_week = col13.selectbox("Day of week", [0, 1, 2, 3, 4, 5, 6], format_func=lambda day: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day])
            velocity_24hr = col14.number_input("Transactions in last 24H", min_value=0, value=4)
            days_since_last_txn = col15.number_input("Days since last txn", min_value=0, value=1)

            with st.expander("Agent verification flags", expanded=True):
                col16, col17, col18 = st.columns(3)
                new_txn_type_flag = col16.checkbox("New transaction type", value=True)
                large_round_amt_flag = col17.checkbox("Large round amount", value=False)
                prior_fraud_complaint = col18.checkbox("Prior fraud complaint", value=False)

            submitted = st.form_submit_button("Verify Transaction", use_container_width=True)

    with right:
        st.subheader("Verification Result")
        if not submitted:
            st.metric("Fraud probability", "Awaiting input")
            st.metric("Decision threshold", "Model threshold")
            st.caption("Enter customer and transaction details, then verify the transaction.")
            return

        values = {
            "age": age,
            "account_type": account_type,
            "city_tier": city_tier,
            "tenure_days": tenure_days,
            "account_balance": account_balance,
            "avg_monthly_spend": avg_monthly_spend,
            "avg_txn_amount": avg_txn_amount,
            "avg_txn_per_day": avg_txn_per_day,
            "usual_txn_hour": usual_txn_hour,
            "txn_type": txn_type,
            "txn_amount": txn_amount,
            "txn_hour": txn_hour,
            "txn_day_of_week": txn_day_of_week,
            "velocity_24hr": velocity_24hr,
            "new_txn_type_flag": new_txn_type_flag,
            "large_round_amt_flag": large_round_amt_flag,
            "days_since_last_txn": days_since_last_txn,
            "prior_fraud_complaint": prior_fraud_complaint,
        }

        try:
            result = predict_fraud(values)
        except FileNotFoundError as exc:
            st.info(str(exc))
            return

        employee = get_current_employee() or {}
        log_prediction(
            employee.get("employee_id"),
            "fraud_detection_prediction",
            result["payload"],
            result["verdict"],
            result["fraud_probability"],
        )

        probability = result["fraud_probability"]
        st.metric("Fraud probability", f"{probability * 100:.1f}%")
        st.metric("Decision threshold", f"{result['threshold'] * 100:.0f}%")
        _risk_badge(result["risk_level"])

        if result["predicted_flag"]:
            st.error("FRAUD VERIFIED. Escalate immediately and restrict the transaction.")
        else:
            st.success("TRANSACTION APPEARS GENUINE. Close the case if customer verification is complete.")

        payload = result["payload"]
        col1, col2 = st.columns(2)
        with col1:
            kpi_card("Amount vs Avg", f"{payload['amount_to_avg_ratio']:.2f}x", format_currency(txn_amount))
        with col2:
            kpi_card("Balance Drain", f"{payload['balance_drain_pct']:.1f}%", "Auto-calculated")

        st.write("Top model signals")
        if result["top_features"]:
            for feature in result["top_features"]:
                st.caption(feature)
        else:
            st.caption("Train the fraud model to show feature importance.")
