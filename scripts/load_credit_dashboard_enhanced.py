from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import CREDIT_DASHBOARD_DATASET
from database.connection import create_session, engine
from database.models import Base, CreditRiskDashboardEnhanced


COLUMN_MAP = {
    "pct_tl_open_L6M": "pct_tl_open_l6m",
    "pct_tl_closed_L6M": "pct_tl_closed_l6m",
    "Tot_TL_closed_L12M": "total_tl_closed_l12m",
    "pct_tl_closed_L12M": "pct_tl_closed_l12m",
    "Tot_Missed_Pmnt": "total_missed_payments",
    "CC_TL": "cc_tradelines",
    "Home_TL": "home_tradelines",
    "PL_TL": "personal_loan_tradelines",
    "Secured_TL": "secured_tradelines",
    "Unsecured_TL": "unsecured_tradelines",
    "Other_TL": "other_tradelines",
    "Age_Oldest_TL": "age_oldest_tradeline",
    "Age_Newest_TL": "age_newest_tradeline",
    "time_since_recent_payment": "time_since_recent_payment",
    "max_recent_level_of_deliq": "max_recent_delinquency_level",
    "num_deliq_6_12mts": "delinquencies_6_12m",
    "num_times_60p_dpd": "times_60p_dpd",
    "num_std_12mts": "standard_accounts_12m",
    "num_sub": "substandard_accounts",
    "num_sub_6mts": "substandard_accounts_6m",
    "num_sub_12mts": "substandard_accounts_12m",
    "num_dbt": "doubtful_accounts",
    "num_dbt_12mts": "doubtful_accounts_12m",
    "num_lss": "loss_accounts",
    "recent_level_of_deliq": "recent_delinquency_level",
    "CC_enq_L12m": "cc_enquiries_12m",
    "PL_enq_L12m": "pl_enquiries_12m",
    "time_since_recent_enq": "time_since_recent_enquiry",
    "enq_L3m": "enquiries_l3m",
    "NETMONTHLYINCOME": "net_monthly_income",
    "Time_With_Curr_Empr": "time_with_current_employer",
    "CC_Flag": "has_credit_card",
    "PL_Flag": "has_personal_loan",
    "HL_Flag": "has_home_loan",
    "GL_Flag": "has_gold_loan",
    "EDUCATION": "education_code",
    "Approved_Flag": "approved_flag",
    "Income_Bucket": "income_bucket",
    "Risk_Profile": "risk_profile",
}

NUMERIC_COLUMNS = [
    "pct_tl_open_l6m",
    "pct_tl_closed_l6m",
    "total_tl_closed_l12m",
    "pct_tl_closed_l12m",
    "total_missed_payments",
    "cc_tradelines",
    "home_tradelines",
    "personal_loan_tradelines",
    "secured_tradelines",
    "unsecured_tradelines",
    "other_tradelines",
    "age_oldest_tradeline",
    "age_newest_tradeline",
    "time_since_recent_payment",
    "max_recent_delinquency_level",
    "delinquencies_6_12m",
    "times_60p_dpd",
    "standard_accounts_12m",
    "substandard_accounts",
    "substandard_accounts_6m",
    "substandard_accounts_12m",
    "doubtful_accounts",
    "doubtful_accounts_12m",
    "loss_accounts",
    "recent_delinquency_level",
    "cc_enquiries_12m",
    "pl_enquiries_12m",
    "time_since_recent_enquiry",
    "enquiries_l3m",
    "net_monthly_income",
    "time_with_current_employer",
]

BOOLEAN_COLUMNS = [
    "has_credit_card",
    "has_personal_loan",
    "has_home_loan",
    "has_gold_loan",
]


def _decode_one_hot(row: pd.Series, prefix: str, values: list[str]) -> str | None:
    for value in values:
        if bool(row.get(f"{prefix}_{value}", False)):
            return value
    return None


def _decode_product(row: pd.Series, prefix: str) -> str | None:
    product_values = ["AL", "CC", "ConsumerLoan", "HL", "PL", "others"]
    return _decode_one_hot(row, prefix, product_values)


def normalize_dashboard_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing_columns = [column for column in COLUMN_MAP if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Enhanced dashboard dataset is missing required columns: {missing_columns}")

    normalized = frame.rename(columns=COLUMN_MAP)[list(COLUMN_MAP.values())].copy()
    normalized["marital_status"] = frame.apply(
        lambda row: _decode_one_hot(row, "MARITALSTATUS", ["Married", "Single"]),
        axis=1,
    )
    normalized["gender"] = frame.apply(lambda row: _decode_one_hot(row, "GENDER", ["F", "M"]), axis=1)
    normalized["last_product_enquiry"] = frame.apply(lambda row: _decode_product(row, "last_prod_enq2"), axis=1)
    normalized["first_product_enquiry"] = frame.apply(lambda row: _decode_product(row, "first_prod_enq2"), axis=1)

    for column in NUMERIC_COLUMNS:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    for column in BOOLEAN_COLUMNS:
        normalized[column] = normalized[column].astype("boolean")

    text_columns = [
        "education_code",
        "approved_flag",
        "marital_status",
        "gender",
        "last_product_enquiry",
        "first_product_enquiry",
        "income_bucket",
        "risk_profile",
    ]
    for column in text_columns:
        normalized[column] = normalized[column].astype("string").str.strip()

    normalized["source_file"] = path.name
    return normalized.where(pd.notna(normalized), None)


def load_credit_dashboard_enhanced(path: Path = CREDIT_DASHBOARD_DATASET, replace: bool = True) -> int:
    if not path.exists():
        raise FileNotFoundError(f"Enhanced dashboard dataset not found: {path}")

    Base.metadata.create_all(bind=engine)
    frame = normalize_dashboard_frame(path)

    with create_session() as session:
        if replace:
            session.query(CreditRiskDashboardEnhanced).delete()

        records = [CreditRiskDashboardEnhanced(**row) for row in frame.to_dict(orient="records")]
        session.add_all(records)
        session.commit()

    return len(frame)


if __name__ == "__main__":
    loaded_count = load_credit_dashboard_enhanced()
    print(f"Loaded {loaded_count:,} enhanced credit dashboard records into SQLite.")
