"""Benchmark package — registers all benchmarks."""

from src.core.benchmark_runner import BenchmarkRegistry
from src.benchmark.inference import InferenceBenchmark
from src.benchmark.latency import LatencyBenchmark
from src.benchmark.throughput_benchmark import ThroughputBenchmark
from src.benchmark.quality_benchmark import QualityBenchmark
from src.benchmark.memory import MemoryBenchmark
from src.benchmark.quantization import QuantizationBenchmark
from src.benchmark.throughput import rodar_benchmark, run_throughput_benchmark
from src.benchmark.quality import avaliar_qualidade, run_quality_benchmark
import src.benchmark.future  # noqa: F401 — registers future benchmarks

BenchmarkRegistry.register("inference", InferenceBenchmark)
BenchmarkRegistry.register("latency", LatencyBenchmark)
BenchmarkRegistry.register("throughput", ThroughputBenchmark)
BenchmarkRegistry.register("quality", QualityBenchmark)
BenchmarkRegistry.register("memory", MemoryBenchmark)
BenchmarkRegistry.register("quantization", QuantizationBenchmark)

__all__ = [
    "rodar_benchmark", "run_throughput_benchmark",
    "avaliar_qualidade", "run_quality_benchmark",
    "BenchmarkRegistry",
]
