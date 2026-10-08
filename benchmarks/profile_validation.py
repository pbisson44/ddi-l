"""Profile schema_loader.validate across validation backends."""

from __future__ import annotations

import argparse
import cProfile
import pstats
import sys
from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ddi_l import schema_loader
from ddi_l.schema_loader import Element

EXAMPLES_DIR = SRC_PATH / "ddi_l" / "examples"
PACKAGE_FIXTURES_DIR = EXAMPLES_DIR / "tests" / "fixtures"
# Large benchmark-only inputs live under tests/fixtures/ rather than inside the
# package, so they do not ship in the wheel.
TEST_FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"


TARGET_FUNCTIONS = {
    "_build_validation_issue",
    "_build_xpath_from_tree",
    "_collect_structural_warnings",
}

DEFAULT_FIXTURE_PATHS: Sequence[Path] = (
    TEST_FIXTURES_DIR / "Canadian_Survey_on_Business_conditions.xml",
    EXAMPLES_DIR / "Quality_of_Life.xml",
    PACKAGE_FIXTURES_DIR / "golden" / "example_instance.canonical.xml",
    PACKAGE_FIXTURES_DIR / "golden" / "quality_of_life_instance.canonical.xml",
)


@dataclass
class FixturePayload:
    """Container for loaded validation fixtures."""

    path: Path
    element: Element


def _existing_paths(paths: Iterable[Path]) -> list[Path]:
    candidates: list[Path] = []
    for path in paths:
        expanded = path.expanduser()
        if expanded.exists():
            candidates.append(expanded)
    return sorted({candidate.resolve() for candidate in candidates})


def _discover_fixtures(explicit: Sequence[Path]) -> list[Path]:
    if explicit:
        return _existing_paths(explicit)
    return _existing_paths(DEFAULT_FIXTURE_PATHS)


def _load_fixture(path: Path) -> FixturePayload:
    xml_payload = path.read_text(encoding="utf-8")
    element = schema_loader.fromstring(xml_payload)
    return FixturePayload(path=path, element=element)


def load_fixtures(paths: Sequence[Path]) -> list[FixturePayload]:
    fixtures = []
    for path in paths:
        fixtures.append(_load_fixture(path))
    if not fixtures:
        raise SystemExit("No fixtures available for profiling.")
    return fixtures


def _run_validation(fixtures: Sequence[FixturePayload], iterations: int) -> None:
    for _ in range(iterations):
        for fixture in fixtures:
            schema_loader.validate(fixture.element, raise_error=False)


@contextmanager
def _use_xmlschema_backend(enabled: bool) -> Iterator[None]:
    original_xmlschema = getattr(schema_loader, "xmlschema", None)
    try:
        schema_loader.clear_schema_cache()
        if not enabled:
            schema_loader.xmlschema = None  # type: ignore[assignment]
        yield
    finally:
        schema_loader.clear_schema_cache()
        schema_loader.xmlschema = original_xmlschema  # type: ignore[assignment]


def _print_target_stats(profile: cProfile.Profile, label: str) -> None:
    stats = pstats.Stats(profile)
    stats.strip_dirs()
    data = {}
    for (filename, _lineno, function_name), stat in stats.stats.items():
        if function_name not in TARGET_FUNCTIONS:
            continue
        if "_validation.py" not in filename:
            continue
        _cc, ncalls, tottime, cumtime, _callers = stat
        data[function_name] = (ncalls, tottime, cumtime)

    print(f"\nProfiling results for {label}:")
    for name in sorted(TARGET_FUNCTIONS):
        if name in data:
            ncalls, tottime, cumtime = data[name]
            print(
                f"  {name}: ncalls={ncalls} tottime={tottime:.6f}s cumtime={cumtime:.6f}s"
            )
        else:
            print(f"  {name}: not observed")


def profile_validation(
    fixtures: Sequence[FixturePayload], iterations: int, *, mode: str
) -> None:
    backends = {
        "both": (True, False),
        "xmlschema": (True,),
        "python": (False,),
    }[mode]

    for use_xmlschema in backends:
        if use_xmlschema and schema_loader.xmlschema is None:
            print("Skipping xmlschema backend profiling; xmlschema is not available.")
            continue

        label = "xmlschema" if use_xmlschema else "python"
        profiler = cProfile.Profile()
        with _use_xmlschema_backend(use_xmlschema):
            profiler.runcall(_run_validation, fixtures, iterations)
        _print_target_stats(profiler, label)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fixtures",
        metavar="FIXTURE",
        nargs="*",
        type=Path,
        help="Optional XML fixtures to profile. Defaults to representative large samples.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of validation rounds to execute for each fixture (default: 3).",
    )
    parser.add_argument(
        "--mode",
        choices=("both", "xmlschema", "python"),
        default="both",
        help=(
            "Select which validation backends to profile: xmlschema only, python-only fallback, or both (default)."
        ),
    )
    args = parser.parse_args()

    fixture_paths = _discover_fixtures(args.fixtures)
    fixtures = load_fixtures(fixture_paths)
    profile_validation(fixtures, args.iterations, mode=args.mode)


if __name__ == "__main__":  # pragma: no cover - profiling entry point
    main()
