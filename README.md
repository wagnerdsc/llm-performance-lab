# LLM Performance Lab

Laboratório para **quantização**, **benchmark de inferência** e **avaliação de qualidade** de modelos GGUF com [llama.cpp](https://github.com/ggerganov/llama.cpp).

Projeto migrado do notebook Colab `Quantization_GPU_Organizado.ipynb` para execução local no Lightning Studio — sem dependência de Google Drive ou `/content/drive`.

Documentação detalhada de pastas: [`docs/data_layout.md`](docs/data_layout.md).

## Estrutura do projeto

```
LLM-Performance-Lab/
├── notebooks/          # Notebooks exploratórios
├── src/                # Módulos Python reutilizáveis
├── scripts/            # Scripts de execução
├── docs/               # Documentação (layout de dados)
├── models/             # Modelos GGUF (busca: **/*.gguf)
├── datasets/           # Datasets JSONL (busca: **/*.jsonl)
├── results/            # Saídas incrementais (CSV + logs)
│   ├── benchmark/
│   ├── quality/
│   └── logs/
└── cache/              # llama.cpp clonado e compilado
```

## Setup

```bash
cd LLM-Performance-Lab

# Dependências Python
pip install -r requirements.txt

# Compilar llama.cpp (CUDA se GPU disponível, senão CPU)
bash scripts/01_setup_llama_cpp.sh
```

## Preparar modelos e datasets

Crie as pastas e copie os dados do ambiente anterior (Colab, Drive local, etc.):

```bash
mkdir -p models datasets results

# Exemplo de cópia vindo do ambiente antigo
cp -r "/caminho/antigo/Modelos/modelos-qtz-4me/Qwen2.5-3B-Instruct" models/
cp -r "/caminho/antigo/Datasets/"* datasets/
```

### Onde colocar modelos GGUF

Busca recursiva: `models/**/*.gguf`

```
models/
└── Qwen2.5-3B-Instruct/
    ├── Qwen2.5-3B-Instruct-F16.gguf
    ├── Qwen2.5-3B-Instruct-Q2_K.gguf
    ├── Qwen2.5-3B-Instruct-Q3_K_M.gguf
    ├── Qwen2.5-3B-Instruct-Q4_K_M.gguf
    ├── Qwen2.5-3B-Instruct-Q5_K_M.gguf
    ├── Qwen2.5-3B-Instruct-Q6_K.gguf
    └── Qwen2.5-3B-Instruct-Q8_0.gguf
```

Qualquer subpasta em `models/` pode conter arquivos `.gguf`.

### Onde colocar datasets

Busca recursiva: `datasets/**/*.jsonl`

```
datasets/
├── enem/
│   ├── 2022.jsonl
│   ├── 2023.jsonl
│   └── 2024.jsonl
├── bbq/
│   ├── Physical_appearance.jsonl
│   ├── Gender_identity.jsonl
│   └── Race_ethnicity.jsonl
└── poetav2/
    ├── gsm8k/
    ├── arithmetic/
    ├── logiqa/
    ├── coqa/
    ├── triviaqa/
    └── wikitext/
        └── wikitext-2-raw-v1/
            ├── train.jsonl
            ├── validation.jsonl
            └── test.jsonl
```

Formato JSONL (um JSON por linha) — ver [`docs/data_layout.md`](docs/data_layout.md).

## Verificar dados (sem inferência)

```bash
python scripts/00_check_data.py
```

Lista quantidade de GGUF e JSONL, primeiros arquivos, tamanho total dos modelos em GB e status de `results/`, `cache/` e `logs/`.

## Exemplos de execução

Teste rápido (1 modelo, 1 dataset, 3 itens):

```bash
python scripts/00_check_data.py

python scripts/02_benchmark_models.py --limit-models 1

python scripts/03_quality_eval.py \
  --limit-models 1 \
  --limit-datasets 1 \
  --limit-items 3 \
  --max-tokens 8
```

Execução completa:

```bash
python scripts/02_benchmark_models.py

python scripts/03_quality_eval.py --limit-items 50 --ngl 999
```

## Parâmetros CLI comuns

| Parâmetro | Descrição |
|-----------|-----------|
| `--models-dir` | Raiz dos GGUF (padrão: `models/`) |
| `--datasets-dir` | Raiz dos JSONL (padrão: `datasets/`) |
| `--results-dir` | Raiz de saídas (padrão: `results/`) |
| `--limit-models` | Limita quantidade de modelos |
| `--limit-datasets` | Limita quantidade de datasets |
| `--limit-items` | Itens por dataset |
| `--max-tokens` | Tokens gerados por prompt |
| `--ngl` | Camadas na GPU (padrão: 999) |
| `--context-size` | Tamanho de contexto `-c` (padrão: 4096) |

## Benchmark de performance

Executa `llama-bench` em todos os GGUF encontrados em `models/**/*.gguf`:

```bash
python scripts/02_benchmark_models.py --models-dir models/ --results-dir results/
```

Resultado incremental em `results/benchmark/benchmark_resultados.csv`:

| Coluna | Descrição |
|--------|-----------|
| arquivo | Caminho relativo do GGUF |
| tamanho_gib | Tamanho em GiB |
| backend | cuda / cpu |
| pp512_tps | Tokens/s (prompt processing, 512) |
| tg128_tps | Tokens/s (text generation, 128) |
| saida_bruta | Saída completa do llama-bench |

Se não houver modelos:

```
Não encontrei modelos GGUF. Coloque os arquivos em models/<nome-do-modelo>/*.gguf
```

## Avaliação de qualidade

```bash
python scripts/03_quality_eval.py --datasets-dir datasets/ --results-dir results/
```

- Salva **uma linha por item** em `results/quality/quality_resultados.csv`
- Erros em `results/logs/quality_erros.log`
- **Retoma automaticamente** se o CSV já existir

Se não houver datasets:

```
Não encontrei datasets JSONL. Coloque os arquivos em datasets/<grupo>/*.jsonl
```

## Configuração

Caminhos centralizados em `src/config.py`:

- `BASE_DIR`, `MODEL_DIR`, `DATASET_DIR`, `RESULT_DIR`, `CACHE_DIR`
- `LLAMA_CPP_DIR`, `LLAMA_CLI`, `LLAMA_BENCH`

## GPU

Por padrão usa `-ngl 999` para offload máximo de camadas na GPU NVIDIA. Ajuste com `--ngl` nos scripts.

## Notas

- Resultados são salvos de forma **incremental** — interrupções não apagam progresso.
- Não há dependência de Colab, Google Drive ou caminhos `/content/drive`.
- Para quantização Hugging Face → GGUF, use notebooks em `notebooks/` ou ferramentas do llama.cpp.
