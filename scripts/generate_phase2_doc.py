from datetime import date
from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


DOCS = Path(r"E:\FraudPulse\docs")
OUT = DOCS / "Fraud Pulse Phase_2.docx"
PROMPT_OUT = DOCS / "presentation" / "Fraud Pulse Phase_2 Canva Prompt.txt"

CANVA_PROMPT = """Do not generate the document from assumptions. Inspect the current codebase, folder structure, dashboard charts, and Version 1 documents first, then write the updated Phase 2 document from evidence.

Create a professional Canva presentation for "Fraud Pulse Phase_2: AI-Driven Credit Risk and Fraud Intelligence Platform". Maximum 10 slides. Use the FraudPulse application color theme: primary teal #1f7a7a, dark teal #176568, navy #1f3444, light background #f6f8fa, white cards #ffffff, border grey #d9e2ea, muted text #6b7a86, risk red #d85b5b, warning amber #b7791f, success green #218568. Use clean academic/business design suitable for MCA faculty review and project demonstration. Avoid generic startup language.

Slide 1 - Title: Fraud Pulse Phase_2. Subtitle: Unified Analyst Platform for Credit Risk, Fraud Intelligence, Secure Prediction Logging, and Streamlit Deployment Readiness.
Slide 2 - Problem Statement: disconnected credit and fraud review, manual analyst effort, limited auditability, and need for dashboard-backed decision support.
Slide 3 - Solution Overview: four modules - Credit Risk Dashboard, Credit Risk Prediction, Fraud Detection Dashboard, Fraud Detection Prediction - with authentication and prediction logging.
Slide 4 - System Architecture: Streamlit UI -> service layer -> ML model layer -> SQLite/Postgres database -> processed datasets. Show app.py, modules, ml, models, database, scripts.
Slide 5 - Credit Risk Dashboard: Applicant Records, Average Income, Average Age, Avg Max Credit, approval and credit-band charts, income and max-credit distributions, risk story charts, segment charts.
Slide 6 - Credit Prediction and Max Credit Regression: analyst input -> preprocessing/default payload -> enhanced classifier -> class probabilities -> compact max-credit regressor -> output -> prediction_logs.
Slide 7 - Fraud Dashboard Analytics: Total Cases, Fraud Cases, Fraud Rate, Avg Fraud Amount, fraud by transaction type, age group, hour, city tier, heatmap, distributions, balance drain, velocity, fraud type, feature importance.
Slide 8 - Live Fraud Prediction: profile + baseline + transaction + flags -> derived features -> scaler + XGBoost -> probability, threshold, risk badge, verdict -> prediction_logs.
Slide 9 - Database, Security, Audit: employees, credit_risk_data, credit_risk_dashboard_enhanced, fraud_detection_data, prediction_logs, bcrypt login, SQLAlchemy, SQLite local, Postgres for deployed persistence.
Slide 10 - Deployment Readiness and Future Scope: locally working; compact model fixed; remaining needs Postgres DATABASE_URL, avoid old >100MB model, Linux smoke test, credential hardening, RBAC, prediction log dashboard, drift monitoring."""


blocks = []


def h(level, text):
    blocks.append(("h", level, text))


def p(text):
    blocks.append(("p", text))


def b(items):
    for item in items:
        blocks.append(("b", item))


def t(headers, rows):
    blocks.append(("t", headers, rows))


def pb():
    blocks.append(("pb",))


