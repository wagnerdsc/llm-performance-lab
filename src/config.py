"""Caminhos e configurações centralizadas do LLM Performance Lab."""

from __future__ import annotations

import os
from pathlib import Path

# Diretório raiz do projeto (LLM-Performance-Lab/)
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"
DATASET_DIR = BASE_DIR / "datasets"
RESULT_DIR = BASE_DIR / "results"
CACHE_DIR = BASE_DIR / "cache"

RESULT_BENCHMARK_DIR = RESULT_DIR / "benchmark"
RESULT_QUALITY_DIR = RESULT_DIR / "quality"
RESULT_LOGS_DIR = RESULT_DIR / "logs"

LLAMA_CPP_DIR = BASE_DIR / "cache" / "llama.cpp"

# Binários compilados (GPU preferencial, fallback CPU)
LLAMA_CLI = LLAMA_CPP_DIR / "build" / "bin" / "llama-cli"
LLAMA_BENCH = LLAMA_CPP_DIR / "build" / "bin" / "llama-bench"

# Inferência
DEFAULT_NGL = 999
DEFAULT_TIMEOUT = 300
DEFAULT_MAX_TOKENS = 256
DEFAULT_CONTEXT_SIZE = 4096
DEFAULT_TEMPERATURE = 0.0

# Avaliação de qualidade
DEFAULT_ITEMS_POR_DATASET = 50

# Benchmark
BENCHMARK_PP_TOKENS = 512
BENCHMARK_TG_TOKENS = 128


def garantir_diretorios() -> None:
    """Cria diretórios de saída se ainda não existirem."""
    for path in (
        MODEL_DIR,
        DATASET_DIR,
        CACHE_DIR,
        RESULT_BENCHMARK_DIR,
        RESULT_QUALITY_DIR,
        RESULT_LOGS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def binario_existe(caminho: Path) -> bool:
    return caminho.is_file() and os.access(caminho, os.X_OK)
