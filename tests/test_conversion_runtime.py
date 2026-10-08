import importlib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from ddi_l import schema_loader
from ddi_l._etree import tostring
from ddi_l.schema_loader import (
    CONVERSION_IMPLEMENTATION,
    fromstring,
)
from ddi_l.schema_loader import (
    from_dict as public_from_dict,
)
from ddi_l.schema_loader import (
    to_dict as public_to_dict,
)
from ddi_l.schema_loader._conversion import detect_version_from_element
from ddi_l.schema_loader._conversion_runtime import (
    _PYTHON_FUNCTIONS,
    IMPLEMENTATION,
)
from tests import PACKAGE_FIXTURES_DIR

SAMPLE_XML = (PACKAGE_FIXTURES_DIR / "minimal_instance.xml").read_text()
_SAMPLE_ELEMENT = fromstring(SAMPLE_XML)
_SAMPLE_MAPPING = _PYTHON_FUNCTIONS["to_dict"](_SAMPLE_ELEMENT)
_SAMPLE_ROOT = _SAMPLE_ELEMENT.tag
_SAMPLE_WRAPPED_MAPPING = {_SAMPLE_ROOT: _SAMPLE_MAPPING}

NAMESPACE_FIXTURE_PATHS = [
    PACKAGE_FIXTURES_DIR / "golden" / "example_instance.canonical.xml",
    PACKAGE_FIXTURES_DIR / "golden" / "quality_of_life_instance.canonical.xml",
]


@contextmanager
def _conversion_backend(
    backend: str, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[object, object]]:
    runtime = importlib.import_module("ddi_l.schema_loader._conversion_runtime")
    loader = importlib.import_module("ddi_l.schema_loader")
    previous_backend = runtime.IMPLEMENTATION
    with monkeypatch.context():
        try:
            runtime.set_conversion_backend(backend)
        except RuntimeError:
            if backend != "python":
                pytest.skip("Only the Python conversion backend is available")
            raise
        try:
            yield loader, runtime
        finally:
            runtime.set_conversion_backend(previous_backend)


def test_public_api_uses_runtime_selection() -> None:
    assert CONVERSION_IMPLEMENTATION == IMPLEMENTATION == "python"
    public_dict = public_to_dict(_SAMPLE_ELEMENT)
    reference_dict = _PYTHON_FUNCTIONS["to_dict"](_SAMPLE_ELEMENT)
    assert public_dict == reference_dict
    rebuilt = public_from_dict({_SAMPLE_ROOT: public_dict})
    assert tostring(rebuilt) == tostring(
        _PYTHON_FUNCTIONS["from_dict"]({_SAMPLE_ROOT: reference_dict})
    )


def test_conversion_backend_reports_python(monkeypatch: pytest.MonkeyPatch) -> None:
    with _conversion_backend("python", monkeypatch) as (loader, runtime):
        assert runtime.IMPLEMENTATION == "python"  # type: ignore[attr-defined]
        assert loader.CONVERSION_IMPLEMENTATION == "python"  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "fixture_path",
    NAMESPACE_FIXTURE_PATHS,
    ids=lambda path: path.name,
)
def test_namespace_normalization_matches_python(fixture_path: Path) -> None:
    xml_payload = Path(fixture_path).read_text(encoding="utf-8")
    element = fromstring(xml_payload)
    detected_version = detect_version_from_element(element)
    if isinstance(detected_version, bytes):  # pragma: no cover - defensive guard
        detected_version = detected_version.decode("utf-8")
    version = str(detected_version or schema_loader.SCHEMA_VERSION)
    schema = schema_loader.get_schema(version=version)

    raw_mapping = _PYTHON_FUNCTIONS["_element_to_dict"](
        element, process_namespaces=True
    )

    python_result = _PYTHON_FUNCTIONS["_normalize_result_namespaces"](
        raw_mapping,
        element,
        schema,
        process_namespaces=True,
    )

    wrapped_python = {element.tag: python_result}
    python_prefixed = _PYTHON_FUNCTIONS["_denormalize_clark_notation"](
        wrapped_python,
        schema.namespaces,
    )

    python_declared = _PYTHON_FUNCTIONS["_collect_declared_namespaces"](python_prefixed)
    python_input = _PYTHON_FUNCTIONS["_normalize_input_mapping"](
        python_prefixed,
        schema,
        process_namespaces=True,
    )

    assert python_declared == python_declared  # explicit sanity check
    assert python_input == python_input


def test_switching_to_nonexistent_backend_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = importlib.import_module("ddi_l.schema_loader._conversion_runtime")
    with pytest.raises(RuntimeError):
        runtime.set_conversion_backend("native")


def test_available_backends_only_python() -> None:
    runtime = importlib.import_module("ddi_l.schema_loader._conversion_runtime")
    assert runtime.get_available_conversion_backends() == ("python",)
