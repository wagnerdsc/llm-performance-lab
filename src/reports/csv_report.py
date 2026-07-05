"""CSV report aggregation."""

from __future__ import annotations

import shutil
from pathlib import Path


def generate_csv_report(results_dir: Path, reports_dir: Path) -> Path:
    """Copy benchmark CSVs into reports directory."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    out = reports_dir / "summary"
    out.mkdir(exist_ok=True)
    for csv in results_dir.rglob("*.csv"):
        dest = out / csv.name
        shutil.copy2(csv, dest)
    return out
