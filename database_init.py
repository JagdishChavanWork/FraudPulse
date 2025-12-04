# database_init.py

from database.database_connector import Base, engine, SessionLocal
from database.models import Employee # Imports the Employee table definition
from bcrypt import hashpw, gensalt 
from sqlalchemy.orm import Session

# --- 1. Create all tables defined in models.py ---
# This looks at the database connection and creates all tables defined using Base.
Base.metadata.create_all(bind=engine)
print("✅ Database tables (employees, prediction_logs) created successfully.")

# --- 2. Add a Test Employee for Login ---
db = SessionLocal()
try:
    # Hash a default password securely for storage
    password_to_hash = "admin123"
    hashed_password = hashpw(password_to_hash.encode('utf-8'), gensalt()).decode('utf-8')

    # Check if a default user already exists
    if db.query(Employee).filter(Employee.username == "admin").first() is None:
        
        # Create a new employee record
        default_user = Employee(
            username="admin", 
            hashed_password=hashed_password,
            is_admin=True
        )
        db.add(default_user)
        db.commit()
        print(f"✅ Default admin user created. Username: admin. Password: {password_to_hash} (hashed and stored).")
    else:
        print("ℹ️ Default admin user already exists.")
except Exception as e:
    db.rollback()
    print(f"❌ Error setting up default user: {e}")
finally:
    db.close()