# run_init.py
import sys
import os

# 1. Get the path to the project root (E:\FraudPulse)
project_root = os.path.dirname(os.path.abspath(__file__))

# 2. Add the project root to the Python search path
# This is the CRITICAL STEP that allows Python to find 'database'
sys.path.insert(0, project_root)

# 3. Now safely import and run the initialization script
try:
    import database_init
    
    # Since database_init.py is designed to run its commands globally,
    # simply running the module will execute the setup.
    print("✅ Attempting to run database initialization...")
    # (The actual success/failure messages will still come from database_init.py)
    
except ModuleNotFoundError as e:
    print(f"❌ Error during import: {e}")
    print("Please ensure database_init.py is in the root directory.")