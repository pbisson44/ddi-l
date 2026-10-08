# mypy: ignore-errors
"""Tests for schema_loader/_versions.py — version detection and normalization."""

from __future__ import annotations

import xml.etree.ElementTree as _StdlibET

import pytest

from ddi_l._etree import create_element
from ddi_l._schema_versions import DEFAULT_SCHEMA_VERSION, SCHEMA_RELEASES
from ddi_l.constants import INSTANCE_NS, XSI_NS
from ddi_l.schema_loader._versions import (
    _detect_from_namespace,
    _detect_from_schema_location,
    _extract_namespace,
    detect_version_from_element,
    detect_version_from_mapping,
    normalize_version,
)

# ===========================================================================
# normalize_version
# ===========================================================================


class TestNormalizeVersion:
    def test_none_returns_default(self):
        assert normalize_version(None) == DEFAULT_SCHEMA_VERSION

    def test_valid_version(self):
        for version in SCHEMA_RELEASES:
            assert normalize_version(version) == version

    def test_invalid_version_raises(self):
        with pytest.raises(ValueError, match="Unsupported DDI schema version"):
            normalize_version("9.9")


# ===========================================================================
# _extract_namespace
# ===========================================================================


class TestExtractNamespace:
    def test_clark_notation(self):
        assert _extract_namespace("{http://example.org}Root") == "http://example.org"

    def test_no_namespace(self):
        assert _extract_namespace("Root") is None

    def test_empty_string(self):
        assert _extract_namespace("") is None


# ===========================================================================
# _detect_from_namespace
# ===========================================================================


class TestDetectFromNamespace:
    def test_known_namespace(self):
        result = _detect_from_namespace(INSTANCE_NS)
        assert result is not None
        assert result in SCHEMA_RELEASES

    def test_unknown_namespace(self):
        assert _detect_from_namespace("http://unknown.example.org") is None

    def test_none_namespace(self):
        assert _detect_from_namespace(None) is None


# ===========================================================================
# _detect_from_schema_location
# ===========================================================================


class TestDetectFromSchemaLocation:
    def test_matching_filename(self):
        for version, release in SCHEMA_RELEASES.items():
            location = f"http://example.org/{release['schema_filename']}"
            assert _detect_from_schema_location(location) == version
            break  # test at least one

    def test_matching_namespace(self):
        for _version, release in SCHEMA_RELEASES.items():
            location = release["namespaces"]["instance"]
            result = _detect_from_schema_location(location)
            assert result is not None
            break

    def test_no_match(self):
        assert _detect_from_schema_location("http://example.org/nothing.xsd") is None


# ===========================================================================
# detect_version_from_element
# ===========================================================================


class TestDetectVersionFromElement:
    def test_from_tag_namespace(self):
        el = create_element(f"{{{INSTANCE_NS}}}DDIInstance")
        version = detect_version_from_element(el)
        assert version is not None
        assert version in SCHEMA_RELEASES

    def test_from_schema_location_attr(self):
        el = create_element("DDIInstance")
        for _version, release in SCHEMA_RELEASES.items():
            el.set(
                f"{{{XSI_NS}}}schemaLocation",
                f"{release['namespaces']['instance']} {release['schema_filename']}",
            )
            break
        result = detect_version_from_element(el)
        assert result is not None

    def test_from_no_namespace_schema_location(self):
        el = create_element("DDIInstance")
        for _version, release in SCHEMA_RELEASES.items():
            el.set(
                f"{{{XSI_NS}}}noNamespaceSchemaLocation",
                release["schema_filename"],
            )
            break
        result = detect_version_from_element(el)
        assert result is not None

    def test_from_plain_schema_location(self):
        el = create_element("DDIInstance")
        for _version, release in SCHEMA_RELEASES.items():
            el.set("schemaLocation", release["schema_filename"])
            break
        result = detect_version_from_element(el)
        assert result is not None

    def test_from_xmlns_attribute(self):
        el = create_element("DDIInstance")
        el.set("xmlns", INSTANCE_NS)
        result = detect_version_from_element(el)
        assert result is not None

    def test_from_xmlns_prefixed_attribute(self):
        # A literal ``xmlns:`` attribute is how the stdlib backend carries a
        # namespace declaration; lxml rejects it as an attribute name, so this
        # path needs a stdlib element regardless of the installed backend.
        el = _StdlibET.Element("DDIInstance")
        el.set("xmlns:ddi", INSTANCE_NS)
        result = detect_version_from_element(el)
        assert result is not None

    def test_from_xmlns_w3c_namespace(self):
        el = create_element("DDIInstance")
        el.set("{http://www.w3.org/2000/xmlns/}ddi", INSTANCE_NS)
        result = detect_version_from_element(el)
        assert result is not None

    def test_unknown_element(self):
        el = create_element("Unknown")
        assert detect_version_from_element(el) is None

    def test_non_string_attr_value(self):
        """Element with non-string tag should not crash."""
        el = create_element("Root")
        # All standard attributes are strings, so this just tests graceful handling
        result = detect_version_from_element(el)
        assert result is None


