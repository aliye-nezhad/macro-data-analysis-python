"""Run the complete macroeconomic regression and diagnostic workflow."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPTS = (
    REPOSITORY_ROOT / "code" / "macro_regression_workflow.py",
    REPOSITORY_ROOT / "code" / "diagnostic_workflow.py",
)
EXPECTED_OUTPUTS = (
    REPOSITORY_ROOT / "outputs" / "figures" / "macro_series.png",
    REPOSITORY_ROOT / "outputs" / "figures" / "actual_vs_fitted.png",
    REPOSITORY_ROOT / "outputs" / "figures" / "baseline_residuals.png",
    REPOSITORY_ROOT / "outputs" / "figures" / "partial_regression_fedfunds.png",
    REPOSITORY_ROOT / "outputs" / "tables" / "descriptive_statistics.csv",
    REPOSITORY_ROOT / "outputs" / "tables" / "correlation_matrix.csv",
    REPOSITORY_ROOT / "outputs" / "tables" / "baseline_regression_summary.txt",
    REPOSITORY_ROOT / "outputs" / "tables" / "fitted_values.csv",
    REPOSITORY_ROOT / "outputs" / "tables" / "diagnostic_tests.csv",
    REPOSITORY_ROOT / "outputs" / "tables" / "ljung_box_tests.csv",
    REPOSITORY_ROOT / "outputs" / "tables" / "standard_error_comparison.csv",
    REPOSITORY_ROOT / "outputs" / "tables" / "variance_inflation_factors.csv",
    REPOSITORY_ROOT
    / "outputs"
    / "diagnostics"
    / "coefficient_hypothesis_tests.txt",
    REPOSITORY_ROOT
    / "outputs"
    / "diagnostics"
    / "residual_autoregression_summary.txt",
)


def run_all() -> None:
    """Execute both workflow stages from the repository root."""
    environment = os.environ.copy()
    environment.setdefault("MPLBACKEND", "Agg")

    for script in WORKFLOW_SCRIPTS:
        if not script.is_file():
            raise FileNotFoundError(f"Required workflow script not found: {script}")

        print(f"Running {script.relative_to(REPOSITORY_ROOT)}", flush=True)
        subprocess.run(
            [sys.executable, str(script)],
            cwd=REPOSITORY_ROOT,
            env=environment,
            check=True,
        )

    missing_or_empty = [
        path
        for path in EXPECTED_OUTPUTS
        if not path.is_file() or path.stat().st_size == 0
    ]
    if missing_or_empty:
        formatted_paths = "\n".join(
            f"- {path.relative_to(REPOSITORY_ROOT)}"
            for path in missing_or_empty
        )
        raise RuntimeError(
            "Workflow finished, but expected outputs are missing or empty:\n"
            f"{formatted_paths}"
        )

    print(
        f"All workflow stages completed successfully; "
        f"validated {len(EXPECTED_OUTPUTS)} output files.",
        flush=True,
    )


if __name__ == "__main__":
    run_all()
