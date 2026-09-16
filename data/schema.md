# Dataset schema

## Source file

- Filename: `car_price_dataset.csv`
- Rows: 9,788
- Columns: 17
- Price currency: To be confirmed
- Dataset type: Used-vehicle listing data

## Columns

| Original column | Standard column | Meaning | Expected type | Initial action |
|---|---|---|---|---|
| `Unnamed: 0` | — | Exported row index | Identifier | Remove after checking uniqueness |
| `Brand` | `brand` | Vehicle manufacturer | Category | Normalize text |
| `Model` | `model` | Vehicle model | Category | Normalize text |
| `YOM` | `year_of_manufacture` | Manufacturing year | Integer | Validate plausible range |
| `Engine (cc)` | `engine_cc` | Engine capacity | Numeric | Convert and validate |
| `Gear` | `transmission` | Gear/transmission type | Category | Normalize text |
| `Fuel Type` | `fuel_type` | Fuel type | Category | Normalize text |
| `Millage(KM)` | `mileage_km` | Reported mileage | Numeric | Convert and validate |
| `Town` | `town` | Listing location | Category | Normalize text |
| `Date` | `listing_date` | Advertisement date | Date | Parse date |
| `Leasing` | `leasing` | Leasing availability | Category | Normalize text |
| `Condition` | `condition` | Vehicle condition | Category | Normalize text |
| `AIR CONDITION` | `air_conditioning` | Air-conditioning feature | Category | Normalize text |
| `POWER STEERING` | `power_steering` | Power steering feature | Category | Normalize text |
| `POWER MIRROR` | `power_mirror` | Power mirror feature | Category | Normalize text |
| `POWER WINDOW` | `power_window` | Power window feature | Category | Normalize text |
| `Price` | `price_lkr` | Asking price | Numeric | Convert and validate |