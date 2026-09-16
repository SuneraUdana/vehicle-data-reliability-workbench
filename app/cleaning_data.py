from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/raw/car_price_dataset.csv")
OUTPUT_FILE = Path("data/processed/cleaned_vehicle_prices.csv")


COLUMN_RENAME_MAP = {
    "Brand": "brand",
    "Model": "model",
    "YOM": "year_of_manufacture",
    "Engine (cc)": "engine_cc",
    "Gear": "transmission",
    "Fuel Type": "fuel_type",
    "Millage(KM)": "mileage_km",
    "Town": "town",
    "Date": "listing_date",
    "Leasing": "leasing",
    "Condition": "condition",
    "AIR CONDITION": "air_conditioning",
    "POWER STEERING": "power_steering",
    "POWER MIRROR": "power_mirror",
    "POWER WINDOW": "power_window",
    "Price": "price",
}


NUMERIC_COLUMNS = [
    "year_of_manufacture",
    "engine_cc",
    "mileage_km",
    "price",
]


TEXT_COLUMNS = [
    "brand",
    "model",
    "transmission",
    "fuel_type",
    "town",
    "leasing",
    "condition",
    "air_conditioning",
    "power_steering",
    "power_mirror",
    "power_window",
]


def clean_text(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    cleaned = " ".join(str(value).strip().split())
    return cleaned.upper() if cleaned else pd.NA


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    df = df.rename(columns=COLUMN_RENAME_MAP)

    missing_expected_columns = set(COLUMN_RENAME_MAP.values()) - set(df.columns)

    if missing_expected_columns:
        raise ValueError(
            f"Missing expected columns: {sorted(missing_expected_columns)}"
        )

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["listing_date"] = pd.to_datetime(
        df["listing_date"],
        errors="coerce",
    )

    for column in TEXT_COLUMNS:
        df[column] = df[column].map(clean_text)

    df = df.drop_duplicates().reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved cleaned dataset to: {OUTPUT_FILE}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print("\nMissing values:")
    print(df.isna().sum().sort_values(ascending=False))


if __name__ == "__main__":
    main()