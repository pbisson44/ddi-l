"""Tests for the Document CRUD API (add_item, items, find, remove)."""

from __future__ import annotations

import pytest

from ddi_l.document import Document, new_study, open_ddi
from ddi_l.exceptions import DDIReferenceError
from ddi_l.models.base import InternationalString, MaintainableBase
from ddi_l.models.concept import Concept, ConceptualVariable, UnitType, Universe
from ddi_l.models.datacollection import (
    CollectionActivity,
    CollectionEvent,
    ComputationItem,
    DataCaptureMethod,
    IfThenElse,
    Instruction,
    InstructionGroup,
    Instrument,
    Loop,
    ObservationPlan,
    QuestionBlock,
    QuestionConstruct,
    QuestionGrid,
    QuestionGroup,
    QuestionItem,
    Sequence,
    StatementItem,
)
from ddi_l.models.logicalproduct import (
    Category,
    CodeList,
    DataRelationship,
    NCube,
    RepresentedVariable,
    Variable,
)
from ddi_l.models.methodology import Methodology
from ddi_l.models.physical import PhysicalInstance, RecordLayout


@pytest.fixture()
def doc() -> Document:
    return new_study(title="Test Survey", agency="test.org")


# ------------------------------------------------------------------
# new_study / open_ddi
# ------------------------------------------------------------------


class TestNewStudy:
    def test_creates_document_with_study(self):
        doc = new_study(title="Hello", agency="a.org")
        assert isinstance(doc, Document)
        assert doc.agency == "a.org"
        assert doc.title == "Hello"

    def test_title_round_trips(self, tmp_path):
        doc = new_study(title="Household Survey", agency="a.org")
        path = tmp_path / "titled.xml"
        doc.save(path)
        assert open_ddi(path).title == "Household Survey"

    def test_custom_identifier(self):
        doc = new_study(title="T", agency="a", identifier="my-id")
        study = doc._get_study()
        assert study.agency == "a"

    def test_custom_version(self):
        doc = new_study(title="T", agency="a", version="2")
        study = doc._get_study()
        assert study.version == "2"

    def test_the_study_carries_its_title_in_a_citation(self):
        """DDI-L keeps a study's title in r:Citation/r:Title, not r:Abstract."""
        doc = new_study(title="Household Survey", agency="a.org")
        rendered = doc.to_xml()
        study = rendered[rendered.index("<s:StudyUnit>") :]

        assert "<r:Citation>" in study
        assert '<r:String xml:lang="en">Household Survey</r:String>' in study

    def test_every_string_carries_a_language(self):
        """The abstract was the one untagged string in the document.

        ``InternationalString(text=title)`` passed no lang, so ``r:Content``
        alone had no ``xml:lang`` -- which carried through to an untyped
        ``dcterms:abstract`` literal in the JSON-LD rendering.
        """
        doc = new_study(title="Household Survey", agency="a.org", lang="fr-CA")
        rendered = doc.to_xml()

        assert "<r:Content>" not in rendered
        assert '<r:Content xml:lang="fr-CA">Household Survey</r:Content>' in rendered


class TestOpenDdi:
    def test_round_trip(self, tmp_path):
        doc = new_study(title="RT", agency="org")
        doc.add_question(text="Q1")
        doc.add_variable(name="V1")
        path = tmp_path / "test.xml"
        doc.save(path)

        doc2 = open_ddi(path)
        assert len(doc2.questions) == 1
        assert len(doc2.variables) == 1

    def test_open_with_validation(self, tmp_path):
        doc = new_study(title="Val", agency="org")
        path = tmp_path / "test.xml"
        doc.save(path)
        doc2 = open_ddi(path, validate=False)
        assert isinstance(doc2, Document)


# ------------------------------------------------------------------
# Explicit convenience methods
# ------------------------------------------------------------------


class TestExplicitMethods:
    def test_add_question(self, doc):
        q = doc.add_question(text="How old?")
        assert isinstance(q, QuestionItem)
        assert len(doc.questions) == 1

    def test_add_question_custom_id(self, doc):
        q = doc.add_question(text="Q", identifier="q-custom")
        assert q.identifier == "q-custom"

    def test_add_question_lang(self, doc):
        q = doc.add_question(text="Quel age?", lang="fr")
        assert q.question_texts[0].lang == "fr"

    def test_add_variable(self, doc):
        v = doc.add_variable(name="Age")
        assert isinstance(v, Variable)
        assert len(doc.variables) == 1

    def test_add_variable_with_question_ref(self, doc):
        q = doc.add_question(text="Q")
        v = doc.add_variable(name="V", question=q)
        assert len(v.question_references) == 1

    def test_add_variable_with_concept_ref(self, doc):
        c = doc.add_concept(name="C")
        v = doc.add_variable(name="V", concept=c)
        assert len(v.concept_references) == 1

    def test_add_concept(self, doc):
        c = doc.add_concept(name="Gender")
        assert isinstance(c, Concept)
        assert len(doc.concepts) == 1

    def test_add_universe(self, doc):
        u = doc.add_universe(name="Adults")
        assert isinstance(u, Universe)
        assert len(doc.universes) == 1

    def test_add_code_list(self, doc):
        cl = doc.add_code_list(name="YesNo")
        assert isinstance(cl, CodeList)
        assert len(doc.code_lists) == 1


# ------------------------------------------------------------------
# Generic add_item / items — all 20 types
# ------------------------------------------------------------------

