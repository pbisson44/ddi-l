"""Edge cases and error paths in ddi_l.schema_loader._conversion."""

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.models.base import qn
from ddi_l.schema_loader._constants import XMLNS_NAMESPACE
from ddi_l.schema_loader._conversion import (
    _align_mapping_with_element,
    _append_child,
    _build_element_from_mapping,
    _collapse_single_item_lists,
    _collapse_text_nodes,
    _collect_declared_namespaces,
    _dict_to_element,
    _element_has_content,
    _element_to_dict,
    _has_payload,
    _normalize_boolean_attributes,
    _prepare_nsmap,
    _prune_schema_defaults_from_element,
    _remove_namespace_declarations,
    _schema_namespace_defaults,
    from_dict,
    to_dict,
)

# ---------------------------------------------------------------------------
# _element_to_dict
# ---------------------------------------------------------------------------


def test_element_to_dict_simple():
    elem = create_element("root")
    elem.text = "hello"
    result = _element_to_dict(elem)
    assert result == "hello"


def test_element_to_dict_empty():
    elem = create_element("root")
    result = _element_to_dict(elem)
    assert result == ""


def test_element_to_dict_with_children():
    root = create_element("root")
    child = create_element("child")
    child.text = "value"
    root.append(child)
    result = _element_to_dict(root)
    assert isinstance(result, dict)
    assert result["child"] == "value"


def test_element_to_dict_duplicate_children():
    root = create_element("root")
    c1 = create_element("item")
    c1.text = "a"
    c2 = create_element("item")
    c2.text = "b"
    root.append(c1)
    root.append(c2)
    result = _element_to_dict(root)
    assert isinstance(result["item"], list)  # type: ignore[index]
    assert len(result["item"]) == 2  # type: ignore[index]


def test_element_to_dict_with_attributes():
    root = create_element("root")
    root.set("id", "123")
    child = create_element("child")
    child.text = "value"
    root.append(child)
    result = _element_to_dict(root)
    assert result["@id"] == "123"  # type: ignore[index]


def test_element_to_dict_with_text_and_children():
    root = create_element("root")
    root.text = "text"
    child = create_element("child")
    child.text = "value"
    root.append(child)
    result = _element_to_dict(root)
    assert result["#text"] == "text"  # type: ignore[index]
    assert result["child"] == "value"  # type: ignore[index]


def test_element_to_dict_no_namespace_processing():
    root = create_element("root")
    root.text = "hello"
    result = _element_to_dict(root, process_namespaces=False)
    assert result == "hello"


# ---------------------------------------------------------------------------
# _remove_namespace_declarations
# ---------------------------------------------------------------------------


def test_remove_namespace_declarations():
    data = {
        f"@{{{XMLNS_NAMESPACE}}}r": "ddi:reusable:3_3",
        "@id": "123",
        "child": "value",
    }
    result = _remove_namespace_declarations(data)
    assert f"@{{{XMLNS_NAMESPACE}}}r" not in result
    assert result["@id"] == "123"


def test_remove_namespace_declarations_list():
    data = [{"@id": "1"}, {"@id": "2"}]
    result = _remove_namespace_declarations(data)
    assert len(result) == 2


def test_remove_namespace_declarations_scalar():
    assert _remove_namespace_declarations("hello") == "hello"


# ---------------------------------------------------------------------------
# _normalize_boolean_attributes
# ---------------------------------------------------------------------------


def test_normalize_boolean_true():
    result = _normalize_boolean_attributes({"@isRequired": "true"})
    assert result["@isRequired"] is True


def test_normalize_boolean_false():
    result = _normalize_boolean_attributes({"@isRequired": "False"})
    assert result["@isRequired"] is False


def test_normalize_boolean_non_attr():
    result = _normalize_boolean_attributes({"name": "true"})
    assert result["name"] == "true"


def test_normalize_boolean_list():
    result = _normalize_boolean_attributes([{"@a": "true"}, {"@b": "false"}])
    assert result[0]["@a"] is True
    assert result[1]["@b"] is False


def test_normalize_boolean_scalar():
    assert _normalize_boolean_attributes(42) == 42


# ---------------------------------------------------------------------------
# _collapse_text_nodes
# ---------------------------------------------------------------------------


def test_collapse_text_only():
    result = _collapse_text_nodes({"#text": "hello"})
    assert result == "hello"


def test_collapse_text_with_other_keys():
    result = _collapse_text_nodes({"#text": "hello", "child": "val"})
    assert result == {"#text": "hello", "child": "val"}


def test_collapse_text_list():
    result = _collapse_text_nodes([{"#text": "a"}, {"#text": "b"}])
    assert result == ["a", "b"]


def test_collapse_text_scalar():
    assert _collapse_text_nodes(42) == 42


