# Finlntel: Banking Risk Intelligence Platform

## Overview

Finlntel is a Streamlit-based banking risk intelligence application for analyst-assisted decision support. The platform combines credit risk analytics, credit approval prediction, maximum credit amount estimation, fraud dashboarding, fraud prediction, authentication, database integration, and prediction logging.

## Current Modules

- **Management Insights**
  - Credit Risk Dashboard
  - Fraud Dashboard
- **Credit Risk Prediction**
  - Approval category prediction
  - Maximum credit amount regression
  - Prediction logging
- **Fraud Detection Prediction**
  - Live fraud checker
  - Auto-calculated anomaly features
  - Risk level and verdict display
  - Prediction logging
- **Authentication**
  - Employee login
  - Bcrypt password verification
  - Streamlit session management

## Tech Stack

- Python
- Streamlit
- pandas, NumPy
- scikit-learn
- XGBoost
- imbalanced-learn
- Plotly
- SQLAlchemy
- SQLite locally, with `DATABASE_URL` support for external databases
- bcrypt

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Default local demo login:

```text
Employee ID: ANL001
Password: FraudPulse@123
```

## Deployment Notes

For Streamlit Cloud, keep required model artifacts and processed datasets available in the repository or use external storage. Use a persistent database such as PostgreSQL through `DATABASE_URL` if prediction logs must survive app restarts.
