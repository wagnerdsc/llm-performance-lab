"""Inference benchmark — single-prompt latency per model."""

from __future__ import annotations

from pathlib import Path

from tqdm import tqdm

from src.config import LabConfig, ensure_directories
from src.core.benchmark_runner import BaseBenchmark
from src.core.experiment import Experiment, ExperimentResult
from src.llm.llama_runner import run_llama
from src.llm.model_loader import discover_models
from src.utils.io import append_csv, init_csv, timestamp_iso

INFERENCE_COLUMNS = ["timestamp", "model", "quantization", "latency_s", "returncode", "prompt_tokens_est"]


class InferenceBenchmark(BaseBenchmark):
    """Measure end-to-end inference latency with a short prompt."""

    name = "inference"

    def run(self, experiment: Experiment) -> ExperimentResult:
        cfg = experiment.config
        ensure_directories(cfg)
        csv_path = cfg.results_dir / "benchmark" / "inference_latency.csv"
        init_csv(csv_path, INFERENCE_COLUMNS)

        models = discover_models(cfg.models_dir, limit=cfg.limit_models, model_glob=cfg.model_glob)
        prompt = "Answer with one word: OK"
        rows = 0

        for model in tqdm(models, desc="inference"):
            result = run_llama(
                model.path, prompt,
                max_tokens=8, ngl=cfg.gpu_layers,
                context_size=cfg.context_size, timeout=cfg.timeout,
            )
            append_csv(csv_path, INFERENCE_COLUMNS, {
                "timestamp": timestamp_iso(),
                "model": model.name,
                "quantization": model.quantization,
                "latency_s": result.latency_s,
                "returncode": result.returncode,
                "prompt_tokens_est": len(prompt.split()),
            })
            rows += 1

        return ExperimentResult(benchmark=self.name, csv_path=csv_path, row_count=rows)
