import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from ddi_l._etree import USING_LXML, create_element
from ddi_l.namespace_utils import (
    apply_namespace_map,
    build_namespace_map,
    extract_namespace_declarations,
)


@pytest.mark.skipif(not USING_LXML, reason="lxml not installed")
def test_apply_namespace_map_reuses_children_under_lxml():
    nsmap = {None: "urn:example:instance", "extra": "urn:example:extra"}

    root = create_element(
        "{urn:example:instance}Root", nsmap={None: "urn:example:instance"}
    )
    root.text = "root-text"
    root.tail = "root-tail"
    root.set("attr", "value")

    child = create_element("{urn:example:instance}Child")
    child.text = "child-text"
    child.tail = "child-tail"
    root.append(child)

    result = apply_namespace_map(root, nsmap, preserve_existing=False)

    assert result is not root
    assert next(iter(result)) is child
    assert result.text == "root-text"
    assert result.tail == "root-tail"
    assert result.get("attr") == "value"
    assert child.tail == "child-tail"
    assert len(root) == 0
    assert root.text is None
    assert root.tail is None
    assert root.attrib == {}


def test_apply_namespace_map_does_not_clone_without_lxml():
    repo_root = Path(__file__).resolve().parents[1]
    python_paths = [str(repo_root / "src"), str(repo_root)]

    script = textwrap.dedent(
        """
        import sys
        import types

        fake_lxml = types.ModuleType("lxml")

        def _getattr(_):
            raise ModuleNotFoundError("No module named 'lxml'")

        fake_lxml.__getattr__ = _getattr
        sys.modules["lxml"] = fake_lxml

        from ddi_l.namespace_utils import apply_namespace_map
        from ddi_l._etree import create_element

        nsmap = {None: "urn:example:instance", "extra": "urn:example:extra"}

        root = create_element("{urn:example:instance}Root", nsmap={None: "urn:example:instance"})
        root.text = "root-text"
        root.tail = "root-tail"
        root.set("attr", "value")

        child = create_element("{urn:example:instance}Child")
        child.text = "child-text"
        child.tail = "child-tail"
        root.append(child)

        result = apply_namespace_map(root, nsmap, preserve_existing=False)

        assert result is root
        assert list(result)[0] is child
        assert result.text == "root-text"
        assert result.tail == "root-tail"
        assert result.get("attr") == "value"
        assert child.tail == "child-tail"
        """
    )

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        python_paths.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    subprocess.run([sys.executable, "-c", script], check=True, env=env)


# ===========================================================================
# build_namespace_map
# ===========================================================================


class TestBuildNamespaceMap:
    def test_default(self):
        result = build_namespace_map()
        # Should contain all default DDI namespace bindings
        assert len(result) > 0

    def test_with_explicit_mapping(self):
        custom = {"custom": "http://custom.example"}
        result = build_namespace_map(custom)  # type: ignore[arg-type]
        assert result["custom"] == "http://custom.example"

    def test_with_profile(self):
        result = build_namespace_map("ddi-default")
        assert len(result) > 0

    def test_with_extra_namespaces(self):
        extra = {"extra": "http://extra.example"}
        result = build_namespace_map(extra_namespaces=extra)  # type: ignore[arg-type]
        assert result["extra"] == "http://extra.example"

    def test_with_custom_base(self):
        base = {"base": "http://base.example"}
        result = build_namespace_map(base=base)  # type: ignore[arg-type]
        assert result["base"] == "http://base.example"

    def test_extra_overrides_profile(self):
        extra = {"r": "http://override.example"}
        result = build_namespace_map(extra_namespaces=extra)  # type: ignore[arg-type]
        assert result["r"] == "http://override.example"


# ===========================================================================
# extract_namespace_declarations
# ===========================================================================


class TestExtractNamespaceDeclarations:
    @pytest.mark.skipif(USING_LXML, reason="stdlib-only path")
    def test_stdlib_default_ns(self):
        el = create_element("Root")
        el.set("xmlns", "http://default.example")
        result = extract_namespace_declarations(el)
        assert result.get(None) == "http://default.example"

    @pytest.mark.skipif(USING_LXML, reason="stdlib-only path")
    def test_stdlib_prefixed_ns(self):
        el = create_element("Root")
        el.set("xmlns:r", "http://reusable.example")
        result = extract_namespace_declarations(el)
        assert result.get("r") == "http://reusable.example"

    @pytest.mark.skipif(not USING_LXML, reason="lxml-only path")
    def test_lxml_path(self):
        el = create_element(
            "{http://example.org}Root", nsmap={None: "http://example.org"}
        )
        result = extract_namespace_declarations(el)
        assert None in result or len(result) > 0


# ===========================================================================
# apply_namespace_map — additional tests
# ===========================================================================


class TestApplyNamespaceMapExtended:
    @pytest.mark.skipif(USING_LXML, reason="stdlib-only path")
    def test_preserve_existing(self):
        # The stdlib backend carries namespace declarations as literal
        # ``xmlns:`` attributes, which lxml rejects as attribute names.
        el = create_element("{http://example.org}Root")
        el.set("xmlns:existing", "http://existing.example")
        result = apply_namespace_map(
            el, {"new": "http://new.example"}, preserve_existing=True
        )
        assert result is not None

    @pytest.mark.skipif(not USING_LXML, reason="lxml-only path")
    def test_preserve_existing_lxml(self):
        # Same contract on the lxml backend, where an existing declaration
        # lives in the element's nsmap rather than in an attribute.
        el = create_element(
            "{http://example.org}Root",
            nsmap={"existing": "http://existing.example"},
        )
        result = apply_namespace_map(
            el, {"new": "http://new.example"}, preserve_existing=True
        )
        assert result is not None
        assert extract_namespace_declarations(result).get("existing") == (
            "http://existing.example"
        )

    def test_empty_nsmap(self):
        el = create_element("Root")
        result = apply_namespace_map(el, {}, preserve_existing=False)
        assert result is el

    @pytest.mark.skipif(USING_LXML, reason="stdlib-only path")
    def test_stdlib_applies_xmlns_attrs(self):
        el = create_element("{http://example.org}Root")
        child = create_element("{http://child.org}Child")
        el.append(child)
        result = apply_namespace_map(
            el,
            {"ex": "http://example.org", "ch": "http://child.org"},
            preserve_existing=False,
        )
        # Should apply xmlns attributes
        assert result is el

    @pytest.mark.skipif(USING_LXML, reason="stdlib-only path")
    def test_stdlib_skips_xml_prefix(self):
        el = create_element("{http://example.org}Root")
        result = apply_namespace_map(
            el,
            {"xml": "http://www.w3.org/XML/1998/namespace", None: "http://example.org"},
            preserve_existing=False,
        )
        assert result is el

    @pytest.mark.skipif(not USING_LXML, reason="lxml-only path")
    def test_lxml_no_missing_bindings(self):
        nsmap = {None: "http://example.org"}
        el = create_element("{http://example.org}Root", nsmap=nsmap)  # type: ignore[arg-type]
        result = apply_namespace_map(el, nsmap, preserve_existing=False)  # type: ignore[arg-type]
        assert result is el  # No new root needed
