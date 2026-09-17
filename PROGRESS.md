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

## Milestone 6: stratified validation sample

The next validation sample combines flagged and unflagged listings so that
precision and recall can be estimated together. It includes 50 top-ranked,
25 middle-ranked, and 25 lower-ranked alerts, plus 50 unflagged listings from
high-quality reference groups, 25 from medium-quality groups, and 25 random
unflagged records. Manual review labels are required before calculating
validation metrics.

## Script consolidation

The active workflow is now limited to data preparation, price-alert
detection/enrichment/ranking, analyst-review validation/evaluation, and the
stratified validation sampler. One-time threshold and representative-sample
tools are archived under `app/archive/`. Mileage and age-mileage tools are
archived under `app/archive/blocked_mileage/` because the source data has
constant annual mileage and zero mileage-group IQR. They are retained for
provenance but are not active production steps.

Current milestone findings:

- 9,770 cleaned records processed.
- 697 eligible price alerts: 350 below and 347 above the expected range.
- Every alert has at least five comparable records; median reference-group
  size is 17.
- Top-100 analyst review: 79 useful alerts out of 83 evaluable alerts
  (95.2% precision among top-ranked alerts).
- Recall remains unmeasured for the top-100 alert-only review.
- The 200-row stratified validation sample contains 100 flagged and 100
  unflagged listings and requires manual labels before evaluation.

## Stage 4: plausibility API

Added `app/api.py` with:

- `GET /health` for service readiness.
- `POST /v1/plausibility` accepting brand, model, year, price, and optional
  mileage.
- IQR-based comparable-price status: `appears_plausible`,
  `potential_anomaly`, or `insufficient_evidence`.
- Auditable group count, expected range, deviation, and explanation fields.

The API is a rule-based plausibility service; it does not make fraud claims.