# ===========================================================================
# detect_version_from_mapping
# ===========================================================================


class TestDetectVersionFromMapping:
    def test_empty_mapping(self):
        assert detect_version_from_mapping({}) is None

    def test_from_root_tag_namespace(self):
        data = {f"{{{INSTANCE_NS}}}DDIInstance": {"some": "data"}}
        result = detect_version_from_mapping(data)
        assert result is not None
        assert result in SCHEMA_RELEASES

    def test_from_schema_location_in_payload(self):
        for _version, release in SCHEMA_RELEASES.items():
            data = {
                "DDIInstance": {
                    f"@{{{XSI_NS}}}schemaLocation": release["schema_filename"],
                }
            }
            result = detect_version_from_mapping(data)
            assert result is not None
            break

    def test_from_no_namespace_schema_location_in_payload(self):
        for _version, release in SCHEMA_RELEASES.items():
            data = {
                "DDIInstance": {
                    f"@{{{XSI_NS}}}noNamespaceSchemaLocation": release[
                        "schema_filename"
                    ],
                }
            }
            result = detect_version_from_mapping(data)
            assert result is not None
            break

    def test_from_plain_schema_location_in_payload(self):
        for _version, release in SCHEMA_RELEASES.items():
            data = {"DDIInstance": {"@schemaLocation": release["schema_filename"]}}
            result = detect_version_from_mapping(data)
            assert result is not None
            break

    def test_from_xmlns_attribute_in_payload(self):
        data = {"DDIInstance": {"@xmlns:ddi": INSTANCE_NS}}
        result = detect_version_from_mapping(data)
        assert result is not None

    def test_multiple_keys_returns_none(self):
        data = {"key1": "val1", "key2": "val2"}
        assert detect_version_from_mapping(data) is None

    def test_non_string_attribute_value_skipped(self):
        data = {"DDIInstance": {"@xmlns": 12345}}
        result = detect_version_from_mapping(data)
        assert result is None

    def test_non_string_key_skipped(self):
        data = {"DDIInstance": {"non-attr-key": "value"}}
        result = detect_version_from_mapping(data)
        assert result is None

    def test_non_mapping_payload(self):
        data = {f"{{{INSTANCE_NS}}}DDIInstance": "just-a-string"}
        result = detect_version_from_mapping(data)
        assert result is not None  # detected from tag namespace


def test_schema_namespaces_match_the_bundled_xsds() -> None:
    """The declared namespace list must match what the XSDs actually declare.

    The expected set is derived from the shipped schemas; a second copy of the
    list lives in ``codegen/xsd_introspect.py``.
    """
    import re
    from pathlib import Path

    from ddi_l._schema_versions import _SCHEMA_NAMESPACE_TEMPLATES

    schema_dir = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "ddi_l"
        / "schemas"
        / "ddi"
        / "v3_3"
    )
    declared = {
        match.group(1)
        for path in schema_dir.glob("*.xsd")
        for match in re.finditer(
            r'targetNamespace="ddi:([a-z_]+):3_3"', path.read_text(encoding="utf-8")
        )
    }
    expected = set(_SCHEMA_NAMESPACE_TEMPLATES)

    assert declared == expected, (
        f"only in the XSDs: {sorted(declared - expected)}; "
        f"only in _SCHEMA_NAMESPACE_TEMPLATES: {sorted(expected - declared)}"
    )


def test_codegen_and_runtime_agree_on_schema_namespaces() -> None:
    """``codegen`` and the runtime must not keep divergent namespace lists."""
    import re
    from pathlib import Path

    from ddi_l._schema_versions import _SCHEMA_NAMESPACE_TEMPLATES

    codegen_source = (
        Path(__file__).resolve().parents[1] / "codegen" / "xsd_introspect.py"
    ).read_text(encoding="utf-8")
    codegen_namespaces = set(re.findall(r'"ddi:([a-z_]+):3_3"', codegen_source))

    assert codegen_namespaces == set(_SCHEMA_NAMESPACE_TEMPLATES), (
        f"only in codegen: {sorted(codegen_namespaces - set(_SCHEMA_NAMESPACE_TEMPLATES))}; "
        f"only in runtime: {sorted(set(_SCHEMA_NAMESPACE_TEMPLATES) - codegen_namespaces)}"
    )
