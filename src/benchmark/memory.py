"""Memory benchmark — snapshot RSS during inference."""

from __future__ import annotations

from tqdm import tqdm

from src.core.benchmark_runner import BaseBenchmark
from src.core.experiment import Experiment, ExperimentResult
from src.llm.llama_runner import run_llama
from src.llm.model_loader import discover_models
from src.metrics.memory import snapshot_memory_mb
from src.utils.io import append_csv, init_csv, timestamp_iso

MEMORY_COLUMNS = [
    "timestamp", "model", "quantization",
    "process_rss_mb", "system_used_mb", "system_percent", "latency_s",
]


class MemoryBenchmark(BaseBenchmark):
    """Capture memory usage during a short inference."""

    name = "memory"

    def run(self, experiment: Experiment) -> ExperimentResult:
        cfg = experiment.config
        csv_path = cfg.results_dir / "benchmark" / "memory_usage.csv"
        init_csv(csv_path, MEMORY_COLUMNS)
        models = discover_models(cfg.models_dir, limit=cfg.limit_models, model_glob=cfg.model_glob)
        rows = 0

        for model in tqdm(models, desc="memory"):
            mem_before = snapshot_memory_mb()
            result = run_llama(model.path, "Hi", max_tokens=4, ngl=cfg.gpu_layers, timeout=cfg.timeout)
            mem_after = snapshot_memory_mb()
            append_csv(csv_path, MEMORY_COLUMNS, {
                "timestamp": timestamp_iso(),
                "model": model.name,
                "quantization": model.quantization,
                "process_rss_mb": mem_after["process_rss_mb"],
                "system_used_mb": mem_after["system_used_mb"],
                "system_percent": mem_after["system_percent"],
                "latency_s": result.latency_s,
            })
            rows += 1

        return ExperimentResult(benchmark=self.name, csv_path=csv_path, row_count=rows)
