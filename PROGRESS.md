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