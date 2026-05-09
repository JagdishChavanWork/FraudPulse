import pandas as pd
import streamlit as st

from modules.common.charts import box_by_category, count_bar, histogram, scatter_segment
from modules.common.ui_helpers import (
    format_currency,
    format_number,
    format_years_from_months,
    kpi_card,
    page_header,
)
from modules.services.credit_risk_service import (
    CREDIT_DISPLAY_COLUMNS,
    apply_credit_filters,
    apply_enhanced_filters,
    get_credit_dashboard_enhanced_data,
    get_credit_risk_data,
)


def _safe_range(series: pd.Series) -> tuple[float, float]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return 0.0, 0.0
    return float(clean.min()), float(clean.max())


def _render_filters(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str], tuple[float, float]]:
    with st.expander("Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)

        approved_options = sorted(frame["approved_flag"].dropna().astype(str).unique())
        credit_band_options = sorted(frame["credit_band"].dropna().astype(str).unique())
        income_min, income_max = _safe_range(frame["net_monthly_income"])
        age_min, age_max = _safe_range(frame["age"])

        approved_flags = col1.multiselect(
            "ApprovedFlag",
            approved_options,
            default=approved_options,
        )
        credit_bands = col2.multiselect(
            "CreditBand",
            credit_band_options,
            default=credit_band_options,
        )
        income_range = col3.slider(
            "Monthly income",
            min_value=float(income_min),
            max_value=float(income_max),
            value=(float(income_min), float(income_max)),
        )
        age_range = col4.slider(
            "Age",
            min_value=float(age_min),
            max_value=float(age_max),
            value=(float(age_min), float(age_max)),
        )

    filtered = apply_credit_filters(frame, approved_flags, credit_bands, income_range, age_range)
    return filtered, approved_flags, income_range


def _render_kpis(frame: pd.DataFrame) -> None:
    total_records = len(frame)
    avg_income = frame["net_monthly_income"].mean()
    median_income = frame["net_monthly_income"].median()
    avg_age = frame["age"].mean()
    avg_tenure = frame["time_with_current_employer"].mean()
    avg_max_credit = frame["max_credit_amount"].mean()
    p4_rate = 0.0 if total_records == 0 else frame["approved_flag"].eq("P4").mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Applicant Records", format_number(total_records), "From SQLite credit_risk_data")
    with col2:
        kpi_card("Average Income", format_currency(avg_income), f"Median {format_currency(median_income)}")
    with col3:
        kpi_card("Average Age", f"{avg_age:.1f} yrs", f"Avg tenure {format_years_from_months(avg_tenure)}")
    with col4:
        kpi_card("Avg Max Credit", format_currency(avg_max_credit), f"P4 share {p4_rate:.1f}%")


def _render_story_kpis(frame: pd.DataFrame) -> None:
    total_records = len(frame)
    avg_missed = frame["total_missed_payments"].mean()
    avg_enquiries = frame["enquiries_l3m"].mean()
    delinquency_share = 0.0 if total_records == 0 else frame["recent_delinquency_level"].gt(0).mean() * 100
    unsecured_share = 0.0
    total_tl = frame["secured_tradelines"].fillna(0) + frame["unsecured_tradelines"].fillna(0)
    has_tl = total_tl.gt(0)
    if has_tl.any():
        unsecured_share = (frame.loc[has_tl, "unsecured_tradelines"] / total_tl[has_tl]).mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Enhanced BI Records", format_number(total_records), "From Dashboard_Data_Enhanced.csv")
    with col2:
        kpi_card("Avg Missed Payments", f"{avg_missed:.2f}", "Portfolio repayment pressure")
    with col3:
        kpi_card("Recent Delinquency", f"{delinquency_share:.1f}%", "Records with delinquency signal")
    with col4:
        kpi_card("Avg L3M Enquiries", f"{avg_enquiries:.2f}", f"Unsecured mix {unsecured_share:.1f}%")


def _chart_note(text: str) -> None:
    st.caption(f"Insight: {text}")


def render_credit_dashboard(show_header: bool = True) -> None:
    if show_header:
        page_header(
            "Credit Risk Dashboard",
            "Portfolio view of applicant approvals, credit bands, income strength, repayment pressure, and recommended credit exposure.",
        )

    frame = get_credit_risk_data()
    enhanced_frame = get_credit_dashboard_enhanced_data()
    if frame.empty:
        st.warning("No credit risk data found. Run: python scripts\\load_credit_risk_data.py")
        return

    filtered, approved_flags, income_range = _render_filters(frame)
    enhanced_filtered = apply_enhanced_filters(enhanced_frame, approved_flags, income_range)
    if filtered.empty:
        st.info("No customer records match the current filters.")
        return

    _render_kpis(filtered)
    st.write("")

    portfolio_tab, story_tab, segment_tab, records_tab = st.tabs(
        ["Portfolio", "Risk Story", "Segments", "Records"]
    )

    with portfolio_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(count_bar(filtered, "approved_flag", "Applicants by Approval Category", "Approval Category"), use_container_width=True)
            _chart_note("Shows how many applicants fall into each approval category.")
        with col2:
            st.plotly_chart(count_bar(filtered, "credit_band", "Applicants by Credit Band", "Credit Band"), use_container_width=True)
            _chart_note("Shows how applicants are grouped by credit eligibility band.")

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(histogram(filtered, "net_monthly_income", "Applicant Monthly Income Distribution", x_label="Net Monthly Income"), use_container_width=True)
            _chart_note("Shows the income range of applicants.")
        with col4:
            st.plotly_chart(histogram(filtered, "max_credit_amount", "Recommended Maximum Credit Amount Distribution", x_label="Maximum Credit Amount"), use_container_width=True)
            _chart_note("Shows the spread of recommended credit exposure.")

    with story_tab:
        if enhanced_filtered.empty:
            st.info("No enhanced BI records match the current approval and income filters.")
        else:
            _render_story_kpis(enhanced_filtered)
            st.write("")

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(count_bar(enhanced_filtered, "risk_profile", "Customers by Risk Profile", "Risk Profile"), use_container_width=True)
                _chart_note("Summarizes customers into risk groups.")
            with col2:
                st.plotly_chart(count_bar(enhanced_filtered, "income_bucket", "Customers by Income Group", "Income Group"), use_container_width=True)
                _chart_note("Shows customer affordability groups.")

            col3, col4 = st.columns(2)
            with col3:
                st.plotly_chart(box_by_category(enhanced_filtered, "risk_profile", "total_missed_payments", "Missed Payments by Risk Profile", "Risk Profile", "Total Missed Payments"), use_container_width=True)
                _chart_note("Compares repayment problems across risk profiles.")
            with col4:
                st.plotly_chart(box_by_category(enhanced_filtered, "approved_flag", "enquiries_l3m", "Recent Credit Enquiries by Approval Category", "Approval Category", "Enquiries in Last 3 Months"), use_container_width=True)
                _chart_note("Shows whether applicants recently searched for more credit.")

            col5, col6 = st.columns(2)
            with col5:
                st.plotly_chart(count_bar(enhanced_filtered, "last_product_enquiry", "Last Product Enquired by Customers", "Product Type"), use_container_width=True)
                _chart_note("Shows which banking product customers most recently enquired about.")
            with col6:
                st.plotly_chart(scatter_segment(enhanced_filtered, "net_monthly_income", "total_missed_payments", "risk_profile", "Income vs Missed Payments", "Net Monthly Income", "Total Missed Payments"), use_container_width=True)
                _chart_note("Shows repayment stress across income levels.")

    with segment_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(count_bar(filtered, "education", "Applicants by Education Level", "Education Level"), use_container_width=True)
            _chart_note("Shows the education mix of selected applicants.")
        with col2:
            st.plotly_chart(count_bar(filtered, "gender", "Applicants by Gender", "Gender"), use_container_width=True)
            _chart_note("Shows the gender composition of selected applicants.")

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(count_bar(filtered, "marital_status", "Applicants by Marital Status", "Marital Status"), use_container_width=True)
            _chart_note("Shows the household profile distribution.")
        with col4:
            st.plotly_chart(box_by_category(filtered, "approved_flag", "active_tradelines", "Active Credit Lines by Approval Category", "Approval Category", "Active Credit Lines"), use_container_width=True)
            _chart_note("Shows active credit relationships by approval category.")

        col5, col6 = st.columns(2)
        with col5:
            st.plotly_chart(scatter_segment(filtered, "age", "net_monthly_income", "approved_flag", "Applicant Age vs Monthly Income", "Applicant Age", "Net Monthly Income"), use_container_width=True)
            _chart_note("Shows approval categories across age and income.")
        with col6:
            st.plotly_chart(box_by_category(filtered, "credit_band", "max_credit_amount", "Maximum Credit Amount by Credit Band", "Credit Band", "Maximum Credit Amount"), use_container_width=True)
            _chart_note("Explains how recommended exposure changes across credit bands.")

    with records_tab:
        display = filtered.rename(columns=CREDIT_DISPLAY_COLUMNS)
        st.dataframe(display, use_container_width=True, hide_index=True)