DC_TYPES = [
    QuestionItem,
    QuestionGrid,
    QuestionBlock,
    QuestionGroup,
    Instrument,
    CollectionEvent,
    CollectionActivity,
    ObservationPlan,
    DataCaptureMethod,
    Methodology,
    Instruction,
    InstructionGroup,
    QuestionConstruct,
    Sequence,
    IfThenElse,
    StatementItem,
    ComputationItem,
    Loop,
]

CONTROL_CONSTRUCT_TYPES = [
    QuestionConstruct,
    Sequence,
    IfThenElse,
    StatementItem,
    ComputationItem,
    Loop,
]

LP_TYPES = [Variable, CodeList, Category, RepresentedVariable]

CC_TYPES = [Concept, Universe, ConceptualVariable, UnitType]

ALL_ITEM_TYPES = DC_TYPES + LP_TYPES + CC_TYPES


@pytest.mark.parametrize("item_type", ALL_ITEM_TYPES, ids=lambda t: t.__name__)
class TestGenericAddItem:
    def test_add_and_retrieve(self, doc, item_type):
        item = doc.add_item(item_type, name="Test")
        assert isinstance(item, item_type)
        found = doc.items(item_type)
        assert len(found) == 1
        assert found[0].identifier == item.identifier

    def test_custom_identifier(self, doc, item_type):
        item = doc.add_item(item_type, name="T", identifier="custom-id")
        assert item.identifier == "custom-id"

    def test_find_by_identifier(self, doc, item_type):
        item = doc.add_item(item_type, name="Findme")
        found = doc.find(item.identifier)
        assert found is not None
        assert found.identifier == item.identifier

    def test_remove_by_identifier(self, doc, item_type):
        item = doc.add_item(item_type, name="Removeme")
        assert doc.remove(item.identifier) is True
        assert doc.find(item.identifier) is None
        assert len(doc.items(item_type)) == 0


class TestGenericAddItemName:
    def test_question_item_uses_question_texts(self, doc):
        qi = doc.add_item(QuestionItem, name="How old?")
        assert len(qi.question_texts) == 1
        assert qi.question_texts[0].text == "How old?"

    def test_non_question_uses_names(self, doc):
        v = doc.add_item(Variable, name="Age")
        assert len(v.names) == 1
        assert v.names[0].text == "Age"

    def test_no_name(self, doc):
        item = doc.add_item(Variable)
        assert isinstance(item, Variable)
        assert len(item.names) == 0

    def test_explicit_names_kwarg_not_overridden(self, doc):
        custom_names = [InternationalString(text="Custom", lang="fr")]
        item = doc.add_item(Variable, name="Ignored", names=custom_names)
        assert len(item.names) == 1
        assert item.names[0].text == "Custom"


class TestGenericAddItemErrors:
    def test_unregistered_type_raises(self, doc):
        with pytest.raises(TypeError, match="not a registered item type"):
            doc.add_item(MaintainableBase, name="bad")

    def test_items_unregistered_type_raises(self, doc):
        with pytest.raises(TypeError, match="not a registered item type"):
            doc.items(MaintainableBase)


# ------------------------------------------------------------------
# find / remove edge cases
# ------------------------------------------------------------------


class TestFindRemove:
    def test_find_missing_returns_none(self, doc):
        assert doc.find("nonexistent") is None

    def test_remove_missing_returns_false(self, doc):
        assert doc.remove("nonexistent") is False

    def test_find_across_types(self, doc):
        q = doc.add_question(text="Q")
        v = doc.add_variable(name="V")
        c = doc.add_concept(name="C")
        assert doc.find(q.identifier) is not None
        assert doc.find(v.identifier) is not None
        assert doc.find(c.identifier) is not None

    def test_remove_then_find(self, doc):
        q = doc.add_question(text="Q")
        ident = q.identifier
        doc.remove(ident)
        assert doc.find(ident) is None

    def test_multiple_items_find_correct_one(self, doc):
        items = [doc.add_item(Variable, name=f"V{i}") for i in range(5)]
        target = items[2]
        found = doc.find(target.identifier)
        assert found is not None
        assert found.identifier == target.identifier


# ------------------------------------------------------------------
# Persistence
# ------------------------------------------------------------------


class TestPersistence:
    def test_save_and_load(self, doc, tmp_path):
        doc.add_question(text="Q1")
        doc.add_variable(name="V1")
        doc.add_concept(name="C1")
        path = tmp_path / "output.xml"
        doc.save(path)

        loaded = open_ddi(path)
        assert len(loaded.questions) == 1
        assert len(loaded.variables) == 1
        assert len(loaded.concepts) == 1

    def test_to_xml_returns_string(self, doc):
        doc.add_question(text="Q")
        xml = doc.to_xml()
        assert isinstance(xml, str)
        assert "<DDIInstance" in xml

    def test_to_xml_pretty_print(self, doc):
        doc.add_question(text="Q")
        pretty = doc.to_xml(pretty_print=True)
        compact = doc.to_xml(pretty_print=False)

        # Both carry the XML declaration on its own line, as ``write()`` and the
        # packaged examples do. ``pretty_print`` governs the body below it.
        declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        assert pretty.startswith(declaration)
        assert compact.startswith(declaration)

        assert "\n" in pretty.removeprefix(declaration)
        assert "\n" not in compact.removeprefix(declaration)

    def test_inner_returns_ddi_document(self, doc):
        from ddi_l.document import DDIDocument

        assert isinstance(doc.inner, DDIDocument)

    def test_validate(self, doc):
        issues = doc.validate()
        assert isinstance(issues, list)


# ------------------------------------------------------------------
# Conceptual component scheme flags
# ------------------------------------------------------------------


