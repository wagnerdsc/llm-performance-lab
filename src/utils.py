"""Utilitários compartilhados."""

from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .config import garantir_diretorios


def listar_gguf(diretorio: Path, recursivo: bool = True) -> list[Path]:
    """Lista arquivos .gguf ordenados por nome."""
    if not diretorio.is_dir():
        return []
    padrao = "**/*.gguf" if recursivo else "*.gguf"
    return sorted(diretorio.glob(padrao))


def tamanho_gib(caminho: Path) -> float:
    """Retorna tamanho do arquivo em GiB."""
    return caminho.stat().st_size / (1024**3)


def tamanho_gb(caminho: Path) -> float:
    """Retorna tamanho do arquivo em GB (decimal, 10^9 bytes)."""
    return caminho.stat().st_size / (1000**3)


def tamanho_total_gb(arquivos: list[Path]) -> float:
    """Soma tamanhos de arquivos em GB (decimal)."""
    return sum(tamanho_gb(p) for p in arquivos)


def timestamp_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def escrever_log_erro(arquivo_log: Path, mensagem: str) -> None:
    """Acrescenta linha de erro em arquivo de log."""
    garantir_diretorios()
    arquivo_log.parent.mkdir(parents=True, exist_ok=True)
    with arquivo_log.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp_iso()}] {mensagem}\n")


def inicializar_csv(caminho: Path, colunas: Iterable[str]) -> None:
    """Cria CSV com cabeçalho se o arquivo ainda não existir."""
    if caminho.exists():
        return
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=list(colunas)).writeheader()


def acrescentar_csv(caminho: Path, colunas: Iterable[str], linha: dict) -> None:
    """Acrescenta uma linha ao CSV (cria cabeçalho se necessário)."""
    colunas = list(colunas)
    inicializar_csv(caminho, colunas)
    with caminho.open("a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=colunas).writerow(linha)


def chaves_processadas_csv(caminho: Path, colunas_chave: Iterable[str]) -> set[tuple]:
    """Retorna conjunto de tuplas já presentes no CSV para retomada."""
    if not caminho.exists():
        return set()
    with caminho.open("r", encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        chaves = list(colunas_chave)
        return {tuple(row.get(c, "") for c in chaves) for row in leitor}


def parsear_tps_llama_bench(saida: str, rotulo: str) -> float | None:
    """
    Extrai tokens/s de uma linha do llama-bench.

    Exemplo de linha: | llama 1B Q4_K - Medium |  512 |    1234.56 |
    """
    for linha in saida.splitlines():
        if rotulo not in linha:
            continue
        numeros = re.findall(r"[\d.]+", linha.split("|")[-1] if "|" in linha else linha)
        if numeros:
            try:
                return float(numeros[-1])
            except ValueError:
                continue
    return None
