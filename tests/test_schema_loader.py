import io
import logging
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import pytest

from ddi_l import schema_loader
from ddi_l._schema_versions import (
    SUPPORTED_SCHEMA_VERSIONS,
    get_schema_release,
    iter_schema_versions,
)
from ddi_l.schema_loader import SchemaValidationError


@pytest.fixture(scope="module")
def schema_fixtures(fixtures_dir: Path) -> Path:
    """Directory containing XML fixtures for schema loader tests."""

    return fixtures_dir


def test_public_exports_are_explicit_and_public():
    """schema_loader exposes a curated list of public helpers."""

    expected_exports = {
        "CONVERSION_IMPLEMENTATION",
        "Element",
        "INSTANCE_NAMESPACE",
        "REUSABLE_NAMESPACE",
        "SCHEMA_VERSION",
        "SchemaInput",
        "SchemaValidationError",
        "SchemaValidationIssue",
        "VALIDATION_IMPLEMENTATION",
        "XMLNS_NAMESPACE",
        "XMLSchemaConverter",
        "XMLSchemaValidationError",
        "clear_known_type_name_cache",
        "clear_schema_cache",
        "create_element",
        "from_dict",
        "fromstring",
        "get_available_conversion_backends",
        "get_available_validation_backends",
        "get_schema",
        "qname_to_clark_notation",
        "set_conversion_backend",
        "set_validation_backend",
        "to_dict",
        "validate",
        "xmlschema",
    }

    assert set(schema_loader.__all__) == expected_exports
    assert all(not name.startswith("_") for name in schema_loader.__all__)


def test_get_schema_returns_object():
    """get_schema returns schema object exposing validate method."""
    schema = schema_loader.get_schema()
    assert hasattr(schema, "validate")


@pytest.mark.parametrize("version", list(iter_schema_versions()))
def test_schema_resource_available_and_uses_xmlschema_when_present(
    version: str,
) -> None:
    """XMLSchema backend loads packaged schema resources when available."""

    xmlschema = pytest.importorskip("xmlschema")

    release = get_schema_release(version)
    resource = resources.files("ddi_l.schemas")
    for part in release["schema_resource"]:
        resource = resource / part

    with resources.as_file(resource) as schema_path:
        assert schema_path.name == release["schema_filename"]
        assert schema_path.exists()

    schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]
    try:
        schema = schema_loader.get_schema(version)
        assert isinstance(schema, xmlschema.XMLSchema)
    finally:
        schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]


def test_validate_accepts_valid_instance(schema_fixtures: Path):
    """validate accepts valid instances from disk paths."""
    valid_path = schema_fixtures / "minimal_instance.xml"
    schema_loader.validate(valid_path)


def test_validate_reports_unsupported_version_override(schema_fixtures: Path):
    """validate raises SchemaValidationError for unsupported overrides."""

    unsupported_version = "0.9"

    with pytest.raises(SchemaValidationError) as excinfo:
        schema_loader.validate(
            schema_fixtures / "minimal_instance.xml", version=unsupported_version
        )

    issue = excinfo.value.issues[0]
    assert unsupported_version in issue.message
    for supported in SUPPORTED_SCHEMA_VERSIONS:
        assert str(supported) in issue.message


def test_validate_returns_issue_when_suppressed_for_unsupported_version(
    schema_fixtures: Path,
):
    """validate returns SchemaValidationIssue when raise_error=False."""

    unsupported_version = "0.9"

    issues = schema_loader.validate(
        schema_fixtures / "minimal_instance.xml",
        version=unsupported_version,
        raise_error=False,
    )

    assert len(issues) == 1
    issue = issues[0]
    assert unsupported_version in issue.message
    assert issue.severity == "error"


@pytest.mark.parametrize(
    "fixture_name",
    [
        "minimal_instance_3_1.xml",
        "minimal_instance_3_2.xml",
    ],
)
def test_validate_detects_version_from_namespace(
    schema_fixtures: Path, fixture_name: str
):
    """validate auto-detects schema version from legacy instance namespaces."""

    schema_loader.clear_schema_cache()
    try:
        schema_loader.validate(schema_fixtures / fixture_name)
    finally:
        schema_loader.clear_schema_cache()


