"""Shared helpers for report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

NO_DATA_MESSAGE = "No benchmark rows available yet."


def safe_read_csv(path: Path) -> pd.DataFrame | None:
    """Read CSV with UTF-8 replacement; return None if missing, empty, or unreadable."""
    if not path.is_file() or path.stat().st_size == 0:
        return None
    try:
        df = pd.read_csv(
            path,
            encoding="utf-8",
            encoding_errors="replace",
            engine="python",
            on_bad_lines="skip",
        )
    except pd.errors.ParserError:
        return None
    if df.empty or len(df) == 0:
        return None
    return df
