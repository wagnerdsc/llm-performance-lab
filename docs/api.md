# API Reference

## CLI

```bash
python run.py [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--config PATH` | YAML config file |
| `--benchmark NAME` | Run specific benchmark (repeatable) |
| `--all` | Run all registered benchmarks |
| `--list` | List available benchmarks |
| `--models-dir`, `--datasets-dir`, `--results-dir` | Override paths |
| `--limit-models`, `--limit-datasets`, `--limit-items` | Limit scope |
| `--model-glob` | Filter models by glob |
| `--ngl` | GPU layers |
| `--no-reports`, `--no-figures` | Skip report generation |

## Python API

```python
from src.config import load_config
from src.core.experiment import Experiment
from src.core.benchmark_runner import BenchmarkRunner
import src.benchmark  # registers benchmarks

cfg = load_config("configs/benchmark.yaml")
experiment = Experiment(cfg)
runner = BenchmarkRunner(experiment)
results = runner.run(["quality", "throughput"])
```

## Registries

```python
from src.core.benchmark_runner import BenchmarkRegistry
from src.evaluators.factory import EvaluatorRegistry
from src.datasets.registry import DatasetRegistry

BenchmarkRegistry.list()
EvaluatorRegistry.get("enem")
DatasetRegistry.list()
```

## Legacy Scripts

Existing scripts remain supported:

- `scripts/00_check_data.py`
- `scripts/02_benchmark_models.py`
- `scripts/03_quality_eval.py`
