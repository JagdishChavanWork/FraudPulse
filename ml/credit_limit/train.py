from __future__ import annotations

import json
from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import CREDIT_MODEL_DATASET


ARTIFACT_DIR = PROJECT_ROOT / "models" / "credit_limit"
MODEL_PATH = ARTIFACT_DIR / "max_credit_amount_regressor.joblib"
METRICS_PATH = ARTIFACT_DIR / "max_credit_amount_metrics.json"

TARGET_COLUMN = "Max_Credit_Amount"
EXCLUDED_COLUMNS = {
    TARGET_COLUMN,
    "Approved_Flag",
}


def load_dataset(path: Path = CREDIT_MODEL_DATASET) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Credit amount dataset not found: {path}")

    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def build_model(categorical_features: list[str], numeric_features: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("numeric", "passthrough", numeric_features),
        ]
    )

    xgb_model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=650,
        max_depth=5,
        learning_rate=0.035,
        subsample=0.92,
        colsample_bytree=0.9,
        reg_lambda=1.4,
        reg_alpha=0.03,
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
    )

    random_forest = RandomForestRegressor(
        n_estimators=300,
        max_depth=20,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    extra_trees = ExtraTreesRegressor(
        n_estimators=300,
        max_depth=20,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    ensemble = VotingRegressor(
        estimators=[
            ("xgboost", xgb_model),
            ("random_forest", random_forest),
            ("extra_trees", extra_trees),
        ],
        weights=[3, 1, 1],
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", ensemble),
        ]
    )


def train() -> dict:
    frame = load_dataset()
    feature_columns = [column for column in frame.columns if column not in EXCLUDED_COLUMNS]
    x = frame[feature_columns].copy()
    y = frame[TARGET_COLUMN].astype(float)

    categorical_features = x.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_features = [column for column in feature_columns if column not in categorical_features]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = build_model(categorical_features, numeric_features)
    model.fit(x_train, y_train)

    predictions = np.clip(model.predict(x_test), 0, None)
    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
    mae = float(mean_absolute_error(y_test, predictions))
    r2 = float(r2_score(y_test, predictions))
    mape = float((np.abs((y_test - predictions) / y_test.clip(lower=1))).mean() * 100)

    metrics = {
        "target": TARGET_COLUMN,
        "rows": int(len(frame)),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "feature_columns": feature_columns,
        "categorical_features": categorical_features,
        "numeric_features": numeric_features,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "mape_percent": mape,
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_columns": feature_columns,
            "target_column": TARGET_COLUMN,
        },
        MODEL_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    training_metrics = train()
    print(json.dumps(training_metrics, indent=2))