# ---------------------------------------------------------------------------
# _collapse_single_item_lists
# ---------------------------------------------------------------------------


def test_collapse_single_item_list():
    assert _collapse_single_item_lists(["only"]) == "only"


def test_collapse_multi_item_list():
    assert _collapse_single_item_lists(["a", "b"]) == ["a", "b"]


def test_collapse_single_item_nested_dict():
    result = _collapse_single_item_lists({"items": ["one"]})
    assert result == {"items": "one"}


def test_collapse_scalar():
    assert _collapse_single_item_lists(42) == 42


# ---------------------------------------------------------------------------
# _element_has_content / _has_payload
# ---------------------------------------------------------------------------


def test_element_has_content_with_attrib():
    elem = create_element("root")
    elem.set("id", "1")
    assert _element_has_content(elem) is True


def test_element_has_content_with_children():
    elem = create_element("root")
    elem.append(create_element("child"))
    assert _element_has_content(elem) is True


def test_element_has_content_with_text():
    elem = create_element("root")
    elem.text = "hello"
    assert _element_has_content(elem) is True


def test_element_has_content_empty():
    elem = create_element("root")
    assert _element_has_content(elem) is False


def test_has_payload_bool():
    assert _has_payload(True) is True
    assert _has_payload(False) is True


def test_has_payload_number():
    assert _has_payload(42) is True
    assert _has_payload(0.0) is True


def test_has_payload_string():
    assert _has_payload("hello") is True
    assert _has_payload("") is False
    assert _has_payload("   ") is False


def test_has_payload_mapping():
    assert _has_payload({"key": "value"}) is True
    assert _has_payload({"#text": ""}) is False
    assert _has_payload({"#text": "  "}) is False


def test_has_payload_list():
    assert _has_payload(["a"]) is True
    assert _has_payload([]) is False
    assert _has_payload([""]) is False


def test_has_payload_none():
    assert _has_payload(None) is False


# ---------------------------------------------------------------------------
# _prepare_nsmap
# ---------------------------------------------------------------------------


def test_prepare_nsmap_none():
    assert _prepare_nsmap(None) is None


def test_prepare_nsmap_empty():
    assert _prepare_nsmap({}) is None


def test_prepare_nsmap_filters_xmlns():
    result = _prepare_nsmap({"xmlns": "http://ns", "r": "http://r"})
    assert "xmlns" not in result  # type: ignore[operator]
    assert result["r"] == "http://r"  # type: ignore[index]


def test_prepare_nsmap_empty_string_prefix():
    result = _prepare_nsmap({"": "http://default", "r": "http://r"})
    assert result.get(None) == "http://default"  # type: ignore[union-attr]


def test_prepare_nsmap_none_prefix():
    result = _prepare_nsmap({None: "http://default"})
    assert result.get(None) == "http://default"  # type: ignore[union-attr]


def test_prepare_nsmap_empty_uri():
    result = _prepare_nsmap({"r": ""})
    assert result is None


# ---------------------------------------------------------------------------
# _collect_declared_namespaces
# ---------------------------------------------------------------------------


def test_collect_declared_namespaces_xmlns():
    data = {"@xmlns": "http://default"}
    result = _collect_declared_namespaces(data)
    assert result[None] == "http://default"


def test_collect_declared_namespaces_prefixed():
    data = {"@xmlns:r": "http://r"}
    result = _collect_declared_namespaces(data)
    assert result["r"] == "http://r"


def test_collect_declared_namespaces_clark():
    data = {f"@{{{XMLNS_NAMESPACE}}}r": "http://r"}
    result = _collect_declared_namespaces(data)
    assert result["r"] == "http://r"


def test_collect_declared_namespaces_clark_default():
    data = {f"@{{{XMLNS_NAMESPACE}}}": "http://default"}
    result = _collect_declared_namespaces(data)
    assert result[None] == "http://default"


def test_collect_declared_namespaces_nested():
    data = {"child": {"@xmlns:l": "http://l"}}
    result = _collect_declared_namespaces(data)
    assert result["l"] == "http://l"


def test_collect_declared_namespaces_list():
    data = [{"@xmlns:a": "http://a"}, {"@xmlns:b": "http://b"}]
    result = _collect_declared_namespaces(data)
    assert "a" in result
    assert "b" in result


# ---------------------------------------------------------------------------
# _build_element_from_mapping
# ---------------------------------------------------------------------------


def test_build_element_scalar():
    elem = _build_element_from_mapping("root", "hello", process_namespaces=False)
    assert elem.tag == "root"
    assert elem.text == "hello"


