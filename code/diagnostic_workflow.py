"""Diagnostic and robustness checks for the macro regression workflow.

This script reuses the cleaned FRED data and baseline model from
macro_regression_workflow.py, then runs residual diagnostics, specification
checks, and a small standard-error sensitivity comparison.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.stats.diagnostic import acorr_ljungbox, het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.ar_model import AutoReg, AutoRegResultsWrapper

from macro_regression_workflow import (
    FORMULA,
    OUTPUT_DIR,
    estimate_baseline_model,
    fetch_fred_data,
    prepare_macro_data,
)

LOGGER = logging.getLogger(__name__)
DIAGNOSTIC_DIR = OUTPUT_DIR / "diagnostics"
REGRESSOR_COLUMNS: tuple[str, ...] = ("FEDFUNDS", "UNRATE")
LJUNG_BOX_LAGS: tuple[int, ...] = (6, 12)
RESIDUAL_AR_LAGS = 3


def configure_logging() -> None:
    """Configure a compact console logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def compute_vif(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate variance inflation factors for the regressors."""
    missing_columns = sorted(set(REGRESSOR_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required regressors: {missing_columns}")

    regressors = sm.add_constant(
        data.loc[:, REGRESSOR_COLUMNS],
        has_constant="add",
    )
    values = regressors.to_numpy()

    rows = []
    for index, variable in enumerate(regressors.columns):
        if variable == "const":
            continue
        rows.append(
            {
                "variable": variable,
                "vif": variance_inflation_factor(values, index),
            }
        )

    return pd.DataFrame(rows)


def run_diagnostic_tests(
    model: RegressionResultsWrapper,
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run linearity, heteroskedasticity, autocorrelation, and VIF checks."""
    rainbow_stat, rainbow_p_value = sm.stats.linear_rainbow(model)
    bp_stat, bp_p_value, bp_f_stat, bp_f_p_value = het_breuschpagan(
        model.resid,
        model.model.exog,
    )

    test_table = pd.DataFrame(
        [
            {
                "test": "Rainbow linearity test",
                "statistic": rainbow_stat,
                "p_value": rainbow_p_value,
            },
            {
                "test": "Breusch-Pagan LM test",
                "statistic": bp_stat,
                "p_value": bp_p_value,
            },
            {
                "test": "Breusch-Pagan F test",
                "statistic": bp_f_stat,
                "p_value": bp_f_p_value,
            },
        ]
    )

    autocorrelation_table = acorr_ljungbox(
        model.resid,
        lags=list(LJUNG_BOX_LAGS),
        return_df=True,
    )
    vif_table = compute_vif(data)

    return test_table, autocorrelation_table, vif_table


def fit_residual_autoreg(
    model: RegressionResultsWrapper,
    lags: int = RESIDUAL_AR_LAGS,
) -> AutoRegResultsWrapper:
    """Fit an autoregressive model to the baseline regression residuals."""
    if lags < 1:
        raise ValueError("The number of autoregressive lags must be positive.")

    residuals = pd.Series(model.resid).dropna()
    if len(residuals) <= lags + 5:
        raise ValueError("Not enough residual observations for the AR model.")

    return AutoReg(residuals, lags=lags).fit()


def compare_standard_errors(data: pd.DataFrame) -> pd.DataFrame:
    """Compare conventional and heteroskedasticity-robust standard errors."""
    conventional = smf.ols(FORMULA, data=data).fit()
    robust = smf.ols(FORMULA, data=data).fit(cov_type="HC1")

    return pd.DataFrame(
        {
            "coefficient": robust.params,
            "standard_error_ols": conventional.bse,
            "standard_error_hc1": robust.bse,
            "p_value_ols": conventional.pvalues,
            "p_value_hc1": robust.pvalues,
        }
    )


def _format_test_summary(test_result: object) -> str:
    """Return a plain-text summary for statsmodels test results."""
    summary = test_result.summary()
    if hasattr(summary, "as_text"):
        return summary.as_text()
    return str(summary)


def build_hypothesis_report(model: RegressionResultsWrapper) -> str:
    """Create a compact text report for joint and individual coefficient tests."""
    joint_test = model.f_test("FEDFUNDS = 0, UNRATE = 0")
    fedfunds_test = model.t_test("FEDFUNDS = 0")
    unemployment_test = model.t_test("UNRATE = 0")

    sections = [
        "Joint test: FEDFUNDS = 0 and UNRATE = 0",
        _format_test_summary(joint_test),
        "Individual test: FEDFUNDS = 0",
        _format_test_summary(fedfunds_test),
        "Individual test: UNRATE = 0",
        _format_test_summary(unemployment_test),
    ]
    return "\n\n".join(sections)


def save_partial_regression_plot(
    data: pd.DataFrame,
    output_dir: Path = DIAGNOSTIC_DIR,
) -> None:
    """Save a partial regression plot for the federal funds rate coefficient."""
    output_dir.mkdir(parents=True, exist_ok=True)

    fig = sm.graphics.plot_partregress(
        endog="INDPRO",
        exog_i="FEDFUNDS",
        exog_others=["UNRATE"],
        data=data,
        obs_labels=False,
    )
    fig.set_size_inches(8, 5)
    fig.tight_layout()
    fig.savefig(output_dir / "partial_regression_fedfunds.png", dpi=300)
    plt.close(fig)


def save_diagnostic_outputs(
    model: RegressionResultsWrapper,
    data: pd.DataFrame,
    output_dir: Path = DIAGNOSTIC_DIR,
) -> None:
    """Save all diagnostic tables and reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    test_table, autocorrelation_table, vif_table = run_diagnostic_tests(
        model,
        data,
    )
    ar_model = fit_residual_autoreg(model)
    standard_error_table = compare_standard_errors(data)
    hypothesis_report = build_hypothesis_report(model)

    test_table.to_csv(output_dir / "diagnostic_tests.csv", index=False)
    autocorrelation_table.to_csv(output_dir / "ljung_box_tests.csv")
    vif_table.to_csv(
        output_dir / "variance_inflation_factors.csv",
        index=False,
    )
    standard_error_table.to_csv(output_dir / "standard_error_comparison.csv")

    (output_dir / "residual_autoregression_summary.txt").write_text(
        ar_model.summary().as_text(),
        encoding="utf-8",
    )
    (output_dir / "coefficient_hypothesis_tests.txt").write_text(
        hypothesis_report,
        encoding="utf-8",
    )

    save_partial_regression_plot(data, output_dir)


def run_diagnostics(output_dir: Path = DIAGNOSTIC_DIR) -> None:
    """Run the diagnostic and robustness workflow."""
    raw_data = fetch_fred_data()
    data = prepare_macro_data(raw_data)
    model = estimate_baseline_model(data)

    save_diagnostic_outputs(model, data, output_dir)

    LOGGER.info("Diagnostic outputs saved in: %s", output_dir.resolve())


def main() -> None:
    """Run the script from the command line."""
    configure_logging()
    try:
        run_diagnostics()
    except Exception as exc:
        LOGGER.exception("Diagnostics failed: %s", exc)
        raise


if __name__ == "__main__":
    main()