class TestSchemeFlags:
    def test_concept_sets_scheme_flag(self, doc):
        doc.add_item(Concept, name="C")
        study = doc._get_study()
        cc = study.conceptual_components[0]
        assert cc.has_concept_scheme is True

    def test_universe_sets_scheme_flag(self, doc):
        doc.add_item(Universe, name="U")
        study = doc._get_study()
        cc = study.conceptual_components[0]
        assert cc.has_universe_scheme is True

    def test_conceptual_variable_sets_scheme_flag(self, doc):
        doc.add_item(ConceptualVariable, name="CV")
        study = doc._get_study()
        cc = study.conceptual_components[0]
        assert cc.has_conceptual_variable_scheme is True

    def test_unit_type_sets_scheme_flag(self, doc):
        doc.add_item(UnitType, name="UT")
        study = doc._get_study()
        cc = study.conceptual_components[0]
        assert cc.has_unit_type_scheme is True


# ------------------------------------------------------------------
# Module creation
# ------------------------------------------------------------------


class TestModuleCreation:
    def test_data_collection_created_on_demand(self, doc):
        study = doc._get_study()
        assert len(study.data_collections) == 0
        doc.add_item(QuestionItem, name="Q")
        assert len(study.data_collections) == 1

    def test_logical_product_created_on_demand(self, doc):
        study = doc._get_study()
        assert len(study.logical_products) == 0
        doc.add_item(Variable, name="V")
        assert len(study.logical_products) == 1

    def test_conceptual_component_created_on_demand(self, doc):
        study = doc._get_study()
        assert len(study.conceptual_components) == 0
        doc.add_item(Concept, name="C")
        assert len(study.conceptual_components) == 1

    def test_existing_module_reused(self, doc):
        doc.add_item(Variable, name="V1")
        doc.add_item(Variable, name="V2")
        study = doc._get_study()
        assert len(study.logical_products) == 1
        assert len(study.logical_products[0].variables) == 2


# ------------------------------------------------------------------
# Control constructs (questionnaire flow) via add_item
# ------------------------------------------------------------------


class TestControlConstructs:
    def test_name_stored_as_construct_name(self, doc):
        seq = doc.add_item(Sequence, name="Section A")
        # Control constructs carry their label in ``construct_names`` (the
        # DDI ``ConstructName`` element), not the generic ``names`` field.
        assert len(seq.construct_names) == 1
        assert seq.construct_names[0].text == "Section A"
        assert not hasattr(seq, "names")

    def test_items_filter_by_type(self, doc):
        doc.add_item(Sequence, name="S1")
        doc.add_item(Sequence, name="S2")
        doc.add_item(IfThenElse, name="Gate")
        doc.add_item(StatementItem, name="Welcome")
        assert len(doc.items(Sequence)) == 2
        assert len(doc.items(IfThenElse)) == 1
        assert len(doc.items(StatementItem)) == 1
        assert len(doc.items(QuestionConstruct)) == 0

    def test_share_single_scheme(self, doc):
        doc.add_item(Sequence, name="S1")
        doc.add_item(IfThenElse, name="Gate")
        dc = doc._get_study().data_collections[0]
        # All constructs live in one control-construct list (one scheme).
        assert len(dc.control_constructs) == 2

    def test_find_and_remove(self, doc):
        seq = doc.add_item(Sequence, name="S1")
        ite = doc.add_item(IfThenElse, name="Gate")
        assert doc.find(seq.identifier) is seq
        assert doc.remove(seq.identifier) is True
        assert doc.find(seq.identifier) is None
        assert len(doc.items(Sequence)) == 0
        # The other construct is untouched.
        assert doc.find(ite.identifier) is ite

    def test_round_trips_and_validates(self, doc, tmp_path):
        q = doc.add_question(text="What is your age?")
        qc = doc.add_item(
            QuestionConstruct, name="Ask Age", question_reference=q.to_reference()
        )
        seq_a = doc.add_item(Sequence, name="Section A")
        seq_b = doc.add_item(Sequence, name="Section B")
        seq_a.control_construct_references = [qc.to_reference()]
        ite = doc.add_item(IfThenElse, name="Age gate")
        ite.then_construct_reference = seq_a.to_reference()
        ite.else_construct_reference = seq_b.to_reference()
        doc.add_item(StatementItem, name="Welcome")
        doc.add_item(Instrument, name="Instrument")

        assert doc.validate() == []

        path = tmp_path / "flow.xml"
        doc.save(path)
        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        assert len(reloaded.items(QuestionConstruct)) == 1
        assert len(reloaded.items(Sequence)) == 2
        assert len(reloaded.items(IfThenElse)) == 1
        assert len(reloaded.items(StatementItem)) == 1

    def test_serializes_single_control_construct_scheme(self, doc):
        doc.add_item(Sequence, name="S1")
        doc.add_item(IfThenElse, name="Gate")
        xml = doc.to_xml()
        assert xml.count("<d:ControlConstructScheme") == 1
        assert "<d:Sequence" in xml
        assert "<d:IfThenElse" in xml

    def test_if_then_else_condition_and_elseif_round_trip(self, doc, tmp_path):
        seq_b = doc.add_item(Sequence, name="Section B")
        seq_c = doc.add_item(Sequence, name="Section C")
        seq_retire = doc.add_item(Sequence, name="Retirement")

        gate = doc.add_item(IfThenElse, name="Age gate")
        assert gate.set_condition("age >= 16", description="Working age") is gate
        gate.then_construct_reference = seq_b.to_reference()
        gate.else_construct_reference = seq_c.to_reference()
        branch = gate.add_elseif(seq_retire.to_reference(), command="age >= 65")
        assert branch.if_condition is not None

        assert doc.validate() == []
        path = tmp_path / "ite.xml"
        doc.save(path)

        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        gate2 = reloaded.items(IfThenElse)[0]
        assert isinstance(gate2, IfThenElse)
        assert gate2.if_condition is not None
        # Command expression survives the round trip.
        from ddi_l.constants import REUSABLE_NS
        from ddi_l.models.base import qn

        content = gate2.if_condition.find(f".//{qn(REUSABLE_NS, 'CommandContent')}")
        assert content is not None and content.text == "age >= 16"
        assert len(gate2.else_if_branches) == 1

    def test_make_if_condition_is_exported(self):
        from ddi_l.constants import REUSABLE_NS
        from ddi_l.models.base import qn
        from ddi_l.models.datacollection import make_if_condition

        condition = make_if_condition("x > 0", description="positive", language="R")
        content = condition.find(f".//{qn(REUSABLE_NS, 'CommandContent')}")
        language = condition.find(f".//{qn(REUSABLE_NS, 'ProgramLanguage')}")
        assert content is not None and content.text == "x > 0"
        assert language is not None and language.text == "R"

    def test_loop_round_trips_with_reference(self, doc, tmp_path):
        seq = doc.add_item(Sequence, name="Demographics")
        loop = doc.add_item(Loop, name="Household roster loop")
        loop.control_construct_reference = seq.to_reference()
        doc.add_item(Instrument, name="Instrument")

        assert doc.validate() == []
        path = tmp_path / "loop.xml"
        doc.save(path)

        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        loops = reloaded.items(Loop)
        assert len(loops) == 1
        loaded_loop = loops[0]
        assert isinstance(loaded_loop, Loop)
        assert loaded_loop.control_construct_reference is not None
        assert loaded_loop.control_construct_reference.identifier == seq.identifier


