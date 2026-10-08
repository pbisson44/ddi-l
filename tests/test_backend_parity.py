# mypy: ignore-errors
"""The two XML backends must serialize identical input to identical bytes.

Whether ``lxml`` is installed must not change the bytes ``ddi-l`` writes.
A process has only one backend active, so these tests pin the properties
that keep the backends aligned, each checkable from either side:

* prefixes come from the canonical DDI table, never from a generated
  ``ns1``/``p0`` name, and never from whatever a source file happened to use;
* namespace declarations are emitted in a deterministic order;
* empty elements use one spelling.

Together these make golden files meaningful regardless of install.
"""

from __future__ import annotations

import re

from ddi_l import read_ddi, write_ddi
from ddi_l._etree import fromstring, parse_xml, tostring
from ddi_l.document import DDIDocument
from ddi_l.examples.build_and_validate import build_example_document
from ddi_l.models import StudyUnit
from ddi_l.namespace_utils import extract_namespace_declarations
from ddi_l.namespaces import NAMESPACE_PREFIXES, canonicalize_prefixes
from tests import EXAMPLES_DIR, PACKAGE_FIXTURES_DIR

INSTANCE_FIXTURES = (
    PACKAGE_FIXTURES_DIR / "minimal_instance.xml",
    PACKAGE_FIXTURES_DIR / "instances" / "example_instance.xml",
    PACKAGE_FIXTURES_DIR / "instances" / "quality_of_life_instance.xml",
)

_CANONICAL_FOR_URI = {uri: prefix for prefix, uri in NAMESPACE_PREFIXES.items()}


def test_canonicalize_prefixes_rekeys_known_namespaces():
    """A source document's arbitrary prefixes map onto the canonical ones."""
    source = {
        None: "ddi:instance:3_3",
        "p0": "ddi:conceptualcomponent:3_3",
        "p4": "ddi:studyunit:3_3",
        "ns1": "ddi:reusable:3_3",
    }

    result = canonicalize_prefixes(source)

    assert result == {
        None: "ddi:instance:3_3",
        "c": "ddi:conceptualcomponent:3_3",
        "s": "ddi:studyunit:3_3",
        "r": "ddi:reusable:3_3",
    }


def test_canonicalize_prefixes_leaves_foreign_namespaces_alone():
    """Prefixes the library does not own are the caller's business."""
    source = {None: "urn:example:default", "acme": "urn:acme:custom"}

    assert canonicalize_prefixes(source) == source


def test_instances_serialize_with_canonical_prefixes():
    """No generated ``p0``/``ns1`` prefix survives a read/write cycle.

    The bundled instance fixtures deliberately declare ``p0``..``p4``.
    """
    for fixture in INSTANCE_FIXTURES:
        declared = extract_namespace_declarations(
            fromstring(read_ddi(fixture).to_xml(pretty_print=True))
        )
        for prefix, uri in declared.items():
            if prefix in (None, ""):
                continue
            canonical = _CANONICAL_FOR_URI.get(uri)
            if canonical is not None:
                assert prefix == canonical, (
                    f"{fixture.name}: {uri} emitted as {prefix!r}, "
                    f"expected the canonical {canonical!r}"
                )


def test_namespace_declarations_are_emitted_in_a_stable_order():
    """Declaration order must not depend on dict insertion order."""
    for fixture in INSTANCE_FIXTURES:
        first_line = read_ddi(fixture).to_xml(pretty_print=True).splitlines()[0]
        prefixes = [
            chunk.split("=", 1)[0].removeprefix("xmlns:")
            for chunk in first_line.split()
            if chunk.startswith("xmlns:")
        ]
        assert prefixes == sorted(prefixes), (
            f"{fixture.name}: namespace declarations are not sorted: {prefixes}"
        )


def test_empty_elements_use_a_single_spelling():
    """``<tag/>`` on both backends -- ElementTree's default is ``<tag />``."""
    rendered = tostring(fromstring("<root><child/></root>"), pretty_print=False)

    assert "<child/>" in rendered
    assert "<child />" not in rendered


