"""Latency benchmark — wraps inference with detailed metrics."""

from __future__ import annotations

from src.core.benchmark_runner import BaseBenchmark
from src.core.experiment import Experiment, ExperimentResult
from src.benchmark.inference import InferenceBenchmark


class LatencyBenchmark(BaseBenchmark):
    """Latency measurement benchmark."""

    name = "latency"

    def run(self, experiment: Experiment) -> ExperimentResult:
        return InferenceBenchmark().run(experiment)
