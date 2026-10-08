"""Build, validate, and round-trip the repository's example DDI instance.

The script is intentionally verbose so newcomers can inspect how the
``ddi_l`` models compose into a multi-study instance.  When invoked with the
``--refresh`` flag it rebuilds the bundled XML payload from scratch before
loading it back via :func:`ddi_l.read_ddi`, applying a small modification,
validating the tree, and writing the serialized XML to disk.

UUID Generation
---------------
DDI identifiers can use UUIDs for globally unique, collision-free IDs.
This script demonstrates two patterns:

1. **Random UUIDs (uuid4)**: Generate completely random identifiers::

       from uuid import uuid4
       identifier = str(uuid4())  # e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

2. **Deterministic UUIDs (uuid5)**: Generate reproducible identifiers from a
   namespace and name, useful when the same input should always produce the
   same UUID::

       from uuid import uuid5, NAMESPACE_DNS
       identifier = str(uuid5(NAMESPACE_DNS, "my-study-name"))

   The library provides ``ddi_l.constants.IDENTIFIER_NAMESPACE`` as a
   standard DDI namespace for deterministic UUID generation.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path
from uuid import uuid4, uuid5

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
for path in (SRC_PATH, PROJECT_ROOT):
    stringified = str(path)
    if stringified not in sys.path:
        sys.path.insert(0, stringified)

from ddi_l import read_ddi, schema_loader, write_ddi
from ddi_l.constants import IDENTIFIER_NAMESPACE
from ddi_l.document import DDIDocument, DDIFragment
from ddi_l.models import (
    Category,
    CodeItem,
    CodeList,
    CodeRepresentation,
    Concept,
    ConceptualComponent,
    DataCollection,
    Instrument,
    InternationalString,
    LogicalProduct,
    PhysicalStructure,
    QuestionItem,
    Reference,
    RepresentedVariable,
    StudyUnit,
    Universe,
    Variable,
)

EXAMPLE_FILENAME = "example_instance.xml"
FRAGMENT_FILENAME = "example_fragment.xml"
DEFAULT_AGENCY = "example.agency"
DEFAULT_VERSION = "1.0"


EMPLOYMENT_CONCEPT_IDENTIFIER = "concept-employment-status"
EMPLOYMENT_UNIVERSE_IDENTIFIER = "universe-urban-adults"
EMPLOYMENT_CODE_LIST_IDENTIFIER = "code-list-employment"
EMPLOYMENT_REPRESENTED_VARIABLE_IDENTIFIER = "represented-variable-employment-status"
EMPLOYMENT_CATEGORY_DEFINITIONS = [
    ("category-employment-full-time", "Employed full-time"),
    ("category-employment-part-time", "Employed part-time"),
    ("category-employment-unemployed", "Unemployed"),
    ("category-employment-not-in-labor-force", "Not in labor force"),
]

SATISFACTION_CATEGORY_DEFINITIONS = [
    ("category-satisfaction-very-satisfied", "Very satisfied"),
    ("category-satisfaction-satisfied", "Satisfied"),
    ("category-satisfaction-neutral", "Neutral"),
    ("category-satisfaction-dissatisfied", "Dissatisfied"),
    ("category-satisfaction-very-dissatisfied", "Very dissatisfied"),
]

SAFETY_CATEGORY_DEFINITIONS = [
    ("category-safety-very-safe", "Very safe"),
    ("category-safety-somewhat-safe", "Somewhat safe"),
    ("category-safety-neutral", "Neither safe nor unsafe"),
    ("category-safety-somewhat-unsafe", "Somewhat unsafe"),
    ("category-safety-very-unsafe", "Very unsafe"),
]


def _string(
    text: str, *, lang: str = "en", child_tag: str = "String"
) -> InternationalString:
    """Shortcut for building reusable internationalized string values."""

    return InternationalString(text=text, lang=lang, child_tag=child_tag)


def _label(text: str, *, lang: str = "en") -> InternationalString:
    """Shortcut for label values, which the schema spells with ``r:Content``."""

    return _string(text, lang=lang, child_tag="Content")


def _employment_concept() -> Concept:
    return Concept(
        agency=DEFAULT_AGENCY,
        identifier=EMPLOYMENT_CONCEPT_IDENTIFIER,
        version=DEFAULT_VERSION,
        names=[_string("Employment status")],
        labels=[_label("Employment status")],
    )


def _employment_universe() -> Universe:
    return Universe(
        agency=DEFAULT_AGENCY,
        identifier=EMPLOYMENT_UNIVERSE_IDENTIFIER,
        version=DEFAULT_VERSION,
        names=[_string("Adults living in metropolitan households")],
        labels=[_label("Adults living in metropolitan households")],
    )


def _employment_concept_reference() -> Reference:
    return Reference(
        type_of_object="Concept",
        agency=DEFAULT_AGENCY,
        identifier=EMPLOYMENT_CONCEPT_IDENTIFIER,
        version=DEFAULT_VERSION,
    )


def _employment_code_list_reference(code_list: CodeList) -> Reference:
    return Reference(
        type_of_object="CodeList",
        agency=code_list.agency,
        identifier=code_list.identifier,
        version=code_list.version,
    )


def _build_code_list(
    identifier: str,
    *,
    names: Iterable[str],
    categories: Iterable[Category | tuple[str, str]] | None = None,
) -> CodeList:
    resolved_names = list(names)

    category_metadata: list[tuple[str, str, str]] = []
    if categories is not None:
        for category in categories:
            if isinstance(category, Category):
                category_metadata.append(
                    (
                        category.agency or DEFAULT_AGENCY,
                        category.identifier,
                        category.version or DEFAULT_VERSION,
                    )
                )
            else:
                category_identifier, _category_label = category
                category_metadata.append(
                    (DEFAULT_AGENCY, category_identifier, DEFAULT_VERSION)
                )
    else:
        for index in range(1, len(resolved_names) + 1):
            category_metadata.append(
                (
                    DEFAULT_AGENCY,
                    f"{identifier}-category-{index}",
                    DEFAULT_VERSION,
                )
            )

    if len(category_metadata) != len(resolved_names):
        raise ValueError("Category metadata must align with provided code names.")

    codes = []
    for index, name in enumerate(resolved_names, start=1):
        category_reference = None
        agency, category_identifier, version = category_metadata[index - 1]
        if category_identifier is None:
            raise ValueError(
                "Category identifiers are required when providing metadata."
            )
        category_reference = Reference(
            type_of_object="Category",
            agency=agency,
            identifier=category_identifier,
            version=version,
        )

        codes.append(
            CodeItem(
                agency=DEFAULT_AGENCY,
                identifier=f"{identifier}-code-{index}",
                version=DEFAULT_VERSION,
                value=str(index),
                category=category_reference,
            )
        )
    return CodeList(
        agency=DEFAULT_AGENCY,
        identifier=identifier,
        version=DEFAULT_VERSION,
        names=[_string(name) for name in resolved_names],
        labels=[_label(name) for name in resolved_names],
        recommended_datatype="string",
        codes=codes,
    )


def _build_employment_concepts() -> ConceptualComponent:
    concept = _employment_concept()
    universe = _employment_universe()
    return ConceptualComponent(
        agency=DEFAULT_AGENCY,
        identifier="component-urban-employment",
        version=DEFAULT_VERSION,
        labels=[_label("Urban employment concepts")],
        concepts=[concept],
        universes=[universe],
        has_concept_scheme=True,
        has_universe_scheme=True,
    )


def _build_employment_code_list() -> CodeList:
    return _build_code_list(
        EMPLOYMENT_CODE_LIST_IDENTIFIER,
        names=[label for _, label in EMPLOYMENT_CATEGORY_DEFINITIONS],
        categories=EMPLOYMENT_CATEGORY_DEFINITIONS,
    )


def _build_categories(
    definitions: Iterable[tuple[str, str]],
    *,
    concept_reference: Reference | None = None,
) -> list[Category]:
    """Build the Category items a code list's CodeItems point at.

    Every ``CodeItem`` carries a ``CategoryReference``, so the referenced
    ``Category`` has to be present in the same document. Omitting them leaves
    an instance that is schema-valid but fails ``ddi lint`` with unresolvable
    references.
    """
    return [
        Category(
            agency=DEFAULT_AGENCY,
            identifier=identifier,
            version=DEFAULT_VERSION,
            names=[_string(label)],
            labels=[_label(label)],
            concept_reference=concept_reference,
        )
        for identifier, label in definitions
    ]


def _build_employment_categories() -> list[Category]:
    return _build_categories(
        EMPLOYMENT_CATEGORY_DEFINITIONS,
        concept_reference=_employment_concept_reference(),
    )


def _build_employment_represented_variable(code_list: CodeList) -> RepresentedVariable:
    return RepresentedVariable(
        agency=DEFAULT_AGENCY,
        identifier=EMPLOYMENT_REPRESENTED_VARIABLE_IDENTIFIER,
        version=DEFAULT_VERSION,
        names=[_string("Employment status (coded response)")],
        labels=[_label("Employment status (coded response)")],
        concept_reference=_employment_concept_reference(),
        code_representation=CodeRepresentation(
            code_list_reference=_employment_code_list_reference(code_list)
        ),
    )


def _label_scheme_wrappers(
    *,
    conceptual_component: ConceptualComponent | None = None,
    data_collection: DataCollection | None = None,
    logical_product: LogicalProduct | None = None,
    physical_structure: PhysicalStructure | None = None,
    prefix: str,
) -> None:
    """Label the scheme wrappers these models create when they serialize.

    ``ConceptScheme``, ``QuestionScheme``, ``CategoryScheme`` and the rest are
    generated during serialization rather than authored, so without
    ``set_scheme_label()`` every one of them shows up in ``ddi lint`` as a
    maintainable missing a label: nine per study, with nothing the author
    could do about it.
    """
    if conceptual_component is not None:
        conceptual_component.set_scheme_label("ConceptScheme", f"{prefix} concepts")
        conceptual_component.set_scheme_label("UniverseScheme", f"{prefix} universes")
    if data_collection is not None:
        data_collection.set_scheme_label("QuestionScheme", f"{prefix} questions")
        data_collection.set_scheme_label("InstrumentScheme", f"{prefix} instruments")
    if logical_product is not None:
        logical_product.set_scheme_label("CategoryScheme", f"{prefix} categories")
        logical_product.set_scheme_label("CodeListScheme", f"{prefix} code lists")
        logical_product.set_scheme_label("VariableScheme", f"{prefix} variables")
    if physical_structure is not None:
        physical_structure.set_scheme_label(
            "PhysicalDataProduct", f"{prefix} physical data product"
        )
        physical_structure.set_scheme_label(
            "PhysicalStructureScheme", f"{prefix} physical structures"
        )


def _build_household_study() -> StudyUnit:
    employment_component = _build_employment_concepts()

    age_question = QuestionItem(
        agency=DEFAULT_AGENCY,
        identifier="question-age",
        version=DEFAULT_VERSION,
        labels=[_label("Age")],
        question_texts=[_string("What is your age in years?", child_tag="Content")],
    )
    employment_question = QuestionItem(
        agency=DEFAULT_AGENCY,
        identifier="question-employment",
        version=DEFAULT_VERSION,
        labels=[_label("Employment status")],
        question_texts=[
            _string("Which of the following best describes your employment status?")
        ],
    )
    income_question = QuestionItem(
        agency=DEFAULT_AGENCY,
        identifier="question-income",
        version=DEFAULT_VERSION,
        labels=[_label("Household income")],
        question_texts=[
            _string(
                "What was your total household income last month (before taxes)?",
                child_tag="Content",
            )
        ],
    )

    instrument = Instrument(
        agency=DEFAULT_AGENCY,
        identifier="instrument-household",
        version=DEFAULT_VERSION,
        names=[_string("Urban Household Questionnaire")],
        labels=[_label("Urban Household Questionnaire")],
    )

    data_collection = DataCollection(
        agency=DEFAULT_AGENCY,
        identifier="collection-household",
        version=DEFAULT_VERSION,
        labels=[_label("Urban household data collection")],
        instruments=[instrument],
        questions=[age_question, employment_question, income_question],
    )

    employment_code_list = _build_employment_code_list()

    concept_reference = _employment_concept_reference()

    age_variable = Variable(
        agency=DEFAULT_AGENCY,
        identifier="var-age",
        version=DEFAULT_VERSION,
        names=[_string("Respondent age (years)")],
        labels=[_label("Respondent age (years)")],
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency=age_question.agency,
                identifier=age_question.identifier,
                version=age_question.version,
            )
        ],
    )
    employment_variable = Variable(
        agency=DEFAULT_AGENCY,
        identifier="var-employment-status",
        version=DEFAULT_VERSION,
        names=[_string("Employment status")],
        labels=[_label("Employment status")],
        concept_references=[concept_reference],
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency=employment_question.agency,
                identifier=employment_question.identifier,
                version=employment_question.version,
            )
        ],
    )
    income_variable = Variable(
        agency=DEFAULT_AGENCY,
        identifier="var-income",
        version=DEFAULT_VERSION,
        names=[_string("Monthly household income (pre-tax)")],
        labels=[_label("Monthly household income (pre-tax)")],
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency=income_question.agency,
                identifier=income_question.identifier,
                version=income_question.version,
            )
        ],
    )

    logical_product = LogicalProduct(
        agency=DEFAULT_AGENCY,
        identifier="logical-product-household",
        version=DEFAULT_VERSION,
        labels=[_label("Urban household logical product")],
        # Every CodeItem in the employment code list carries a
        # CategoryReference, so the Category items it points at have to travel
        # in the same document. Without them the instance is still
        # schema-valid but `ddi lint` reports unresolvable references.
        categories=_build_employment_categories(),
        code_lists=[employment_code_list],
        variables=[age_variable, employment_variable, income_variable],
    )

    physical_structure = PhysicalStructure(
        agency=DEFAULT_AGENCY,
        identifier="physical-household",
        version=DEFAULT_VERSION,
        names=[_string("CSV extract layout")],
        labels=[_label("CSV extract layout")],
        file_format="text/csv",
        default_data_type="string",
        default_delimiter="comma",
        default_decimal_separator=".",
    )

    _label_scheme_wrappers(
        conceptual_component=employment_component,
        data_collection=data_collection,
        logical_product=logical_product,
        physical_structure=physical_structure,
        prefix="Urban household",
    )

    return StudyUnit(
        agency=DEFAULT_AGENCY,
        identifier="study-urban-household-2021",
        version=DEFAULT_VERSION,
        data_collections=[data_collection],
        logical_products=[logical_product],
        physical_structures=[physical_structure],
        conceptual_components=[employment_component],
    )


def _build_community_study() -> StudyUnit:
    quality_concept = Concept(
        agency=DEFAULT_AGENCY,
        identifier="concept-community-quality",
        version=DEFAULT_VERSION,
        names=[_string("Perceived community quality")],
        labels=[_label("Perceived community quality")],
    )
    universe = Universe(
        agency=DEFAULT_AGENCY,
        identifier="universe-urban-households",
        version=DEFAULT_VERSION,
        names=[_string("Households located within the metropolitan study area")],
        labels=[_label("Households located within the metropolitan study area")],
    )

    satisfaction_question = QuestionItem(
        agency=DEFAULT_AGENCY,
        identifier="question-satisfaction",
        version=DEFAULT_VERSION,
        labels=[_label("Service satisfaction")],
        question_texts=[
            _string(
                "Overall, how satisfied are you with the services in your neighborhood?",
                child_tag="Content",
            )
        ],
    )
    safety_question = QuestionItem(
        agency=DEFAULT_AGENCY,
        identifier="question-safety",
        version=DEFAULT_VERSION,
        labels=[_label("Perceived safety")],
        question_texts=[
            _string("How safe do you feel walking alone at night in your area?")
        ],
    )

    instrument = Instrument(
        agency=DEFAULT_AGENCY,
        identifier="instrument-community",
        version=DEFAULT_VERSION,
        names=[_string("Community Services Questionnaire")],
        labels=[_label("Community Services Questionnaire")],
    )

    data_collection = DataCollection(
        agency=DEFAULT_AGENCY,
        identifier="collection-community",
        version=DEFAULT_VERSION,
        labels=[_label("Community services data collection")],
        instruments=[instrument],
        questions=[satisfaction_question, safety_question],
    )

    satisfaction_scale = _build_code_list(
        "code-list-satisfaction",
        names=[label for _, label in SATISFACTION_CATEGORY_DEFINITIONS],
        categories=SATISFACTION_CATEGORY_DEFINITIONS,
    )

    safety_scale = _build_code_list(
        "code-list-safety",
        names=[label for _, label in SAFETY_CATEGORY_DEFINITIONS],
        categories=SAFETY_CATEGORY_DEFINITIONS,
    )

    satisfaction_variable = Variable(
        agency=DEFAULT_AGENCY,
        identifier="var-satisfaction",
        version=DEFAULT_VERSION,
        names=[_string("Neighborhood service satisfaction")],
        labels=[_label("Neighborhood service satisfaction")],
        concept_references=[
            Reference(
                type_of_object="Concept",
                agency=quality_concept.agency,
                identifier=quality_concept.identifier,
                version=quality_concept.version,
            )
        ],
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency=satisfaction_question.agency,
                identifier=satisfaction_question.identifier,
                version=satisfaction_question.version,
            )
        ],
    )
    safety_variable = Variable(
        agency=DEFAULT_AGENCY,
        identifier="var-safety",
        version=DEFAULT_VERSION,
        names=[_string("Perceived neighborhood safety")],
        labels=[_label("Perceived neighborhood safety")],
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency=safety_question.agency,
                identifier=safety_question.identifier,
                version=safety_question.version,
            )
        ],
    )

    logical_product = LogicalProduct(
        agency=DEFAULT_AGENCY,
        identifier="logical-product-community",
        version=DEFAULT_VERSION,
        labels=[_label("Community services logical product")],
        categories=[
            *_build_categories(SATISFACTION_CATEGORY_DEFINITIONS),
            *_build_categories(SAFETY_CATEGORY_DEFINITIONS),
        ],
        code_lists=[satisfaction_scale, safety_scale],
        variables=[satisfaction_variable, safety_variable],
    )

    conceptual_component = ConceptualComponent(
        agency=DEFAULT_AGENCY,
        identifier="component-community-quality",
        version=DEFAULT_VERSION,
        labels=[_label("Community quality concepts")],
        concepts=[quality_concept],
        universes=[universe],
        has_concept_scheme=True,
        has_universe_scheme=True,
    )

    physical_structure = PhysicalStructure(
        agency=DEFAULT_AGENCY,
        identifier="physical-community",
        version=DEFAULT_VERSION,
        names=[_string("Column metadata for fixed-width extract")],
        labels=[_label("Column metadata for fixed-width extract")],
        file_format="text/plain",
        default_data_type="integer",
        default_delimiter="space",
        default_decimal_separator=".",
    )

    _label_scheme_wrappers(
        conceptual_component=conceptual_component,
        data_collection=data_collection,
        logical_product=logical_product,
        physical_structure=physical_structure,
        prefix="Community services",
    )

    return StudyUnit(
        agency=DEFAULT_AGENCY,
        identifier="study-community-services-2023",
        version=DEFAULT_VERSION,
        data_collections=[data_collection],
        logical_products=[logical_product],
        physical_structures=[physical_structure],
        conceptual_components=[conceptual_component],
    )


def build_example_document() -> DDIDocument:
    """Construct the repository's example instance using model helpers."""

    document = DDIDocument.create(
        agency=DEFAULT_AGENCY,
        identifier="urban-survey-series",
        version=DEFAULT_VERSION,
        title="Urban Survey Series",
    )
    document.ensure_namespace_prefixes()

    document.add_study_unit(_build_household_study())
    document.add_study_unit(_build_community_study())
    return document


