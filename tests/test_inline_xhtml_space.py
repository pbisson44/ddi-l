"""The space between inline XHTML elements is text, on both backends.

In ``<b>Kind</b> <i>of</i> pet`` the space after ``</b>`` is the only text
between two elements, so a parser that drops blank text (lxml's
``remove_blank_text``) read it as indentation: the text became "Kindof pet",
and the stdlib backend, which keeps it, wrote the file differently. Both now
keep it where XHTML is inline and drop it where it is layout (between
blocks, around DDI elements), and write it back as read.
"""

from __future__ import annotations

import gzip
import io
from pathlib import Path
from typing import Any

import pytest

import ddi_l
from ddi_l._etree import USING_LXML, fromstring, tostring
from ddi_l.io import iterparse_ddi
from ddi_l.models import Category

FIXTURES = Path(__file__).parent / "fixtures" / "colectica"
CONDITIONS = FIXTURES / "pets_conditions.ddi33.xml"
XHTML = "http://www.w3.org/1999/xhtml"
X = f'xmlns="{XHTML}"'
DOG = "22222222-2222-4222-8222-000000000002"
DOG_LABEL = '<r:Content xml:lang="en-CA">Dog</r:Content>'

INLINE = {
    "elements-then-text": f"<b {X}>Kind</b> <i {X}>of</i> pet",
    "nested": f"Kind <span {X}><b>of</b> <i>pet</i></span>",
    "elements-only": f"<b {X}>Kind</b> <i {X}>of pet</i>",
    "space-first": f" <b {X}>Kind</b> of pet",
}


def _with_label(content: str) -> bytes:
    text = CONDITIONS.read_text(encoding="utf-8-sig")
    assert text.count(DOG_LABEL) == 1
    label = f'<r:Content xml:lang="en-CA">{content}</r:Content>'
    data = CONDITIONS.read_bytes()
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.replace(DOG_LABEL, label).encode()


def _fragment(source: bytes) -> ddi_l.DDIFragment:
    fragment = ddi_l.read_ddi(source)
    assert isinstance(fragment, ddi_l.DDIFragment)
    return fragment


@pytest.mark.parametrize("content", INLINE.values(), ids=INLINE.keys())
def test_the_space_is_text(content: str) -> None:
    dog = _fragment(_with_label(content)).get(DOG)
    assert isinstance(dog, Category)
    assert dog.labels[0].text.strip() == "Kind of pet"


@pytest.mark.parametrize("content", INLINE.values(), ids=INLINE.keys())
def test_inline_xhtml_round_trips_byte_for_byte(content: str) -> None:
    source = _with_label(content)
    fragment = _fragment(source)
    assert fragment.to_colectica_bytes() == source
    dog = fragment.get(DOG)
    assert dog is not None
    fragment.put(dog)
    assert fragment.to_colectica_bytes() == source


@pytest.mark.parametrize("content", INLINE.values(), ids=INLINE.keys())
def test_the_default_layout_keeps_the_space(content: str) -> None:
    fragment = _fragment(_with_label(content))
    written = fromstring(tostring(fragment.root))
    texts = {
        "".join(node.itertext()).strip()
        for node in written.iter("{ddi:reusable:3_3}Content")
    }
    assert "Kind of pet" in texts
    assert not {"Kindof pet", "Kind ofpet"} & texts


BLOCKS = {
    "compact": f"<p {X}>Kind</p><ul {X}><li>of pet</li></ul>",
    "indented": (
        f"\n        <p {X}>Kind</p>\n        <ul {X}>\n          <li>of pet</li>"
        "\n        </ul>\n      "
    ),
}


@pytest.mark.parametrize("content", BLOCKS.values(), ids=BLOCKS.keys())
def test_whitespace_between_blocks_is_layout(content: str) -> None:
    source = _with_label(content)
    once = _fragment(source).to_colectica_bytes()
    assert _fragment(once).to_colectica_bytes() == once
    dog = _fragment(source).get(DOG)
    assert isinstance(dog, Category)
    assert dog.labels[0].text == "Kind of pet"
    assert b"<p xmlns" in once and b"<li>of pet</li>" in once


