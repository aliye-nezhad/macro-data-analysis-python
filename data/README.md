# Data Documentation

## Source

The project retrieves data programmatically from the Federal Reserve Economic
Data (FRED) database using `pandas-datareader`. Raw data are not stored in this
repository because the scripts download the required public series directly.

| Series | Description | Frequency and units | FRED page |
| --- | --- | --- | --- |
| `INDPRO` | Industrial Production: Total Index | Monthly; index, 2017 = 100; seasonally adjusted | https://fred.stlouisfed.org/series/INDPRO |
| `FEDFUNDS` | Effective Federal Funds Rate | Monthly; percent; not seasonally adjusted | https://fred.stlouisfed.org/series/FEDFUNDS |
| `UNRATE` | Civilian Unemployment Rate | Monthly; percent; seasonally adjusted | https://fred.stlouisfed.org/series/UNRATE |

## Sample

- Start date: `1990-01-01`
- End date: latest observation available when the scripts are run
- Observation frequency: monthly

The code requires at least 30 complete observations after cleaning.

## Processing

`prepare_macro_data()` performs the following steps:

1. verifies that the downloaded data are not empty;
2. verifies that all three required series are present;
3. converts the index to dates;
4. converts all series to numeric values;
5. removes observations with missing values across the three series; and
6. sorts observations chronologically.

The cleaned analysis sample is represented in
`outputs/fitted_values.csv`, together with fitted industrial production and
baseline residuals. Summary statistics and correlations are stored in
`outputs/descriptive_statistics.csv` and `outputs/correlation_matrix.csv`.

## Reproducibility Note

FRED data can be revised and the scripts request the latest available
observations by default. Therefore, a future run may not reproduce every saved
number exactly. To freeze a replication window, replace `END_DATE = None` in
`code/macro_regression_workflow.py` with a specific date and regenerate all
outputs.

## Data License and Attribution

Users should consult the source pages above for current series notes, release
details, and applicable terms. This repository does not redistribute a separate
raw-data copy.