# ------------------------------------------------------------------
# Physical instance (data file) via add_item
# ------------------------------------------------------------------


class TestPhysicalInstance:
    def test_add_and_retrieve_at_study_level(self, doc):
        pi = doc.add_item(PhysicalInstance, name="2021 Microdata File")
        assert isinstance(pi, PhysicalInstance)
        assert len(doc.items(PhysicalInstance)) == 1
        # Stored directly on the study, not inside a sub-module.
        assert doc._get_study().physical_instances[0] is pi

    def test_name_becomes_citation_title(self, doc):
        from ddi_l.constants import REUSABLE_NS
        from ddi_l.models.base import qn

        pi = doc.add_item(PhysicalInstance, name="My data file")
        assert pi.citation is not None
        title = pi.citation.find(f".//{qn(REUSABLE_NS, 'String')}")
        assert title is not None and title.text == "My data file"
        # PhysicalInstance has no Name element.
        assert not hasattr(pi, "names")

    def test_helpers_round_trip_and_validate(self, doc, tmp_path):
        from ddi_l.constants import PHYSICAL_INSTANCE_NS
        from ddi_l.models.base import qn

        doc.add_variable(name="age")
        pi = doc.add_item(PhysicalInstance, name="2021 Microdata File")
        assert pi.set_data_file("https://example.org/health-2021.csv") is pi
        assert pi.set_record_count(15000) is pi

        assert doc.validate() == []
        path = tmp_path / "pi.xml"
        doc.save(path)

        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        instances = reloaded.items(PhysicalInstance)
        assert len(instances) == 1
        pi2 = instances[0]
        assert isinstance(pi2, PhysicalInstance)
        uri = pi2.data_file_identifications[0].find(
            qn(PHYSICAL_INSTANCE_NS, "DataFileURI")
        )
        assert uri is not None and uri.text == "https://example.org/health-2021.csv"
        assert pi2.gross_file_structure is not None
        case_quantity = pi2.gross_file_structure.find(
            qn(PHYSICAL_INSTANCE_NS, "CaseQuantity")
        )
        assert case_quantity is not None and case_quantity.text == "15000"

    def test_find_and_remove(self, doc):
        pi = doc.add_item(PhysicalInstance, name="F1")
        assert doc.find(pi.identifier) is pi
        assert doc.remove(pi.identifier) is True
        assert doc.find(pi.identifier) is None
        assert len(doc.items(PhysicalInstance)) == 0


# ------------------------------------------------------------------
# Record layouts (variable-to-position mapping) via add_record_layout
# ------------------------------------------------------------------


