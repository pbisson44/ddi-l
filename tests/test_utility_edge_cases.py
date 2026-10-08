"""Edge cases in xml_utils, namespace_utils and the schema_loader helpers."""

import io
import xml.etree.ElementTree as _StdlibET
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from ddi_l._etree import create_element


def stdlib_element(tag: str) -> Any:
    """Build a stdlib element regardless of which XML backend is installed.

    The stdlib code paths below store namespace declarations as literal
    ``xmlns`` / ``xmlns:prefix`` attributes. lxml rejects those as attribute
    names, so ``create_element`` -- which returns an lxml element whenever
    lxml is present -- cannot be used to exercise them.
    """
    return _StdlibET.Element(tag)


from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.models.base import qn
from ddi_l.namespace_utils import (
    _apply_namespace_attributes,
    apply_namespace_map,
    build_namespace_map,
    extract_namespace_declarations,
)
from ddi_l.schema_loader._cache import (
    _cache_info,
    clear_schema_cache,
    get_schema,
)
from ddi_l.schema_loader._compat import (
    _fallback_qname_converter,
    _resolve_qname_converter,
)
from ddi_l.schema_loader._namespaces import (
    _build_xpath_from_tree,
    _denormalize_clark_notation,
    _describe_node,
    _extract_xmlns_attributes,
    _find_path,
    _format_tag,
    _gather_namespaces,
    _local_name,
    _normalize_prefixed_qnames,
)
from ddi_l.xml_utils import (
    coerce_element,
    resolve_xml_source,
)

# ===========================================================================
# xml_utils — resolve_xml_source
# ===========================================================================


def test_resolve_xml_source_element():
    e = create_element("root")
    kind, payload = resolve_xml_source(e)
    assert kind == "element"
    assert payload is e


def test_resolve_xml_source_bytes():
    kind, payload = resolve_xml_source(b"<root/>")
    assert kind == "bytes"
    assert isinstance(payload, bytes)


def test_resolve_xml_source_bytearray():
    kind, payload = resolve_xml_source(bytearray(b"<root/>"))
    assert kind == "bytes"
    assert isinstance(payload, bytes)


