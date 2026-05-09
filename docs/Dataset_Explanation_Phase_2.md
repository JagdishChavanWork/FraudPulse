# Finlntel Phase 2 Dataset Explanation

## 1. Credit Risk Dataset With Bands

**Location:** `data/processed/credit_risk_dataset_with_bands.xlsx`

This dataset supports the Credit Risk Dashboard and Maximum Credit Amount regression model. It contains applicant profile, bureau, tradeline, approval category, credit band, and recommended maximum credit amount fields.

Key usage:
- Dashboard portfolio records in `credit_risk_data`
- Credit band and maximum credit amount analysis
- Maximum credit amount model training

Important fields:
- `AGE`, `EDUCATION`, `GENDER`, `MARITALSTATUS`
- `NETMONTHLYINCOME`, `Time_With_Curr_Empr`
- `Total_TL`, `Tot_Active_TL`, `Total_TL_opened_L6M`
- `time_since_recent_enq`
- `Approved_Flag`, `Credit_Band`, `Max_Credit_Amount`

## 2. Enhanced Credit Dashboard Dataset

**Location:** `data/processed/Dashboard_Data_Enhanced.csv`

This dataset supports deeper credit risk story charts and default feature values for the Credit Risk Prediction page. It contains repayment behavior, product enquiry, delinquency, income bucket, and risk profile fields.

Key usage:
- Risk Story tab in Management Insights
- Credit prediction default values for model features not manually entered by the analyst
- Enhanced credit risk segmentation

Important fields:
- `Tot_Missed_Pmnt`, `recent_level_of_deliq`, `max_recent_level_of_deliq`
- `enq_L3m`, `CC_enq_L12m`, `PL_enq_L12m`
- `Secured_TL`, `Unsecured_TL`, `CC_TL`, `PL_TL`, `Home_TL`
- `Income_Bucket`, `Risk_Profile`
- One-hot product and demographic fields

## 3. Fraud Dataset Version 2

**Location:** `data/processed/fraud_dataset_v2.csv`

This dataset supports the Fraud Dashboard, Fraud Detection model training, and fraud case lookup. It contains 70,000 transaction records with 12,600 fraud cases and 57,400 legitimate cases.

Key usage:
- Fraud Detection Dashboard
- Fraud XGBoost classifier training
- Fraud case profile lookup using generated case IDs

Important fields:
- Customer profile: `age`, `account_type`, `city_tier`, `tenure_days`, `account_balance`
- Spending baseline: `avg_monthly_spend`, `avg_txn_amount`, `avg_txn_per_day`, `usual_txn_hour`
- Transaction details: `txn_type`, `txn_amount`, `txn_hour`, `txn_day_of_week`
- Derived anomaly signals: `amount_to_avg_ratio`, `balance_drain_pct`, `hour_anomaly`, `velocity_24hr`, `new_txn_type_flag`, `large_round_amt_flag`
- History fields: `days_since_last_txn`, `prior_fraud_complaint`
- Target: `is_fraud`
- Dashboard-only analysis field: `fraud_type`

## Deployment Note

Only required processed datasets should be committed for Streamlit deployment. Large raw datasets and unused model artifacts should not be committed unless they are required by the live app.
