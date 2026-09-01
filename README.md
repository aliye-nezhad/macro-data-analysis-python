# Macroeconomic Regression Workflow Using Python

## Overview

This project implements a reproducible empirical workflow for analyzing macroeconomic data using Python. The workflow retrieves data from the Federal Reserve Economic Data (FRED) database, performs data cleaning and validation, estimates regression models, conducts diagnostic tests, and generates research outputs.

## Research Question

How do macroeconomic conditions, represented by industrial production, monetary policy, and labor market conditions, relate within a regression framework?

## Data

The workflow uses monthly macroeconomic series from FRED:

- Industrial Production (INDPRO)
- Federal Funds Rate (FEDFUNDS)
- Unemployment Rate (UNRATE)

## Methodology

The workflow includes:

- Data retrieval and preparation using pandas
- Ordinary Least Squares (OLS) regression estimation
- Heteroskedasticity-robust standard errors (HC1)
- Residual analysis
- Model specification tests
- Heteroskedasticity testing
- Autocorrelation testing
- Multicollinearity diagnostics
- Hypothesis testing
- Robustness comparisons

## Outputs

The workflow generates:

- Regression summaries
- Descriptive statistics
- Correlation matrices
- Fitted values
- Diagnostic test results
- Regression figures
- Residual analysis plots

## Repository Structure

The repository will be organized as follows:

```text
macro-data-analysis-python/

├── code/
│   ├── macro_regression_workflow.py
│   └── diagnostic_workflow.py
│
├── outputs/
│   ├── tables/
│   └── figures/
│
├── README.md
└── requirements.txt
```

## Tools

- Python
- pandas
- statsmodels
- Matplotlib
- pandas-datareader

## Reproducibility

Run the baseline workflow first, followed by the diagnostic workflow, to reproduce the generated tables, figures, and regression outputs.
