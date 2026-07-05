"""LaTeX report generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.reports._io import NO_DATA_MESSAGE, safe_read_csv


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
    has_content = False

    bench_csv = results_dir / "benchmark" / "benchmark_resultados.csv"
    bench_df = safe_read_csv(bench_csv)
    if bench_df is not None:
        has_content = True
        bench_df = bench_df.drop_duplicates("arquivo", keep="last")
        lines.append(r"\section{Throughput}")
        lines.append(r"\begin{tabular}{lrr}")
        lines.append(r"\toprule")
        lines.append(r"Model & pp512 t/s & tg128 t/s \\")
        lines.append(r"\midrule")
        for _, row in bench_df.iterrows():
            model = str(row.get("arquivo", "")).replace("_", r"\_")
            lines.append(f"{model} & {row.get('pp512_tps', '')} & {row.get('tg128_tps', '')} \\\\")
        lines.append(r"\bottomrule")
        lines.append(r"\end{tabular}")

    quality_csv = results_dir / "quality" / "quality_resultados.csv"
    quality_df = safe_read_csv(quality_csv)
    if quality_df is not None and "acertou" in quality_df.columns:
        has_content = True
        quality_df = quality_df.copy()
        quality_df["acertou"] = quality_df["acertou"].astype(str).str.lower().isin(["true", "1"])
        acc = quality_df["acertou"].mean()
        lines.append(r"\section{Quality}")
        lines.append(f"Overall accuracy: {acc:.1%} ({len(quality_df)} items).")

    if not has_content:
        lines.append(f"\\textit{{{NO_DATA_MESSAGE}}}")

    lines.extend([r"\end{document}", ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