def test_validate_rejects_invalid_instance(schema_fixtures: Path):
    """validate raises SchemaValidationError for invalid files."""
    invalid_path = schema_fixtures / "invalid_instance_missing_id.xml"
    with pytest.raises(SchemaValidationError) as excinfo:
        schema_loader.validate(invalid_path)
    issue = excinfo.value.issues[0]
    assert "Missing required identification" in issue.message
    assert issue.xpath.endswith("DDIInstance")  # type: ignore[union-attr]
    assert "DDIInstance" in (issue.context or "")
    assert issue.to_dict()["line"] == issue.line


@pytest.mark.parametrize(
    "fixture_name",
    [
        "invalid_instance_3_1_missing_id.xml",
        "invalid_instance_3_2_missing_id.xml",
    ],
)
def test_validate_detects_version_for_invalid_documents(
    schema_fixtures: Path, fixture_name: str
):
    """validate reports structured issues for legacy versions lacking IDs."""

    schema_loader.clear_schema_cache()
    try:
        with pytest.raises(SchemaValidationError) as excinfo:
            schema_loader.validate(schema_fixtures / fixture_name)
        issue = excinfo.value.issues[0]
        assert "Missing required identification" in issue.message
    finally:
        schema_loader.clear_schema_cache()


def test_validate_rejects_invalid_instance_with_fallback(
    schema_fixtures: Path, monkeypatch
):
    """Fallback schema also surfaces structured validation errors.

    Args:
        monkeypatch: Fixture patching xmlschema availability for fallback.
    """
    monkeypatch.setattr(schema_loader, "xmlschema", None)
    schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]

    try:
        schema = schema_loader.get_schema()
        assert isinstance(schema, schema_loader._FallbackSchema)

        invalid_path = schema_fixtures / "invalid_instance_missing_id.xml"
        with pytest.raises(SchemaValidationError) as excinfo:
            schema_loader.validate(invalid_path)
        issue = excinfo.value.issues[0]
        assert issue.xpath.endswith("DDIInstance")  # type: ignore[union-attr]
        assert "Missing required" in issue.message
        payload = issue.to_dict()
        assert payload["line"] == issue.line
        assert payload["column"] == issue.column
    finally:
        schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]


def test_validate_accepts_xml_string(schema_fixtures: Path):
    """validate accepts XML strings in addition to file paths."""
    xml_string = (schema_fixtures / "minimal_instance.xml").read_text(encoding="utf-8")
    schema_loader.validate(xml_string)


def test_validate_accepts_stream_input(schema_fixtures: Path):
    """validate accepts file-like streams while using xmlschema backend."""
    xml_bytes = (schema_fixtures / "minimal_instance.xml").read_bytes()

    xmlschema = pytest.importorskip("xmlschema")

    schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]
    try:
        schema = schema_loader.get_schema()
        assert isinstance(schema, xmlschema.XMLSchema)
        schema_loader.validate(io.BytesIO(xml_bytes))
    finally:
        schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]


def test_validate_accepts_stream_input_with_fallback(
    schema_fixtures: Path, monkeypatch
):
    """Fallback schema validates stream inputs when xmlschema is unavailable.

    Args:
        monkeypatch: Fixture patching xmlschema availability for fallback.
    """
    monkeypatch.setattr(schema_loader, "xmlschema", None)
    schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]

    try:
        schema = schema_loader.get_schema()
        assert isinstance(schema, schema_loader._FallbackSchema)

        xml_bytes = (schema_fixtures / "minimal_instance.xml").read_bytes()
        schema_loader.validate(io.BytesIO(xml_bytes))
    finally:
        schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]


def test_validate_reports_coordinates_with_xmlschema(
    schema_fixtures: Path, monkeypatch
):
    """xmlschema-backed validation attaches location metadata when provided."""

    xmlschema = pytest.importorskip("xmlschema")

    schema_loader.clear_schema_cache()
    try:
        schema = schema_loader.get_schema()
        assert isinstance(schema, xmlschema.XMLSchema)

        class DummyValidationError(Exception):
            def __init__(
                self,
                message: str,
                elem=None,
                xpath: str | None = None,
                *,
                line: int | None = None,
                column: int | None = None,
            ) -> None:
                super().__init__(message)
                self.reason = message
                self.elem = elem
                self.obj = elem
                self.path = xpath
                self.line = line
                self.column = column
                if line is not None and column is not None:
                    self.position = (line, column)

        def fake_validate(self, node):
            raise DummyValidationError(
                "boom", elem=node, xpath="/Fake", line=42, column=7
            )

        monkeypatch.setattr(
            schema_loader, "XMLSchemaValidationError", DummyValidationError
        )
        monkeypatch.setattr(type(schema), "validate", fake_validate, raising=False)

        with pytest.raises(SchemaValidationError) as excinfo:
            schema_loader.validate(schema_fixtures / "minimal_instance.xml")

        issue = excinfo.value.issues[0]
        assert issue.line == 42
        assert issue.column == 7
        payload = issue.to_dict()
        assert payload["line"] == 42
        assert payload["column"] == 7
    finally:
        schema_loader.clear_schema_cache()


