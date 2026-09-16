from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/cleaned_vehicle_prices.csv")
OUTPUT_FILE = Path("reports/anomalies/vehicle_context_signals.csv")
GROUP_COLUMNS = ["brand", "model", "year_of_manufacture"]
IQR_MULTIPLIER = 1.5
REFERENCE_YEAR = 2025


def add_iqr_flag(
    df: pd.DataFrame,
    value_column: str,
    prefix: str,
) -> pd.Series:
    stats = (
        df.groupby(GROUP_COLUMNS)[value_column]
        .agg(
            median="median",
            q1=lambda values: values.quantile(0.25),
            q3=lambda values: values.quantile(0.75),
        )
        .reset_index()
    )
    stats["iqr"] = stats["q3"] - stats["q1"]
    stats["lower"] = stats["q1"] - IQR_MULTIPLIER * stats["iqr"]
    stats["upper"] = stats["q3"] + IQR_MULTIPLIER * stats["iqr"]
    merged = df[GROUP_COLUMNS].merge(stats, on=GROUP_COLUMNS, how="left")
    return (
        (df[value_column] < merged["lower"])
        | (df[value_column] > merged["upper"])
    ).rename(prefix)


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    required = set(GROUP_COLUMNS) | {
        "price",
        "mileage_km",
        "condition",
        "transmission",
        "fuel_type",
        "engine_cc",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = df.copy()
    result["vehicle_age_years"] = (
        REFERENCE_YEAR - result["year_of_manufacture"]
    ).clip(lower=1)
    result["mileage_per_age_year"] = (
        result["mileage_km"] / result["vehicle_age_years"]
    )
    result["price_anomaly"] = add_iqr_flag(result, "price", "price_anomaly")
    result["mileage_anomaly"] = add_iqr_flag(
        result, "mileage_km", "mileage_anomaly"
    )
    result["age_mileage_anomaly"] = add_iqr_flag(
        result, "mileage_per_age_year", "age_mileage_anomaly"
    )
    result["combined_review_priority"] = (
        result["price_anomaly"].astype(int)
        + result["mileage_anomaly"].astype(int)
        + result["age_mileage_anomaly"].astype(int)
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved: {OUTPUT_FILE}")
    print(
        result[
            [
                "price_anomaly",
                "mileage_anomaly",
                "age_mileage_anomaly",
            ]
        ].sum()
    )


if __name__ == "__main__":
    main()
