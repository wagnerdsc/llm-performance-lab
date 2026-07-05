"""Argumentos CLI compartilhados entre scripts."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import (
    CACHE_DIR,
    DATASET_DIR,
    DEFAULT_CONTEXT_SIZE,
    DEFAULT_ITEMS_POR_DATASET,
    DEFAULT_MAX_TOKENS,
    DEFAULT_NGL,
    DEFAULT_TIMEOUT,
    MODEL_DIR,
    RESULT_DIR,
)


def add_path_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=MODEL_DIR,
        help="Diretório raiz dos modelos GGUF (busca recursiva: **/*.gguf)",
    )
    parser.add_argument(
        "--datasets-dir",
        type=Path,
        default=DATASET_DIR,
        help="Diretório raiz dos datasets (busca recursiva: **/*.jsonl)",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULT_DIR,
        help="Diretório raiz de resultados (benchmark/, quality/, logs/)",
    )


def add_limit_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--limit-models",
        type=int,
        default=None,
        help="Limita quantidade de modelos GGUF processados",
    )
    parser.add_argument(
        "--model-glob",
        type=str,
        default=None,
        help="Filtra modelos por padrão glob (ex.: '*Q4_K_M*')",
    )
    parser.add_argument(
        "--limit-datasets",
        type=int,
        default=None,
        help="Limita quantidade de datasets JSONL processados",
    )
    parser.add_argument(
        "--limit-items",
        type=int,
        default=DEFAULT_ITEMS_POR_DATASET,
        help="Máximo de itens por dataset",
    )


def add_inference_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--ngl", type=int, default=DEFAULT_NGL, help="Camadas na GPU (-ngl)")
    parser.add_argument(
        "--context-size",
        type=int,
        default=DEFAULT_CONTEXT_SIZE,
        help="Tamanho de contexto (-c)",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout por execução (s)")


def resolve_results_paths(results_dir: Path) -> tuple[Path, Path, Path]:
    """Retorna (benchmark_dir, quality_dir, logs_dir) a partir de results-dir."""
    return results_dir / "benchmark", results_dir / "quality", results_dir / "logs"


def cache_dir() -> Path:
    return CACHE_DIR
