from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/price_alerts_ranked.csv")
OUTPUT_FILE = Path("reports/anomalies/analyst_review.csv")

TOP_N = 100


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    top = df.head(TOP_N).copy()

    top["review_label"] = ""
    top["review_reason"] = ""
    top["review_confidence"] = ""
    top["review_notes"] = ""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    top.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Rows for analyst review: {len(top)}")


if __name__ == "__main__":
    main()

    