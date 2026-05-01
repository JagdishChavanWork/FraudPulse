import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Employee


DEFAULT_EMPLOYEE_ID = "ANL001"
DEFAULT_EMPLOYEE_PASSWORD = "FraudPulse@123"


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def seed_default_employee(session: Session) -> None:
    existing_employee = session.scalar(
        select(Employee).where(Employee.employee_id == DEFAULT_EMPLOYEE_ID)
    )
    if existing_employee:
        return

    session.add(
        Employee(
            employee_id=DEFAULT_EMPLOYEE_ID,
            employee_name="Analyst User",
            employee_password_hash=hash_password(DEFAULT_EMPLOYEE_PASSWORD),
            is_active=True,
        )
    )
