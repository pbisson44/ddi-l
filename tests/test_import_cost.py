"""Importing the package and building the CLI parser stay lightweight."""

from __future__ import annotations

import subprocess
import sys


def _modules_loaded_by(code: str) -> set[str]:
    script = f"{code}\nimport sys\nprint('\\n'.join(sys.modules))"
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )
    return set(result.stdout.split())


def test_import_does_not_load_the_model_layer() -> None:
    loaded = _modules_loaded_by("import ddi_l")
    assert "ddi_l.models" not in loaded
    assert "xmlschema" not in loaded


def test_cli_parser_does_not_load_the_model_layer() -> None:
    loaded = _modules_loaded_by("from ddi_l import cli; cli.build_parser()")
    assert "ddi_l.models" not in loaded
    assert "xmlschema" not in loaded


def test_public_names_resolve_lazily() -> None:
    import ddi_l

    for name in ddi_l.__all__:
        assert getattr(ddi_l, name) is not None
    assert ddi_l.read_ddi is ddi_l.io.read_ddi


def test_unknown_attribute_raises_attribute_error() -> None:
    import pytest

    import ddi_l

    with pytest.raises(AttributeError):
        ddi_l.does_not_exist  # noqa: B018
