# mypy: ignore-errors
"""Tests for schema_loader/_fallback.py — fallback schema validation and conversion."""

from __future__ import annotations

from pathlib import Path

import pytest

from ddi_l._etree import fromstring
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.schema_loader._fallback import _FallbackSchema


@pytest.fixture
def fallback():
    """Create a fallback schema for DDI 3.3."""
    return _FallbackSchema(path=Path("."), version="3.3")


class _CoordinateNode:
    """Stand-in for the assorted node objects ``_node_coordinates`` accepts.

    That helper reads ``sourceline`` / ``sourcecolumn`` / ``position`` off
    whatever the validator hands it, which is a real element for one backend
    and an xmlschema error node for another. Real lxml elements cannot stand
    in here: ``sourceline`` is a typed read-only property and ``position``
    cannot be assigned at all, so the duck-typed contract needs a duck.
    """

    def __init__(self, **attributes: object) -> None:
        for name, value in attributes.items():
            setattr(self, name, value)


class TestFallbackSchemaInit:
    def test_creates_namespace_map(self, fallback):
        assert fallback.instance_namespace == INSTANCE_NS
        assert fallback.reusable_namespace == REUSABLE_NS
        assert fallback.instance_tag == f"{{{INSTANCE_NS}}}DDIInstance"
        assert fallback.fragment_tag == f"{{{INSTANCE_NS}}}FragmentInstance"
        assert fallback.namespaces is not None
        assert len(fallback.namespaces) > 0

    def test_custom_namespaces_preserved(self):
        custom = {"custom": "http://custom"}
        fb = _FallbackSchema(path=Path("."), version="3.3", namespaces=custom)
        # Custom namespaces should remain (with additions from __post_init__)
        assert "custom" in fb.namespaces


class TestNodeCoordinates:
    def test_none_node(self, fallback):
        assert fallback._node_coordinates(None) == (None, None)

    def test_int_sourceline(self, fallback):
        el = _CoordinateNode(sourceline=42)
        line, _col = fallback._node_coordinates(el)
        assert line == 42

    def test_str_sourceline(self, fallback):
        el = _CoordinateNode(sourceline="10")
        line, _ = fallback._node_coordinates(el)
        assert line == 10

    def test_invalid_str_sourceline(self, fallback):
        el = _CoordinateNode(sourceline="not-a-number")
        line, _ = fallback._node_coordinates(el)
        # Falls back to position tuple or None
        assert line is None

    def test_position_tuple(self, fallback):
        el = _CoordinateNode(position=(5, 10))
        line, col = fallback._node_coordinates(el)
        assert line == 5
        assert col == 10

    def test_position_tuple_partial(self, fallback):
        el = _CoordinateNode(position=(7,))
        line, col = fallback._node_coordinates(el)
        assert line == 7
        assert col is None

    def test_position_non_int(self, fallback):
        el = _CoordinateNode(position=("abc", "def"))
        line, col = fallback._node_coordinates(el)
        assert line is None
        assert col is None


class TestValidate:
    def test_valid_instance(self, fallback):
        xml = f"""<DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>test.org</r:Agency>
            <r:ID>doc1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>"""
        fromstring(xml)
        # Should not raise
        fallback.validate(xml)

    def test_valid_fragment_instance(self, fallback):
        xml = f'<FragmentInstance xmlns="{INSTANCE_NS}"/>'
        # FragmentInstance doesn't require identification elements
        fallback.validate(xml)

    def test_invalid_root_tag(self, fallback):
        xml = f'<WrongRoot xmlns="{INSTANCE_NS}"/>'
        with pytest.raises(Exception):
            fallback.validate(xml)

    def test_missing_identification(self, fallback):
        xml = f'<DDIInstance xmlns="{INSTANCE_NS}"/>'
        with pytest.raises(Exception):
            fallback.validate(xml)


class TestToDict:
    def test_basic_conversion(self, fallback):
        xml = f"""<DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>test.org</r:Agency>
            <r:ID>doc1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>"""
        el = fromstring(xml)
        result = fallback.to_dict(el)
        assert isinstance(result, dict)

    def test_without_namespace_processing(self, fallback):
        xml = f"""<DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>test.org</r:Agency>
            <r:ID>doc1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>"""
        el = fromstring(xml)
        result = fallback.to_dict(el, process_namespaces=False)
        assert isinstance(result, dict)


class TestFromDict:
    def test_basic_conversion(self, fallback):
        data = {
            f"{{{INSTANCE_NS}}}DDIInstance": {
                f"{{{REUSABLE_NS}}}Agency": "test.org",
                f"{{{REUSABLE_NS}}}ID": "doc1",
                f"{{{REUSABLE_NS}}}Version": "1.0",
            }
        }
        el = fallback.from_dict(data)
        assert el.tag == f"{{{INSTANCE_NS}}}DDIInstance"

    def test_without_namespace_processing(self, fallback):
        data = {
            f"{{{INSTANCE_NS}}}DDIInstance": {
                f"{{{REUSABLE_NS}}}Agency": "test.org",
            }
        }
        el = fallback.from_dict(data, process_namespaces=False)
        assert el is not None
