"""
Benchmark report generation.

Produces:
    • Markdown reports
    • HTML reports
"""

from __future__ import annotations
from typing import Dict


def generate_markdown_report(results: Dict[str, Dict[str, float]]) -> str:
    """
    results = {
        "crf": {"accuracy": 0.991, "boundary_f1": 0.987},
        "rule": {...}
    }
    """
    lines = ["# Zomi-Syl Benchmark Report", ""]
    lines.append("| Backend | Accuracy | Boundary-F1 |")
    lines.append("|---------|----------|-------------|")

    for backend, metrics in results.items():
        acc = f"{metrics['accuracy']*100:.2f}%"
        f1 = f"{metrics['boundary_f1']*100:.2f}%"
        lines.append(f"| {backend} | {acc} | {f1} |")

    return "\n".join(lines)


def generate_html_report(results: Dict[str, Dict[str, float]]) -> str:
    rows = []
    for backend, metrics in results.items():
        rows.append(
            f"<tr><td>{backend}</td>"
            f"<td>{metrics['accuracy']*100:.2f}%</td>"
            f"<td>{metrics['boundary_f1']*100:.2f}%</td></tr>"
        )

    return f"""
<html>
<head><title>Zomi-Syl Benchmark Report</title></head>
<body>
<h1>Zomi-Syl Benchmark Report</h1>
<table border="1" cellpadding="6">
<tr><th>Backend</th><th>Accuracy</th><th>Boundary-F1</th></tr>
{''.join(rows)}
</table>
</body>
</html>
"""
