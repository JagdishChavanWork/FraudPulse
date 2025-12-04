import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime

# --- 1. CONFIGURATION & MODEL LOADING PATH ---

# 🛑 CHANGE 1: Use the final MLOps deployment path for the saved pipeline.
MODEL_PATH = r"E:\FraudPulse\models\fraud_detection_deployment_pipeline.pkl" 

# Use a try-except block for robust loading
try:
    # 🛑 CHANGE 2: Use the correct path variable and handle loading errors.
    model = joblib.load(MODEL_PATH)
    st.sidebar.success("✅ Model Pipeline Loaded")
except FileNotFoundError:
    st.error(f"❌ ERROR: Model file not found at {MODEL_PATH}. Check file path.")
    st.stop()
except Exception as e:
    st.error(f"❌ ERROR loading model: {e}")
    st.stop()


# --- 2. INPUT FIELDS & UI ---
st.title("FraudPulse: Real-Time Risk Assessment")
st.markdown("Enter The Transaction Details (Requires FE Parameters)")
st.divider()

# 🛑 CHANGE 3: Add inputs for all features required for Feature Engineering (FE)
c1, c2 = st.columns(2)
step = c1.number_input("Current Hour of Day (Step)", min_value=1, max_value=744, value=300)
transaction_type = c2.selectbox("Transaction Type", ["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"])

# Core Balances
amount = st.number_input("Amount", min_value=0.0, value=9999.0)
oldbalanceOrg = st.number_input("Old Balance (Sender)", min_value=0.0, value=10000.0)
newbalanceOrig = st.number_input("New Balance (Sender)", min_value=0.0, value=1.0)
oldbalanceDest = st.number_input("Old Balance (Receiver)", min_value=0.0, value=100.0)
newbalanceDest = st.number_input("New Balance (Receiver)", min_value=0.0, value=10099.0)

# 🛑 CHANGE 4: Add Sender/Receiver IDs for FE checks (is_merchant, velocity)
nameOrig = st.text_input("Sender ID (nameOrig)", value="C_TEST_SENDER")
nameDest = st.text_input("Receiver ID (nameDest)", value="C_TEST_RECEIVER")


# --- 3. PREDICTION LOGIC & FEATURE ENGINEERING ---
if st.button("PREDICT RISK"):
    # 1. Create Raw Data Frame
    input_data = pd.DataFrame([{
        "type": transaction_type,
        "amount": amount,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest,
        "step": step,
        "nameOrig": nameOrig,
        "nameDest": nameDest,
        "isFlaggedFraud": 0 # Placeholder for consistent column count (optional but safer)
    }])

    # 🛑 CHANGE 5: Perform Feature Engineering in Real-Time (MUST match training logic)
    
    # a. Core Predictor (Balance Difference)
    input_data["balanceDiffOrig"] = input_data["oldbalanceOrg"] - input_data["newbalanceOrig"]
    input_data["balanceDiffDest"] = input_data["newbalanceDest"] - input_data["oldbalanceDest"]
    
    # b. Behavioral Flag (is_merchant)
    input_data["is_merchant"] = input_data["nameDest"].str.startswith('M').astype(int)
    
    # c. Velocity Feature Proxy (MUST be added, but hardcoded for MVP demo)
    # In a production API, this would query a database; here we assume low velocity (0).
    input_data['Orig_Count_1step'] = 0 
    
    # 2. Final Feature Selection
    # 🛑 CHANGE 6: Drop raw columns not expected by the ColumnTransformer/Model
    X_predict = input_data.drop(columns=['nameOrig', 'nameDest', 'isFlaggedFraud', 'step'])

    # 3. Prediction
    prediction = model.predict(X_predict)[0]
    risk_score = model.predict_proba(X_predict)[0][1] # Get confidence score

    # 4. Display Results (Enhanced)
    st.subheader(f"RISK ASSESSMENT: {'FRAUD (1)' if prediction == 1 else 'SAFE (0)'}")

    if prediction == 1:
        st.error(f"🚨 TRANSACTION FLAGGED AS HIGH RISK! (Probability: {risk_score:.4f})")
    else:
        st.success(f"✅ Transaction Approved. (Risk Score: {risk_score:.4f})")