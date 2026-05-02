from __future__ import annotations

from contextlib import suppress
import json
from typing import Any

from database.connection import create_session
from database.models import PredictionLog


def _json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def serialize_payload(payload: dict) -> str:
    return json.dumps(payload, default=_json_default, sort_keys=True)


def log_prediction(
    employee_id: str | None,
    module_name: str,
    input_payload: dict,
    prediction_label: str | None,
    prediction_score: float | None,
) -> bool:
    if not employee_id:
        return False

    with suppress(Exception):
        with create_session() as session:
            session.add(
                PredictionLog(
                    employee_id=employee_id,
                    module_name=module_name,
                    input_payload=serialize_payload(input_payload),
                    prediction_label=prediction_label,
                    prediction_score=prediction_score,
                )
            )
            session.commit()
        return True

    return False
