"""Benchmark orchestration using the benchmark registry."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from src.core.experiment import Experiment, ExperimentResult
from src.core.registry import Registry

logger = logging.getLogger(__name__)


class BaseBenchmark(ABC):
    """Abstract base class for all benchmarks."""

    name: str = "base"

    @abstractmethod
    def run(self, experiment: Experiment) -> ExperimentResult:
        """Execute the benchmark and return structured results."""


BenchmarkRegistry: Registry[type[BaseBenchmark]] = Registry("BenchmarkRegistry")


class BenchmarkRunner:
    """Runs one or more registered benchmarks."""

    def __init__(self, experiment: Experiment) -> None:
        self.experiment = experiment

    def run(self, names: list[str]) -> list[ExperimentResult]:
        experiment = self.experiment
        experiment.ensure_dirs()
        if experiment.config.save_metadata:
            experiment.save_metadata()

        results: list[ExperimentResult] = []
        for name in names:
            cls = BenchmarkRegistry.get(name)
            benchmark = cls()
            logger.info("Running benchmark: %s", name)
            result = benchmark.run(experiment)
            results.append(result)
            logger.info("Benchmark %s completed (%d rows)", name, result.row_count)
        return results

    @staticmethod
    def available() -> list[str]:
        return BenchmarkRegistry.list()
