"""Multiple-choice evaluator (ENEM, BBQ, LogiQA)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.datasets._legacy import acertou, extrair_alternativa, montar_prompt, obter_resposta_esperada
from src.evaluators.base import BaseEvaluator, EvalResult
from src.metrics.accuracy import compute_accuracy


class MultipleChoiceEvaluator(BaseEvaluator):
    """Evaluator for multiple-choice datasets using accuracy."""

    name = "multiple_choice"
    metric = "accuracy"

    def build_prompt(self, item: dict[str, Any], dataset_path: Path | None = None) -> str:
        return montar_prompt(item, dataset_path)

    def get_expected(self, item: dict[str, Any], dataset_path: Path | None = None) -> str:
        return obter_resposta_esperada(item, dataset_path)

    def evaluate(
        self,
        response: str,
        item: dict[str, Any],
        dataset_path: Path | None = None,
    ) -> EvalResult:
        expected = self.get_expected(item, dataset_path)
        correct = acertou(response, expected, caminho=dataset_path, item=item)
        predicted = extrair_alternativa(response)
        return EvalResult(
            correct=correct,
            predicted=predicted,
            expected=expected,
            score=compute_accuracy(correct),
            metric=self.metric,
        )