def build_uuid4_example() -> StudyUnit:
    """Demonstrate building DDI elements with random UUID4 identifiers.

    This is the simplest UUID pattern: every identifier is completely random
    and unique. Use this when you don't need reproducible IDs and just want
    guaranteed uniqueness.

    Returns:
        A StudyUnit with random UUID4 identifiers.

    Example:
        >>> study = build_uuid4_example()
        >>> print(study.identifier)  # Random UUID like "a1b2c3d4-..."
        >>> xml = study.to_xml()  # Serialize to DDI XML
    """
    # All identifiers are random UUIDs - simple and unique
    study_id = str(uuid4())
    question_id = str(uuid4())
    variable_id = str(uuid4())
    collection_id = str(uuid4())
    logical_id = str(uuid4())

    # Build question with random UUID
    age_question = QuestionItem(
        agency=DEFAULT_AGENCY,
        identifier=question_id,
        version=DEFAULT_VERSION,
        question_texts=[_string("What is your age?", child_tag="Content")],
    )

    # Build variable referencing the question
    age_variable = Variable(
        agency=DEFAULT_AGENCY,
        identifier=variable_id,
        version=DEFAULT_VERSION,
        names=[_string("Respondent age")],
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency=DEFAULT_AGENCY,
                identifier=question_id,
                version=DEFAULT_VERSION,
            )
        ],
    )

    # Data collection with random UUID
    data_collection = DataCollection(
        agency=DEFAULT_AGENCY,
        identifier=collection_id,
        version=DEFAULT_VERSION,
        questions=[age_question],
    )

    # Logical product with random UUID
    logical_product = LogicalProduct(
        agency=DEFAULT_AGENCY,
        identifier=logical_id,
        version=DEFAULT_VERSION,
        variables=[age_variable],
    )

    return StudyUnit(
        agency=DEFAULT_AGENCY,
        identifier=study_id,
        version=DEFAULT_VERSION,
        labels=[_label("UUID4 Random Demo Study")],
        data_collections=[data_collection],
        logical_products=[logical_product],
    )


