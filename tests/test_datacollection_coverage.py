"""Edge cases and error paths in ddi_l.models.datacollection._monolith."""

from __future__ import annotations

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import DATA_COLLECTION_NS as D
from ddi_l.constants import REUSABLE_NS as R
from ddi_l.models.base import (
    InternationalString,
    Reference,
    qn,
)

# ── Helpers ──────────────────────────────────────────────────────────────


def _el(ns, tag, text=None, **attrib):
    el = create_element(qn(ns, tag))
    if text is not None:
        el.text = str(text)
    for k, v in attrib.items():
        el.set(k, v)
    return el


def _add_id(parent, agency="ag", ident="id-1", version="1.0.0"):
    parent.append(_el(R, "Agency", agency))
    parent.append(_el(R, "ID", ident))
    parent.append(_el(R, "Version", version))


def _make_ref(ident="ref-1"):
    return Reference(agency="ag", identifier=ident, version="1.0.0")


# ── _is_uuid_like ───────────────────────────────────────────────────────


class TestIsUuidLike:
    def test_valid_uuid(self):
        from ddi_l.models.datacollection._monolith import _is_uuid_like

        assert _is_uuid_like("550e8400-e29b-41d4-a716-446655440000")

    def test_invalid_uuid(self):
        from ddi_l.models.datacollection._monolith import _is_uuid_like

        assert not _is_uuid_like("not-a-uuid")

    def test_none(self):
        from ddi_l.models.datacollection._monolith import _is_uuid_like

        assert not _is_uuid_like(None)


# ── _maybe_generate_reference_urn ────────────────────────────────────────


class TestMaybeGenerateReferenceUrn:
    def test_generates_urn_for_non_uuid(self):
        from ddi_l.models.datacollection._monolith import (
            _maybe_generate_reference_urn,
        )

        ref = Reference(agency="ag", identifier="human-readable", version="1.0.0")
        _maybe_generate_reference_urn(ref)
        assert ref.urn is not None  # URN should have been set

    def test_no_generation_for_none_agency(self):
        from ddi_l.models.datacollection._monolith import (
            _maybe_generate_reference_urn,
        )

        ref = Reference(agency=None, identifier="id", version="1.0.0")
        result = _maybe_generate_reference_urn(ref)
        assert result is None

    def test_uuid_identifier_canonical(self):
        from ddi_l.models.datacollection._monolith import (
            _maybe_generate_reference_urn,
        )

        ref = Reference(
            agency="ag",
            identifier="550e8400-e29b-41d4-a716-446655440000",
            version="1.0.0",
            urn="urn:wrong",
        )
        result = _maybe_generate_reference_urn(ref)
        assert result is None
        # URN should be set to canonical
        assert ref.urn.startswith("urn:ddi:")  # type: ignore[union-attr]


# ── DynamicText ──────────────────────────────────────────────────────────


class TestDynamicText:
    def test_from_xml_with_plain_text(self):
        from ddi_l.models.datacollection._monolith import DynamicText

        el = create_element(qn(D, "QuestionText"))
        el.set("audienceLanguage", "en")
        el.set("isStructureRequired", "true")
        literal = create_element(qn(D, "LiteralText"))
        text_el = create_element(qn(D, "Text"))
        text_el.text = "What is your age?"
        text_el.set("isPlainText", "true")
        literal.append(text_el)
        el.append(literal)
        dt = DynamicText.from_xml(el)
        assert len(dt.texts) == 1
        assert dt.audience_language == "en"
        assert dt.is_structure_required is True

    def test_to_xml(self):
        from ddi_l.models.datacollection._monolith import DynamicText

        dt = DynamicText(
            texts=[
                InternationalString(text="Question?", lang="en", is_plain_text=True)
            ],
            audience_language="en",
            is_structure_required=False,
        )
        xml = dt.to_xml("QuestionText")
        assert xml.get("audienceLanguage") == "en"
        assert xml.get("isStructureRequired") == "false"
        literal = xml.find(qn(D, "LiteralText"))
        assert literal is not None

    def test_to_xml_other_elements(self):
        from ddi_l.models.datacollection._monolith import DynamicText

        dt = DynamicText(
            texts=[],
            other_elements=[_el(D, "Custom", "data")],
        )
        xml = dt.to_xml("QuestionText")
        assert xml.find(qn(D, "Custom")) is not None


