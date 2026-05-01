from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Employee


def get_active_employee_by_id(session: Session, employee_id: str) -> Employee | None:
    return session.scalar(
        select(Employee).where(
            Employee.employee_id == employee_id,
            Employee.is_active.is_(True),
        )
    )
