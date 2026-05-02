from __future__ import annotations

import json
from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

try:
    from imblearn.over_sampling import SMOTE
except ImportError:  # pragma: no cover - supports first run before dependency install
    SMOTE = None

try:
    from xgboost import XGBClassifier
except ImportError:  # pragma: no cover
    XGBClassifier = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import FRAUD_DATASET


ARTIFACT_DIR = PROJECT_ROOT / "models" / "fraud"
MODEL_PATH = ARTIFACT_DIR / "fraud_xgb_classifier.joblib"
SCALER_PATH = ARTIFACT_DIR / "fraud_scaler.joblib"
FEATURES_PATH = ARTIFACT_DIR / "fraud_feature_columns.json"
THRESHOLD_PATH = ARTIFACT_DIR / "fraud_threshold.json"
METRICS_PATH = ARTIFACT_DIR / "fraud_metrics.json"
REPORT_PATH = ARTIFACT_DIR / "fraud_classification_report.csv"
CONFUSION_MATRIX_PATH = ARTIFACT_DIR / "fraud_confusion_matrix.csv"
IMPORTANCE_PATH = ARTIFACT_DIR / "fraud_feature_importance.csv"

TARGET_COLUMN = "is_fraud"
DASHBOARD_ONLY_COLUMNS = {"account_type", "txn_type", "age_group", "fraud_type"}
RANDOM_STATE = 42


def load_dataset(path: Path = FRAUD_DATASET) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Fraud dataset not found: {path}")
    return pd.read_csv(path)


def build_model(y_train: pd.Series):
    if XGBClassifier is not None:
        fraud_count = int((y_train == 1).sum())
        legit_count = int((y_train == 0).sum())
        scale_pos_weight = max(1.0, legit_count / max(fraud_count, 1))
        return XGBClassifier(
            objective="binary:logistic",
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            min_child_weight=3,
            reg_lambda=1.4,
            reg_alpha=0.02,
            scale_pos_weight=scale_pos_weight,
            eval_metric="aucpr",
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )

    return RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )


def _choose_threshold(y_true, probabilities: pd.Series) -> tuple[float, list[dict]]:
    rows = []
    best_threshold = 0.4
    best_score = -1.0
    for step in range(30, 61, 5):
        threshold = step / 100
        predictions = (probabilities >= threshold).astype(int)
        precision = precision_score(y_true, predictions, zero_division=0)
        recall = recall_score(y_true, predictions, zero_division=0)
        f1 = f1_score(y_true, predictions, zero_division=0)
        rows.append(
            {
                "threshold": threshold,
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
            }
        )

        business_score = (0.65 * recall) + (0.35 * f1)
        if recall >= 0.80 and business_score > best_score:
            best_score = business_score
            best_threshold = threshold

    return best_threshold, rows


def train() -> dict:
    frame = load_dataset()
    excluded = DASHBOARD_ONLY_COLUMNS | {TARGET_COLUMN}
    feature_columns = [column for column in frame.columns if column not in excluded]
    x = frame[feature_columns].copy()
    y = frame[TARGET_COLUMN].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    resampled = False
    if SMOTE is not None:
        sampler = SMOTE(sampling_strategy=0.30, random_state=RANDOM_STATE)
        x_train_scaled, y_train = sampler.fit_resample(x_train_scaled, y_train)
        resampled = True

    model = build_model(pd.Series(y_train))
    model.fit(x_train_scaled, y_train)

    probabilities = model.predict_proba(x_test_scaled)[:, 1]
    threshold, threshold_rows = _choose_threshold(y_test, probabilities)
    predictions = (probabilities >= threshold).astype(int)

    report = pd.DataFrame(
        classification_report(y_test, predictions, target_names=["Legitimate", "Fraud"], output_dict=True, zero_division=0)
    ).transpose()
    confusion = pd.DataFrame(
        confusion_matrix(y_test, predictions),
        index=["actual_legitimate", "actual_fraud"],
        columns=["predicted_legitimate", "predicted_fraud"],
    )

    importances = getattr(model, "feature_importances_", None)
    importance_frame = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": importances if importances is not None else [0.0] * len(feature_columns),
        }
    ).sort_values("importance", ascending=False)

    metrics = {
        "model_type": model.__class__.__name__,
        "rows": int(len(frame)),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "smote_applied": resampled,
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "threshold": float(threshold),
        "fraud_precision": float(precision_score(y_test, predictions, zero_division=0)),
        "fraud_recall": float(recall_score(y_test, predictions, zero_division=0)),
        "fraud_f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "threshold_tuning": threshold_rows,
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    FEATURES_PATH.write_text(json.dumps(feature_columns, indent=2), encoding="utf-8")
    THRESHOLD_PATH.write_text(json.dumps({"threshold": threshold}, indent=2), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    report.to_csv(REPORT_PATH)
    confusion.to_csv(CONFUSION_MATRIX_PATH)
    importance_frame.to_csv(IMPORTANCE_PATH, index=False)

    return metrics


if __name__ == "__main__":
    training_metrics = train()
    print(json.dumps(training_metrics, indent=2))