def build_content():
    h(0, "Fraud Pulse Phase_2")
    p("AI-Driven Credit Risk and Fraud Intelligence Platform")
    p("Unified Analyst Platform for Credit Risk Dashboarding, Prediction, Fraud Verification, Secure Prediction Logging, and Streamlit Deployment Readiness")
    p("Phase 2 Project Documentation Package")
    p("Prepared for MCA Project Review")
    p("Student: Jagdish Dilip Chavan")
    p("Guide: Prof. Megha Mane")
    p("Institute: Suryadatta Institute of Business Management and Technology, Pune")
    p("Document Date: " + date.today().strftime("%d %B %Y"))
    pb()

    h(1, "Document Control")
    t(["Item", "Description"], [
        ["Document Title", "Fraud Pulse Phase_2"],
        ["Project Stage", "Phase 2 - integrated local Streamlit analytics and prediction application"],
        ["Source Material Reviewed", "Version 1 final report format, synopsis, SRS, current codebase, database schema, dashboard modules, prediction modules, model artifacts, tests, and deployment configuration"],
        ["Storage Location", r"E:\FraudPulse\docs"],
        ["Theme Upgrade", "From standalone fraud prototype to unified AI-driven risk intelligence and analyst decision support platform"],
    ])
    h(1, "Index")
    t(["Chapter", "Contents"], [["1", "Introduction"], ["2", "Proposed System"], ["3", "Analysis and Design"], ["4", "User Manual"], ["5", "Data Reports and Dashboard Documentation"], ["6", "Prediction Workflow and Models"], ["7", "Testing, Deployment Readiness, and Limitations"], ["8", "Future Scope"], ["9", "Bibliography and References"]])
    pb()

    h(1, "CHAPTER 1: INTRODUCTION")
    h(2, "1.1 Project Overview")
    p("FraudPulse Phase 2 is a Streamlit-based financial risk intelligence platform developed to support analyst decision-making across credit risk and fraud verification workflows. The project is no longer limited to the initial fraud prototype. It now combines a completed Credit Risk Dashboard, Credit Risk Prediction, Maximum Credit Amount regression, Fraud Detection Dashboard, Fraud Detection Prediction, authentication, SQLite-backed data loading, and prediction logging into one analyst-facing application.")
    p("The application entry point is app.py. It initializes the Streamlit page, initializes the database schema, injects the global UI theme, checks employee session state, renders the sidebar, and dispatches to the selected module. The business modules are under modules/dashboard and modules/prediction. Model training and inference code is under ml/credit_risk, ml/credit_limit, and ml/fraud.")
    p("Updated subtitle/theme: AI-driven credit risk and fraud intelligence through a unified analyst platform with decision support dashboarding, secure prediction logging, and Streamlit deployment readiness.")
    h(2, "1.2 Existing System and Need for System")
    p("Traditional risk review depends on disconnected spreadsheets, static checks, and manual investigation. Such systems provide weak auditability and slow decision support. FraudPulse improves this workflow by connecting dashboards, saved ML models, analyst forms, database records, and prediction logs in a controlled web application.")
    h(2, "1.3 Scope of Work")
    t(["Scope Area", "Phase 2 Coverage"], [
        ["Credit Risk Dashboard", "Implemented: portfolio KPIs, approval and credit-band analysis, income and max-credit distributions, risk story charts, segment charts, and records table."],
        ["Credit Risk Prediction", "Implemented: applicant, bureau, tradeline, enquiry, and delinquency inputs; approval class prediction; maximum credit amount regression; prediction logging."],
        ["Fraud Detection Dashboard", "Implemented in current code: overview, pattern analysis, customer/case risk profile lookup, filters, KPIs, charts, model feature importance, and records."],
        ["Fraud Detection Prediction", "Implemented: live fraud checker, automatic derived features, probability, threshold, LOW/MEDIUM/HIGH badge, verdict, and log storage."],
        ["Authentication", "Implemented with employee login, bcrypt password verification, and Streamlit session state."],
        ["Database Integration", "Implemented locally using SQLAlchemy and SQLite. Main tables: employees, credit_risk_data, credit_risk_dashboard_enhanced, fraud_detection_data, prediction_logs."],
        ["Deployment Preparation", "Partly ready: relative paths and requirements are present; remaining concerns are persistent DB, large artifact hygiene, secrets, and cloud smoke testing."],
    ])
    h(2, "1.4 Operating Environment")
    t(["Component", "Current Phase 2 Requirement"], [
        ["Language", "Python with Streamlit application runtime. Local environment is Python 3.13; deployment should use a supported Python version compatible with listed packages."],
        ["Framework", "Streamlit 1.51.0 for UI and application server."],
        ["Database", "SQLite locally; DATABASE_URL supports external DB. Postgres is recommended for deployed prediction log persistence."],
        ["Libraries", "pandas, numpy, scikit-learn, xgboost, imbalanced-learn, SQLAlchemy, bcrypt, plotly, openpyxl, python-dotenv, psycopg2-binary."],
        ["Theme", "Teal #1f7a7a, dark teal #176568, navy #1f3444, light background #f6f8fa, white cards, muted grey, risk red, warning amber, success green."],
    ])
    pb()

    h(1, "CHAPTER 2: PROPOSED SYSTEM")
    h(2, "2.1 Proposed System")
    p("The proposed Phase 2 system is a unified analyst platform. Authenticated employees can move between credit portfolio analysis, applicant prediction, fraud trend analysis, and live transaction verification. Each page is a separate renderer selected from the sidebar. The design is modular rather than a single-script prototype.")
    h(2, "2.2 Module Specifications")
    t(["Module", "Implementation Evidence", "Status"], [
        ["Authentication", "modules/auth/Login.py and session_manager.py verify employees and maintain session state.", "Working locally"],
        ["Sidebar Navigation", "modules/common/sidebar.py navigates to four business modules and logout.", "Working locally"],
        ["Credit Risk Dashboard", "modules/dashboard/credit_dashboard.py with credit_risk_service.py.", "Implemented"],
        ["Credit Risk Prediction", "modules/prediction/credit_risk.py calls enhanced approval classifier and max-credit regressor and logs both events.", "Implemented"],
        ["Fraud Dashboard", "modules/dashboard/fraud_dashboard.py reads fraud_detection_data and renders overview, pattern, profile, and records tabs.", "Implemented"],
        ["Fraud Prediction", "modules/prediction/fraud_detection.py calculates derived fraud signals, calls fraud model, displays verdict, and logs event.", "Implemented"],
        ["Data Loading", "scripts/load_credit_risk_data.py, load_credit_dashboard_enhanced.py, load_fraud_detection_data.py.", "Implemented"],
        ["Prediction Logging", "modules/services/prediction_log_service.py writes audit rows to prediction_logs.", "Implemented"],
    ])
    h(2, "2.3 Objectives")
    b(["Provide one controlled interface for credit risk and fraud risk intelligence.", "Reduce manual analyst effort using KPIs, charts, probability outputs, and clear verdicts.", "Store analyst-generated prediction inquiries for auditability.", "Use saved model artifacts and ordered feature payloads, not ad hoc prediction logic.", "Prepare the project for GitHub and Streamlit Cloud while naming deployment blockers honestly."])
    h(2, "2.4 Feasibility Study")
    t(["Type", "Assessment"], [["Technical", "Feasible with open-source Python, Streamlit, ML, and database libraries."], ["Economic", "Feasible for academic/prototype use; production logging may require a managed Postgres service."], ["Operational", "Feasible for analyst-assisted workflows; login, dashboards, prediction forms, and logging work locally."], ["Deployment", "Partly feasible; compact artifacts and relative paths help, but DB persistence and cloud smoke tests remain required."]])
    pb()

    h(1, "CHAPTER 3: ANALYSIS AND DESIGN")
    h(2, "3.1 Folder Structure")
    t(["Path", "Purpose"], [
        ["app.py", "Main Streamlit entry point, page setup, DB initialization, auth gate, and page dispatch."],
        ["config/", "Settings, project paths, dataset paths, DATABASE_URL."],
        ["data/processed/", "Processed datasets required by dashboards and training."],
        ["database/", "SQLAlchemy connection, ORM models, schema, seed, SQLite DB."],
        ["docs/", "Documentation root with diagrams, presentation, reports, srs, synopsis; Phase 2 output stored here."],
        ["ml/", "Training and prediction code for credit risk, credit limit, and fraud."],
        ["models/", "Saved artifacts and metrics."],
        ["modules/auth/", "Login and session handling."],
        ["modules/common/", "Charts, sidebar, styling helpers."],
        ["modules/dashboard/", "Credit and fraud dashboards."],
        ["modules/prediction/", "Credit and fraud prediction pages."],
        ["modules/services/", "Data services and prediction logging."],
        ["scripts/", "Dataset loaders."],
        ["tests/", "Pytest tests and placeholders."],
    ])
    h(2, "3.2 System Architecture")
    p("Architecture flow: Streamlit UI -> page renderer -> service/model helper -> database/model artifact -> result display -> prediction log. Dashboard pages query service functions and render Plotly charts. Prediction pages transform form inputs into model payloads, run inference, display outputs, and log the inquiry.")
    h(2, "3.3 Database Design")
    t(["Table", "Purpose", "Important Columns"], [
        ["employees", "Application login users.", "employee_id, employee_name, employee_password_hash, is_active, timestamps"],
        ["credit_risk_data", "Portfolio dashboard records.", "age, education, gender, income, approved_flag, credit_band, max_credit_amount"],
        ["credit_risk_dashboard_enhanced", "Enhanced BI and prediction-default fields.", "missed payments, enquiries, delinquency, risk_profile, income_bucket, product enquiry fields"],
        ["fraud_detection_data", "Sender-centric fraud dashboard records.", "transaction_id, account_type, txn_type, txn_amount, hour, ratios, velocity, fraud_type, is_fraud"],
        ["prediction_logs", "Analyst inquiry audit trail.", "employee_id, module_name, input_payload, prediction_label, prediction_score, created_at"],
    ])
    h(2, "3.4 Model Loading Flow")
    t(["Model Area", "Artifact", "Flow"], [["Credit Approval", "models/credit_risk/enhanced_approved_flag_classifier.joblib", "Loaded by ml/credit_risk/predict.py with saved feature columns."], ["Max Credit Amount", "models/credit_limit/max_credit_amount_regressor.joblib", "Compact HistGradientBoostingRegressor artifact loaded by ml/credit_limit/predict.py."], ["Fraud Detection", "models/fraud/fraud_xgb_classifier.joblib plus scaler, feature list, threshold", "Loaded by ml/fraud/predict.py after encoding and derived feature calculation."]])
    pb()

    h(1, "CHAPTER 4: USER MANUAL")
    h(2, "4.1 Login")
    p("The user logs in using employee ID and password. Bcrypt verifies password hashes stored in the employees table. After successful login, Streamlit session state stores the employee and enables module navigation. This is authentication with basic role readiness; detailed page-level RBAC is future scope.")
    h(2, "4.2 Module Flows")
    b(["Credit Dashboard: filter by ApprovedFlag, CreditBand, income, and age; review KPI cards, portfolio charts, risk story charts, segment charts, and records.", "Credit Prediction: enter applicant and bureau fields; submit Analyze Credit Profile; review approval class, confidence, max credit amount, and class probability table; log two prediction events.", "Fraud Dashboard: filter by transaction type, fraud pattern, and status; review overview, pattern analysis, customer risk profile, and records.", "Fraud Prediction: enter customer, baseline, transaction, and flags; auto-calculate derived features; show probability, threshold, risk badge, verdict, and top signals; log fraud_detection_prediction."])
    pb()

    h(1, "CHAPTER 5: DATA REPORTS AND DASHBOARD DOCUMENTATION")
    h(2, "5.1 Dataset Summary")
    t(["Dataset", "Location", "Use"], [["Dashboard_Data_Enhanced.csv", "data/processed/", "Enhanced credit BI and prediction defaults."], ["credit_risk_dataset_with_bands.xlsx", "data/processed/", "Credit risk dashboard loading and max-credit regression training."], ["fraud_dataset_v2.csv", "data/processed/", "Fraud dashboard, fraud training, and case lookup. Contains 70,000 records: 12,600 fraud and 57,400 legitimate."]])
    h(2, "5.2 Credit Risk Dashboard Charts")
    t(["Chart/KPI", "Purpose", "Business Meaning"], [["Applicant Records", "Count selected portfolio records.", "Shows sample size behind filters."], ["Average Income", "Mean and median income.", "Indicates affordability profile."], ["Average Age", "Average age and tenure note.", "Shows demographic and job-stability context."], ["Avg Max Credit", "Average max credit and P4 share.", "Shows exposure and higher-risk approval share."], ["ApprovedFlag distribution", "Bar count by approval class.", "Shows approval mix across P1-P4."], ["CreditBand distribution", "Bar count by credit band.", "Shows creditworthiness segmentation."], ["Net monthly income distribution", "Histogram of income.", "Reveals income spread and outliers."], ["Maximum credit amount distribution", "Histogram of credit limit.", "Shows exposure concentration."], ["Risk profile distribution", "Count by risk_profile.", "Shows risk category mix."], ["Income bucket distribution", "Count by income bucket.", "Shows affordability segmentation."], ["Missed payments by risk profile", "Box plot.", "Validates repayment pressure across risk groups."], ["Recent enquiries by approval class", "Box plot.", "Shows enquiry burden by approval class."], ["Last product enquiry", "Count bar.", "Shows recent product intent."], ["Income vs missed payments", "Scatter.", "Shows repayment stress across income."], ["Education distribution", "Count bar.", "Demographic view."], ["Gender split", "Count bar.", "Demographic view."], ["Marital status split", "Count bar.", "Customer profile view."], ["Active tradelines by approval class", "Box plot.", "Shows active credit depth by class."], ["Income vs age by approval class", "Scatter.", "Shows approval class across income-age space."], ["Max credit amount by credit band", "Box plot.", "Shows limit allocation by band."]])
    h(2, "5.3 Fraud Dashboard Charts")
    t(["Chart/KPI", "Purpose", "Business Meaning"], [["Total Cases", "Count selected transactions.", "Shows case load."], ["Fraud Cases", "Count is_fraud=1.", "Shows confirmed fraud volume."], ["Fraud Rate", "Fraud percentage.", "Shows risk density."], ["Avg Fraud Amount", "Average fraud transaction amount.", "Shows loss exposure."], ["Fraud vs legitimate by transaction type", "Grouped bar.", "Identifies risky channels."], ["Fraud distribution by age group", "Pie chart.", "Shows affected customer age groups."], ["Fraud rate by hour of day", "Line chart.", "Identifies high-risk transaction hours."], ["Fraud rate by city tier", "Bar chart.", "Shows geographic-tier risk differences."], ["Fraud rate heatmap: account type vs transaction type", "Heatmap.", "Identifies risky account-channel combinations."], ["Transaction amount distribution", "Overlapping histogram.", "Compares fraud and normal amount patterns."], ["Amount-to-average ratio distribution", "Overlapping histogram.", "Explains abnormal-spend signal."], ["Balance drain by fraud pattern", "Box plot.", "Shows account drain intensity by fraud type."], ["Fraud velocity distribution", "Bar chart.", "Shows rapid transaction behavior."], ["Fraud type breakdown", "Pie chart.", "Shows fraud pattern mix."], ["Model Feature Importance table", "Ranked table.", "Explains strongest model drivers."], ["Customer Risk Profile cards", "Account, balance, amount, status.", "Supports case review."], ["Active anomaly flags", "Flag summary.", "Supports escalation decision."], ["Fraud records table", "Filtered detail table.", "Supports audit and manual investigation."]])
    h(2, "5.4 Screenshots and Visual Assets")
    p("Existing screenshots and diagrams are stored under docs/diagrams. Several belong to Version 1 and older UI screens. Current Phase 2 dashboard screenshots were not found as exported images. Therefore this document documents current dynamic Plotly chart components directly from code rather than embedding outdated visuals.")
    pb()

    h(1, "CHAPTER 6: PREDICTION WORKFLOW AND MODELS")
    h(2, "6.1 Prediction Flow")
    p("Credit prediction builds a default-aware payload, one-hot encodes selected categorical values, invokes the enhanced approval classifier, then invokes the maximum credit amount regressor. Fraud prediction encodes account and transaction categories, calculates derived features, scales ordered features, invokes the XGBoost fraud model, applies the saved threshold, and displays a risk-level verdict.")
    t(["Derived Fraud Feature", "Calculation"], [["amount_to_avg_ratio", "txn_amount / avg_txn_amount capped at 50"], ["balance_drain_pct", "txn_amount / account_balance * 100 capped at 100"], ["hour_anomaly", "1 if absolute difference between txn_hour and usual_txn_hour is greater than 4"], ["is_weekend", "1 if day of week is 5 or 6"]])
    h(2, "6.2 Model Metrics")
    t(["Model", "Current Artifact", "Metric Summary"], [["Enhanced Credit Approval", "enhanced_approved_flag_classifier.joblib", "Accuracy 0.7786, macro F1 0.6880, weighted F1 0.7640."], ["Maximum Credit Amount", "max_credit_amount_regressor.joblib", "Compact HistGradientBoostingRegressor. MAE 3772.00, RMSE 10751.53, R2 0.99977."], ["Fraud Detection", "fraud_xgb_classifier.joblib + scaler + threshold", "Precision 0.9988, recall 1.0000, F1 0.9994, ROC-AUC 1.0000, threshold 0.50, SMOTE applied."]])
    p("Fraud metrics are extremely high because the dataset contains strong engineered fraud signals. Production use requires validation on newer unseen data and drift monitoring.")
    h(2, "6.3 Prediction Logging")
    p("prediction_log_service.py serializes model input payloads and writes employee_id, module_name, prediction_label, prediction_score, and created_at into prediction_logs. Current module names are credit_risk_prediction, max_credit_amount_regression, and fraud_detection_prediction. The logging function fails safely so the page does not crash if the database write fails.")
    pb()

    h(1, "CHAPTER 7: TESTING, DEPLOYMENT READINESS, AND LIMITATIONS")
    h(2, "7.1 Testing")
    t(["Test Area", "Evidence"], [["Fraud payload derivation", "tests/test_fraud_payload.py verifies encoding, weekend, capped balance drain, hour anomaly, and risk thresholds."], ["Prediction logging", "tests/test_prediction_logging.py verifies serialization, log creation, and skip behavior."], ["Compile check", "python -m compileall passed across app, modules, ml, database, scripts, and tests."], ["Database smoke test", "Temporary prediction log row was inserted and removed successfully."]])
    h(2, "7.2 Deployment Readiness Assessment")
    t(["Area", "Status", "Action"], [["Folder structure", "Ready. Modular and GitHub-friendly.", "Keep app.py at repository root."], ["Imports", "Mostly ready.", "Run Streamlit Cloud/Linux smoke test for path casing."], ["Model loading", "Partly ready. Current used artifacts are small enough; old approved_flag_classifier.joblib is too large and unused by current UI.", "Do not commit old approved_flag_classifier.joblib; use Git LFS only if needed."], ["Paths", "Ready. Project-relative paths are used.", "Avoid E:\\ hardcoded paths in runtime code."], ["Database", "Local SQLite works; cloud writes may be temporary.", "Use Postgres DATABASE_URL in Streamlit secrets for persistence."], ["Secrets", "Partly ready. .env ignored and .env.example exists.", "Do not expose real credentials; replace demo credentials before public use."], ["Large files", "Corrected for max-credit model; old large approval model ignored.", "Check Git status before commit and avoid files over 100 MB."], ["Data files", "Processed datasets are below 100 MB.", "Commit only required processed datasets, not unnecessary raw files."]])
    h(2, "7.3 GitHub Large File Warning Resolution")
    p("The warning was caused by max_credit_amount_regressor.joblib and approved_flag_classifier.joblib being larger than 100 MB. The max-credit model has been retrained into a compact deployment artifact around 669 KB. The old approved_flag_classifier.joblib is ignored because the current Phase 2 UI uses enhanced_approved_flag_classifier.joblib. If the old model is required later, store it with Git LFS or external model hosting, not normal Git.")
    h(2, "7.4 Limitations")
    b(["SQLite is not a durable deployed logging store on Streamlit Cloud; Postgres is recommended.", "Authentication exists, but detailed RBAC is future scope.", "Fraud case lookup uses generated case IDs because the fraud dataset has no real customer ID.", "Current fraud metrics need validation on newer unseen data before production.", "Current Phase 2 screenshots are not exported; charts are documented from code."])
    pb()

    h(1, "CHAPTER 8: FUTURE SCOPE")
    b(["Move prediction logs to managed Postgres.", "Add role-based authorization for Admin, Risk Analyst, and Auditor users.", "Add a Prediction Log dashboard.", "Add model drift monitoring and scheduled retraining reports.", "Automate current dashboard screenshot exports.", "Add GitHub Actions or Streamlit smoke tests.", "Add customer/account identifiers when available in future fraud data."])
    h(1, "CHAPTER 9: BIBLIOGRAPHY AND REFERENCES")
    t(["Reference", "Use"], [["Streamlit Documentation", "Application framework, session state, forms, deployment."], ["Plotly Python Documentation", "Interactive dashboard charts."], ["pandas Documentation", "Data loading and transformations."], ["scikit-learn Documentation", "Pipelines, preprocessing, metrics, gradient boosting."], ["XGBoost Documentation", "Fraud and credit classifiers."], ["imbalanced-learn Documentation", "SMOTE for fraud class balancing."], ["SQLAlchemy Documentation", "ORM models and sessions."], ["bcrypt Documentation", "Password hashing."], ["GitHub Large File Storage Documentation", "Large model file handling."], ["Streamlit Community Cloud Documentation", "Cloud deployment considerations."]])
    h(1, "Appendix A: Canva Presentation Prompt")
    p("The Canva prompt is stored separately at docs/presentation/Fraud Pulse Phase_2 Canva Prompt.txt.")
    p(CANVA_PROMPT)


