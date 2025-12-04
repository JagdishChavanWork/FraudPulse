# database/auth_manager.py
from bcrypt import hashpw, checkpw, gensalt
from sqlalchemy.orm import Session
from .models import Employee # Import the Employee table model
import streamlit as st # Used for accessing session state in the delete function (security check)

# --- Password Hashing and Verification ---

def get_password_hash(password: str) -> str:
    """Hashes a plaintext password securely using bcrypt."""
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a plaintext password matches a stored hashed password."""
    return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(db: Session, username: str, password: str) -> Employee | None:
    """R: Reads a user from the database and verifies the password."""
    user = db.query(Employee).filter(Employee.username == username).first()
    
    if not user:
        return None # User not found

    if not verify_password(password, user.hashed_password):
        return None # Password incorrect
        
    return user # Authentication successful

# --- Employee Management (CRUD) ---

def add_new_employee(db: Session, username: str, password: str, is_admin: bool = False) -> Employee | None:
    """C: Creates a new user with a hashed password and saves them to the database."""
    
    if db.query(Employee).filter(Employee.username == username).first():
        return None  # User already exists

    hashed_password = get_password_hash(password)
    
    new_employee = Employee(
        username=username,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return new_employee

def update_employee(db: Session, user_id: int, new_username: str, new_password: str | None, is_admin: bool) -> Employee | None:
    """U: Updates a user's details, including optional password change and position."""
    employee = db.query(Employee).filter(Employee.id == user_id).first()
    
    if employee:
        employee.username = new_username
        employee.is_admin = is_admin
        
        # Only update password if a new one is provided
        if new_password:
            employee.hashed_password = get_password_hash(new_password)
            
        db.commit()
        db.refresh(employee)
        return employee
    return None

def delete_employee(db: Session, user_id: int, current_user_session_username: str) -> bool:
    """D: Deletes an employee record from the database, preventing self-deletion."""
    
    employee = db.query(Employee).filter(Employee.id == user_id).first()
    
    # Security Check: Prevent the admin from deleting their own active account.
    if employee and employee.username == current_user_session_username:
        st.error("You cannot delete your own active administrator account.")
        return False
        
    if employee:
        db.delete(employee)
        db.commit()
        return True
    return False

def get_all_employees(db: Session):
    """R: Reads all employee records for the administrative display."""
    return db.query(Employee).all()