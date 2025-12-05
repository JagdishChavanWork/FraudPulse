# app_modules/prediction_utility.py (CLEANED)

import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from database.database_connector import get_db
from database.models import PredictionLog 
import numpy as np

# --- HELPER FUNCTION: Feature Engineering ---

def feature_engineer_input(input_df: pd.DataFrame) -> pd.DataFrame:
    """Applies the custom feature engineering logic to raw input data."""
    
    input_df["balanceDiffOrig"] = input_df["oldbalanceOrg"] - input_df["newbalanceOrig"]
    input_df["balanceDiffDest"] = input_df["newbalanceDest"] - input_df["oldbalanceDest"]
    input_df["is_merchant"] = input_df["nameDest"].str.startswith('M').astype(int)
    input_df['Orig_Count_1step'] = 0 
    
    return input_df


# --- MAIN PAGE FUNCTION ---
# FIX: Function MUST accept the 'model' argument
def prediction_page(model): 
    st.header("Real-Time Risk Assessment Utility")
    st.markdown("Enter the 9 required raw transaction parameters below to test the Stacking Ensemble Model.")
    st.divider()
    
    # --- Input Fields ---
    with st.form("prediction_form"):
        c1, c2, c3 = st.columns(3)
        
        step = c1.number_input("Current Hour (Step)", min_value=1, value=300)
        nameOrig = c2.text_input("Sender ID (nameOrig)", value="C_TEST_SENDER")
        nameDest = c3.text_input("Receiver ID (nameDest)", value="C_TEST_RECEIVER")
        
        c4, c5 = st.columns(2)
        transaction_type = c4.selectbox("Transaction Type", ["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"])
        amount = c5.number_input("Amount", min_value=0.0, value=9999.0)
        
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
            
            # 3. Final Feature Selection 
            X_predict = input_data_fe.drop(columns=['nameOrig', 'nameDest', 'isFlaggedFraud', 'step'])

            # 4. Prediction
            prediction = model.predict(X_predict)[0] 
            risk_score = model.predict_proba(X_predict)[0][1]

            # --- 5. LOGGING THE PREDICTION ---
            try:
                db_generator = get_db()
                db: Session = next(db_generator)
                
                new_log = PredictionLog(
                    transaction_type=transaction_type, amount=amount, oldbalanceOrg=oldbalanceOrg, 
                    newbalanceOrig=newbalanceOrig, risk_score=risk_score, predicted_class=int(prediction)
                )
                db.add(new_log)
                db.commit()
                st.info("✅ Prediction logged successfully to database.")
            except Exception as e:
                st.warning(f"⚠️ Could not log prediction to DB. Error: {e}")
            finally:
                if 'db' in locals() and db:
                    db.close()


            # 6. Display Results
            st.subheader(f"RISK ASSESSMENT: {'FRAUD (1)' if prediction == 1 else 'SAFE (0)'}")

            if prediction == 1:
                st.error(f"🚨 FLAG: High Risk. Probability: {risk_score:.4f} (Precision: 89%)")
            else:
                st.success(f"✅ APPROVED. Risk Score: {risk_score:.4f}")