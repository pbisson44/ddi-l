"""Render a DDI Lifecycle document as JSON-LD, using DDI-RDF Discovery (Disco).

Why Disco, and what that costs
------------------------------

There is no official JSON-LD serialization of DDI Lifecycle 3.3. The nearest
standard is the DDI Alliance's own **DDI-RDF Discovery Vocabulary** ("Disco",
``http://rdf-vocabulary.ddialliance.org/discovery#``), an RDF vocabulary
covering a subset of DDI-Codebook and DDI-Lifecycle for *discovery*: studies,
their variables, the questions those variables came from, universes and
instruments. It reuses Dublin Core, SKOS, XKOS and the RDF Data Cube vocabulary
rather than reinventing them.

Two consequences follow:

* **This is lossy, by design.** Disco describes what a dataset is *about* so it
  can be found and compared. It has no vocabulary for questionnaire flow logic,
  physical record layouts, NCubes, processing instructions or the rest of what
  DDI-L models. Those are dropped rather than approximated.
* **It does not round-trip.** The Disco specification is explicit that
  transforming DDI XML to RDF is supported and the reverse "is not intended".
  ``ddi_l.operations.to_json_payload`` remains the lossless, round-trippable
  representation; this one is for publishing to the Web of Linked Data.

Every term emitted here respects the published vocabulary, including its
``rdfs:domain``: ``disco:concept`` has domain
``RepresentedVariable | Question | Variable``, not ``Study``, so concepts are
emitted as standalone ``skos:Concept`` nodes.

Shape
-----

Output is a flat ``@graph``: every item is a node with its own ``@id`` and
``@type``, and links between them are ``{"@id": ...}`` references. A flat graph
is the normal result of an XML-to-RDF transform, it never forces a link that the
vocabulary does not license, and each node stays independently addressable.

``@id`` values are DDI URNs (``urn:ddi:<agency>:<identifier>:<version>``), which
the library already mints and which are valid IRIs.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from .document import Document
    from .models.base import InternationalString, MaintainableBase, Reference

__all__ = ["DISCO_CONTEXT", "to_jsonld"]

DISCO = "http://rdf-vocabulary.ddialliance.org/discovery#"

#: The ``@context`` emitted with every document. Prefixes match those used by
#: the Disco specification itself, so a reader familiar with Disco sees the
#: names they expect.
DISCO_CONTEXT: dict[str, str] = {
    "disco": DISCO,
    "dcterms": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xkos": "http://purl.org/linked-data/xkos#",
    "qb": "http://purl.org/linked-data/cube#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "adms": "http://www.w3.org/ns/adms#",
}


def _urn(item: MaintainableBase) -> str | None:
    """Return the DDI URN for ``item``, which doubles as its IRI."""
    urn = item._format_urn()
    if urn:
        return str(urn)
    if item.identifier:
        return f"urn:ddi:{item.agency}:{item.identifier}:{item.version}"
    return None


def _reference_urn(reference: Reference) -> str | None:
    """Return the URN a reference points at."""
    return reference.urn or reference._canonical_urn() or None


def _lang_values(strings: list[InternationalString]) -> list[dict[str, str]] | None:
    """Render ``InternationalString`` values as JSON-LD language-tagged literals.

    DDI carries language on every human-readable string, and Disco's text
    properties range over ``rdf:langString``, so the language belongs in the
    output rather than being flattened away. A string with no language becomes a
    plain literal instead of one tagged with a language nobody asserted.
    """
    values: list[dict[str, str]] = []
    for string in strings or []:
        text = getattr(string, "text", None)
        if not text:
            continue
        value: dict[str, str] = {"@value": text}
        lang = getattr(string, "lang", None)
        if lang:
            value["@language"] = lang
        values.append(value)
    return values or None


def _node(item: MaintainableBase, rdf_type: str) -> dict[str, Any] | None:
    """Start a graph node for ``item``, or ``None`` if it has no identity."""
    identifier = _urn(item)
    if identifier is None:
        return None
    return {"@id": identifier, "@type": rdf_type}


def _set(node: dict[str, Any], key: str, value: Any) -> None:
    """Assign ``key`` only when there is something to say."""
    if value:
        node[key] = value


def to_jsonld(document: Document, *, include_context: bool = True) -> dict[str, Any]:
    """Render ``document`` as a JSON-LD graph using Disco.

    Args:
        document: A :class:`~ddi_l.document.Document`, as returned by
            :func:`~ddi_l.document.new_study` or
            :func:`~ddi_l.document.open_ddi`.
        include_context: Emit the ``@context``. Set ``False`` when embedding the
            graph in a larger document that supplies its own.

    Returns:
        A JSON-serialisable mapping with ``@context`` and ``@graph``.
    """
    graph: list[dict[str, Any]] = []

    study = document.study_unit
    study_node = _node(study, "disco:Study")
    if study_node is not None:
        # The title lives in the study's raw `r:Citation`, read via `Document.title`.
        if document.title:
            study_node["dcterms:title"] = document.title
        _set(
            study_node,
            "dcterms:abstract",
            _lang_values(getattr(study, "abstracts", [])),
        )
        # The agency is the organisation maintaining the metadata. `publisher`
        # is the closest Dublin Core term that DDI's `r:Agency` actually
        # supports -- it is an identifier for the maintainer, not a named
        # `foaf:Organization` we could honestly construct.
        _set(study_node, "dcterms:publisher", document.agency)
        graph.append(study_node)

    def _link(key: str, items: Sequence[MaintainableBase]) -> None:
        """Add ``{"@id": ...}`` links from the study to ``items``."""
        if study_node is None:
            return
        refs = [{"@id": urn} for urn in map(_urn, items) if urn]
        _set(study_node, key, refs)

    questions = document.questions
    variables = document.variables
    universes = document.universes
    concepts = document.concepts
    code_lists = document.code_lists

    # Domains checked against the vocabulary: disco:variable, disco:universe and
    # disco:instrument all admit disco:Study. disco:question does not -- it is
    # Variable|Questionnaire -- so questions are linked from their variable.
    _link("disco:variable", variables)
    _link("disco:universe", universes)

    for question in questions:
        node = _node(question, "disco:Question")
        if node is None:
            continue
        _set(
            node,
            "disco:questionText",
            _lang_values(getattr(question, "question_texts", [])),
        )
        graph.append(node)

    for variable in variables:
        node = _node(variable, "disco:Variable")
        if node is None:
            continue
        _set(node, "skos:prefLabel", _lang_values(getattr(variable, "names", [])))
        question_links = [
            {"@id": urn}
            for urn in (
                _reference_urn(reference)
                for reference in getattr(variable, "question_references", [])
            )
            if urn
        ]
        _set(node, "disco:question", question_links)
        concept_links = [
            {"@id": urn}
            for urn in (
                _reference_urn(reference)
                for reference in getattr(variable, "concept_references", [])
            )
            if urn
        ]
        _set(node, "disco:concept", concept_links)
        graph.append(node)

    for universe in universes:
        node = _node(universe, "disco:Universe")
        if node is None:
            continue
        _set(node, "skos:prefLabel", _lang_values(getattr(universe, "names", [])))
        graph.append(node)

    # Standalone nodes. `disco:concept` is domain Variable|Question|
    # RepresentedVariable, so a concept the high-level API created without a
    # variable to hang it on is emitted on its own rather than attached to the
    # study, which the vocabulary does not license.
    for concept in concepts:
        node = _node(concept, "skos:Concept")
        if node is None:
            continue
        _set(node, "skos:prefLabel", _lang_values(getattr(concept, "names", [])))
        graph.append(node)

    # Disco types a code list's target as skos:ConceptScheme (the range of
    # disco:representation); XKOS is the vocabulary for the classification
    # semantics on top of it.
    for code_list in code_lists:
        node = _node(code_list, "skos:ConceptScheme")
        if node is None:
            continue
        _set(node, "dcterms:title", _lang_values(getattr(code_list, "names", [])))
        graph.append(node)

    payload: dict[str, Any] = {}
    if include_context:
        payload["@context"] = dict(DISCO_CONTEXT)
    payload["@graph"] = graph
    return payload
