from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/price_anomalies.csv")
OUTPUT_FILE = Path("reports/anomalies/threshold_comparison.csv")


def main() -> None:
    df = pd.read_csv(INPUT_FILE)

    df["absolute_deviation"] = (
        df["price_deviation_percentage"].abs()
    )

    df["flag_baseline"] = (
        df["eligible_for_detection"]
        & (
            (df["price"] < df["lower_bound"])
            | (df["price"] > df["upper_bound"])
        )
    )

    for threshold in [15, 20, 30]:
        column_name = f"flag_iqr_and_{threshold}pct"
        df[column_name] = (
            df["flag_baseline"]
            & (df["absolute_deviation"] >= threshold)
        )

    summary = []

    flag_columns = [
        "flag_baseline",
        "flag_iqr_and_15pct",
        "flag_iqr_and_20pct",
        "flag_iqr_and_30pct",
    ]

    for column in flag_columns:
        count = int(df[column].sum())
        eligible_count = int(df["eligible_for_detection"].sum())
        rate = count / eligible_count * 100 if eligible_count else 0

        summary.append(
            {
                "detector": column,
                "flagged_count": count,
                "eligible_count": eligible_count,
                "flag_rate_percent": round(rate, 2),
            }
        )

    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(OUTPUT_FILE, index=False)

    print(summary_df.to_string(index=False))
    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()