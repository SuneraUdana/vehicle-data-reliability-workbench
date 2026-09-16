from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/cleaned_vehicle_prices.csv")
REPORT_FILE = Path("reports/validation_report.txt")


def add_check(
    checks: list[str],
    name: str,
    passed: bool,
    detail: str,
) -> None:
    status = "PASS" if passed else "REVIEW"
    checks.append(f"[{status}] {name}: {detail}")


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    checks: list[str] = []

    add_check(
        checks,
        "No duplicate rows",
        not df.duplicated().any(),
        f"{df.duplicated().sum()} duplicate rows",
    )

    add_check(
        checks,
        "Positive prices",
        (df["price"] > 0).all(),
        f"{(df['price'] <= 0).sum()} rows have zero or negative price",
    )

    add_check(
        checks,
        "Non-negative mileage",
        (df["mileage_km"] >= 0).all(),
        f"{(df['mileage_km'] < 0).sum()} rows have negative mileage",
    )

    year_check = df["year_of_manufacture"].between(1950, 2026).all()
    add_check(
        checks,
        "Plausible manufacturing years",
        year_check,
        (
            f"minimum={df['year_of_manufacture'].min()}, "
            f"maximum={df['year_of_manufacture'].max()}"
        ),
    )

    engine_check = df["engine_cc"].between(400, 10_000).all()
    add_check(
        checks,
        "Plausible engine sizes",
        engine_check,
        (
            f"minimum={df['engine_cc'].min()}, "
            f"maximum={df['engine_cc'].max()}"
        ),
    )

    mileage_check = df["mileage_km"].between(0, 1_000_000).all()
    add_check(
        checks,
        "Plausible mileage",
        mileage_check,
        (
            f"minimum={df['mileage_km'].min()}, "
            f"maximum={df['mileage_km'].max()}"
        ),
    )

    price_quantiles = df["price"].quantile([0.01, 0.5, 0.99])

    checks.append("")
    checks.append("PRICE DISTRIBUTION")
    checks.append(f"1st percentile: {price_quantiles.loc[0.01]:,.2f}")
    checks.append(f"Median: {price_quantiles.loc[0.50]:,.2f}")
    checks.append(f"99th percentile: {price_quantiles.loc[0.99]:,.2f}")

    checks.append("")
    checks.append("TOP BRANDS")
    checks.append(df["brand"].value_counts().head(15).to_string())

    checks.append("")
    checks.append("TOP MODELS")
    checks.append(df["model"].value_counts().head(15).to_string())

    checks.append("")
    checks.append("CATEGORY VALUES")

    for column in [
        "transmission",
        "fuel_type",
        "condition",
        "leasing",
        "air_conditioning",
        "power_steering",
        "power_mirror",
        "power_window",
    ]:
        checks.append(f"\n{column}:")
        checks.append(df[column].value_counts(dropna=False).head(15).to_string())

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(checks), encoding="utf-8")

    print(f"Validation report saved to: {REPORT_FILE}")
    print("\n".join(checks))


if __name__ == "__main__":
    main()