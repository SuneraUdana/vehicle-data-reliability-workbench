from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/review_priority.csv")
OUTPUT_FILE = Path(
    "reports/anomalies/price_anomalies_enriched.csv"
)

GROUP_COLUMNS = [
    "brand",
    "model",
    "year_of_manufacture",
]


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    df["listing_id"] = (
        "listing_"
        + (df.index + 1).astype(str).str.zfill(5)
    )

    group_price_stats = (
        df.groupby(GROUP_COLUMNS)["price"]
        .agg(
            price_group_count="count",
            price_median="median",
            price_q1=lambda values: values.quantile(0.25),
            price_q3=lambda values: values.quantile(0.75),
        )
        .reset_index()
    )

    group_price_stats["price_iqr"] = (
        group_price_stats["price_q3"]
        - group_price_stats["price_q1"]
    )

    df = df.merge(
        group_price_stats,
        on=GROUP_COLUMNS,
        how="left",
    )

    df["expected_price_low"] = df["price_q1"]
    df["expected_price_high"] = df["price_q3"]

    df["price_deviation_percentage"] = (
        (
            (df["price"] - df["price_median"])
            / df["price_median"]
        )
        * 100
    )

    df["price_deviation_abs"] = (
        df["price_deviation_percentage"].abs()
    )

    df["price_anomaly_direction"] = (
        "within_expected_range"
    )

    df.loc[
        df["price"] < df["expected_price_low"],
        "price_anomaly_direction",
    ] = "below_expected_range"

    df.loc[
        df["price"] > df["expected_price_high"],
        "price_anomaly_direction",
    ] = "above_expected_range"

    df["price_alert_reason"] = (
        df["price_anomaly_direction"]
        + "; deviation_from_group_median="
        + df["price_deviation_percentage"]
        .round(1)
        .astype(str)
        + "%"
    )

    df["price_reference_quality"] = "low"

    df.loc[
        df["price_group_count"] >= 5,
        "price_reference_quality",
    ] = "medium"

    df.loc[
        df["price_group_count"] >= 10,
        "price_reference_quality",
    ] = "high"

    duplicate_columns = [
        "brand",
        "model",
        "year_of_manufacture",
        "price",
    ]

    df["duplicate_record_count"] = (
        df.groupby(duplicate_columns)["price"]
        .transform("size")
    )

    df["duplicate_record_flag"] = (
        df["duplicate_record_count"] > 1
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Rows: {len(df)}")
    print(
        "Price anomaly directions:"
    )
    print(
        df["price_anomaly_direction"]
        .value_counts()
        .to_string()
    )
    print(
        "\nReference quality:"
    )
    print(
        df["price_reference_quality"]
        .value_counts()
        .to_string()
    )
    print(
        "\nRows in repeated groups:",
        int(df["duplicate_record_flag"].sum()),
    )


if __name__ == "__main__":
    main()