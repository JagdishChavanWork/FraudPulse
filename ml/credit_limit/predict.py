from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODEL_PATH = PROJECT_ROOT / "models" / "credit_limit" / "max_credit_amount_regressor.joblib"


def load_artifact(path: Path = MODEL_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Credit amount model artifact not found: {path}")
    return joblib.load(path)


def predict_max_credit_amount(input_payload: dict) -> dict:
    artifact = load_artifact()
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    frame = pd.DataFrame([input_payload])
    frame = frame.reindex(columns=feature_columns)
    prediction = float(np.clip(model.predict(frame)[0], 0, None))

    return {
        "max_credit_amount": prediction,
        "rounded_max_credit_amount": round(prediction / 1000) * 1000,
    }
