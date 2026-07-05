"""Accuracy metric."""

from __future__ import annotations


def compute_accuracy(correct: bool) -> float:
    return 1.0 if correct else 0.0
