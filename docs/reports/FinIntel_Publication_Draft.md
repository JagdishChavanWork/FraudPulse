# FinIntel: An Integrated Machine Learning Platform for Credit Risk Assessment and Fraud Detection in Banking

## Abstract

Banking institutions increasingly require decision-support systems that can handle both borrower-level credit assessment and transaction-level fraud verification within a unified analytical environment. Many existing machine learning studies address credit scoring and fraud detection as separate modeling tasks, while fewer works focus on combining these functions into an operational analyst-facing system. This paper presents **FinIntel**, an integrated banking risk intelligence platform that combines multiclass credit approval prediction, credit amount estimation, fraud detection, dashboard-based management insights, authentication, and prediction logging within a single Streamlit-based application. The platform uses a compact credit-risk workflow based on a soft-voting ensemble of XGBoost, Random Forest, and Extra Trees; an enhanced credit workflow based on XGBoost; a credit amount estimation workflow based on HistGradientBoostingRegressor; and a fraud-detection workflow based on XGBoost with StandardScaler, SMOTE, and threshold tuning. On the enhanced credit dataset, the deployed approval model achieved **77.86% accuracy**, **0.7640 weighted F1-score**, and **0.5024 multiclass log loss**. On the fraud dataset, the deployed XGBoost model achieved **99.88% precision**, **100.00% recall**, **99.94% F1-score**, and **1.0000 ROC-AUC** on the held-out test set. The results indicate that FinIntel is a strong applied decision-support system for integrated banking intelligence. The paper also discusses experimental protocol, reproducibility, deployment considerations, and limitations required for publication-grade evaluation.

## Keywords

Credit risk prediction, fraud detection, banking analytics, XGBoost, ensemble learning, decision support system, financial intelligence

## 1. Introduction

The banking sector is moving from isolated rule-based assessment processes toward data-driven intelligence systems that can support faster and more consistent decisions across lending and fraud operations. In many practical settings, credit-risk models, fraud-screening workflows, dashboards, and audit trails remain fragmented. This fragmentation increases operational overhead and limits the ability of analysts and supervisors to interpret risk in a unified manner.

FinIntel addresses this problem by integrating credit approval prediction, credit amount estimation, fraud verification, and management dashboards into a single platform. The project is not positioned as a new foundation model or a novel deep-learning architecture. Its research value lies instead in the **system-level integration of multiple machine learning workflows**, the use of **task-specific engineered datasets**, and the translation of predictive outputs into **analyst-usable banking operations**.

## 2. Research Motivation and Publication Angle

This work is publication-worthy only when framed as an **applied machine learning system study**, not merely as a college implementation report. The core publication angle is:

1. An integrated banking intelligence platform joining **credit-risk analytics** and **fraud analytics** in one deployable system.
2. A comparative study showing why different models were selected for **compact credit approval**, **enhanced credit approval**, **credit amount estimation**, and **fraud detection**.
3. A deployment-oriented contribution in which predictive models are embedded within **dashboard workflows, user authentication, and prediction logging**, thereby supporting analyst-facing decision processes.

Under this framing, the contribution is not novelty in algorithm invention, but novelty in **applied integration, workflow design, and comparative system evaluation**.

## 3. Contributions

The paper makes the following contributions:

1. It presents a unified banking machine learning platform that combines borrower assessment, fraud screening, visualization, and logging.
2. It constructs a two-level credit-risk pipeline using both a compact borrower dataset and an enhanced engineered credit dataset.
3. It develops a behavior-oriented fraud-detection workflow based on engineered anomaly indicators such as transaction-to-average ratio, balance-drain percentage, and transaction velocity.
4. It provides a comparative model-selection framework that maps model choice to data structure, target type, and operational deployment needs.
5. It documents reproducible project assets, including training scripts, processed datasets, model artifacts, dashboards, and analysis notebooks.

## 4. System Overview

FinIntel is implemented in Python using Streamlit for the application layer, SQLAlchemy for persistence, and saved Joblib artifacts for deployed inference. The system includes three primary functional areas:

1. **Credit Risk Prediction**  
   Performs multiclass approval prediction and maximum credit amount estimation.
