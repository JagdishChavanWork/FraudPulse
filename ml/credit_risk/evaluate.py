import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = PROJECT_ROOT / "models" / "credit_risk" / "approved_flag_metrics.json"
ENHANCED_METRICS_PATH = PROJECT_ROOT / "models" / "credit_risk" / "enhanced_approved_flag_metrics.json"
REPORT_PATH = PROJECT_ROOT / "models" / "credit_risk" / "approved_flag_classification_report.csv"
CONFUSION_MATRIX_PATH = PROJECT_ROOT / "models" / "credit_risk" / "approved_flag_confusion_matrix.csv"


def main() -> None:
    if not METRICS_PATH.exists():
        raise FileNotFoundError("Train the credit risk classifier before running evaluation.")

    print(METRICS_PATH.read_text(encoding="utf-8"))
    print(f"Classification report: {REPORT_PATH}")
    print(f"Confusion matrix: {CONFUSION_MATRIX_PATH}")
    if ENHANCED_METRICS_PATH.exists():
        print("\nEnhanced bureau model:")
        print(ENHANCED_METRICS_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
