# mypy: ignore-errors
from __future__ import annotations

import io
import itertools
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from unittest import mock
from uuid import uuid5

import pytest

import ddi_l.io as io_module
import ddi_l.schema_loader as schema_loader
from ddi_l import (
    DDIDocument,
    DDIFragment,
    DDIReadError,
    DDIWriteError,
    iter_questions,
    iter_variables,
    iterparse_ddi,
    read_ddi,
    write_ddi,
)
from ddi_l._etree import parse_xml
from ddi_l.constants import INSTANCE_NS
from ddi_l.models import (
    Category,
    CollectionEvent,
    ConceptualVariable,
    DataCaptureDevelopment,
    DataCollection,
    GeneralInstruction,
    GenerationInstruction,
    InformationClassification,
    InternationalString,
    LogicalProduct,
    MaintainableBase,
    ProcessingEvent,
    ProcessingEventScheme,
    ProcessingInstructionGroup,
    ProcessingInstructionScheme,
    QualityScheme,
    QualityStandard,
    QualityStandardGroup,
    QualityStatement,
    QualityStatementGroup,
    QuestionItem,
    QuestionScheme,
    Reference,
    RepresentedVariable,
    SamplingInformationGroup,
    SamplingInformationScheme,
    SamplingPlan,
    StudyUnit,
    Variable,
    clone_element,
    qn,
)
from ddi_l.models.datacollection import _REFERENCE_NAMESPACE
from tests import PACKAGE_FIXTURES_DIR
from tests.helpers.synthetic_maintainable import synthetic_maintainable

FIXTURE_PATH = PACKAGE_FIXTURES_DIR / "minimal_instance.xml"
FRAGMENT_FIXTURE_PATH = PACKAGE_FIXTURES_DIR / "minimal_fragment.xml"
MODEL_FIXTURE_DIR = PACKAGE_FIXTURES_DIR / "models"


READ_PAYLOADS = [
    pytest.param("path", lambda: FIXTURE_PATH, id="path"),
    pytest.param("bytes", lambda: FIXTURE_PATH.read_bytes(), id="bytes"),
    pytest.param("buffer", lambda: io.BytesIO(FIXTURE_PATH.read_bytes()), id="buffer"),
    pytest.param(
        "file_handle",
        lambda: FIXTURE_PATH.open("rb"),
        id="file-handle",
    ),
]


def _build_mixed_payload(pairs: int = 3) -> bytes:
    """Create XML bytes interleaving variables and questions for streaming tests.

    Args:
        pairs: Number of variable/question pairs to embed in the document.
    """
    document = DDIDocument.create(
        agency="example.agency",
        identifier="streamed",
        version="1.0",
        title="Streamed instance",
    )
    for index in range(pairs):
        variable = Variable(
            agency="example.agency",
            identifier=f"var-{index}",
            version="1.0",
            names=[InternationalString(text=f"Variable {index}")],
        )
        question = QuestionItem(
            agency="example.agency",
            identifier=f"question-{index}",
            version="1.0",
            question_texts=[InternationalString(text=f"Question {index}")],
        )
        document.root.append(variable.to_xml())
        document.root.append(question.to_xml())

    buffer = io.BytesIO()
    write_ddi(document, buffer)
    return buffer.getvalue()


def _build_document_for_iter_helpers() -> DDIDocument:
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
    return document


def test_short_aliases_match_existing_helpers() -> None:
    """Short helper names delegate to the established entry points."""

    assert io_module.read is io_module.read_ddi
    assert io_module.write is io_module.write_ddi
    assert io_module.validate is schema_loader.validate


def test_read_helpers_raise_for_missing_string_path(tmp_path: Path) -> None:
    """String paths must exist on disk when resolving XML sources."""

    missing = tmp_path / "missing.xml"

    with pytest.raises(FileNotFoundError):
        read_ddi(str(missing))

    with pytest.raises(FileNotFoundError):
        read_ddi(str(missing))