# ── GridDimension ────────────────────────────────────────────────────────


class TestGridDimension:
    def test_from_xml_basic(self):
        from ddi_l.models.datacollection._monolith import GridDimension

        el = create_element(qn(D, "GridDimension"))
        el.set("rank", "1")
        el.set("displayCode", "true")
        el.set("displayLabel", "false")
        gd = GridDimension.from_xml(el)
        assert gd.rank == 1
        assert gd.display_code is True
        assert gd.display_label is False

    def test_from_xml_with_code_domain(self):
        from ddi_l.models.datacollection._monolith import GridDimension

        el = create_element(qn(D, "GridDimension"))
        el.set("rank", "2")
        cd = create_element(qn(D, "CodeDomain"))
        el.append(cd)
        gd = GridDimension.from_xml(el)
        assert gd.code_domain is not None

    def test_to_xml(self):
        from ddi_l.models.datacollection._monolith import GridDimension

        gd = GridDimension(
            rank=1,
            display_code=True,
            display_label=False,
            code_domain=_el(D, "CodeDomain"),
            roster=_el(D, "Roster"),
        )
        xml = gd.to_xml()
        assert xml.get("rank") == "1"
        assert xml.get("displayCode") == "true"
        assert xml.find(qn(D, "CodeDomain")) is not None
        assert xml.find(qn(D, "Roster")) is not None


# ── OutParameter ─────────────────────────────────────────────────────────


class TestOutParameter:
    def test_from_xml_wrong_tag(self):
        from ddi_l.models.datacollection._monolith import OutParameter

        with pytest.raises(ValueError):
            OutParameter.from_xml(create_element("wrong"))

    def test_from_xml_with_numeric_representation(self):
        from ddi_l.models.datacollection._monolith import OutParameter

        el = create_element(qn(R, "OutParameter"))
        el.append(_el(R, "URN", "urn:ddi:ag:op1:1"))
        el.append(_el(R, "Agency", "ag"))
        el.append(_el(R, "ID", "op1"))
        el.append(_el(R, "Version", "1.0.0"))
        el.append(_el(R, "Alias", "my-alias"))
        num_rep = create_element(qn(R, "NumericRepresentation"))
        el.append(num_rep)
        op = OutParameter.from_xml(el)
        assert op.alias == "my-alias"
        assert op.representation is not None

    def test_to_xml(self):
        from ddi_l.models.datacollection._monolith import OutParameter

        op = OutParameter(
            urn="urn:ddi:ag:op1:1",
            agency="ag",
            identifier="op1",
            version="1.0.0",
            alias="my-alias",
            representation=_el(R, "NumericRepresentation"),
            other_elements=[_el(R, "Extra")],
        )
        xml = op.to_xml()
        assert xml.find(qn(R, "URN")).text == "urn:ddi:ag:op1:1"  # type: ignore[union-attr]
        assert xml.find(qn(R, "Alias")).text == "my-alias"  # type: ignore[union-attr]
        assert xml.find(qn(R, "NumericRepresentation")) is not None
        assert xml.find(qn(R, "Extra")) is not None


# ── ConstructSequence ────────────────────────────────────────────────────


class TestConstructSequence:
    def test_from_xml_to_xml(self):
        from ddi_l.models.datacollection._monolith import ConstructSequence

        el = create_element(qn(D, "ConstructSequence"))
        el.append(_el(D, "ItemSequenceType", "InOrderOfAppearance"))
        ref_el = create_element(qn(D, "ControlConstructReference"))
        ref_el.append(_el(R, "ID", "cc1"))
        el.append(ref_el)
        cs = ConstructSequence.from_xml(el)
        assert cs.item_sequence_type == "InOrderOfAppearance"
        assert len(cs.control_construct_references) == 1
        xml = cs.to_xml()
        assert xml.find(qn(D, "ItemSequenceType")).text == "InOrderOfAppearance"  # type: ignore[union-attr]
        assert xml.find(qn(D, "ControlConstructReference")) is not None


