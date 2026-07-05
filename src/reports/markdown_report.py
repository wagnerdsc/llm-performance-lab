"""Markdown report generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.reports._io import NO_DATA_MESSAGE, safe_read_csv


def generate_markdown_report(results_dir: Path, reports_dir: Path) -> Path:
    """Generate a Markdown summary report from result CSVs."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "report.md"
    lines = [
        "# LLM Performance Lab — Benchmark Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    has_content = False

    quality_csv = results_dir / "quality" / "quality_resultados.csv"
    df = safe_read_csv(quality_csv)
    if df is not None and "acertou" in df.columns:
        has_content = True
        df = df.copy()
        df["acertou"] = df["acertou"].astype(str).str.lower().isin(["true", "1"])
        lines.append("## Quality Summary")
        lines.append("")
        lines.append(f"- Total items: {len(df)}")
        lines.append(f"- Overall accuracy: {df['acertou'].mean():.1%}")
        lines.append("")
        by_ds = df.groupby("dataset")["acertou"].mean().sort_values(ascending=False)
        lines.append("### Accuracy by Dataset")
        lines.append("")
        lines.append("| Dataset | Accuracy |")
        lines.append("|---------|----------|")
        for ds, acc in by_ds.head(20).items():
            lines.append(f"| {ds} | {acc:.1%} |")
        lines.append("")

    bench_csv = results_dir / "benchmark" / "benchmark_resultados.csv"
    bench_df = safe_read_csv(bench_csv)
    if bench_df is not None:
        has_content = True
        bench_df = bench_df.drop_duplicates("arquivo", keep="last")
        lines.append("## Throughput Summary")
        lines.append("")
        lines.append("| Model | pp512 t/s | tg128 t/s |")
        lines.append("|-------|-----------|-----------|")
        for _, row in bench_df.iterrows():
            lines.append(
                f"| {row.get('arquivo', '')} | {row.get('pp512_tps', '')} | {row.get('tg128_tps', '')} |"
            )
        lines.append("")

    if not has_content:
        lines.append(f"> {NO_DATA_MESSAGE}")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
