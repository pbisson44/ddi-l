"""Fail when mutation testing finds a surviving mutant the baseline does not list.

Run it after ``mutmut run``. A surviving mutant is a small change to the code
that no test notices. ``tests/mutation_baseline.txt`` lists the known ones, one
name per line, with the reason after ``#`` once someone has looked at it. The
check also fails when a listed mutant is no longer a survivor, so the list
only shrinks.

    uv run python scripts/check_mutation.py           # check
    uv run python scripts/check_mutation.py --update  # rewrite the baseline
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASELINE = Path(__file__).resolve().parents[1] / "tests" / "mutation_baseline.txt"
# A mutant some test noticed; every other status counts as a survivor.
CAUGHT = {"killed", "timeout", "caught by type check", "skipped"}
HEADER = """\
# Mutants that survive `mutmut run`: changes to the code no test notices.
# scripts/check_mutation.py fails on a survivor missing from this list, and on
# an entry that no longer survives. After `#`, why it survives: "equivalent"
# when no test can tell the mutant from the original, "stdlib backend only"
# when only the stdlib backend runs that code (the run uses lxml). An entry
# with no reason has not been looked at yet. Rewrite with: check_mutation.py --update
"""


def _results() -> dict[str, str]:
    output = subprocess.run(
        [sys.executable, "-m", "mutmut", "results", "--all", "true"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    results = {}
    for line in output.splitlines():
        name, separator, status = line.strip().rpartition(": ")
        if separator:
            results[name] = status
    return results


def _baseline() -> dict[str, str]:
    entries = {}
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        name, _, reason = line.partition("#")
        if name.strip():
            entries[name.strip()] = reason.strip()
    return entries


def main(argv: list[str]) -> int:
    """Check the survivors against the baseline, or rewrite it with ``--update``."""
    results = _results()
    unchecked = sorted(
        name for name, status in results.items() if status == "not checked"
    )
    if unchecked:
        print(f"{len(unchecked)} mutants not checked: let `mutmut run` finish.")
        return 1
    survivors = sorted(name for name, status in results.items() if status not in CAUGHT)
    baseline = _baseline() if BASELINE.exists() else {}

    if "--update" in argv:
        lines = [
            f"{name}  # {baseline[name]}" if baseline.get(name) else name
            for name in survivors
        ]
        BASELINE.write_text(
            HEADER + "".join(f"{line}\n" for line in lines), encoding="utf-8"
        )
        print(f"Wrote {len(survivors)} survivors to {BASELINE.name}.")
        return 0

    new = [name for name in survivors if name not in baseline]
    gone = [name for name in baseline if name not in results or results[name] in CAUGHT]
    for name in new:
        print(f"new survivor: {name} ({results[name]}); see `mutmut show {name}`")
    for name in gone:
        print(f"no longer survives: {name}; remove it from {BASELINE.name}")
    print(
        f"{len(results)} mutants, {len(survivors)} survivors, {len(baseline)} listed."
    )
    return 1 if new or gone else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
