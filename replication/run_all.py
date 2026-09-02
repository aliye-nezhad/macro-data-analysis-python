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

    print("All workflow stages completed successfully.", flush=True)


if __name__ == "__main__":
    run_all()