def test_iterparse_reads_items_as_read_ddi_does() -> None:
    source = _with_label(INLINE["elements-then-text"])
    fragment = _fragment(source)
    streamed = list(iterparse_ddi(source))
    assert streamed
    for item in streamed:
        assert item.identifier is not None
        read = fragment.get(item.identifier)
        assert read is not None
        assert tostring(item.to_xml()) == tostring(read.to_xml()), item.identifier


INLINE_ONLY = {
    "inside-a-block": f"<p {X}><b>Pet</b><i>s</i></p>",
    "inline-only": f"<b {X}>Pet</b><i {X}>s</i>",
    "one-element": f"<b {X}>Pets</b>",
}


@pytest.mark.parametrize("content", INLINE_ONLY.values(), ids=INLINE_ONLY.keys())
def test_the_default_layout_does_not_indent_inline_xhtml(content: str) -> None:
    # Indenting <b>Pet</b><i>s</i> would read back as "Pet s".
    fragment = _fragment(_with_label(content))
    before = fragment.to_colectica_bytes()
    again = _fragment(tostring(fragment.root).encode())
    dog = again.get(DOG)
    assert isinstance(dog, Category)
    assert dog.labels[0].text == "Pets"
    # Writing the default layout does not change the tree read.
    assert fragment.to_colectica_bytes() == before


def test_blank_text_between_blocks_of_mixed_content_is_text() -> None:
    source = _with_label(f"<p {X}>Kind</p> <p {X}>of</p> pet")
    fragment = _fragment(source)
    dog = fragment.get(DOG)
    assert isinstance(dog, Category)
    assert dog.labels[0].text == "Kind of pet"
    assert fragment.to_colectica_bytes() == source
    (streamed,) = [i for i in iterparse_ddi(source) if i.identifier == DOG]
    assert isinstance(streamed, Category)
    assert streamed.labels[0].text == "Kind of pet"


def test_preserved_whitespace_stays_whatever_else_the_file_holds() -> None:
    preserved = (
        '<r:Content xml:lang="fr-CA" xml:space="preserve">\n   '
        f"<p {X}>Chien</p>\n   <p {X}>Chiens</p>\n</r:Content>"
    )
    text = _with_label(INLINE["elements-then-text"]).decode("utf-8-sig")
    text = text.replace('<r:Content xml:lang="fr-CA">Chien</r:Content>', preserved)
    root = fromstring(text.encode())
    (content,) = [
        node
        for node in root.iter("{ddi:reusable:3_3}Content")
        if node.get("{http://www.w3.org/XML/1998/namespace}space") == "preserve"
    ]
    assert content.text == "\n   "
    assert content[0].tail == "\n   "


def test_a_text_stream_is_read_in_its_own_encoding() -> None:
    text = '<?xml version="1.0" encoding="ISO-8859-1"?>\n' + _with_label(
        INLINE["elements-then-text"]
    ).decode("utf-8-sig").split("?>", 1)[1].replace("Chien", "Chien \u00e9")
    fragment = ddi_l.read_ddi(io.StringIO(text))
    assert isinstance(fragment, ddi_l.DDIFragment)
    dog = fragment.get(DOG)
    assert isinstance(dog, Category)
    assert [s.text.strip() for s in dog.labels] == ["Kind of pet", "Chien \u00e9"]


@pytest.mark.skipif(not USING_LXML, reason="lxml reads compressed files")
def test_a_compressed_file_is_read_again_compressed(tmp_path: Path) -> None:
    path = tmp_path / "pets.xml.gz"
    path.write_bytes(gzip.compress(_with_label(INLINE["elements-then-text"])))
    fragment = ddi_l.read_ddi(path)
    assert isinstance(fragment, ddi_l.DDIFragment)
    dog = fragment.get(DOG)
    assert isinstance(dog, Category)
    assert dog.labels[0].text == "Kind of pet"