# ── Sequence ─────────────────────────────────────────────────────────────


class TestSequence:
    def test_from_xml_to_xml(self):
        from ddi_l.models.datacollection._monolith import Sequence

        el = create_element(qn(D, "Sequence"))
        _add_id(el, ident="seq-1")
        el.append(_el(D, "TypeOfSequence", "InOrderOfAppearance"))
        ref_el = create_element(qn(D, "ControlConstructReference"))
        ref_el.append(_el(R, "ID", "cc1"))
        el.append(ref_el)
        seq = Sequence.from_xml(el)
        assert seq.type_of_sequence == "InOrderOfAppearance"
        xml = seq.to_xml()
        assert xml.find(qn(D, "TypeOfSequence")).text == "InOrderOfAppearance"  # type: ignore[union-attr]
        assert xml.find(qn(D, "ControlConstructReference")) is not None


# ── ElseIf ───────────────────────────────────────────────────────────────


class TestElseIf:
    def test_from_xml_wrong_tag(self):
        from ddi_l.models.datacollection._monolith import ElseIf

        with pytest.raises(ValueError):
            ElseIf.from_xml(create_element("wrong"))

    def test_from_xml_roundtrip(self):
        from ddi_l.models.datacollection._monolith import ElseIf

        el = create_element(qn(D, "ElseIf"))
        cond = create_element(qn(D, "IfCondition"))
        cond.text = "x > 5"
        el.append(cond)
        ref_el = create_element(qn(D, "ThenConstructReference"))
        ref_el.append(_el(R, "ID", "then-1"))
        el.append(ref_el)
        ei = ElseIf.from_xml(el)
        assert ei.if_condition is not None
        assert ei.then_construct_reference is not None
        xml = ei.to_xml()
        assert xml.find(qn(D, "IfCondition")) is not None
        assert xml.find(qn(D, "ThenConstructReference")) is not None


# ── _normalize_statement_display_text ────────────────────────────────────


class TestNormalizeStatementDisplayText:
    def test_normalize_text_with_content(self):
        from ddi_l.models.datacollection._monolith import (
            _normalize_statement_display_text,
        )

        el = create_element(qn(D, "DisplayText"))
        text_el = create_element(qn(D, "Text"))
        content = _el(R, "Content", "Hello world")
        content.set(qn("http://www.w3.org/XML/1998/namespace", "lang"), "en")
        text_el.append(content)
        el.append(text_el)
        result = _normalize_statement_display_text(el)
        assert result is not None

    def test_normalize_text_without_content(self):
        from ddi_l.models.datacollection._monolith import (
            _normalize_statement_display_text,
        )

        el = create_element(qn(D, "DisplayText"))
        text_el = create_element(qn(D, "Text"))
        text_el.text = "Plain text"
        el.append(text_el)
        result = _normalize_statement_display_text(el)
        assert result is not None


# ── _flatten_if_condition_element ────────────────────────────────────────


class TestFlattenIfCondition:
    def test_flatten_with_command_code(self):
        from ddi_l.models.datacollection._monolith import (
            _flatten_if_condition_element,
        )

        cond = create_element(qn(D, "IfCondition"))
        cmd = create_element(qn(R, "CommandCode"))
        inner = _el(R, "Command", "x > 5")
        cmd.append(inner)
        cond.append(cmd)
        result = _flatten_if_condition_element(cond)
        # CommandCode should be unwrapped
        assert result.find(qn(R, "CommandCode")) is None
        assert result.find(qn(R, "Command")) is not None

    def test_flatten_without_command_code(self):
        from ddi_l.models.datacollection._monolith import (
            _flatten_if_condition_element,
        )

        cond = create_element(qn(D, "IfCondition"))
        cond.text = "x > 5"
        result = _flatten_if_condition_element(cond)
        assert result.text == "x > 5"


# ── QuestionScheme from_xml ─────────────────────────────────────────────


