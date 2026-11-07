"""Edge cases and error paths in ddi_l.io."""

import io
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from unittest.mock import patch

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.document import DDIDocument, DDIFragment
from ddi_l.exceptions import DDIReadError, DDIWriteError
from ddi_l.io import (
    _coerce_element,
    _coerce_source,
    _prune_element,
    _write_to_destination,
    iter_questions,
    iter_variables,
    iterparse_ddi,
    read_ddi,
    write_ddi,
)
from ddi_l.models.datacollection import QuestionItem
from ddi_l.models.logicalproduct import Variable


def _minimal_ddi_xml(tag="DDIInstance", ns=INSTANCE_NS):
    return textwrap.dedent(f"""\
        <{tag} xmlns="{ns}"
               xmlns:r="{REUSABLE_NS}">
            <r:Agency>test.org</r:Agency>
            <r:ID>test-id</r:ID>
            <r:Version>1.0</r:Version>
        </{tag}>
    """)


def _minimal_ddi_bytes():
    return _minimal_ddi_xml().encode("utf-8")


# ---------------------------------------------------------------------------
# _coerce_source
# ---------------------------------------------------------------------------


def test_coerce_source_path(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text(_minimal_ddi_xml())
    handle, should_close = _coerce_source(p)
    assert isinstance(handle, str)
    assert not should_close


def test_coerce_source_str_path(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text(_minimal_ddi_xml())
    handle, should_close = _coerce_source(str(p))
    assert isinstance(handle, str)
    assert not should_close


def test_coerce_source_str_xml():
    handle, should_close = _coerce_source(_minimal_ddi_xml())
    assert should_close
    assert hasattr(handle, "read")
    handle.close()  # type: ignore[union-attr]


def test_coerce_source_bytes():
    handle, should_close = _coerce_source(_minimal_ddi_bytes())
    assert should_close
    assert hasattr(handle, "read")
    handle.close()  # type: ignore[union-attr]


def test_coerce_source_bytearray():
    handle, should_close = _coerce_source(bytearray(_minimal_ddi_bytes()))
    assert should_close
    assert hasattr(handle, "read")
    handle.close()  # type: ignore[union-attr]


def test_coerce_source_file_object():
    buf = io.BytesIO(_minimal_ddi_bytes())
    handle, should_close = _coerce_source(buf)
    assert handle is buf
    assert not should_close


def test_coerce_source_nonexistent_path():
    with pytest.raises(FileNotFoundError):
        _coerce_source(Path("/nonexistent/path.xml"))


# ---------------------------------------------------------------------------
# _coerce_element
# ---------------------------------------------------------------------------


def test_coerce_element_document():
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    elem = _coerce_element(doc)
    assert elem is doc.root


def test_coerce_element_fragment():
    frag = DDIFragment.create()
    elem = _coerce_element(frag)
    assert elem is frag.root


def test_coerce_element_element():
    e = create_element("test")
    assert _coerce_element(e) is e


def test_coerce_element_maintainable():
    v = Variable(agency="test.org", identifier="v1", version="1.0")
    elem = _coerce_element(v)
    assert elem.tag == Variable.TAG


def test_coerce_element_string():
    elem = _coerce_element("<root/>")
    assert elem.tag == "root"


def test_coerce_element_bytes():
    elem = _coerce_element(b"<root/>")
    assert elem.tag == "root"


# ---------------------------------------------------------------------------
# read_ddi
# ---------------------------------------------------------------------------


def test_read_ddi_from_string():
    doc = read_ddi(_minimal_ddi_xml())
    assert isinstance(doc, DDIDocument)


def test_read_ddi_from_bytes():
    doc = read_ddi(_minimal_ddi_bytes())
    assert isinstance(doc, DDIDocument)


def test_read_ddi_from_path(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text(_minimal_ddi_xml())
    doc = read_ddi(p)
    assert isinstance(doc, DDIDocument)


def test_read_ddi_fragment():
    xml = _minimal_ddi_xml(tag="FragmentInstance")
    frag = read_ddi(xml)
    assert isinstance(frag, DDIFragment)


def test_read_ddi_invalid_root():
    xml = '<StudyUnit xmlns="http://www.ddialliance.org/Specification/DDI-Lifecycle/3.3/XMLSchema/instance"/>'
    with pytest.raises(DDIReadError):
        read_ddi(xml)


def test_read_ddi_malformed_xml():
    with pytest.raises(DDIReadError):
        read_ddi("<not closed")


def test_read_ddi_nonexistent_path():
    with pytest.raises(FileNotFoundError):
        read_ddi(Path("/nonexistent/path.xml"))


def test_read_ddi_no_index():
    doc = read_ddi(_minimal_ddi_xml(), build_index=False)
    assert isinstance(doc, DDIDocument)


def test_read_ddi_unknown_root_tag():
    xml = '<Unknown xmlns="http://www.ddialliance.org/Specification/DDI-Lifecycle/3.3/XMLSchema/instance"><r:Agency xmlns:r="ddi:reusable:3_3">a</r:Agency><r:ID xmlns:r="ddi:reusable:3_3">b</r:ID><r:Version xmlns:r="ddi:reusable:3_3">1</r:Version></Unknown>'
    with pytest.raises(DDIReadError, match="DDIInstance or FragmentInstance"):
        read_ddi(xml)


# ---------------------------------------------------------------------------
# write_ddi
# ---------------------------------------------------------------------------


def test_write_ddi_returns_bytes():
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    result = write_ddi(doc)
    assert isinstance(result, bytes)
    assert b"DDIInstance" in result


def test_write_ddi_to_path(tmp_path):
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    p = tmp_path / "out.xml"
    result = write_ddi(doc, p)
    assert isinstance(result, bytes)
    assert p.exists()


def test_write_ddi_to_binary_stream():
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    buf = io.BytesIO()
    write_ddi(doc, buf)
    assert buf.getvalue()


def test_write_ddi_to_text_stream():
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    buf = io.StringIO()
    write_ddi(doc, buf)
    assert buf.getvalue()


def test_write_ddi_unsupported_destination(tmp_path):
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    with pytest.raises(DDIWriteError) as caught:
        write_ddi(doc, 42)  # type: ignore[arg-type]
    assert str(caught.value) == (
        "Unexpected failure while writing DDI XML. (xpath /DDIInstance)"
    )
    cause = caught.value.original_exception
    assert isinstance(cause, TypeError)
    assert str(cause) == "Unsupported destination type for DDI serialization."

    # The location names the file the document came from.
    source = tmp_path / "in.xml"
    source.write_text("<root/>")
    with pytest.raises(DDIWriteError) as caught:
        write_ddi(source, 42)  # type: ignore[arg-type]
    location = caught.value.location
    assert location is not None
    assert (location.filename, location.xpath) == (str(source), "/root")


@dataclass
class _Named:
    name: str = "pets.xml"


def test_write_ddi_type_error():
    with pytest.raises(DDIWriteError) as caught:
        write_ddi(42)  # type: ignore[arg-type]
    assert str(caught.value) == "Failed to prepare DDI XML for serialisation."
    cause = caught.value.original_exception
    assert isinstance(cause, TypeError)
    assert str(cause) == "Unsupported document type for DDI serialization."

    # A dataclass without to_xml is not a document, and its name is the file.
    with pytest.raises(DDIWriteError) as caught:
        write_ddi(_Named())  # type: ignore[arg-type]
    assert str(caught.value) == (
        "Failed to prepare DDI XML for serialisation. (pets.xml)"
    )


@dataclass
class _Wrapper:
    def to_xml(self):
        return create_element(f"{{{INSTANCE_NS}}}DDIInstance")


@dataclass
class _Broken:
    def to_xml(self):
        raise RuntimeError("boom")


def test_write_ddi_dataclass_with_to_xml():
    assert b"DDIInstance" in write_ddi(_Wrapper())  # type: ignore[arg-type]

    with pytest.raises(DDIWriteError) as caught:
        write_ddi(_Broken())  # type: ignore[arg-type]
    assert str(caught.value) == "Unexpected failure while writing DDI XML."
    assert isinstance(caught.value.original_exception, RuntimeError)


def test_write_ddi_a_file_that_cannot_be_read(tmp_path):
    bad = tmp_path / "bad.xml"
    bad.write_text("<root")
    with pytest.raises(DDIWriteError) as caught:
        write_ddi(bad)
    assert str(caught.value) == f"Unexpected failure while writing DDI XML. ({bad})"

    # A file opened for writing cannot be read: a ValueError.
    with (tmp_path / "out.xml").open("w") as handle:
        with pytest.raises(DDIWriteError) as caught:
            write_ddi(handle)
    assert str(caught.value) == (
        f"Failed to serialise DDI XML content. ({tmp_path / 'out.xml'})"
    )
    assert isinstance(caught.value.original_exception, ValueError)


def test_write_ddi_string():
    result = write_ddi("<root/>")
    assert isinstance(result, bytes)


def test_write_ddi_bytes():
    result = write_ddi(b"<root/>")
    assert isinstance(result, bytes)


def test_write_ddi_maintainable():
    v = Variable(agency="test.org", identifier="v1", version="1.0")
    result = write_ddi(v)
    assert isinstance(result, bytes)


def test_write_ddi_with_version():
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    result = write_ddi(doc, version="3.3")
    assert isinstance(result, bytes)
    with pytest.raises(ValueError, match=r"^Unsupported DDI schema version: '9\.9'$"):
        write_ddi(doc, version="9.9")


def test_write_ddi_unknown_layout():
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    with pytest.raises(
        ValueError,
        match=r"^Unknown layout 'tight'; expected 'default' or 'colectica'\.$",
    ):
        write_ddi(doc, layout="tight")


def test_write_ddi_colectica_layout_to_a_text_stream():
    fragment = DDIFragment.from_xml(_minimal_ddi_xml("FragmentInstance"))
    buf = io.StringIO()
    written = write_ddi(fragment, buf, layout="colectica")
    assert buf.getvalue() == written.decode("utf-8")


def test_write_ddi_colectica_layout_of_an_instance(tmp_path):
    source = tmp_path / "in.xml"
    source.write_text("<root/>")
    with pytest.raises(DDIWriteError) as caught:
        write_ddi(source, layout="colectica")
    assert caught.value.message == "Failed to serialise DDI XML content."
    location = caught.value.location
    assert location is not None
    assert (location.filename, location.xpath) == (str(source), "/root")
    assert isinstance(caught.value.original_exception, ValueError)


def test_write_ddi_declaration_and_trailing_newline():
    element = create_element("a")
    compact = write_ddi(element, pretty_print=False, xml_declaration=False)
    assert compact.startswith(b"<a ") and compact.endswith(b"/>")

    pretty = write_ddi(element, encoding="latin-1")
    assert pretty.startswith(b'<?xml version="1.0" encoding="LATIN-1"?>\n<a ')
    assert pretty.endswith(b"/>\n")


def test_write_ddi_writes_text_as_characters():
    element = create_element(f"{{{INSTANCE_NS}}}DDIInstance")
    element.text = "chat \u00e9"
    assert "chat \u00e9".encode() in write_ddi(element, pretty_print=False)


def test_write_ddi_value_error():
    """Trigger the ValueError path in write_ddi."""
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")

    # Patch _coerce_element to raise ValueError
    with patch("ddi_l.io._coerce_element", side_effect=ValueError("bad value")):
        with pytest.raises(DDIWriteError) as caught:
            write_ddi(doc)
    assert str(caught.value) == "Failed to serialise DDI XML content."
    assert str(caught.value.original_exception) == "bad value"


def test_write_ddi_value_error_during_emit():
    """Trigger ValueError during XML emission."""
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    with patch("ddi_l.io._emit_xml", side_effect=ValueError("emit error")):
        with pytest.raises(DDIWriteError) as caught:
            write_ddi(doc)
    assert (
        str(caught.value) == "Failed to serialise DDI XML content. (xpath /DDIInstance)"
    )
    assert str(caught.value.original_exception) == "emit error"


# ---------------------------------------------------------------------------
# _write_to_destination
# ---------------------------------------------------------------------------


def test_write_to_destination_none():
    result = _write_to_destination(b"payload", None, encoding="utf-8")
    assert result == b"payload"


def test_write_to_destination_path(tmp_path):
    p = tmp_path / "out.xml"
    _write_to_destination(b"payload", p, encoding="utf-8")
    assert p.read_bytes() == b"payload"


def test_write_to_destination_str_path(tmp_path):
    p = tmp_path / "out.xml"
    _write_to_destination(b"payload", str(p), encoding="utf-8")
    assert p.read_bytes() == b"payload"


def test_write_to_destination_binary_stream():
    buf = io.BytesIO()
    _write_to_destination(b"payload", buf, encoding="utf-8")
    assert buf.getvalue() == b"payload"


def test_write_to_destination_text_stream():
    buf = io.StringIO()
    _write_to_destination(b"payload", buf, encoding="utf-8")
    assert buf.getvalue() == "payload"


def test_write_to_destination_unsupported():
    with pytest.raises(TypeError):
        _write_to_destination(b"payload", 42, encoding="utf-8")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _prune_element
# ---------------------------------------------------------------------------


def test_prune_element_detaches_from_parent():
    root = create_element("root")
    child1 = create_element("c1")
    child2 = create_element("c2")
    child2.append(create_element("grandchild"))
    root.append(child1)
    root.append(child2)
    _prune_element(child2, root)
    assert list(root) == [child1]
    assert len(child2) == 0


def test_prune_element_without_parent_only_clears():
    orphan = create_element("orphan")
    orphan.append(create_element("child"))
    _prune_element(orphan, None)
    assert len(orphan) == 0


# ---------------------------------------------------------------------------
# iterparse_ddi
# ---------------------------------------------------------------------------


def test_iterparse_ddi_empty_document():
    xml = _minimal_ddi_xml()
    results = list(iterparse_ddi(xml))
    assert results == []


def test_iterparse_ddi_with_variable(tmp_path):
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}"
                     xmlns:r="{REUSABLE_NS}"
                     xmlns:l="ddi:logicalproduct:3_3">
            <r:Agency>test.org</r:Agency>
            <r:ID>inst</r:ID>
            <r:Version>1.0</r:Version>
            <l:Variable>
                <r:Agency>test.org</r:Agency>
                <r:ID>var1</r:ID>
                <r:Version>1.0</r:Version>
            </l:Variable>
        </DDIInstance>
    """)
    results = list(iterparse_ddi(xml, maintainable_types=[Variable]))
    assert len(results) == 1
    assert isinstance(results[0], Variable)


def test_iterparse_ddi_skips_unwanted_maintainables():
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}"
                     xmlns:r="{REUSABLE_NS}"
                     xmlns:l="ddi:logicalproduct:3_3">
            <r:Agency>test.org</r:Agency>
            <r:ID>inst</r:ID>
            <r:Version>1.0</r:Version>
            <l:Variable>
                <r:Agency>test.org</r:Agency>
                <r:ID>var1</r:ID>
                <r:Version>1.0</r:Version>
            </l:Variable>
        </DDIInstance>
    """)
    # Ask for CodeList only — should skip the Variable and still prune it
    results = list(iterparse_ddi(xml, maintainable_types=[]))
    assert len(results) == 0


def test_iterparse_ddi_closes_only_what_it_opened(monkeypatch, tmp_path):
    import ddi_l.io as io_module

    opened: list[io.IOBase] = []
    real = io_module._coerce_source

    def spy(source):
        handle, should_close = real(source)
        opened.append(cast(io.IOBase, handle))
        return handle, should_close

    monkeypatch.setattr(io_module, "_coerce_source", spy)
    list(iterparse_ddi(_minimal_ddi_bytes()))
    assert opened[0].closed

    path = tmp_path / "in.xml"
    path.write_bytes(_minimal_ddi_bytes())
    with path.open("rb") as handle:
        list(iterparse_ddi(handle))
        assert not handle.closed


# ---------------------------------------------------------------------------
# iter_variables / iter_questions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("iterate", [iter_variables, iter_questions])
def test_iter_helpers_pass_options_to_the_parser(iterate):
    with pytest.raises(TypeError):
        list(iterate(_minimal_ddi_bytes(), no_such_option=True))


def test_iter_variables_from_xml_string():
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}"
                     xmlns:r="{REUSABLE_NS}"
                     xmlns:l="ddi:logicalproduct:3_3">
            <r:Agency>test.org</r:Agency>
            <r:ID>inst</r:ID>
            <r:Version>1.0</r:Version>
            <l:Variable>
                <r:Agency>test.org</r:Agency>
                <r:ID>v1</r:ID>
                <r:Version>1.0</r:Version>
            </l:Variable>
        </DDIInstance>
    """)
    results = list(iter_variables(xml))
    assert len(results) == 1
    assert isinstance(results[0], Variable)


def test_iter_variables_from_document():
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    # No variables in empty doc
    results = list(iter_variables(doc))  # type: ignore[arg-type]
    assert results == []


def test_iter_questions_from_document():
    doc = DDIDocument.create(agency="test.org", identifier="doc", version="1.0")
    results = list(iter_questions(doc))  # type: ignore[arg-type]
    assert results == []


def test_iter_questions_from_xml_string():
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}"
                     xmlns:r="{REUSABLE_NS}"
                     xmlns:dc="ddi:datacollection:3_3">
            <r:Agency>test.org</r:Agency>
            <r:ID>inst</r:ID>
            <r:Version>1.0</r:Version>
            <dc:QuestionItem>
                <r:Agency>test.org</r:Agency>
                <r:ID>q1</r:ID>
                <r:Version>1.0</r:Version>
            </dc:QuestionItem>
        </DDIInstance>
    """)
    results = list(iter_questions(xml))
    assert len(results) == 1
    assert isinstance(results[0], QuestionItem)
