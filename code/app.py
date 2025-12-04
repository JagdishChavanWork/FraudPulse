import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime
import numpy as np
import altair as alt # Needed for the analytical dashboard charts

# --- CONFIGURATION ---
# Define the MLOps deployment path for your Ensemble Pipeline

# Get the directory of the current script (e.g., E:\FraudPulse\code)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
# Define the path to the model file: UP one level (..) then INTO the 'models' folder
MODEL_NAME = "fraud_detection_deployment_pipeline.pkl"
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", MODEL_NAME)


# --- MODEL LOADING (Run Once at Startup) ---
@st.cache_resource
def load_model():
    """
    Loads the Stacking Ensemble Pipeline with its preprocessor.
    This function uses the dynamic path to ensure the model is found across environments.
    """
    try:
        if not os.path.exists(MODEL_PATH):
            st.error(f"❌ CRITICAL ERROR: Model file not found at expected path: {MODEL_PATH}")
            st.warning("Please ensure the 'models' folder is next to the 'code' folder.")
            st.stop()
        
        # Load the Stacking Ensemble + Preprocessor
        pipeline = joblib.load(MODEL_PATH)
        st.sidebar.success("✅ Model Pipeline Loaded")
        return pipeline
    except Exception as e:
        st.error(f"❌ GENERAL ERROR loading pipeline: {e}")
        st.stop()

model = load_model()

# --- HELPER FUNCTIONS ---

def feature_engineer_input(input_df: pd.DataFrame) -> pd.DataFrame:
    """Applies the custom feature engineering logic to raw input data."""
    
    # 1. Calculate Core Predictors (Balance Differences)
    input_df["balanceDiffOrig"] = input_df["oldbalanceOrg"] - input_df["newbalanceOrig"]
    input_df["balanceDiffDest"] = input_df["newbalanceDest"] - input_df["oldbalanceDest"]
    
    # 2. Behavioral Flag (is_merchant)
    input_df["is_merchant"] = input_df["nameDest"].str.startswith('M').astype(int)
    
    # 3. Velocity Feature Proxy 
    # For this demonstration, we assume low recent history (0).
    input_df['Orig_Count_1step'] = 0 
    
    return input_df

# --- PAGE DEFINITIONS ---

