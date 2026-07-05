"""Quality benchmark engine."""

from __future__ import annotations

from pathlib import Path

from tqdm import tqdm

from src.config import (
    DATASET_DIR,
    DEFAULT_ITEMS_POR_DATASET,
    DEFAULT_MAX_TOKENS,
    DEFAULT_NGL,
    DEFAULT_TIMEOUT,
    MODEL_DIR,
    RESULT_LOGS_DIR,
    RESULT_QUALITY_DIR,
    ensure_directories,
)
from src.datasets import (
    acertou,
    carregar_jsonl,
    dataset_suportado_qualidade,
    extrair_alternativa,
    montar_prompt,
    obter_resposta_esperada,
)
from src.evaluators.factory import EvaluatorFactory
from src.llm.llama_runner import run_llama
from src.utils.io import append_csv, processed_csv_keys, timestamp_iso

QUALITY_COLUMNS = [
    "timestamp", "modelo", "dataset", "item_idx",
    "resposta_esperada", "resposta_modelo", "alternativa_extraida",
    "acertou", "tempo_s", "erro", "metric", "score",
]

COLUNAS_QUALITY = QUALITY_COLUMNS


def run_quality_benchmark(
    models_dir: Path | None = None,
    datasets_dir: Path | None = None,
    output_csv: Path | None = None,
    *,
    items_per_dataset: int = DEFAULT_ITEMS_POR_DATASET,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    ngl: int = DEFAULT_NGL,
    context_size: int | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    limit_models: int | None = None,
    limit_datasets: int | None = None,
    model_glob: str | None = None,
    results_dir: Path | None = None,
) -> Path:
    """Run quality evaluation across models and datasets with incremental CSV."""
    from src.validacao import obter_datasets, obter_modelos, validar_datasets, validar_modelos

    ensure_directories()
    base_models = models_dir or MODEL_DIR
    base_datasets = datasets_dir or DATASET_DIR
    quality_dir = (results_dir / "quality") if results_dir else RESULT_QUALITY_DIR
    csv_path = output_csv or (quality_dir / "quality_resultados.csv")
    log_path = ((results_dir / "logs") if results_dir else RESULT_LOGS_DIR) / "quality_erros.log"

    validar_modelos(base_models, sair_se_vazio=True)
    validar_datasets(base_datasets, sair_se_vazio=True)

    models = obter_modelos(base_models, limit=limit_models, model_glob=model_glob)
    datasets = obter_datasets(base_datasets, limit=limit_datasets)
    processed = processed_csv_keys(csv_path, ["modelo", "dataset", "item_idx"])

    for model in tqdm(models, desc="Models"):
        model_name = str(model.relative_to(base_models))
        for dataset_path in datasets:
            dataset_name = str(dataset_path.relative_to(base_datasets))
            items = carregar_jsonl(dataset_path, limite=items_per_dataset)

            for idx, item in enumerate(items):
                key = (model_name, dataset_name, str(idx))
                if key in processed or not dataset_suportado_qualidade(dataset_path, item):
                    continue

                evaluator = EvaluatorFactory.create(dataset_path, item)
                expected = evaluator.get_expected(item, dataset_path)
                prompt = evaluator.build_prompt(item, dataset_path)

                result = run_llama(
                    model, prompt,
                    max_tokens=max_tokens, ngl=ngl,
                    context_size=context_size, timeout=timeout,
                    error_log=log_path,
                )

                response, error, correct, alt, metric, score = "", "", False, "", "", 0.0
                if result.success:
                    eval_result = evaluator.evaluate(result.response, item, dataset_path)
                    response = result.response
                    alt = extrair_alternativa(response)
                    correct = eval_result.correct
                    metric = eval_result.metric
                    score = eval_result.score
                else:
                    error = result.error or f"exit={result.returncode}"
                    if result.timeout:
                        error = f"TIMEOUT: {error}"

                append_csv(csv_path, QUALITY_COLUMNS, {
                    "timestamp": timestamp_iso(),
                    "modelo": model_name,
                    "dataset": dataset_name,
                    "item_idx": idx,
                    "resposta_esperada": expected,
                    "resposta_modelo": response[:2000].encode("utf-8", errors="replace").decode("utf-8"),
                    "alternativa_extraida": alt,
                    "acertou": correct,
                    "tempo_s": result.latency_s,
                    "erro": error[:500],
                    "metric": metric,
                    "score": score,
                })
                processed.add(key)
    return csv_path


avaliar_qualidade = run_quality_benchmark
