"""Memory usage metrics."""

from __future__ import annotations

import psutil


def snapshot_memory_mb() -> dict[str, float]:
    """Capture current process and system memory in MB."""
    proc = psutil.Process()
    mem = proc.memory_info()
    vm = psutil.virtual_memory()
    return {
        "process_rss_mb": round(mem.rss / (1024**2), 2),
        "process_vms_mb": round(mem.vms / (1024**2), 2),
        "system_used_mb": round(vm.used / (1024**2), 2),
        "system_total_mb": round(vm.total / (1024**2), 2),
        "system_percent": vm.percent,
    }
