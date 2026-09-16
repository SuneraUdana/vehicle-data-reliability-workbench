from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/price_anomalies.csv")
OUTPUT_FILE = Path(
    "reports/anomalies/threshold_review_sample.csv"
)

SAMPLE_SIZE = 30
RANDOM_STATE = 20260917
FLAG_COLUMNS = [
    "flag_iqr_and_15pct",
    "flag_iqr_and_20pct",
    "flag_iqr_and_30pct",
]
BASE_COLUMNS = [
    "eligible_for_detection",
    "price",
    "lower_bound",
    "upper_bound",
    "price_deviation_percentage",
]
REVIEW_COLUMNS = [
    "review_label",
    "review_reason",
    "review_confidence",
    "review_notes",
]


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
    required_columns = set(BASE_COLUMNS)
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    eligible = df.loc[parse_bool(df["eligible_for_detection"])].copy()
    eligible["flag_baseline"] = (
        (eligible["price"] < eligible["lower_bound"])
        | (eligible["price"] > eligible["upper_bound"])
    )
    absolute_deviation = eligible["price_deviation_percentage"].abs()
    flags = {
        column: eligible["flag_baseline"]
        & (absolute_deviation >= threshold)
        for column, threshold in zip(FLAG_COLUMNS, [15, 20, 30])
    }
    for column, values in flags.items():
        eligible[column] = values

    selected_parts = []
    selected_indices: set[int] = set()

    for column in FLAG_COLUMNS:
        candidate_indices = eligible.index[flags[column]]
        sample_indices = eligible.loc[candidate_indices].sample(
            n=min(SAMPLE_SIZE, len(candidate_indices)),
            random_state=RANDOM_STATE,
        ).index
        selected_parts.append(eligible.loc[sample_indices])
        selected_indices.update(sample_indices)

    no_stricter_flag = ~pd.concat(flags, axis=1).any(axis=1)
    remaining_indices = eligible.index[
        no_stricter_flag & ~eligible.index.isin(selected_indices)
    ]
    sample_indices = eligible.loc[remaining_indices].sample(
        n=min(SAMPLE_SIZE, len(remaining_indices)),
        random_state=RANDOM_STATE,
    ).index
    selected_parts.append(eligible.loc[sample_indices])
    selected_indices.update(sample_indices)

    sample = pd.concat(selected_parts)
    sample = sample.loc[~sample.index.duplicated(keep="first")].copy()
    sample.insert(0, "original_row_index", sample.index)
    sample = sample.reset_index(drop=True)
    sample["absolute_deviation"] = (
        sample["price_deviation_percentage"].abs()
    )

    for column in REVIEW_COLUMNS:
        sample[column] = ""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Eligible source rows: {len(eligible)}")
    print(f"Rows after deduplication: {len(sample)}")
    for column in FLAG_COLUMNS:
        print(f"{column}: {int(parse_bool(sample[column]).sum())}")
    print(
        "not_flagged_by_stricter_rules:",
        int((~pd.concat(
            {column: parse_bool(sample[column]) for column in FLAG_COLUMNS},
            axis=1,
        ).any(axis=1)).sum()),
    )


if __name__ == "__main__":
    main()
