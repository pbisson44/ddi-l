"""Round-trip coverage for representative DDI instance fixtures."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pytest

from ddi_l import read_ddi
from ddi_l._etree import cleanup_namespaces, fromstring, tostring
from ddi_l.constants import DEFAULT_NSMAP
from ddi_l.validation import validate_document
from tests import PACKAGE_FIXTURES_DIR


def _canonicalize(xml: str) -> str:
    """Return a normalized XML string with stable namespace bindings."""

    element = fromstring(xml)
    cleanup_namespaces(element, DEFAULT_NSMAP)  # type: ignore[arg-type]
    return tostring(element, pretty_print=True).strip()


def _fixture_cases() -> Iterable[tuple[str, Path, Path]]:
    """Yield parametrized fixture cases covering tiny/medium/large documents."""

    yield (
        "tiny-minimal",
        PACKAGE_FIXTURES_DIR / "minimal_instance.xml",
        PACKAGE_FIXTURES_DIR / "golden" / "minimal_instance.canonical.xml",
    )
    yield (
        "medium-example-instance",
        PACKAGE_FIXTURES_DIR / "instances" / "example_instance.xml",
        PACKAGE_FIXTURES_DIR / "golden" / "example_instance.canonical.xml",
    )
    yield (
        "large-quality-of-life",
        PACKAGE_FIXTURES_DIR / "instances" / "quality_of_life_instance.xml",
        PACKAGE_FIXTURES_DIR / "golden" / "quality_of_life_instance.canonical.xml",
    )


@pytest.mark.parametrize(
    ("fixture_path", "golden_path"),
    [pytest.param(case[1], case[2], id=case[0]) for case in _fixture_cases()],
)
def test_instance_roundtrip(fixture_path: Path, golden_path: Path) -> None:
    """Ensure representative instances survive read/write cycles without drift."""

    document = read_ddi(fixture_path)

    round_trip_xml = _canonicalize(document.to_xml(pretty_print=True))
    expected_xml = golden_path.read_text(encoding="utf-8").strip()

    assert round_trip_xml == expected_xml

    validate_document(document, include_lint=False, raise_error=True)  # type: ignore[arg-type]