def build_uuid5_example() -> StudyUnit:
    """Demonstrate building DDI elements with deterministic UUID5 identifiers.

    This example shows how to use UUID5 for reproducible identifiers.
    The same input (namespace + name) always produces the same UUID,
    which is useful for reproducible pipelines and when you need to
    regenerate the same identifiers from source data.

    Returns:
        A StudyUnit with deterministic UUID5 identifiers.

    Example:
        >>> study = build_uuid5_example()
        >>> print(study.identifier)  # Deterministic UUID
        >>> xml = study.to_xml()  # Serialize to DDI XML
    """
    # Deterministic UUIDs based on logical names - same input always
    # produces the same UUID, useful for reproducible pipelines
    study_id = str(uuid5(IDENTIFIER_NAMESPACE, "survey-2024:study"))
    question_id = str(uuid5(IDENTIFIER_NAMESPACE, "survey-2024:age-question"))
    variable_id = str(uuid5(IDENTIFIER_NAMESPACE, "survey-2024:age-variable"))
    collection_id = str(uuid5(IDENTIFIER_NAMESPACE, "survey-2024:data-collection"))
    logical_id = str(uuid5(IDENTIFIER_NAMESPACE, "survey-2024:logical-product"))

    # Build question with deterministic UUID
    age_question = QuestionItem(
        agency=DEFAULT_AGENCY,
        identifier=question_id,
        version=DEFAULT_VERSION,
        question_texts=[_string("What is your age?", child_tag="Content")],
    )

    # Build variable referencing the question
    age_variable = Variable(
        agency=DEFAULT_AGENCY,
        identifier=variable_id,
        version=DEFAULT_VERSION,
        names=[_string("Respondent age")],
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency=DEFAULT_AGENCY,
                identifier=question_id,
                version=DEFAULT_VERSION,
            )
        ],
    )

    # Data collection with deterministic UUID
    data_collection = DataCollection(
        agency=DEFAULT_AGENCY,
        identifier=collection_id,
        version=DEFAULT_VERSION,
        questions=[age_question],
    )

    # Logical product with deterministic UUID
    logical_product = LogicalProduct(
        agency=DEFAULT_AGENCY,
        identifier=logical_id,
        version=DEFAULT_VERSION,
        variables=[age_variable],
    )

    # Study unit with deterministic UUID (same every run)
    return StudyUnit(
        agency=DEFAULT_AGENCY,
        identifier=study_id,
        version=DEFAULT_VERSION,
        labels=[_label("UUID5 Deterministic Demo Study")],
        data_collections=[data_collection],
        logical_products=[logical_product],
    )