class TestRecordLayout:
    def test_add_record_layout_at_study_level(self, doc):
        rl = doc.add_record_layout()
        assert isinstance(rl, RecordLayout)
        assert len(doc.items(RecordLayout)) == 1
        assert doc._get_study().record_layouts[0] is rl
        # A backing physical structure is created and linked.
        assert rl.physical_structure_link_reference is not None
        assert len(doc._get_study().physical_structures) == 1

    def test_data_items_round_trip_and_validate(self, doc, tmp_path):
        from ddi_l.constants import PHYSICAL_DATA_PRODUCT_NS, REUSABLE_NS
        from ddi_l.models.base import qn

        age = doc.add_variable(name="age")
        income = doc.add_variable(name="income")
        rl = doc.add_record_layout()
        rl.add_data_item(age.to_reference(), start_position=1, width=2)
        rl.add_data_item(income.to_reference(), start_position=3, width=8)

        assert doc.validate() == []
        path = tmp_path / "rl.xml"
        doc.save(path)

        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        layouts = reloaded.items(RecordLayout)
        assert len(layouts) == 1
        rl2 = layouts[0]
        assert isinstance(rl2, RecordLayout)
        assert rl2.array_base == 0
        assert len(rl2.data_items) == 2
        # First mapping points at the age variable at start position 1.
        var_id = rl2.data_items[0].find(
            f"{qn(REUSABLE_NS, 'VariableReference')}/{qn(REUSABLE_NS, 'ID')}"
        )
        start = rl2.data_items[0].find(
            f"{qn(PHYSICAL_DATA_PRODUCT_NS, 'PhysicalLocation')}/"
            f"{qn(PHYSICAL_DATA_PRODUCT_NS, 'StartPosition')}"
        )
        assert var_id is not None and var_id.text == age.identifier
        assert start is not None and start.text == "1"

    def test_find_and_remove(self, doc):
        rl = doc.add_record_layout()
        assert doc.find(rl.identifier) is rl
        assert doc.remove(rl.identifier) is True
        assert doc.find(rl.identifier) is None
        assert len(doc.items(RecordLayout)) == 0

    def test_link_to_logical_record(self, doc, tmp_path):
        from ddi_l.constants import PHYSICAL_DATA_PRODUCT_NS, REUSABLE_NS
        from ddi_l.models.base import qn

        age = doc.add_variable(name="age")
        dr = doc.add_data_relationship()
        record = dr.add_logical_record()
        rl = doc.add_record_layout(logical_record=record)
        rl.add_data_item(age.to_reference(), start_position=1, width=2)

        assert doc.validate() == []
        path = tmp_path / "linked.xml"
        doc.save(path)

        reopened = open_ddi(path)
        assert reopened.validate() == []
        structure = reopened._get_study().physical_structures[0]
        assert len(structure.gross_record_structures) == 1
        ref_id = structure.gross_record_structures[0].find(
            f"{qn(PHYSICAL_DATA_PRODUCT_NS, 'LogicalRecordReference')}/"
            f"{qn(REUSABLE_NS, 'ID')}"
        )
        assert ref_id is not None and ref_id.text == record.identifier


# ------------------------------------------------------------------
# Data relationships / logical records
# ------------------------------------------------------------------


class TestDataRelationship:
    def test_add_in_logical_product(self, doc):
        dr = doc.add_data_relationship()
        assert isinstance(dr, DataRelationship)
        assert len(doc.items(DataRelationship)) == 1
        assert doc._get_study().logical_products[0].data_relationships[0] is dr

    def test_logical_records_round_trip_and_validate(self, doc, tmp_path):
        from ddi_l.models.logicalproduct import LogicalRecord

        doc.add_variable(name="age")
        doc.add_variable(name="income")
        dr = doc.add_data_relationship()
        record = dr.add_logical_record()
        assert record.variables_in_record is not None

        assert doc.validate() == []
        path = tmp_path / "dr.xml"
        doc.save(path)

        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        relationships = reloaded.items(DataRelationship)
        assert len(relationships) == 1
        dr2 = relationships[0]
        assert isinstance(dr2, DataRelationship)
        assert len(dr2.logical_records) == 1
        assert isinstance(dr2.logical_records[0], LogicalRecord)
        assert dr2.logical_records[0].variables_in_record is not None

    def test_find_and_remove(self, doc):
        dr = doc.add_data_relationship()
        assert doc.find(dr.identifier) is dr
        assert doc.remove(dr.identifier) is True
        assert doc.find(dr.identifier) is None
        assert len(doc.items(DataRelationship)) == 0


# ------------------------------------------------------------------
# NCubes (multidimensional data)
# ------------------------------------------------------------------


class TestNCube:
    def test_add_in_logical_product(self, doc):
        cube = doc.add_ncube(name="Population")
        assert isinstance(cube, NCube)
        assert len(doc.items(NCube)) == 1
        assert doc._get_study().logical_products[0].n_cubes[0] is cube

    def test_dimensions_and_measures_round_trip_and_validate(self, doc, tmp_path):
        year = doc.add_variable(name="year")
        region = doc.add_variable(name="region")
        population = doc.add_variable(name="population")
        cube = doc.add_ncube(name="Population by year and region")
        cube.add_dimension(year.to_reference())
        cube.add_dimension(region.to_reference())
        cube.add_measure(population.to_reference())
        # Ranks are assigned in order.
        assert cube.dimensions[0].get("rank") == "1"
        assert cube.dimensions[1].get("rank") == "2"

        assert doc.validate() == []
        path = tmp_path / "cube.xml"
        doc.save(path)

        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        cubes = reloaded.items(NCube)
        assert len(cubes) == 1
        cube2 = cubes[0]
        assert isinstance(cube2, NCube)
        assert len(cube2.dimensions) == 2
        assert len(cube2.measure_definitions) == 1

    def test_attribute_round_trips(self, doc, tmp_path):
        year = doc.add_variable(name="year")
        pop = doc.add_variable(name="pop")
        flag = doc.add_variable(name="quality_flag")
        cube = doc.add_ncube(name="Pop")
        cube.add_dimension(year.to_reference())
        cube.add_measure(pop.to_reference())
        cube.add_attribute(flag.to_reference())
        assert doc.validate() == []

        path = tmp_path / "attr.xml"
        doc.save(path)
        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        cube2 = reloaded.items(NCube)[0]
        assert isinstance(cube2, NCube)
        assert len(cube2.attributes) == 1

    def test_find_and_remove(self, doc):
        cube = doc.add_ncube(name="C")
        assert doc.find(cube.identifier) is cube
        assert doc.remove(cube.identifier) is True
        assert doc.find(cube.identifier) is None
        assert len(doc.items(NCube)) == 0


