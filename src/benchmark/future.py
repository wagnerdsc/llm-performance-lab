"""Future benchmark placeholders."""

from __future__ import annotations

from src.core.benchmark_runner import BaseBenchmark, BenchmarkRegistry
from src.core.experiment import Experiment, ExperimentResult


class _FutureBenchmark(BaseBenchmark):
    def __init__(self, benchmark_name: str):
        self.name = benchmark_name

    def run(self, experiment: Experiment) -> ExperimentResult:
        raise NotImplementedError(
            f"Benchmark '{self.name}' is reserved for a future release. "
            "See docs/architecture.md for the roadmap."
        )


class GPUBenchmark(_FutureBenchmark):
    name = "gpu"


class EnergyBenchmark(_FutureBenchmark):
    name = "energy"


class RAGBenchmark(_FutureBenchmark):
    name = "rag"


class MultimodalBenchmark(_FutureBenchmark):
    name = "multimodal"


class LongContextBenchmark(_FutureBenchmark):
    name = "long_context"


for cls in (GPUBenchmark, EnergyBenchmark, RAGBenchmark, MultimodalBenchmark, LongContextBenchmark):
    BenchmarkRegistry.register(cls.name, cls)
