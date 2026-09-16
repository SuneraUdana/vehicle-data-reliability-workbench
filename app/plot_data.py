from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


INPUT_FILE = Path("data/processed/cleaned_vehicle_prices.csv")
OUTPUT_DIR = Path("reports/eda/plots")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 6))
    sns.histplot(df["price"], bins=50)
    plt.title("Vehicle Price Distribution")
    plt.xlabel("Price")
    plt.ylabel("Listings")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "price_distribution.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.histplot(df["mileage_km"], bins=50)
    plt.title("Vehicle Mileage Distribution")
    plt.xlabel("Mileage (km)")
    plt.ylabel("Listings")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "mileage_distribution.png", dpi=150)
    plt.close()

    top_brands = df["brand"].value_counts().head(15)

    plt.figure(figsize=(10, 6))
    top_brands.sort_values().plot(kind="barh")
    plt.title("Top Vehicle Brands")
    plt.xlabel("Number of Listings")
    plt.ylabel("Brand")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "top_brands.png", dpi=150)
    plt.close()

    top_models = df["model"].value_counts().head(15)

    plt.figure(figsize=(10, 6))
    top_models.sort_values().plot(kind="barh")
    plt.title("Top Vehicle Models")
    plt.xlabel("Number of Listings")
    plt.ylabel("Model")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "top_models.png", dpi=150)
    plt.close()

    print(f"Charts saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()