# ------------------------------------------------------------------
# Editing after reopening (scheme-member reconciliation)
# ------------------------------------------------------------------


class TestReopenAndEdit:
    def test_direct_mutation_after_save_persists(self, tmp_path):
        # A direct in-place edit (set_property) after a save must serialize on
        # the next save without any manual dirty flag.
        doc = new_study(title="T", agency="a.org")
        variable = doc.add_variable(name="income")
        path = tmp_path / "a.xml"
        doc.save(path)

        found = doc.find(variable.identifier)
        assert found is not None
        found.set_property("myorg:source_system", "CRM-2024")
        path2 = tmp_path / "b.xml"
        doc.save(path2)

        final = open_ddi(path2)
        assert final.variables[0].get_property("myorg:source_system") == "CRM-2024"

    def test_add_variable_after_reopen_is_kept(self, tmp_path):
        # Regression: appending to a parsed logical product must serialize.
        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        path = tmp_path / "a.xml"
        doc.save(path)

        reopened = open_ddi(path)
        reopened.add_variable(name="income")
        path2 = tmp_path / "b.xml"
        reopened.save(path2)

        final = open_ddi(path2)
        names = sorted(v.names[0].text for v in final.variables)
        assert names == ["age", "income"]
        assert final.validate() == []

    def test_add_code_list_after_reopen_is_kept(self, tmp_path):
        doc = new_study(title="T", agency="a.org")
        doc.add_code_list(name="Sex")
        path = tmp_path / "a.xml"
        doc.save(path)

        reopened = open_ddi(path)
        reopened.add_code_list(name="Region")
        path2 = tmp_path / "b.xml"
        reopened.save(path2)

        final = open_ddi(path2)
        assert len(final.code_lists) == 2


# ------------------------------------------------------------------
# Groups (study series / publication packaging)
# ------------------------------------------------------------------


class TestGroup:
    def test_add_group_organizes_study(self, doc):
        from ddi_l.models.group import Group

        doc.add_variable(name="age")
        group = doc.add_group()
        assert isinstance(group, Group)
        assert len(doc.groups) == 1
        # The study still resolves (now nested in the group).
        assert len(doc.variables) == 1

    def test_edit_after_group_round_trips(self, tmp_path):
        doc = new_study(title="Wave 1", agency="health.gc.ca")
        doc.add_variable(name="age")
        doc.add_group()
        # Editing after grouping must still reach the grouped study.
        doc.add_variable(name="income")
        doc.add_question(text="How old?")
        assert doc.validate() == []

        path = tmp_path / "grouped.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []
        assert len(reopened.groups) == 1
        assert sorted(v.names[0].text for v in reopened.variables) == ["age", "income"]
        assert len(reopened.questions) == 1

    def test_grouped_file_reopens_and_edits(self, tmp_path):
        doc = new_study(title="S", agency="a.org")
        doc.add_variable(name="age")
        doc.add_group()
        path = tmp_path / "g.xml"
        doc.save(path)

        # Reopen a group-organized file and keep editing it.
        reopened = open_ddi(path)
        reopened.add_variable(name="region")
        path2 = tmp_path / "g2.xml"
        reopened.save(path2)

        final = open_ddi(path2)
        assert sorted(v.names[0].text for v in final.variables) == ["age", "region"]
        assert final.validate() == []


# ------------------------------------------------------------------
# DDI profiles (declaring which elements a system uses)
# ------------------------------------------------------------------


class TestDDIProfile:
    def test_add_and_used_statements_round_trip(self, tmp_path):
        from ddi_l.models.profile import DDIProfile

        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        profile = doc.add_ddi_profile(
            name="Deposit profile", used_xpaths=["//s:StudyUnit"]
        )
        assert isinstance(profile, DDIProfile)
        # Post-creation edits must persist (tracked re-serialization).
        profile.add_used("//l:Variable", is_required=True)

        assert doc.validate() == []
        path = tmp_path / "profile.xml"
        doc.save(path)

        reopened = open_ddi(path)
        assert reopened.validate() == []
        profiles = reopened.ddi_profiles
        assert len(profiles) == 1
        assert profiles[0].names[0].text == "Deposit profile"
        assert len(profiles[0].useds) == 2

    def test_profile_serializes_with_pr_prefix(self):
        """DDIProfile uses the stable ``pr`` prefix, not an auto-generated one."""
        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        doc.add_ddi_profile(name="P", used_xpaths=["//s:StudyUnit"])
        xml = doc.to_xml()
        assert 'xmlns:pr="ddi:ddiprofile:3_3"' in xml
        assert "<pr:DDIProfile>" in xml
        # No auto-generated fallback prefix for the ddiprofile namespace.
        assert 'xmlns:p0="ddi:ddiprofile:3_3"' not in xml

    def test_open_existing_p0_profile_migrates_to_pr(self, tmp_path):
        """Opening a doc that used the old auto-generated p0 prefix re-emits pr."""
        legacy = (
            '<DDIInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3"'
            ' xmlns:s="ddi:studyunit:3_3" xmlns:p0="ddi:ddiprofile:3_3">'
            "<r:Agency>ex.org</r:Agency><r:ID>I1</r:ID><r:Version>1</r:Version>"
            "<s:StudyUnit><r:Agency>ex.org</r:Agency><r:ID>SU1</r:ID>"
            "<r:Version>1</r:Version><r:Abstract><r:Content>T</r:Content>"
            "</r:Abstract></s:StudyUnit>"
            "<p0:DDIProfile><r:Agency>ex.org</r:Agency><r:ID>P1</r:ID>"
            "<r:Version>1</r:Version>"
            "<p0:DDIProfileName><r:String>P</r:String></p0:DDIProfileName>"
            "<p0:XPathVersion>1.0</p0:XPathVersion>"
            '<p0:Used xpath="//s:StudyUnit"/></p0:DDIProfile></DDIInstance>'
        )
        path = tmp_path / "legacy.xml"
        path.write_text(legacy, encoding="utf-8")

        doc = open_ddi(path)
        out = doc.to_xml()
        assert doc.validate() == []
        assert 'xmlns:pr="ddi:ddiprofile:3_3"' in out
        assert "<pr:DDIProfile>" in out
        # The stale auto-generated prefix must not survive the round-trip.
        assert "p0" not in out
        # Canonical prefixes for other modules are preserved too.
        assert "<s:StudyUnit>" in out


