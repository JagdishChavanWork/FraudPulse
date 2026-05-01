from __future__ import annotations

import json
from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from xgboost import XGBClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import CREDIT_DASHBOARD_DATASET


ARTIFACT_DIR = PROJECT_ROOT / "models" / "credit_risk"
MODEL_PATH = ARTIFACT_DIR / "enhanced_approved_flag_classifier.joblib"
METRICS_PATH = ARTIFACT_DIR / "enhanced_approved_flag_metrics.json"
REPORT_PATH = ARTIFACT_DIR / "enhanced_approved_flag_classification_report.csv"
CONFUSION_MATRIX_PATH = ARTIFACT_DIR / "enhanced_approved_flag_confusion_matrix.csv"

TARGET_COLUMN = "Approved_Flag"
EXCLUDED_COLUMNS = {
    TARGET_COLUMN,
    "Risk_Profile",
    "Income_Bucket",
}


def load_dataset(path: Path = CREDIT_DASHBOARD_DATASET) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Enhanced credit dashboard dataset not found: {path}")
    return pd.read_csv(path)


def build_model(categorical_features: list[str], numeric_features: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("numeric", "passthrough", numeric_features),
        ]
    )

    classifier = XGBClassifier(
        objective="multi:softprob",
        num_class=4,
        n_estimators=850,
        max_depth=5,
        learning_rate=0.035,
        subsample=0.92,
        colsample_bytree=0.9,
        min_child_weight=2,
        reg_lambda=1.6,
        reg_alpha=0.04,
        eval_metric="mlogloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def train() -> dict:
    frame = load_dataset()
    feature_columns = [column for column in frame.columns if column not in EXCLUDED_COLUMNS]
    x = frame[feature_columns].copy()

    categorical_features = x.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_features = [column for column in feature_columns if column not in categorical_features]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(frame[TARGET_COLUMN])

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = build_model(categorical_features, numeric_features)
    model.fit(x_train, y_train)

    probabilities = model.predict_proba(x_test)
    probabilities = probabilities / probabilities.sum(axis=1, keepdims=True)
    predictions = probabilities.argmax(axis=1)

    metrics = {
        "target": TARGET_COLUMN,
        "classes": label_encoder.classes_.tolist(),
        "rows": int(len(frame)),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "categorical_features": categorical_features,
        "numeric_features": numeric_features,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "macro_f1": float(f1_score(y_test, predictions, average="macro")),
        "weighted_f1": float(f1_score(y_test, predictions, average="weighted")),
        "multiclass_log_loss": float(log_loss(y_test, probabilities, labels=list(range(len(label_encoder.classes_))))),
    }

    report = pd.DataFrame(
        classification_report(
            y_test,
            predictions,
            target_names=label_encoder.classes_,
            output_dict=True,
            zero_division=0,
        )
    ).transpose()
    confusion = pd.DataFrame(
        confusion_matrix(y_test, predictions),
        index=[f"actual_{label}" for label in label_encoder.classes_],
        columns=[f"predicted_{label}" for label in label_encoder.classes_],
    )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "label_encoder": label_encoder,
            "feature_columns": feature_columns,
            "target_column": TARGET_COLUMN,
        },
        MODEL_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    report.to_csv(REPORT_PATH)
    confusion.to_csv(CONFUSION_MATRIX_PATH)

    return metrics


if __name__ == "__main__":
    training_metrics = train()
    print(json.dumps(training_metrics, indent=2))
