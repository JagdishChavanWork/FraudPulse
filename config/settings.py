import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "FraudPulse"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fraudpulse"
)