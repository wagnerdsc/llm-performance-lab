#!/usr/bin/env python3
"""LLM Performance Lab — unified benchmark pipeline CLI."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import LabConfig, load_config, ensure_directories  # noqa: E402
from src.core.benchmark_runner import BenchmarkRunner  # noqa: E402
from src.core.experiment import Experiment  # noqa: E402
from src.llm.model_loader import discover_models  # noqa: E402
from src.datasets.registry import discover_datasets  # noqa: E402
import src.benchmark  # noqa: F401 — register benchmarks
from src.reports.csv_report import generate_csv_report  # noqa: E402
from src.reports.markdown_report import generate_markdown_report  # noqa: E402
from src.reports.latex_report import generate_latex_report  # noqa: E402
from src.visualization.plots import generate_all_plots  # noqa: E402


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LLM Performance Lab — reproducible GGUF benchmarking framework",
    )
    parser.add_argument("--config", type=Path, default=None, help="YAML config file")
    parser.add_argument("--benchmark", action="append", dest="benchmarks", help="Benchmark to run")
    parser.add_argument("--all", action="store_true", help="Run all registered benchmarks")
    parser.add_argument("--list", action="store_true", help="List available benchmarks")
    parser.add_argument("--models-dir", type=Path, default=None)
    parser.add_argument("--datasets-dir", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=None)
    parser.add_argument("--limit-models", type=int, default=None)
    parser.add_argument("--limit-datasets", type=int, default=None)
    parser.add_argument("--limit-items", type=int, default=None)
    parser.add_argument("--model-glob", type=str, default=None)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--ngl", type=int, default=None, help="GPU layers (-ngl)")
    parser.add_argument("--context-size", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=None)
    parser.add_argument("--no-reports", action="store_true")
    parser.add_argument("--no-figures", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def apply_cli_overrides(cfg: LabConfig, args: argparse.Namespace) -> None:
    overrides = {
        "models_dir": args.models_dir,
        "datasets_dir": args.datasets_dir,
        "results_dir": args.results_dir,
        "limit_models": args.limit_models,
        "limit_datasets": args.limit_datasets,
        "limit_items": args.limit_items,
        "model_glob": args.model_glob,
        "max_tokens": args.max_tokens,
        "gpu_layers": args.ngl,
        "context_size": args.context_size,
        "timeout": args.timeout,
    }
    for key, value in overrides.items():
        if value is not None:
            setattr(cfg, key, value)
    if args.limit_items is not None:
        cfg.items_per_dataset = args.limit_items


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.list:
        print("Available benchmarks:")
        for name in BenchmarkRunner.available():
            print(f"  - {name}")
        return 0

    cfg = load_config(args.config)
    apply_cli_overrides(cfg, args)
    ensure_directories(cfg)

    models = discover_models(cfg.models_dir, limit=cfg.limit_models, model_glob=cfg.model_glob)
    datasets = discover_datasets(cfg.datasets_dir, limit=cfg.limit_datasets)
    logging.info("Discovered %d models, %d datasets", len(models), len(datasets))

    if not models:
        logging.error("No GGUF models found in %s", cfg.models_dir)
        return 1

    benchmarks = BenchmarkRunner.available() if args.all else (args.benchmarks or cfg.benchmarks)
    if not benchmarks:
        benchmarks = ["quality"]

    experiment = Experiment(cfg, name="run")
    runner = BenchmarkRunner(experiment)
    results = runner.run(benchmarks)

    if cfg.generate_reports and not args.no_reports:
        generate_csv_report(cfg.results_dir, cfg.reports_dir)
        md = generate_markdown_report(cfg.results_dir, cfg.reports_dir)
        generate_latex_report(cfg.results_dir, cfg.reports_dir)
        logging.info("Reports saved to %s", md.parent)

    if cfg.generate_figures and not args.no_figures:
        plots = generate_all_plots(cfg.results_dir, cfg.figures_dir)
        logging.info("Generated %d figures in %s", len(plots), cfg.figures_dir)

    for r in results:
        print(f"  {r.benchmark}: {r.csv_path} ({r.row_count} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
