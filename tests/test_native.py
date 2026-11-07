"""The native core matches its references.

Its parser builds the tree the standard library's builds, and refuses what
that parser refuses; its elements behave like the standard library's under
the same edits; its digests are ``ddi_l._lossless``'s after any edit; and,
on the native backend, its source index makes the lossless writer produce
the bytes the pure-Python index does.
"""

from __future__ import annotations

import copy
import io
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tests.helpers.examples import examples

native = pytest.importorskip("ddi_l_native")

from ddi_l import _lossless, read_ddi, write_ddi
from ddi_l._etree import NATIVE
from ddi_l._lossless import _digests
from tests.test_lossless import INSTANCE, PETS, _apply

FIXTURES = Path(__file__).parent / "fixtures"
XML_FILES = sorted(FIXTURES.rglob("*.xml"))
# Less the one deliberately truncated for the parsers' error tests.
WELL_FORMED_XML_FILES = [
    path for path in XML_FILES if path.name != "malformed_instance.xml"
]
EXAMPLES = examples(300)


def _same(native_root, stdlib_root) -> None:
    pending = [(native_root, stdlib_root)]
    while pending:
        mine, theirs = pending.pop()
        assert mine.tag == theirs.tag
        assert dict(mine.attrib) == dict(theirs.attrib)
        assert list(mine.keys()) == list(theirs.keys())
        assert mine.text == theirs.text
        assert mine.tail == theirs.tail
        assert len(mine) == len(theirs)
        pending.extend(zip(mine, theirs, strict=True))


def _same_outcome(data: bytes) -> None:
    """Native parses ``data`` to the stdlib's tree, or fails where it fails."""
    try:
        expected = ET.fromstring(data)
    except ET.ParseError:
        expected = None
    try:
        mine = native.parse(data)
    except ET.ParseError as error:
        # Native refuses a document type declaration, which expat reads.
        assert expected is None or "Document type declarations" in str(error)
        return
    assert expected is not None, "native read what the standard library refuses"
    _same(mine, expected)


# ---- Parsing ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "path", XML_FILES, ids=lambda path: str(path.relative_to(FIXTURES))
)
def test_every_fixture_parses_to_the_standard_librarys_tree(path: Path) -> None:
    _same_outcome(path.read_bytes())


WELL_FORMED = [
    b'<?xml version="1.0" encoding="UTF-8"?>\n<a/>',
    b"\xef\xbb\xbf<a>bom</a>",
    b"<a>x &lt; y &amp; &#65;&#x42; &gt; &quot;&apos;</a>",
    b"<a>one<!-- c -->two<?pi data?>three</a>",
    b"<a><![CDATA[<raw> & ]]>after</a>",
    b"<a>\r\nline\rend</a>",
    b'<a x="a\tb\r\nc\nd" y="&#10;&#9;"/>',
    b'<a xmlns="urn:d" xmlns:p="urn:p"><p:b p:c="1" c="2"><c xmlns=""/></p:b></a>',
    b'<a xml:lang="en"><b xml:space="preserve">  </b></a>',
    b"<a>\n  <b>t</b>tail\n  <c/>\n</a>\n<!-- after -->\n",
    "<café été='é'>é</café>".encode(),
    b"<a b='1' c=\"2\" d = '3' />",
    b"<a><b></b><c><![CDATA[]]></c></a>",
]

MALFORMED = [
    b"",
    b"   ",
    b"<a>",
    b"<a></b>",
    b"<a><b></a></b>",
    b"<p:a/>",
    b'<a x="1" x="2"/>',
    b'<a xmlns:p="u" xmlns:q="u" p:x="1" q:x="2"/>',
    b"<a>&nope;</a>",
    b"<a>&#0;</a>",
    b"<a>&#xD800;</a>",
    b"<a/><b/>",
    b"<a/>junk",
    b"text<a/>",
    b"<a>]]></a>",
    b'<a x="<"/>',
    b"<a>\x01</a>",
    b"<a>\xff</a>",
    b"<a>\xef\xbf\xbe</a>",
    b"<a><!-- a -- b --></a>",
    b"<a><!-- open</a>",
    b"<a><?xml version='1.0'?></a>",
    b"<a x='1'y='2'/>",
    b"<1a/>",
    b"<a></a  b>",
    b"<a b/>",
]


@pytest.mark.parametrize("data", WELL_FORMED + MALFORMED, ids=repr)
def test_the_parser_reads_and_refuses_what_the_standard_library_does(
    data: bytes,
) -> None:
    _same_outcome(data)


