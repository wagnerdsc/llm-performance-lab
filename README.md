# LLM Performance Lab

**Open-source, modular benchmarking framework for quantized LLMs with llama.cpp.**

Compare GGUF models across quality, speed, throughput, latency, memory, and quantization — with reproducible reports for research and publication.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Features

- **Modular architecture** — registries for benchmarks, datasets, evaluators, models
- **Reproducible** — saves environment metadata (OS, CPU, GPU, llama.cpp commit, config)
- **Incremental CSV** — resume interrupted runs without losing progress
- **Multiple evaluators** — multiple-choice, arithmetic, QA (EM/F1), generation (stub)
- **Auto-reports** — CSV, Markdown, LaTeX + matplotlib figures
- **YAML configuration** — `configs/default.yaml`, `cpu.yaml`, `gpu.yaml`
- **Backward compatible** — legacy scripts still work

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Build llama.cpp
bash scripts/01_setup_llama_cpp.sh

# Add models to models/ and datasets to datasets/

# Verify data
python scripts/00_check_data.py

# Run benchmarks
python run.py --benchmark quality --limit-models 1 --limit-items 5
python run.py --benchmark throughput --model-glob '*Q4_K_M*'
python run.py --all --limit-models 1   # all benchmarks, 1 model
```

## CLI

```bash
python run.py --list                          # available benchmarks
python run.py --benchmark quality             # quality evaluation
python run.py --benchmark inference           # latency
python run.py --benchmark throughput          # llama-bench t/s
python run.py --benchmark memory              # RSS usage
python run.py --benchmark quantization        # quant comparison
python run.py --all                           # run everything
python run.py --config configs/gpu.yaml       # GPU profile
```

## Project Structure

```
LLM-Performance-Lab/
├── run.py                  # Main CLI pipeline
├── configs/                # YAML configuration
├── docs/                   # Documentation
├── models/                 # GGUF models (models/**/*.gguf)
├── datasets/               # JSONL datasets (datasets/**/*.jsonl)
├── results/                # Incremental CSV outputs
├── reports/                # Generated reports
├── figures/                # Generated plots
├── scripts/                # Legacy + setup scripts
├── src/                    # Framework source code
└── tests/                  # Unit + integration tests
```

## Benchmarks

| Benchmark | Command | Output |
|-----------|---------|--------|
| Quality | `--benchmark quality` | `results/quality/quality_resultados.csv` |
| Throughput | `--benchmark throughput` | `results/benchmark/benchmark_resultados.csv` |
| Inference/Latency | `--benchmark inference` | `results/benchmark/inference_latency.csv` |
| Memory | `--benchmark memory` | `results/benchmark/memory_usage.csv` |
| Quantization | `--benchmark quantization` | `results/benchmark/quantization_comparison.csv` |

## Configuration

Edit `configs/default.yaml` or create a custom profile:

```yaml
models_dir: models
datasets_dir: datasets
context_size: 4096
gpu_layers: 999
timeout: 600
items_per_dataset: 50
```

## Documentation

- [Architecture](docs/architecture.md)
- [Adding Models](docs/adding_models.md)
- [Adding Datasets](docs/adding_datasets.md)
- [API Reference](docs/api.md)
- [Data Layout](docs/data_layout.md)

## Testing

```bash
pytest tests/ -v
python -m py_compile run.py src/**/*.py
```

## Citation

If you use LLM Performance Lab in research, please cite the repository and include the reproducibility metadata from `results/<run_id>/metadata.json`.

## License

MIT — see [LICENSE](LICENSE).
