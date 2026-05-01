import pandas as pd
import streamlit as st

from config.settings import CREDIT_DASHBOARD_DATASET
from ml.credit_limit.predict import predict_max_credit_amount
from ml.credit_risk.predict import ENHANCED_MODEL_PATH, load_artifact, predict_enhanced_approved_flag
from modules.common.ui_helpers import page_header


PRODUCT_VALUES = ["AL", "CC", "ConsumerLoan", "HL", "PL", "others"]


@st.cache_data(show_spinner=False)
def _load_default_feature_values() -> dict:
    enhanced_artifact = load_artifact(ENHANCED_MODEL_PATH)
    feature_columns = enhanced_artifact["feature_columns"]

    frame = pd.read_csv(CREDIT_DASHBOARD_DATASET)
    defaults = {}
    for column in feature_columns:
        if column not in frame.columns:
            defaults[column] = False if _is_indicator_column(column) else 0
            continue

        series = frame[column]
        if pd.api.types.is_bool_dtype(series):
            defaults[column] = bool(series.mode(dropna=True).iloc[0])
        elif pd.api.types.is_numeric_dtype(series):
            defaults[column] = float(series.median())
        else:
            defaults[column] = series.mode(dropna=True).iloc[0]
    return defaults


def _is_indicator_column(column: str) -> bool:
    return (
        column.startswith("MARITALSTATUS_")
        or column.startswith("GENDER_")
        or column.startswith("last_prod_enq2_")
        or column.startswith("first_prod_enq2_")
    )


def _set_one_hot(payload: dict, prefix: str, selected_value: str, values: list[str]) -> None:
    for value in values:
        payload[f"{prefix}_{value}"] = value == selected_value


def _render_probability_table(class_probabilities: dict[str, float]) -> None:
    st.write("Class probabilities")
    st.dataframe(
        {
            "Class": list(class_probabilities.keys()),
            "Probability": [f"{value * 100:.1f}%" for value in class_probabilities.values()],
        },
        hide_index=True,
        use_container_width=True,
    )


def _build_prediction_payload(values: dict) -> dict:
    payload = _load_default_feature_values().copy()

    payload.update(
        {
            "NETMONTHLYINCOME": values["income"],
            "Time_With_Curr_Empr": values["employer_tenure"],
            "EDUCATION": values["education_code"],
            "Tot_Missed_Pmnt": values["missed_payments"],
            "Total_TL": values["total_tradelines"],
            "Tot_Active_TL": values["active_tradelines"],
            "Secured_TL": values["secured_tradelines"],
            "Unsecured_TL": values["unsecured_tradelines"],
            "CC_TL": values["credit_card_tradelines"],
            "PL_TL": values["personal_loan_tradelines"],
            "Home_TL": values["home_loan_tradelines"],
            "Total_TL_opened_L6M": values["opened_l6m"],
            "pct_tl_open_L6M": values["pct_open_l6m"] / 100,
            "pct_tl_closed_L6M": values["pct_closed_l6m"] / 100,
            "time_since_recent_enq": values["recent_enquiry_months"],
            "enq_L3m": values["enquiries_l3m"],
            "CC_enq_L12m": values["cc_enquiries_l12m"],
            "PL_enq_L12m": values["pl_enquiries_l12m"],
            "recent_level_of_deliq": values["recent_delinquency_level"],
            "max_recent_level_of_deliq": values["max_recent_delinquency_level"],
            "num_deliq_6_12mts": values["delinquencies_6_12m"],
            "num_times_60p_dpd": values["times_60p_dpd"],
            "CC_Flag": values["has_credit_card"],
            "PL_Flag": values["has_personal_loan"],
            "HL_Flag": values["has_home_loan"],
            "GL_Flag": values["has_gold_loan"],
        }
    )

    _set_one_hot(payload, "MARITALSTATUS", values["marital_status"], ["Married", "Single"])
    _set_one_hot(payload, "GENDER", values["gender"], ["F", "M"])
    _set_one_hot(payload, "last_prod_enq2", values["last_product_enquiry"], PRODUCT_VALUES)
    _set_one_hot(payload, "first_prod_enq2", values["first_product_enquiry"], PRODUCT_VALUES)
    return payload


