from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/cleaned_vehicle_prices.csv")
OUTPUT_DIR = Path("reports/anomalies")
OUTPUT_FILE = OUTPUT_DIR / "mileage_anomalies.csv"

GROUP_COLUMNS = [
    "brand",
    "model",
    "year_of_manufacture",
]

MIN_GROUP_SIZE = 5
IQR_MULTIPLIER = 1.5


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    df["listing_date"] = pd.to_datetime(
        df["listing_date"],
        errors="coerce",
    )

    reference_year = int(df["listing_date"].dt.year.max())

    df["vehicle_age"] = (
        reference_year - df["year_of_manufacture"]
    )

    df["vehicle_age_for_calculation"] = (
        df["vehicle_age"].clip(lower=1)
    )

    df["annual_mileage"] = (
        df["mileage_km"]
        / df["vehicle_age_for_calculation"]
    )

    annual_mileage_unique = (
        df["annual_mileage"].nunique(dropna=True)
    )

    if annual_mileage_unique <= 1:
        raise ValueError(
            "Annual mileage has no variation. "
            "Check whether mileage_km is mechanically derived "
            "from vehicle age before running anomaly detection."
        )

    group_stats = (
        df.groupby(GROUP_COLUMNS)["mileage_km"]
        .agg(
            group_count="count",
            mileage_median="median",
            mileage_q1=lambda values: values.quantile(0.25),
            mileage_q3=lambda values: values.quantile(0.75),
        )
        .reset_index()
    )

    group_stats["mileage_iqr"] = (
        group_stats["mileage_q3"]
        - group_stats["mileage_q1"]
    )

    group_stats["mileage_lower_bound"] = (
        group_stats["mileage_q1"]
        - IQR_MULTIPLIER * group_stats["mileage_iqr"]
    )

    group_stats["mileage_upper_bound"] = (
        group_stats["mileage_q3"]
        + IQR_MULTIPLIER * group_stats["mileage_iqr"]
    )

    result = df.merge(
        group_stats,
        on=GROUP_COLUMNS,
        how="left",
    )

    result["eligible_for_mileage_detection"] = (
        result["group_count"] >= MIN_GROUP_SIZE
    )

    result["mileage_anomaly"] = (
        result["eligible_for_mileage_detection"]
        & (
            (result["mileage_km"] < result["mileage_lower_bound"])
            | (
                result["mileage_km"]
                > result["mileage_upper_bound"]
            )
        )
    )

    if result["mileage_iqr"].sum() == 0:
        raise ValueError(
            "All mileage comparison groups have zero IQR. "
            "Mileage-based anomaly detection is not informative "
            "for this dataset."
        )

    result["mileage_deviation_percentage"] = (
        (
            result["mileage_km"]
            - result["mileage_median"]
        )
        / result["mileage_median"]
        * 100
    )

    result["mileage_anomaly_reason"] = "within_comparable_range"

    result.loc[
        result["mileage_km"] < result["mileage_lower_bound"],
        "mileage_anomaly_reason",
    ] = "mileage_below_comparable_range"

    result.loc[
        result["mileage_km"] > result["mileage_upper_bound"],
        "mileage_anomaly_reason",
    ] = "mileage_above_comparable_range"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print(f"Reference year: {reference_year}")
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Rows: {len(result)}")
    print(
        "Eligible:",
        int(result["eligible_for_mileage_detection"].sum()),
    )
    print(
        "Mileage anomalies:",
        int(result["mileage_anomaly"].sum()),
    )


if __name__ == "__main__":
    main()