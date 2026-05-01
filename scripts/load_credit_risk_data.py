from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import CREDIT_MODEL_DATASET
from database.connection import create_session, engine
from database.models import Base, CreditRiskData


COLUMN_MAP = {
    "AGE": "age",
    "EDUCATION": "education",
    "GENDER": "gender",
    "MARITALSTATUS": "marital_status",
    "NETMONTHLYINCOME": "net_monthly_income",
    "Time_With_Curr_Empr": "time_with_current_employer",
    "Total_TL": "total_tradelines",
    "Tot_Active_TL": "active_tradelines",
    "Total_TL_opened_L6M": "tradelines_opened_last_6m",
    "time_since_recent_enq": "time_since_recent_enquiry",
    "Approved_Flag": "approved_flag",
    "Credit_Band": "credit_band",
    "Max_Credit_Amount": "max_credit_amount",
}

NUMERIC_COLUMNS = [
    "age",
    "net_monthly_income",
    "time_with_current_employer",
    "total_tradelines",
    "active_tradelines",
    "tradelines_opened_last_6m",
    "time_since_recent_enquiry",
    "max_credit_amount",
]


def load_source_frame(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def normalize_credit_risk_frame(path: Path) -> pd.DataFrame:
    frame = load_source_frame(path)
    missing_columns = [column for column in COLUMN_MAP if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Credit risk dataset is missing required columns: {missing_columns}")

    normalized = frame.rename(columns=COLUMN_MAP)[list(COLUMN_MAP.values())].copy()
    for column in NUMERIC_COLUMNS:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    text_columns = ["education", "gender", "marital_status", "approved_flag", "credit_band"]
    for column in text_columns:
        normalized[column] = normalized[column].astype("string").str.strip()

    normalized["source_file"] = path.name
    return normalized.where(pd.notna(normalized), None)


def load_credit_risk_data(path: Path = CREDIT_MODEL_DATASET, replace: bool = True) -> int:
    if not path.exists():
        raise FileNotFoundError(f"Credit risk dataset not found: {path}")

    Base.metadata.create_all(bind=engine)
    frame = normalize_credit_risk_frame(path)

    with create_session() as session:
        if replace:
            session.query(CreditRiskData).delete()

        records = [CreditRiskData(**row) for row in frame.to_dict(orient="records")]
        session.add_all(records)
        session.commit()

    return len(frame)


if __name__ == "__main__":
    loaded_count = load_credit_risk_data()
    print(f"Loaded {loaded_count:,} credit risk records into SQLite.")