class TestInstanceLevelPackages:
    def test_add_archive_round_trip(self, tmp_path):
        from ddi_l.models.archive import Archive

        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        archive = doc.add_archive()
        assert isinstance(archive, Archive)
        assert doc.validate() == []

        path = tmp_path / "arc.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []
        assert len(reopened.archives) == 1
        assert reopened.archives[0].identifier == archive.identifier

    def test_add_resource_package_round_trip(self, tmp_path):
        from ddi_l.models.group import ResourcePackage

        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        pkg = doc.add_resource_package()
        assert isinstance(pkg, ResourcePackage)
        assert doc.validate() == []

        path = tmp_path / "rp.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []
        packages = reopened.resource_packages
        assert len(packages) == 1
        assert packages[0].identifier == pkg.identifier

    def test_add_local_holding_package_round_trip(self, tmp_path):
        from ddi_l.models.group import LocalHoldingPackage

        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        pkg = doc.add_local_holding_package()
        assert isinstance(pkg, LocalHoldingPackage)
        # The default holding references the primary study.
        assert len(pkg.depository_study_unit_references) == 1
        assert doc.validate() == []

        path = tmp_path / "lhp.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []
        packages = reopened.local_holding_packages
        assert len(packages) == 1
        assert packages[0].identifier == pkg.identifier

    def test_add_translation_information_round_trip(self, tmp_path):
        from ddi_l.models.instance import TranslationInformation

        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        info = doc.add_translation_information(
            languages=["en", "fr"], description="Translated from French."
        )
        assert isinstance(info, TranslationInformation)
        assert doc.validate() == []

        path = tmp_path / "ti.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []
        loaded = reopened.translation_information
        assert loaded is not None
        assert loaded.languages == ["en", "fr"]
        assert loaded.description == "Translated from French."

    def test_translation_information_is_replaced_not_duplicated(self):
        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        doc.add_translation_information(languages=["en"])
        doc.add_translation_information(languages=["fr"], description="Nouvelle.")
        assert doc.validate() == []
        info = doc.translation_information
        assert info is not None
        assert info.languages == ["fr"]
        assert info.description == "Nouvelle."
        # Exactly one TranslationInformation element on the instance.
        assert doc.to_xml().count("<TranslationInformation") == 1

    def test_all_instance_extras_together_validate(self, tmp_path):
        doc = new_study(title="T", agency="a.org")
        doc.add_variable(name="age")
        doc.add_archive()
        doc.add_resource_package()
        doc.add_local_holding_package()
        doc.add_ddi_profile(name="P", used_xpaths=["//s:StudyUnit"])
        doc.add_translation_information(languages=["en"])
        assert doc.validate() == []

        path = tmp_path / "all.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []
        assert len(reopened.resource_packages) == 1
        assert len(reopened.local_holding_packages) == 1
        assert len(reopened.archives) == 1
        assert reopened.translation_information is not None


# ------------------------------------------------------------------
# Comparisons and multi-study groups (harmonization)
# ------------------------------------------------------------------


