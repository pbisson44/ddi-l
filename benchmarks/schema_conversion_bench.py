"""Benchmark schema_loader mapping conversions across available backends."""

from __future__ import annotations

import argparse
import statistics
import sys
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from timeit import Timer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

try:  # pragma: no cover - benchmark helper
    from ddi_l import schema_loader
except ModuleNotFoundError:  # pragma: no cover - dev helper when running from repo root
    if SRC_PATH.exists():
        sys.path.insert(0, str(SRC_PATH))
    from ddi_l import schema_loader

# The large survey lives in `tests/fixtures/` so it stays out of the wheel.
DEFAULT_FIXTURES: Sequence[Path] = (
    SRC_PATH / "ddi_l" / "examples" / "Quality_of_Life.xml",
    PROJECT_ROOT / "tests" / "fixtures" / "Canadian_Survey_on_Business_conditions.xml",
)


@contextmanager
def _select_backend(name: str) -> Iterator[str]:
    """Configure schema_loader to use the requested conversion backend."""

    backend = name.lower()
    if backend not in {"auto", "python"}:
        raise SystemExit(f"Unsupported backend: {name!r}. Expected auto/python.")

    schema_loader.clear_schema_cache()

    try:
        yield schema_loader.CONVERSION_IMPLEMENTATION
    finally:
        schema_loader.clear_schema_cache()


def _load_elements(paths: Sequence[Path]) -> list[schema_loader.Element]:
    elements: list[schema_loader.Element] = []
    for path in paths:
        payload = path.read_text(encoding="utf-8")
        elements.append(schema_loader.fromstring(payload))
    return elements


def _prepare_mappings(elements: Sequence[schema_loader.Element]) -> list[dict]:
    mappings: list[dict] = []
    for element in elements:
        payload = schema_loader.to_dict(element, process_namespaces=True)
        mappings.append({element.tag: payload})
    return mappings


def _run_to_dict(elements: Sequence[schema_loader.Element]) -> None:
    for element in elements:
        schema_loader.to_dict(element, process_namespaces=True)


def _run_from_dict(mappings: Sequence[dict]) -> None:
    for mapping in mappings:
        schema_loader.from_dict(mapping, process_namespaces=True)


def _summarize(label: str, durations: Sequence[float], conversions: int) -> str:
    median = statistics.median(durations) if durations else 0.0
    best = min(durations) if durations else 0.0
    worst = max(durations) if durations else 0.0
    per_conversion = median / conversions if conversions else 0.0
    return (
        f"{label}\n"
        f"Rounds: {len(durations)}\n"
        f"Median: {median:.4f}s\n"
        f"Best: {best:.4f}s\n"
        f"Worst: {worst:.4f}s\n"
        f"Median per conversion: {per_conversion:.6f}s"
    )


def _resolve_fixtures(inputs: Sequence[Path] | None) -> list[Path]:
    if inputs:
        resolved = [path.expanduser().resolve() for path in inputs]
    else:
        resolved = [path.resolve() for path in DEFAULT_FIXTURES]
    missing = [str(path) for path in resolved if not path.exists()]
    if missing:
        message = "\n".join(missing)
        raise SystemExit(f"Fixture path(s) do not exist:\n{message}")
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fixtures",
        nargs="*",
        type=Path,
        default=None,
        help="Path(s) to XML fixtures used for benchmarking (defaults to bundled examples).",
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "python"],
        default=None,
        help=(
            "Conversion backend to exercise. Defaults to 'auto', which uses "
            "whichever backend the runtime already selected."
        ),
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

    fixtures = _resolve_fixtures(args.fixtures)
    backend_choice = args.backend or "auto"

    with _select_backend(backend_choice) as backend:
        print(f"Backend: {backend}")
        if fixtures:
            print("Fixtures:")
            for path in fixtures:
                try:
                    display = path.relative_to(PROJECT_ROOT)
                except ValueError:
                    display = path
                print(f"  - {display}")

        elements = _load_elements(fixtures)
        mappings = _prepare_mappings(elements)

        # Warm the cache to keep measurements focused on steady-state conversion.
        _run_to_dict(elements)
        _run_from_dict(mappings)

        conversions_per_round = len(fixtures) * max(1, args.iterations)

        to_dict_timer = Timer(lambda: _run_to_dict(elements))
        to_dict_durations = to_dict_timer.repeat(
            repeat=args.repeats,
            number=args.iterations,
        )

        from_dict_timer = Timer(lambda: _run_from_dict(mappings))
        from_dict_durations = from_dict_timer.repeat(
            repeat=args.repeats,
            number=args.iterations,
        )

        print()
        print(_summarize("to_dict", to_dict_durations, conversions_per_round))
        print()
        print(_summarize("from_dict", from_dict_durations, conversions_per_round))


if __name__ == "__main__":  # pragma: no cover - benchmark entry point
    main()
