"""Macroeconomic regression workflow using FRED data.

This script downloads three monthly macroeconomic series from FRED, estimates a
baseline OLS model for industrial production, and saves the main regression
outputs and figures.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import RegressionResultsWrapper

LOGGER = logging.getLogger(__name__)

FRED_SERIES: tuple[str, ...] = ("INDPRO", "FEDFUNDS", "UNRATE")
START_DATE = "1990-01-01"
END_DATE: str | None = None
OUTPUT_DIR = Path("outputs")
FORMULA = "INDPRO ~ FEDFUNDS + UNRATE"
MIN_OBSERVATIONS = 30


class DataDownloadError(RuntimeError):
    """Raised when macroeconomic data cannot be downloaded."""


def configure_logging() -> None:
    """Configure a compact console logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def fetch_fred_data(
    series: Sequence[str] = FRED_SERIES,
    start_date: str = START_DATE,
    end_date: str | None = END_DATE,
) -> pd.DataFrame:
    """Download selected FRED series.

    Args:
        series: FRED series codes.
        start_date: First observation date.
        end_date: Last observation date. If omitted, FRED returns the latest
            available observations.

    Returns:
        Raw monthly data indexed by date.

    Raises:
        DataDownloadError: If pandas-datareader is missing, the FRED request
            fails, or FRED returns no observations.
    """
    series_codes = tuple(series)
    if not series_codes:
        raise ValueError("At least one FRED series code must be provided.")

    try:
        import pandas_datareader.data as web
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise DataDownloadError(
            "Missing dependency: pandas-datareader. Install it with "
            "'pip install pandas-datareader' before running this script."
        ) from exc

    try:
        data = web.DataReader(list(series_codes), "fred", start_date, end_date)
    except Exception as exc:  # pragma: no cover - depends on live connection
        raise DataDownloadError(
            "FRED data could not be downloaded. Check the internet connection, "
            "the FRED series codes, and the requested date range."
        ) from exc

    if data.empty:
        raise DataDownloadError("FRED returned an empty data set.")

    return data


def prepare_macro_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate the macroeconomic data set."""
    if raw_data.empty:
        raise ValueError("The input data set is empty.")

    missing_columns = sorted(set(FRED_SERIES) - set(raw_data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    data = raw_data.loc[:, list(FRED_SERIES)].copy()
    data.index = pd.to_datetime(data.index)
    data = data.apply(pd.to_numeric, errors="coerce")
    data = data.dropna().sort_index()

    if len(data) < MIN_OBSERVATIONS:
        raise ValueError(
            f"The cleaned sample has {len(data)} observations; at least "
            f"{MIN_OBSERVATIONS} are required for this regression."
        )

    return data


def estimate_baseline_model(data: pd.DataFrame) -> RegressionResultsWrapper:
    """Estimate the baseline OLS model with heteroskedasticity-robust errors."""
    return smf.ols(FORMULA, data=data).fit(cov_type="HC1")


def build_fitted_values(
    data: pd.DataFrame,
    model: RegressionResultsWrapper,
) -> pd.DataFrame:
    """Return actual values, fitted values, and residuals in one table."""
    fitted = pd.DataFrame(index=data.index)
    fitted["INDPRO_actual"] = data["INDPRO"]
    fitted["INDPRO_fitted"] = model.fittedvalues
    fitted["residual"] = model.resid
    return fitted


def save_summary_tables(
    data: pd.DataFrame,
    model: RegressionResultsWrapper,
    output_dir: Path = OUTPUT_DIR,
) -> None:
    """Save descriptive statistics, correlations, and regression results."""
    output_dir.mkdir(parents=True, exist_ok=True)

    data.describe().T.to_csv(output_dir / "descriptive_statistics.csv")
    data.corr().to_csv(output_dir / "correlation_matrix.csv")
    build_fitted_values(data, model).to_csv(output_dir / "fitted_values.csv")

    summary_path = output_dir / "baseline_regression_summary.txt"
    summary_path.write_text(model.summary().as_text(), encoding="utf-8")


def save_time_series_plot(
    data: pd.DataFrame,
    output_dir: Path = OUTPUT_DIR,
) -> None:
    """Plot the three macroeconomic variables over time."""
    output_dir.mkdir(parents=True, exist_ok=True)

    axes = data.plot(subplots=True, figsize=(10, 7), linewidth=1.2)
    axes_list = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for axis in axes_list:
        axis.grid(True, alpha=0.3)

    fig = axes_list[0].figure
    fig.tight_layout()
    fig.savefig(output_dir / "macro_series.png", dpi=300)
    plt.close(fig)


def save_actual_vs_fitted_plot(
    fitted_values: pd.DataFrame,
    output_dir: Path = OUTPUT_DIR,
) -> None:
    """Plot actual and fitted industrial production."""
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, axis = plt.subplots(figsize=(10, 5))
    axis.plot(
        fitted_values.index,
        fitted_values["INDPRO_actual"],
        label="Actual INDPRO",
        linewidth=1.3,
    )
    axis.plot(
        fitted_values.index,
        fitted_values["INDPRO_fitted"],
        label="Fitted INDPRO",
        linewidth=1.3,
    )
    axis.set_title("Industrial Production: Actual vs. Fitted")
    axis.set_xlabel("Date")
    axis.set_ylabel("Index")
    axis.grid(True, alpha=0.3)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "actual_vs_fitted.png", dpi=300)
    plt.close(fig)


def save_residual_plot(
    fitted_values: pd.DataFrame,
    output_dir: Path = OUTPUT_DIR,
) -> None:
    """Plot baseline regression residuals."""
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, axis = plt.subplots(figsize=(10, 4))
    axis.plot(fitted_values.index, fitted_values["residual"], linewidth=1.2)
    axis.axhline(0, linestyle="--", linewidth=1)
    axis.set_title("Baseline Regression Residuals")
    axis.set_xlabel("Date")
    axis.set_ylabel("Residual")
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "baseline_residuals.png", dpi=300)
    plt.close(fig)


def run_workflow(output_dir: Path = OUTPUT_DIR) -> RegressionResultsWrapper:
    """Run the complete baseline regression workflow."""
    raw_data = fetch_fred_data()
    data = prepare_macro_data(raw_data)
    model = estimate_baseline_model(data)
    fitted_values = build_fitted_values(data, model)

    save_summary_tables(data, model, output_dir)
    save_time_series_plot(data, output_dir)
    save_actual_vs_fitted_plot(fitted_values, output_dir)
    save_residual_plot(fitted_values, output_dir)

    LOGGER.info("Observations used: %s", len(data))
    LOGGER.info("Adjusted R-squared: %.4f", model.rsquared_adj)
    LOGGER.info("Outputs saved in: %s", output_dir.resolve())

    return model


def main() -> None:
    """Run the script from the command line."""
    configure_logging()
    try:
        run_workflow()
    except Exception as exc:
        LOGGER.exception("Workflow failed: %s", exc)
        raise


if __name__ == "__main__":
    main()
