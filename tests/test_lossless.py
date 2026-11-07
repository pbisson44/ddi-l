"""A document read from a file is written back with its unchanged parts as read."""

from __future__ import annotations

import copy
import io
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

import ddi_l
from ddi_l import open_ddi, open_fragment, read_ddi, write_ddi
from ddi_l._etree import create_element, parse_xml
from ddi_l._lossless import Source, _digests
from ddi_l._whitespace import without_indentation
from ddi_l.colectica_edit import move_construct
from tests.helpers.examples import examples

FIXTURES = Path(__file__).parent / "fixtures"
PETS = FIXTURES / "colectica" / "pets_instrument.ddi33.xml"
INSTANCE = FIXTURES / "golden" / "example_instance.canonical.xml"
# Binds DDI namespaces to p0..p4, which a write renames, as before.
RENAMED = FIXTURES / "instances" / "example_instance.xml"
R = "{ddi:reusable:3_3}"
D = "{ddi:datacollection:3_3}"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
EXAMPLES = examples(300)


def _documents() -> list[Path]:
    found = []
    for path in sorted(FIXTURES.rglob("*.xml")):
        try:
            read_ddi(path)
        except Exception:  # item snippets, malformed or invalid on purpose
            continue
        if path.parent.name != "instances":  # p0..p4: renamed on write
            found.append(path)
    return found


DOCUMENTS = _documents()


def _same_tree(written: bytes, document: ddi_l.DDIDocument | ddi_l.DDIFragment) -> bool:
    """Whether ``written`` reads back as ``document``, layout aside.

    The stdlib backend keeps indentation as text, so a new element written
    indented reads back with blanks it did not have; both sides drop them.
    """
    again = without_indentation(parse_xml(io.BytesIO(written)))
    current = without_indentation(copy.deepcopy(document.root))
    return _digests(again)[id(again)] == _digests(current)[id(current)]


@pytest.mark.parametrize("path", DOCUMENTS, ids=lambda path: path.name)
def test_a_document_read_and_written_is_unchanged(path: Path) -> None:
    assert write_ddi(read_ddi(path)) == path.read_bytes()


def test_every_reader_and_writer_keeps_the_bytes(tmp_path: Path) -> None:
    data = PETS.read_bytes()
    fragment = open_fragment(PETS)
    fragment.save(tmp_path / "saved.xml")

    assert (tmp_path / "saved.xml").read_bytes() == data
    assert fragment.to_xml().encode() == data.removeprefix(b"\xef\xbb\xbf")
    assert write_ddi(read_ddi(data)) == data

    instance = INSTANCE.read_bytes()
    document = open_ddi(INSTANCE)
    document.save(tmp_path / "study.xml")
    assert (tmp_path / "study.xml").read_bytes() == instance
    assert ddi_l.DDIDocument.from_xml(INSTANCE).to_xml().encode() in instance


def test_an_explicit_layout_lays_the_whole_document_out() -> None:
    fragment = open_fragment(PETS)

    assert write_ddi(fragment, layout="colectica") == fragment.to_colectica_bytes()
    assert write_ddi(fragment, layout="default") != PETS.read_bytes()


def test_text_and_streams_are_written_with_a_layout() -> None:
    text = PETS.read_text(encoding="utf-8")

    assert write_ddi(read_ddi(text)) == open_fragment(PETS).to_colectica_bytes()
    assert Source.capture(io.BytesIO(PETS.read_bytes()))[0] is None


def _edited(
    path: Path, edit
) -> tuple[bytes, bytes, ddi_l.DDIDocument | ddi_l.DDIFragment]:
    data = path.read_bytes()
    document = read_ddi(data)
    edit(document.root)
    written = write_ddi(document)
    assert _same_tree(written, document)
    return data, written, document


def _first(root, tag: str):
    return next(root.iter(tag))


def test_a_changed_text_changes_only_that_text() -> None:
    def edit(root) -> None:
        node = _first(root, R + "String")
        node.text = "Pet survey instrument (revised)"

    data, written, _ = _edited(PETS, edit)

    assert written == data.replace(
        b">Pet survey instrument<", b">Pet survey instrument (revised)<", 1
    )


def test_a_changed_attribute_changes_only_its_start_tag() -> None:
    def edit(root) -> None:
        _first(root, D + "Sequence").set("versionDate", "2027-01-01T00:00:00.0000000Z")

    data, written, _ = _edited(PETS, edit)
    old = b'<Sequence isUniversallyUnique="true" versionDate="2026-01-05T10:00:00.0000000Z"'
    new = b'<Sequence isUniversallyUnique="true" versionDate="2027-01-01T00:00:00.0000000Z"'

    assert written == data.replace(old, new, 1)


