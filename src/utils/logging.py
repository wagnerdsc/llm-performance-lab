"""Logging helpers."""

from __future__ import annotations

from pathlib import Path

from src.config import ensure_directories
from src.utils.io import timestamp_iso


def write_error_log(log_file: Path, message: str) -> None:
    """Append a timestamped error line to a log file."""
    ensure_directories()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp_iso()}] {message}\n")


escrever_log_erro = write_error_log
