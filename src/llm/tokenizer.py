"""Tokenizer utilities (placeholder for future HuggingFace integration)."""

from __future__ import annotations

from pathlib import Path


def count_tokens_approx(text: str) -> int:
    """Rough token count estimate (whitespace split)."""
    return len(text.split())


def load_tokenizer(model_path: Path | None = None):
    """Placeholder for future tokenizer loading."""
    raise NotImplementedError("Tokenizer loading is reserved for future releases.")
