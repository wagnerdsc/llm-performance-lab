"""Shared I/O utilities."""

from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from src.config import ensure_directories


def list_gguf_files(directory: Path, recursive: bool = True) -> list[Path]:
    """List .gguf files sorted by name."""
    if not directory.is_dir():
        return []
    pattern = "**/*.gguf" if recursive else "*.gguf"
    return sorted(directory.glob(pattern))


listar_gguf = list_gguf_files


def file_size_gib(path: Path) -> float:
    return path.stat().st_size / (1024**3)


def file_size_gb(path: Path) -> float:
    return path.stat().st_size / (1000**3)


tamanho_gib = file_size_gib
tamanho_gb = file_size_gb


def total_size_gb(files: list[Path]) -> float:
    return sum(file_size_gb(p) for p in files)


tamanho_total_gb = total_size_gb


def timestamp_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_csv(path: Path, columns: Iterable[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=list(columns)).writeheader()


inicializar_csv = init_csv


def append_csv(path: Path, columns: Iterable[str], row: dict) -> None:
    columns = list(columns)
    init_csv(path, columns)
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore", restval="")
        writer.writerow(row)


acrescentar_csv = append_csv


def processed_csv_keys(path: Path, key_columns: Iterable[str]) -> set[tuple]:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        keys = list(key_columns)
        return {tuple(row.get(c, "") for c in keys) for row in reader}


chaves_processadas_csv = processed_csv_keys
