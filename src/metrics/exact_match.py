"""Exact match metric."""

from __future__ import annotations

from src.datasets._legacy import normalizar_txt


def exact_match(prediction: str, reference: str) -> float:
    return 1.0 if normalizar_txt(prediction) == normalizar_txt(reference) else 0.0
