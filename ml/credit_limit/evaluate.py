import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = PROJECT_ROOT / "models" / "credit_limit" / "max_credit_amount_metrics.json"


def main() -> None:
    if not METRICS_PATH.exists():
        raise FileNotFoundError("Train the max credit amount model before running evaluation.")

    print(METRICS_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
