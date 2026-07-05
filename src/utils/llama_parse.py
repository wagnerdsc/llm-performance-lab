"""llama.cpp output parsers."""

from __future__ import annotations

import re


def parse_llama_bench_tps(output: str, label: str) -> float | None:
    """Extract tokens/s from llama-bench markdown table output."""
    for line in output.splitlines():
        if label not in line or "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            continue
        if label in parts[-2] or label in parts[-1]:
            nums = re.findall(r"[\d.]+", parts[-1])
            if nums:
                try:
                    return float(nums[0])
                except ValueError:
                    continue
    return None


parsear_tps_llama_bench = parse_llama_bench_tps
