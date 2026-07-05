"""Benchmark de performance com llama-bench."""

from __future__ import annotations

import subprocess
from pathlib import Path

from tqdm import tqdm

from .config import (
    BENCHMARK_PP_TOKENS,
    BENCHMARK_TG_TOKENS,
    DEFAULT_NGL,
    DEFAULT_TIMEOUT,
    LLAMA_BENCH,
    MODEL_DIR,
    RESULT_BENCHMARK_DIR,
    garantir_diretorios,
)
from .utils import (
    acrescentar_csv,
    escrever_log_erro,
    inicializar_csv,
    parsear_tps_llama_bench,
    tamanho_gib,
    timestamp_iso,
)

COLUNAS_BENCHMARK = [
    "timestamp",
    "arquivo",
    "tamanho_gib",
    "backend",
    "pp512_tps",
    "tg128_tps",
    "saida_bruta",
]


def _detectar_backend(saida: str) -> str:
    saida_lower = saida.lower()
    if "cuda" in saida_lower or "cublas" in saida_lower or "gpu" in saida_lower:
        return "cuda"
    if "metal" in saida_lower:
        return "metal"
    if "vulkan" in saida_lower:
        return "vulkan"
    return "cpu"


def executar_llama_bench(
    modelo: Path,
    *,
    llama_bench: Path | None = None,
    ngl: int = DEFAULT_NGL,
    context_size: int | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> tuple[str, int]:
    """Executa llama-bench para um modelo GGUF."""
    from .config import DEFAULT_CONTEXT_SIZE

    binario = llama_bench or LLAMA_BENCH
    ctx = context_size if context_size is not None else DEFAULT_CONTEXT_SIZE
    comando = [
        str(binario),
        "-m", str(modelo),
        "-ngl", str(ngl),
        "-c", str(ctx),
        "-p", str(BENCHMARK_PP_TOKENS),
        "-n", str(BENCHMARK_TG_TOKENS),
    ]
    try:
        proc = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        saida = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return saida.strip(), proc.returncode
    except subprocess.TimeoutExpired:
        return f"TIMEOUT após {timeout}s", -1
    except OSError as exc:
        return str(exc), 127


def rodar_benchmark(
    modelos_dir: Path | None = None,
    saida_csv: Path | None = None,
    *,
    llama_bench: Path | None = None,
    ngl: int = DEFAULT_NGL,
    context_size: int | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    limit_models: int | None = None,
    model_glob: str | None = None,
    results_dir: Path | None = None,
) -> Path:
    """
    Executa llama-bench em todos os GGUF e salva CSV incremental.

    Retorna caminho do CSV gerado.
    """
    from .validacao import obter_modelos, validar_modelos

    garantir_diretorios()
    base_modelos = modelos_dir or MODEL_DIR
    benchmark_dir = (results_dir / "benchmark") if results_dir else RESULT_BENCHMARK_DIR
    csv_path = saida_csv or (benchmark_dir / "benchmark_resultados.csv")
    logs_dir = (results_dir / "logs") if results_dir else RESULT_BENCHMARK_DIR.parent / "logs"
    log_path = logs_dir / "benchmark_erros.log"

    validar_modelos(base_modelos, sair_se_vazio=True)
    modelos = obter_modelos(base_modelos, limit=limit_models, model_glob=model_glob)

    binario = llama_bench or LLAMA_BENCH
    if not binario.is_file():
        escrever_log_erro(log_path, f"llama-bench não encontrado: {binario}")
        inicializar_csv(csv_path, COLUNAS_BENCHMARK)
        return csv_path

    inicializar_csv(csv_path, COLUNAS_BENCHMARK)

    for modelo in tqdm(modelos, desc="llama-bench"):
        saida, codigo = executar_llama_bench(
            modelo,
            llama_bench=binario,
            ngl=ngl,
            context_size=context_size,
            timeout=timeout,
        )
        if codigo != 0:
            escrever_log_erro(log_path, f"Falha {modelo.name} (code={codigo}): {saida[:300]}")

        pp_tps = parsear_tps_llama_bench(saida, str(BENCHMARK_PP_TOKENS))
        tg_tps = parsear_tps_llama_bench(saida, str(BENCHMARK_TG_TOKENS))

        acrescentar_csv(
            csv_path,
            COLUNAS_BENCHMARK,
            {
                "timestamp": timestamp_iso(),
                "arquivo": str(modelo.relative_to(base_modelos)),
                "tamanho_gib": round(tamanho_gib(modelo), 3),
                "backend": _detectar_backend(saida),
                "pp512_tps": pp_tps if pp_tps is not None else "",
                "tg128_tps": tg_tps if tg_tps is not None else "",
                "saida_bruta": saida.replace("\n", "\\n")[:8000],
            },
        )

    return csv_path
