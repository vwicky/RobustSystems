from __future__ import annotations

import base64
import html
import io
import json
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from src.input_dataclass import InputData


@dataclass(frozen=True)
class ExportReportPaths:
    html_path: Path
    pdf_path: Path


def export_report_bundle(
    base_path: str | Path,
    input_data: InputData,
    task1_payload: dict[str, dict[str, Any]],
    task2_payload: dict[str, dict[str, Any]],
    task3_figure: Figure,
    task4_figure: Figure,
    explanations: dict[str, str],
) -> ExportReportPaths:
    base = Path(base_path).expanduser()
    if base.suffix:
        base = base.with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)

    html_path = base.with_suffix(".html")
    pdf_path = base.with_suffix(".pdf")

    _write_html_report(
        html_path=html_path,
        input_data=input_data,
        task1_payload=task1_payload,
        task2_payload=task2_payload,
        task3_figure=task3_figure,
        task4_figure=task4_figure,
        explanations=explanations,
    )
    _write_pdf_report(
        pdf_path=pdf_path,
        input_data=input_data,
        task1_payload=task1_payload,
        task2_payload=task2_payload,
        task3_figure=task3_figure,
        task4_figure=task4_figure,
        explanations=explanations,
    )

    return ExportReportPaths(html_path=html_path, pdf_path=pdf_path)


def _flatten_metrics(payload: dict[str, dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    return list(payload.items())


def _stringify_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (int, bool)):
        return str(value)
    if isinstance(value, (list, tuple, dict)):
        try:
            return json.dumps(value, ensure_ascii=False, indent=2)
        except TypeError:
            return str(value)
    return str(value)


def _figure_to_png_base64(fig: Figure) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=170, bbox_inches="tight")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _input_rows(data: InputData) -> list[tuple[str, str]]:
    return [
        ("Variant ID", str(data.var_id)),
        ("a1, a2, a3", f"{data.a1}, {data.a2}, {data.a3}"),
        ("k", str(data.k)),
        ("t", f"{data.t_display}"),
        ("lambda0", f"{data.lambda0}"),
        ("lambda1", f"{data.lambda1}"),
        ("lambda2", f"{data.lambda2}"),
        ("lambda3", f"{data.lambda3}"),
        ("beta", f"{data.beta}"),
        ("plots", ", ".join(data.plots)),
    ]


def _build_metric_table_html(
    title: str,
    payload: dict[str, dict[str, Any]],
    explanations: dict[str, str],
) -> str:
    rows = []
    for metric_name, item in _flatten_metrics(payload):
        value_text = html.escape(_stringify_value(item.get("value")))
        latex_text = html.escape(str(item.get("latex", "")))
        runtime = float(item.get("time", 0.0))
        error = item.get("error")
        error_text = html.escape(str(error)) if error else ""
        interp = html.escape(explanations.get(metric_name, ""))
        steps = item.get("steps") or []
        steps_html = "<br/>".join(html.escape(str(s)) for s in steps[:8])
        rows.append(
            f"""
            <tr>
                <td><b>{html.escape(metric_name)}</b></td>
                <td><pre>{value_text}</pre></td>
                <td><code>{latex_text}</code></td>
                <td>{runtime:.4f}s</td>
                <td>{error_text}</td>
                <td>{interp}</td>
                <td>{steps_html}</td>
            </tr>
            """
        )

    return f"""
    <h2>{html.escape(title)}</h2>
    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Formula (LaTeX)</th>
                <th>Runtime</th>
                <th>Error</th>
                <th>Interpretation</th>
                <th>Steps (preview)</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


def _write_html_report(
    html_path: Path,
    input_data: InputData,
    task1_payload: dict[str, dict[str, Any]],
    task2_payload: dict[str, dict[str, Any]],
    task3_figure: Figure,
    task4_figure: Figure,
    explanations: dict[str, str],
) -> None:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task3_png_b64 = _figure_to_png_base64(task3_figure)
    task4_png_b64 = _figure_to_png_base64(task4_figure)

    input_table_rows = "".join(
        f"<tr><td>{html.escape(k)}</td><td>{html.escape(v)}</td></tr>" for k, v in _input_rows(input_data)
    )

    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Reliability Report — Variant {input_data.var_id}</title>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    body {{
      font-family: "Segoe UI", Arial, sans-serif;
      margin: 24px;
      color: #1f2937;
      background: #f8fafc;
    }}
    h1, h2, h3 {{ color: #0f4c81; }}
    .meta {{ color: #4b5563; margin-bottom: 16px; }}
    .card {{
      background: #ffffff;
      border: 1px solid #dbe4ee;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 13px;
    }}
    th, td {{
      border: 1px solid #d7e0ea;
      padding: 8px;
      vertical-align: top;
      text-align: left;
    }}
    th {{ background: #eef4fa; }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "Cascadia Mono", Consolas, monospace;
      font-size: 12px;
    }}
    img {{
      width: 100%;
      border: 1px solid #dbe4ee;
      border-radius: 8px;
      background: #fff;
    }}
    .footer {{ margin-top: 20px; color: #6b7280; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>Reliability Solver Report</h1>
  <div class="meta">Generated: {html.escape(generated_at)} | Variant: {input_data.var_id}</div>

  <div class="card">
    <h2>Input Parameters</h2>
    <table>
      <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
      <tbody>{input_table_rows}</tbody>
    </table>
  </div>

  <div class="card">
    {_build_metric_table_html("Task 1 - Core Characteristics", task1_payload, explanations)}
  </div>
  <div class="card">
    {_build_metric_table_html("Task 2 - Readiness Condition", task2_payload, explanations)}
  </div>

  <div class="card">
    <h2>Task 3 - Plots</h2>
    <img alt="Task 3 plots" src="data:image/png;base64,{task3_png_b64}"/>
  </div>

  <div class="card">
    <h2>Task 4 - Architecture</h2>
    <img alt="Task 4 architecture" src="data:image/png;base64,{task4_png_b64}"/>
  </div>

  <div class="footer">
    Report includes metrics values, runtime, LaTeX formulas, interpretation text, and current figure snapshots.
  </div>
</body>
</html>
"""
    html_path.write_text(content, encoding="utf-8")


