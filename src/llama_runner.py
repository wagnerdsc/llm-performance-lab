"""Wrapper para execução do llama-cli via subprocess."""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .config import (
    DEFAULT_CONTEXT_SIZE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_NGL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    LLAMA_CLI,
)
from .utils import escrever_log_erro


@dataclass
class ResultadoLlama:
    resposta: str
    erro: str
    tempo_s: float
    returncode: int
    comando: list[str]
    timeout: bool = False

    @property
    def sucesso(self) -> bool:
        return self.returncode == 0 and not self.timeout


_gpu_cache: bool | None = None


def gpu_disponivel() -> bool:
    """Detecta GPU NVIDIA via nvidia-smi (resultado cacheado)."""
    global _gpu_cache
    if _gpu_cache is not None:
        return _gpu_cache
    try:
        proc = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
        _gpu_cache = proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        _gpu_cache = False
    return _gpu_cache


def _limpar_resposta(stdout: str, prompt: str) -> str:
    """Remove banner, spinner e metadados do llama-cli; retorna texto gerado."""
    texto = re.sub(r"[\|\\/\-\x08]", "", stdout)
    texto = re.sub(r"Loading model\.\.\.", "", texto)

    if f"> {prompt}" in texto:
        texto = texto.split(f"> {prompt}", 1)[1]
    elif "> " in texto:
        texto = texto.rsplit("> ", 1)[-1]

    for stop in ("[ Prompt:", "Exiting..."):
        if stop in texto:
            texto = texto.split(stop, 1)[0]

    linhas: list[str] = []
    for linha in texto.splitlines():
        if re.search(r"[▄█▀▐▌░▒▓]", linha):
            continue
        s = linha.strip()
        if not s:
            continue
        if s.startswith(("build ", "model ", "ftype ", "modalities ", "available commands")):
            continue
        if s.startswith("/") and s not in ("/exit",):
            continue
        if s.startswith(">"):
            continue
        linhas.append(s)

    return "\n".join(linhas).strip()


def _montar_comando(
    binario: Path,
    modelo: Path,
    prompt: str,
    *,
    max_tokens: int,
    ngl: int,
    context_size: int,
    temperature: float,
    extra_args: list[str] | None,
) -> list[str]:
    comando = [
        str(binario),
        "-m", str(modelo),
        "-p", prompt,
        "-n", str(max_tokens),
        "-c", str(context_size),
        "--temp", str(temperature),
        "--no-display-prompt",
        "--single-turn",
        "--log-disable",
        "--no-perf",
    ]
    if gpu_disponivel() and ngl > 0:
        comando.extend(["-ngl", str(ngl)])
    if extra_args:
        comando.extend(extra_args)
    return comando


def rodar_llama(
    modelo: Path,
    prompt: str,
    *,
    llama_cli: Path | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    ngl: int = DEFAULT_NGL,
    context_size: int | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
    timeout: int = DEFAULT_TIMEOUT,
    log_erros: Path | None = None,
    extra_args: list[str] | None = None,
) -> ResultadoLlama:
    """
    Executa llama-cli com subprocess.run.

    Usa -ngl somente quando há GPU disponível; inclui --single-turn e
    stdin=DEVNULL para evitar bloqueio interativo.
    """
    binario = llama_cli or LLAMA_CLI
    ctx = context_size if context_size is not None else DEFAULT_CONTEXT_SIZE

    if not binario.is_file():
        msg = f"Binário não encontrado: {binario}"
        if log_erros:
            escrever_log_erro(log_erros, msg)
        return ResultadoLlama("", msg, 0.0, 127, [str(binario)])

    comando = _montar_comando(
        binario,
        modelo,
        prompt,
        max_tokens=max_tokens,
        ngl=ngl,
        context_size=ctx,
        temperature=temperature,
        extra_args=extra_args,
    )

    inicio = time.perf_counter()
    try:
        proc = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
        tempo_s = round(time.perf_counter() - inicio, 3)
        bruto = (proc.stdout or "").strip()
        resposta = _limpar_resposta(bruto, prompt)
        erro = (proc.stderr or "").strip()

        if proc.returncode != 0 and log_erros:
            escrever_log_erro(
                log_erros,
                f"llama-cli falhou (code={proc.returncode}) modelo={modelo.name}: {erro[:500]}",
            )
        return ResultadoLlama(
            resposta=resposta,
            erro=erro,
            tempo_s=tempo_s,
            returncode=proc.returncode,
            comando=comando,
        )
    except subprocess.TimeoutExpired as exc:
        tempo_s = round(time.perf_counter() - inicio, 3)
        msg = f"Timeout ({timeout}s) modelo={modelo.name}"
        if log_erros:
            escrever_log_erro(log_erros, msg)
        stderr = (exc.stderr or "").strip() if exc.stderr else msg
        stdout = _limpar_resposta((exc.stdout or "").strip() if exc.stdout else "", prompt)
        return ResultadoLlama(
            resposta=stdout,
            erro=stderr or msg,
            tempo_s=tempo_s,
            returncode=-1,
            comando=comando,
            timeout=True,
        )
    except OSError as exc:
        tempo_s = round(time.perf_counter() - inicio, 3)
        msg = f"Erro ao executar llama-cli: {exc}"
        if log_erros:
            escrever_log_erro(log_erros, msg)
        return ResultadoLlama("", msg, tempo_s, 127, comando)