def test_a_stream_is_rewound_for_the_second_reading(tmp_path: Path) -> None:
    path = tmp_path / "pets.xml"
    path.write_bytes(b"padding" + _with_label(INLINE["elements-then-text"]))
    with path.open("rb") as handle:
        handle.seek(len(b"padding"))
        root = ddi_l._etree.parse_xml(handle)
    texts = {"".join(n.itertext()) for n in root.iter("{ddi:reusable:3_3}Content")}
    assert "Kind of pet" in texts


def test_the_second_reading_is_not_skipped_by_reused_ids() -> None:
    # Many XHTML parents before the inline label: lxml frees each parent proxy
    # and reuses its address, which an id()-based "seen" set mistook for one
    # already looked at.
    text = CONDITIONS.read_text(encoding="utf-8-sig")
    list_label = '<r:Content xml:lang="en-CA">Kinds of pet</r:Content>'
    assert text.count(list_label) == 1
    paragraphs = "".join(
        f'\n      <r:Content xml:lang="{lang}"><p {X}>Kinds of pet</p></r:Content>'
        for lang in ("de", "es", "it", "nl", "pt", "sv", "da", "fi")
    )
    text = text.replace(list_label, list_label + paragraphs)
    text = text.replace(
        DOG_LABEL,
        f'<r:Content xml:lang="en-CA">{INLINE["elements-then-text"]}</r:Content>',
    )
    for _ in range(5):
        dog = _fragment(text.encode()).get(DOG)
        assert isinstance(dog, Category)
        assert dog.labels[0].text == "Kind of pet"


def test_a_stream_that_cannot_seek_is_read_whole() -> None:
    class ForwardOnly(io.RawIOBase):
        def __init__(self, data: bytes) -> None:
            self._data = io.BytesIO(data)

        def readable(self) -> bool:
            return True

        def seekable(self) -> bool:
            return True  # but it cannot

        def tell(self) -> int:
            return self._data.tell()

        def seek(self, *args: object) -> int:
            raise io.UnsupportedOperation("seek")

        def readinto(self, buffer: Any) -> int:
            chunk = self._data.read(len(buffer))
            buffer[: len(chunk)] = chunk
            return len(chunk)

    root = ddi_l._etree.parse_xml(
        ForwardOnly(_with_label(INLINE["elements-then-text"]))
    )
    texts = {"".join(n.itertext()) for n in root.iter("{ddi:reusable:3_3}Content")}
    assert "Kind of pet" in texts


@pytest.mark.parametrize("encoding", ["ISO-8859-1", "UTF-16"])
def test_a_str_is_read_whatever_its_declaration_says(encoding: str) -> None:
    text = _with_label("Chien été").decode("utf-8-sig")
    text = f'<?xml version="1.0" encoding="{encoding}"?>' + text.split("?>", 1)[1]
    for fragment in (ddi_l.read_ddi(text), ddi_l.DDIFragment.from_xml(text)):
        assert isinstance(fragment, ddi_l.DDIFragment)
        dog = fragment.get(DOG)
        assert isinstance(dog, Category)
        assert dog.labels[0].text == "Chien été"


def test_preserved_layout_is_written_as_read() -> None:
    preserved = (
        '<r:Content xml:lang="en-CA" xml:space="preserve">\n        '
        f"<p {X}>Dog</p>\n        <p {X}>Big</p>\n      </r:Content>"
    )
    fragment = _fragment(
        _with_label("Dog").replace(
            b'<r:Content xml:lang="en-CA">Dog</r:Content>', preserved.encode()
        )
    )
    again = fromstring(tostring(fragment.root).encode())
    (content,) = [
        node
        for node in again.iter("{ddi:reusable:3_3}Content")
        if node.get("{http://www.w3.org/XML/1998/namespace}space") == "preserve"
    ]
    assert "".join(content.itertext()) == "\n        Dog\n        Big\n      "


def test_a_line_break_separates_words() -> None:
    dog = _fragment(_with_label(f"Dog<br {X}/>Cat")).get(DOG)
    assert isinstance(dog, Category)
    assert dog.labels[0].text == "Dog Cat"