class TestComparisonAndMultiStudy:
    def test_comparison_maps_round_trip(self, tmp_path):
        from ddi_l.models.comparison import Comparison

        doc = new_study(title="Wave 1", agency="health.gc.ca")
        age_2020 = doc.add_variable(name="age_2020")
        age_2021 = doc.add_variable(name="age_2021")
        comparison = doc.add_comparison(name="2020 to 2021")
        assert isinstance(comparison, Comparison)
        comparison.add_variable_map(age_2020.to_reference(), age_2021.to_reference())

        assert doc.validate() == []
        path = tmp_path / "cmp.xml"
        doc.save(path)

        reopened = open_ddi(path)
        assert reopened.validate() == []
        comparisons = reopened.comparisons
        assert len(comparisons) == 1
        assert len(comparisons[0].variable_maps) == 1

    def test_add_study_makes_a_multi_study_group(self, tmp_path):
        from ddi_l.constants import GROUP_NS, STUDY_UNIT_NS
        from ddi_l.models.base import qn

        doc = new_study(title="Wave 1", agency="a.org")
        doc.add_variable(name="age")
        doc.add_study(title="Wave 2")
        assert doc.validate() == []

        path = tmp_path / "series.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []
        group = reopened._inner._root.find(qn(GROUP_NS, "Group"))
        assert group is not None
        assert len(group.findall(qn(STUDY_UNIT_NS, "StudyUnit"))) == 2
        # The primary study is still editable.
        assert sorted(v.names[0].text for v in reopened.variables) == ["age"]

    def test_study_cursor_targets_the_chosen_study(self, tmp_path):
        from ddi_l.constants import GROUP_NS, STUDY_UNIT_NS
        from ddi_l.models.base import qn
        from ddi_l.models.study import StudyUnit

        doc = new_study(title="Wave 1", agency="a.org")
        # The primary study, edited through a cursor.
        doc.study().add_variable(name="age_w1")
        wave2 = doc.add_study(title="Wave 2")
        # A non-primary study, edited through its cursor.
        doc.study(wave2.identifier).add_variable(name="income_w2")
        doc.study(wave2.identifier).add_question(text="Income?")
        assert doc.validate() == []

        path = tmp_path / "cursor.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []

        group = reopened._inner._root.find(qn(GROUP_NS, "Group"))
        assert group is not None
        variables_by_study = {}
        for element in group.findall(qn(STUDY_UNIT_NS, "StudyUnit")):
            study = StudyUnit.from_xml(element)
            names = [
                v.names[0].text
                for lp in study.logical_products
                for v in lp.variables
                if v.names
            ]
            variables_by_study[study.identifier] = names

        # Each study owns exactly its own variable — no cross-contamination.
        assert sorted(sorted(v) for v in variables_by_study.values()) == [
            ["age_w1"],
            ["income_w2"],
        ]

    def test_study_cursor_unknown_identifier_raises(self):
        doc = new_study(title="Wave 1", agency="a.org")
        doc.add_variable(name="age")
        with pytest.raises(DDIReferenceError):
            doc.study("does-not-exist")

    def test_additional_map_types_validate(self, tmp_path):
        doc = new_study(title="T", agency="a.org")
        c1 = doc.add_concept(name="c1")
        c2 = doc.add_concept(name="c2")
        u1 = doc.add_universe(name="u1")
        u2 = doc.add_universe(name="u2")
        comparison = doc.add_comparison(name="maps")
        comparison.add_concept_map(c1.to_reference(), c2.to_reference())
        comparison.add_universe_map(u1.to_reference(), u2.to_reference())
        assert doc.validate() == []

        path = tmp_path / "maps.xml"
        doc.save(path)
        reopened = open_ddi(path)
        assert reopened.validate() == []
        comparison2 = reopened.comparisons[0]
        assert len(comparison2.concept_maps) == 1
        assert len(comparison2.universe_maps) == 1


# ------------------------------------------------------------------
# Inline datasets (data values stored in the document)
# ------------------------------------------------------------------


class TestDataSet:
    def test_namespace_constants_are_correct(self):
        from ddi_l.constants import DATASET_NS, DDI_PROFILE_NS

        assert DDI_PROFILE_NS == "ddi:ddiprofile:3_3"
        assert DATASET_NS == "ddi:dataset:3_3"

    def test_inline_values_round_trip_and_validate(self, tmp_path):
        from ddi_l.models.dataset import DataSet

        doc = new_study(title="T", agency="a.org")
        age = doc.add_variable(name="age")
        dataset = doc.add_dataset(name="Sample rows")
        assert isinstance(dataset, DataSet)
        dataset.add_item_value(age.to_reference(), record="1", value="42")
        dataset.add_item_value(age.to_reference(), record="2", value="37")

        assert doc.validate() == []
        path = tmp_path / "ds.xml"
        doc.save(path)

        reopened = open_ddi(path)
        assert reopened.validate() == []
        datasets = reopened._get_study().datasets
        assert len(datasets) == 1
        assert len(datasets[0].item_values) == 2


# ------------------------------------------------------------------
# Variable representations (numeric / coded / text / datetime)
# ------------------------------------------------------------------


class TestVariableRepresentation:
    def test_setters_chain_and_return_self(self, doc):
        v = doc.add_variable(name="age")
        assert v.set_numeric("Integer", low=0, high=120) is v
        rep = v.variable_representation.numeric_representation
        assert rep.numeric_type_code == "Integer"
        assert rep.number_range.low == "0"
        assert rep.number_range.high == "120"

    def test_coded_takes_code_list_reference(self, doc):
        cl = doc.add_code_list(name="Sex")
        v = doc.add_variable(name="sex").set_coded(cl)
        ref = v.variable_representation.code_representation.code_list_reference
        assert ref is not None and ref.identifier == cl.identifier

    def test_all_representations_round_trip_and_validate(self, doc, tmp_path):
        cl = doc.add_code_list(name="Sex")
        doc.add_variable(name="age").set_numeric("Integer", low=0, high=120)
        doc.add_variable(name="sex").set_coded(cl)
        doc.add_variable(name="comment").set_text()
        doc.add_variable(name="dob").set_datetime("Date")

        assert doc.validate() == []
        path = tmp_path / "rep.xml"
        doc.save(path)

        reloaded = open_ddi(path)
        assert reloaded.validate() == []
        by_name = {v.names[0].text: v for v in reloaded.variables}

        age_rep = by_name["age"].variable_representation
        assert age_rep is not None and age_rep.numeric_representation is not None
        assert age_rep.numeric_representation.numeric_type_code == "Integer"

        sex_rep = by_name["sex"].variable_representation
        assert sex_rep is not None and sex_rep.code_representation is not None

        comment_rep = by_name["comment"].variable_representation
        assert comment_rep is not None and comment_rep.text_representation is not None

        dob_rep = by_name["dob"].variable_representation
        assert dob_rep is not None and dob_rep.date_time_representation is not None
        assert dob_rep.date_time_representation.date_type_code == "Date"
