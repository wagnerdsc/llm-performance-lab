"""Carregamento e utilitários para datasets JSONL de avaliação."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterator

from .config import DATASET_DIR


def listar_datasets(diretorio: Path | None = None) -> list[Path]:
    """Lista arquivos .jsonl no diretório de datasets."""
    base = diretorio or DATASET_DIR
    if not base.is_dir():
        return []
    return sorted(base.glob("**/*.jsonl"))


def carregar_jsonl(caminho: Path, limite: int | None = None) -> list[dict[str, Any]]:
    """Carrega itens de um arquivo JSONL."""
    itens: list[dict[str, Any]] = []
    with caminho.open("r", encoding="utf-8") as f:
        for i, linha in enumerate(f):
            if limite is not None and i >= limite:
                break
            linha = linha.strip()
            if not linha:
                continue
            itens.append(json.loads(linha))
    return itens


def iterar_jsonl(caminho: Path, limite: int | None = None) -> Iterator[dict[str, Any]]:
    """Itera itens de um JSONL sem carregar tudo em memória."""
    with caminho.open("r", encoding="utf-8") as f:
        for i, linha in enumerate(f):
            if limite is not None and i >= limite:
                break
            linha = linha.strip()
            if linha:
                yield json.loads(linha)


def normalizar_txt(texto: str) -> str:
    """Normaliza texto para comparação (minúsculas, sem acentos, espaços)."""
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower().strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def _obter_campo(item: dict[str, Any], chaves: list[str], padrao: str = "") -> str:
    for chave in chaves:
        if chave in item and item[chave] is not None:
            return str(item[chave])
    return padrao


def obter_resposta_esperada(item: dict[str, Any]) -> str:
    """Extrai a resposta correta de um item (A/B/C/D ou texto)."""
    return _obter_campo(
        item,
        ["resposta", "resposta_correta", "answer", "label", "gold", "correct"],
    ).strip()


def _formatar_alternativas(item: dict[str, Any]) -> str:
    alternativas = item.get("alternativas") or item.get("choices") or item.get("options")
    if isinstance(alternativas, dict):
        linhas = [f"{letra}) {texto}" for letra, texto in sorted(alternativas.items())]
        return "\n".join(linhas)
    if isinstance(alternativas, list):
        letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return "\n".join(
            f"{letras[i]}) {alt}" for i, alt in enumerate(alternativas) if i < len(letras)
        )
    return ""


def montar_prompt(item: dict[str, Any], template: str | None = None) -> str:
    """
    Monta prompt a partir de um item do dataset.

    Suporta campos: pergunta/question/enunciado, alternativas/choices.
    """
    if template:
        return template.format(**item)

    pergunta = _obter_campo(item, ["pergunta", "question", "enunciado", "prompt", "input"])
    alternativas = _formatar_alternativas(item)

    partes = [pergunta]
    if alternativas:
        partes.append(alternativas)
    partes.append("Responda apenas com a letra da alternativa correta (A, B, C ou D).")
    return "\n\n".join(p for p in partes if p)


def extrair_alternativa(texto: str) -> str:
    """
    Extrai letra de alternativa (A-D) da resposta do modelo.

    Prioriza padrões explícitos como 'Resposta: B' ou resposta isolada.
    """
    if not texto:
        return ""

    texto_limpo = texto.strip()

    padroes = [
        r"(?:resposta|answer|alternativa|opcao|opção)\s*(?:é|eh|is|:|-)\s*([a-dA-D])",
        r"(?:resposta|answer|alternativa|opcao|opção)\s*[:\-]?\s*([a-dA-D])",
        r"^([a-dA-D])\s*$",
        r"^([a-dA-D])\s*[\).]",
        r"\(([a-dA-D])\)",
    ]
    for padrao in padroes:
        m = re.search(padrao, texto_limpo, re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(1).upper()

    # Última letra A-D isolada (evita pegar artigo "A" no início)
    candidatos = re.findall(r"(?<![a-zA-Z])([A-Da-d])(?![a-zA-Z])", texto_limpo)
    if candidatos:
        return candidatos[-1].upper()

    return normalizar_txt(texto_limpo)[:1].upper()


def acertou(resposta_modelo: str, resposta_esperada: str) -> bool:
    """Compara resposta do modelo com a esperada."""
    alt_modelo = extrair_alternativa(resposta_modelo)
    alt_esperada = extrair_alternativa(resposta_esperada) or resposta_esperada.strip().upper()

    if alt_modelo and alt_esperada and len(alt_esperada) == 1:
        return alt_modelo == alt_esperada.upper()

    return normalizar_txt(resposta_modelo) == normalizar_txt(resposta_esperada)