@pytest.mark.parametrize(("payload_id", "payload_factory"), READ_PAYLOADS)
def test_read_accepts_various_payloads(
    payload_id: str, payload_factory: Callable[[], object]
) -> None:
    """read handles diverse payload types while preserving shared guarantees."""

    payload = payload_factory()
    try:
        document = read_ddi(payload)
        assert isinstance(document, DDIDocument)
        metadata = document.get_identification()
        assert metadata["agency"] == "example.agency"

        if payload_id == "file_handle":
            assert not payload.closed
    finally:
        if payload_id == "file_handle" and not payload.closed:
            payload.close()


def test_write_to_path(tmp_path: Path):
    """write writes documents to disk paths and preserves identity.

    Args:
        tmp_path: Temporary directory path for writing a document copy.
    """
    document = read_ddi(FIXTURE_PATH)
    destination = tmp_path / "copy.xml"
    write_ddi(document, destination)
    assert destination.exists()
    copy = read_ddi(destination)
    expected_identifier = str(
        uuid5(_REFERENCE_NAMESPACE, "example.agency:minimal-instance")
    )
    assert copy.get_identification()["id"] == expected_identifier


def test_write_to_buffer():
    """write writes to file-like buffers enabling in-memory round-trips."""
    document = read_ddi(FIXTURE_PATH)
    buffer = io.BytesIO()
    write_ddi(document, buffer)
    buffer.seek(0)
    copy = read_ddi(buffer)
    assert copy.get_identification()["version"] == "1.0"


def test_read_and_write_fragment_documents(tmp_path: Path):
    """DDIFragment can be read and written via read/write helpers.

    Args:
        tmp_path: Temporary directory path for writing a fragment copy.
    """
    document = read_ddi(FRAGMENT_FIXTURE_PATH, validate=True)
    assert isinstance(document, DDIFragment)

    destination = tmp_path / "fragment.xml"
    write_ddi(document, destination)

    reparsed = read_ddi(destination, validate=True)
    assert isinstance(reparsed, DDIFragment)


