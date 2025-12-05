# app_modules/admin_management.py (Complete CRUD UI Logic)

import streamlit as st
from sqlalchemy.orm import Session
from database.database_connector import get_db
from database.auth_manager import add_new_employee, update_employee, delete_employee, get_all_employees
from database.models import Employee # Needed for querying


def admin_management_page():
    
    # Helper function to get current user ID and username
    def get_current_user_db_details(db: Session):
        username = st.session_state.get('username')
        if username:
            user = db.query(Employee).filter(Employee.username == username).first()
            return user.id if user else None, username
        return None, None
        
    # --- SECURITY CHECK (Role-Based Access Control) ---
    if not st.session_state.get('logged_in') or not st.session_state.get('is_admin'):
        st.error("🚨 Access Denied. You must be logged in as an Administrator to view this page.")
        return

    st.title("🔐 Employee Management System (CRUD)")
    st.markdown("Administrator panel for managing user accounts and privileges (Admin vs. Standard Employee).")
    st.divider()

    # --- Database Session Setup ---
    db_generator = get_db()
    db: Session = next(db_generator)
    
    current_user_db_id, current_username = get_current_user_db_details(db)


    # --- SECTION A: CREATE (Add New Employee) ---
    st.subheader("1. Register New Employee (Create)")
    with st.expander("Click to Add New User", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            new_username = col1.text_input("Username")
            new_password = col2.text_input("Temporary Password", type="password")
            is_admin_check = st.checkbox("Grant Admin Privileges", value=False)
            submitted = st.form_submit_button("Register Employee")

        if submitted:
            if new_username and new_password:
                new_user = add_new_employee(db, new_username, new_password, is_admin_check)
                if new_user:
                    st.success(f"User '{new_username}' registered successfully! Password: {new_password}")
                    st.rerun()
                else:
                    st.error(f"User '{new_username}' already exists.")
            else:
                st.warning("Please enter a valid username and password.")
    
    st.divider()

    # --- SECTION B: READ, UPDATE, DELETE (RUD Operations) ---
    st.subheader("2. Manage Existing Employees (Read, Update, Delete)")
    
    employees = get_all_employees(db) # READ operation
    
    # Display table and RUD forms dynamically
    for employee in employees:
        
        # Determine if the current employee is the one logged in (cannot delete own account)
        is_current_user = (employee.id == current_user_db_id)
        
        with st.container(border=True):
            col_id, col_user, col_admin, col_actions = st.columns([0.5, 2, 1.5, 2])
            
            # Read Operation (Display)
            col_id.markdown(f"**ID:** `{employee.id}`")
            col_user.markdown(f"**User:** `{employee.username}` {'(You)' if is_current_user else ''}")
            col_admin.markdown(f"**Admin:** {employee.is_admin}")
            
            # Actions Column
            col_actions_inner = col_actions.container()

            # --- UPDATE (U) ---
            if col_actions_inner.button("Edit/Update", key=f"edit_{employee.id}", use_container_width=True):
                st.session_state[f'edit_user_{employee.id}'] = not st.session_state.get(f'edit_user_{employee.id}', False)
                st.rerun()

            if st.session_state.get(f'edit_user_{employee.id}'):
                with st.form(f"update_form_{employee.id}"):
                    st.markdown(f"#### Update Details for {employee.username}")
                    
                    new_username_val = st.text_input("New Username", value=employee.username, key=f"new_user_{employee.id}")
                    new_password_val = st.text_input("New Password (Leave Blank)", type="password", key=f"new_pass_{employee.id}")
                    new_is_admin_val = st.checkbox("Is Administrator?", value=employee.is_admin, key=f"new_admin_{employee.id}")
                    
                    if st.form_submit_button("Save Changes"):
                        updated_user = update_employee(db, employee.id, new_username_val, new_password_val if new_password_val else None, new_is_admin_val)
                        if updated_user:
                            st.success(f"User {updated_user.username} updated successfully.")
                            st.session_state[f'edit_user_{employee.id}'] = False
                            st.rerun()
                        else:
                            st.error("Error updating user.")

            # --- DELETE (D) ---
            if not is_current_user:
                if col_actions_inner.button("Delete User", key=f"delete_{employee.id}", use_container_width=True):
                    # Pass the current username for the security check in auth_manager.py
                    if delete_employee(db, employee.id, current_username):
                        st.success(f"User {employee.username} deleted.")
                        st.rerun()
                    else:
                        st.error("Cannot delete an existing administrator account.")
            else:
                col_actions_inner.markdown("**(Cannot delete active session)**")

    db.close()