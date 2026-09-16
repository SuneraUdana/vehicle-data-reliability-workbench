from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/price_anomalies.csv")
OUTPUT_FILE = Path(
    "reports/anomalies/representative_review_sample.csv"
)


def main() -> None:
    df = pd.read_csv(INPUT_FILE)

    eligible = df[df["eligible_for_detection"]].copy()

    sample = eligible.sample(
        n=min(100, len(eligible)),
        random_state=20260917,
    ).reset_index(drop=True)

    sample["flag_baseline"] = sample["price_anomaly"]

    sample["absolute_deviation"] = (
        sample["price_deviation_percentage"].abs()
    )

    for threshold in [15, 20, 30]:
        sample[f"flag_iqr_and_{threshold}pct"] = (
            sample["price_anomaly"]
            & (sample["absolute_deviation"] >= threshold)
        )

    sample["review_label"] = ""
    sample["review_reason"] = ""
    sample["review_confidence"] = ""
    sample["review_notes"] = ""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Rows: {len(sample)}")
    print("Eligible source rows:", len(eligible))


if __name__ == "__main__":
    main()