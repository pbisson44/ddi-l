"""Packaging smoke tests to ensure bundled assets remain accessible."""

from __future__ import annotations

from importlib import resources


def test_examples_fixtures_accessible() -> None:
    """Examples and fixtures should be loadable via ``importlib.resources``."""

    examples = resources.files("ddi_l").joinpath("examples")
    assert examples.exists()  # type: ignore[attr-defined]
    assert examples.is_dir()
    assert examples.joinpath("Quality_of_Life.xml").is_file()

    fixtures = examples.joinpath("tests", "fixtures")
    assert fixtures.exists()  # type: ignore[attr-defined]
    assert fixtures.is_dir()
    assert fixtures.joinpath("minimal_instance.xml").is_file()
