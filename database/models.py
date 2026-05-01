from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    employee_name: Mapped[str] = mapped_column(String(120), nullable=False)
    employee_password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CreditRiskData(Base):
    __tablename__ = "credit_risk_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    age: Mapped[float | None] = mapped_column(Float)
    education: Mapped[str | None] = mapped_column(String(80), index=True)
    gender: Mapped[str | None] = mapped_column(String(20), index=True)
    marital_status: Mapped[str | None] = mapped_column(String(40), index=True)
    net_monthly_income: Mapped[float | None] = mapped_column(Float, index=True)
    time_with_current_employer: Mapped[float | None] = mapped_column(Float)
    total_tradelines: Mapped[float | None] = mapped_column(Float)
    active_tradelines: Mapped[float | None] = mapped_column(Float)
    tradelines_opened_last_6m: Mapped[float | None] = mapped_column(Float)
    time_since_recent_enquiry: Mapped[float | None] = mapped_column(Float)
    approved_flag: Mapped[str | None] = mapped_column(String(20), index=True)
    credit_band: Mapped[str | None] = mapped_column(String(40), index=True)
    max_credit_amount: Mapped[float | None] = mapped_column(Float)
    income_bucket: Mapped[str | None] = mapped_column(String(40), index=True)
    risk_profile: Mapped[str | None] = mapped_column(String(40), index=True)
    source_file: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class CreditRiskDashboardEnhanced(Base):
    __tablename__ = "credit_risk_dashboard_enhanced"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pct_tl_open_l6m: Mapped[float | None] = mapped_column(Float)
    pct_tl_closed_l6m: Mapped[float | None] = mapped_column(Float)
    total_tl_closed_l12m: Mapped[float | None] = mapped_column(Float)
    pct_tl_closed_l12m: Mapped[float | None] = mapped_column(Float)
    total_missed_payments: Mapped[float | None] = mapped_column(Float, index=True)
    cc_tradelines: Mapped[float | None] = mapped_column(Float)
    home_tradelines: Mapped[float | None] = mapped_column(Float)
    personal_loan_tradelines: Mapped[float | None] = mapped_column(Float)
    secured_tradelines: Mapped[float | None] = mapped_column(Float)
    unsecured_tradelines: Mapped[float | None] = mapped_column(Float)
    other_tradelines: Mapped[float | None] = mapped_column(Float)
    age_oldest_tradeline: Mapped[float | None] = mapped_column(Float)
    age_newest_tradeline: Mapped[float | None] = mapped_column(Float)
    time_since_recent_payment: Mapped[float | None] = mapped_column(Float)
    max_recent_delinquency_level: Mapped[float | None] = mapped_column(Float)
    delinquencies_6_12m: Mapped[float | None] = mapped_column(Float)
    times_60p_dpd: Mapped[float | None] = mapped_column(Float)
    standard_accounts_12m: Mapped[float | None] = mapped_column(Float)
    substandard_accounts: Mapped[float | None] = mapped_column(Float)
    substandard_accounts_6m: Mapped[float | None] = mapped_column(Float)
    substandard_accounts_12m: Mapped[float | None] = mapped_column(Float)
    doubtful_accounts: Mapped[float | None] = mapped_column(Float)
    doubtful_accounts_12m: Mapped[float | None] = mapped_column(Float)
    loss_accounts: Mapped[float | None] = mapped_column(Float)
    recent_delinquency_level: Mapped[float | None] = mapped_column(Float)
    cc_enquiries_12m: Mapped[float | None] = mapped_column(Float)
    pl_enquiries_12m: Mapped[float | None] = mapped_column(Float)
    time_since_recent_enquiry: Mapped[float | None] = mapped_column(Float)
    enquiries_l3m: Mapped[float | None] = mapped_column(Float)
    net_monthly_income: Mapped[float | None] = mapped_column(Float, index=True)
    time_with_current_employer: Mapped[float | None] = mapped_column(Float)
    has_credit_card: Mapped[bool | None] = mapped_column(Boolean)
    has_personal_loan: Mapped[bool | None] = mapped_column(Boolean)
    has_home_loan: Mapped[bool | None] = mapped_column(Boolean)
    has_gold_loan: Mapped[bool | None] = mapped_column(Boolean)
    education_code: Mapped[str | None] = mapped_column(String(40), index=True)
    approved_flag: Mapped[str | None] = mapped_column(String(20), index=True)
    marital_status: Mapped[str | None] = mapped_column(String(40), index=True)
    gender: Mapped[str | None] = mapped_column(String(20), index=True)
    last_product_enquiry: Mapped[str | None] = mapped_column(String(80), index=True)
    first_product_enquiry: Mapped[str | None] = mapped_column(String(80), index=True)
    income_bucket: Mapped[str | None] = mapped_column(String(40), index=True)
    risk_profile: Mapped[str | None] = mapped_column(String(40), index=True)
    source_file: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class FraudDetectionData(Base):
    __tablename__ = "fraud_detection_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    transaction_timestamp: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    transaction_type: Mapped[str | None] = mapped_column(String(80), index=True)
    amount: Mapped[float | None] = mapped_column(Float)
    origin_account: Mapped[str | None] = mapped_column(String(80))
    destination_account: Mapped[str | None] = mapped_column(String(80))
    old_balance_origin: Mapped[float | None] = mapped_column(Float)
    new_balance_origin: Mapped[float | None] = mapped_column(Float)
    old_balance_destination: Mapped[float | None] = mapped_column(Float)
    new_balance_destination: Mapped[float | None] = mapped_column(Float)
    location: Mapped[str | None] = mapped_column(String(120), index=True)
    risk_score: Mapped[float | None] = mapped_column(Float, index=True)
    risk_band: Mapped[str | None] = mapped_column(String(40), index=True)
    is_fraud: Mapped[bool | None] = mapped_column(Boolean, index=True)
    source_file: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    module_name: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    input_payload: Mapped[str] = mapped_column(Text, nullable=False)
    prediction_label: Mapped[str | None] = mapped_column(String(80))
    prediction_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