# The monthly workflow raises the number of examples.
FUZZ = settings(
    max_examples=int(os.environ.get("DDI_L_FUZZ_EXAMPLES", "300")),
    deadline=None,
    suppress_health_check=list(HealthCheck),
)
_PIECES = st.sampled_from(
    [
        b"<",
        b">",
        b"/",
        b"a",
        b"b",
        b":",
        b"p",
        b"=",
        b'"',
        b"'",
        b"&",
        b"lt",
        b";",
        b"#",
        b"x",
        b"4",
        b"1",
        b" ",
        b"\t",
        b"\n",
        b"\r",
        b"<!--",
        b"--",
        b"-->",
        b"<![CDATA[",
        b"]]>",
        b"<?",
        b"?>",
        b"xmlns",
        b"xml",
        b"\xc3\xa9",
        b"\x01",
        b"\xff",
        b"<a>",
        b"</a>",
        b"<b/>",
        b'="v"',
        b"<!DOCTYPE a>",
    ]
)


@FUZZ
@given(pieces=st.lists(_PIECES, max_size=40))
def test_fuzzed_input_is_read_as_the_standard_library_reads_it(pieces) -> None:
    _same_outcome(b"".join(pieces))


@FUZZ
@given(
    edits=st.lists(
        st.tuples(st.integers(min_value=0), st.integers(0, 3), _PIECES), max_size=6
    )
)
def test_a_damaged_document_is_read_as_the_standard_library_reads_it(edits) -> None:
    data = bytearray(SOURCE)
    for position, length, piece in edits:
        at = position % (len(data) + 1)
        data[at : at + length] = piece
    _same_outcome(bytes(data))


def test_a_document_type_declaration_is_refused() -> None:
    with pytest.raises(ET.ParseError, match="Document type declarations"):
        native.parse(b'<!DOCTYPE a [<!ENTITY e "x">]><a>&e;</a>')


def test_a_parse_error_carries_its_line_and_column() -> None:
    with pytest.raises(ET.ParseError) as raised:
        native.parse(b"<a>\n  <b>\n</a>")
    assert raised.value.position[0] == 3
    assert "mismatched tag" in str(raised.value)


# ---- Elements behave like the standard library's ----------------------------------

SOURCE = (
    b'<r xmlns:p="urn:p"><a k="1">t<b/>u</a><p:c p:k="2">v</p:c>'
    b"<a k='3'><d>w</d></a></r>"
)

_OPERATIONS = st.lists(
    st.tuples(
        st.sampled_from(
            [
                "text",
                "tail",
                "set",
                "del-attribute",
                "update",
                "append",
                "insert",
                "remove",
                "delete",
                "delete-slice",
                "replace",
                "clear",
                "tag",
                "extend",
            ]
        ),
        st.integers(min_value=0, max_value=50),
        st.integers(min_value=-5, max_value=50),
    ),
    max_size=12,
)


def _edit(root, make, operation) -> None:
    kind, first, second = operation
    nodes = list(root.iter())
    node = nodes[first % len(nodes)]
    if kind == "text":
        node.text = None if second < 0 else f"text {second}"
    elif kind == "tail":
        node.tail = None if second < 0 else f"tail {second}"
    elif kind == "set":
        node.set(f"k{second % 3}", str(second))
    elif kind == "del-attribute" and len(node.attrib):
        del node.attrib[sorted(node.attrib)[second % len(node.attrib)]]
    elif kind == "update":
        node.attrib.update({"u": str(second)}, v="w")
    elif kind == "append":
        node.append(make(f"n{second}"))
    elif kind == "insert":
        node.insert(second, make(f"i{second}"))
    elif kind == "remove" and len(node):
        node.remove(node[second % len(node)])
    elif kind == "delete" and len(node):
        del node[second % len(node)]
    elif kind == "delete-slice":
        del node[second % 3 :: 2]
    elif kind == "replace" and len(node):
        node[second % len(node)] = make(f"s{second}")
    elif kind == "clear" and node is not root:
        node.clear()
    elif kind == "tag":
        node.tag = f"{{urn:p}}t{second}"
    elif kind == "extend":
        node.extend([make(f"e{second}"), make("f")])


def _queries(root) -> list:
    found = []
    for node in root.iter():
        found.append(
            (
                node.tag,
                sorted(node.items()),
                node.get("k"),
                node.get("missing", "default"),
                [child.tag for child in node.findall("a")],
                [child.tag for child in node.findall(".//{urn:p}c")],
                getattr(node.find("a"), "tag", None),
                node.findtext("a"),
                node.findtext("missing", "default"),
                list(node.itertext()),
                [child.tag for child in node.iter("a")],
                [child.tag for child in node[1:]],
                "k" in node.attrib,
                len(node),
            )
        )
    return found


