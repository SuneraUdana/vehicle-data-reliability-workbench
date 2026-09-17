from pathlib import Path

import pandas as pd


ALERTS_FILE = Path("reports/anomalies/price_alerts_ranked.csv")
ALL_RECORDS_FILE = Path(
    "reports/anomalies/price_anomalies_enriched.csv"
)
OUTPUT_FILE = Path(
    "reports/anomalies/stratified_validation_sample.csv"
)
RANDOM_STATE = 20260917
REVIEW_COLUMNS = [
    "review_label",
    "review_reason",
    "review_confidence",
    "review_notes",
]


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
    for path in (ALERTS_FILE, ALL_RECORDS_FILE):
        if not path.exists():
            raise FileNotFoundError(f"Missing input file: {path}")

    alerts = pd.read_csv(ALERTS_FILE)
    all_records = pd.read_csv(ALL_RECORDS_FILE)
    if "listing_id" not in all_records:
        raise ValueError("Full records file must contain listing_id")

    flagged = alerts.copy()
    if len(flagged) < 100:
        raise ValueError("At least 100 ranked alerts are required")

    top = flagged.nsmallest(50, "alert_rank").copy()
    middle = flagged[
        flagged["alert_rank"].between(337, 361)
    ].copy()
    lower = flagged.nlargest(25, "alert_rank").copy()
    if len(middle) != 25:
        raise ValueError("Expected 25 middle-ranked alerts")

    flagged_parts = [
        top.assign(sample_stratum="flagged_top_50"),
        middle.assign(sample_stratum="flagged_middle_25"),
        lower.assign(sample_stratum="flagged_lower_25"),
    ]

    flagged_ids = set(flagged["listing_id"])
    unflagged = all_records[
        ~all_records["listing_id"].isin(flagged_ids)
    ].copy()
    high_quality = unflagged[
        unflagged["price_reference_quality"] == "high"
    ].sample(n=50, random_state=RANDOM_STATE)
    medium_quality = unflagged[
        unflagged["price_reference_quality"] == "medium"
    ].drop(index=high_quality.index, errors="ignore").sample(
        n=25,
        random_state=RANDOM_STATE,
    )
    random_pool = unflagged.drop(
        index=high_quality.index.union(medium_quality.index),
        errors="ignore",
    ).sample(n=25, random_state=RANDOM_STATE)
    unflagged_parts = [
        high_quality.assign(sample_stratum="unflagged_high_quality_50"),
        medium_quality.assign(sample_stratum="unflagged_medium_quality_25"),
        random_pool.assign(sample_stratum="unflagged_random_25"),
    ]

    sample = pd.concat(flagged_parts + unflagged_parts, ignore_index=True)
    if sample["listing_id"].duplicated().any():
        raise ValueError("Sample contains duplicate listing_id values")

    for column in REVIEW_COLUMNS:
        sample[column] = ""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Rows: {len(sample)}")
    print(sample["sample_stratum"].value_counts().to_string())


if __name__ == "__main__":
    main()
