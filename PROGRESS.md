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