def test_validate_reports_coordinates_with_fallback(schema_fixtures: Path, monkeypatch):
    """Fallback schema propagates coordinates from validation errors."""

    monkeypatch.setattr(schema_loader, "xmlschema", None)
    schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]

    try:
        schema = schema_loader.get_schema()
        assert isinstance(schema, schema_loader._FallbackSchema)

        class DummyValidationError(Exception):
            def __init__(
                self,
                message: str,
                elem=None,
                xpath: str | None = None,
                *,
                line: int | None = None,
                column: int | None = None,
            ) -> None:
                super().__init__(message)
                self.reason = message
                self.elem = elem
                self.obj = elem
                self.path = xpath
                self.line = line
                self.column = column
                if line is not None and column is not None:
                    self.position = (line, column)

        def fake_validate(node):
            raise DummyValidationError(
                "boom", elem=node, xpath="/Fake", line=21, column=3
            )

        monkeypatch.setattr(
            schema_loader, "XMLSchemaValidationError", DummyValidationError
        )
        monkeypatch.setattr(schema, "validate", fake_validate)

        with pytest.raises(SchemaValidationError) as excinfo:
            schema_loader.validate(schema_fixtures / "minimal_instance.xml")

        issue = excinfo.value.issues[0]
        assert issue.line == 21
        assert issue.column == 3
        payload = issue.to_dict()
        assert payload["line"] == 21
        assert payload["column"] == 3
    finally:
        schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]


def test_validate_returns_structured_issue_without_raising(
    schema_fixtures: Path, monkeypatch
):
    """validate returns structured issues when raise_error=False.

    Args:
        monkeypatch: Fixture patching xmlschema availability for fallback.
    """
    monkeypatch.setattr(schema_loader, "xmlschema", None)
    schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]

    try:
        schema = schema_loader.get_schema()
        assert isinstance(schema, schema_loader._FallbackSchema)

        invalid_path = schema_fixtures / "invalid_instance_missing_id.xml"
        issues = schema_loader.validate(invalid_path, raise_error=False)
        assert issues, "Expected validation issues"
        issue = issues[0]
        assert "Missing required identification" in issue.message
        assert issue.xpath.endswith("DDIInstance")  # type: ignore[union-attr]
        assert issue.context and "DDIInstance" in issue.context
        assert issue.severity == "error"
    finally:
        schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]


def test_validate_returns_structured_issue_with_xmlschema(monkeypatch):
    """xmlschema-backed validate reports structured issue payloads.

    Args:
        monkeypatch: Fixture patching schema loader internals for fake errors.
    """

    class FakeXMLSchemaError(Exception):
        def __init__(
            self, message: str, elem: schema_loader.Element, path: str
        ) -> None:
            """Capture message, failing element, and xpath for fake errors."""
            super().__init__(message)
            self.reason = message
            self.path = path
            self.elem = elem

    @dataclass
    class _SchemaFactory:
        schema: Any

        def __call__(self, *args: Any, **kwargs: Any):
            """Return the cached schema instance for monkeypatching."""
            return self.schema

        def cache_clear(self):
            """Provide cache_clear attribute to mimic functools.lru_cache."""
            pass

    fake_root = schema_loader.create_element(
        f"{{{schema_loader.INSTANCE_NAMESPACE}}}DDIInstance"
    )
    for name in ("Agency", "ID", "Version"):
        fake_root.append(
            schema_loader.create_element(
                f"{{{schema_loader.REUSABLE_NAMESPACE}}}{name}"
            )
        )

    class FakeSchema:
        namespaces = {
            None: schema_loader.INSTANCE_NAMESPACE,
            "ddi": schema_loader.INSTANCE_NAMESPACE,
            "r": schema_loader.REUSABLE_NAMESPACE,
        }

        def validate(self, document):
            """Raise deterministic xmlschema error for testing."""
            raise FakeXMLSchemaError(
                "Fake xmlschema validation error",
                fake_root,
                "/ddi:DDIInstance/r:ID",
            )

    schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.setattr(schema_loader, "XMLSchemaValidationError", FakeXMLSchemaError)
    monkeypatch.setattr(schema_loader, "get_schema", _SchemaFactory(FakeSchema()))

    issues = schema_loader.validate(fake_root, raise_error=False)
    assert issues
    issue = issues[0]
    assert issue.message == "Fake xmlschema validation error"
    assert issue.xpath == "/ddi:DDIInstance/r:ID"
    assert issue.context and "DDIInstance" in issue.context
    assert issue.severity == "error"


