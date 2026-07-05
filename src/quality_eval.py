"""Avaliação de qualidade de modelos GGUF em datasets JSONL."""

from __future__ import annotations

from pathlib import Path

from tqdm import tqdm

from .config import (
    DATASET_DIR,
    DEFAULT_ITEMS_POR_DATASET,
    DEFAULT_MAX_TOKENS,
    DEFAULT_NGL,
    DEFAULT_TIMEOUT,
    MODEL_DIR,
    RESULT_LOGS_DIR,
    RESULT_QUALITY_DIR,
    garantir_diretorios,
)
from .datasets import (
    acertou,
    carregar_jsonl,
    extrair_alternativa,
    montar_prompt,
    obter_resposta_esperada,
)
from .llama_runner import rodar_llama
from .utils import acrescentar_csv, chaves_processadas_csv, timestamp_iso

COLUNAS_QUALITY = [
    "timestamp",
    "modelo",
    "dataset",
    "item_idx",
    "resposta_esperada",
    "resposta_modelo",
    "alternativa_extraida",
    "acertou",
    "tempo_s",
    "erro",
]


def avaliar_qualidade(
    modelos_dir: Path | None = None,
    datasets_dir: Path | None = None,
    saida_csv: Path | None = None,
    *,
    itens_por_dataset: int = DEFAULT_ITEMS_POR_DATASET,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    ngl: int = DEFAULT_NGL,
    context_size: int | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    limit_models: int | None = None,
    limit_datasets: int | None = None,
    model_glob: str | None = None,
    results_dir: Path | None = None,
) -> Path:
    """
    Avalia qualidade percorrendo modelos e datasets.

    Salva CSV incrementalmente a cada item. Retoma execução se o CSV existir.
    """
    from .validacao import obter_datasets, obter_modelos, validar_datasets, validar_modelos

    garantir_diretorios()
    base_modelos = modelos_dir or MODEL_DIR
    base_datasets = datasets_dir or DATASET_DIR
    quality_dir = (results_dir / "quality") if results_dir else RESULT_QUALITY_DIR
    csv_path = saida_csv or (quality_dir / "quality_resultados.csv")
    logs_dir = (results_dir / "logs") if results_dir else RESULT_LOGS_DIR
    log_path = logs_dir / "quality_erros.log"

    validar_modelos(base_modelos, sair_se_vazio=True)
    validar_datasets(base_datasets, sair_se_vazio=True)

    modelos = obter_modelos(base_modelos, limit=limit_models, model_glob=model_glob)
    datasets = obter_datasets(base_datasets, limit=limit_datasets)

    processados = chaves_processadas_csv(csv_path, ["modelo", "dataset", "item_idx"])

    for modelo in tqdm(modelos, desc="Modelos"):
        nome_modelo = str(modelo.relative_to(base_modelos))

        for dataset_path in datasets:
            nome_dataset = str(dataset_path.relative_to(base_datasets))
            itens = carregar_jsonl(dataset_path, limite=itens_por_dataset)

            for idx, item in enumerate(itens):
                chave = (nome_modelo, nome_dataset, str(idx))
                if chave in processados:
                    continue

                resposta_esperada = obter_resposta_esperada(item)
                prompt = montar_prompt(item)
                erro = ""
                resposta_modelo = ""
                alternativa = ""
                acerto = False
                tempo_s = 0.0

                resultado = rodar_llama(
                    modelo,
                    prompt,
                    max_tokens=max_tokens,
                    ngl=ngl,
                    context_size=context_size,
                    timeout=timeout,
                    log_erros=log_path,
                )
                tempo_s = resultado.tempo_s

                if resultado.sucesso:
                    resposta_modelo = resultado.resposta
                    alternativa = extrair_alternativa(resposta_modelo)
                    acerto = acertou(resposta_modelo, resposta_esperada)
                else:
                    erro = resultado.erro or f"exit={resultado.returncode}"
                    if resultado.timeout:
                        erro = f"TIMEOUT: {erro}"

                acrescentar_csv(
                    csv_path,
                    COLUNAS_QUALITY,
                    {
                        "timestamp": timestamp_iso(),
                        "modelo": nome_modelo,
                        "dataset": nome_dataset,
                        "item_idx": idx,
                        "resposta_esperada": resposta_esperada,
                        "resposta_modelo": resposta_modelo[:2000],
                        "alternativa_extraida": alternativa,
                        "acertou": acerto,
                        "tempo_s": tempo_s,
                        "erro": erro[:500],
                    },
                )
                processados.add(chave)

    return csv_path