2. **Fraud Detection Prediction**  
   Performs transaction-level fraud verification and risk-level generation.
3. **Management Insights**  
   Provides dashboard views for credit-risk segmentation, repayment pressure, enquiry activity, fraud concentration, and pattern analysis.

Supporting components include authentication, session management, preprocessing services, charting services, and centralized prediction logging.

## 5. Datasets

### 5.1 Credit Pipeline

The credit workflow originates from two source datasets:

- `case_study1`: 51,336 records, 26 columns
- `case_study2`: 51,336 records, 62 columns

These datasets were integrated and transformed into two task-specific processed datasets:

- `credit_risk_dataset_with_bands`: 32,000 records, 13 columns
- `Dashboard_Data_Enhanced`: 42,064 records, 57 columns

The compact dataset supports approval modeling and credit amount estimation, while the enhanced dataset supports richer approval modeling and management-level analysis.

### 5.2 Fraud Pipeline

The fraud workflow uses:

- `fraud_dataset_v2`: 70,000 records, 27 columns

The class distribution contains 12,600 fraud records and 57,400 legitimate records. The dataset combines customer profile attributes, transaction descriptors, and engineered anomaly-sensitive fields.

## 6. Methodology

### 6.1 Credit Workflow

The compact credit workflow uses applicant demographics, employment features, tradeline counts, recent enquiry timing, approval class, and credit-band information. The enhanced workflow extends this base with delinquency, enquiry, one-hot encoded demographic fields, product-enquiry indicators, and risk-segmentation features.

### 6.2 Fraud Workflow

The fraud workflow combines raw transactional fields with behavioral indicators such as:

- `amount_to_avg_ratio`
- `balance_drain_pct`
- `hour_anomaly`
- `velocity_24hr`
- `new_txn_type_flag`
- `large_round_amt_flag`
- `days_since_last_txn`
- `prior_fraud_complaint`

### 6.3 Preprocessing

The modeling pipeline includes:

- structured train-test split
- categorical encoding where required
- feature-column synchronization between training and inference
- standardization for the fraud workflow
- SMOTE-based resampling in the fraud training pipeline

## 7. Experimental Protocol

To make the work publication-ready, the experimental section should be presented more rigorously than a standard project report. The recommended protocol for the paper is:

1. Use an **80:20 train-test split** with fixed random seed `42`, matching the project artifacts.
2. Report dataset sizes, feature counts, and target definitions for all workflows.
3. Compare at least the following baseline models:
   - Logistic Regression
   - Decision Tree
   - Random Forest
   - XGBoost
   - Voting Ensemble for compact credit
4. Use consistent evaluation metrics:
   - Credit classification: accuracy, macro F1, weighted F1, multiclass log loss
   - Fraud classification: precision, recall, F1, ROC-AUC
   - Credit amount estimation: MAE, RMSE, R2
5. Include confusion matrices and feature-importance analysis where relevant.
6. Report threshold tuning explicitly for the fraud workflow.

The newly created notebooks in:

- `notebooks/credit_risk/02_ml_model_building.ipynb`
- `notebooks/fraud/01_fraud_detection.ipynb`

are intended to generate the baseline-comparison tables and charts needed for this section.

## 8. Model Selection Rationale

### 8.1 Compact Credit Approval

The compact credit workflow uses a **soft-voting ensemble** of XGBoost, Random Forest, and Extra Trees. This design is appropriate because the compact borrower dataset mixes categorical and numeric financial attributes, and multiclass borrower approval requires stable probability estimates. The deployed saved metrics show:

- Accuracy: **71.70%**
- Macro F1-score: **0.7132**
- Weighted F1-score: **0.7132**
- Multiclass Log Loss: **0.7834**

### 8.2 Enhanced Credit Approval

The enhanced credit workflow uses **XGBoost** as the final deployed model. It was selected because the engineered feature space is larger and more interaction-rich, making gradient-boosted trees a strong fit. The deployed metrics are:

- Accuracy: **77.86%**
- Macro F1-score: **0.6880**
- Weighted F1-score: **0.7640**
- Multiclass Log Loss: **0.5024**

### 8.3 Credit Amount Estimation