class TestQuestionScheme:
    def test_from_xml_with_names(self):
        from ddi_l.models.datacollection._monolith import QuestionScheme

        el = create_element(qn(D, "QuestionScheme"))
        _add_id(el, ident="qs-1")
        name_el = create_element(qn(D, "QuestionSchemeName"))
        s = _el(R, "String", "Test Scheme")
        name_el.append(s)
        el.append(name_el)
        qs = QuestionScheme.from_xml(el)
        assert qs.identifier == "qs-1"
        assert len(qs.names) >= 1

    def test_to_xml_with_names(self):
        from ddi_l.models.datacollection._monolith import QuestionScheme

        el = create_element(qn(D, "QuestionScheme"))
        _add_id(el, ident="qs-1")
        name_el = create_element(qn(D, "QuestionSchemeName"))
        s = _el(R, "String", "Test Scheme")
        name_el.append(s)
        el.append(name_el)
        qs = QuestionScheme.from_xml(el)
        xml = qs.to_xml()
        assert xml.find(qn(D, "QuestionSchemeName")) is not None


# ── DataCaptureDevelopment to_xml ────────────────────────────────────────


class TestDataCaptureDevelopment:
    def test_from_xml_roundtrip(self):
        from ddi_l.models.datacollection._monolith import DataCaptureDevelopment

        el = create_element(qn(D, "DataCaptureDevelopment"))
        _add_id(el, ident="dcd-1")
        dcd = DataCaptureDevelopment.from_xml(el)
        xml = dcd.to_xml()
        assert xml.tag == qn(D, "DataCaptureDevelopment")


# ── _normalize_data_appraisal_information ────────────────────────────────


class TestNormalizeDataAppraisal:
    def test_normalize(self):
        from ddi_l.models.datacollection._monolith import (
            _normalize_data_appraisal_information,
        )

        el = create_element(qn(R, "DataAppraisalInformation"))
        # Add a SamplingError in wrong namespace
        se = create_element(qn(R, "SamplingError"))
        se.text = "0.05"
        el.append(se)
        result = _normalize_data_appraisal_information(el)
        assert result is not None


# ── SamplingInformationGroup ─────────────────────────────────────────────


class TestSamplingInformationGroup:
    def test_from_xml_basic(self):
        from ddi_l.models.datacollection._monolith import SamplingInformationGroup

        el = create_element(qn(D, "SamplingInformationGroup"))
        _add_id(el, ident="sig-1")
        sig = SamplingInformationGroup.from_xml(el)
        assert sig.identifier == "sig-1"

    def test_to_xml(self):
        from ddi_l.models.datacollection._monolith import SamplingInformationGroup

        el = create_element(qn(D, "SamplingInformationGroup"))
        _add_id(el, ident="sig-1")
        sig = SamplingInformationGroup.from_xml(el)
        xml = sig.to_xml()
        assert xml.tag == qn(D, "SamplingInformationGroup")


# ── ComputationItem ──────────────────────────────────────────────────────


class TestComputationItem:
    def test_from_xml_to_xml(self):
        from ddi_l.models.datacollection._monolith import ComputationItem

        el = create_element(qn(D, "ComputationItem"))
        _add_id(el, ident="ci-1")
        type_el = create_element(qn(D, "TypeOfComputationItem"))
        type_el.text = "Recoding"
        el.append(type_el)
        cmd = create_element(qn(R, "CommandCode"))
        cmd_inner = _el(R, "Command", "recode x = 1 -> 'A'")
        cmd.append(cmd_inner)
        el.append(cmd)
        ci = ComputationItem.from_xml(el)
        assert ci.type_of_computation_item.text == "Recoding"  # type: ignore[union-attr]
        xml = ci.to_xml()
        assert xml.find(qn(D, "TypeOfComputationItem")) is not None


# ── StatementItem ────────────────────────────────────────────────────────


class TestStatementItem:
    def test_from_xml_to_xml(self):
        from ddi_l.models.datacollection._monolith import StatementItem

        el = create_element(qn(D, "StatementItem"))
        _add_id(el, ident="si-1")
        display = create_element(qn(D, "DisplayText"))
        text_el = create_element(qn(D, "Text"))
        text_el.text = "Welcome"
        display.append(text_el)
        el.append(display)
        si = StatementItem.from_xml(el)
        xml = si.to_xml()
        assert xml.find(qn(D, "DisplayText")) is not None
