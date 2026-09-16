from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/cleaned_vehicle_prices.csv")
OUTPUT_DIR = Path("reports/anomalies")
OUTPUT_FILE = OUTPUT_DIR / "price_anomalies.csv"

GROUP_COLUMNS = [
    "brand",
    "model",
    "year_of_manufacture",
]

MIN_GROUP_SIZE = 5
IQR_MULTIPLIER = 1.5


def calculate_group_statistics(df: pd.DataFrame) -> pd.DataFrame:
    group_stats = (
        df.groupby(GROUP_COLUMNS)["price"]
        .agg(
            group_count="count",
            group_median="median",
            group_q1=lambda values: values.quantile(0.25),
            group_q3=lambda values: values.quantile(0.75),
        )
        .reset_index()
    )

    group_stats["group_iqr"] = (
        group_stats["group_q3"] - group_stats["group_q1"]
    )

    group_stats["lower_bound"] = (
        group_stats["group_q1"] - IQR_MULTIPLIER * group_stats["group_iqr"]
    )

    group_stats["upper_bound"] = (
        group_stats["group_q3"] + IQR_MULTIPLIER * group_stats["group_iqr"]
    )

    return group_stats


def create_reason(row: pd.Series) -> str:
    if row["price"] < row["lower_bound"]:
        return "price_below_comparable_range"

    if row["price"] > row["upper_bound"]:
        return "price_above_comparable_range"

    return "within_comparable_range"


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    group_stats = calculate_group_statistics(df)

    result = df.merge(
        group_stats,
        on=GROUP_COLUMNS,
        how="left",
    )

    result["eligible_for_detection"] = (
        result["group_count"] >= MIN_GROUP_SIZE
    )

    result["price_anomaly"] = (
        result["eligible_for_detection"]
        & (
            (result["price"] < result["lower_bound"])
            | (result["price"] > result["upper_bound"])
        )
    )

    result["anomaly_reason"] = result.apply(create_reason, axis=1)

    result["price_deviation_percentage"] = (
        (result["price"] - result["group_median"])
        / result["group_median"]
        * 100
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    eligible_count = int(result["eligible_for_detection"].sum())
    anomaly_count = int(result["price_anomaly"].sum())

    print(f"Saved anomaly results to: {OUTPUT_FILE}")
    print(f"Total listings: {len(result)}")
    print(f"Eligible listings: {eligible_count}")
    print(f"Potential price anomalies: {anomaly_count}")

    print("\nAnomalies by reason:")
    print(
        result.loc[result["price_anomaly"], "anomaly_reason"]
        .value_counts()
    )

    print("\nMost unusual listings:")
    columns_to_show = [
        "brand",
        "model",
        "year_of_manufacture",
        "price",
        "group_count",
        "group_median",
        "lower_bound",
        "upper_bound",
        "price_deviation_percentage",
        "anomaly_reason",
    ]

    print(
        result.loc[result["price_anomaly"], columns_to_show]
        .sort_values(
            "price_deviation_percentage",
            key=lambda values: values.abs(),
            ascending=False,
        )
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
    