The maximum credit amount workflow uses **HistGradientBoostingRegressor**. This model is appropriate because the target is continuous and the borrower feature set contains non-linear relationships. Saved evaluation metrics are:

- MAE: **3772.00**
- RMSE: **10751.53**
- R2: **0.99977**

### 8.4 Fraud Detection

The fraud workflow uses **XGBoost** as the primary deployed classifier, with Random Forest available as a fallback in the training code path. StandardScaler, SMOTE, and threshold tuning are part of the final pipeline. The deployed model achieved:

- Precision: **99.88%**
- Recall: **100.00%**
- F1-score: **99.94%**
- ROC-AUC: **1.0000**
- Operational threshold: **0.50**

## 9. Results

### 9.1 Credit Results

The enhanced credit model outperforms the compact ensemble in overall accuracy and log loss, suggesting that the engineered dataset contains meaningful signals beyond the compact borrower view. Confusion-matrix analysis also indicates that approval class `P2` is the easiest to predict reliably, while `P3` remains the most difficult and would benefit from additional class-separation work.

### 9.2 Fraud Results

The fraud model demonstrates very strong performance on the held-out test set. Feature-importance analysis from the project artifacts shows that `amount_to_avg_ratio` and `balance_drain_pct` are dominant predictors, validating the behavioral feature-engineering strategy.

### 9.3 System-Level Interpretation

From a system perspective, FinIntel’s strongest result is not only high model performance but also the successful integration of prediction, visualization, and traceability into one analyst-oriented environment.

## 10. Comparison With Prior Work

For publication, this section should explicitly compare FinIntel against prior work in three ways:

1. **Problem scope**  
   Many studies address either credit scoring or fraud detection. FinIntel integrates both.
2. **Operational framing**  
   Much prior literature is model-centric. FinIntel is workflow-centric and deployment-oriented.
3. **Evaluation style**  
   The paper should compare baseline and final models for each workflow, not just present final scores.

This comparison should be written conservatively. The paper should not claim algorithmic superiority over all prior work. Instead, it should claim a strong **applied contribution in integrated banking ML operations**.

## 11. Reproducibility

The paper should include a dedicated reproducibility statement. The current project already supports this well because it contains:

- raw and processed datasets
- training scripts
- evaluation scripts
- saved model artifacts
- application source code
- analysis notebooks

To strengthen reproducibility further, the publication version should also state:

1. Python version and package versions
2. fixed random seed values
3. exact train-test split protocol
4. feature inclusion and exclusion rules
5. model hyperparameters
6. threshold-selection logic for fraud detection

## 12. Limitations and Threats to Validity

The paper should explicitly acknowledge the following:

1. The project datasets are task-specific and may not represent all banking populations.
2. The fraud results are very strong, so additional robustness testing is necessary to rule out leakage or overfitting.
3. The credit workflow still shows class difficulty in intermediate approval segments, especially `P3`.
4. The regression model reports extremely strong `R2`, so external validation on unseen operational credit cases is still recommended.
5. The current results are based primarily on single-split evaluation; publication quality would improve with cross-validation and sensitivity testing.

## 13. What Still Needs To Be Done Before Submission

The project is closer to publication readiness now, but not fully ready for journal or conference submission until the following are completed:

1. Execute the new notebooks and capture baseline comparison tables and final figures.
2. Deduplicate and tighten the reference list.
3. Add a formal “Related Work” and “Threats to Validity” section in paper style.
4. Run robustness checks:
   - repeated train-test runs or cross-validation
   - leakage checks for fraud features
   - class distribution sensitivity for credit approval
5. Convert the report language fully from implementation-report style to manuscript style.

## 14. Conclusion

FinIntel is not merely a classroom implementation. It has the foundation of a publishable applied machine learning paper if it is framed correctly as an integrated banking risk intelligence system with comparative model evaluation and analyst-facing deployment. Its strongest publication value lies in combining multiclass credit approval, credit amount estimation, fraud verification, dashboards, and logging into one practical financial decision-support platform. The next step is to complete the experimental baselines and reproducibility packaging so that the work can move from a strong academic project into a credible submission-ready applied research manuscript.
