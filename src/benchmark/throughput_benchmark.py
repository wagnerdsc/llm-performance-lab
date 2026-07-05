"""Throughput benchmark — llama-bench wrapper."""

from __future__ import annotations

from src.core.benchmark_runner import BaseBenchmark
from src.core.experiment import Experiment, ExperimentResult
from src.benchmark.throughput import run_throughput_benchmark


class ThroughputBenchmark(BaseBenchmark):
    """Tokens-per-second benchmark via llama-bench."""

    name = "throughput"

    def run(self, experiment: Experiment) -> ExperimentResult:
        cfg = experiment.config
        csv_path = run_throughput_benchmark(
            models_dir=cfg.models_dir,
            ngl=cfg.gpu_layers,
            timeout=cfg.timeout,
            limit_models=cfg.limit_models,
            model_glob=cfg.model_glob,
            results_dir=cfg.results_dir,
        )
        return ExperimentResult(benchmark=self.name, csv_path=csv_path)
