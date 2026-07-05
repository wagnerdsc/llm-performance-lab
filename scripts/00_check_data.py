#!/usr/bin/env python3
"""Verifica modelos, datasets e diretórios do projeto (sem inferência)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cli_common import add_path_args, cache_dir  # noqa: E402
from src.config import BASE_DIR, CACHE_DIR, RESULT_DIR, RESULT_LOGS_DIR, garantir_diretorios  # noqa: E402
from src.utils import listar_gguf, tamanho_gb, tamanho_total_gb  # noqa: E402
from src.validacao import listar_datasets_recursivo  # noqa: E402


def _status(path: Path) -> str:
    return "OK" if path.is_dir() else "AUSENTE"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lista modelos GGUF e datasets JSONL disponíveis (sem inferência)",
    )
    add_path_args(parser)
    args = parser.parse_args()

    models_dir: Path = args.models_dir
    datasets_dir: Path = args.datasets_dir
    results_dir: Path = args.results_dir

    modelos = listar_gguf(models_dir)
    datasets = listar_datasets_recursivo(datasets_dir)

    print("=== LLM Performance Lab — Verificação de dados ===")
    print(f"Base:         {BASE_DIR}")
    print(f"Models dir:   {models_dir}")
    print(f"Datasets dir: {datasets_dir}")
    print(f"Results dir:  {results_dir}")
    print()

    print(f"Modelos GGUF encontrados:   {len(modelos)}")
    print(f"Datasets JSONL encontrados: {len(datasets)}")
    print()

    if modelos:
        print("Primeiros modelos (até 10):")
        for m in modelos[:10]:
            rel = m.relative_to(models_dir) if m.is_relative_to(models_dir) else m
            print(f"  - {rel} ({tamanho_gb(m):.2f} GB)")
        total_gb = tamanho_total_gb(modelos)
        print(f"\nTamanho total dos modelos: {total_gb:.2f} GB")
    else:
        print("Nenhum modelo GGUF encontrado.")
        print("  → Coloque os arquivos em models/<nome-do-modelo>/*.gguf")

    print()

    if datasets:
        print("Primeiros datasets (até 20):")
        for d in datasets[:20]:
            rel = d.relative_to(datasets_dir) if d.is_relative_to(datasets_dir) else d
            print(f"  - {rel}")
    else:
        print("Nenhum dataset JSONL encontrado.")
        print("  → Coloque os arquivos em datasets/<grupo>/*.jsonl")

    print()
    print("=== Diretórios ===")
    print(f"  results/       [{_status(results_dir)}]  {results_dir}")
    print(f"  results/logs/  [{_status(results_dir / 'logs')}]  {results_dir / 'logs'}")
    print(f"  cache/         [{_status(CACHE_DIR)}]  {CACHE_DIR}")

    if results_dir != RESULT_DIR:
        print(f"  (padrão results/) [{_status(RESULT_DIR)}]  {RESULT_DIR}")
    if RESULT_LOGS_DIR != results_dir / "logs":
        print(f"  (padrão logs/)    [{_status(RESULT_LOGS_DIR)}]  {RESULT_LOGS_DIR}")

    cache = cache_dir()
    llama_cli = cache / "llama.cpp" / "build" / "bin" / "llama-cli"
    print(f"  llama-cli      [{'OK' if llama_cli.is_file() else 'AUSENTE'}]  {llama_cli}")

    garantir_diretorios()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
