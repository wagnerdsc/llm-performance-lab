"""Tests for report generation."""

from pathlib import Path

from src.reports._io import NO_DATA_MESSAGE, safe_read_csv
from src.reports.markdown_report import generate_markdown_report
from src.reports.latex_report import generate_latex_report


def test_safe_read_csv_empty(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("timestamp,modelo\n", encoding="utf-8")
    assert safe_read_csv(empty) is None

    missing = tmp_path / "missing.csv"
    assert safe_read_csv(missing) is None


def test_markdown_report_no_data(tmp_path):
    results = tmp_path / "results"
    reports = tmp_path / "reports"
    results.mkdir()
    (results / "quality").mkdir()
    (results / "benchmark").mkdir()

    path = generate_markdown_report(results, reports)
    content = path.read_text(encoding="utf-8")
    assert NO_DATA_MESSAGE in content


def test_markdown_report_with_quality(tmp_path):
    results = tmp_path / "results"
    reports = tmp_path / "reports"
    quality_dir = results / "quality"
    quality_dir.mkdir(parents=True)
    (quality_dir / "quality_resultados.csv").write_text(
        "timestamp,modelo,dataset,item_idx,acertou\n"
        "2026-01-01T00:00:00Z,m1,ds1,0,True\n"
        "2026-01-01T00:00:00Z,m1,ds1,1,False\n",
        encoding="utf-8",
    )

    path = generate_markdown_report(results, reports)
    content = path.read_text(encoding="utf-8")
    assert "Quality Summary" in content
    assert NO_DATA_MESSAGE not in content


def test_latex_report_no_data(tmp_path):
    results = tmp_path / "results"
    reports = tmp_path / "reports"
    results.mkdir()
    path = generate_latex_report(results, reports)
    assert NO_DATA_MESSAGE in path.read_text(encoding="utf-8")
