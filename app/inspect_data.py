from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")


def find_dataset() -> Path:
    print(f"Looking for datasets in: {RAW_DIR.resolve()}")

    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {RAW_DIR.resolve()}"
        )

    all_files = list(RAW_DIR.iterdir())

    print("Files found:")
    for file_path in all_files:
        print(f"- {file_path.name}")

    supported_files = [
        file_path
        for file_path in all_files
        if file_path.suffix.lower() in {".csv", ".xlsx", ".xls"}
    ]

    if not supported_files:
        raise FileNotFoundError(
            "No CSV or Excel dataset found in data/raw/"
        )

    return supported_files[0]


def load_dataset(file_path: Path) -> pd.DataFrame:
    print(f"Loading: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path)

    if suffix == ".xlsx":
        return pd.read_excel(file_path)

    if suffix == ".xls":
        return pd.read_excel(file_path, engine="xlrd")

    raise ValueError(f"Unsupported file type: {suffix}")


def main() -> None:
    print("Starting data inspection...")

    file_path = find_dataset()
    df = load_dataset(file_path)

    print(f"\nFile: {file_path}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names:")
    print(list(df.columns))

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isna().sum().sort_values(ascending=False))

    print(f"\nDuplicate rows: {df.duplicated().sum()}")

    print("\nFirst five rows:")
    print(df.head().to_string())

    print("\nNumeric summary:")
    print(df.describe(include="all").transpose())


if __name__ == "__main__":
    main()
