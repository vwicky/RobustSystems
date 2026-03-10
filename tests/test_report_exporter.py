from pathlib import Path

from matplotlib.figure import Figure

from src.input_dataclass import var_6
from src.report_exporter import export_report_bundle


def _sample_payload() -> dict[str, dict]:
    return {
        "Q_3W": {
            "value": 0.1234,
            "latex": "1 - K_{\\Gamma 3W}",
            "steps": ["step 1", "step 2"],
            "time": 0.0456,
            "error": None,
        }
    }


def _simple_figure(title: str) -> Figure:
    fig = Figure(figsize=(4, 3), dpi=90)
    ax = fig.add_subplot(111)
    ax.plot([0, 1, 2], [0, 1, 0])
    ax.set_title(title)
    return fig


def test_export_report_bundle_creates_html_and_pdf(tmp_path: Path) -> None:
    report_base = tmp_path / "out" / "demo_report"
    result = export_report_bundle(
        base_path=report_base,
        input_data=var_6,
        task1_payload=_sample_payload(),
        task2_payload=_sample_payload(),
        task3_figure=_simple_figure("Task 3"),
        task4_figure=_simple_figure("Task 4"),
        explanations={"Q_3W": "Interpretation sample"},
    )

    assert result.html_path.exists()
    assert result.pdf_path.exists()
    assert result.html_path.suffix == ".html"
    assert result.pdf_path.suffix == ".pdf"
    assert result.html_path.stat().st_size > 0
    assert result.pdf_path.stat().st_size > 0
