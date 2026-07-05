"""Unit tests."""

from pathlib import Path

import pytest

from src.llm.model_loader import parse_quantization, parse_family
from src.utils.llama_parse import parse_llama_bench_tps
from src.metrics.f1 import token_f1
from src.metrics.exact_match import exact_match
from src.core.registry import Registry


SAMPLE_BENCH = """
| model | test | t/s |
| qwen2 3B Q4_K | pp512 | 44.68 ± 2.09 |
| qwen2 3B Q4_K | tg128 | 3.87 ± 0.64 |
"""


def test_parse_quantization():
    assert parse_quantization("Qwen2.5-3B-Instruct-Q4_K_M.gguf") == "Q4_K_M"
    assert parse_quantization("model-F16.gguf") == "F16"


def test_parse_family(tmp_path):
    models_dir = tmp_path / "models"
    model_dir = models_dir / "Qwen2.5-3B-Instruct"
    model_dir.mkdir(parents=True)
    model = model_dir / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"
    model.write_bytes(b"x")
    assert parse_family(model, models_dir) == "Qwen2.5-3B-Instruct"


def test_parse_llama_bench_tps():
    assert parse_llama_bench_tps(SAMPLE_BENCH, "pp512") == pytest.approx(44.68)
    assert parse_llama_bench_tps(SAMPLE_BENCH, "tg128") == pytest.approx(3.87)
    assert parse_llama_bench_tps(SAMPLE_BENCH, "missing") is None


def test_token_f1():
    assert token_f1("hello world", "hello there world") > 0.5


def test_exact_match():
    assert exact_match("Hello", "hello") == 1.0
    assert exact_match("A", "B") == 0.0


def test_registry():
    reg: Registry[str] = Registry("test")
    reg.register("a", "alpha")
    assert reg.get("a") == "alpha"
    assert "a" in reg
