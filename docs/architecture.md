# LLM Performance Lab — Architecture

## Overview

LLM Performance Lab is a modular, extensible benchmarking framework for quantized GGUF models using [llama.cpp](https://github.com/ggerganov/llama.cpp).

## Design Principles

- **SOLID**: Single-responsibility modules, open for extension via registries
- **Reproducibility**: Every run saves environment metadata (OS, CPU, GPU, llama.cpp commit, config)
- **Incremental results**: CSV outputs are append-only with resume support
- **Backward compatibility**: Legacy scripts (`scripts/02_*.py`) remain functional

## Module Structure

```
src/
├── config.py           # YAML configuration loader
├── core/
│   ├── registry.py     # Generic Registry[T]
│   ├── experiment.py   # Experiment + EnvironmentInfo
│   └── benchmark_runner.py  # BaseBenchmark + BenchmarkRunner
├── llm/
│   ├── llama_runner.py # llama-cli subprocess wrapper
│   └── model_loader.py # GGUF discovery + metadata
├── datasets/
│   ├── dataset_loader.py
│   └── registry.py     # DatasetRegistry
├── evaluators/
│   ├── factory.py      # EvaluatorFactory
│   ├── multiple_choice.py
│   ├── arithmetic.py
│   ├── qa.py
│   └── generation.py   # BLEU/ROUGE stub
├── metrics/
├── benchmark/          # Registered benchmarks
├── reports/
└── visualization/
```

## Benchmark Registry

All benchmarks implement `BaseBenchmark.run(experiment) -> ExperimentResult`.

| Benchmark | Status | Description |
|-----------|--------|-------------|
| `quality` | ✓ | Dataset evaluation with evaluator factory |
| `inference` | ✓ | Single-prompt latency |
| `throughput` | ✓ | llama-bench tokens/s |
| `latency` | ✓ | Alias for inference |
| `memory` | ✓ | RSS snapshot during inference |
| `quantization` | ✓ | Quant level comparison |
| `gpu` | Planned | GPU-specific metrics |
| `energy` | Planned | Power consumption |
| `rag` | Planned | Retrieval-augmented generation |
| `multimodal` | Planned | Vision/audio models |
| `long_context` | Planned | Context scaling tests |

## Pipeline

```
run.py
  → load YAML config
  → discover models (models/**/*.gguf)
  → discover datasets (datasets/**/*.jsonl)
  → BenchmarkRunner.run([...])
  → generate reports (CSV, Markdown, LaTeX)
  → generate figures (matplotlib)
```

## Extension Points

1. **New benchmark**: Subclass `BaseBenchmark`, register with `BenchmarkRegistry.register`
2. **New dataset**: Drop JSONL in `datasets/<family>/`, auto-detected by path
3. **New evaluator**: Subclass `BaseEvaluator`, register in `EvaluatorRegistry`
4. **New metric**: Add module under `src/metrics/`
