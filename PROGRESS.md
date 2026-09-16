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