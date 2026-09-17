from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/analyst_review.csv")
LABELS = {
    "confirmed_anomaly",
    "probably_anomaly",
    "appears_normal",
    "insufficient_evidence",
    "data_error",
}
CONFIDENCE = {"high", "medium", "low"}


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    invalid_labels = sorted(set(df["review_label"].dropna()) - LABELS)
    invalid_confidence = sorted(
        set(df["review_confidence"].dropna()) - CONFIDENCE
    )
    blank_labels = int(df["review_label"].isna().sum())

    print(f"Rows: {len(df)}")
    print(f"Blank labels: {blank_labels}")
    print(f"Invalid review_label values: {invalid_labels}")
    print(f"Invalid review_confidence values: {invalid_confidence}")

    if len(df) != 100 or blank_labels or invalid_labels or invalid_confidence:
        raise ValueError("Analyst review validation failed")


if __name__ == "__main__":
    main()