def test_model_round_trip_ignores_the_source_documents_prefixes():
    """Re-serializing adopts canonical prefixes rather than echoing the input."""
    fixture = PACKAGE_FIXTURES_DIR / "models" / "study_unit_minimal.xml"

    rendered = tostring(
        StudyUnit.from_xml(parse_xml(fixture)).to_xml(), pretty_print=False
    )

    assert "ns0:" not in rendered
    assert "ns1:" not in rendered
    assert ":StudyUnit" in rendered or "<StudyUnit" in rendered


def test_xml_declaration_has_one_spelling():
    """Both backends write the same declaration.

    lxml emits ``<?xml version='1.0' encoding='utf-8'?>`` and the stdlib
    double-quotes and upper-cases it. Nothing reads the difference, but it puts
    a spurious first-line diff on every file written by the other install.
    """
    document = DDIDocument.create(agency="example.org", identifier="d", version="1.0")

    payload = write_ddi(document, None)

    assert payload.startswith(b'<?xml version="1.0" encoding="UTF-8"?>\n')


def test_pretty_printed_output_ends_with_a_newline():
    """A pretty-printed document is a text file and ends like one."""
    document = DDIDocument.create(agency="example.org", identifier="d", version="1.0")

    assert write_ddi(document, None).endswith(b"\n")


def test_namespace_declarations_live_only_on_the_root():
    """Bindings are hoisted, so a model's NSMAP does not re-declare per element.

    lxml fixes an element's namespace map at creation; declarations must still
    be hoisted to the root, as on the stdlib backend.
    """
    document = build_example_document()

    lines = write_ddi(document, None).decode("utf-8").splitlines()

    offenders = [
        line.strip()[:100] for line in lines[2:] if "xmlns:" in line or "xmlns=" in line
    ]
    assert offenders == [], (
        f"{len(offenders)} element(s) below the root re-declare a namespace: {offenders[:3]}"
    )


def test_third_party_layouts_round_trip_with_content_intact():
    """A foreign namespace layout survives semantically, if not byte for byte.

    ``Quality_of_Life.xml`` declares namespaces in a style ``ddi-l`` never
    produces -- a prefixed root plus per-element ``xmlns=`` redeclarations --
    and the two backends spell the result differently: lxml echoes the source
    layout, the stdlib canonicalises it onto the root. lxml fixes an element's
    prefix when the element is created, so matching would mean rebuilding every
    subtree that carries its own nsmap, on the write path, for prefix
    cosmetics.

    What must hold, and is what actually matters, is that neither backend
    changes the document: same elements, same qualified names, same attributes,
    same text. The byte-for-byte guarantee is asserted separately for documents
    ``ddi-l`` authors, which is where version-control churn would bite.
    """
    source = EXAMPLES_DIR / "Quality_of_Life.xml"

    original = parse_xml(source)
    reserialized = fromstring(write_ddi(read_ddi(source), None))

    def skeleton(root):
        return [
            (
                node.tag if isinstance(node.tag, str) else "<non-element>",
                tuple(sorted(node.attrib.items())),
                (node.text or "").strip(),
            )
            for node in root.iter()
        ]

    before, after = skeleton(original), skeleton(reserialized)

    assert len(after) == len(before), (
        f"element count changed on round-trip: {len(before)} -> {len(after)}"
    )
    assert after == before, "round-tripping altered the document's content"


def test_documents_ddi_l_authors_use_only_canonical_prefixes():
    """Nothing we author is written with a generated prefix for a DDI namespace.

    This is the property that makes output byte-identical across backends for
    documents ``ddi-l`` creates: every DDI namespace resolves to its canonical
    prefix rather than an invented ``ns0``/``p1``, on either backend.
    """
    rendered = write_ddi(build_example_document(), None).decode("utf-8")

    declarations = dict(re.findall(r'xmlns:([A-Za-z0-9_]+)="([^"]+)"', rendered))
    generated_ddi = {
        prefix: uri
        for prefix, uri in declarations.items()
        if uri.startswith("ddi:") and re.fullmatch(r"(ns|p)\d+", prefix)
    }

    assert generated_ddi == {}, (
        f"DDI namespaces bound to generated prefixes: {generated_ddi}"
    )


def _authored_document():
    """A document built through the CRUD facade, as the docs teach."""
    import ddi_l as ddi

    document = ddi.new_study(title="Parity Check", agency="example.org")
    question = document.add_question(text="How old are you?")
    document.add_variable(name="age", question=question)
    document.add_concept(name="Age")
    return document


