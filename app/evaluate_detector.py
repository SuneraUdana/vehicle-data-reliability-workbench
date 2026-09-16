from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "reports/anomalies/review_sample_completed.csv"
)
OUTPUT_FILE = Path(
    "reports/anomalies/evaluation_report.txt"
)


def calculate_metrics(
    predicted: pd.Series,
    actual: pd.Series,
) -> dict[str, float | int | None]:
    true_positive = int((predicted & actual).sum())
    false_positive = int((predicted & ~actual).sum())
    true_negative = int((~predicted & ~actual).sum())
    false_negative = int((~predicted & actual).sum())

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else None
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else None
    )

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "true_negative": true_negative,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
    }


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    reviewed = df[
        df["review_label"].notna()
        & (df["review_label"] != "insufficient_evidence")
    ].copy()

    strict_actual = reviewed["review_label"].eq(
        "confirmed_anomaly"
    )

    broad_actual = reviewed["review_label"].isin(
        ["confirmed_anomaly", "probably_anomaly"]
    )

    predicted = reviewed["price_anomaly"].astype(bool)

    strict_metrics = calculate_metrics(
        predicted,
        strict_actual,
    )

    broad_metrics = calculate_metrics(
        predicted,
        broad_actual,
    )

    report_lines = [
        "PRICE ANOMALY DETECTOR EVALUATION",
        "=" * 60,
        f"Total reviewed rows: {len(df)}",
        f"Excluded as insufficient evidence: "
        f"{(df['review_label'] == 'insufficient_evidence').sum()}",
        f"Evaluated rows: {len(reviewed)}",
        "",
        "REVIEW LABEL COUNTS",
        "-" * 60,
        df["review_label"].value_counts().to_string(),
        "",
        "STRICT EVALUATION",
        "-" * 60,
        "Positive label: confirmed_anomaly",
        str(strict_metrics),
        "",
        "BROAD EVALUATION",
        "-" * 60,
        "Positive labels: confirmed_anomaly + probably_anomaly",
        str(broad_metrics),
    ]

    OUTPUT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print("\n".join(report_lines))
    print(f"\nSaved report to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()