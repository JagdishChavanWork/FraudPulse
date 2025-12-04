# database/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.sql import func
# Note: The relative import below requires the __init__.py file to work correctly
from .database_connector import Base 
import datetime

# --- 1. Employee Authentication Table ---
class Employee(Base):
    """Defines the structure for the employee login table."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# --- 2. Prediction Log Table (For Future Reference/Reporting) ---
class PredictionLog(Base):
    """Defines the structure for logging real-time prediction results."""
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Raw Transaction Inputs
    transaction_type = Column(String)
    amount = Column(Float)
    oldbalanceOrg = Column(Float)
    newbalanceOrig = Column(Float)
    
    # Model Output
    risk_score = Column(Float)
    predicted_class = Column(Integer)
    
    # MLOps Context
    model_version = Column(String, default="1.0_Stacking_Ensemble")
    timestamp = Column(DateTime, default=func.now())