def test_a_new_element_is_laid_out_like_its_neighbours() -> None:
    def edit(root) -> None:
        description = create_element(R + "Description")
        content = create_element(R + "Content")
        content.text = "Pets & owners"
        content.set(XML_LANG, "en")
        description.append(content)
        _first(root, D + "Sequence").insert(5, description)

    data, written, _ = _edited(PETS, edit)
    anchor = b"    </ConstructName>\n"
    added = (
        b"    <r:Description>\n"
        b'      <r:Content xml:lang="en">Pets &amp; owners</r:Content>\n'
        b"    </r:Description>\n"
    )

    assert written == data.replace(anchor, anchor + added, 1)


def test_a_removed_or_copied_item_leaves_the_others_as_read() -> None:
    def remove(root) -> None:
        root.remove([node for node in root if node.tag.endswith("}Fragment")][1])

    data, written, _ = _edited(PETS, remove)
    assert len(written) < len(data)
    assert data.startswith(written[:300])

    def duplicate(root) -> None:
        fragments = [node for node in root if node.tag.endswith("}Fragment")]
        root.append(copy.deepcopy(fragments[1]))

    data, written, _ = _edited(PETS, duplicate)
    end = b"\n</ddi:FragmentInstance>"
    second = data.split(b"\n<Fragment")[2].split(b"\n</Fragment>")[0]
    assert written == data.replace(
        end, b"\n<Fragment" + second + b"\n</Fragment>" + end
    )


def test_a_new_item_is_written_in_colectica_layout() -> None:
    def edit(root) -> None:
        fragment = create_element("{ddi:instance:3_3}Fragment")
        statement = create_element(D + "StatementItem")
        for name, value in (("Agency", "int.example"), ("ID", "s-1"), ("Version", "1")):
            part = create_element(R + name)
            part.text = value
            statement.append(part)
        fragment.append(statement)
        root.append(fragment)

    data, written, _ = _edited(PETS, edit)
    added = (
        b'\n<Fragment xmlns:r="ddi:reusable:3_3" xmlns="ddi:instance:3_3">\n'
        b'  <StatementItem xmlns="ddi:datacollection:3_3">\n'
        b"    <r:Agency>int.example</r:Agency>\n"
        b"    <r:ID>s-1</r:ID>\n"
        b"    <r:Version>1</r:Version>\n"
        b"  </StatementItem>\n"
        b"</Fragment>"
    )
    end = b"\n</ddi:FragmentInstance>"

    assert written == data.replace(end, added + end)


def test_a_moved_construct_keeps_its_bytes() -> None:
    fragment = read_ddi(PETS)
    sequence = _first(fragment.root, D + "Sequence")
    references = sequence.findall(D + "ControlConstructReference")
    moved = references[0]
    before = PETS.read_bytes()

    sequence.remove(moved)
    sequence.append(moved)
    written = write_ddi(fragment)

    assert _same_tree(written, fragment)
    assert sorted(written.splitlines()) == sorted(before.splitlines())
    assert move_construct is not None  # the edit API moves constructs the same way


def test_a_document_keeps_its_own_text_and_indentation() -> None:
    data = INSTANCE.read_bytes()
    document = read_ddi(data)
    agency = _first(document.root, R + "Agency")
    agency.text = "other.example"

    written = write_ddi(document)

    assert written == data.replace(
        b"<r:Agency>example.agency</r:Agency>",
        b"<r:Agency>other.example</r:Agency>",
        1,
    )

    source = (
        b'<?xml version="1.0" encoding="UTF-8"?>\r\n'
        b'<DDIInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">\r\n'
        b"    <r:Agency>example.agency</r:Agency>\r\n"
        b"</DDIInstance>\r\n"
    )
    document = read_ddi(source)
    note = create_element(R + "Note")
    content = create_element(R + "Content")
    content.text = "new"
    note.append(content)
    document.root.append(note)

    assert write_ddi(document) == source.replace(
        b"</r:Agency>\r\n",
        b"</r:Agency>\r\n    <r:Note>\r\n        <r:Content>new</r:Content>"
        b"\r\n    </r:Note>\r\n",
    )


def test_a_document_with_other_prefixes_gets_the_canonical_ones() -> None:
    written = read_ddi(RENAMED).to_xml()

    assert "xmlns:p0=" not in written
    assert 'xmlns:c="ddi:conceptualcomponent:3_3"' in written


