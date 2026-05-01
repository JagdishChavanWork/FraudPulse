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


def render_credit_dashboard() -> None:
    page_header(
        "Credit Risk Analysis",
        "Database-backed portfolio view for approval bands, credit bands, income, tenure, and credit amount allocation.",
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
            st.plotly_chart(count_bar(filtered, "approved_flag", "ApprovedFlag distribution"), use_container_width=True)
        with col2:
            st.plotly_chart(count_bar(filtered, "credit_band", "CreditBand distribution"), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(histogram(filtered, "net_monthly_income", "Net monthly income distribution"), use_container_width=True)
        with col4:
            st.plotly_chart(histogram(filtered, "max_credit_amount", "Maximum credit amount distribution"), use_container_width=True)

    with story_tab:
        if enhanced_filtered.empty:
            st.info("No enhanced BI records match the current approval and income filters.")
        else:
            _render_story_kpis(enhanced_filtered)
            st.write("")

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(count_bar(enhanced_filtered, "risk_profile", "Risk profile distribution"), use_container_width=True)
            with col2:
                st.plotly_chart(count_bar(enhanced_filtered, "income_bucket", "Income bucket distribution"), use_container_width=True)

            col3, col4 = st.columns(2)
            with col3:
                st.plotly_chart(box_by_category(enhanced_filtered, "risk_profile", "total_missed_payments", "Missed payments by risk profile"), use_container_width=True)
            with col4:
                st.plotly_chart(box_by_category(enhanced_filtered, "approved_flag", "enquiries_l3m", "Recent enquiries by approval class"), use_container_width=True)

            col5, col6 = st.columns(2)
            with col5:
                st.plotly_chart(count_bar(enhanced_filtered, "last_product_enquiry", "Last product enquiry"), use_container_width=True)
            with col6:
                st.plotly_chart(scatter_segment(enhanced_filtered, "net_monthly_income", "total_missed_payments", "risk_profile", "Income vs missed payments"), use_container_width=True)

    with segment_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(count_bar(filtered, "education", "Education distribution"), use_container_width=True)
        with col2:
            st.plotly_chart(count_bar(filtered, "gender", "Gender split"), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(count_bar(filtered, "marital_status", "Marital status split"), use_container_width=True)
        with col4:
            st.plotly_chart(box_by_category(filtered, "approved_flag", "active_tradelines", "Active tradelines by approval class"), use_container_width=True)

        col5, col6 = st.columns(2)
        with col5:
            st.plotly_chart(scatter_segment(filtered, "age", "net_monthly_income", "approved_flag", "Income vs age by approval class"), use_container_width=True)
        with col6:
            st.plotly_chart(box_by_category(filtered, "credit_band", "max_credit_amount", "Max credit amount by credit band"), use_container_width=True)

    with records_tab:
        display = filtered.rename(columns=CREDIT_DISPLAY_COLUMNS)
        st.dataframe(display, use_container_width=True, hide_index=True)
