# app_modules/dashboard_reports.py

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy.orm import Session
# FIX: Corrected import to reference external database package
from database.database_connector import get_db
from database.models import PredictionLog # For retrieving log data
from database.models import Employee # Ensure Employee model is available if needed


# --- Data for Part A: Original Dataset Analysis (Simulated) ---
NUMERICAL_SUMMARY_DATA = {
    'Metric': ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50% (Median)', '75%', 'Max'],
    'Amount': [6362620, 179861, 603858, 0, 13389, 74871, 208721, 92445516],
    'Old Balance Org': [6362620, 83387, 862410, 0, 0, 14208, 107315, 59585040],
    'New Balance Dest': [6362620, 119991, 600670, 0, 0, 14660, 292837, 356015889]
}
DF_DESCRIBE = pd.DataFrame(NUMERICAL_SUMMARY_DATA).set_index('Metric')

# Data for Visualizations (Simulated from confirmed EDA insights)
VOLUME_DATA = pd.DataFrame({
    'Transaction Type': ['PAYMENT', 'CASH_OUT', 'CASH_IN', 'TRANSFER', 'DEBIT'],
    'Volume (Millions)': [2.15, 2.23, 1.40, 0.53, 0.17]
})
FEATURE_IMPORTANCE_DATA = pd.DataFrame({
    'Feature': ['balanceDiffOrig', 'Orig_Count_1step', 'is_merchant', 'amount'],
    'Importance Score': [0.45, 0.25, 0.15, 0.10] 
}).sort_values(by='Importance Score', ascending=False)


# --- MAIN PAGE FUNCTION ---
def dashboard_page():
    
    # --- Check for minimum required privileges ---
    if not st.session_state.get('is_admin'):
        st.error("🚨 Access Denied. Only Administrators can view the Performance Dashboard.")
        return

    st.header("Automated Stakeholder Performance Dashboard")
    st.markdown("View Key Performance Indicators (KPIs) and MLOps Validation.")
    st.divider()

    # ... [Rest of the dashboard_page() function content, including charts and metrics] ...
    
    # --- SECTION A: OPERATIONAL METRICS ---
    st.header("1. Model Validation and Cost-Benefit")
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Final Precision (Correct Flags)", "89%", "44.5x Improvement vs. Legacy")
    col2.metric("Final Recall (Fraud Catch Rate)", "80%", "Minimal Loss for Max Precision")
    col3.metric("False Alarms (FP in Test)", "23", "Minimal Operational Overhead")
    st.markdown("---")

    # --- SECTION B: ANALYTICAL VISUALIZATIONS ---
    st.header("2. Analytical Insights and Risk Scoping")
    c1, c2 = st.columns(2)
    
    # Chart 1: Transaction Volume Distribution
    volume_chart = alt.Chart(VOLUME_DATA).mark_bar().encode(
        x=alt.X('Transaction Type', sort='-y'),
        y=alt.Y('Volume (Millions)', title='Volume (Millions)'),
        tooltip=['Transaction Type', 'Volume (Millions)']
    ).transform_calculate(
        is_high_risk = "datum['Transaction Type'] == 'TRANSFER' || datum['Transaction Type'] == 'CASH_OUT'"
    ).encode(
        color=alt.condition(
            alt.datum.is_high_risk,
            alt.value('red'),
            alt.value('lightgray')
        )
    ).properties(title="Transaction Volume Distribution (Risk Scoping)").interactive()
    
    c1.subheader("Transaction Volume")
    c1.altair_chart(volume_chart, use_container_width=True)

    # Chart 3: Feature Importance
    importance_chart = alt.Chart(FEATURE_IMPORTANCE_DATA).mark_bar(color='darkblue').encode(
        x=alt.X('Importance Score', title='Predictive Power (Proxy)'),
        y=alt.Y('Feature', sort='-x'),
        tooltip=['Feature', alt.Tooltip('Importance Score', format='.2f')]
    ).properties(title="Feature Importance in Fraud Detection").interactive()
    
    st.subheader("3. Model Explainability: Feature Importance")
    st.altair_chart(importance_chart, use_container_width=True)


    # --- Section 2.2: Live Prediction Log (ADBMS Read Operation) ---
    st.subheader("2.2 Recent Prediction Log (ADBMS Read Operation)")
    
    try:
        db_generator = get_db()
        db: Session = next(db_generator)
        
        # Retrieve the last 100 logged predictions for display (READ operation)
        logs = db.query(PredictionLog).order_by(PredictionLog.timestamp.desc()).limit(100).all()
        
        # Convert objects to DataFrame for clean display
        log_data = [{
            'ID': log.id,
            'Timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'User': st.session_state.get('username', 'N/A'),
            'Type': log.transaction_type,
            'Amount': f"{log.amount:,.2f}",
            'Risk Score': f"{log.risk_score:.4f}",
            'Predicted': 'FRAUD' if log.predicted_class == 1 else 'SAFE',
        } for log in logs]
        
        st.dataframe(log_data, use_container_width=True)
        
    except Exception as e:
        st.error(f"⚠️ Could not load prediction logs for reporting. Error: {e}")
    finally:
        if 'db' in locals() and db:
            db.close()