def _estimate_credit_band(predicted_approval_flag: str, values: dict) -> int:
    if predicted_approval_flag == "P1":
        band = 5
    elif predicted_approval_flag == "P2":
        band = 4
    elif predicted_approval_flag == "P3":
        band = 3
    else:
        band = 2

    if values["missed_payments"] > 2 or values["recent_delinquency_level"] > 0:
        band -= 1
    if values["income"] > 60000 and values["active_tradelines"] >= 4:
        band += 1
    return min(5, max(1, band))


def _build_amount_payload(values: dict, predicted_approval_flag: str) -> dict:
    return {
        "AGE": values["age"],
        "EDUCATION": values["education_label"],
        "GENDER": values["gender"],
        "MARITALSTATUS": values["marital_status"],
        "NETMONTHLYINCOME": values["income"],
        "Time_With_Curr_Empr": values["employer_tenure"],
        "Total_TL": values["total_tradelines"],
        "Tot_Active_TL": values["active_tradelines"],
        "Total_TL_opened_L6M": values["opened_l6m"],
        "time_since_recent_enq": values["recent_enquiry_months"],
        "Credit_Band": _estimate_credit_band(predicted_approval_flag, values),
    }


def render_credit_prediction() -> None:
    page_header(
        "Credit Risk Prediction",
        "Analyst-assisted approval class prediction from applicant, bureau, enquiry, and tradeline inputs.",
    )

    left, right = st.columns([1.25, 0.75])
    with left:
        with st.form("credit_prediction_form"):
            st.subheader("Applicant Profile")
            col0, col1, col2, col3 = st.columns(4)
            age = col0.number_input("Applicant age", min_value=18, max_value=80, value=35)
            income = col1.number_input("Net monthly income", min_value=0, value=45000, step=1000)
            employer_tenure = col2.number_input("Current employer tenure", min_value=0, value=36)
            education_label = col3.selectbox(
                "Education",
                ["SSC", "12TH", "GRADUATE", "POST-GRADUATE"],
                index=2,
            )

            col4, col5 = st.columns(2)
            gender = col4.selectbox("Gender", ["M", "F"])
            marital_status = col5.selectbox("Marital status", ["Single", "Married"])

            st.subheader("Bureau & Tradeline Summary")
            col6, col7, col8 = st.columns(3)
            total_tradelines = col6.number_input("Total tradelines", min_value=0, value=8)
            active_tradelines = col7.number_input("Active tradelines", min_value=0, value=4)
            opened_l6m = col8.number_input("Tradelines opened L6M", min_value=0, value=1)

            col9, col10, col11 = st.columns(3)
            secured_tradelines = col9.number_input("Secured tradelines", min_value=0, value=3)
            unsecured_tradelines = col10.number_input("Unsecured tradelines", min_value=0, value=4)
            credit_card_tradelines = col11.number_input("Credit card tradelines", min_value=0, value=1)

            col12, col13 = st.columns(2)
            personal_loan_tradelines = col12.number_input("Personal loan tradelines", min_value=0, value=1)
            home_loan_tradelines = col13.number_input("Home loan tradelines", min_value=0, value=0)

            with st.expander("Advanced bureau indicators", expanded=False):
                col14, col15, col16 = st.columns(3)
                missed_payments = col14.number_input("Total missed payments", min_value=0, value=0)
                recent_delinquency_level = col15.number_input("Recent delinquency level", min_value=0, value=0)
                max_recent_delinquency_level = col16.number_input("Max recent delinquency level", min_value=0, value=0)

                col17, col18, col19 = st.columns(3)
                delinquencies_6_12m = col17.number_input("Delinquencies 6-12M", min_value=0, value=0)
                times_60p_dpd = col18.number_input("60+ DPD count", min_value=0, value=0)
                recent_enquiry_months = col19.number_input("Months since recent enquiry", min_value=0, value=6)

                col20, col21, col22 = st.columns(3)
                enquiries_l3m = col20.number_input("Enquiries L3M", min_value=0, value=1)
                cc_enquiries_l12m = col21.number_input("CC enquiries L12M", min_value=0, value=0)
                pl_enquiries_l12m = col22.number_input("PL enquiries L12M", min_value=0, value=0)

                col23, col24 = st.columns(2)
                pct_open_l6m = col23.slider("Open tradeline % L6M", 0, 100, 10)
                pct_closed_l6m = col24.slider("Closed tradeline % L6M", 0, 100, 5)

                col25, col26 = st.columns(2)
                first_product_enquiry = col25.selectbox("First product enquiry", PRODUCT_VALUES, index=5)
                last_product_enquiry = col26.selectbox("Last product enquiry", PRODUCT_VALUES, index=5)

                col27, col28, col29, col30 = st.columns(4)
                has_credit_card = col27.checkbox("CC flag", value=credit_card_tradelines > 0)
                has_personal_loan = col28.checkbox("PL flag", value=personal_loan_tradelines > 0)
                has_home_loan = col29.checkbox("HL flag", value=home_loan_tradelines > 0)
                has_gold_loan = col30.checkbox("GL flag", value=False)

            education_map = {"SSC": 1, "12TH": 2, "GRADUATE": 3, "POST-GRADUATE": 4}
            submitted = st.form_submit_button("Analyze Credit Profile", use_container_width=True)

    with right:
        st.subheader("AI Recommendation")
        if submitted:
            values = {
                "age": age,
                "income": income,
                "employer_tenure": employer_tenure,
                "education_label": education_label,
                "education_code": education_map[education_label],
                "gender": gender,
                "marital_status": marital_status,
                "total_tradelines": total_tradelines,
                "active_tradelines": active_tradelines,
                "opened_l6m": opened_l6m,
                "secured_tradelines": secured_tradelines,
                "unsecured_tradelines": unsecured_tradelines,
                "credit_card_tradelines": credit_card_tradelines,
                "personal_loan_tradelines": personal_loan_tradelines,
                "home_loan_tradelines": home_loan_tradelines,
                "missed_payments": missed_payments,
                "recent_delinquency_level": recent_delinquency_level,
                "max_recent_delinquency_level": max_recent_delinquency_level,
                "delinquencies_6_12m": delinquencies_6_12m,
                "times_60p_dpd": times_60p_dpd,
                "recent_enquiry_months": recent_enquiry_months,
                "enquiries_l3m": enquiries_l3m,
                "cc_enquiries_l12m": cc_enquiries_l12m,
                "pl_enquiries_l12m": pl_enquiries_l12m,
                "pct_open_l6m": pct_open_l6m,
                "pct_closed_l6m": pct_closed_l6m,
                "first_product_enquiry": first_product_enquiry,
                "last_product_enquiry": last_product_enquiry,
                "has_credit_card": has_credit_card,
                "has_personal_loan": has_personal_loan,
                "has_home_loan": has_home_loan,
                "has_gold_loan": has_gold_loan,
            }
            try:
                result = predict_enhanced_approved_flag(_build_prediction_payload(values))
                amount_result = predict_max_credit_amount(
                    _build_amount_payload(values, result["predicted_approved_flag"])
                )
                st.metric("Predicted approval category", result["predicted_approved_flag"])
                st.metric("Model confidence", f"{result['confidence'] * 100:.1f}%")
                st.metric("Maximum credit amount", f"Rs. {amount_result['rounded_max_credit_amount']:,.0f}")
                _render_probability_table(result["class_probabilities"])
            except FileNotFoundError as exc:
                st.info(str(exc))
        else:
            st.metric("Predicted approval category", "Awaiting input")
            st.metric("Model confidence", "Awaiting input")
            st.metric("Maximum credit amount", "Next model phase")
            st.caption("Enter applicant and bureau indicators, then analyze the profile.")
