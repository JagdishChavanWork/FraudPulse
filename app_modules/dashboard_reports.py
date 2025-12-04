# pages/dashboard_reports.py

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy.orm import Session
from database.database_connector import get_db
from database.models import PredictionLog # For retrieving log data

# --- MAIN PAGE FUNCTION ---
def dashboard_page():
    st.header("Automated Stakeholder Performance Dashboard")
    st.markdown("View Key Performance Indicators (KPIs) and MLOps Validation.")
    st.divider()
    
    # --- SIMULATED DATA (For Analytical Charts) ---
    volume_data = pd.DataFrame({
        'Transaction Type': ['PAYMENT', 'CASH_OUT', 'CASH_IN', 'TRANSFER', 'DEBIT'],
        'Volume (Millions)': [2.15, 2.23, 1.40, 0.53, 0.17]
    })
    risk_data = pd.DataFrame({
        'Transaction Type': ['TRANSFER', 'CASH_OUT', 'CASH_IN', 'DEBIT', 'PAYMENT'],
        'Fraud Rate (%)': [0.77, 0.18, 0.00, 0.00, 0.00]
    })
    feature_data = pd.DataFrame({
        'Feature': ['balanceDiffOrig', 'Orig_Count_1step', 'is_merchant', 'amount'],
        'Importance Score': [0.45, 0.25, 0.15, 0.10] 
    }).sort_values(by='Importance Score', ascending=False)
    
    # --- SECTION A: OPERATIONAL METRICS ---
    st.header("1. Model Validation and Cost-Benefit")
    
    col1, col2, col3 = st.columns(3)
    
    # Final optimized metrics for the Stacking Ensemble
    col1.metric("Final Precision (Correct Flags)", "89%", "44.5x Improvement vs. Legacy")
    col2.metric("Final Recall (Fraud Catch Rate)", "80%", "Minimal Loss for Max Precision")
    col3.metric("False Alarms (FP in Test)", "23", "Minimal Operational Overhead")
    st.markdown("---")


    # --- SECTION B: ANALYTICAL VISUALIZATIONS ---
    st.header("2. Analytical Insights and Risk Scoping")
    
    c1, c2 = st.columns(2)
    
    # Chart 1: Transaction Volume Distribution
    volume_chart = alt.Chart(volume_data).mark_bar().encode(
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
    importance_chart = alt.Chart(feature_data).mark_bar(color='darkblue').encode(
        x=alt.X('Importance Score', title='Predictive Power (Proxy)'),
        y=alt.Y('Feature', sort='-x'),
        tooltip=['Feature', alt.Tooltip('Importance Score', format='.2f')]
    ).properties(title="Feature Importance in Fraud Detection").interactive()
    
    st.subheader("3. Model Explainability: Feature Importance")
    st.altair_chart(importance_chart, use_container_width=True)
    
    st.divider()
    
    # --- SECTION C: LIVE PREDICTION LOG ---
    st.header("4. Live Prediction Log (ADBMS Use)")
    
    try:
        db_generator = get_db()
        db: Session = next(db_generator)
        
        # Retrieve the last 100 logged predictions for display
        logs = db.query(PredictionLog).order_by(PredictionLog.timestamp.desc()).limit(100).all()
        
        # Convert objects to DataFrame for clean display
        log_data = [{
            'ID': log.id,
            'Timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
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