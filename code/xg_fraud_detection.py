import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime

# --- Configuration ---
MODEL_PATH = r"E:\FraudPulse\models\fraud_detection_deployment_pipeline.pkl"

# --- Load the Robust Pipeline ---
# This single asset contains the preprocessor (scaling, encoding, imputation) and the XGBoost model.
try:
    # Ensure the path is correct before loading
    if not os.path.exists(MODEL_PATH):
        st.error(f"❌ Model file not found at the specified path: {MODEL_PATH}")
        st.stop()
        
    xgb_pipeline = joblib.load(MODEL_PATH)
    st.sidebar.success("✅ Model Pipeline Loaded")
except Exception as e:
    st.error(f"❌ Error loading pipeline: {e}")
    st.stop()


# --- Streamlit UI Setup ---
st.title("FraudPulse: Real-Time Transaction Risk Assessment")
st.markdown("### For Financial Institutions and Stakeholders")
st.divider()

# --- Input Fields ---
st.subheader("Transaction Parameters (Required Inputs)")

# The 'step' column is now an input, representing the current hour of the simulation/day
step = st.number_input("Current Hour of Day (Step)", min_value=1, max_value=744, value=300)

transaction_type = st.selectbox("Transaction Type", ["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"])
amount = st.number_input("Amount", min_value=0.0, value=1000.0)
oldbalanceOrg = st.number_input("Old Balance (Sender)", min_value=0.0, value=10000.0)
newbalanceOrig = st.number_input("New Balance (Sender)", min_value=0.0, value=9000.0)
oldbalanceDest = st.number_input("Old Balance (Receiver)", min_value=0.0, value=0.0)
newbalanceDest = st.number_input("New Balance (Receiver)", min_value=0.0, value=0.0)

# We include mock fields for columns needed for Feature Engineering (FE), even if they're dropped later
nameOrig = st.text_input("Sender ID (C or M)", value="C123456789")
nameDest = st.text_input("Receiver ID (C or M)", value="C987654321")


# --- Prediction Logic ---
if st.button("PREDICT RISK"):
    # 1. Create a DataFrame from the raw inputs
    input_data = pd.DataFrame([{
        "type": transaction_type,
        "amount": amount,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest,
        "step": step,
        "nameOrig": nameOrig, # Needed for Orig_Count_1step (FE)
        "nameDest": nameDest, # Needed for is_merchant (FE)
        "isFlaggedFraud": 0 # Placeholder, as the model was trained with this column's index
    }])
    
    # 2. FEATURE ENGINEERING (MUST be done before prediction, matching training data)
    
    # a. Difference Features (Core Predictors)
    input_data["balanceDiffOrig"] = input_data["oldbalanceOrg"] - input_data["newbalanceOrig"]
    input_data["balanceDiffDest"] = input_data["newbalanceDest"] - input_data["oldbalanceDest"]
    
    # b. Behavioral Flag
    input_data["is_merchant"] = input_data["nameDest"].str.startswith('M').astype(int)
    
    # c. Velocity Feature Proxy (Based on our simplified training feature)
    # In a real API, this would require querying a database for 'nameOrig' activity in the last hour.
    # For the MVP demo, we assume no recent history (0) unless specified.
    # We will assume a fixed value for demonstration purposes:
    input_data['Orig_Count_1step'] = 0 
    
    # 3. Data Cleaning / Feature Selection
    # Drop all columns the pipeline expects to NOT see (IDs, time, etc.)
    X_predict = input_data.drop(columns=[
        'nameOrig', 'nameDest', 'isFlaggedFraud', 'step'
    ])
    
    # 4. Prediction
    prediction = xgb_pipeline.predict(X_predict)[0]
    risk_score = xgb_pipeline.predict_proba(X_predict)[0][1]
    
    # --- 5. Display Results ---
    st.subheader(f"RISK ASSESSMENT: {'FRAUD (1)' if prediction == 1 else 'SAFE (0)'}")
    
    if prediction == 1:
        st.error(f"🚨 TRANSACTION FLAGGED AS HIGH RISK! (Probability: {risk_score:.4f})")
    else:
        st.success(f"✅ Transaction Approved. (Probability of Fraud: {risk_score:.4f})")
        
    st.write("---")
    st.markdown("###### Model Confidence Breakdown")
    st.json({
        "Predicted Class": int(prediction),
        "Probability of Fraud": f"{risk_score:.6f}",
        "Deployment Pipeline Used": "XGBoost + Robust Preprocessor"
    })