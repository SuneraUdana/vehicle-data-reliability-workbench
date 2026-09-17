from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DATA_FILE = Path("data/processed/cleaned_vehicle_prices.csv")
GROUP_COLUMNS = ["brand", "model", "year_of_manufacture"]
MIN_GROUP_SIZE = 5
IQR_MULTIPLIER = 1.5


class ListingRequest(BaseModel):
    brand: str = Field(min_length=1)
    model: str = Field(min_length=1)
    year_of_manufacture: int = Field(ge=1950, le=2100)
    price: float = Field(gt=0)
    mileage_km: float | None = Field(default=None, ge=0)


class PlausibilityResponse(BaseModel):
    status: str
    explanation: str
    group_count: int
    group_median: float | None
    expected_price_low: float | None
    expected_price_high: float | None
    price_deviation_percentage: float | None
    price_anomaly: bool | None


def load_reference_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Reference dataset not found: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)
    missing = set(GROUP_COLUMNS + ["price"]) - set(df.columns)
    if missing:
        raise ValueError(f"Reference dataset is missing columns: {sorted(missing)}")
    return df


REFERENCE_DATA = load_reference_data()


def assess_listing(listing: ListingRequest) -> PlausibilityResponse:
    normalized_brand = listing.brand.strip().upper()
    normalized_model = listing.model.strip().upper()
    matches = REFERENCE_DATA[
        (REFERENCE_DATA["brand"] == normalized_brand)
        & (REFERENCE_DATA["model"] == normalized_model)
        & (
            REFERENCE_DATA["year_of_manufacture"]
            == listing.year_of_manufacture
        )
    ]["price"]

    group_count = int(matches.count())
    if group_count < MIN_GROUP_SIZE:
        return PlausibilityResponse(
            status="insufficient_evidence",
            explanation=(
                "Fewer than five comparable listings are available for "
                "this brand, model, and manufacturing year."
            ),
            group_count=group_count,
            group_median=None,
            expected_price_low=None,
            expected_price_high=None,
            price_deviation_percentage=None,
            price_anomaly=None,
        )

    median = float(matches.median())
    q1 = float(matches.quantile(0.25))
    q3 = float(matches.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - IQR_MULTIPLIER * iqr
    upper = q3 + IQR_MULTIPLIER * iqr
    deviation = (listing.price - median) / median * 100
    anomaly = listing.price < lower or listing.price > upper

    if anomaly:
        direction = "below" if listing.price < lower else "above"
        explanation = (
            f"Price is {abs(deviation):.1f}% {direction} the comparable-group "
            f"median and outside the IQR-based expected range."
        )
        status = "potential_anomaly"
    else:
        explanation = (
            "Price is within the IQR-based expected range for comparable "
            "listings."
        )
        status = "appears_plausible"

    return PlausibilityResponse(
        status=status,
        explanation=explanation,
        group_count=group_count,
        group_median=round(median, 4),
        expected_price_low=round(lower, 4),
        expected_price_high=round(upper, 4),
        price_deviation_percentage=round(deviation, 4),
        price_anomaly=bool(anomaly),
    )


app = FastAPI(
    title="Vehicle Data Plausibility API",
    version="0.1.0",
    description="Rule-based vehicle listing price plausibility checks.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/plausibility", response_model=PlausibilityResponse)
def plausibility(listing: ListingRequest) -> PlausibilityResponse:
    try:
        return assess_listing(listing)
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
