"""Throughput benchmark engine (llama-bench)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from tqdm import tqdm

from src.config import (
    BENCHMARK_PP_TOKENS,
    BENCHMARK_TG_TOKENS,
    DEFAULT_NGL,
    DEFAULT_TIMEOUT,
    LLAMA_BENCH,
    MODEL_DIR,
    RESULT_BENCHMARK_DIR,
    ensure_directories,
)
from src.llm.llama_runner import gpu_available
from src.utils.io import append_csv, file_size_gib, init_csv, timestamp_iso
from src.utils.llama_parse import parse_llama_bench_tps
from src.utils.logging import write_error_log

BENCHMARK_COLUMNS = [
    "timestamp", "arquivo", "tamanho_gib", "backend",
    "pp512_tps", "tg128_tps", "saida_bruta",
]

COLUNAS_BENCHMARK = BENCHMARK_COLUMNS


def _detect_backend(output: str) -> str:
    lower = output.lower()
    if "cuda" in lower or "cublas" in lower or "gpu" in lower:
        return "cuda"
    if "metal" in lower:
        return "metal"
    if "vulkan" in lower:
        return "vulkan"
    return "cpu"


def run_llama_bench(
    model: Path,
    *,
    llama_bench: Path | None = None,
    ngl: int = DEFAULT_NGL,
    timeout: int = DEFAULT_TIMEOUT,
) -> tuple[str, int]:
    """Execute llama-bench for one GGUF model."""
    binary = llama_bench or LLAMA_BENCH
    cmd = [
        str(binary), "-m", str(model),
        "-ngl", str(ngl if gpu_available() and ngl > 0 else 0),
        "-p", str(BENCHMARK_PP_TOKENS),
        "-n", str(BENCHMARK_TG_TOKENS),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return output.strip(), proc.returncode
    except subprocess.TimeoutExpired:
        return f"TIMEOUT after {timeout}s", -1
    except OSError as exc:
        return str(exc), 127


executar_llama_bench = run_llama_bench


def run_throughput_benchmark(
    models_dir: Path | None = None,
    output_csv: Path | None = None,
    *,
    llama_bench: Path | None = None,
    ngl: int = DEFAULT_NGL,
    timeout: int = DEFAULT_TIMEOUT,
    limit_models: int | None = None,
    model_glob: str | None = None,
    results_dir: Path | None = None,
) -> Path:
    """Run llama-bench on all GGUF models and save incremental CSV."""
    from src.validacao import obter_modelos, validar_modelos

    ensure_directories()
    base = models_dir or MODEL_DIR
    bench_dir = (results_dir / "benchmark") if results_dir else RESULT_BENCHMARK_DIR
    csv_path = output_csv or (bench_dir / "benchmark_resultados.csv")
    log_path = ((results_dir / "logs") if results_dir else RESULT_BENCHMARK_DIR.parent / "logs") / "benchmark_erros.log"

    validar_modelos(base, sair_se_vazio=True)
    models = obter_modelos(base, limit=limit_models, model_glob=model_glob)
    binary = llama_bench or LLAMA_BENCH

    if not binary.is_file():
        write_error_log(log_path, f"llama-bench not found: {binary}")
        init_csv(csv_path, BENCHMARK_COLUMNS)
        return csv_path

    init_csv(csv_path, BENCHMARK_COLUMNS)
    for model in tqdm(models, desc="llama-bench"):
        output, code = run_llama_bench(model, llama_bench=binary, ngl=ngl, timeout=timeout)
        if code != 0:
            write_error_log(log_path, f"Failed {model.name} (code={code}): {output[:300]}")

        pp = parse_llama_bench_tps(output, "pp512") or parse_llama_bench_tps(output, str(BENCHMARK_PP_TOKENS))
        tg = parse_llama_bench_tps(output, "tg128") or parse_llama_bench_tps(output, str(BENCHMARK_TG_TOKENS))

        append_csv(csv_path, BENCHMARK_COLUMNS, {
            "timestamp": timestamp_iso(),
            "arquivo": str(model.relative_to(base)),
            "tamanho_gib": round(file_size_gib(model), 3),
            "backend": _detect_backend(output),
            "pp512_tps": pp if pp is not None else "",
            "tg128_tps": tg if tg is not None else "",
            "saida_bruta": output.replace("\n", "\\n")[:8000],
        })
    return csv_path


rodar_benchmark = run_throughput_benchmark
