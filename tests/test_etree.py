import io

import pytest

from ddi_l import __all__ as ddi_l_all
from ddi_l._etree import (
    USING_LXML,
    cleanup_namespaces,
    create_element,
    parse_xml,
    tostring,
)
from ddi_l.document import DEFAULT_NSMAP, INSTANCE_NS, REUSABLE_NS, DDIDocument
from ddi_l.namespace_utils import apply_namespace_map


@pytest.mark.parametrize("pretty_print, expect_indent", [(True, True), (False, False)])
def test_to_xml_pretty_print_controls_indentation(pretty_print, expect_indent):
    """Ensure XML pretty_print flag toggles indentation and namespace bindings.

    Args:
        pretty_print: Flag passed to DDIDocument.to_xml.
        expect_indent: Expected newline presence based on pretty_print flag.
    """
    document = DDIDocument.create(agency="demo", identifier="id", version="1.0")
    document.set_citation(title="Example")

    xml_output = document.to_xml(pretty_print=pretty_print)

    assert xml_output.startswith("<DDIInstance")
    assert 'xmlns="ddi:instance:3_3"' in xml_output
    # The reusable namespace binding must be present even if the backend
    # chooses an automatic prefix such as ``ns0``.
    assert "ddi:reusable:3_3" in xml_output

    has_newlines = "\n" in xml_output
    assert has_newlines is expect_indent


def test_parse_xml_accepts_path_and_file_like(tmp_path):
    """Parse XML from path and file-like objects yielding identical trees.

    Args:
        tmp_path: Temporary directory provided by pytest for writing XML.
    """
    xml = """<root xmlns=\"urn:test\"><child attr=\"value\">text</child></root>"""
    xml_bytes = xml.encode("utf-8")

    xml_path = tmp_path / "sample.xml"
    xml_path.write_bytes(xml_bytes)

    parsed_from_path = parse_xml(xml_path)
    parsed_from_stream = parse_xml(io.BytesIO(xml_bytes))

    assert parsed_from_path.tag == parsed_from_stream.tag == "{urn:test}root"

    children_from_path = list(parsed_from_path)
    children_from_stream = list(parsed_from_stream)
    assert len(children_from_path) == len(children_from_stream) == 1
    assert children_from_path[0].tag == children_from_stream[0].tag == "{urn:test}child"
    assert (
        children_from_path[0].attrib
        == children_from_stream[0].attrib
        == {"attr": "value"}
    )
    assert children_from_path[0].text == children_from_stream[0].text == "text"

    assert tostring(parsed_from_path, pretty_print=False) == tostring(
        parsed_from_stream, pretty_print=False
    )


def test_cleanup_namespaces_removes_unused_prefixes():
    """Namespace cleanup removes unused prefixes for both XML backends."""
    extra_ns = "urn:extra"
    root = create_element(
        f"{{{INSTANCE_NS}}}Root",
        nsmap={None: INSTANCE_NS, "r": REUSABLE_NS, "extra": extra_ns},
    )
    child = create_element(f"{{{REUSABLE_NS}}}Child")
    root.append(child)

    xml_before = tostring(root, pretty_print=False)
    if USING_LXML:
        # lxml preserves explicit namespace declarations even when unused.
        assert "xmlns:extra" in xml_before
    else:
        # The stdlib backend does not attach unused declarations during
        # creation, so they are already absent prior to cleanup.
        assert "xmlns:extra" not in xml_before

    cleanup_namespaces(root, DEFAULT_NSMAP)  # type: ignore[arg-type]

    xml_after = tostring(root, pretty_print=False)
    assert "xmlns:extra" not in xml_after
    assert 'xmlns="ddi:instance:3_3"' in xml_after
    assert 'xmlns:r="ddi:reusable:3_3"' in xml_after


def test_apply_namespace_map_binds_required_prefixes():
    """Applying a namespace map yields the same bindings on both backends.

    ``apply_namespace_map`` is what *binds* a namespace map, and it returns a
    root because lxml cannot rebind an element's prefix in place -- a prefix is
    fixed when the element is created. ``cleanup_namespaces`` only prunes
    declarations that are unused, so it cannot be the function that establishes
    a default namespace on an element that was created without one.
    """
    root = create_element(f"{{{INSTANCE_NS}}}Root")
    root.append(create_element(f"{{{REUSABLE_NS}}}Child"))

    root = apply_namespace_map(root, DEFAULT_NSMAP, preserve_existing=False)

    xml_after = tostring(root, pretty_print=False)
    assert 'xmlns="ddi:instance:3_3"' in xml_after
    assert 'xmlns:r="ddi:reusable:3_3"' in xml_after
    # The element itself must sit in the default namespace, not under a
    # prefix the serializer invented for it.
    assert xml_after.startswith("<Root ")


EXPECTED_PUBLIC_API = [
    "CodeList",
    "Concept",
    "DDIDocument",
    "DDIError",
    "DDIFragment",
    "DDIModelError",
    "DDIParseError",
    "DDIReadError",
    "DDIReferenceError",
    "DDIReferenceWarning",
    "DDIValidationError",
    "DDIWriteError",
    "DataCollection",
    "Document",
    "DuplicateIdentifierError",
    "ErrorLocation",
    "InternationalString",
    "LogicalProduct",
    "MaintainableBase",
    "ModelBuildError",
    "ModelValidationError",
    "QuestionItem",
    "Reference",
    "StudyCursor",
    "StudyUnit",
    "Universe",
    "Variable",
    "__author__",
    "__version__",
    "iter_questions",
    "iter_variables",
    "iterparse_ddi",
    "new_study",
    "open_ddi",
    "read_ddi",
    "write_ddi",
]


def test_public_api_surface_matches_expected():
    """Verify ddi_l exports the expected stable public API surface."""
    assert sorted(ddi_l_all) == sorted(EXPECTED_PUBLIC_API)


def test_empty_element_normalization_leaves_attribute_values_alone():
    """`` />`` inside an attribute value does not close a start tag.

    ``<x note="foo /> bar">`` must be left untouched.
    """
    from ddi_l._etree import _normalize_empty_elements

    assert (
        _normalize_empty_elements('<x note="foo /> bar"></x>')
        == '<x note="foo /> bar"></x>'
    )
    assert (
        _normalize_empty_elements("<x note='foo /> bar'></x>")
        == "<x note='foo /> bar'></x>"
    )
    # ...while still doing the job it exists for, including alongside one.
    assert _normalize_empty_elements("<tag />") == "<tag/>"
    assert (
        _normalize_empty_elements('<x note="a /> b" other="c" />')
        == '<x note="a /> b" other="c"/>'
    )
    assert _normalize_empty_elements("<x>text /> more</x>") == "<x>text /> more</x>"
