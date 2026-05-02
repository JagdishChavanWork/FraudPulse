import json

from modules.services import prediction_log_service
from modules.services.prediction_log_service import log_prediction, serialize_payload


class FakeSession:
    def __init__(self):
        self.records = []
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def add(self, record):
        self.records.append(record)

    def commit(self):
        self.committed = True


def test_serialize_payload_handles_non_standard_values():
    class CustomValue:
        def __str__(self):
            return "custom"

    payload = serialize_payload({"b": CustomValue(), "a": 1})

    assert json.loads(payload) == {"a": 1, "b": "custom"}


def test_log_prediction_writes_prediction_log(monkeypatch):
    fake_session = FakeSession()
    monkeypatch.setattr(prediction_log_service, "create_session", lambda: fake_session)

    logged = log_prediction(
        "ANL001",
        "fraud_detection_prediction",
        {"amount": 1000},
        "LOW",
        0.12,
    )

    assert logged is True
    assert fake_session.committed is True
    assert len(fake_session.records) == 1
    record = fake_session.records[0]
    assert record.employee_id == "ANL001"
    assert record.module_name == "fraud_detection_prediction"
    assert record.prediction_label == "LOW"
    assert record.prediction_score == 0.12


def test_log_prediction_skips_when_employee_missing():
    logged = log_prediction(
        None,
        "credit_risk_prediction",
        {"income": 50000},
        "P2",
        0.91,
    )

    assert logged is False
