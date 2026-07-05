"""llama.cpp CLI runner for GGUF inference."""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from src.config import DEFAULT_CONTEXT_SIZE, DEFAULT_MAX_TOKENS, DEFAULT_NGL, DEFAULT_TEMPERATURE, DEFAULT_TIMEOUT, LLAMA_CLI
from src.utils.logging import write_error_log


@dataclass
class LlamaResult:
    """Structured result from a llama-cli invocation."""

    response: str
    error: str
    latency_s: float
    returncode: int
    command: list[str]
    timeout: bool = False

    @property
    def success(self) -> bool:
        return self.returncode == 0 and not self.timeout

    # Legacy aliases
    @property
    def resposta(self) -> str:
        return self.response

    @property
    def erro(self) -> str:
        return self.error

    @property
    def tempo_s(self) -> float:
        return self.latency_s

    @property
    def sucesso(self) -> bool:
        return self.success


ResultadoLlama = LlamaResult

_gpu_cache: bool | None = None


def gpu_available() -> bool:
    """Detect NVIDIA GPU via nvidia-smi (cached)."""
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


gpu_disponivel = gpu_available


def _clean_response(stdout: str, prompt: str) -> str:
    """Strip llama-cli banners, spinners, and metadata from stdout."""
    text = re.sub(r"[\|\\/\-\x08]", "", stdout)
    text = re.sub(r"Loading model\.\.\.", "", text)

    if f"> {prompt}" in text:
        text = text.split(f"> {prompt}", 1)[1]
    elif "> " in text:
        text = text.rsplit("> ", 1)[-1]

    for stop in ("[ Prompt:", "Exiting..."):
        if stop in text:
            text = text.split(stop, 1)[0]

    lines: list[str] = []
    for line in text.splitlines():
        if re.search(r"[▄█▀▐▌░▒▓]", line):
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith(("build ", "model ", "ftype ", "modalities ", "available commands")):
            continue
        if s.startswith("/") and s not in ("/exit",):
            continue
        if s.startswith(">"):
            continue
        lines.append(s)

    return "\n".join(lines).strip()


def _build_command(
    binary: Path,
    model: Path,
    prompt: str,
    *,
    max_tokens: int,
    ngl: int,
    context_size: int,
    temperature: float,
    extra_args: list[str] | None,
) -> list[str]:
    cmd = [
        str(binary),
        "-m", str(model),
        "-p", prompt,
        "-n", str(max_tokens),
        "-c", str(context_size),
        "--temp", str(temperature),
        "--no-display-prompt",
        "--single-turn",
        "--log-disable",
        "--no-perf",
    ]
    if gpu_available() and ngl > 0:
        cmd.extend(["-ngl", str(ngl)])
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def run_llama(
    model: Path,
    prompt: str,
    *,
    llama_cli: Path | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    ngl: int = DEFAULT_NGL,
    context_size: int | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
    timeout: int = DEFAULT_TIMEOUT,
    error_log: Path | None = None,
    extra_args: list[str] | None = None,
) -> LlamaResult:
    """Run llama-cli via subprocess with GPU offload when available."""
    binary = llama_cli or LLAMA_CLI
    ctx = context_size if context_size is not None else DEFAULT_CONTEXT_SIZE

    if not binary.is_file():
        msg = f"Binary not found: {binary}"
        if error_log:
            write_error_log(error_log, msg)
        return LlamaResult("", msg, 0.0, 127, [str(binary)])

    command = _build_command(
        binary, model, prompt,
        max_tokens=max_tokens, ngl=ngl, context_size=ctx,
        temperature=temperature, extra_args=extra_args,
    )

    start = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=False,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
        latency_s = round(time.perf_counter() - start, 3)
        raw = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
        response = _clean_response(raw, prompt)
        error = (proc.stderr or b"").decode("utf-8", errors="replace").strip()

        if proc.returncode != 0 and error_log:
            write_error_log(
                error_log,
                f"llama-cli failed (code={proc.returncode}) model={model.name}: {error[:500]}",
            )
        return LlamaResult(response, error, latency_s, proc.returncode, command)
    except subprocess.TimeoutExpired as exc:
        latency_s = round(time.perf_counter() - start, 3)
        msg = f"Timeout ({timeout}s) model={model.name}"
        if error_log:
            write_error_log(error_log, msg)
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace").strip() if exc.stderr else msg
        stdout = _clean_response(
            (exc.stdout or b"").decode("utf-8", errors="replace").strip() if exc.stdout else "",
            prompt,
        )
        return LlamaResult(stdout, stderr or msg, latency_s, -1, command, timeout=True)
    except OSError as exc:
        latency_s = round(time.perf_counter() - start, 3)
        msg = f"Failed to run llama-cli: {exc}"
        if error_log:
            write_error_log(error_log, msg)
        return LlamaResult("", msg, latency_s, 127, command)


rodar_llama = run_llama
