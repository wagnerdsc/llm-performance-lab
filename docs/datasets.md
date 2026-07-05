# Datasets

Datasets are discovered recursively: `datasets/**/*.jsonl`

See also: [data_layout.md](data_layout.md) (legacy Portuguese layout doc).

## Registered Families

| Family | Evaluator | Metrics |
|--------|-----------|---------|
| `bbq` | MultipleChoice | Accuracy |
| `enem` | MultipleChoice | Accuracy |
| `logiqa` | MultipleChoice | Accuracy |
| `gsm8k` | Arithmetic | Numeric match |
| `arithmetic` | Arithmetic | Numeric match |
| `triviaqa` | QuestionAnswering | Exact Match, F1 |
| `coqa` | QuestionAnswering | Exact Match, F1 |
| `wikitext` | — | Skipped (generation-only) |

## JSONL Format

Each line is a JSON object. Required fields vary by family — see evaluators for details.

## Adding a Dataset

1. Create `datasets/<your_benchmark>/<split>.jsonl`
2. Optionally register family in `src/datasets/registry.py`
3. If new task type, add evaluator in `src/evaluators/` and register in factory

No code changes needed if the dataset matches an existing family pattern.
