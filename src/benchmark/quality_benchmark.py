"""Quality benchmark — registered wrapper."""

from __future__ import annotations

from src.core.benchmark_runner import BaseBenchmark
from src.core.experiment import Experiment, ExperimentResult
from src.benchmark.quality import run_quality_benchmark


class QualityBenchmark(BaseBenchmark):
    """Dataset quality evaluation benchmark."""

    name = "quality"

    def run(self, experiment: Experiment) -> ExperimentResult:
        cfg = experiment.config
        csv_path = run_quality_benchmark(
            models_dir=cfg.models_dir,
            datasets_dir=cfg.datasets_dir,
            items_per_dataset=cfg.items_per_dataset,
            max_tokens=cfg.max_tokens,
            ngl=cfg.gpu_layers,
            context_size=cfg.context_size,
            timeout=cfg.timeout,
            limit_models=cfg.limit_models,
            limit_datasets=cfg.limit_datasets,
            model_glob=cfg.model_glob,
            results_dir=cfg.results_dir,
        )
        return ExperimentResult(benchmark=self.name, csv_path=csv_path)
