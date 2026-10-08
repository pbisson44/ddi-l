import os
import subprocess
import sys
import textwrap
from pathlib import Path
from uuid import uuid5

import pytest

from ddi_l import (
    Concept,
    DataCollection,
    InternationalString,
    LogicalProduct,
    QuestionItem,
    Reference,
    StudyUnit,
    Variable,
    schema_loader,
)
from ddi_l.document import INSTANCE_NS, DDIDocument
from ddi_l.models import CollectionEvent
from ddi_l.models.datacollection import _REFERENCE_NAMESPACE
from ddi_l.namespaces import (
    DDI_PROFILE_PROFILE,
    DDI_STUDY_UNIT_PROFILE,
)


@pytest.fixture(scope="module")
def document_fixtures(fixtures_dir: Path) -> Path:
    """Directory containing document-level XML fixtures."""

    return fixtures_dir


def test_round_trip_from_fixture(document_fixtures: Path):
    """Round-trip fixture XML through DDIDocument to ensure lossless conversion."""
    source = document_fixtures / "minimal_instance.xml"
    document = DDIDocument.from_xml(source, validate=True)
    identification = document.get_identification()
    expected_identifier = str(
        uuid5(_REFERENCE_NAMESPACE, "example.agency:minimal-instance")
    )
    assert identification == {
        "agency": "example.agency",
        "id": expected_identifier,
        "version": "1.0",
    }

    xml_output = document.to_xml()
    schema_loader.validate(xml_output)

    reparsed = DDIDocument.from_xml(xml_output, validate=True)
    assert reparsed.get_identification() == identification

    data = reparsed.to_dict()
    assert data["{ddi:reusable:3_3}Agency"] == "example.agency"


def test_document_validate_surfaces_structured_errors(document_fixtures: Path):
    """Document.validate returns structured issues for invalid fixture data."""
    source = document_fixtures / "invalid_instance_missing_id.xml"
    document = DDIDocument.from_xml(source)

    issues = document.validate()
    assert issues
    issue = issues[0]
    assert "Missing required identification" in issue.message
    assert issue.xpath.endswith("DDIInstance")  # type: ignore[union-attr]


def test_builder_and_mutation_support():
    """Builder helpers allow mutation, namespace setup, and validation."""
    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
        title="Demo Instance",
    )
    document.ensure_namespace_prefixes(DDI_PROFILE_PROFILE)
    assert "xmlns:pr" in document.to_xml()

    document.set_identification(
        agency="demo.agency", identifier="demo-instance", version="2.0"
    )
    document.set_citation(title="Updated Demo", lang="en")
    # `ensure_namespace_prefixes()` declares the default map, and on the stdlib
    # backend declarations are literal attributes that xmlschema reports as
    # not allowed; filter those issues.
    issues = [
        issue
        for issue in document.validate()
        if "'xmlns:xsi' attribute not allowed for element" not in issue.message
    ]
    assert issues == []

    assert document.get_identification()["version"] == "2.0"