def test_save_and_to_xml_agree(tmp_path):
    """``save()`` writes exactly what ``to_xml()`` returns, byte for byte."""
    document = _authored_document()

    target = tmp_path / "saved.xml"
    document.save(target)

    assert target.read_bytes() == document.to_xml().encode("utf-8")


def test_the_crud_facade_declares_no_unused_namespace(tmp_path):
    """``save()`` prunes a binding the document does not use.

    A document built from the default map declares ``xsi`` on lxml whether or
    not anything uses it; pruning makes the backends agree.
    """
    document = _authored_document()
    target = tmp_path / "saved.xml"
    document.save(target)

    _assert_declares_no_unused_namespace(target.read_text(encoding="utf-8"))


def _assert_declares_no_unused_namespace(rendered: str) -> None:
    """Assert every ``xmlns:`` binding in ``rendered`` is actually used."""
    declared = set(re.findall(r"xmlns:([A-Za-z0-9_]+)=", rendered))
    used = set(re.findall(r"<([A-Za-z0-9_]+):", rendered))

    assert declared <= used, f"declared but never used: {sorted(declared - used)}"


def test_write_ddi_declares_no_unused_namespace(tmp_path):
    """``write_ddi()`` is held to the same bar as ``save()``.

    The property above was pinned on one writer only, and the other quietly
    broke it: ``write_ddi`` seeded its root map from the defaults, so every file
    it produced declared ``xmlns:xsi`` that nothing used. Demo 5 shipped it, and
    demo 8's round-trip -- which tells the reader that any difference means
    something did not survive the parse -- came back 54 bytes longer than it
    went in, all of them that one declaration.
    """
    from ddi_l.io import write_ddi

    target = tmp_path / "written.xml"
    write_ddi(_authored_document().inner, target)

    _assert_declares_no_unused_namespace(target.read_text(encoding="utf-8"))


def test_write_ddi_round_trips_byte_for_byte(tmp_path):
    """What `write_ddi` returns for a parsed document is what it was given.

    This is the identity demo 8 states in prose at ``/v1/roundtrip``. It did not
    hold: the writer added a namespace declaration on the way out.
    """
    from ddi_l.io import read_ddi, write_ddi

    original = _authored_document().to_xml().encode("utf-8")

    assert write_ddi(read_ddi(original)) == original


def test_the_crud_facade_output_carries_the_declaration_and_newline(tmp_path):
    """The properties pinned for ``write_ddi()``, asserted on the facade's own path."""
    document = _authored_document()
    target = tmp_path / "saved.xml"
    document.save(target)

    payload = target.read_bytes()

    assert payload.startswith(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    assert payload.endswith(b"\n")


def test_the_crud_facade_hoists_namespaces_onto_the_root(tmp_path):
    """No element below the root re-declares a namespace, via ``save()``."""
    document = _authored_document()
    target = tmp_path / "saved.xml"
    document.save(target)

    lines = target.read_text(encoding="utf-8").splitlines()
    offenders = [
        line.strip()[:100] for line in lines[2:] if "xmlns:" in line or "xmlns=" in line
    ]

    assert offenders == [], (
        f"{len(offenders)} element(s) below the root re-declare a namespace: "
        f"{offenders[:3]}"
    )


def test_a_document_that_uses_xsi_keeps_its_declaration(tmp_path):
    """Pruning the unused xsi binding must not prune a used one.

    A document carrying ``xsi:schemaLocation`` keeps its ``xmlns:xsi``
    declaration.
    """
    from ddi_l.constants import XSI_NS
    from ddi_l.io import read_ddi, write_ddi

    source = _authored_document().to_xml()
    located = source.replace(
        "<DDIInstance ",
        f'<DDIInstance xmlns:xsi="{XSI_NS}" '
        'xsi:schemaLocation="ddi:instance:3_3 instance.xsd" ',
        1,
    ).encode("utf-8")

    target = tmp_path / "with-schema-location.xml"
    write_ddi(read_ddi(located), target)
    rendered = target.read_text(encoding="utf-8")

    assert "xsi:schemaLocation" in rendered
    assert f'xmlns:xsi="{XSI_NS}"' in rendered, (
        "the document uses the xsi prefix, so the declaration has to survive:\n"
        + rendered.splitlines()[1]
    )