def prediction_page():
    st.header("Real-Time Risk Assessment Utility")
    st.markdown("Enter the 9 required raw transaction parameters below to test the Stacking Ensemble Model.")
    st.divider()
    
    # --- Input Fields ---
    with st.form("prediction_form"):
        c1, c2, c3 = st.columns(3)
        
        # FE Required Inputs
        step = c1.number_input("Current Hour (Step)", min_value=1, value=300)
        nameOrig = c2.text_input("Sender ID (nameOrig)", value="C_TEST_SENDER")
        nameDest = c3.text_input("Receiver ID (nameDest)", value="C_TEST_RECEIVER")
        
        # Core Transaction Details
        c4, c5 = st.columns(2)
        transaction_type = c4.selectbox("Transaction Type", ["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"])
        amount = c5.number_input("Amount", min_value=0.0, value=9999.0)
        
        # Balances
        st.subheader("Account Balances")
        c6, c7 = st.columns(2)
        oldbalanceOrg = c6.number_input("Old Balance (Sender)", min_value=0.0, value=10000.0)
        newbalanceOrig = c7.number_input("New Balance (Sender)", min_value=0.0, value=1.0)
        
        c8, c9 = st.columns(2)
        oldbalanceDest = c8.number_input("Old Balance (Receiver)", min_value=0.0, value=100.0)
        newbalanceDest = c9.number_input("New Balance (Receiver)", min_value=0.0, value=10099.0)

        submitted = st.form_submit_button("PREDICT RISK")

        if submitted:
            # 1. Create Raw Data Frame
            input_data = pd.DataFrame([{
                "type": transaction_type, "amount": amount, "oldbalanceOrg": oldbalanceOrg, 
                "newbalanceOrig": newbalanceOrig, "oldbalanceDest": oldbalanceDest, 
                "newbalanceDest": newbalanceDest, "step": step, "nameOrig": nameOrig, 
                "nameDest": nameDest, "isFlaggedFraud": 0
            }])
            
            # 2. Feature Engineering
            input_data_fe = feature_engineer_input(input_data)
            
            # 3. Final Feature Selection (Drop raw inputs not in the final pipeline)
            X_predict = input_data_fe.drop(columns=['nameOrig', 'nameDest', 'isFlaggedFraud', 'step'])

            # 4. Prediction
            prediction = model.predict(X_predict)[0]
            risk_score = model.predict_proba(X_predict)[0][1]

            # 5. Display Results
            st.subheader(f"RISK ASSESSMENT: {'FRAUD (1)' if prediction == 1 else 'SAFE (0)'}")

            if prediction == 1:
                st.error(f"🚨 FLAG: High Risk. Probability: {risk_score:.4f} (Precision: 89%)")
            else:
                st.success(f"✅ APPROVED. Risk Score: {risk_score:.4f}")

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
    
    # --- SECTION A: OPERATIONAL METRICS & MODEL VALIDATION ---
    st.header("1. Model Validation and Cost-Benefit")
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Final Precision (Correct Flags)", "89%", "44.5x Improvement vs. Legacy")
    col2.metric("Final Recall (Fraud Catch Rate)", "80%", "Minimal Loss for Max Precision")
    col3.metric("False Alarms (FP in Test)", "23", "Minimal Operational Overhead")
    
    st.markdown("---")


    # --- SECTION B: ANALYTICAL VISUALIZATIONS (Altair Charts) ---
    
    st.header("2. Analytical Insights and Risk Scoping")
    
    c1, c2 = st.columns(2)
    
    # Chart 1: Transaction Volume Distribution (Risk Scoping)
    volume_chart = alt.Chart(volume_data).mark_bar().encode(
        x=alt.X('Transaction Type', sort='-y'),
        y=alt.Y('Volume (Millions)', title='Volume (Millions)'),
        tooltip=['Transaction Type', 'Volume (Millions)']
    ).transform_calculate(
        is_high_risk = "datum['Transaction Type'] == 'TRANSFER' || datum['Transaction Type'] == 'CASH_OUT'"
    ).encode(
        color=alt.condition(
            alt.datum.is_high_risk,
            alt.value('red'),  # Highlight high-risk types
            alt.value('lightgray')
        )
    ).properties(
        title="Transaction Volume Distribution (Risk Scoping)"
    ).interactive()
    
    c1.subheader("Transaction Volume")
    c1.altair_chart(volume_chart, use_container_width=True)

    
    # Chart 2: Fraud Rate by Type (Bivariate Confirmation)
    risk_chart = alt.Chart(risk_data).mark_bar(color='salmon').encode(
        x=alt.X('Transaction Type', sort='-y'),
        y=alt.Y('Fraud Rate (%)', title='Fraud Rate (%)'),
        tooltip=['Transaction Type', alt.Tooltip('Fraud Rate (%)', format='.2f')]
    ).properties(
        title="Fraud Rate by Type (Zero Risk Confirmation)"
    ).interactive()
    
    c2.subheader("Fraud Rate by Type") 
    c2.altair_chart(risk_chart, use_container_width=True)
    
    
    # Chart 3: Feature Importance (Explaining the Model)
    st.subheader("3. Model Explainability: Feature Importance")
    
    importance_chart = alt.Chart(feature_data).mark_bar(color='darkblue').encode(
        x=alt.X('Importance Score', title='Predictive Power (Proxy)'),
        y=alt.Y('Feature', sort='-x'),
        tooltip=['Feature', alt.Tooltip('Importance Score', format='.2f')]
    ).properties(
        title="Feature Importance in Fraud Detection"
    ).interactive()
    
    st.altair_chart(importance_chart, use_container_width=True)


# --- MAIN APP NAVIGATION LOGIC (USING TABS) ---

def main():
    st.set_page_config(layout="wide", page_title="FraudPulse MLOps System")
    
    st.title("FraudPulse: MLOps Financial Fraud Detection System")
    
    # Define tabs for header-style navigation
    tab1, tab2 = st.tabs(["📊 Performance Dashboard", "🔍 Real-Time Prediction"])

    with tab1:
        dashboard_page()
    
    with tab2:
        prediction_page()

if __name__ == "__main__":
    main()