def test_fallback_validation_surfaces_reference_warnings(monkeypatch):
    """Fallback validation emits warnings about reference structure."""

    monkeypatch.setattr(schema_loader, "xmlschema", None)
    schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]

    try:
        # Ensure maintainable registry is populated for type-of-object heuristics.
        import ddi_l.models  # noqa: F401

        xml = """
        <DDIInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">
          <r:Agency>example.agency</r:Agency>
          <r:ID>doc</r:ID>
          <r:Version>1.0</r:Version>
          <r:ControlConstructReference>
            <r:TypeOfObject></r:TypeOfObject>
          </r:ControlConstructReference>
        </DDIInstance>
        """
        issues = schema_loader.validate(xml, raise_error=False)
        assert issues
        warning_messages = {
            issue.message for issue in issues if issue.severity == "warning"
        }
        assert any(
            "Missing both URN" in message or "missing both URN" in message
            for message in warning_messages
        )
        assert any("TypeOfObject" in message for message in warning_messages)
    finally:
        schema_loader.get_schema.cache_clear()  # type: ignore[attr-defined]


def test_fallback_schema_to_dict_preserves_attributes():
    """Fallback schema to_dict retains XML attributes like xml:lang."""
    schema = schema_loader._FallbackSchema(
        Path("."), version=schema_loader.SCHEMA_VERSION
    )
    element = schema_loader.fromstring("<Value xml:lang='en'>Hello</Value>")

    result = schema.to_dict(element)

    assert result["@{http://www.w3.org/XML/1998/namespace}lang"] == "en"
    assert result["#text"] == "Hello"


def test_to_dict_recovers_from_empty_xmlschema_payload(monkeypatch):
    """Fallback conversion fills in data when xmlschema returns empty payload."""

    namespace = schema_loader.INSTANCE_NAMESPACE
    element = schema_loader.create_element(f"{{{namespace}}}Root")
    child = schema_loader.create_element(f"{{{namespace}}}Child")
    child.text = "value"
    element.append(child)

    class FakeSchema:
        def to_dict(self, *_, **__):
            return {element.tag: {}}

    class FakeConverter:
        def __init__(self, **kwargs: Any) -> None:
            pass

    @dataclass
    class _SchemaFactory:
        schema: Any

        def __call__(self, *args: Any, **kwargs: Any):
            return self.schema

        def cache_clear(self):
            pass

    monkeypatch.setattr(schema_loader, "xmlschema", object())
    monkeypatch.setattr(schema_loader, "XMLSchemaConverter", FakeConverter)
    monkeypatch.setattr(schema_loader, "get_schema", _SchemaFactory(FakeSchema()))

    result = schema_loader.to_dict(element, process_namespaces=True)

    assert result == {f"{{{namespace}}}Child": "value"}


def test_to_dict_uses_fallback_when_element_check_reports_empty(monkeypatch):
    """Fallback conversion is used even if element inspection suggests emptiness."""

    namespace = schema_loader.INSTANCE_NAMESPACE
    element = schema_loader.create_element(f"{{{namespace}}}Root")
    child = schema_loader.create_element(f"{{{namespace}}}Child")
    child.text = "value"
    element.append(child)

    class FakeSchema:
        def to_dict(self, *_args: Any, **_kwargs: Any):
            return {}

    class FakeConverter:
        def __init__(self, **_kwargs: Any) -> None:
            pass

    @dataclass
    class _SchemaFactory:
        schema: Any

        def __call__(self, *args: Any, **kwargs: Any):
            return self.schema

        def cache_clear(self):
            pass

    monkeypatch.setattr(schema_loader, "xmlschema", object())
    monkeypatch.setattr(schema_loader, "XMLSchemaConverter", FakeConverter)
    monkeypatch.setattr(schema_loader, "get_schema", _SchemaFactory(FakeSchema()))
    monkeypatch.setattr(
        schema_loader._conversion, "_element_has_content", lambda _elem: False
    )

    result = schema_loader.to_dict(element, process_namespaces=True)

    assert result == {f"{{{namespace}}}Child": "value"}


