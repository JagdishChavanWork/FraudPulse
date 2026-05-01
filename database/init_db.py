from database.connection import create_session, engine
from database.models import Base
from database.seed import seed_default_employee


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with create_session() as session:
        seed_default_employee(session)
        session.commit()


if __name__ == "__main__":
    initialize_database()
    print("FraudPulse SQLite database initialized.")
