import pandas as pd

from database.connection import engine


CREDIT_DISPLAY_COLUMNS = {
    "age": "Age",
    "education": "Education",
    "gender": "Gender",
    "marital_status": "Marital Status",
    "net_monthly_income": "Net Monthly Income",
    "time_with_current_employer": "Employer Tenure Months",
    "total_tradelines": "Total Tradelines",
    "active_tradelines": "Active Tradelines",
    "tradelines_opened_last_6m": "Tradelines Opened L6M",
    "time_since_recent_enquiry": "Months Since Recent Enquiry",
    "approved_flag": "Approved Flag",
    "credit_band": "Credit Band",
    "max_credit_amount": "Max Credit Amount",
}


def get_credit_risk_data() -> pd.DataFrame:
    query = """
        SELECT
            age,
            education,
            gender,
            marital_status,
            net_monthly_income,
            time_with_current_employer,
            total_tradelines,
            active_tradelines,
            tradelines_opened_last_6m,
            time_since_recent_enquiry,
            approved_flag,
            credit_band,
            max_credit_amount
        FROM credit_risk_data
        ORDER BY id DESC
    """
    return pd.read_sql_query(query, con=engine)


def get_credit_dashboard_enhanced_data() -> pd.DataFrame:
    query = """
        SELECT
            pct_tl_open_l6m,
            pct_tl_closed_l6m,
            total_tl_closed_l12m,
            pct_tl_closed_l12m,
            total_missed_payments,
            cc_tradelines,
            home_tradelines,
            personal_loan_tradelines,
            secured_tradelines,
            unsecured_tradelines,
            other_tradelines,
            age_oldest_tradeline,
            age_newest_tradeline,
            time_since_recent_payment,
            max_recent_delinquency_level,
            delinquencies_6_12m,
            times_60p_dpd,
            standard_accounts_12m,
            substandard_accounts,
            substandard_accounts_6m,
            substandard_accounts_12m,
            doubtful_accounts,
            doubtful_accounts_12m,
            loss_accounts,
            recent_delinquency_level,
            cc_enquiries_12m,
            pl_enquiries_12m,
            time_since_recent_enquiry,
            enquiries_l3m,
            net_monthly_income,
            time_with_current_employer,
            has_credit_card,
            has_personal_loan,
            has_home_loan,
            has_gold_loan,
            education_code,
            approved_flag,
            marital_status,
            gender,
            last_product_enquiry,
            first_product_enquiry,
            income_bucket,
            risk_profile
        FROM credit_risk_dashboard_enhanced
        ORDER BY id DESC
    """
    return pd.read_sql_query(query, con=engine)


def get_enhanced_prediction_records(limit: int = 250) -> pd.DataFrame:
    query = f"""
        SELECT
            id,
            approved_flag,
            risk_profile,
            income_bucket,
            net_monthly_income,
            total_missed_payments,
            time_since_recent_enquiry,
            enquiries_l3m,
            recent_delinquency_level,
            last_product_enquiry,
            first_product_enquiry
        FROM credit_risk_dashboard_enhanced
        ORDER BY id DESC
        LIMIT {int(limit)}
    """
    return pd.read_sql_query(query, con=engine)


def get_enhanced_prediction_payload(record_id: int) -> dict:
    query = """
        SELECT *
        FROM credit_risk_dashboard_enhanced
        WHERE id = ?
        LIMIT 1
    """
    frame = pd.read_sql_query(query, con=engine, params=(record_id,))
    if frame.empty:
        raise ValueError(f"Enhanced credit record not found: {record_id}")

    row = frame.iloc[0].to_dict()
    reverse_column_map = {
        "pct_tl_open_l6m": "pct_tl_open_L6M",
        "pct_tl_closed_l6m": "pct_tl_closed_L6M",
        "total_tl_closed_l12m": "Tot_TL_closed_L12M",
        "pct_tl_closed_l12m": "pct_tl_closed_L12M",
        "total_missed_payments": "Tot_Missed_Pmnt",
        "cc_tradelines": "CC_TL",
        "home_tradelines": "Home_TL",
        "personal_loan_tradelines": "PL_TL",
        "secured_tradelines": "Secured_TL",
        "unsecured_tradelines": "Unsecured_TL",
        "other_tradelines": "Other_TL",
        "age_oldest_tradeline": "Age_Oldest_TL",
        "age_newest_tradeline": "Age_Newest_TL",
        "time_since_recent_payment": "time_since_recent_payment",
        "max_recent_delinquency_level": "max_recent_level_of_deliq",
        "delinquencies_6_12m": "num_deliq_6_12mts",
        "times_60p_dpd": "num_times_60p_dpd",
        "standard_accounts_12m": "num_std_12mts",
        "substandard_accounts": "num_sub",
        "substandard_accounts_6m": "num_sub_6mts",
        "substandard_accounts_12m": "num_sub_12mts",
        "doubtful_accounts": "num_dbt",
        "doubtful_accounts_12m": "num_dbt_12mts",
        "loss_accounts": "num_lss",
        "recent_delinquency_level": "recent_level_of_deliq",
        "cc_enquiries_12m": "CC_enq_L12m",
        "pl_enquiries_12m": "PL_enq_L12m",
        "time_since_recent_enquiry": "time_since_recent_enq",
        "enquiries_l3m": "enq_L3m",
        "net_monthly_income": "NETMONTHLYINCOME",
        "time_with_current_employer": "Time_With_Curr_Empr",
        "has_credit_card": "CC_Flag",
        "has_personal_loan": "PL_Flag",
        "has_home_loan": "HL_Flag",
        "has_gold_loan": "GL_Flag",
        "education_code": "EDUCATION",
    }
    payload = {model_column: row[db_column] for db_column, model_column in reverse_column_map.items()}

    marital_status = row.get("marital_status")
    gender = row.get("gender")
    last_product = row.get("last_product_enquiry")
    first_product = row.get("first_product_enquiry")
    product_values = ["AL", "CC", "ConsumerLoan", "HL", "PL", "others"]

    payload["MARITALSTATUS_Married"] = marital_status == "Married"
    payload["MARITALSTATUS_Single"] = marital_status == "Single"
    payload["GENDER_F"] = gender == "F"
    payload["GENDER_M"] = gender == "M"
    for value in product_values:
        payload[f"last_prod_enq2_{value}"] = last_product == value
        payload[f"first_prod_enq2_{value}"] = first_product == value

    return payload


def apply_credit_filters(
    frame: pd.DataFrame,
    approved_flags: list[str],
    credit_bands: list[str],
    income_range: tuple[float, float],
    age_range: tuple[float, float],
) -> pd.DataFrame:
    filtered = frame.copy()

    if approved_flags:
        filtered = filtered[filtered["approved_flag"].isin(approved_flags)]
    if credit_bands:
        filtered = filtered[filtered["credit_band"].isin(credit_bands)]

    filtered = filtered[
        filtered["net_monthly_income"].between(income_range[0], income_range[1], inclusive="both")
        & filtered["age"].between(age_range[0], age_range[1], inclusive="both")
    ]
    return filtered


def apply_enhanced_filters(
    frame: pd.DataFrame,
    approved_flags: list[str],
    income_range: tuple[float, float],
) -> pd.DataFrame:
    filtered = frame.copy()

    if approved_flags:
        filtered = filtered[filtered["approved_flag"].isin(approved_flags)]

    filtered = filtered[
        filtered["net_monthly_income"].between(income_range[0], income_range[1], inclusive="both")
    ]
    return filtered
