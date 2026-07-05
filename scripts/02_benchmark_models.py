#!/usr/bin/env python3
"""Script de entrada para benchmark de performance."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.benchmark import rodar_benchmark  # noqa: E402
from src.cli_common import add_inference_args, add_limit_args, add_path_args, resolve_results_paths  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark llama-bench em modelos GGUF")
    add_path_args(parser)
    add_limit_args(parser)
    add_inference_args(parser)
    parser.add_argument(
        "--saida",
        type=Path,
        default=None,
        help="CSV de saída (padrão: <results-dir>/benchmark/benchmark_resultados.csv)",
    )
    args = parser.parse_args()

    benchmark_dir, _, _ = resolve_results_paths(args.results_dir)
    saida = args.saida or (benchmark_dir / "benchmark_resultados.csv")

    csv_path = rodar_benchmark(
        modelos_dir=args.models_dir,
        saida_csv=saida,
        ngl=args.ngl,
        context_size=args.context_size,
        timeout=args.timeout,
        limit_models=args.limit_models,
        model_glob=args.model_glob,
        results_dir=args.results_dir,
    )
    print(f"Resultados salvos em: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