def test_iterparse_ddi_streams_maintainables(tmp_path: Path):
    """iterparse_ddi yields maintainables from streamed documents.

    Args:
        tmp_path: Temporary directory path for writing a streamed document.
    """
    document = DDIDocument.create(
        agency="example.agency",
        identifier="streamed",
        version="1.0",
        title="Streamed instance",
    )
    study = StudyUnit(
        agency="example.agency",
        identifier="study-1",
        version="1.0",
        data_collection_references=[
            Reference(
                agency="example.agency",
                identifier="collection",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    document.add_study_unit(study)

    buffer = io.BytesIO()
    write_ddi(document, buffer)
    buffer.seek(0)

    maintainables = list(iterparse_ddi(buffer))
    assert maintainables
    assert isinstance(maintainables[0], StudyUnit)


def test_iterparse_ddi_discovers_processing_events():
    """iterparse_ddi discovers ProcessingEvent maintainables in streams."""
    document = DDIDocument.create(
        agency="example.agency",
        identifier="processing-stream",
        version="1.0",
        title="Processing stream",
    )
    scheme_element = parse_xml(
        MODEL_FIXTURE_DIR / "processing_event_scheme_with_groups.xml"
    )
    document.root.append(clone_element(scheme_element))

    buffer = io.BytesIO()
    write_ddi(document, buffer)
    buffer.seek(0)

    maintainables = list(iterparse_ddi(buffer))
    assert any(isinstance(item, ProcessingEventScheme) for item in maintainables)
    assert any(isinstance(item, ProcessingEvent) for item in maintainables)


@pytest.mark.parametrize(
    ("fixture_name", "expected_type"),
    [
        ("category_representative", Category),
        ("conceptual_variable_minimal", ConceptualVariable),
        ("information_classification_minimal", InformationClassification),
        ("represented_variable_with_code", RepresentedVariable),
        ("general_instruction_minimal", GeneralInstruction),
        ("generation_instruction_minimal", GenerationInstruction),
        ("processing_instruction_group_minimal", ProcessingInstructionGroup),
        ("processing_instruction_scheme_minimal", ProcessingInstructionScheme),
        ("quality_scheme_minimal", QualityScheme),
        ("quality_standard_minimal", QualityStandard),
        ("quality_standard_group_minimal", QualityStandardGroup),
        ("quality_statement_minimal", QualityStatement),
        ("quality_statement_group_minimal", QualityStatementGroup),
    ],
)
def test_iterparse_ddi_discovers_new_default_maintainables(
    fixture_name: str, expected_type: type[MaintainableBase]
) -> None:
    """iterparse_ddi yields newer maintainable types included by default.

    Args:
        fixture_name: Fixture XML filename representing the maintainable.
        expected_type: Maintainable class expected from streaming parser.
    """
    document = DDIDocument.create(
        agency="example.agency",
        identifier="export-check",
        version="1.0",
        title="Export check",
    )
    element = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.xml")
    document.root.append(clone_element(element))

    buffer = io.BytesIO()
    write_ddi(document, buffer)
    buffer.seek(0)

    maintainables = list(iterparse_ddi(buffer))
    assert any(isinstance(item, expected_type) for item in maintainables)


@pytest.mark.parametrize(
    "maintainable_cls",
    [
        CollectionEvent,
        DataCaptureDevelopment,
        QuestionScheme,
        SamplingInformationGroup,
        SamplingInformationScheme,
        SamplingPlan,
    ],
    ids=lambda cls: cls.__name__,
)
def test_iterparse_ddi_discovers_programmatic_defaults(
    maintainable_cls: type[MaintainableBase],
) -> None:
    """iterparse_ddi yields maintainables created programmatically by default."""

    document = DDIDocument.create(
        agency="example.agency",
        identifier="programmatic",
        version="1.0",
        title="Programmatic maintainables",
    )
    maintainable = maintainable_cls(
        agency="example.agency",
        identifier=f"{maintainable_cls.__name__.lower()}-1",
        version="1.0",
    )
    document.root.append(maintainable.to_xml())

    buffer = io.BytesIO()
    write_ddi(document, buffer)
    buffer.seek(0)

    maintainables = list(iterparse_ddi(buffer))
    assert any(isinstance(item, maintainable_cls) for item in maintainables)


def test_default_maintainables_include_new_types() -> None:
    """Default maintainables set includes newly supported types."""
    expected = {
        Category,
        ConceptualVariable,
        InformationClassification,
        ProcessingEvent,
        ProcessingInstructionScheme,
        QualityScheme,
        RepresentedVariable,
        SamplingPlan,
    }

    assert expected.issubset(set(MaintainableBase.maintainable_types()))


def test_default_maintainables_cover_index_registry() -> None:
    """Default maintainables mirror the maintainables indexed for discovery."""

    from ddi_l.index import Index

    available = set(MaintainableBase.maintainable_types())
    assert set(Index.maintainable_classes()).issubset(available)


def test_iterparse_ddi_detects_newly_registered_maintainables() -> None:
    """iterparse_ddi recognizes maintainables registered after module import."""

    with synthetic_maintainable() as SyntheticMaintainable:
        document = DDIDocument.create(
            agency="synthetic.agency",
            identifier="synthetic-doc",
            version="1.0",
            build_index=False,
        )
        maintainable = SyntheticMaintainable(
            agency="synthetic.agency",
            identifier="synthetic-1",
            version="1.0",
            value="payload",
        )
        document.root.append(maintainable.to_xml())

        buffer = io.BytesIO()
        write_ddi(document, buffer)
        payload = buffer.getvalue()

        parsed = list(iterparse_ddi(payload))

        assert any(isinstance(item, SyntheticMaintainable) for item in parsed)


def test_iterparse_ddi_prunes_processed_nodes():
    """Streaming parser prunes processed nodes to bound memory usage."""
    document = DDIDocument.create(
        agency="example.agency",
        identifier="streamed",
        version="1.0",
        title="Streamed instance",
    )
    for index in range(25):
        study = StudyUnit(
            agency="example.agency",
            identifier=f"study-{index}",
            version="1.0",
            data_collection_references=[
                Reference(
                    agency="example.agency",
                    identifier=f"collection-{index}",
                    version="1.0",
                    type_of_object="DataCollection",
                )
            ],
        )
        document.add_study_unit(study)

    buffer = io.BytesIO()
    write_ddi(document, buffer)
    buffer.seek(0)

    captured: dict[str, object] = {}
    lengths: list[int] = []
    original_iterparse = io_module.etree.iterparse

    def tracking_iterparse(*args, **kwargs):
        """Wrap iterparse to capture root length during streaming tests."""
        context = original_iterparse(*args, **kwargs)

        def generator():
            """Yield events while recording the root element for assertions."""
            for event, element in context:
                if captured.get("root") is None and event == "start":
                    captured["root"] = element
                yield event, element

        return generator()

    with mock.patch("ddi_l.io.etree.iterparse", new=tracking_iterparse):
        for maintainable in iterparse_ddi(buffer):
            assert isinstance(maintainable, StudyUnit)
            root = captured.get("root")
            assert root is not None
            lengths.append(len(root))

    root = captured.get("root")
    assert root is not None
    assert lengths
    assert all(later <= earlier for earlier, later in itertools.pairwise(lengths))
    assert lengths[0] > lengths[-1]
    assert len(root) == 0


def test_iterparse_ddi_forwards_iterparse_kwargs():
    """iterparse_ddi forwards custom keyword arguments to etree.iterparse."""

    payload = b"<DDIInstance xmlns='ddi:instance:3_3'></DDIInstance>"
    received_kwargs: dict[str, object] = {}

    def fake_iterparse(handle, *, events=("start", "end"), **kwargs):  # type: ignore[no-untyped-def]
        nonlocal received_kwargs
        received_kwargs = kwargs
        # ``io_module.etree.Element`` constructs a valid backend-specific element
        # (``lxml.etree.Element`` when lxml is installed, otherwise the stdlib
        # ``xml.etree`` fallback). Using the module helper rather than the
        # ``Element`` alias imported from ``ddi_l._etree`` avoids creating an
        # invalid proxy object when lxml is active, which mirrors the objects
        # produced by :func:`etree.iterparse` in production.
        root = io_module.etree.Element("DDIInstance")

        def iterator():
            yield "start", root
            yield "end", root

        return iterator()

    with mock.patch("ddi_l.io.etree.iterparse", new=fake_iterparse):
        list(
            iterparse_ddi(
                io.BytesIO(payload),
                maintainable_types=(Variable,),
                recover=True,
            )
        )

    assert received_kwargs["recover"] is True
    if io_module.USING_LXML:
        # Streaming uses the same hardening as the regular lxml parser.
        assert received_kwargs["resolve_entities"] is False
        assert received_kwargs["no_network"] is True
        assert received_kwargs["load_dtd"] is False


def test_iterparse_ddi_accepts_late_registered_maintainables() -> None:
    """Maintainables registered after import are discovered by iterparse."""

    @dataclass
    class LateMaintainable(MaintainableBase):
        TAG: ClassVar[str] = qn(INSTANCE_NS, "LateMaintainable")

    maintainable = LateMaintainable(
        agency="example.agency",
        identifier="late",
        version="1.0",
    )

    root = io_module.etree.Element(qn(INSTANCE_NS, "DDIInstance"))
    root.append(maintainable.to_xml())
    payload = io_module.tostring(root)
    if isinstance(payload, str):
        payload = payload.encode("utf-8")

    parsed = list(iterparse_ddi(io.BytesIO(payload)))

    assert any(isinstance(item, LateMaintainable) for item in parsed)


def test_iter_variables_filters_requested_maintainables():
    """iter_variables yields only Variable maintainables from mixed payloads."""
    payload = _build_mixed_payload(pairs=4)
    variables = list(iter_variables(io.BytesIO(payload)))
    assert variables
    assert all(isinstance(variable, Variable) for variable in variables)
    assert {variable.identifier for variable in variables} == {
        f"var-{index}" for index in range(4)
    }


def test_iter_questions_filters_requested_maintainables():
    """iter_questions yields only QuestionItem maintainables from streams."""
    payload = _build_mixed_payload(pairs=2)
    questions = list(iter_questions(io.BytesIO(payload)))
    assert questions
    assert all(isinstance(question, QuestionItem) for question in questions)
    assert {question.identifier for question in questions} == {
        "question-0",
        "question-1",
    }


def test_iter_helpers_use_document_resolver() -> None:
    """iter_variables and iter_questions reuse a document's cached resolver."""

    document = _build_document_for_iter_helpers()

    variables = list(iter_variables(document))
    assert {variable.version for variable in variables} == {"1.0", "2.0"}

    questions = list(iter_questions(document))
    assert [question.identifier for question in questions] == ["q1"]


def test_iter_variables_streaming_prunes_mixed_content():
    """iter_variables stream pruning shrinks root children as items emit."""
    payload = _build_mixed_payload(pairs=6)
    buffer = io.BytesIO(payload)
    captured: dict[str, object] = {}
    lengths: list[int] = []
    original_iterparse = io_module.etree.iterparse

    def tracking_iterparse(*args, **kwargs):
        """Wrap iterparse to monitor root size while streaming variables."""
        context = original_iterparse(*args, **kwargs)

        def generator():
            """Yield events while capturing root for pruning assertions."""
            for event, element in context:
                if captured.get("root") is None and event == "start":
                    captured["root"] = element
                yield event, element

        return generator()

    with mock.patch("ddi_l.io.etree.iterparse", new=tracking_iterparse):
        for variable in iter_variables(buffer):
            assert isinstance(variable, Variable)
            root = captured.get("root")
            assert root is not None
            lengths.append(len(root))

    root = captured.get("root")
    assert root is not None
    assert lengths
    assert all(later <= earlier for earlier, later in itertools.pairwise(lengths))
    assert len(root) == 0


def test_read_wraps_parser_errors():
    """Malformed XML raises DDIReadError and preserves the parser exception."""

    malformed_xml = "<DDIInstance><Broken></DDIInstance"
    with pytest.raises(DDIReadError) as excinfo:
        read_ddi(malformed_xml)

    cause = excinfo.value.__cause__
    assert cause is not None
    assert isinstance(cause, BaseException)
    assert excinfo.value.original_exception is cause


def test_write_wraps_stream_errors():
    """write surfaces stream failures via DDIWriteError with chaining."""

    document = read_ddi(FIXTURE_PATH)

    class ExplodingWriter(io.BytesIO):
        def write(self, data):  # type: ignore[override]
            raise RuntimeError("boom")

    exploding = ExplodingWriter()
    with pytest.raises(DDIWriteError) as excinfo:
        write_ddi(document, exploding)

    cause = excinfo.value.__cause__
    assert isinstance(cause, RuntimeError)
    assert excinfo.value.original_exception is cause


def test_read_structural_failure_includes_location(tmp_path: Path) -> None:
    """Structural read failures surface filename and XPath context."""

    broken_path = tmp_path / "broken.xml"
    broken_path.write_text("<Broken></Broken>", encoding="utf-8")

    with pytest.raises(DDIReadError) as excinfo:
        read_ddi(broken_path)

    message = str(excinfo.value)
    assert str(broken_path) in message
    assert "/Broken" in message

    location = excinfo.value.location
    assert location is not None
    assert location.filename == str(broken_path)
    assert location.xpath == "/Broken"


def test_write_value_error_includes_xpath(monkeypatch: pytest.MonkeyPatch) -> None:
    """write_ddi wraps backend ValueError exceptions with location hints."""

    document = read_ddi(FIXTURE_PATH)

    def explode(
        *args: object, **kwargs: object
    ) -> bytes:  # pragma: no cover - patched in test
        raise ValueError("boom")

    monkeypatch.setattr(io_module, "_emit_xml", explode)

    with pytest.raises(DDIWriteError) as excinfo:
        write_ddi(document)

    message = str(excinfo.value)
    assert "/DDIInstance" in message

    location = excinfo.value.location
    assert location is not None
    assert location.xpath == "/DDIInstance"


def test_tree_uses_namespace_looks_at_tags_and_attributes():
    """A namespace counts as used when a tag *or* an attribute names it.

    This decides whether the writer declares a binding at all, and only the
    attribute half is reachable through XSI -- ``xsi`` has no elements, only
    ``xsi:type``, ``xsi:nil`` and ``xsi:schemaLocation``. The tag half is
    checked here directly rather than left to a caller that cannot exercise it.
    """
    from ddi_l._etree import create_element
    from ddi_l.io import _tree_uses_namespace

    marker = "urn:example:marker"

    plain = create_element("root")
    child = create_element("child")
    plain.append(child)
    assert _tree_uses_namespace(plain, marker) is False

    by_tag = create_element("root")
    by_tag.append(create_element(f"{{{marker}}}child"))
    assert _tree_uses_namespace(by_tag, marker) is True

    by_attribute = create_element("root")
    tagged = create_element("child")
    tagged.set(f"{{{marker}}}flag", "1")
    by_attribute.append(tagged)
    assert _tree_uses_namespace(by_attribute, marker) is True

    on_the_root_itself = create_element(f"{{{marker}}}root")
    assert _tree_uses_namespace(on_the_root_itself, marker) is True


def test_root_nsmap_seeds_the_defaults_and_xsi_only_when_used():
    """The seeded root map is the whole answer on the stdlib backend.

    Under lxml the per-element nsmaps fill most of this in anyway, which hides
    mistakes here: mutating the condition so the default bindings drop out, or
    so the xsi check asks about the wrong namespace, leaves an lxml-only suite
    green. The contract is asserted directly so it holds on both backends.
    """
    from ddi_l._etree import create_element
    from ddi_l.constants import DEFAULT_NSMAP, XSI_NS
    from ddi_l.io import _root_nsmap_for_tree

    plain = create_element("{ddi:instance:3_3}DDIInstance")
    seeded = _root_nsmap_for_tree(plain)

    for prefix, uri in DEFAULT_NSMAP.items():
        if uri == XSI_NS:
            continue
        assert seeded.get(prefix) == uri, (
            f"the default binding {prefix!r} -> {uri} has to be seeded"
        )
    assert XSI_NS not in seeded.values(), "nothing uses xsi, so nothing declares it"

    using_xsi = create_element("{ddi:instance:3_3}DDIInstance")
    using_xsi.set(f"{{{XSI_NS}}}schemaLocation", "ddi:instance:3_3 instance.xsd")

    assert XSI_NS in _root_nsmap_for_tree(using_xsi).values()


def test_iterparse_ddi_yields_populated_parents():
    """Nested maintainables are yielded without emptying their parents."""
    import ddi_l as ddi

    doc = ddi.new_study(title="Streamed", agency="example.org")
    for name in ("a", "b", "c"):
        doc.add_variable(name=name)
    payload = doc.to_xml().encode("utf-8")

    yielded = list(iterparse_ddi(io.BytesIO(payload)))
    by_type = {type(item).__name__: item for item in yielded}

    assert [type(item).__name__ for item in yielded].count("Variable") == 3
    assert len(by_type["VariableScheme"].variables) == 3
    assert len(by_type["LogicalProduct"].variables) == 3
