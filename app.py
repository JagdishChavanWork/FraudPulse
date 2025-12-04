import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime
import numpy as np
import altair as alt

# --- MLOPS IMPORTS ---
from database.database_connector import get_db
from database.auth_manager import authenticate_user, add_new_employee, update_employee, delete_employee, get_all_employees
from sqlalchemy.orm import Session 
from database.models import PredictionLog, Employee 

# --- CRITICAL FIX: IMPORT MODULED PAGES FROM APP_MODULES ---
# These imports rely on the functions existing in your app_modules/ files.
from app_modules.dashboard_reports import dashboard_page
from app_modules.prediction_utility import prediction_page
from app_modules.admin_management import admin_management_page 


# --- CONFIGURATION & MODEL LOADING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
MODEL_NAME = "fraud_detection_deployment_pipeline.pkl"
MODEL_PATH = os.path.join(BASE_DIR, "models", MODEL_NAME)


@st.cache_resource
def load_model():
    """Loads the Stacking Ensemble Pipeline with its preprocessor."""
    try:
        if not os.path.exists(MODEL_PATH):
            st.error(f"❌ CRITICAL ERROR: Model file not found at expected path: {MODEL_PATH}")
            st.warning("Please ensure the 'models' folder is next to app.py.")
            st.stop()
        
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
    
    input_df["balanceDiffOrig"] = input_df["oldbalanceOrg"] - input_df["newbalanceOrig"]
    input_df["balanceDiffDest"] = input_df["newbalanceDest"] - input_df["oldbalanceDest"]
    input_df["is_merchant"] = input_df["nameDest"].str.startswith('M').astype(int)
    input_df['Orig_Count_1step'] = 0 
    
    return input_df

# --- PAGE DEFINITIONS (Integrated) ---

def login_page():
    """Renders the employee login form (The Authentication Gate)."""
    st.set_page_config(layout="centered", page_title="FraudPulse Login")
    st.title("🛡️ Employee Login Required")
    st.markdown("Access restricted to FraudPulse analysts and risk officers.")
    st.divider()

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

    if submitted:
        db_generator = get_db()
        db: Session = next(db_generator)
        
        user = authenticate_user(db, username, password)
        
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = user.username
            st.session_state['is_admin'] = user.is_admin
            st.session_state['user_id'] = user.id
            st.success("Login Successful! Redirecting to Dashboard...")
            st.rerun()
        else:
            st.error("Invalid username or password.")

# --- MAIN APP ENTRY POINT (Login and Navigation Control) ---

def main():
    st.set_page_config(layout="wide", page_title="FraudPulse MLOps System")
    
    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['is_admin'] = False
        st.session_state['username'] = None
    
    # 1. AUTHENTICATION GATE
    if not st.session_state.get('logged_in'):
        login_page()
        return 

    # 2. LOGGED-IN NAVIGATION
    st.sidebar.title(f"Welcome, {st.session_state.get('username')}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update(logged_in=False, username=None, is_admin=False, user_id=None))
    
    st.title("FraudPulse: MLOps Financial Fraud Detection System")
    
    # --- RBAC: Define Available Pages ---
    is_admin = st.session_state.get('is_admin', False)
    
    # Base set of tabs
    page_options = ["🔍 Real-Time Prediction"]
    
    if is_admin:
        page_options.insert(0, "📊 Performance Dashboard")
        page_options.append("🔐 Admin Management")

    # The actual navigation widget (placed in the sidebar)
    selected_page = st.sidebar.radio("Go to Page", page_options, key="sidebar_nav")

    # --- Conditional Page Rendering ---
    
    # FIX: Use lambda to correctly pass the global 'model' object where required.
    page_map = {
        "📊 Performance Dashboard": dashboard_page,
        "🔍 Real-Time Prediction": lambda: prediction_page(model), # CORRECTED CALL
        "🔐 Admin Management": admin_management_page
    }

    # Render content based on the sidebar selection
    if selected_page in page_map:
        page_map[selected_page]()


if __name__ == "__main__":
    main()