def _render_text_page(pdf: PdfPages, title: str, lines: list[str]) -> None:
    fig = Figure(figsize=(8.27, 11.69), dpi=120)
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.03, 0.98, title, fontsize=15, fontweight="bold", va="top")

    y = 0.94
    for line in lines:
        for wrapped in textwrap.wrap(line, width=110) or [""]:
            if y < 0.04:
                pdf.savefig(fig, bbox_inches="tight")
                fig = Figure(figsize=(8.27, 11.69), dpi=120)
                ax = fig.add_subplot(111)
                ax.axis("off")
                ax.text(0.03, 0.98, f"{title} (cont.)", fontsize=15, fontweight="bold", va="top")
                y = 0.94
            ax.text(0.03, y, wrapped, fontsize=9.3, va="top", family="DejaVu Sans")
            y -= 0.022
    pdf.savefig(fig, bbox_inches="tight")


def _metric_lines(
    section_title: str,
    payload: dict[str, dict[str, Any]],
    explanations: dict[str, str],
) -> list[str]:
    lines = [section_title]
    for metric_name, item in _flatten_metrics(payload):
        lines.append("")
        lines.append(f"Metric: {metric_name}")
        lines.append(f"  Value: {_stringify_value(item.get('value'))}")
        lines.append(f"  Runtime: {float(item.get('time', 0.0)):.4f}s")
        lines.append(f"  Formula: {item.get('latex', '')}")
        if item.get("error"):
            lines.append(f"  Error: {item.get('error')}")
        interpretation = explanations.get(metric_name)
        if interpretation:
            lines.append(f"  Interpretation: {interpretation}")
        steps = item.get("steps") or []
        if steps:
            lines.append("  Steps:")
            for idx, step in enumerate(steps[:8], start=1):
                lines.append(f"    {idx}. {step}")
    return lines


def _write_pdf_report(
    pdf_path: Path,
    input_data: InputData,
    task1_payload: dict[str, dict[str, Any]],
    task2_payload: dict[str, dict[str, Any]],
    task3_figure: Figure,
    task4_figure: Figure,
    explanations: dict[str, str],
) -> None:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    intro_lines = [
        f"Generated: {generated_at}",
        f"Variant ID: {input_data.var_id}",
        "",
        "Input Parameters:",
    ]
    intro_lines.extend([f"  {k}: {v}" for k, v in _input_rows(input_data)])

    with PdfPages(pdf_path) as pdf:
        _render_text_page(pdf, "Reliability Solver Report", intro_lines)
        _render_text_page(
            pdf,
            "Task 1 / Task 2 Results",
            _metric_lines("Task 1 - Core Characteristics", task1_payload, explanations)
            + ["", ""]
            + _metric_lines("Task 2 - Readiness Condition", task2_payload, explanations),
        )
        pdf.savefig(task3_figure, bbox_inches="tight")
        pdf.savefig(task4_figure, bbox_inches="tight")
