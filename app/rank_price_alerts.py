from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/price_anomalies_enriched.csv")
OUTPUT_FILE = Path("reports/anomalies/price_alerts_ranked.csv")


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    alerts = df[df["price_signal"] == True].copy()

    alerts = alerts.sort_values(
        "price_deviation_abs", ascending=False
    )

    alerts["alert_rank"] = range(1, len(alerts) + 1)

    columns_to_keep = [
    "listing_id",
    "alert_rank",
    "brand",
    "model",
    "year_of_manufacture",
    "engine_cc",
    "transmission",
    "fuel_type",
    "mileage_km",
    "town",
    "listing_date",
    "condition",
    "price",
    "price_median",
    "expected_price_low",
    "expected_price_high",
    "price_deviation_percentage",
    "price_anomaly_direction",
    "price_alert_reason",
    "price_group_count",
    "price_reference_quality",
    "duplicate_record_count",
    "duplicate_record_flag",
    "review_priority",
]

    existing_columns = [
    column
    for column in columns_to_keep
    if column in alerts.columns
]

    alerts[existing_columns].to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Total alerts: {len(alerts)}")
    print(alerts[existing_columns].head(10).to_string(index=False))


if __name__ == "__main__":
    main()