def build_fragment_bundle() -> DDIFragment:
    """Bundle employment classifications into a fragment for reuse.

    The payload mirrors the employment slice of ``Quality_of_Life.xml`` by
    reusing the same concept, categories, and code list metadata assembled for
    the example instance.  Seeding the fragment's top-level reference with the
    represented variable shows how reusable maintainables can be distributed and
    validated independently of a full ``DDIInstance`` document.
    """

    # The fragment packages the shared employment classifications that appear in
    # ``Quality_of_Life.xml`` so they can be reused without re-encoding each
    # maintainable.  It relies on the same helper builders as the instance path
    # to keep both representations synchronized.
    code_list = _build_employment_code_list()
    represented_variable = _build_employment_represented_variable(code_list)
    fragment = DDIFragment.create(top_level=represented_variable)

    fragment.add_fragment(represented_variable)
    fragment.add_fragment(_employment_concept())
    for category in _build_employment_categories():
        fragment.add_fragment(category)
    fragment.add_fragment(code_list)
    return fragment


def _modify_loaded_document(document: DDIDocument) -> None:
    document.set_citation(title="Urban Survey Series (validated example)")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Rebuild the example instance before validating it.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / EXAMPLE_FILENAME,
        help="Location of the example XML document.",
    )
    parser.add_argument(
        "--refresh-fragment",
        action="store_true",
        help="Rebuild the example fragment before validating it.",
    )
    parser.add_argument(
        "--fragment-output",
        type=Path,
        default=Path(__file__).resolve().parent / FRAGMENT_FILENAME,
        help="Location of the reusable fragment XML document.",
    )
    parser.add_argument(
        "--uuid-demo",
        action="store_true",
        help="Build and display study units with both UUID4 and UUID5 identifiers.",
    )
    parser.add_argument(
        "--uuid4-demo",
        action="store_true",
        help="Build and display a study unit with random UUID4 identifiers only.",
    )
    parser.add_argument(
        "--uuid5-demo",
        action="store_true",
        help="Build and display a study unit with deterministic UUID5 identifiers only.",
    )
    args = parser.parse_args(argv)

    # UUID demonstration modes
    if args.uuid4_demo or args.uuid_demo:
        study = build_uuid4_example()
        print("=== UUID4 Random Demo Study ===")
        print("All identifiers are random - different every run.\n")
        print(f"Study ID: {study.identifier}")
        for dc in study.data_collections:
            print(f"DataCollection ID: {dc.identifier}")
            for q in dc.questions:
                print(f"  Question ID: {q.identifier}")
        for lp in study.logical_products:
            print(f"LogicalProduct ID: {lp.identifier}")
            for v in lp.variables:
                print(f"  Variable ID: {v.identifier}")
        if not args.uuid_demo:
            print("\nXML output preview:")
            xml_output = study.to_xml()
            from ddi_l._etree import tostring

            print(tostring(xml_output, pretty_print=True)[:1000] + "...")
            return
        print()

    if args.uuid5_demo or args.uuid_demo:
        study = build_uuid5_example()
        print("=== UUID5 Deterministic Demo Study ===")
        print("All identifiers are reproducible - same every run.\n")
        print(f"Study ID: {study.identifier}")
        for dc in study.data_collections:
            print(f"DataCollection ID: {dc.identifier}")
            for q in dc.questions:
                print(f"  Question ID: {q.identifier}")
        for lp in study.logical_products:
            print(f"LogicalProduct ID: {lp.identifier}")
            for v in lp.variables:
                print(f"  Variable ID: {v.identifier}")
        print("\nXML output preview:")
        xml_output = study.to_xml()
        from ddi_l._etree import tostring

        print(tostring(xml_output, pretty_print=True)[:1000] + "...")
        return

    if args.uuid4_demo:
        return

    output_path = args.output
    if args.refresh or not output_path.exists():
        document = build_example_document()
        write_ddi(document.root, output_path)

    instance = read_ddi(output_path, validate=True)
    _modify_loaded_document(instance)
    schema_loader.validate(instance.root)
    write_ddi(instance.root, output_path)
    print(f"Wrote validated example to {output_path}")

    fragment_output = args.fragment_output
    if args.refresh_fragment or not fragment_output.exists():
        fragment = build_fragment_bundle()
        write_ddi(fragment.root, fragment_output)
        read_ddi(fragment_output, validate=True)
        print(f"Wrote validated fragment to {fragment_output}")
    elif fragment_output.exists():
        read_ddi(fragment_output, validate=True)
        print(f"Validated existing fragment at {fragment_output}")


if __name__ == "__main__":
    main()
