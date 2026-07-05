"""Integration tests (lightweight, no inference)."""

from pathlib import Path

from src.config import load_config, ensure_directories
from src.core.benchmark_runner import BenchmarkRunner
from src.core.experiment import Experiment
import src.benchmark  # noqa: F401


def test_config_load():
    cfg = load_config()
    assert cfg.models_dir.name == "models"
    assert cfg.context_size > 0


def test_benchmark_registry():
    names = BenchmarkRunner.available()
    assert "quality" in names
    assert "throughput" in names
    assert "inference" in names


def test_experiment_metadata(tmp_path):
    cfg = load_config()
    cfg.results_dir = tmp_path / "results"
    ensure_directories(cfg)
    exp = Experiment(cfg)
    meta = exp.save_metadata()
    assert meta.exists()
