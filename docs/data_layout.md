# Layout de dados — LLM Performance Lab

Este documento descreve a estrutura esperada de **modelos GGUF** e **datasets JSONL**.
O código busca arquivos **recursivamente** a partir das pastas raiz `models/` e `datasets/`.

| Tipo | Padrão de busca |
|------|-----------------|
| Modelos | `models/**/*.gguf` |
| Datasets | `datasets/**/*.jsonl` |

Qualquer subpasta dentro de `models/` ou `datasets/` é válida.

---

## Modelos GGUF

Coloque cada família de modelo em sua própria subpasta. Exemplo com Qwen2.5-3B-Instruct:

```
LLM-Performance-Lab/
└── models/
    └── Qwen2.5-3B-Instruct/
        ├── Qwen2.5-3B-Instruct-F16.gguf
        ├── Qwen2.5-3B-Instruct-Q2_K.gguf
        ├── Qwen2.5-3B-Instruct-Q3_K_M.gguf
        ├── Qwen2.5-3B-Instruct-Q4_K_M.gguf
        ├── Qwen2.5-3B-Instruct-Q5_K_M.gguf
        ├── Qwen2.5-3B-Instruct-Q6_K.gguf
        └── Qwen2.5-3B-Instruct-Q8_0.gguf
```

### Convenções

- **Uma pasta por modelo base** (ex.: `Qwen2.5-3B-Instruct/`, `Llama-3.2-1B/`).
- **Um arquivo `.gguf` por nível de quantização** — F16, Q2_K, Q4_K_M, etc.
- Nomes descritivos ajudam na leitura dos CSVs de resultado.
- Não é necessário achatar tudo em `models/` — subpastas são esperadas.

### Cópia a partir de ambiente antigo

```bash
mkdir -p models datasets results

cp -r "/caminho/antigo/Modelos/modelos-qtz-4me/Qwen2.5-3B-Instruct" models/
```

---

## Datasets JSONL

Organize por **grupo** (benchmark, domínio ou fonte). Exemplo completo:

```
LLM-Performance-Lab/
└── datasets/
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
        │   ├── train.jsonl
        │   └── test.jsonl
        ├── arithmetic/
        │   ├── arithmetic_2da.validation.jsonl
        │   ├── arithmetic_2ds.validation.jsonl
        │   └── ...
        ├── logiqa/
        ├── coqa/
        ├── triviaqa/
        └── wikitext/
            └── wikitext-2-raw-v1/
                ├── train.jsonl
                ├── validation.jsonl
                └── test.jsonl
```

### Cópia a partir de ambiente antigo

```bash
mkdir -p models datasets results

cp -r "/caminho/antigo/Datasets/"* datasets/
```

---

## Formato JSONL (avaliação de qualidade)

Um objeto JSON por linha. Campos suportados (use os que existirem no seu dataset):

```json
{
  "pergunta": "Qual a capital do Brasil?",
  "alternativas": {
    "A": "São Paulo",
    "B": "Brasília",
    "C": "Rio de Janeiro",
    "D": "Salvador"
  },
  "resposta": "B"
}
```

Aliases aceitos:

| Função | Campos alternativos |
|--------|---------------------|
| Pergunta | `question`, `enunciado`, `prompt`, `input` |
| Alternativas | `choices`, `options` (lista ou dict) |
| Resposta | `answer`, `label`, `gold`, `resposta_correta`, `correct` |

Datasets sem alternativas (ex.: geração livre) também podem ser usados; a métrica `acertou` compara texto normalizado.

---

## Resultados e cache

```
LLM-Performance-Lab/
├── results/
│   ├── benchmark/     # CSV de llama-bench
│   ├── quality/       # CSV de avaliação de qualidade
│   └── logs/          # Logs de erro
└── cache/
    └── llama.cpp/     # Clone e build do llama.cpp
```

Os scripts criam subpastas automaticamente se não existirem.

---

## Verificação rápida

Antes de rodar benchmark ou avaliação, confira se os dados estão no lugar:

```bash
python scripts/00_check_data.py
```

Mensagens quando faltam dados:

- **Sem modelos:** `Não encontrei modelos GGUF. Coloque os arquivos em models/<nome-do-modelo>/*.gguf`
- **Sem datasets:** `Não encontrei datasets JSONL. Coloque os arquivos em datasets/<grupo>/*.jsonl`
