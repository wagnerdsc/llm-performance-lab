"""Backward-compatibility shim — use src.datasets package."""

from src.datasets import *  # noqa: F401,F403
from src.datasets.dataset_loader import listar_datasets, carregar_jsonl, iterar_jsonl
