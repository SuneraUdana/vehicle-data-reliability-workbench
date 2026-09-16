from pathlib import Path
import pandas as pd


INPUT_FILE = Path("data/raw/car_price_dataset.csv")
REPORT_FILE = Path("reports/data_quality_report.txt")


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    report_lines: list[str] = []

    report_lines.append("DATA QUALITY REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"File: {INPUT_FILE}")
    report_lines.append(f"Rows: {df.shape[0]}")
    report_lines.append(f"Columns: {df.shape[1]}")
    report_lines.append("")

    report_lines.append("COLUMN INFORMATION")
    report_lines.append("-" * 60)

    for column in df.columns:
        missing_count = int(df[column].isna().sum())
        missing_percentage = missing_count / len(df) * 100
        unique_count = int(df[column].nunique(dropna=True))

        report_lines.append(
            f"{column} | "
            f"type={df[column].dtype} | "
            f"missing={missing_count} "
            f"({missing_percentage:.2f}%) | "
            f"unique={unique_count}"
        )

    report_lines.append("")
    report_lines.append("DUPLICATES")
    report_lines.append("-" * 60)
    report_lines.append(f"Duplicate rows: {df.duplicated().sum()}")

    report_lines.append("")
    report_lines.append("NUMERIC SUMMARY")
    report_lines.append("-" * 60)
    report_lines.append(
        df.describe(include="number").transpose().to_string()
    )

    report_lines.append("")
    report_lines.append("CATEGORICAL VALUE SAMPLES")
    report_lines.append("-" * 60)

    for column in df.select_dtypes(exclude="number").columns:
        values = df[column].dropna().astype(str).value_counts().head(10)
        report_lines.append(f"\n{column}:")
        report_lines.append(values.to_string())

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Report written to: {REPORT_FILE}")
    print(f"Rows analysed: {len(df)}")
    print(f"Columns analysed: {len(df.columns)}")


if __name__ == "__main__":
    main()