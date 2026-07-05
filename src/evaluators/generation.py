"""Generation evaluator (placeholder for BLEU, ROUGE, BERTScore)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.evaluators.base import BaseEvaluator, EvalResult


class GenerationEvaluator(BaseEvaluator):
    """Placeholder for open-ended generation metrics."""

    name = "generation"
    metric = "generation"

    def build_prompt(self, item: dict[str, Any], dataset_path: Path | None = None) -> str:
        return str(item.get("prompt", item.get("input", "")))

    def get_expected(self, item: dict[str, Any], dataset_path: Path | None = None) -> str:
        return str(item.get("reference", item.get("output", "")))

    def evaluate(
        self,
        response: str,
        item: dict[str, Any],
        dataset_path: Path | None = None,
    ) -> EvalResult:
        # Reserved for BLEU, ROUGE, BERTScore
        return EvalResult(
            correct=False,
            predicted=response,
            expected=self.get_expected(item, dataset_path),
            score=0.0,
            metric="generation_stub",
        )
