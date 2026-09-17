from pathlib import Path

import pandas as pd


INPUT_FILE = Path("reports/anomalies/analyst_review.csv")
OUTPUT_FILE = Path(
    "reports/anomalies/analyst_review_evaluation.txt"
)
POSITIVE_LABELS = {
    "confirmed_anomaly",
    "probably_anomaly",
    "data_error",
}


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    evaluable = df[df["review_label"] != "insufficient_evidence"].copy()
    useful = evaluable["review_label"].isin(POSITIVE_LABELS)
    precision = useful.mean() if len(evaluable) else None

    lines = [
        "ANALYST REVIEW EVALUATION",
        "=" * 60,
        "Scope: precision among top-100 ranked alerts",
        f"Reviewed rows: {len(df)}",
        f"Excluded insufficient-evidence rows: {len(df) - len(evaluable)}",
        f"Useful reviewed alerts: {int(useful.sum())}",
        f"Appears-normal alerts: {int((~useful).sum())}",
        f"Precision among evaluable alerts: "
        f"{precision:.3f}" if precision is not None else
        "Precision among evaluable alerts: Undefined",
        "",
        "Recall is not estimated because this file contains no unflagged listings.",
    ]
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
