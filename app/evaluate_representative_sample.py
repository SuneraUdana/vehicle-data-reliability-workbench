from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "reports/anomalies/representative_review_sample_completed.csv"
)
OUTPUT_FILE = Path(
    "reports/anomalies/representative_evaluation.txt"
)


def metrics(
    predicted: pd.Series,
    actual: pd.Series,
) -> dict[str, float | int | None]:
    tp = int((predicted & actual).sum())
    fp = int((predicted & ~actual).sum())
    tn = int((~predicted & ~actual).sum())
    fn = int((~predicted & actual).sum())

    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None
        and recall is not None
        and precision + recall
        else None
    )

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 3) if precision is not None else None,
        "recall": round(recall, 3) if recall is not None else None,
        "f1": round(f1, 3) if f1 is not None else None,
    }


def parse_bool(series: pd.Series) -> pd.Series:
    normalized = series.astype(str).str.strip().str.lower()
    invalid = ~normalized.isin({"true", "false"})
    if invalid.any():
        values = sorted(normalized[invalid].unique())
        raise ValueError(f"Invalid boolean values: {values}")
    return normalized.eq("true")


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    required_columns = {
        "review_label",
        "flag_baseline",
        "flag_iqr_and_15pct",
        "flag_iqr_and_20pct",
        "flag_iqr_and_30pct",
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    df = df[
        df["review_label"].notna()
        & (df["review_label"] != "insufficient_evidence")
    ].copy()

    actual = df["review_label"].isin(
        ["probably_anomaly", "confirmed_anomaly", "data_error"]
    )

    detectors = {
        "baseline": "flag_baseline",
        "15_percent": "flag_iqr_and_15pct",
        "20_percent": "flag_iqr_and_20pct",
        "30_percent": "flag_iqr_and_30pct",
    }

    report_lines = [
        "REPRESENTATIVE SAMPLE EVALUATION",
        "=" * 60,
        f"Evaluated rows: {len(df)}",
        "Positive labels: probably_anomaly, confirmed_anomaly, data_error",
        "",
    ]

    for name, column in detectors.items():
        predicted = parse_bool(df[column])
        result = metrics(predicted, actual)

        report_lines.append(name)
        report_lines.append("-" * 60)
        report_lines.append(str(result))
        report_lines.append("")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print("\n".join(report_lines))
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
