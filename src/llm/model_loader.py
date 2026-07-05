"""GGUF model discovery and metadata extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

from src.core.registry import Registry
from src.utils.io import file_size_gib, file_size_gb, list_gguf_files


@dataclass
class ModelInfo:
    """Metadata for a discovered GGUF model."""

    path: Path
    name: str
    family: str
    quantization: str
    size_gib: float
    size_gb: float
    backend: str = "cpu"

    @property
    def relative_path(self) -> str:
        return self.name


ModelRegistry: Registry[type] = Registry("ModelRegistry")


_QUANT_PATTERNS = [
    r"F16", r"F32", r"Q2_K", r"Q3_K_S", r"Q3_K_M", r"Q3_K_L",
    r"Q4_K_S", r"Q4_K_M", r"Q4_0", r"Q4_1",
    r"Q5_K_S", r"Q5_K_M", r"Q5_0", r"Q5_1",
    r"Q6_K", r"Q8_0", r"IQ2_XXS", r"IQ3_XXS",
]


def parse_quantization(filename: str) -> str:
    """Extract quantization label from GGUF filename."""
    for pattern in _QUANT_PATTERNS:
        if re.search(rf"-{pattern}(?:\.|$)", filename, re.IGNORECASE):
            return pattern.upper()
    m = re.search(r"Q\d[_A-Z0-9]+", filename, re.IGNORECASE)
    return m.group(0).upper() if m else "UNKNOWN"


def parse_family(path: Path, models_dir: Path) -> str:
    """Extract model family from directory or filename."""
    try:
        rel = path.relative_to(models_dir)
        if len(rel.parts) > 1:
            return rel.parts[0]
    except ValueError:
        pass
    stem = path.stem
    for q in _QUANT_PATTERNS:
        stem = re.sub(rf"-{q}$", "", stem, flags=re.IGNORECASE)
    return stem


def discover_models(
    models_dir: Path,
    *,
    limit: int | None = None,
    model_glob: str | None = None,
) -> list[ModelInfo]:
    """Discover all GGUF models under models_dir."""
    paths = list_gguf_files(models_dir)
    if model_glob:
        paths = [
            p for p in paths
            if fnmatch(p.name, model_glob) or fnmatch(str(p.relative_to(models_dir)), model_glob)
        ]
    if limit is not None and limit > 0:
        paths = paths[:limit]

    models: list[ModelInfo] = []
    for path in paths:
        try:
            rel = str(path.relative_to(models_dir))
        except ValueError:
            rel = path.name
        models.append(ModelInfo(
            path=path,
            name=rel,
            family=parse_family(path, models_dir),
            quantization=parse_quantization(path.name),
            size_gib=round(file_size_gib(path), 3),
            size_gb=round(file_size_gb(path), 3),
        ))
    return models