def test_namespace_profiles_propagate_to_study_units():
    """Ensuring namespace profiles propagate to StudyUnit XML output."""
    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    study = StudyUnit(
        agency="demo.agency",
        identifier="demo-study",
        version="1.0",
        data_collection_references=[
            Reference(
                agency="demo.agency",
                identifier="demo-collection",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    document.add_study_unit(study)
    document.ensure_namespace_prefixes(DDI_STUDY_UNIT_PROFILE)

    xml_output = document.to_xml(pretty_print=False)
    assert 'xmlns:s="ddi:studyunit:3_3"' in xml_output
    assert 'xmlns:c="ddi:conceptualcomponent:3_3"' in xml_output
    assert "<s:StudyUnit" in xml_output


def test_set_identification_multiple_updates_preserve_ordering():
    """Multiple identification updates preserve element order without duplicates."""
    document = DDIDocument.create(
        agency="initial.agency",
        identifier="initial-id",
        version="0.1",
    )

    # First update without scope.
    document.set_identification(
        agency="agency.one",
        identifier="identifier-one",
        version="1.0",
    )

    # Second update includes a scope of uniqueness to ensure attribute management.
    document.set_identification(
        agency="agency.two",
        identifier="identifier-two",
        version="2.0",
        scope_of_uniqueness="Study",
    )

    # Third update should replace the previous values cleanly while retaining ordering.
    document.set_identification(
        agency="agency.three",
        identifier="identifier-three",
        version="3.0",
    )

    agency_element, id_element, version_element, *rest = list(document.root)
    assert agency_element.tag.endswith("Agency")
    assert id_element.tag.endswith("ID")
    assert version_element.tag.endswith("Version")
    assert agency_element.text == "agency.three"
    assert id_element.text == "identifier-three"
    assert version_element.text == "3.0"
    assert not rest  # No leftover duplicate elements

    xml_output = document.to_xml(pretty_print=False)
    assert xml_output.count("agency.two") == 0
    assert xml_output.count("identifier-two") == 0
    assert xml_output.count("agency.three") == 1
    assert xml_output.count("identifier-three") == 1


def test_set_identification_scope_updates_attribute():
    """Scope changes update scopeOfUniqueness attribute and support removal."""
    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    document.set_identification(
        agency="agency.scope",
        identifier="identifier-scope",
        version="4.2",
        scope_of_uniqueness="Series",
    )

    assert document.root.get("scopeOfUniqueness") == "Series"
    xml_output = document.to_xml(pretty_print=False)
    assert 'scopeOfUniqueness="Series"' in xml_output

    # Toggling the scope off should remove the attribute entirely.
    document.set_identification(
        agency="agency.scope",
        identifier="identifier-scope",
        version="4.3",
    )

    assert document.root.get("scopeOfUniqueness") is None


def test_to_etree_exposes_underlying_element():
    """`to_etree` returns the root element with the expected namespace tag."""
    document = DDIDocument.create(agency="demo", identifier="id", version="1.0")
    element = document.to_etree()
    assert element.tag == f"{{{INSTANCE_NS}}}DDIInstance"


def test_to_dict_preserves_qnames_with_xmlschema(fixtures_dir: Path):
    """to_dict retains QName keys when xmlschema helpers are present."""
    pytest.importorskip("xmlschema")

    source = fixtures_dir / "minimal_instance.xml"
    document = DDIDocument.from_xml(source)

    data = document.to_dict()
    assert data["{ddi:reusable:3_3}Agency"] == "example.agency"


def test_ensure_namespace_prefixes_under_lxml():
    """ensure_namespace_prefixes retains custom prefixes when using lxml."""

    repo_root = Path(__file__).resolve().parents[1]
    python_paths = [str(repo_root / "src"), str(repo_root)]
    script = textwrap.dedent(
        """
        import importlib
        import sys
        import types
        from copy import deepcopy

        # Provide a lightweight lxml replacement that exercises the lxml code path.
        class FakeElement:
            def __init__(self, tag, *, nsmap=None, attrib=None, text=None):
                self.tag = tag
                self.nsmap = dict(nsmap or {})
                self.attrib = dict(attrib or {})
                self.text = text
                self.tail = None
                self._children = []

            def append(self, child):
                self._children.append(child)

            def __iter__(self):
                return iter(self._children)

            def iter(self):
                yield self
                for child in self._children:
                    yield from child.iter()

            def set(self, key, value):
                self.attrib[key] = value

            def clear(self):
                # ``apply_namespace_map`` empties the old root after moving its
                # children onto a rebuilt one.
                self.attrib.clear()
                self._children.clear()
                self.text = None
                self.tail = None

            def get(self, key, default=None):
                return self.attrib.get(key, default)

            def find(self, tag):
                for child in self._children:
                    if child.tag == tag:
                        return child
                return None

            def findall(self, tag):
                return [child for child in self._children if child.tag == tag]

            def __len__(self):
                return len(self._children)

            def __deepcopy__(self, memo):
                clone = FakeElement(
                    self.tag,
                    nsmap=self.nsmap,
                    attrib=self.attrib.copy(),
                    text=self.text,
                )
                clone.tail = self.tail
                memo[id(self)] = clone
                clone._children = [deepcopy(child, memo) for child in self._children]
                return clone


        def _format_tag(tag, nsmap):
            if tag.startswith("{"):
                uri, local = tag[1:].split("}", 1)
                for prefix, bound in (nsmap or {}).items():
                    if bound == uri:
                        if prefix in (None, ""):
                            return local
                        return f"{prefix}:{local}"
                return local
            return tag


        def cleanup_namespaces(element, nsmap=None, **kwargs):
            if "top_nsmap" in kwargs and kwargs["top_nsmap"] is not None:
                nsmap = kwargs["top_nsmap"]
            nsmap = dict(nsmap or {})
            element.nsmap = nsmap
            for child in element._children:
                cleanup_namespaces(child, nsmap)


        def tostring(element, encoding="unicode", *, pretty_print=True):
            _ = encoding  # Preserve compatibility with lxml signature.
            def serialize(node, include_namespaces):
                tag = _format_tag(node.tag, node.nsmap)
                attrs = []
                if include_namespaces:
                    for prefix, uri in (node.nsmap or {}).items():
                        if prefix in (None, ""):
                            attrs.append(f'xmlns="{uri}"')
                        else:
                            attrs.append(f'xmlns:{prefix}="{uri}"')
                for key, value in node.attrib.items():
                    attrs.append(f'{key}="{value}"')
                attr_text = (" " + " ".join(attrs)) if attrs else ""
                content = node.text or ""
                if node._children:
                    children = "".join(serialize(child, False) for child in node._children)
                    return f"<{tag}{attr_text}>{content}{children}</{tag}>"
                return f"<{tag}{attr_text}>{content}</{tag}>"

            return serialize(element, True)


        def create_element(tag, nsmap=None):
            return FakeElement(tag, nsmap=nsmap)


        class XMLParser:
            def __init__(self, **_):
                pass


        def parse(*_, **__):  # pragma: no cover - unused in this shim
            raise NotImplementedError("parse not implemented for fake lxml shim")


        def fromstring(*_, **__):  # pragma: no cover - unused in this shim
            raise NotImplementedError("fromstring not implemented for fake lxml shim")


        fake_etree = types.SimpleNamespace(
            Element=create_element,
            _Element=FakeElement,
            tostring=tostring,
            cleanup_namespaces=cleanup_namespaces,
            XMLParser=XMLParser,
            parse=parse,
            fromstring=fromstring,
        )

        fake_lxml = types.ModuleType("lxml")
        fake_lxml.etree = fake_etree
        sys.modules["lxml"] = fake_lxml
        sys.modules["lxml.etree"] = fake_etree

        import ddi_l._etree as ddi_etree
        importlib.reload(ddi_etree)
        import ddi_l.namespace_utils as ns_utils
        importlib.reload(ns_utils)
        import ddi_l._document_namespaces as doc_ns
        importlib.reload(doc_ns)
        import ddi_l.document as document_module
        importlib.reload(document_module)

        from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
        from ddi_l.document import DDIDocument
        from ddi_l.namespaces import DDI_PROFILE_PROFILE

        root = fake_etree.Element(
            f"{{{INSTANCE_NS}}}DDIInstance",
            nsmap={
                None: INSTANCE_NS,
                "r": REUSABLE_NS,
                "orig": "http://example.com/original",
            },
        )

        def make_child(tag, text):
            child = fake_etree.Element(tag, nsmap=root.nsmap)
            child.text = text
            return child


        root.append(make_child(f"{{{REUSABLE_NS}}}Agency", "demo.agency"))
        root.append(make_child(f"{{{REUSABLE_NS}}}ID", "demo-instance"))
        root.append(make_child(f"{{{REUSABLE_NS}}}Version", "1.0"))
        root.append(make_child("{http://example.com/original}Custom", "value"))

        document = DDIDocument(root)
        document.ensure_namespace_prefixes(
            DDI_PROFILE_PROFILE,
            extra_namespaces={"orig": "http://example.com/original", "new": "http://example.com/new"},
        )

        xml_output = document.to_xml(pretty_print=False)
        assert 'xmlns:orig="http://example.com/original"' in xml_output, xml_output
        assert 'xmlns:new="http://example.com/new"' in xml_output, xml_output
        assert "<orig:Custom>value</orig:Custom>" in xml_output, xml_output
        """
    )

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        python_paths.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    subprocess.run([sys.executable, "-c", script], check=True, env=env)


def test_ensure_namespace_prefixes_under_stdlib():
    """ensure_namespace_prefixes works without lxml by patching import."""
    repo_root = Path(__file__).resolve().parents[1]
    python_paths = [str(repo_root / "src"), str(repo_root)]
    script = textwrap.dedent(
        '''
        import sys
        import types

        fake_lxml = types.ModuleType("lxml")

        def _getattr(_):
            raise ModuleNotFoundError("No module named 'lxml'")

        fake_lxml.__getattr__ = _getattr
        sys.modules["lxml"] = fake_lxml

        from ddi_l.document import DDIDocument

        xml = """
        <DDIInstance xmlns=\"ddi:instance:3_3\" xmlns:r=\"ddi:reusable:3_3\" xmlns:orig=\"http://example.com/original\">
            <r:Agency>demo.agency</r:Agency>
            <r:ID>demo-instance</r:ID>
            <r:Version>1.0</r:Version>
            <orig:Custom>value</orig:Custom>
        </DDIInstance>
        """
        document = DDIDocument.from_xml(xml)
        from ddi_l.namespaces import DDI_PROFILE_PROFILE

        document.ensure_namespace_prefixes(
            DDI_PROFILE_PROFILE,
            extra_namespaces={"orig": "http://example.com/original", "new": "http://example.com/new"},
        )

        xml_output = document.to_xml(pretty_print=False)
        assert 'xmlns:orig="http://example.com/original"' in xml_output, xml_output
        assert 'xmlns:new="http://example.com/new"' in xml_output, xml_output
        assert "<orig:Custom>value</orig:Custom>" in xml_output, xml_output
        '''
    )

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        python_paths.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    subprocess.run([sys.executable, "-c", script], check=True, env=env)


def test_set_citation_title_none_preserves_existing():
    """Setting citation title to None preserves existing InternationalString."""
    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    document.set_citation(title="Initial Title", lang="en")
    document.set_citation(title=None)

    citation = document.root.find("{ddi:reusable:3_3}Citation")
    titles = list(citation.findall("{ddi:reusable:3_3}Title"))  # type: ignore[union-attr]
    assert len(titles) == 1
    assert titles[0].find("{ddi:reusable:3_3}String").text == "Initial Title"


def test_set_citation_multiple_updates_leave_single_title():
    """Repeated set_citation calls keep only the latest title entry."""
    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    document.set_citation(title="Title One", lang="en")
    document.set_citation(title="Title Two", lang="fr")
    document.set_citation(title="Title Three", lang="de")

    citation = document.root.find("{ddi:reusable:3_3}Citation")
    titles = list(citation.findall("{ddi:reusable:3_3}Title"))  # type: ignore[union-attr]
    assert len(titles) == 1
    title_string = titles[0].find("{ddi:reusable:3_3}String")
    assert title_string.text == "Title Three"
    assert title_string.get("{http://www.w3.org/XML/1998/namespace}lang") == "de"


def _instance(
    *, study_citation: str = "", doc_citation: str = "", abstract: str = ""
) -> str:
    """Build a minimal instance with the citation shapes under test."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<DDIInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3" xmlns:s="ddi:studyunit:3_3">
  <r:Agency>example.org</r:Agency>
  <r:ID>4d1e9d5a-0a3f-4b1e-9e6f-9d1c2b3a4e5f</r:ID>
  <r:Version>1</r:Version>
  {doc_citation}
  <s:StudyUnit>
    <r:Agency>example.org</r:Agency>
    <r:ID>7f2b8c14-5d6e-4f7a-8b9c-0d1e2f3a4b5c</r:ID>
    <r:Version>1</r:Version>
    {study_citation}
    {abstract}
  </s:StudyUnit>
</DDIInstance>
"""


_NESTED = (
    '<r:Citation><r:Title><r:String xml:lang="en">{}</r:String></r:Title></r:Citation>'
)
_ABSTRACT = '<r:Abstract><r:Content xml:lang="en">{}</r:Content></r:Abstract>'


@pytest.mark.parametrize(
    ("xml", "expected"),
    [
        pytest.param(
            _instance(
                doc_citation=_NESTED.format("Household Survey 2026"),
                abstract=_ABSTRACT.format("Annual survey of household composition."),
            ),
            "Household Survey 2026",
            id="nested-r-String-is-the-shape-set_citation-writes",
        ),
        pytest.param(
            _instance(
                study_citation=_NESTED.format("Study Level Title"),
                doc_citation=_NESTED.format("Doc Level Title"),
            ),
            "Study Level Title",
            id="the-study-s-own-citation-outranks-the-document-s",
        ),
        pytest.param(
            _instance(
                doc_citation="<r:Citation><r:Title>Flat Title</r:Title></r:Citation>"
            ),
            "Flat Title",
            id="text-directly-on-r-Title-as-some-producers-emit-it",
        ),
        pytest.param(
            _instance(abstract=_ABSTRACT.format("Only an abstract.")),
            "Only an abstract.",
            id="abstract-is-the-documented-last-resort",
        ),
        pytest.param(_instance(), None, id="nothing-to-report"),
    ],
)
def test_title_reads_the_citation_the_writer_produced(tmp_path, xml, expected):
    """`Document.title` must read the shape `set_citation` writes.

    `set_citation` nests the text in an `r:String` child; the title must be
    read from there, not from the abstract.
    """
    import ddi_l

    path = tmp_path / "study.xml"
    path.write_text(xml, encoding="utf-8")

    assert ddi_l.open_ddi(path).title == expected


def test_jsonld_titles_a_study_by_its_citation(tmp_path):
    """JSON-LD publishes the citation title as `dcterms:title`."""
    import ddi_l
    from ddi_l.jsonld import to_jsonld

    path = tmp_path / "study.xml"
    path.write_text(
        _instance(
            doc_citation=_NESTED.format("Household Survey 2026"),
            abstract=_ABSTRACT.format("Annual survey of household composition."),
        ),
        encoding="utf-8",
    )

    graph = to_jsonld(ddi_l.open_ddi(path))
    study = next(node for node in graph["@graph"] if node["@type"] == "disco:Study")

    assert study["dcterms:title"] == "Household Survey 2026"
    assert study["dcterms:abstract"] == [
        {"@value": "Annual survey of household composition.", "@language": "en"}
    ]


@pytest.mark.parametrize(
    "present_tags, expected",
    [
        (("ID", "Version"), {"agency": None, "id": "demo-id", "version": "2.0"}),
        (
            ("Agency", "Version"),
            {"agency": "demo.agency", "id": None, "version": "2.0"},
        ),
        (("Agency", "ID"), {"agency": "demo.agency", "id": "demo-id", "version": None}),
    ],
)
def test_get_identification_missing_elements_return_none(present_tags, expected):
    """Missing identification tags result in None values for absent fields.

    Args:
        present_tags: Combination of identification tag names to include.
        expected: Expected identification mapping returned by DDIDocument.
    """
    elements = []
    for tag in present_tags:
        if tag == "Agency":
            elements.append("<r:Agency>demo.agency</r:Agency>")
        elif tag == "ID":
            elements.append("<r:ID>demo-id</r:ID>")
        elif tag == "Version":
            elements.append("<r:Version>2.0</r:Version>")

    xml = """
    <DDIInstance xmlns=\"ddi:instance:3_3\" xmlns:r=\"ddi:reusable:3_3\">
        {content}
    </DDIInstance>
    """.format(content="\n        ".join(elements))

    document = DDIDocument.from_xml(textwrap.dedent(xml))
    assert document.get_identification() == expected


def test_iter_and_add_study_units_round_trip():
    """Study units added to document iterate back with nested data."""
    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    study = StudyUnit(
        agency="demo.agency",
        identifier="study-1",
        version="1.0",
        data_collections=[
            DataCollection(
                agency="demo.agency",
                identifier="collection-1",
                version="1.0",
                collection_events=[
                    CollectionEvent(
                        agency="demo.agency",
                        identifier="collection-1-event",
                        version="1.0",
                    )
                ],
            )
        ],
    )

    document.add_study_unit(study)

    studies = list(document.iter_study_units())
    assert len(studies) == 1
    loaded_study = studies[0]
    assert loaded_study.identifier == "study-1"
    expected_collection_id = str(
        uuid5(_REFERENCE_NAMESPACE, "demo.agency:collection-1")
    )
    assert loaded_study.data_collections[0].identifier == expected_collection_id

    serialized = document.to_xml(pretty_print=False)
    assert "study-1" in serialized


def test_iter_maintainables_returns_requested_type():
    """Generic maintainable iteration yields the requested class instances."""

    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    concept = Concept(
        agency="demo.agency",
        identifier="concept-1",
        version="1.0",
        names=[InternationalString(text="Concept One")],
    )
    document.add_maintainable(concept)

    loaded = list(document.iter_maintainables(Concept))
    assert len(loaded) == 1
    assert loaded[0].identifier == "concept-1"
    assert loaded[0].names[0].text == "Concept One"


def test_replace_maintainable_swaps_matching_element():
    """Existing maintainables are replaced when identifiers match."""

    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    original = Concept(
        agency="demo.agency",
        identifier="concept-1",
        version="1.0",
        names=[InternationalString(text="Original")],
    )
    document.add_maintainable(original)

    updated = Concept(
        agency="demo.agency",
        identifier="concept-1",
        version="1.0",
        names=[InternationalString(text="Updated")],
    )
    document.replace_maintainable(updated)

    loaded = list(document.iter_maintainables(Concept))
    assert len(loaded) == 1
    assert loaded[0].names[0].text == "Updated"


def test_remove_maintainable_supports_reference_inputs():
    """References can remove maintainables without direct XML manipulation."""

    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    concept = Concept(
        agency="demo.agency",
        identifier="concept-1",
        version="1.0",
        names=[InternationalString(text="Removable")],
    )
    document.add_maintainable(concept)

    removed = document.remove_maintainable(
        Reference(
            agency="demo.agency",
            identifier="concept-1",
            version="1.0",
            type_of_object="Concept",
        )
    )

    assert removed is True
    assert not list(document.iter_maintainables(Concept))


def test_remove_maintainable_missing_returns_false():
    """Removing a non-existent maintainable returns False without error."""

    document = DDIDocument.create(
        agency="demo.agency",
        identifier="demo-instance",
        version="1.0",
    )

    removed = document.remove_maintainable(
        Reference(agency="demo.agency", identifier="unknown", version="1.0")
    )

    assert removed is False


def _build_document_with_variables() -> tuple[
    DDIDocument, QuestionItem, Variable, Variable
]:
    question = QuestionItem(
        urn="urn:ddi:agency.test:q1:1.0",
        agency="agency.test",
        identifier="q1",
        version="1.0",
        question_texts=[
            InternationalString(text="How old are you?", child_tag="Content")
        ],
    )

    question_reference = Reference(
        type_of_object="QuestionItem",
        urn=question.urn,
        agency=question.agency,
        identifier=question.identifier,
        version=question.version,
    )

    variable_v1 = Variable(
        urn="urn:ddi:agency.test:var-age:1.0",
        agency="agency.test",
        identifier="var-age",
        version="1.0",
        question_references=[question_reference],
    )
    variable_v2 = Variable(
        urn="urn:ddi:agency.test:var-age:2.0",
        agency="agency.test",
        identifier="var-age",
        version="2.0",
        question_references=[question_reference],
    )

    collection = DataCollection(
        urn="urn:ddi:agency.test:collection-1:1.0",
        agency="agency.test",
        identifier="collection-1",
        version="1.0",
        questions=[question],
    )

    logical_product = LogicalProduct(
        urn="urn:ddi:agency.test:logical-product-1:1.0",
        agency="agency.test",
        identifier="logical-product-1",
        version="1.0",
        variables=[variable_v1, variable_v2],
    )

    study_unit = StudyUnit(
        urn="urn:ddi:agency.test:study-1:1.0",
        agency="agency.test",
        identifier="study-1",
        version="1.0",
        data_collections=[collection],
        logical_products=[logical_product],
    )

    document = DDIDocument.create(
        agency="agency.test",
        identifier="doc",
        version="1.0",
        build_index=False,
    )
    document.add_study_unit(study_unit)
    return document, question, variable_v1, variable_v2


def test_document_resolver_handles_urn_and_identifier() -> None:
    """DDIDocument.resolve uses the cached resolver for URN and identifier lookups."""

    document, question, variable_v1, _ = _build_document_with_variables()

    resolver = document.resolver
    assert document.resolver is resolver

    resolved_question = document.resolve(question.urn, type=QuestionItem)  # type: ignore[arg-type]
    assert resolved_question.identifier == question.identifier

    identifier_key = (variable_v1.agency, variable_v1.identifier, variable_v1.version)
    resolved_variable = document.resolve(identifier_key, type=Variable)  # type: ignore[arg-type]
    assert resolved_variable.version == variable_v1.version


def test_document_resolver_raises_on_identifier_ambiguity() -> None:
    """DDIDocument.resolve surfaces ambiguity errors reported by the index."""

    document, _, variable_v1, variable_v2 = _build_document_with_variables()

    ambiguous_key = (variable_v1.agency, variable_v1.identifier, None)
    with pytest.raises(LookupError):
        document.resolve(ambiguous_key, type=Variable)  # type: ignore[arg-type]

    versioned_key = (variable_v2.agency, variable_v2.identifier, variable_v2.version)
    resolved = document.resolve(versioned_key, type=Variable)  # type: ignore[arg-type]
    assert resolved.version == variable_v2.version
