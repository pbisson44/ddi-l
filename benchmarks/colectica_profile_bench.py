"""Time the ``colectica-questionnaire`` lint profile on one file.

Run from the project root::

    uv run python benchmarks/colectica_profile_bench.py FILE [--repeat N]

The file is read once; each repeat lints the same document, without schema
validation, and the best time is reported with the number of findings.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

try:  # pragma: no cover - helper for direct execution
    from ddi_l import read_ddi
    from ddi_l.lint import COLECTICA_QUESTIONNAIRE_PROFILE, run_profile
except ModuleNotFoundError:  # pragma: no cover - development convenience
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from ddi_l import read_ddi
    from ddi_l.lint import COLECTICA_QUESTIONNAIRE_PROFILE, run_profile


def main(argv: list[str] | None = None) -> int:
    """Lint the file ``--repeat`` times and print the best time."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path)
    parser.add_argument("--repeat", type=int, default=5)
    args = parser.parse_args(argv)

    document = read_ddi(args.path)
    times: list[float] = []
    findings = 0
    for _ in range(args.repeat):
        start = time.perf_counter()
        result = run_profile(
            document, COLECTICA_QUESTIONNAIRE_PROFILE, include_schema=False
        )
        times.append(time.perf_counter() - start)
        findings = len(result.lint_findings)
    print(f"{args.path.name}: best {min(times):.2f} s, {findings} findings")
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    raise SystemExit(main())
