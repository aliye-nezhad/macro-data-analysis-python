# Macroeconomic Regression Workflow Using Python

## Overview

This repository implements a reproducible Python workflow for retrieving, preparing, analyzing, and documenting monthly US macroeconomic data from the Federal Reserve Economic Data (FRED) database.

The project is presented as a Python econometrics and reproducible research coding sample. It demonstrates a complete empirical workflow, including automated data acquisition, data validation, regression estimation, diagnostic testing, and structured output generation.

The regression estimates describe conditional associations and should not be interpreted as causal effects.

## Research Question

How are short-term monetary policy conditions and labor-market slack associated with movements in US industrial production?

## Data

The workflow retrieves three monthly macroeconomic series directly from FRED:

| Variable | Description | Role |
|---|---|---|
| `INDPRO` | Industrial Production: Total Index | Dependent variable |
| `FEDFUNDS` | Effective Federal Funds Rate | Monetary policy indicator |
| `UNRATE` | Civilian Unemployment Rate | Labor-market indicator |

The sample begins on 1990-01-01 and ends at the latest available observation when the workflow is executed.

Raw data are not committed to the repository because they are retrieved programmatically from FRED. See [`data/README.md`](data/README.md) for series definitions, data processing steps, and reproducibility notes.

## Baseline Specification

The descriptive baseline regression model is:

```text
INDPRO ~ FEDFUNDS + UNRATE