@EXAMPLES
@given(operations=_OPERATIONS)
def test_edits_leave_the_tree_the_standard_library_would(operations) -> None:
    mine, theirs = native.parse(SOURCE), ET.fromstring(SOURCE)
    for operation in operations:
        _edit(mine, native.Element, operation)
        _edit(theirs, ET.Element, operation)
        _same(mine, theirs)
    assert _queries(mine) == _queries(theirs)
    assert ET.tostring(mine) == ET.tostring(theirs)


def test_an_element_is_one_object_while_it_is_alive() -> None:
    root = native.parse(SOURCE)
    first = root[0]
    assert root[0] is first
    assert next(iter(root)) is first
    assert next(root.iter()) is root
    assert root.find("a") is first


def test_adding_an_element_moves_it_and_cycles_are_refused() -> None:
    root = native.parse(SOURCE)
    first, last = root[0], root[2]
    last.append(first)
    assert [child.tag for child in root] == ["{urn:p}c", "a"]
    assert last[-1] is first
    with pytest.raises(ValueError):
        first.append(root)
    with pytest.raises(ValueError):
        first.append(first)
    with pytest.raises(TypeError):
        root.append(ET.Element("x"))


def test_a_deep_copy_is_separate_and_equal() -> None:
    root = native.parse(SOURCE)
    copied = copy.deepcopy(root[0])
    _same(copied, ET.fromstring(SOURCE)[0])
    copied.text = "changed"
    assert root[0].text == "t"


def test_attributes_are_a_live_mapping() -> None:
    from collections.abc import MutableMapping

    root = native.parse(SOURCE)
    attrib = root[0].attrib
    assert isinstance(attrib, MutableMapping)
    attrib["n"] = "2"
    assert root[0].get("n") == "2"
    assert attrib.pop("n") == "2"
    assert attrib.pop("n", None) is None
    assert attrib == {"k": "1"}
    assert dict(attrib) == {"k": "1"}
    with pytest.raises(KeyError):
        attrib["missing"]


# ---- Digests -----------------------------------------------------------------------


def _digest_parity(root) -> None:
    elements = list(root.iter())  # alive, so each keeps its id
    reference = _digests(root)
    for element in elements:
        assert native.digest(element) == reference[id(element)]


@EXAMPLES
@given(operations=_OPERATIONS)
def test_a_cached_digest_follows_every_edit(operations) -> None:
    root = native.parse(SOURCE)
    _digest_parity(root)
    for operation in operations:
        _edit(root, native.Element, operation)
        _digest_parity(root)


@pytest.mark.parametrize("path", [PETS, INSTANCE], ids=lambda path: path.name)
def test_digests_match_the_reference(path: Path) -> None:
    _digest_parity(native.parse(path.read_bytes()))


# ---- The lossless writer's index (native backend) ----------------------------------

native_backend = pytest.mark.skipif(
    not NATIVE, reason="the native backend is not active"
)


def _written(data: bytes, edits, *, reference: bool, monkeypatch) -> bytes:
    document = read_ddi(data)
    _apply(document.root, edits)
    with monkeypatch.context() as patch:
        if reference:
            patch.setattr(_lossless, "NATIVE", False)
        return write_ddi(document)


@native_backend
@pytest.mark.parametrize("path", [PETS, INSTANCE], ids=lambda path: path.name)
def test_the_native_index_is_the_reference_index(path: Path) -> None:
    data = path.read_bytes()
    _root, index = native.parse(data, index=True)
    table = native.Table(index)
    reference = _lossless._scan(data)
    assert reference is not None
    assert len(table) == len(reference)
    for at, span in enumerate(reference):
        mine = table.span(at)
        assert (mine.start, mine.open_end, mine.close_start, mine.end, mine.depth) == (
            span.start,
            span.open_end,
            span.close_start,
            span.end,
            span.depth,
        )
        assert mine.children == span.children
        assert mine.declares == span.declares
        assert mine.tag_needs == span.tag_needs
        assert mine.needs == span.needs
        assert mine.self_closing == span.self_closing


@native_backend
@EXAMPLES
@given(
    path=st.sampled_from([PETS, INSTANCE]),
    edits=st.lists(
        st.tuples(
            st.sampled_from(["text", "attribute", "remove", "copy", "add", "move"]),
            st.integers(min_value=0, max_value=10_000),
            st.integers(min_value=0, max_value=10_000),
        ),
        max_size=4,
    ),
)
def test_the_native_index_writes_the_reference_bytes(path: Path, edits) -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        data = path.read_bytes()
        assert _written(
            data, edits, reference=False, monkeypatch=monkeypatch
        ) == _written(data, edits, reference=True, monkeypatch=monkeypatch)


