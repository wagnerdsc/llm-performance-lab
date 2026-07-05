"""Quantization benchmark — compare quant levels from throughput results."""

from __future__ import annotations

import csv
from pathlib import Path

from src.core.benchmark_runner import BaseBenchmark
from src.core.experiment import Experiment, ExperimentResult
from src.benchmark.throughput import run_throughput_benchmark
from src.utils.io import append_csv, init_csv, timestamp_iso

QUANT_COLUMNS = ["timestamp", "model", "quantization", "size_gib", "pp512_tps", "tg128_tps", "efficiency"]


class QuantizationBenchmark(BaseBenchmark):
    """Run throughput benchmark and emit quantization comparison CSV."""

    name = "quantization"

    def run(self, experiment: Experiment) -> ExperimentResult:
        cfg = experiment.config
        throughput_csv = run_throughput_benchmark(
            models_dir=cfg.models_dir,
            ngl=cfg.gpu_layers,
            timeout=cfg.timeout,
            limit_models=cfg.limit_models,
            model_glob=cfg.model_glob,
            results_dir=cfg.results_dir,
        )

        quant_csv = cfg.results_dir / "benchmark" / "quantization_comparison.csv"
        init_csv(quant_csv, QUANT_COLUMNS)
        rows = 0

        if throughput_csv.exists():
            with throughput_csv.open(encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    pp = float(row["pp512_tps"]) if row.get("pp512_tps") else 0.0
                    size = float(row["tamanho_gib"]) if row.get("tamanho_gib") else 1.0
                    eff = pp / size if size else 0.0
                    append_csv(quant_csv, QUANT_COLUMNS, {
                        "timestamp": timestamp_iso(),
                        "model": row.get("arquivo", ""),
                        "quantization": Path(row.get("arquivo", "")).stem,
                        "size_gib": size,
                        "pp512_tps": pp,
                        "tg128_tps": row.get("tg128_tps", ""),
                        "efficiency": round(eff, 3),
                    })
                    rows += 1

        return ExperimentResult(benchmark=self.name, csv_path=quant_csv, row_count=rows)
