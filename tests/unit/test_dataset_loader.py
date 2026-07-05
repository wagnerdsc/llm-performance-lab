"""Unit test for load_jsonl limit/limite compatibility."""

from pathlib import Path

import pytest

from src.datasets.dataset_loader import carregar_jsonl, load_jsonl


def test_load_jsonl_limit_and_limite(tmp_path):
    path = tmp_path / "test.jsonl"
    path.write_text('{"a": 1}\n{"a": 2}\n{"a": 3}\n', encoding="utf-8")

    assert len(load_jsonl(path, limit=2)) == 2
    assert len(load_jsonl(path, limite=1)) == 1
    assert len(carregar_jsonl(path, limite=2)) == 2
    assert len(carregar_jsonl(path, limit=3)) == 3
