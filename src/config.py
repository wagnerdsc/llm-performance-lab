"""Central configuration for LLM Performance Lab."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIGS_DIR = BASE_DIR / "configs"

# Legacy path constants (backward compatibility)
MODEL_DIR = BASE_DIR / "models"
DATASET_DIR = BASE_DIR / "datasets"
RESULT_DIR = BASE_DIR / "results"
CACHE_DIR = BASE_DIR / "cache"
RESULT_BENCHMARK_DIR = RESULT_DIR / "benchmark"
RESULT_QUALITY_DIR = RESULT_DIR / "quality"
RESULT_LOGS_DIR = RESULT_DIR / "logs"
LLAMA_CPP_DIR = CACHE_DIR / "llama.cpp"
LLAMA_CLI = LLAMA_CPP_DIR / "build" / "bin" / "llama-cli"
LLAMA_BENCH = LLAMA_CPP_DIR / "build" / "bin" / "llama-bench"

DEFAULT_NGL = 999
DEFAULT_TIMEOUT = 600
DEFAULT_MAX_TOKENS = 256
DEFAULT_CONTEXT_SIZE = 4096
DEFAULT_TEMPERATURE = 0.0
DEFAULT_ITEMS_POR_DATASET = 50
BENCHMARK_PP_TOKENS = 512
BENCHMARK_TG_TOKENS = 128


@dataclass
class LabConfig:
    """Typed configuration loaded from YAML."""

    models_dir: Path = field(default_factory=lambda: MODEL_DIR)
    datasets_dir: Path = field(default_factory=lambda: DATASET_DIR)
    results_dir: Path = field(default_factory=lambda: RESULT_DIR)
    reports_dir: Path = field(default_factory=lambda: BASE_DIR / "reports")
    figures_dir: Path = field(default_factory=lambda: BASE_DIR / "figures")
    cache_dir: Path = field(default_factory=lambda: CACHE_DIR)

    context_size: int = DEFAULT_CONTEXT_SIZE
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    threads: int = -1
    gpu_layers: int = DEFAULT_NGL
    timeout: int = DEFAULT_TIMEOUT

    items_per_dataset: int = DEFAULT_ITEMS_POR_DATASET
    benchmark_pp_tokens: int = BENCHMARK_PP_TOKENS
    benchmark_tg_tokens: int = BENCHMARK_TG_TOKENS

    llama_cpp_dir: Path = field(default_factory=lambda: LLAMA_CPP_DIR)
    llama_cli: Path = field(default_factory=lambda: LLAMA_CLI)
    llama_bench: Path = field(default_factory=lambda: LLAMA_BENCH)

    limit_models: int | None = None
    limit_datasets: int | None = None
    limit_items: int | None = None
    model_glob: str | None = None

    benchmarks: list[str] = field(default_factory=lambda: ["quality", "inference"])
    generate_reports: bool = True
    generate_figures: bool = True
    save_metadata: bool = True

    @property
    def ngl(self) -> int:
        return self.gpu_layers

    def to_dict(self) -> dict[str, Any]:
        return {
            k: str(v) if isinstance(v, Path) else v
            for k, v in self.__dict__.items()
        }


def _resolve_path(base: Path, value: str | Path) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (base / p).resolve()


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(config_path: Path | str | None = None) -> LabConfig:
    """Load configuration from YAML with optional inheritance via 'extends'."""
    if config_path is None:
        config_path = CONFIGS_DIR / "default.yaml"
    path = Path(config_path)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve() if not path.exists() else path.resolve()
        if not path.exists():
            path = (CONFIGS_DIR / config_path).resolve()

    data: dict[str, Any] = {}
    if path.is_file():
        data = _load_yaml(path)
        if "extends" in data:
            parent_name = data.pop("extends")
            parent_path = path.parent / parent_name
            parent_data = _load_yaml(parent_path)
            parent_data.update(data)
            data = parent_data

    cfg = LabConfig()
    path_fields = {
        "models_dir", "datasets_dir", "results_dir", "reports_dir",
        "figures_dir", "cache_dir", "llama_cpp_dir", "llama_cli", "llama_bench",
    }
    for key, value in data.items():
        if not hasattr(cfg, key):
            continue
        if key in path_fields and value is not None:
            setattr(cfg, key, _resolve_path(BASE_DIR, value))
        else:
            setattr(cfg, key, value)
    return cfg


def ensure_directories(config: LabConfig | None = None) -> None:
    """Create standard output directories."""
    cfg = config or LabConfig()
    for path in (
        cfg.models_dir,
        cfg.datasets_dir,
        cfg.results_dir,
        cfg.reports_dir,
        cfg.figures_dir,
        cfg.cache_dir,
        cfg.results_dir / "benchmark",
        cfg.results_dir / "quality",
        cfg.results_dir / "logs",
    ):
        path.mkdir(parents=True, exist_ok=True)


def binary_exists(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


# Legacy alias
garantir_diretorios = ensure_directories
binario_existe = binary_exists
