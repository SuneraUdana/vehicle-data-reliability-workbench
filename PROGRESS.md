## Dataset cleaning milestone

- Loaded the original vehicle dataset.
- Removed the exported `Unnamed: 0` index column.
- Standardized 16 column names.
- Converted numeric fields.
- Parsed listing dates.
- Normalized text fields.
- Removed 18 exact duplicate rows.
- Produced `data/processed/cleaned_vehicle_prices.csv`.
- Missing values after cleaning: 0.
- Next step: validate realistic ranges and identify suspicious observations.

### Representative sample evaluation

- Evaluated rows: 94
- Excluded insufficient-evidence rows: 6
- Broad positive labels: probably_anomaly, confirmed_anomaly, data_error
- Broad positives: 10

| Detector | Precision | Recall | F1 |
|---|---:|---:|---:|
| Baseline IQR | 0.444 | 0.400 | 0.421 |
| IQR + 15% | 1.000 | 0.100 | 0.182 |
| IQR + 20% | Undefined | 0.000 | Undefined |
| IQR + 30% | Undefined | 0.000 | Undefined |

These results are exploratory because the stricter thresholds generated very few
predictions in the random sample. A targeted threshold-review sample is required
before selecting the final operating threshold.

## Milestone 3 conclusion

The first price anomaly detector has been evaluated using:
- An initial balanced review sample.
- A representative random sample.
- A targeted threshold sample.

The chosen operating rule is:

- Rule: IQR + 15% absolute price-deviation threshold (provisional).
- Expected eligible alerts: 118 of 5,613 eligible listings (2.10%).
- Precision: 1.000 in the targeted sample.
- Recall: 0.989 in the targeted sample.
- F1: 0.994 in the targeted sample.
- Reason for selection: it substantially reduces the baseline review workload
  while retaining the strongest recall/F1 trade-off in the targeted sample.
- Known limitations: the targeted sample is intentionally enriched for flagged
  rows, its labels are manual review candidates rather than proof of fraud, and
  the representative random sample produced weaker baseline/15% estimates.
  The rule remains provisional until a larger independent review is completed.

The system is an investigation-support tool. It does not prove fraud.

## Milestone 4 — Mileage and vehicle-age signals

Status: In progress

### New signals

- Vehicle age based on listing year and manufacturing year.
- Annual mileage.
- Comparable mileage IQR signal.
- Age-based annual-mileage screening.
- Combined review priority.

### Outputs

- [ ] `reports/anomalies/mileage_anomalies.csv`
- [ ] `reports/anomalies/age_mileage_anomalies.csv`
- [ ] `reports/anomalies/review_priority.csv`

### Limitations

- Annual mileage thresholds are initial screening assumptions.
- Mileage anomalies are not proof of odometer tampering.
- Price and mileage signals require manual review.
- Vehicle variants and condition may not be fully represented.

## Milestone 4 — Mileage and vehicle-age signals

Status: Blocked for mileage-based detection

### Finding

The dataset contains 9,770 rows, but `annual_mileage` has only one unique value:

- Annual mileage: 11,000 km/year for every row.
- Minimum: 11,000 km/year.
- Median: 11,000 km/year.
- Maximum: 11,000 km/year.
- Standard deviation: 0.

Mileage is mechanically determined by vehicle age:

- `mileage_km = vehicle_age × 11,000`.

The comparable-group mileage detector also produced zero anomalies because every group has zero mileage IQR.

### Consequence

Mileage and annual-mileage signals cannot distinguish records in the current dataset. The current review priority is therefore still price-only:

- Low: 9,073.
- Medium: 697.
- High: 0.

### Decision

Do not tune mileage thresholds using this dataset. Keep the mileage logic in the project as a documented data-quality check, but do not use it as an active anomaly signal until the dataset contains independent mileage variation.

## Milestone 5 — Price alert explanations and review outputs

Status: In progress

### New outputs

- `reports/anomalies/price_anomalies_enriched.csv`
  Adds expected price range (Q1–Q3) and deviation percentage per listing.
- `reports/anomalies/price_alerts_ranked.csv`
  Ranks the 697 price alerts by absolute deviation from the group median.
- `reports/anomalies/analyst_review.csv`
  Top 100 highest-deviation alerts, formatted for manual labeling.

### Notes

- Mileage signal remains excluded pending better data (see Milestone 4 finding).
- Ranking uses `price_deviation_abs`, computed against brand+model+year median.
- This does not prove fraud; it prioritizes review effort.