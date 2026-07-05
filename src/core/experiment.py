"""Experiment context and reproducibility metadata."""

from __future__ import annotations

import json
import logging
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil

from src.config import LabConfig

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentInfo:
    """Captured system and runtime metadata for reproducibility."""

    timestamp: str
    python_version: str
    platform_system: str
    platform_release: str
    cpu_model: str
    cpu_count: int
    ram_gb: float
    gpu_name: str
    llama_cpp_commit: str
    llama_cpp_build: str
    config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentResult:
    """Aggregated output from a benchmark run."""

    benchmark: str
    csv_path: Path | None = None
    metadata_path: Path | None = None
    row_count: int = 0
    extra: dict[str, Any] = field(default_factory=dict)


class Experiment:
    """Orchestrates a single benchmark experiment with reproducibility tracking."""

    def __init__(self, config: LabConfig, name: str = "experiment") -> None:
        self.config = config
        self.name = name
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.results_dir = config.results_dir / self.run_id
        self.reports_dir = config.reports_dir
        self.figures_dir = config.figures_dir
        self.environment = self._capture_environment()

    def _capture_environment(self) -> EnvironmentInfo:
        gpu_name = "none"
        try:
            proc = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                gpu_name = proc.stdout.strip().split("\n")[0]
        except (OSError, subprocess.TimeoutExpired):
            pass

        llama_commit = ""
        llama_build = ""
        llama_dir = self.config.llama_cpp_dir
        if (llama_dir / ".git").is_dir():
            try:
                proc = subprocess.run(
                    ["git", "-C", str(llama_dir), "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                llama_commit = proc.stdout.strip()
            except OSError:
                pass
        if self.config.llama_cli.is_file():
            llama_build = str(self.config.llama_cli)

        return EnvironmentInfo(
            timestamp=datetime.now(timezone.utc).isoformat(),
            python_version=sys.version.split()[0],
            platform_system=platform.system(),
            platform_release=platform.release(),
            cpu_model=platform.processor() or "unknown",
            cpu_count=psutil.cpu_count(logical=True) or 0,
            ram_gb=round(psutil.virtual_memory().total / (1024**3), 2),
            gpu_name=gpu_name,
            llama_cpp_commit=llama_commit,
            llama_cpp_build=llama_build,
            config=self.config.to_dict(),
        )

    def ensure_dirs(self) -> None:
        for path in (
            self.results_dir,
            self.reports_dir,
            self.figures_dir,
            self.config.results_dir / "benchmark",
            self.config.results_dir / "quality",
            self.config.results_dir / "logs",
        ):
            path.mkdir(parents=True, exist_ok=True)

    def save_metadata(self) -> Path:
        self.ensure_dirs()
        path = self.results_dir / "metadata.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.environment.to_dict(), f, indent=2, default=str)
        logger.info("Saved experiment metadata to %s", path)
        return path
