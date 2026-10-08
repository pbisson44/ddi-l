"""The JSON-LD rendering, checked as RDF rather than as JSON that looks like it.

Most of these parse the output with ``rdflib`` and assert on the resulting
triples. That distinction matters: a dict with an ``@context`` key is trivially
easy to produce and can still expand to nothing, or to the wrong predicates. If
a term is misspelled or a link points at an IRI no node uses, the graph says so
and a shape assertion would not.
"""

from __future__ import annotations

import json

import pytest

import ddi_l as ddi
from ddi_l import operations
from ddi_l.jsonld import DISCO_CONTEXT, to_jsonld

rdflib = pytest.importorskip("rdflib", reason="requires the dev group")

from rdflib import Graph, Literal, Namespace, URIRef

DISCO = Namespace("http://rdf-vocabulary.ddialliance.org/discovery#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
RDF_TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")


@pytest.fixture
def document():
    """A study exercising every mapped type."""
    from ddi_l.models.datacollection import Instrument

    doc = ddi.new_study(title="Household Survey", agency="example.org")
    question = doc.add_question(text="How old are you?")
    doc.add_variable(name="Age", question=question)
    doc.add_concept(name="Demographics")
    doc.add_universe(name="Canadian adults aged 18+")
    doc.add_code_list(name="Sex")
    doc.add_item(Instrument, name="CAWI Questionnaire")
    return doc


@pytest.fixture
def graph(document) -> Graph:
    """The document parsed as RDF."""
    parsed = Graph()
    parsed.parse(data=json.dumps(to_jsonld(document)), format="json-ld")
    return parsed


def _one(graph: Graph, rdf_type) -> URIRef:
    subjects = list(graph.subjects(RDF_TYPE, rdf_type))
    assert len(subjects) == 1, f"expected one {rdf_type}, found {subjects}"
    subject = subjects[0]
    assert isinstance(subject, URIRef)
    return subject


def test_the_output_is_parseable_rdf(graph):
    assert len(graph) > 0, "JSON-LD expanded to no triples at all"


@pytest.mark.parametrize(
    "rdf_type",
    [DISCO.Study, DISCO.Variable, DISCO.Question, DISCO.Universe, SKOS.Concept],
)
def test_each_mapped_type_appears(graph, rdf_type):
    assert list(graph.subjects(RDF_TYPE, rdf_type)), f"no {rdf_type} node"


def test_the_study_carries_dublin_core_metadata(graph):
    study = _one(graph, DISCO.Study)

    assert (study, DCTERMS.title, Literal("Household Survey")) in graph
    assert (study, DCTERMS.publisher, Literal("example.org")) in graph


def test_the_study_links_to_its_variables(graph):
    study = _one(graph, DISCO.Study)
    variable = _one(graph, DISCO.Variable)

    assert (study, DISCO.variable, variable) in graph


def test_the_variable_links_to_its_question(graph):
    """`disco:question` has domain Variable, not Study -- so it hangs here."""
    variable = _one(graph, DISCO.Variable)
    question = _one(graph, DISCO.Question)

    assert (variable, DISCO.question, question) in graph


def test_the_study_does_not_claim_domain_violating_links(graph):
    """`disco:question` and `disco:concept` do not admit a Study as subject.

    Emitting them there would produce output that reads fine as JSON and is
    wrong as RDF -- the kind of error only a graph assertion catches.
    """
    study = _one(graph, DISCO.Study)

    assert (study, DISCO.question, None) not in graph
    assert (study, DISCO.concept, None) not in graph


def test_question_text_keeps_its_language_tag(graph):
    question = _one(graph, DISCO.Question)

    texts = list(graph.objects(question, DISCO.questionText))
    assert texts == [Literal("How old are you?", lang="en")]


def test_every_link_target_resolves_to_a_node_in_the_graph(graph):
    """A dangling `{"@id": ...}` is a link to nothing, and silent in JSON."""
    subjects = set(graph.subjects())
    for predicate in (DISCO.variable, DISCO.universe, DISCO.question):
        for target in graph.objects(None, predicate):
            assert target in subjects, f"{predicate} points at unknown {target}"


def test_identifiers_are_ddi_urns(graph):
    for subject in graph.subjects():
        assert str(subject).startswith("urn:ddi:"), f"unexpected @id: {subject}"


def test_the_context_declares_every_prefix_used(document):
    """A prefix used but not declared expands to a relative IRI, or is dropped."""
    payload = to_jsonld(document)
    declared = set(payload["@context"])

    used = {
        key.split(":", 1)[0]
        for node in payload["@graph"]
        for key in node
        if ":" in key and not key.startswith("@")
    }

    assert used <= declared, f"undeclared prefixes: {sorted(used - declared)}"


def test_the_context_can_be_omitted_for_embedding(document):
    payload = to_jsonld(document, include_context=False)

    assert "@context" not in payload
    assert payload["@graph"]


def test_the_declared_context_matches_the_disco_namespace():
    assert DISCO_CONTEXT["disco"] == str(DISCO)


def test_operations_renders_jsonld_from_bytes(document, tmp_path):
    path = tmp_path / "study.xml"
    document.save(path)

    payload = operations.to_jsonld_payload(path.read_bytes())

    assert payload["@context"]["disco"] == str(DISCO)
    assert payload["@graph"]


def test_a_fragment_is_refused_with_a_reason(tmp_path):
    """A FragmentInstance has no study, and Disco is a study-centred vocabulary."""
    from tests import PACKAGE_FIXTURES_DIR

    fragment = (PACKAGE_FIXTURES_DIR / "minimal_fragment.xml").read_bytes()

    with pytest.raises(ValueError, match="FragmentInstance"):
        operations.to_jsonld_payload(fragment)


def test_a_profiled_fragment_returns_a_profile_result():
    """The return type follows the request, not the kind of document.

    A profiled `DDIInstance` or `FragmentInstance` both return a
    `ProfileResult`, including its schema issues.
    """
    from ddi_l.lint import ProfileResult
    from tests import PACKAGE_FIXTURES_DIR

    fragment = (PACKAGE_FIXTURES_DIR / "minimal_fragment.xml").read_bytes()

    profiled = operations.lint_source(fragment, profile="DDI_PROFILE_DEFAULT")
    assert isinstance(profiled, ProfileResult)
    assert sorted(profiled.as_dict()) == ["lint_findings", "schema_issues"]

    # Without a profile the plain list is still what comes back.
    assert isinstance(operations.lint_source(fragment), list)
