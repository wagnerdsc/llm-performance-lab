"""Throughput metrics."""

from __future__ import annotations


def compute_throughput(tokens: int, latency_s: float) -> float:
    if latency_s <= 0:
        return 0.0
    return tokens / latency_s