def test_streams_are_read_as_utf8_whatever_they_declare() -> None:
    from ddi_l._etree import fromstring

    latin = '<?xml version="1.0" encoding="ISO-8859-1"?><a>café</a>'.encode("latin-1")
    assert fromstring(latin).text == "café"
    utf16 = '<?xml version="1.0" encoding="UTF-16"?><a>é</a>'.encode("utf-16")
    assert fromstring(utf16).text == "é"
    assert fromstring(io.BytesIO(b"<a/>").read()).tag == "a"


# ---- Schema validation (native backend) ---------------------------------------------

_MUTATIONS = st.lists(
    st.tuples(
        st.sampled_from(
            [
                "remove",
                "duplicate",
                "unknown",
                "swap",
                "attribute",
                "text",
                "value",
                "drop",
                "tail",
            ]
        ),
        st.integers(min_value=0, max_value=10_000),
        st.sampled_from(
            [
                "x y",
                "-1",
                "1.5",
                "",
                "true",
                "2024-13-01",
                "P1Y",
                "abc$$",
                " 12 ",
                "en",
                "1e5",
                "@@",
            ]
        ),
    ),
    min_size=1,
    max_size=3,
)


def _mutate(root, mutations) -> None:
    from ddi_l._etree import create_element

    for kind, at, value in mutations:
        nodes = list(root.iter())[1:]
        node = nodes[at % len(nodes)]
        parent = next(p for p in root.iter() if any(c is node for c in p))
        index = list(parent).index(node)
        if kind == "remove":
            parent.remove(node)
        elif kind == "duplicate":
            parent.insert(index, copy.deepcopy(node))
        elif kind == "unknown":
            parent.insert(index, create_element("{ddi:reusable:3_3}Bogus"))
        elif kind == "swap" and index:
            parent.remove(node)
            parent.insert(index - 1, node)
        elif kind == "attribute":
            node.set("bogus", "1")
        elif kind == "text":
            node.text = value
        elif kind == "value" and node.attrib:
            node.set(sorted(node.attrib)[at % len(node.attrib)], value)
        elif kind == "drop" and node.attrib:
            del node.attrib[sorted(node.attrib)[at % len(node.attrib)]]
        elif kind == "tail":
            node.tail = "junk"


def _native_errors(root, version: str):
    from ddi_l.schema_loader._cache import get_schema
    from ddi_l.schema_loader._native_validation import schema_errors, unflagged

    schema = get_schema(version)
    expected = [(error.reason, error.path) for error in schema.iter_errors(root)]
    found = unflagged(root, version)
    if found is None:  # left to xmlschema as a whole
        return expected, expected
    return [
        (e.reason, e.path) for e in schema_errors(schema, root, version, found)
    ], expected


@native_backend
@EXAMPLES
@given(path=st.sampled_from([PETS, INSTANCE]), mutations=_MUTATIONS)
def test_native_validation_finds_xmlschemas_errors(path: Path, mutations) -> None:
    from ddi_l._etree import parse_xml

    root = parse_xml(path)
    _mutate(root, mutations)
    found, expected = _native_errors(root, "3.3")
    assert found == expected


@native_backend
@pytest.mark.parametrize(
    "path", WELL_FORMED_XML_FILES, ids=lambda path: str(path.relative_to(FIXTURES))
)
def test_native_validation_agrees_on_every_fixture(path: Path) -> None:
    from ddi_l._etree import parse_xml
    from ddi_l.schema_loader._versions import (
        detect_version_from_element,
        normalize_version,
    )

    root = parse_xml(path)
    version = normalize_version(detect_version_from_element(root))
    found, expected = _native_errors(root, version)
    assert found == expected


@native_backend
def test_a_valid_document_never_loads_xmlschema(monkeypatch) -> None:
    from ddi_l import schema_loader
    from ddi_l._etree import parse_xml

    def refuse(*_args, **_kwargs):
        raise AssertionError("xmlschema was loaded")

    monkeypatch.setattr(schema_loader, "get_schema", refuse)
    root = parse_xml(PETS)
    assert schema_loader.validate(root, raise_error=False, backend="native") == []


@native_backend
def test_native_issues_carry_their_line() -> None:
    from ddi_l import schema_loader
    from ddi_l._etree import parse_xml

    data = PETS.read_bytes().replace(b"<r:Version>", b"<r:Bogus/><r:Version>", 1)
    root = parse_xml(io.BytesIO(data))
    native = schema_loader.validate(root, raise_error=False, backend="native")
    python = schema_loader.validate(root, raise_error=False, backend="python")
    assert native == python
    line = data[: data.index(b"<r:Bogus/>")].count(b"\n") + 1
    parent_line = native[0].line
    assert parent_line is not None and parent_line <= line
