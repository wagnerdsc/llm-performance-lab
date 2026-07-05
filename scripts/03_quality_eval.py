#!/usr/bin/env python3
"""Script de entrada para avaliação de qualidade."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cli_common import add_inference_args, add_limit_args, add_path_args, resolve_results_paths  # noqa: E402
from src.quality_eval import avaliar_qualidade  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Avaliação de qualidade em datasets JSONL")
    add_path_args(parser)
    add_limit_args(parser)
    add_inference_args(parser)
    parser.add_argument(
        "--saida",
        type=Path,
        default=None,
        help="CSV de saída (padrão: <results-dir>/quality/quality_resultados.csv)",
    )
    args = parser.parse_args()

    _, quality_dir, _ = resolve_results_paths(args.results_dir)
    saida = args.saida or (quality_dir / "quality_resultados.csv")

    csv_path = avaliar_qualidade(
        modelos_dir=args.models_dir,
        datasets_dir=args.datasets_dir,
        saida_csv=saida,
        itens_por_dataset=args.limit_items,
        max_tokens=args.max_tokens,
        ngl=args.ngl,
        context_size=args.context_size,
        timeout=args.timeout,
        limit_models=args.limit_models,
        limit_datasets=args.limit_datasets,
        model_glob=args.model_glob,
        results_dir=args.results_dir,
    )
    print(f"Resultados salvos em: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
