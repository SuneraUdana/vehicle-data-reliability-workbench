from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/cleaned_vehicle_prices.csv")
OUTPUT_DIR = Path("reports/eda")


def save_text_report(df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_lines: list[str] = []

    report_lines.append("VEHICLE DATA EDA REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"Rows: {len(df)}")
    report_lines.append(f"Columns: {len(df.columns)}")
    report_lines.append("")

    report_lines.append("TOP BRANDS")
    report_lines.append("-" * 70)
    report_lines.append(df["brand"].value_counts().head(20).to_string())
    report_lines.append("")

    report_lines.append("TOP MODELS")
    report_lines.append("-" * 70)
    report_lines.append(df["model"].value_counts().head(30).to_string())
    report_lines.append("")

    report_lines.append("PRICE SUMMARY")
    report_lines.append("-" * 70)
    report_lines.append(df["price"].describe().to_string())
    report_lines.append("")

    report_lines.append("MILEAGE SUMMARY")
    report_lines.append("-" * 70)
    report_lines.append(df["mileage_km"].describe().to_string())
    report_lines.append("")

    report_lines.append("YEAR SUMMARY")
    report_lines.append("-" * 70)
    report_lines.append(df["year_of_manufacture"].describe().to_string())
    report_lines.append("")

    report_lines.append("MODEL/YEAR GROUP COUNTS")
    report_lines.append("-" * 70)

    group_counts = (
        df.groupby(["brand", "model", "year_of_manufacture"])
        .size()
        .reset_index(name="listing_count")
        .sort_values("listing_count", ascending=False)
    )

    report_lines.append(group_counts.head(50).to_string(index=False))
    report_lines.append("")

    report_lines.append("POSSIBLE NUMERIC EXTREMES")
    report_lines.append("-" * 70)

    for column in ["price", "mileage_km", "engine_cc"]:
        report_lines.append(f"\nLowest {column}:")
        report_lines.append(
            df.nsmallest(10, column)[
                ["brand", "model", "year_of_manufacture", column]
            ].to_string(index=False)
        )

        report_lines.append(f"\nHighest {column}:")
        report_lines.append(
            df.nlargest(10, column)[
                ["brand", "model", "year_of_manufacture", column]
            ].to_string(index=False)
        )

    report_path = OUTPUT_DIR / "eda_summary.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    group_counts.to_csv(
        OUTPUT_DIR / "model_year_group_counts.csv",
        index=False,
    )

    print(f"Saved report: {report_path}")
    print(f"Saved group counts: {OUTPUT_DIR / 'model_year_group_counts.csv'}")


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    save_text_report(df)


if __name__ == "__main__":
    main()