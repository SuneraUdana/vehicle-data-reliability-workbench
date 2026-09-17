from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/mileage_anomalies.csv")
OUTPUT_FILE = Path(
    "reports/anomalies/age_mileage_anomalies.csv"
)

LOW_ANNUAL_MILEAGE = 2_000
HIGH_ANNUAL_MILEAGE = 80_000


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    df["annual_mileage_anomaly"] = (
        (df["annual_mileage"] < LOW_ANNUAL_MILEAGE)
        | (df["annual_mileage"] > HIGH_ANNUAL_MILEAGE)
    )

    df["annual_mileage_reason"] = "within_age_based_range"

    df.loc[
        df["annual_mileage"] < LOW_ANNUAL_MILEAGE,
        "annual_mileage_reason",
    ] = "very_low_annual_mileage"

    df.loc[
        df["annual_mileage"] > HIGH_ANNUAL_MILEAGE,
        "annual_mileage_reason",
    ] = "very_high_annual_mileage"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(
        df["annual_mileage_anomaly"].value_counts()
    )
    print(
        df["annual_mileage_reason"].value_counts()
    )


if __name__ == "__main__":
    main()