def test_to_dict_retains_raw_payload_when_normalization_drops_data(monkeypatch):
    """Fallback conversion returns raw element mapping when normalization empties it."""

    namespace = schema_loader.INSTANCE_NAMESPACE
    element = schema_loader.create_element(f"{{{namespace}}}Root")
    child = schema_loader.create_element(f"{{{namespace}}}Child")
    child.text = "value"
    element.append(child)

    class FakeSchema:
        def to_dict(self, *_args: Any, **_kwargs: Any):
            return {element.tag: {}}

    class FakeConverter:
        def __init__(self, **_kwargs: Any) -> None:
            pass

    @dataclass
    class _SchemaFactory:
        schema: Any

        def __call__(self, *args: Any, **kwargs: Any):
            return self.schema

        def cache_clear(self):
            pass

    def _always_empty_normalize(*_args: Any, **_kwargs: Any):
        return {}

    monkeypatch.setattr(schema_loader, "xmlschema", object())
    monkeypatch.setattr(schema_loader, "XMLSchemaConverter", FakeConverter)
    monkeypatch.setattr(schema_loader, "get_schema", _SchemaFactory(FakeSchema()))
    monkeypatch.setattr(
        schema_loader._conversion,
        "_normalize_result_namespaces",
        _always_empty_normalize,
    )

    result = schema_loader.to_dict(element, process_namespaces=True)

    assert result == {f"{{{namespace}}}Child": "value"}


def test_to_dict_treats_whitespace_only_payloads_as_empty(monkeypatch):
    """Whitespace-only payloads from xmlschema trigger the raw fallback mapping."""

    namespace = schema_loader.INSTANCE_NAMESPACE
    element = schema_loader.create_element(f"{{{namespace}}}Root")
    child = schema_loader.create_element(f"{{{namespace}}}Child")
    child.text = "value"
    element.append(child)

    class FakeSchema:
        def to_dict(self, *_args: Any, **_kwargs: Any):
            return {element.tag: {"#text": "   "}}

    class FakeConverter:
        def __init__(self, **_kwargs: Any) -> None:
            pass

    @dataclass
    class _SchemaFactory:
        schema: Any

        def __call__(self, *args: Any, **kwargs: Any):
            return self.schema

        def cache_clear(self):
            pass

    monkeypatch.setattr(schema_loader, "xmlschema", object())
    monkeypatch.setattr(schema_loader, "XMLSchemaConverter", FakeConverter)
    monkeypatch.setattr(schema_loader, "get_schema", _SchemaFactory(FakeSchema()))

    result = schema_loader.to_dict(element, process_namespaces=True)

    assert result == {f"{{{namespace}}}Child": "value"}


def test_to_dict_logs_xmlschema_validation_errors(monkeypatch, caplog):
    """xmlschema validation errors are logged for troubleshooting."""

    namespace = schema_loader.INSTANCE_NAMESPACE
    element = schema_loader.create_element(f"{{{namespace}}}Root")
    child = schema_loader.create_element(f"{{{namespace}}}Child")
    child.text = "value"
    element.append(child)

    class FakeSchema:
        def to_dict(self, *_args: Any, **_kwargs: Any):
            return ({element.tag: {child.tag: child.text}}, [ValueError("boom")])

    class FakeConverter:
        def __init__(self, **_kwargs: Any) -> None:
            pass

    @dataclass
    class _SchemaFactory:
        schema: Any

        def __call__(self, *args: Any, **kwargs: Any):
            return self.schema

        def cache_clear(self):
            pass

    monkeypatch.setattr(schema_loader, "xmlschema", object())
    monkeypatch.setattr(schema_loader, "XMLSchemaConverter", FakeConverter)
    monkeypatch.setattr(schema_loader, "get_schema", _SchemaFactory(FakeSchema()))

    with caplog.at_level(logging.DEBUG, logger="ddi_l.schema_loader._conversion"):
        result = schema_loader.to_dict(element, process_namespaces=True)

    assert result == {child.tag: child.text}
    assert any(
        "xmlschema returned validation errors" in message for message in caplog.messages
    ), "Expected xmlschema validation error log entry"
