# Adding Datasets

## Step 1: Prepare JSONL

One JSON object per line. Example for multiple-choice:

```json
{"question": "What is 2+2?", "alternatives": ["3", "4", "5", "6"], "label": "B"}
```

## Step 2: Place in datasets directory

```bash
mkdir -p datasets/my_benchmark
cp data/test.jsonl datasets/my_benchmark/
```

## Step 3: Match an existing family (recommended)

If your dataset resembles ENEM, BBQ, GSM8K, etc., place it under a matching path:

```
datasets/enem/2025.jsonl
datasets/bbq/my_category.jsonl
```

## Step 4: Custom evaluator (optional)

For new task types:

1. Create `src/evaluators/my_task.py` subclassing `BaseEvaluator`
2. Register in `src/evaluators/factory.py`:

```python
EvaluatorRegistry.register("my_task", MyTaskEvaluator)
```

3. Register dataset family in `src/datasets/registry.py`

## Step 5: Run quality benchmark

```bash
python run.py --benchmark quality --limit-datasets 1 --limit-items 10
```

Results append incrementally to `results/quality/quality_resultados.csv`.