def rpr(bold=False, size=24, color="000000"):
    return f'<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:color w:val="{color}"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>{"<w:b/>" if bold else ""}</w:rPr>'


def para(text="", kind="Normal", bold=False, size=24, color="000000", center=False):
    if kind == "Title":
        bold, size, color, center = True, 44, "1F3444", True
    elif kind == "Heading1":
        bold, size, color = True, 32, "1F3444"
    elif kind == "Heading2":
        bold, size, color = True, 28, "1F7A7A"
    jc = '<w:jc w:val="center"/>' if center else ""
    text = escape(str(text)).replace("\n", "<w:br/>")
    return f'<w:p><w:pPr>{jc}</w:pPr><w:r>{rpr(bold, size, color)}<w:t xml:space="preserve">{text}</w:t></w:r></w:p>'


def bullet(text):
    return f'<w:p><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr><w:r>{rpr()}<w:t xml:space="preserve">- {escape(str(text))}</w:t></w:r></w:p>'


def table(headers, rows):
    width = max(1200, int(9000 / len(headers)))
    out = ['<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/><w:tblBorders><w:top w:val="single" w:sz="4" w:color="D9E2EA"/><w:left w:val="single" w:sz="4" w:color="D9E2EA"/><w:bottom w:val="single" w:sz="4" w:color="D9E2EA"/><w:right w:val="single" w:sz="4" w:color="D9E2EA"/><w:insideH w:val="single" w:sz="4" w:color="D9E2EA"/><w:insideV w:val="single" w:sz="4" w:color="D9E2EA"/></w:tblBorders></w:tblPr>']
    def cell(value, head=False):
        fill = '<w:shd w:fill="E9EEF2"/>' if head else ""
        return f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{fill}</w:tcPr>{para(value, bold=head, size=22, color="1F3444" if head else "000000")}</w:tc>'
    out.append("<w:tr>" + "".join(cell(x, True) for x in headers) + "</w:tr>")
    for row in rows:
        out.append("<w:tr>" + "".join(cell(x) for x in row) + "</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def write_docx():
    build_content()
    body = []
    for item in blocks:
        if item[0] == "h":
            body.append(para(item[2], "Title" if item[1] == 0 else "Heading1" if item[1] == 1 else "Heading2"))
        elif item[0] == "p":
            body.append(para(item[1]))
        elif item[0] == "b":
            body.append(bullet(item[1]))
        elif item[0] == "t":
            body.append(table(item[1], item[2]))
        elif item[0] == "pb":
            body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>' + "".join(body) + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1080" w:bottom="1440" w:left="1080" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>'
    content_types = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    word_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'

    DOCS.mkdir(parents=True, exist_ok=True)
    PROMPT_OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/_rels/document.xml.rels", word_rels)
        z.writestr("word/document.xml", document)
    PROMPT_OUT.write_text(CANVA_PROMPT, encoding="utf-8")
    print(OUT)
    print(PROMPT_OUT)


if __name__ == "__main__":
    write_docx()
