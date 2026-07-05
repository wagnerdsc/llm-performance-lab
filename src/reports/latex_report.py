"""LaTeX report generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def generate_latex_report(results_dir: Path, reports_dir: Path) -> Path:
    """Generate a LaTeX table from benchmark results."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "report.tex"
    lines = [
        r"\documentclass{article}",
        r"\usepackage{booktabs}",
        r"\begin{document}",
        r"\title{LLM Performance Lab Benchmark Report}",
        f"\\date{{{datetime.now(timezone.utc).strftime('%Y-%m-%d')}}}",
        r"\maketitle",
    ]

    bench_csv = results_dir / "benchmark" / "benchmark_resultados.csv"
    if bench_csv.exists():
        df = pd.read_csv(bench_csv).drop_duplicates("arquivo", keep="last")
        lines.append(r"\section{Throughput}")
        lines.append(r"\begin{tabular}{lrr}")
        lines.append(r"\toprule")
        lines.append(r"Model & pp512 t/s & tg128 t/s \\")
        lines.append(r"\midrule")
        for _, row in df.iterrows():
            model = str(row.get("arquivo", "")).replace("_", r"\_")
            lines.append(f"{model} & {row.get('pp512_tps','')} & {row.get('tg128_tps','')} \\\\")
        lines.append(r"\bottomrule")
        lines.append(r"\end{tabular}")

    lines.extend([r"\end{document}", ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