def test_build_element_dict():
    elem = _build_element_from_mapping(
        "root",
        {"child": "value", "#text": "text", "@id": "1"},
        process_namespaces=False,
    )
    assert elem.tag == "root"
    assert elem.get("id") == "1"
    assert elem.text == "text"
    assert len(list(elem)) == 1


def test_build_element_list_children():
    elem = _build_element_from_mapping(
        "root",
        {"item": ["a", "b"]},
        process_namespaces=False,
    )
    children = list(elem)
    assert len(children) == 2


def test_build_element_clark_attribute():
    elem = _build_element_from_mapping(
        "root",
        {"@{http://ns}attr": "val"},
        process_namespaces=True,
    )
    assert elem.get("{http://ns}attr") == "val"


# ---------------------------------------------------------------------------
# _dict_to_element
# ---------------------------------------------------------------------------


def test_dict_to_element_simple():
    elem = _dict_to_element({"root": "hello"}, process_namespaces=False)
    assert elem.tag == "root"
    assert elem.text == "hello"


def test_dict_to_element_multi_key_error():
    with pytest.raises(ValueError, match="single XML element"):
        _dict_to_element({"a": "1", "b": "2"}, process_namespaces=False)


# ---------------------------------------------------------------------------
# _prune_schema_defaults_from_element
# ---------------------------------------------------------------------------


def test_prune_schema_defaults_removes_extra_attrs():
    elem = create_element("root")
    elem.set("id", "1")
    elem.set("extra", "2")
    payload = {"@id": "1"}
    _prune_schema_defaults_from_element(elem, payload)
    assert elem.get("id") == "1"
    assert elem.get("extra") is None


def test_prune_schema_defaults_removes_extra_children():
    elem = create_element("root")
    child1 = create_element("kept")
    child2 = create_element("removed")
    elem.append(child1)
    elem.append(child2)
    payload = {"kept": "value"}
    _prune_schema_defaults_from_element(elem, payload)
    tags = [c.tag for c in elem]
    assert "kept" in tags
    assert "removed" not in tags


def test_prune_schema_defaults_non_mapping():
    elem = create_element("root")
    _prune_schema_defaults_from_element(elem, "scalar")
    # Should not raise


# ---------------------------------------------------------------------------
# _append_child
# ---------------------------------------------------------------------------


def test_append_child_new_key():
    result = {}  # type: ignore[var-annotated]
    _append_child(result, "a", "1")
    assert result["a"] == "1"


def test_append_child_existing_scalar():
    result = {"a": "1"}
    _append_child(result, "a", "2")
    assert result["a"] == ["1", "2"]


def test_append_child_existing_list():
    result = {"a": ["1", "2"]}
    _append_child(result, "a", "3")
    assert result["a"] == ["1", "2", "3"]


# ---------------------------------------------------------------------------
# _align_mapping_with_element
# ---------------------------------------------------------------------------


def test_align_mapping_none_element():
    data = {"child": "value"}
    result = _align_mapping_with_element(data, None)
    assert result == {"child": "value"}


def test_align_mapping_scalar():
    assert _align_mapping_with_element("hello", None) == "hello"


def test_align_mapping_list_with_none():
    result = _align_mapping_with_element(["a", "b"], None)
    assert result == ["a", "b"]


# ---------------------------------------------------------------------------
# _schema_namespace_defaults
# ---------------------------------------------------------------------------


def test_schema_namespace_defaults_no_schema():
    result = _schema_namespace_defaults(None)
    assert "xml" in result
    assert "xmlns" in result


def test_schema_namespace_defaults_with_schema_namespaces():
    class FakeSchema:
        namespaces = {"r": "http://reusable", "": "http://default"}

    result = _schema_namespace_defaults(FakeSchema())
    assert result.get(None) == "http://default"
    assert result.get("r") == "http://reusable"


# ---------------------------------------------------------------------------
# from_dict / to_dict (high-level)
# ---------------------------------------------------------------------------


def test_from_dict_simple():
    root_tag = qn(INSTANCE_NS, "DDIInstance")
    data = {
        root_tag: {
            qn(REUSABLE_NS, "Agency"): "test.org",
            qn(REUSABLE_NS, "ID"): "doc1",
            qn(REUSABLE_NS, "Version"): "1.0",
        }
    }
    elem = from_dict(data)
    assert elem.tag == root_tag


def test_to_dict_roundtrip():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    agency = create_element(qn(REUSABLE_NS, "Agency"))
    agency.text = "test.org"
    root.append(agency)
    id_elem = create_element(qn(REUSABLE_NS, "ID"))
    id_elem.text = "doc1"
    root.append(id_elem)
    version = create_element(qn(REUSABLE_NS, "Version"))
    version.text = "1.0"
    root.append(version)
    result = to_dict(root)
    assert isinstance(result, dict)