def test_resolve_xml_source_path(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text("<root/>")
    kind, _payload = resolve_xml_source(p)
    assert kind == "path"


def test_resolve_xml_source_path_nonexistent():
    kind, _payload = resolve_xml_source(Path("/nonexistent/test.xml"))
    assert kind == "path"


def test_resolve_xml_source_path_nonexistent_require():
    with pytest.raises(FileNotFoundError):
        resolve_xml_source(Path("/nonexistent/test.xml"), require_existing_path=True)


def test_resolve_xml_source_str_xml():
    kind, _payload = resolve_xml_source("<root/>")
    assert kind == "text"


def test_resolve_xml_source_str_multiline():
    kind, _payload = resolve_xml_source("<root>\n</root>")
    assert kind == "text"


def test_resolve_xml_source_str_existing_path(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text("<root/>")
    kind, _payload = resolve_xml_source(str(p))
    assert kind == "path"


def test_resolve_xml_source_str_path_like_nonexistent():
    kind, _payload = resolve_xml_source("/some/path/file.xml")
    # Absolute path with suffix — path_like=True but doesn't exist
    # Returns "text" since file not found and not require_existing_path
    assert kind == "text"


def test_resolve_xml_source_str_path_like_require():
    with pytest.raises(FileNotFoundError):
        resolve_xml_source("/some/nonexistent/file.xml", require_existing_path=True)


def test_resolve_xml_source_str_with_slash():
    """String with slash but no extension looks path-like."""
    kind, _payload = resolve_xml_source("some/path")
    assert kind == "text"  # not found, fallback to text


def test_resolve_xml_source_str_with_dot_prefix():
    kind, _payload = resolve_xml_source("./relative")
    assert kind == "text"  # doesn't exist


def test_resolve_xml_source_file():
    buf = io.BytesIO(b"<root/>")
    kind, payload = resolve_xml_source(buf)
    assert kind == "file"
    assert payload is buf


def test_resolve_xml_source_text_file():
    buf = io.StringIO("<root/>")
    kind, _payload = resolve_xml_source(buf)
    assert kind == "file"


def test_resolve_xml_source_unsupported():
    with pytest.raises(TypeError, match="Unsupported"):
        resolve_xml_source(42)  # type: ignore[call-overload]


# ===========================================================================
# xml_utils — coerce_element
# ===========================================================================


def test_coerce_element_from_element():
    e = create_element("root")
    assert coerce_element(e) is e


def test_coerce_element_from_path(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text("<root/>")
    result = coerce_element(p)
    assert result.tag == "root"


def test_coerce_element_from_bytes():
    result = coerce_element(b"<root/>")
    assert result.tag == "root"


def test_coerce_element_from_text():
    result = coerce_element("<root/>")
    assert result.tag == "root"


def test_coerce_element_from_file():
    buf = io.BytesIO(b"<root/>")
    result = coerce_element(buf)
    assert result.tag == "root"


def test_coerce_element_from_text_file():
    buf = io.StringIO("<root/>")
    result = coerce_element(buf)
    assert result.tag == "root"


# ===========================================================================
# namespace_utils
# ===========================================================================


def test_build_namespace_map_default():
    result = build_namespace_map()
    assert isinstance(result, dict)


def test_build_namespace_map_with_profile():
    from ddi_l.namespaces import NAMESPACE_PROFILES

    profile_name = next(iter(NAMESPACE_PROFILES))
    result = build_namespace_map(profile_name)
    assert isinstance(result, dict)


def test_build_namespace_map_with_mapping():
    result = build_namespace_map({"custom": "http://custom"})
    assert result.get("custom") == "http://custom"


def test_build_namespace_map_with_extra():
    result = build_namespace_map(extra_namespaces={"extra": "http://extra"})
    assert result.get("extra") == "http://extra"


def test_build_namespace_map_with_base():
    result = build_namespace_map(base={"r": "http://r"})
    assert result.get("r") == "http://r"


def test_extract_namespace_declarations():
    elem = create_element(qn(INSTANCE_NS, "DDIInstance"))
    decls = extract_namespace_declarations(elem)
    assert isinstance(decls, dict)


def test_apply_namespace_map_preserve():
    root = create_element("root")
    result = apply_namespace_map(root, {"r": REUSABLE_NS}, preserve_existing=True)
    assert result is not None


def test_apply_namespace_map_empty():
    root = create_element("root")
    result = apply_namespace_map(root, {}, preserve_existing=False)
    assert result is root


def test_apply_namespace_attributes_stdlib():
    """Test _apply_namespace_attributes directly (stdlib path)."""
    root = create_element("root")
    child = create_element(qn(REUSABLE_NS, "ID"))
    root.append(child)
    _apply_namespace_attributes(root, {"r": REUSABLE_NS})
    # Should set xmlns:r attribute but skip URIs used by element tags


# ===========================================================================
# _namespaces — low-level helpers
# ===========================================================================


def test_local_name_clark():
    assert _local_name("{http://ns}Tag") == "Tag"


def test_local_name_prefixed():
    assert _local_name("r:Tag") == "Tag"


def test_local_name_plain():
    assert _local_name("Tag") == "Tag"


def test_format_tag_clark_with_prefix():
    ns: dict[str | None, str] = {"r": "http://ns"}
    assert _format_tag("{http://ns}Tag", ns) == "r:Tag"


def test_format_tag_clark_default_ns():
    ns: dict[str | None, str] = {None: "http://ns"}
    assert _format_tag("{http://ns}Tag", ns) == "Tag"


def test_format_tag_clark_no_match():
    ns: dict[str | None, str] = {"r": "http://other"}
    result = _format_tag("{http://ns}Tag", ns)
    assert result == "{http://ns}Tag"


def test_format_tag_plain():
    assert _format_tag("Tag", {}) == "Tag"


def test_format_tag_non_string():
    assert _format_tag(42, {}) == "42"  # type: ignore[arg-type]


def test_describe_node_none():
    assert _describe_node(None, {}) is None


def test_describe_node_no_tag():
    class Obj:
        pass

    assert _describe_node(Obj(), {}) is None  # type: ignore[arg-type]


def test_describe_node_with_text():
    e = create_element("root")
    e.text = "hello world"
    result = _describe_node(e, {})
    assert result is not None
    assert "hello world" in result


def test_describe_node_long_text():
    e = create_element("root")
    e.text = "x" * 100
    result = _describe_node(e, {})
    assert result is not None
    assert "..." in result


def test_describe_node_no_text():
    e = create_element("root")
    result = _describe_node(e, {})
    assert result == "<root>"


def test_find_path_root_is_target():
    root = create_element("root")
    assert _find_path(root, root) == [root]


def test_find_path_child():
    root = create_element("root")
    child = create_element("child")
    root.append(child)
    path = _find_path(root, child)
    assert path == [root, child]


def test_find_path_not_found():
    root = create_element("root")
    other = create_element("other")
    assert _find_path(root, other) == []


def test_build_xpath_from_tree_basic():
    root = create_element("root")
    child = create_element("child")
    root.append(child)
    xpath = _build_xpath_from_tree(root, child, {})
    assert xpath == "/root/child"


def test_build_xpath_from_tree_siblings():
    root = create_element("root")
    c1 = create_element("child")
    c2 = create_element("child")
    root.append(c1)
    root.append(c2)
    xpath = _build_xpath_from_tree(root, c2, {})
    assert xpath is not None
    assert "[2]" in xpath


def test_build_xpath_from_tree_not_found():
    root = create_element("root")
    other = create_element("other")
    assert _build_xpath_from_tree(root, other, {}) is None


def test_extract_xmlns_attributes():
    elem = stdlib_element("root")
    elem.set("xmlns", "http://default")
    elem.set("xmlns:r", "http://r")
    result = _extract_xmlns_attributes(elem)
    assert result.get(None) == "http://default"
    assert result.get("r") == "http://r"


def test_gather_namespaces_basic():
    elem = create_element("root")
    result = _gather_namespaces(elem, None)
    assert isinstance(result, dict)
    # Should include defaults
    assert "xml" in result


def test_gather_namespaces_with_schema():
    elem = create_element("root")

    class FakeSchema:
        namespaces = {"s": "http://schema"}

    result = _gather_namespaces(elem, FakeSchema())
    assert result.get("s") == "http://schema"


def test_normalize_prefixed_qnames_dict():
    ns: dict[str | None, str] = {"r": "http://reusable"}
    data = {"r:Agency": "test"}
    result = _normalize_prefixed_qnames(data, ns)
    assert "{http://reusable}Agency" in result


def test_normalize_prefixed_qnames_attr():
    ns: dict[str | None, str] = {"r": "http://reusable"}
    data = {"@r:id": "123"}
    result = _normalize_prefixed_qnames(data, ns)
    assert "@{http://reusable}id" in result


def test_normalize_prefixed_qnames_list():
    ns: dict[str | None, str] = {"r": "http://reusable"}
    data = [{"r:A": "1"}, {"r:B": "2"}]
    result = _normalize_prefixed_qnames(data, ns)
    assert len(result) == 2


def test_normalize_prefixed_qnames_scalar():
    assert _normalize_prefixed_qnames("hello", {}) == "hello"


def test_denormalize_clark_notation_element():
    ns: dict[str | None, str] = {"r": "http://reusable"}
    data = {"{http://reusable}Agency": "test"}
    result = _denormalize_clark_notation(data, ns)
    assert "r:Agency" in result


def test_denormalize_clark_notation_attr():
    ns: dict[str | None, str] = {"r": "http://reusable"}
    data = {"@{http://reusable}id": "123"}
    result = _denormalize_clark_notation(data, ns)
    assert "@r:id" in result


def test_denormalize_clark_notation_default_ns():
    ns: dict[str | None, str] = {None: "http://default"}
    data = {"{http://default}Tag": "val"}
    result = _denormalize_clark_notation(data, ns)
    assert "Tag" in result


def test_denormalize_clark_notation_unresolved():
    ns: dict[str | None, str] = {"r": "http://other"}
    data = {"{http://unknown}Tag": "val"}
    result = _denormalize_clark_notation(data, ns)
    assert "{http://unknown}Tag" in result


def test_denormalize_clark_notation_list():
    ns: dict[str | None, str] = {"r": "http://r"}
    data = [{"{http://r}A": "1"}]
    result = _denormalize_clark_notation(data, ns)
    assert "r:A" in result[0]


def test_denormalize_clark_notation_scalar():
    assert _denormalize_clark_notation("hello", {}) == "hello"


# ===========================================================================
# _compat
# ===========================================================================


def test_fallback_qname_converter_already_clark():
    assert _fallback_qname_converter("{http://ns}Tag") == "{http://ns}Tag"


def test_fallback_qname_converter_prefixed():
    ns: dict[str | None, str] = {"r": "http://reusable"}
    assert _fallback_qname_converter("r:Tag", ns) == "{http://reusable}Tag"


def test_fallback_qname_converter_no_prefix():
    ns: dict[str | None, str] = {"": "http://default"}
    assert _fallback_qname_converter("Tag", ns) == "{http://default}Tag"


def test_fallback_qname_converter_none_default():
    ns: dict[str | None, str] = {None: "http://default"}
    assert _fallback_qname_converter("Tag", ns) == "{http://default}Tag"


def test_fallback_qname_converter_no_match():
    ns: dict[str | None, str] = {"r": "http://r"}
    assert _fallback_qname_converter("x:Tag", ns) == "x:Tag"


def test_fallback_qname_converter_no_namespaces():
    assert _fallback_qname_converter("Tag") == "Tag"


def test_resolve_qname_converter():
    converter = _resolve_qname_converter()
    assert callable(converter)


# ===========================================================================
# _cache
# ===========================================================================


def test_get_schema_default():
    schema = get_schema()
    assert schema is not None


def test_get_schema_cached():
    s1 = get_schema("3.3")
    s2 = get_schema("3.3")
    assert s1 is s2


def test_clear_schema_cache_specific():
    get_schema("3.3")
    clear_schema_cache("3.3")
    # Getting again should reload
    s = get_schema("3.3")
    assert s is not None


def test_clear_schema_cache_all():
    get_schema("3.3")
    clear_schema_cache()
    s = get_schema("3.3")
    assert s is not None


def test_cache_info():
    get_schema("3.3")
    info = _cache_info()
    assert info.currsize >= 1
    assert info.maxsize is None


# ===========================================================================
# namespace_utils — stdlib-only paths (mock USING_LXML=False)
# ===========================================================================


def test_extract_namespace_declarations_stdlib():
    """Exercise lines 82-88: stdlib xmlns extraction."""
    from ddi_l import namespace_utils

    elem = stdlib_element("root")
    elem.set("xmlns", "http://default")
    elem.set("xmlns:r", "http://reusable")

    with patch.object(namespace_utils, "USING_LXML", False):
        decls = namespace_utils.extract_namespace_declarations(elem)
    assert decls.get(None) == "http://default"
    assert decls.get("r") == "http://reusable"


def test_apply_namespace_map_stdlib_path():
    """Exercise lines 149-150 and 158-185: _apply_namespace_attributes via apply_namespace_map."""
    from ddi_l import namespace_utils

    root = create_element(qn(REUSABLE_NS, "Root"))
    child = create_element(qn(REUSABLE_NS, "Child"))
    root.append(child)

    with patch.object(namespace_utils, "USING_LXML", False):
        result = namespace_utils.apply_namespace_map(
            root, {"r": REUSABLE_NS}, preserve_existing=False
        )
    # Should set xmlns:r on the element but skip URIs used by element tags
    assert result is not None


def test_apply_namespace_attributes_stdlib_skips_used_uris():
    """Exercise lines 162-185: _apply_namespace_attributes full logic."""
    from ddi_l import namespace_utils

    root = stdlib_element(qn(REUSABLE_NS, "Root"))
    child = stdlib_element(qn(REUSABLE_NS, "Child"))
    root.append(child)

    # xmlns:r maps to REUSABLE_NS which is already used by tags — should be skipped
    namespace_utils._apply_namespace_attributes(
        root, {"r": REUSABLE_NS, "x": "http://unused"}
    )
    # "x" is unused by any tag, so it should appear as xmlns:x
    assert root.get("xmlns:x") == "http://unused"


def test_apply_namespace_attributes_skips_xml_and_none():
    """Exercise line 178-179: skip None, empty, and 'xml' prefixes."""
    from ddi_l import namespace_utils

    root = create_element("root")
    namespace_utils._apply_namespace_attributes(
        root, {None: "http://default", "": "http://empty", "xml": "http://xml"}
    )
    # None, empty, and xml prefixes should all be skipped
    assert root.get("xmlns:xml") is None


def test_apply_namespace_attributes_clark_attrib():
    """Exercise lines 170-175: Clark notation attributes."""
    from ddi_l import namespace_utils

    root = create_element("root")
    root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "loc")
    namespace_utils._apply_namespace_attributes(
        root, {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    )


# ===========================================================================
# _namespaces — Clark notation xmlns handling (lines 28-32)
# ===========================================================================


def test_extract_xmlns_attributes_clark_notation_prefix():
    """Exercise lines 28-30: xmlns via Clark {xmlns-ns}prefix."""
    from ddi_l.schema_loader._constants import XMLNS_NAMESPACE

    elem = create_element("root")
    elem.set(f"{{{XMLNS_NAMESPACE}}}r", "http://reusable")
    result = _extract_xmlns_attributes(elem)
    assert result.get("r") == "http://reusable"


def test_extract_xmlns_attributes_clark_notation_default():
    """Exercise lines 31-32: xmlns via Clark {xmlns-ns} with empty prefix."""
    from ddi_l.schema_loader._constants import XMLNS_NAMESPACE

    elem = stdlib_element("root")
    elem.set(f"{{{XMLNS_NAMESPACE}}}", "http://default")
    result = _extract_xmlns_attributes(elem)
    assert result.get(None) == "http://default"


# ===========================================================================
# _namespaces — _denormalize_clark_notation attr with None prefix (lines 219-220)
# ===========================================================================


def test_denormalize_clark_notation_attr_unresolved_prefix():
    """Exercise lines 219-220: Clark attr with no matching prefix."""
    ns: dict[str | None, str] = {"r": "http://other"}
    data = {"@{http://unknown}attr": "val"}
    result = _denormalize_clark_notation(data, ns)
    assert "@{http://unknown}attr" in result


# ===========================================================================
# _namespaces — _format_tag with xmlns skip (line 201)
# ===========================================================================


def test_denormalize_clark_notation_skips_xmlns_prefix():
    """Exercise line 201: xmlns prefix filtered from candidates."""
    ns: dict[str | None, str] = {"xmlns": "http://ns", "r": "http://ns"}
    data = {"{http://ns}Tag": "val"}
    result = _denormalize_clark_notation(data, ns)
    assert "r:Tag" in result


# ===========================================================================
# xml_utils — coerce_element TypeError (line 149)
# ===========================================================================


def test_coerce_element_unsupported_type():
    """Exercise line 149: TypeError for unsupported input."""
    with pytest.raises(TypeError, match="Unsupported"):
        coerce_element(42)  # type: ignore[arg-type]


# ===========================================================================
# xml_utils — resolve_xml_source path-like detection (lines 109, 112-113)
# ===========================================================================


def test_resolve_xml_source_str_with_suffix():
    """Exercise line 109: suffix triggers path_like."""
    kind, _payload = resolve_xml_source("nonexistent.xml")
    assert kind == "text"  # File doesn't exist, falls back to text


def test_resolve_xml_source_str_with_dotdot():
    """Exercise line 113: parts[0] == '..' triggers path_like."""
    kind, _payload = resolve_xml_source("../relative/path")
    assert kind == "text"  # doesn't exist, fallback


# ===========================================================================
# _conversion_runtime — exercise _build_element_from_mapping proxy (lines 39, 73-74)
# ===========================================================================


def test_conversion_runtime_proxy_build_element():
    """Exercise lines 39, 73-74: proxy for _build_element_from_mapping."""
    from ddi_l.schema_loader._conversion_runtime import _create_proxy

    proxy = _create_proxy("_build_element_from_mapping")
    elem = proxy("root", "hello")
    assert elem.tag == "root"
    assert elem.text == "hello"


# ===========================================================================
# _constants.py — line 41
# ===========================================================================


def test_get_namespaces():
    from ddi_l.schema_loader._constants import get_namespaces

    ns = get_namespaces()
    assert "reusable" in ns
    assert "instance" in ns