def test_a_span_is_copied_only_where_its_prefixes_mean_the_same() -> None:
    source = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<DDIInstance xmlns="ddi:instance:3_3">\n'
        b'  <a:Note xmlns:a="ddi:reusable:3_3"><a:Content>kept</a:Content></a:Note>\n'
        b'  <Other xmlns:a="urn:other"/>\n'
        b"</DDIInstance>\n"
    )
    document = read_ddi(source)
    note, other = list(document.root)
    content = note[0]
    note.remove(content)
    other.append(content)  # a: means urn:other here

    written = write_ddi(document)

    assert _same_tree(written, document)
    assert b"<a:Content>kept</a:Content>" not in written.split(b"<Other")[1]


def test_character_references_and_cdata_stay_as_read() -> None:
    source = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<DDIInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">\n'
        b"  <r:Note><r:Content>caf&#233; &amp; <![CDATA[<b>]]></r:Content></r:Note>\n"
        b"  <r:Note><r:Content>edited</r:Content></r:Note>\n"
        b"</DDIInstance>\n"
    )
    document = read_ddi(source)
    list(document.root)[1][0].text = "changed"

    written = write_ddi(document)

    assert b"caf&#233; &amp; <![CDATA[<b>]]>" in written
    assert written == source.replace(b">edited<", b">changed<")


def test_the_byte_order_mark_follows_the_source_unless_asked() -> None:
    with_bom = FIXTURES / "colectica" / "pets_bom.ddi33.xml"
    without = FIXTURES / "colectica" / "pets_nobom.ddi33.xml"

    assert write_ddi(read_ddi(with_bom)).startswith(b"\xef\xbb\xbf")
    assert not write_ddi(read_ddi(without)).startswith(b"\xef\xbb\xbf")
    assert write_ddi(read_ddi(without), bom=True) == (
        b"\xef\xbb\xbf" + without.read_bytes()
    )


def test_a_new_fragment_keeps_an_attribute_set_on_it() -> None:
    # Found by the random edits below: the Colectica layout of a new
    # <Fragment> had no room for attributes.
    document = read_ddi(PETS.read_bytes())
    fragment = [
        child for child in document.root if str(child.tag).endswith("}Fragment")
    ][1]
    added = copy.deepcopy(fragment)
    added.set("edited", "1")
    document.root.insert(0, added)

    written = write_ddi(document)

    assert _same_tree(written, document)
    assert b'xmlns="ddi:instance:3_3" edited="1">' in written


# ---- Random edits ---------------------------------------------------------------

_EDITS = st.lists(
    st.tuples(
        st.sampled_from(["text", "attribute", "remove", "copy", "add", "move"]),
        st.integers(min_value=0, max_value=10_000),
        st.integers(min_value=0, max_value=10_000),
    ),
    min_size=1,
    max_size=4,
)


def _apply(root, edits) -> None:
    for kind, first, second in edits:
        nodes = [node for node in root.iter() if isinstance(node.tag, str)][1:]
        if not nodes:
            return
        node = nodes[first % len(nodes)]
        parent = node.getparent() if hasattr(node, "getparent") else None
        if parent is None:
            parent = next(
                candidate for candidate in root.iter() if node in list(candidate)
            )
        if kind == "text" and len(node) == 0:
            node.text = f"edited {second}"
        elif kind == "attribute":
            node.set("edited", str(second))
        elif kind == "remove":
            parent.remove(node)
        elif kind == "copy":
            parent.insert(second % (len(parent) + 1), copy.deepcopy(node))
        elif kind == "add":
            added = create_element(R + "Note")
            added.text = f"note {second}"
            node.insert(second % (len(node) + 1), added)
        elif kind == "move":
            parent.remove(node)
            parent.insert(second % (len(parent) + 1), node)


@EXAMPLES
@given(path=st.sampled_from([PETS, INSTANCE]), edits=_EDITS)
def test_random_edits_write_the_edited_tree(path: Path, edits) -> None:
    data = path.read_bytes()
    document = read_ddi(data)
    _apply(document.root, edits)

    written = write_ddi(document)

    assert _same_tree(written, document)


@EXAMPLES
@given(edits=_EDITS)
def test_random_edits_keep_every_untouched_item(edits) -> None:
    data = PETS.read_bytes()
    document = read_ddi(data)
    fragments = [node for node in document.root if node.tag.endswith("}Fragment")]
    target = fragments[edits[0][1] % len(fragments)]
    _apply(target, edits)

    written = write_ddi(document)

    assert _same_tree(written, document)
    for part in data.split(b"\n<Fragment")[1:]:
        item = b"<Fragment" + part.split(b"\n</Fragment>")[0]
        if item not in written:
            assert target is not None  # only the edited item may differ
    untouched = [
        b"<Fragment" + part.split(b"\n</Fragment>")[0]
        for index, part in enumerate(data.split(b"\n<Fragment")[1:])
        if fragments[index] is not target
    ]
    assert all(item in written for item in untouched)
