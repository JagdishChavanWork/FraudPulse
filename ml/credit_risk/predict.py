from pathlib import Path
import sys

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODEL_PATH = PROJECT_ROOT / "models" / "credit_risk" / "approved_flag_classifier.joblib"
ENHANCED_MODEL_PATH = PROJECT_ROOT / "models" / "credit_risk" / "enhanced_approved_flag_classifier.joblib"


def load_artifact(path: Path = MODEL_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Credit risk model artifact not found: {path}")
    return joblib.load(path)


def predict_approved_flag(input_payload: dict) -> dict:
    artifact = load_artifact()
    model = artifact["model"]
    label_encoder = artifact["label_encoder"]
    feature_columns = artifact["feature_columns"]

    frame = pd.DataFrame([input_payload])
    frame = frame.reindex(columns=feature_columns)

    probabilities = model.predict_proba(frame)[0]
    probabilities = probabilities / probabilities.sum()
    predicted_index = int(probabilities.argmax())
    predicted_label = label_encoder.inverse_transform([predicted_index])[0]
    class_probabilities = {
        label: float(probabilities[index])
        for index, label in enumerate(label_encoder.classes_)
    }

    return {
        "predicted_approved_flag": predicted_label,
        "confidence": float(probabilities[predicted_index]),
        "class_probabilities": class_probabilities,
    }


def predict_enhanced_approved_flag(input_payload: dict) -> dict:
    artifact = load_artifact(ENHANCED_MODEL_PATH)
    model = artifact["model"]
    label_encoder = artifact["label_encoder"]
    feature_columns = artifact["feature_columns"]

    frame = pd.DataFrame([input_payload])
    frame = frame.reindex(columns=feature_columns)

    probabilities = model.predict_proba(frame)[0]
    probabilities = probabilities / probabilities.sum()
    predicted_index = int(probabilities.argmax())
    predicted_label = label_encoder.inverse_transform([predicted_index])[0]
    class_probabilities = {
        label: float(probabilities[index])
        for index, label in enumerate(label_encoder.classes_)
    }

    return {
        "predicted_approved_flag": predicted_label,
        "confidence": float(probabilities[predicted_index]),
        "class_probabilities": class_probabilities,
    }
