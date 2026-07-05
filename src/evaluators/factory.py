"""Evaluator factory — selects evaluator by dataset family."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.core.registry import Registry
from src.datasets.registry import detect_family
from src.evaluators.arithmetic import ArithmeticEvaluator
from src.evaluators.base import BaseEvaluator
from src.evaluators.generation import GenerationEvaluator
from src.evaluators.multiple_choice import MultipleChoiceEvaluator
from src.evaluators.qa import QuestionAnsweringEvaluator

EvaluatorRegistry: Registry[type[BaseEvaluator]] = Registry("EvaluatorRegistry")

EvaluatorRegistry.register("bbq", MultipleChoiceEvaluator)
EvaluatorRegistry.register("enem", MultipleChoiceEvaluator)
EvaluatorRegistry.register("logiqa", MultipleChoiceEvaluator)
EvaluatorRegistry.register("mcq", MultipleChoiceEvaluator)
EvaluatorRegistry.register("gsm8k", ArithmeticEvaluator)
EvaluatorRegistry.register("arithmetic", ArithmeticEvaluator)
EvaluatorRegistry.register("triviaqa", QuestionAnsweringEvaluator)
EvaluatorRegistry.register("coqa", QuestionAnsweringEvaluator)
EvaluatorRegistry.register("generation", GenerationEvaluator)


def get_evaluator(dataset_path: Path, item: dict[str, Any] | None = None) -> BaseEvaluator:
    """Return the appropriate evaluator for a dataset."""
    family = detect_family(dataset_path, item)
    if family in EvaluatorRegistry:
        return EvaluatorRegistry.get(family)()
    return MultipleChoiceEvaluator()


class EvaluatorFactory:
    """Factory for creating evaluators by dataset path."""

    @staticmethod
    def create(dataset_path: Path, item: dict[str, Any] | None = None) -> BaseEvaluator:
        return get_evaluator(dataset_path, item)
