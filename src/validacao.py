"""Validação de modelos e datasets."""

from __future__ import annotations

import sys
from fnmatch import fnmatch
from pathlib import Path

from .utils import listar_gguf

MSG_SEM_MODELOS = (
    "Não encontrei modelos GGUF. Coloque os arquivos em models/<nome-do-modelo>/*.gguf"
)
MSG_SEM_DATASETS = (
    "Não encontrei datasets JSONL. Coloque os arquivos em datasets/<grupo>/*.jsonl"
)


def listar_datasets_recursivo(datasets_dir: Path) -> list[Path]:
    """Lista datasets JSONL recursivamente (datasets/**/*.jsonl)."""
    if not datasets_dir.is_dir():
        return []
    return sorted(datasets_dir.glob("**/*.jsonl"))


def obter_modelos(
    models_dir: Path,
    limit: int | None = None,
    model_glob: str | None = None,
) -> list[Path]:
    """Retorna modelos GGUF (models/**/*.gguf), opcionalmente filtrados."""
    modelos = listar_gguf(models_dir)
    if model_glob:
        modelos = [
            m for m in modelos
            if fnmatch(m.name, model_glob) or fnmatch(str(m.relative_to(models_dir)), model_glob)
        ]
    if limit is not None and limit > 0:
        return modelos[:limit]
    return modelos


def obter_datasets(datasets_dir: Path, limit: int | None = None) -> list[Path]:
    """Retorna datasets JSONL (datasets/**/*.jsonl), opcionalmente limitados."""
    datasets = listar_datasets_recursivo(datasets_dir)
    if limit is not None and limit > 0:
        return datasets[:limit]
    return datasets


def validar_modelos(models_dir: Path, *, sair_se_vazio: bool = False) -> list[Path]:
    """Valida presença de GGUF; opcionalmente encerra o processo."""
    modelos = listar_gguf(models_dir)
    if not modelos:
        print(MSG_SEM_MODELOS, file=sys.stderr)
        if sair_se_vazio:
            raise SystemExit(1)
    return modelos


def validar_datasets(datasets_dir: Path, *, sair_se_vazio: bool = False) -> list[Path]:
    """Valida presença de JSONL; opcionalmente encerra o processo."""
    datasets = listar_datasets_recursivo(datasets_dir)
    if not datasets:
        print(MSG_SEM_DATASETS, file=sys.stderr)
        if sair_se_vazio:
            raise SystemExit(1)
    return datasets
