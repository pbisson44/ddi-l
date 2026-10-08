"""Regression tests for xmlschema helper compatibility."""

from __future__ import annotations

import importlib
import sys
import types

import pytest

from tests import PACKAGE_FIXTURES_DIR


def test_document_to_dict_without_qname_helper():
    """Ensure DDIDocument.to_dict works when helper is missing."""

    try:
        real_xmlschema = importlib.import_module("xmlschema")
    except ModuleNotFoundError:
        real_xmlschema = None
    else:  # pragma: no cover - depends on external package state
        helpers = getattr(real_xmlschema, "helpers", None)
        if (
            helpers is not None
            and getattr(helpers, "qname_to_clark_notation", None) is not None
        ):
            pytest.skip("xmlschema still provides qname_to_clark_notation")

    preserved: dict[str, types.ModuleType] = {}
    for name in [
        "xmlschema",
        "xmlschema.converters",
        "xmlschema.validators",
        "xmlschema.validators.exceptions",
        "xmlschema.helpers",
        "ddi_l.schema_loader",
        "ddi_l.document",
    ]:
        module = sys.modules.pop(name, None)
        if module is not None:
            preserved[name] = module

    stubbed_modules = set()

    if real_xmlschema is None:
        stub_xmlschema = types.ModuleType("xmlschema")
        stub_xmlschema.__dict__["__all__"] = []

        class _StubXMLSchema:
            def __init__(self, _path):
                """Stub schema storing namespace mappings for tests."""
                self.namespaces = {
                    None: "ddi:instance:3_3",
                    "": "ddi:instance:3_3",
                    "r": "ddi:reusable:3_3",
                    "xml": "http://www.w3.org/XML/1998/namespace",
                }

            def validate(self, _document):
                """Pretend to validate without raising to emulate success."""
                return None

            def to_dict(self, element, *, process_namespaces, converter):
                """Convert elements to dicts using provided converter stubs."""

                def convert(name: str) -> str:
                    """Convert Clark-notation names using optional converter."""
                    if converter.map_qnames and converter.qname_converter is not None:
                        return converter.qname_converter(name, {})
                    return name

                result: dict[str, object] = {}

                for attr_name, attr_value in element.attrib.items():
                    key = f"{converter.attr_prefix}{convert(attr_name)}"
                    result[key] = attr_value

                for child in list(element):
                    key = convert(child.tag)
                    value = self.to_dict(
                        child,
                        process_namespaces=process_namespaces,
                        converter=converter,
                    )
                    if key in result:
                        current = result[key]
                        if isinstance(current, list):
                            current.append(value)
                        else:
                            result[key] = [current, value]
                    else:
                        result[key] = value

                if result:
                    if element.text is not None:
                        result[converter.text_key] = element.text
                    return result

                return element.text or ""

        stub_xmlschema.XMLSchema = _StubXMLSchema  # type: ignore[attr-defined]

        stub_converters = types.ModuleType("xmlschema.converters")

        class _StubXMLSchemaConverter:
            def __init__(
                self,
                *,
                map_qnames: bool = False,
                attr_prefix: str = "@",
                text_key: str = "#text",
                qname_converter=None,
            ) -> None:
                """Store converter configuration flags for stub conversions."""
                self.map_qnames = map_qnames
                self.attr_prefix = attr_prefix
                self.text_key = text_key
                self.qname_converter = qname_converter

        stub_converters.XMLSchemaConverter = _StubXMLSchemaConverter  # type: ignore[attr-defined]

        stub_exceptions = types.ModuleType("xmlschema.validators.exceptions")

        class _StubXMLSchemaValidationError(Exception):
            pass

        stub_exceptions.XMLSchemaValidationError = _StubXMLSchemaValidationError  # type: ignore[attr-defined]

        stub_validators = types.ModuleType("xmlschema.validators")
        stub_validators.exceptions = stub_exceptions  # type: ignore[attr-defined]

        stub_helpers = types.ModuleType("xmlschema.helpers")

        for module in (
            stub_xmlschema,
            stub_converters,
            stub_validators,
            stub_exceptions,
            stub_helpers,
        ):
            sys.modules[module.__name__] = module
            stubbed_modules.add(module.__name__)

        stub_xmlschema.converters = stub_converters  # type: ignore[attr-defined]
        stub_xmlschema.validators = stub_validators  # type: ignore[attr-defined]
        stub_xmlschema.helpers = stub_helpers  # type: ignore[attr-defined]

    try:
        document_module = importlib.import_module("ddi_l.document")
        DDIDocument = document_module.DDIDocument

        source = PACKAGE_FIXTURES_DIR / "minimal_instance.xml"
        document = DDIDocument.from_xml(source)
        data = document.to_dict()

        def assert_no_prefixed_keys(obj):
            """Ensure nested mapping/list structures have no prefixed keys."""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    candidate = key[1:] if key.startswith("@") else key
                    if not candidate.startswith("#"):
                        assert not (
                            ":" in candidate and not candidate.startswith("{")
                        ), f"Unexpected prefixed key: {key}"
                    assert_no_prefixed_keys(value)
            elif isinstance(obj, list):
                for item in obj:
                    assert_no_prefixed_keys(item)

        assert data["{ddi:reusable:3_3}Agency"] == "example.agency"
        assert_no_prefixed_keys(data)

        from ddi_l import schema_loader as reloaded_schema_loader

        original_xmlschema = reloaded_schema_loader.xmlschema
        original_converter = reloaded_schema_loader.XMLSchemaConverter
        try:
            reloaded_schema_loader.xmlschema = None
            reloaded_schema_loader.XMLSchemaConverter = None
            fallback_data = reloaded_schema_loader.to_dict(
                document.root, process_namespaces=True
            )
        finally:
            reloaded_schema_loader.xmlschema = original_xmlschema
            reloaded_schema_loader.XMLSchemaConverter = original_converter

        assert fallback_data["{ddi:reusable:3_3}Agency"] == "example.agency"
        assert_no_prefixed_keys(fallback_data)
    finally:
        for name in stubbed_modules:
            sys.modules.pop(name, None)
        for name, module in preserved.items():
            sys.modules[name] = module
