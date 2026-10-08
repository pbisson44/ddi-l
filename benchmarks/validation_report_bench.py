"""Benchmark helpers for :class:`ddi_l.validation.ValidationReport`."""

from __future__ import annotations

import statistics
import sys
import timeit
from collections.abc import Iterable
from pathlib import Path

try:  # pragma: no cover - helper for direct execution
    from ddi_l.lint import LintFinding
    from ddi_l.schema_loader import SchemaValidationIssue
    from ddi_l.validation import ValidationReport
except ModuleNotFoundError:  # pragma: no cover - development convenience
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    from ddi_l.lint import LintFinding
    from ddi_l.schema_loader import SchemaValidationIssue
    from ddi_l.validation import ValidationReport


def _build_report(count: int) -> ValidationReport:
    issues: list[SchemaValidationIssue] = []
    findings: list[LintFinding] = []
    for index in range(count):
        issues.append(
            SchemaValidationIssue(
                message=f"Error message {index}",
                xpath=f"/Example[{index}]",
                context=None,
                severity="error" if index % 2 == 0 else "warning",
            )
        )
        findings.append(
            LintFinding(
                rule_id=f"lint.rule.{index}",
                message=f"Lint message {index}",
                severity="warning" if index % 3 else "error",
                location=f"/Example/{index}",
            )
        )
    return ValidationReport(schema_issues=issues, lint_findings=findings)


def _legacy_has_errors(report: ValidationReport) -> bool:
    return any(message.severity == "error" for message in report.iter_messages())


def _legacy_has_warnings(report: ValidationReport) -> bool:
    return any(message.severity == "warning" for message in report.iter_messages())


def _timeit(
    stmt: str, *, setup: str, number: int = 10, repeat: int = 5
) -> Iterable[float]:
    timer = timeit.Timer(stmt, setup=setup)
    return timer.repeat(repeat=repeat, number=number)


def benchmark(count: int = 500, iterations: int = 20) -> dict:
    """Return timing information comparing legacy and cached severity helpers."""

    setup = (
        "from __main__ import _build_report, _legacy_has_errors, _legacy_has_warnings"
    )
    legacy_stmt = (
        f"report = _build_report({count})\n"
        "for _ in range(iterations):\n"
        "    _legacy_has_errors(report)\n"
        "    _legacy_has_warnings(report)"
    )
    current_stmt = (
        f"report = _build_report({count})\n"
        "for _ in range(iterations):\n"
        "    report.has_errors()\n"
        "    report.has_warnings()"
    )

    legacy_runs = list(
        _timeit(
            legacy_stmt,
            setup=setup + f"\niterations = {iterations}",
            number=1,
        )
    )
    current_runs = list(
        _timeit(
            current_stmt,
            setup=setup + f"\niterations = {iterations}",
            number=1,
        )
    )

    return {
        "count": count,
        "iterations": iterations,
        "legacy_message_creations": count * 4 * iterations,
        "current_message_creations": 0,
        "legacy_mean": statistics.mean(legacy_runs),
        "legacy_stdev": statistics.stdev(legacy_runs) if len(legacy_runs) > 1 else 0.0,
        "current_mean": statistics.mean(current_runs),
        "current_stdev": statistics.stdev(current_runs)
        if len(current_runs) > 1
        else 0.0,
        "speedup": statistics.mean(legacy_runs) / statistics.mean(current_runs),
    }


def main() -> None:
    results = benchmark()
    print(
        "ValidationReport severity helpers benchmark",
        f"(count={results['count']}, iterations={results['iterations']})",
    )
    print(
        f"Legacy mean:   {results['legacy_mean']:.6f}s ± {results['legacy_stdev']:.6f}s"
    )
    print(
        f"Current mean:  {results['current_mean']:.6f}s ± {results['current_stdev']:.6f}s"
    )
    print(
        "Legacy ValidationMessage creations:",
        f"{results['legacy_message_creations']:,}",
    )
    print(
        "Current ValidationMessage creations:",
        f"{results['current_message_creations']:,}",
    )
    print(f"Approx. speedup: {results['speedup']:.2f}x")


if __name__ == "__main__":
    main()
