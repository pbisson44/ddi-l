"""Benchmark utilities for measuring clone performance on large fragments."""

from __future__ import annotations

import argparse
import statistics
from collections.abc import Iterable
from pathlib import Path
from timeit import Timer

from ddi_l._etree import Element
from ddi_l.document import DDIFragment
from ddi_l.models import clone_element


def _load_payloads(fragment_path: Path) -> list[Element]:
    fragment = DDIFragment.from_xml(fragment_path, validate=False)
    try:
        return list(fragment.iter_fragment_payloads())
    finally:
        # Keep the fragment alive until the payloads have been collected to
        # avoid dangling references under the stdlib XML backend.
        fragment  # pragma: no cover - defensive reference


def _clone_payloads(payloads: Iterable[Element]) -> None:
    for payload in payloads:
        clone_element(payload)


def run_benchmark(
    payloads: Iterable[Element], *, repeats: int, iterations: int
) -> list[float]:
    timer = Timer(lambda: _clone_payloads(payloads))
    return timer.repeat(repeat=repeats, number=iterations)


def _summarize(results: list[float], payload_count: int) -> str:
    median = statistics.median(results)
    best = min(results)
    worst = max(results)
    per_payload = median / payload_count if payload_count else 0.0
    return (
        f"Rounds: {len(results)}\n"
        f"Median: {median:.4f}s\n"
        f"Best: {best:.4f}s\n"
        f"Worst: {worst:.4f}s\n"
        f"Median per payload: {per_payload:.6f}s"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fragment",
        type=Path,
        nargs="?",
        default=Path("examples/Quality_of_Life.xml"),
        help="Path to a fragment instance used for benchmarking.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="Number of timing rounds to execute (default: 5).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of benchmark iterations per round (default: 1).",
    )
    args = parser.parse_args()

    fragment_path = args.fragment.expanduser().resolve()
    if not fragment_path.exists():
        raise SystemExit(f"Fragment {fragment_path} does not exist.")

    payloads = _load_payloads(fragment_path)
    results = run_benchmark(payloads, repeats=args.repeats, iterations=args.iterations)
    summary = _summarize(results, len(payloads))
    print(summary)


if __name__ == "__main__":  # pragma: no cover - benchmark entry point
    main()
