"""Base evaluator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class EvalResult:
    """Result of evaluating a single model response."""

    correct: bool
    predicted: str
    expected: str
    score: float
    metric: str


class BaseEvaluator(ABC):
    """Abstract evaluator for a dataset type."""

    name: str = "base"
    metric: str = "accuracy"

    @abstractmethod
    def build_prompt(self, item: dict[str, Any], dataset_path: Path | None = None) -> str:
        ...

    @abstractmethod
    def get_expected(self, item: dict[str, Any], dataset_path: Path | None = None) -> str:
        ...

    @abstractmethod
    def evaluate(
        self,
        response: str,
        item: dict[str, Any],
        dataset_path: Path | None = None,
    ) -> EvalResult:
        ...
