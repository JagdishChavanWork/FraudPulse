import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "fraudpulse.db"

APP_NAME = "FraudPulse"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

CREDIT_DASHBOARD_DATASET = PROCESSED_DATA_DIR / "Dashboard_Data_Enhanced.csv"
CREDIT_MODEL_DATASET = PROCESSED_DATA_DIR / "credit_risk_dataset_with_bands.xlsx"
FRAUD_DATASET = PROCESSED_DATA_DIR / "fraud_dataset_v2.csv"
