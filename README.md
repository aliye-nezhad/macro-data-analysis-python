# Macroeconomic Regression Workflow Using Python

## Overview

This project implements a reproducible empirical workflow for analyzing macroeconomic data using Python. The workflow retrieves data from the Federal Reserve Economic Data (FRED) database, performs data cleaning and validation, estimates regression models, conducts diagnostic tests, and generates research outputs.

## Research Question

How are monetary policy conditions and real economic activity associated with fluctuations in macroeconomic performance?

The analysis examines whether changes in monetary conditions and labor market dynamics are systematically associated with industrial production movements using a reproducible empirical framework.

## Motivation

Understanding the relationship between monetary conditions, labor markets, and real activity is central to empirical macroeconomics.

This project implements a transparent workflow for macroeconomic data retrieval, preparation, estimation, and diagnostics using publicly available Federal Reserve data.

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
- Regression specification diagnostics
- Heteroskedasticity diagnostics
- Serial correlation diagnostics
- Multicollinearity diagnostics
- Hypothesis testing
- Robustness comparisons

## Outputs

The workflow generates:

- Cleaned macroeconomic datasets
- Summary statistics and correlation analysis
- Regression estimates with heteroskedasticity-robust inference
- Model diagnostic tests
- Residual analysis and specification checks
- Research-quality figures

## Repository Structure

The repository is organized as follows:

```text
macro-data-analysis-python/

├── README.md
├── requirements.txt

├── code/
│   ├── macro_regression_workflow.py
│   └── diagnostic_workflow.py

├── data/
│   └── README.md

├── outputs/
│   ├── figures/
│   └── tables/

```

## Computational Environment

- Python
- pandas for data manipulation and transformation
- pandas-datareader for automated FRED data retrieval
- statsmodels for econometric estimation and inference
- Matplotlib for research visualization

## Reproducibility

Run the workflow scripts sequentially to reproduce the generated tables, figures, and regression outputs.

```bash
python code/macro_regression_workflow.py
python code/diagnostic_workflow.py
```

## Research Skills Demonstrated

This repository demonstrates:

- Automated macroeconomic data acquisition
- Data cleaning and transformation
- Econometric estimation
- Robust inference
- Model diagnostics
- Reproducible research workflows
