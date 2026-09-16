from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/age_mileage_anomalies.csv")
PRICE_INPUT_FILE = Path("reports/anomalies/price_anomalies.csv")
OUTPUT_FILE = Path("reports/anomalies/review_priority.csv")


def parse_bool(series: pd.Series, column: str) -> pd.Series:
    values = series.astype(str).str.strip().str.lower()
    invalid = ~values.isin({"true", "false"})
    if invalid.any():
        raise ValueError(
            f"Invalid boolean values in {column}: "
            f"{sorted(values[invalid].unique())}"
        )
    return values.eq("true")


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")
    if not PRICE_INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {PRICE_INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    price_df = pd.read_csv(PRICE_INPUT_FILE)

    alignment_columns = ["brand", "model", "year_of_manufacture", "price"]
    if len(df) != len(price_df):
        raise ValueError(
            "Age/mileage and price anomaly files have different row counts"
        )
    if not df[alignment_columns].equals(price_df[alignment_columns]):
        raise ValueError(
            "Age/mileage and price anomaly files are not row-aligned"
        )

    df["price_signal"] = parse_bool(
        price_df["price_anomaly"], "price_anomaly"
    )
    df["mileage_signal"] = parse_bool(
        df["mileage_anomaly"], "mileage_anomaly"
    )
    df["age_mileage_signal"] = parse_bool(
        df["annual_mileage_anomaly"], "annual_mileage_anomaly"
    )

    signal_columns = [
        "price_signal",
        "mileage_signal",
        "age_mileage_signal",
    ]
    df["signal_count"] = df[signal_columns].astype(int).sum(axis=1)
    df["review_priority"] = "low"
    df.loc[df["signal_count"] == 1, "review_priority"] = "medium"
    df.loc[df["signal_count"] >= 2, "review_priority"] = "high"
    df["review_priority_reason"] = "no anomaly signals"
    df.loc[
        df["signal_count"] == 1,
        "review_priority_reason",
    ] = "one anomaly signal requires review"
    df.loc[
        df["signal_count"] >= 2,
        "review_priority_reason",
    ] = "multiple independent anomaly signals"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(df["review_priority"].value_counts())
    print(df["signal_count"].value_counts().sort_index())


if __name__ == "__main__":
    main()
