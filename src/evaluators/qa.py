"""Question-answering evaluator (TriviaQA, CoQA)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.datasets._legacy import acertou, montar_prompt, obter_resposta_esperada, normalizar_txt
from src.evaluators.base import BaseEvaluator, EvalResult
from src.metrics.exact_match import exact_match
from src.metrics.f1 import token_f1


class QuestionAnsweringEvaluator(BaseEvaluator):
    """QA evaluator using exact match and token F1."""

    name = "question_answering"
    metric = "exact_match"

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
        em = exact_match(response, expected)
        f1 = token_f1(response, expected)
        return EvalResult(
            correct=correct,
            predicted=normalizar_txt(response),
            expected=expected,
            score=max(em, f1),
            metric="exact_match" if em else "f1",
        )
