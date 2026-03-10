from dataclasses import dataclass
from typing import Any


@dataclass
class MetricResult:
    name: str
    value: Any
    latex: str
    elapsed_seconds: float
    steps: list[str]
    error: str | None = None


def normalize_metrics(payload: dict[str, dict]) -> list[MetricResult]:
    normalized: list[MetricResult] = []
    for name, item in payload.items():
        normalized.append(
            MetricResult(
                name=name,
                value=item.get("value"),
                latex=item.get("latex", ""),
                elapsed_seconds=float(item.get("time", 0.0)),
                steps=item.get("steps", []),
                error=item.get("error"),
            )
        )
    return normalized
