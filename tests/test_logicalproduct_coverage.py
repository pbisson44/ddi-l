"""Edge cases and error paths in ddi_l.models.logicalproduct."""

from __future__ import annotations

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import LOGICAL_PRODUCT_NS as L
from ddi_l.constants import REUSABLE_NS as R
from ddi_l.models.base import (
    InternationalString,
    Reference,
    qn,
)
from ddi_l.models.logicalproduct import (
    Category,
    CategoryScheme,
    CodeItem,
    CodeList,
    CodeListScheme,
    CodeRepresentation,
    DateTimeRepresentation,
    LogicalProduct,
    NumberRange,
    NumericRepresentation,
    RepresentedVariable,
    RepresentedVariableScheme,
    TextRepresentation,
    Variable,
    VariableGroup,
    VariableRepresentation,
    VariableScheme,
)

# ── Helpers ──────────────────────────────────────────────────────────────


def _el(ns, tag, text=None, **attrib):
    el = create_element(qn(ns, tag))
    if text is not None:
        el.text = str(text)
    for k, v in attrib.items():
        el.set(k, v)
    return el


def _add_id(parent, agency="test.agency", ident="id-1", version="1.0.0"):
    parent.append(_el(R, "Agency", agency))
    parent.append(_el(R, "ID", ident))
    parent.append(_el(R, "Version", version))


def _ref_el(tag, ns=R, agency="ag", ident="ref-1", version="1.0.0"):
    """Build a reference XML element."""
    el = create_element(qn(ns, tag))
    el.append(_el(R, "Agency", agency))
    el.append(_el(R, "ID", ident))
    el.append(_el(R, "Version", version))
    return el


def _make_ref(agency="ag", ident="ref-1", version="1.0.0"):
    """Return a Reference object."""
    el = _ref_el("SomeReference", agency=agency, ident=ident, version=version)
    return Reference.from_xml(el)


# ── NumberRange ──────────────────────────────────────────────────────────


class TestNumberRange:
    def test_from_xml_wrong_tag_raises(self):
        el = create_element("wrong")
        with pytest.raises(ValueError):
            NumberRange.from_xml(el)

    def test_from_xml_missing_limits(self):
        el = create_element(qn(R, "NumberRange"))
        nr = NumberRange.from_xml(el)
        assert nr.low is None and nr.high is None

    def test_roundtrip(self):
        el = create_element(qn(R, "NumberRange"))
        low = _el(R, "Low", "0")
        low.set("isInclusive", "true")
        el.append(low)
        high = _el(R, "High", "100")
        high.set("isInclusive", "false")
        el.append(high)
        nr = NumberRange.from_xml(el)
        out = nr.to_xml()
        assert out.find(qn(R, "Low")).text == "0"  # type: ignore[union-attr]
        assert out.find(qn(R, "High")).text == "100"  # type: ignore[union-attr]


# ── Representation tag validation ────────────────────────────────────────


class TestRepresentationTagValidation:
    def test_code_representation_wrong_tag(self):
        with pytest.raises(ValueError):
            CodeRepresentation.from_xml(create_element("wrong"))

    def test_numeric_representation_wrong_tag(self):
        with pytest.raises(ValueError):
            NumericRepresentation.from_xml(create_element("wrong"))

    def test_datetime_representation_wrong_tag(self):
        with pytest.raises(ValueError):
            DateTimeRepresentation.from_xml(create_element("wrong"))

    def test_text_representation_wrong_tag(self):
        with pytest.raises(ValueError):
            TextRepresentation.from_xml(create_element("wrong"))

    def test_variable_representation_wrong_tag(self):
        with pytest.raises(ValueError):
            VariableRepresentation.from_xml(create_element("wrong"))


# ── VariableRepresentation to_xml branches ───────────────────────────────


class TestVariableRepresentationToXml:
    def test_other_attributes(self):
        vr = VariableRepresentation(other_attributes={"foo": "bar"})
        xml = vr.to_xml()
        assert xml.get("foo") == "bar"

    def test_date_time_representation(self):
        vr = VariableRepresentation(
            date_time_representation=DateTimeRepresentation(date_type_code="Year")
        )
        xml = vr.to_xml()
        assert xml.find(qn(R, "DateTimeRepresentation")) is not None

    def test_text_representation(self):
        vr = VariableRepresentation(
            text_representation=TextRepresentation(blank_is_missing_value=True)
        )
        xml = vr.to_xml()
        assert xml.find(qn(R, "TextRepresentation")) is not None

    def test_missing_values_reference(self):
        ref = _make_ref()
        vr = VariableRepresentation(missing_values_reference=ref)
        xml = vr.to_xml()
        assert xml.find(qn(L, "MissingValuesReference")) is not None

    def test_other_elements(self):
        extra = _el(L, "CustomChild", "data")
        vr = VariableRepresentation(other_elements=[extra])
        xml = vr.to_xml()
        children = [c.tag for c in xml]
        assert qn(L, "CustomChild") in children


# ── CodeItem ─────────────────────────────────────────────────────────────


class TestCodeItem:
    def test_urn_serialization(self):
        ci = CodeItem(urn="urn:ddi:test:1", value="1")
        xml = ci.to_xml()
        assert xml.find(qn(R, "URN")).text == "urn:ddi:test:1"  # type: ignore[union-attr]

    def test_other_elements_serialization(self):
        extra = _el(R, "Extra", "x")
        ci = CodeItem(value="1", other_elements=[extra])
        xml = ci.to_xml()
        assert xml.find(qn(R, "Extra")) is not None

    def test_roundtrip_with_urn(self):
        el = create_element(qn(L, "Code"))
        el.append(_el(R, "URN", "urn:ddi:test:1"))
        el.append(_el(R, "Value", "A"))
        ci = CodeItem.from_xml(el)
        assert ci.urn == "urn:ddi:test:1"
        xml = ci.to_xml()
        assert xml.find(qn(R, "URN")).text == "urn:ddi:test:1"  # type: ignore[union-attr]


# ── CodeList to_xml branches ────────────────────────────────────────────


class TestCodeListToXml:
    def _make_codelist(self, **kwargs):
        defaults = dict(
            agency="ag",
            identifier="cl-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        defaults.update(kwargs)
        return CodeList(**defaults)  # type: ignore[arg-type]

    def test_code_list_references(self):
        cl = self._make_codelist(code_list_references=[_make_ref()])
        xml = cl.to_xml()
        assert xml.find(qn(R, "CodeListReference")) is not None

    def test_category_scheme_reference(self):
        cl = self._make_codelist(category_scheme_reference=_make_ref())
        xml = cl.to_xml()
        assert xml.find(qn(R, "CategorySchemeReference")) is not None

    def test_hierarchy_type(self):
        cl = self._make_codelist(hierarchy_type="Regular")
        xml = cl.to_xml()
        ht = xml.find(qn(L, "HierarchyType"))
        assert ht is not None and ht.text == "Regular"

    def test_levels(self):
        level_el = _el(L, "Level", "level1")
        cl = self._make_codelist(levels=[level_el])
        xml = cl.to_xml()
        assert xml.find(qn(L, "Level")) is not None


# ── Variable to_xml branches ────────────────────────────────────────────


class TestVariableToXml:
    def _make_variable(self, **kwargs):
        defaults = dict(
            agency="ag",
            identifier="var-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        defaults.update(kwargs)
        return Variable(**defaults)  # type: ignore[arg-type]

    def test_out_parameter(self):
        param = _el(L, "OutParameter")
        param.append(_el(R, "ID", "op-1"))
        v = self._make_variable(out_parameter=param)
        xml = v.to_xml()
        assert xml.find(qn(L, "OutParameter")) is not None

    def test_source_parameter_reference(self):
        v = self._make_variable(source_parameter_reference=_make_ref())
        xml = v.to_xml()
        assert xml.find(qn(R, "SourceParameterReference")) is not None

    def test_weighting_process_reference(self):
        v = self._make_variable(weighting_process_reference=_make_ref())
        xml = v.to_xml()
        assert xml.find(qn(L, "WeightingProcessReference")) is not None

    def test_measurement_references(self):
        v = self._make_variable(measurement_references=[_make_ref()])
        xml = v.to_xml()
        assert xml.find(qn(R, "MeasurementReference")) is not None

    def test_embargo_reference(self):
        v = self._make_variable(embargo_reference=_make_ref())
        xml = v.to_xml()
        assert xml.find(qn(L, "EmbargoReference")) is not None

    def test_source_unit(self):
        from ddi_l.models.base import CodeValue

        v = self._make_variable(source_unit=CodeValue(text="SU"))
        xml = v.to_xml()
        assert xml.find(qn(L, "SourceUnit")) is not None

    def test_analysis_unit(self):
        from ddi_l.models.base import CodeValue

        v = self._make_variable(analysis_unit=CodeValue(text="AU"))
        xml = v.to_xml()
        assert xml.find(qn(R, "AnalysisUnit")) is not None

    def test_unit_type_reference(self):
        v = self._make_variable(unit_type_reference=_make_ref())
        xml = v.to_xml()
        assert xml.find(qn(R, "UnitTypeReference")) is not None


# ── Category to_xml branches ────────────────────────────────────────────


class TestCategoryToXml:
    def _make_category(self, **kwargs):
        defaults = dict(
            agency="ag",
            identifier="cat-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        defaults.update(kwargs)
        return Category(**defaults)  # type: ignore[arg-type]

    def test_concept_reference(self):
        c = self._make_category(concept_reference=_make_ref())
        xml = c.to_xml()
        assert xml.find(qn(R, "ConceptReference")) is not None

    def test_generation(self):
        gen = _el(L, "Generation")
        gen.append(_el(L, "GenerationInstruction", "instr"))
        c = self._make_category(generation=gen)
        xml = c.to_xml()
        assert xml.find(qn(L, "Generation")) is not None

    def test_sub_category_references(self):
        c = self._make_category(sub_category_references=[_make_ref()])
        xml = c.to_xml()
        assert xml.find(qn(L, "SubCategoryReference")) is not None


# ── CategoryScheme from_xml / to_xml ────────────────────────────────────


class TestCategoryScheme:
    def _build_xml(self):
        el = create_element(qn(L, "CategoryScheme"))
        _add_id(el)
        name_el = _el(L, "CategorySchemeName")
        s = _el(R, "String", "Test Scheme")
        s.set(qn("http://www.w3.org/XML/1998/namespace", "lang"), "en")
        name_el.append(s)
        el.append(name_el)
        cat_el = create_element(qn(L, "Category"))
        _add_id(cat_el, ident="cat-1")
        el.append(cat_el)
        el.append(_ref_el("CategoryReference"))
        return el

    def test_from_xml(self):
        scheme = CategoryScheme.from_xml(self._build_xml())
        assert len(scheme.names) >= 1
        assert len(scheme.categories) == 1
        assert len(scheme.category_references) == 1

    def test_to_xml(self):
        scheme = CategoryScheme.from_xml(self._build_xml())
        xml = scheme.to_xml()
        assert xml.find(qn(L, "CategorySchemeName")) is not None
        assert xml.find(qn(L, "Category")) is not None
        assert xml.find(qn(R, "CategoryReference")) is not None


# ── CodeListScheme from_xml / to_xml ────────────────────────────────────


class TestCodeListScheme:
    def _build_xml(self):
        el = create_element(qn(L, "CodeListScheme"))
        _add_id(el)
        name_el = _el(L, "CodeListSchemeName")
        s = _el(R, "String", "CLS")
        s.set(qn("http://www.w3.org/XML/1998/namespace", "lang"), "en")
        name_el.append(s)
        el.append(name_el)
        cl_el = create_element(qn(L, "CodeList"))
        _add_id(cl_el, ident="cl-1")
        el.append(cl_el)
        el.append(_ref_el("CodeListReference"))
        return el

    def test_from_xml(self):
        scheme = CodeListScheme.from_xml(self._build_xml())
        assert len(scheme.code_lists) == 1
        assert len(scheme.code_list_references) == 1

    def test_to_xml(self):
        scheme = CodeListScheme.from_xml(self._build_xml())
        xml = scheme.to_xml()
        assert xml.find(qn(L, "CodeListSchemeName")) is not None
        assert xml.find(qn(L, "CodeList")) is not None


# ── VariableScheme from_xml / to_xml ────────────────────────────────────


class TestVariableScheme:
    def _build_xml(self):
        el = create_element(qn(L, "VariableScheme"))
        _add_id(el)
        name_el = _el(L, "VariableSchemeName")
        s = _el(R, "String", "VS")
        s.set(qn("http://www.w3.org/XML/1998/namespace", "lang"), "en")
        name_el.append(s)
        el.append(name_el)
        var_el = create_element(qn(L, "Variable"))
        _add_id(var_el, ident="v-1")
        el.append(var_el)
        el.append(_ref_el("VariableReference"))
        return el

    def test_from_xml(self):
        scheme = VariableScheme.from_xml(self._build_xml())
        assert len(scheme.variables) == 1
        assert len(scheme.variable_references) == 1

    def test_to_xml(self):
        scheme = VariableScheme.from_xml(self._build_xml())
        xml = scheme.to_xml()
        assert xml.find(qn(L, "VariableSchemeName")) is not None
        assert xml.find(qn(L, "Variable")) is not None


# ── RepresentedVariableScheme ────────────────────────────────────────────


class TestRepresentedVariableScheme:
    def _build_xml(self):
        el = create_element(qn(L, "RepresentedVariableScheme"))
        _add_id(el)
        name_el = _el(L, "RepresentedVariableSchemeName")
        s = _el(R, "String", "RVS")
        s.set(qn("http://www.w3.org/XML/1998/namespace", "lang"), "en")
        name_el.append(s)
        el.append(name_el)
        rv_el = create_element(qn(L, "RepresentedVariable"))
        _add_id(rv_el, ident="rv-1")
        el.append(rv_el)
        el.append(_ref_el("RepresentedVariableReference"))
        return el

    def test_from_xml(self):
        scheme = RepresentedVariableScheme.from_xml(self._build_xml())
        assert len(scheme.represented_variables) == 1
        assert len(scheme.represented_variable_references) == 1

    def test_to_xml(self):
        scheme = RepresentedVariableScheme.from_xml(self._build_xml())
        xml = scheme.to_xml()
        assert xml.find(qn(L, "RepresentedVariableSchemeName")) is not None
        assert xml.find(qn(L, "RepresentedVariable")) is not None


# ── RepresentedVariable ─────────────────────────────────────────────────


class TestRepresentedVariable:
    def _make_rv(self, **kwargs):
        defaults = dict(
            agency="ag",
            identifier="rv-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        defaults.update(kwargs)
        return RepresentedVariable(**defaults)  # type: ignore[arg-type]

    def test_from_xml_with_unit_type_and_concept(self):
        """When no ConceptualVariableReference, parse UnitType and Concept."""
        el = create_element(qn(L, "RepresentedVariable"))
        _add_id(el)
        el.append(_ref_el("UnitTypeReference"))
        el.append(_ref_el("ConceptReference"))
        rv = RepresentedVariable.from_xml(el)
        assert rv.unit_type_reference is not None
        assert rv.concept_reference is not None
        assert rv.conceptual_variable_reference is None

    def test_to_xml_with_conceptual_variable_reference(self):
        rv = self._make_rv(conceptual_variable_reference=_make_ref())
        xml = rv.to_xml()
        assert xml.find(qn(R, "ConceptualVariableReference")) is not None

    def test_to_xml_with_unit_type_and_concept(self):
        rv = self._make_rv(
            unit_type_reference=_make_ref(ident="ut-1"),
            concept_reference=_make_ref(ident="c-1"),
        )
        xml = rv.to_xml()
        assert xml.find(qn(R, "UnitTypeReference")) is not None
        assert xml.find(qn(R, "ConceptReference")) is not None

    def test_to_xml_is_missing(self):
        rv = self._make_rv(is_missing=True)
        xml = rv.to_xml()
        assert xml.get("isMissing") == "true"

    def test_to_xml_names(self):
        rv = self._make_rv(names=[InternationalString(lang="en", text="Test")])
        xml = rv.to_xml()
        assert xml.find(qn(L, "RepresentedVariableName")) is not None

    def test_to_xml_code_representation(self):
        rv = self._make_rv(
            code_representation=CodeRepresentation(blank_is_missing_value=False)
        )
        xml = rv.to_xml()
        assert xml.find(qn(R, "CodeRepresentation")) is not None

    def test_to_xml_date_time_representation(self):
        rv = self._make_rv(
            date_time_representation=DateTimeRepresentation(date_type_code="Year")
        )
        xml = rv.to_xml()
        assert xml.find(qn(R, "DateTimeRepresentation")) is not None

    def test_to_xml_text_representation(self):
        rv = self._make_rv(text_representation=TextRepresentation())
        xml = rv.to_xml()
        assert xml.find(qn(R, "TextRepresentation")) is not None

    def test_to_xml_suppresses_duplicate_refs(self):
        """other_elements containing ref tags already handled are suppressed."""
        extra = _ref_el("UnitTypeReference", ident="dup")
        rv = self._make_rv(
            unit_type_reference=_make_ref(ident="ut-1"),
            other_elements=[extra],
        )
        xml = rv.to_xml()
        # Only one UnitTypeReference (the primary one)
        refs = xml.findall(qn(R, "UnitTypeReference"))
        assert len(refs) == 1


# ── VariableGroup ────────────────────────────────────────────────────────


class TestVariableGroup:
    def _build_xml(self):
        el = create_element(qn(L, "VariableGroup"))
        _add_id(el)
        el.append(_el(R, "VersionResponsibility", "org"))
        vr = create_element(qn(R, "VersionRationale"))
        desc = create_element(qn(R, "RationaleDescription"))
        s = _el(R, "String", "Some change")
        s.set(qn("http://www.w3.org/XML/1998/namespace", "lang"), "en")
        desc.append(s)
        vr.append(desc)
        el.append(vr)
        el.append(_ref_el("VariableReference"))
        return el

    def test_from_xml_to_xml_roundtrip(self):
        vg = VariableGroup.from_xml(self._build_xml())
        assert vg.version_responsibility == "org"
        assert len(vg.version_rationales) == 1
        assert len(vg.variable_references) == 1
        xml = vg.to_xml()
        assert xml.find(qn(R, "VersionResponsibility")).text == "org"  # type: ignore[union-attr]
        assert xml.find(qn(R, "VariableReference")) is not None


# ── LogicalProduct ───────────────────────────────────────────────────────


class TestLogicalProductFromXml:
    def _build_lp_xml(self, include_repr_vars=False):
        el = create_element(qn(L, "LogicalProduct"))
        _add_id(el, ident="lp-1")
        # Name
        name_el = _el(L, "LogicalProductName")
        s = _el(R, "String", "Test LP")
        s.set(qn("http://www.w3.org/XML/1998/namespace", "lang"), "en")
        name_el.append(s)
        el.append(name_el)
        # CategoryScheme with inline categories
        cat_scheme = create_element(qn(L, "CategoryScheme"))
        cat_scheme.append(_el(R, "ID", "cs-1"))
        cat_scheme.append(_el(R, "Agency", "test.agency"))
        cat_scheme.append(_el(R, "Version", "1.0.0"))
        cat_el = create_element(qn(L, "Category"))
        _add_id(cat_el, ident="cat-1")
        cat_scheme.append(cat_el)
        el.append(cat_scheme)
        # VariableScheme with inline variables
        var_scheme = create_element(qn(L, "VariableScheme"))
        var_scheme.append(_el(R, "ID", "vs-1"))
        var_scheme.append(_el(R, "Agency", "test.agency"))
        var_scheme.append(_el(R, "Version", "1.0.0"))
        var_el = create_element(qn(L, "Variable"))
        _add_id(var_el, ident="var-1")
        var_scheme.append(var_el)
        el.append(var_scheme)
        # CodeListScheme
        cl_scheme = create_element(qn(L, "CodeListScheme"))
        cl_scheme.append(_el(R, "ID", "cls-1"))
        cl_scheme.append(_el(R, "Agency", "test.agency"))
        cl_scheme.append(_el(R, "Version", "1.0.0"))
        cl_el = create_element(qn(L, "CodeList"))
        _add_id(cl_el, ident="cl-1")
        cl_scheme.append(cl_el)
        el.append(cl_scheme)
        if include_repr_vars:
            rv_scheme = create_element(qn(L, "RepresentedVariableScheme"))
            rv_scheme.append(_el(R, "ID", "rvs-1"))
            rv_scheme.append(_el(R, "Agency", "test.agency"))
            rv_scheme.append(_el(R, "Version", "1.0.0"))
            rv_el = create_element(qn(L, "RepresentedVariable"))
            _add_id(rv_el, ident="rv-1")
            rv_scheme.append(rv_el)
            el.append(rv_scheme)
        return el

    def test_from_xml_inline_schemes(self):
        lp = LogicalProduct.from_xml(self._build_lp_xml(include_repr_vars=True))
        assert len(lp.categories) == 1
        assert len(lp.variables) == 1
        assert len(lp.code_lists) == 1
        assert len(lp.represented_variables) == 1
        assert len(lp.names) >= 1

    def test_to_xml_full(self):
        lp = LogicalProduct.from_xml(self._build_lp_xml(include_repr_vars=True))
        xml = lp.to_xml()
        assert xml.find(qn(L, "LogicalProductName")) is not None
        assert xml.find(qn(L, "CategoryScheme")) is not None
        assert xml.find(qn(L, "VariableScheme")) is not None
        assert xml.find(qn(L, "CodeListScheme")) is not None
        assert xml.find(qn(L, "RepresentedVariableScheme")) is not None


class TestLogicalProductToXmlBranches:
    def _make_lp(self, **kwargs):
        defaults = dict(
            agency="ag",
            identifier="lp-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        defaults.update(kwargs)
        return LogicalProduct(**defaults)  # type: ignore[arg-type]

    def test_names(self):
        lp = self._make_lp(
            names=[InternationalString(lang="en", text="LP")],
            categories=[
                Category(
                    agency="ag",
                    identifier="c-1",
                    version="1.0.0",
                    labels=[],
                    descriptions=[],
                    other_elements=[],
                )
            ],
        )
        xml = lp.to_xml()
        assert xml.find(qn(L, "LogicalProductName")) is not None

    def test_coverage(self):
        cov = _el(R, "Coverage")
        cov.append(_el(R, "TopicalCoverage"))
        lp = self._make_lp(
            coverage=[cov],
            categories=[
                Category(
                    agency="ag",
                    identifier="c-1",
                    version="1.0.0",
                    labels=[],
                    descriptions=[],
                    other_elements=[],
                )
            ],
        )
        xml = lp.to_xml()
        assert xml.find(qn(R, "Coverage")) is not None

    def test_data_relationship_references(self):
        lp = self._make_lp(
            data_relationship_references=[_make_ref()],
            categories=[
                Category(
                    agency="ag",
                    identifier="c-1",
                    version="1.0.0",
                    labels=[],
                    descriptions=[],
                    other_elements=[],
                )
            ],
        )
        xml = lp.to_xml()
        assert xml.find(qn(R, "DataRelationshipReference")) is not None

    def test_scheme_references(self):
        lp = self._make_lp(
            category_scheme_references=[_make_ref(ident="csr")],
            code_list_scheme_references=[_make_ref(ident="clsr")],
            managed_representation_scheme_references=[_make_ref(ident="mrsr")],
            represented_variable_scheme_references=[_make_ref(ident="rvsr")],
            variable_scheme_references=[_make_ref(ident="vsr")],
            n_cube_scheme_references=[_make_ref(ident="ncsr")],
        )
        xml = lp.to_xml()
        assert xml.find(qn(R, "CategorySchemeReference")) is not None
        assert xml.find(qn(R, "CodeListSchemeReference")) is not None
        assert xml.find(qn(R, "ManagedRepresentationSchemeReference")) is not None
        assert xml.find(qn(R, "RepresentedVariableSchemeReference")) is not None
        assert xml.find(qn(R, "VariableSchemeReference")) is not None
        assert xml.find(qn(R, "NCubeSchemeReference")) is not None


# ── Iterators ────────────────────────────────────────────────────────────


class TestLogicalProductIterators:
    def _make_lp_with_content(self):
        cat = Category(
            agency="ag",
            identifier="cat-1",
            version="1.0.0",
            urn="urn:cat:1",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        var = Variable(
            agency="ag",
            identifier="var-1",
            version="1.0.0",
            urn="urn:var:1",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        cl = CodeList(
            agency="ag",
            identifier="cl-1",
            version="1.0.0",
            urn="urn:cl:1",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        rv = RepresentedVariable(
            agency="ag",
            identifier="rv-1",
            version="1.0.0",
            urn="urn:rv:1",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        return LogicalProduct(
            agency="ag",
            identifier="lp-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            categories=[cat],
            variables=[var],
            code_lists=[cl],
            represented_variables=[rv],
        )

    def test_iter_categories_no_filter(self):
        lp = self._make_lp_with_content()
        assert len(list(lp.iter_categories())) == 1

    def test_iter_categories_by_identifier(self):
        lp = self._make_lp_with_content()
        assert len(list(lp.iter_categories(identifier="cat-1"))) == 1
        assert len(list(lp.iter_categories(identifier="nonexistent"))) == 0

    def test_iter_categories_by_urn(self):
        lp = self._make_lp_with_content()
        assert len(list(lp.iter_categories(urn="urn:cat:1"))) == 1
        assert len(list(lp.iter_categories(urn="urn:nope"))) == 0

    def test_iter_categories_by_scheme_identifier(self):
        lp = self._make_lp_with_content()
        # Default scheme gets auto-generated identifier
        schemes = lp._ensure_category_schemes()
        sid = schemes[0].identifier
        assert len(list(lp.iter_categories(scheme_identifier=sid))) == 1
        assert len(list(lp.iter_categories(scheme_identifier="nope"))) == 0

    def test_iter_categories_by_scheme_urn(self):
        lp = self._make_lp_with_content()
        assert len(list(lp.iter_categories(scheme_urn="nope"))) == 0

    def test_iter_variables_filters(self):
        lp = self._make_lp_with_content()
        assert len(list(lp.iter_variables())) == 1
        assert len(list(lp.iter_variables(identifier="var-1"))) == 1
        assert len(list(lp.iter_variables(urn="urn:var:1"))) == 1
        assert len(list(lp.iter_variables(urn="nope"))) == 0
        assert len(list(lp.iter_variables(scheme_urn="nope"))) == 0

    def test_iter_code_lists_filters(self):
        lp = self._make_lp_with_content()
        assert len(list(lp.iter_code_lists())) == 1
        assert len(list(lp.iter_code_lists(identifier="cl-1"))) == 1
        assert len(list(lp.iter_code_lists(urn="urn:cl:1"))) == 1
        assert len(list(lp.iter_code_lists(urn="nope"))) == 0
        assert len(list(lp.iter_code_lists(scheme_urn="nope"))) == 0

    def test_iter_represented_variables_filters(self):
        lp = self._make_lp_with_content()
        assert len(list(lp.iter_represented_variables())) == 1
        assert len(list(lp.iter_represented_variables(identifier="rv-1"))) == 1
        assert len(list(lp.iter_represented_variables(urn="urn:rv:1"))) == 1
        assert len(list(lp.iter_represented_variables(urn="nope"))) == 0
        assert len(list(lp.iter_represented_variables(scheme_urn="nope"))) == 0


class TestLogicalProductEnsureSchemes:
    def test_ensure_represented_variable_schemes_creates_default(self):
        rv = RepresentedVariable(
            agency="ag",
            identifier="rv-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        lp = LogicalProduct(
            agency="ag",
            identifier="lp-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            represented_variables=[rv],
        )
        schemes = lp._ensure_represented_variable_schemes()
        assert len(schemes) == 1
        assert len(schemes[0].members) == 1

    def test_populate_scheme_defaults_sets_agency_version(self):
        cat = Category(
            agency="ag",
            identifier="c-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        lp = LogicalProduct(
            agency="my-agency",
            identifier="lp-1",
            version="2.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            categories=[cat],
        )
        schemes = lp._ensure_category_schemes()
        assert schemes[0].agency == "my-agency"
        assert schemes[0].version == "2.0.0"

    def test_default_inline_identifier_no_prefix(self):
        lp = LogicalProduct(
            agency="ag",
            identifier=None,
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        result = lp._default_inline_identifier("suffix", 1)
        assert result is None

    def test_default_inline_identifier_with_index(self):
        lp = LogicalProduct(
            agency="ag",
            identifier="lp-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        r1 = lp._default_inline_identifier("scheme", 1)
        r2 = lp._default_inline_identifier("scheme", 2)
        assert r1 is not None
        assert r2 is not None
        assert r1 != r2


class TestLogicalProductValidation:
    def test_validate_empty_raises(self):
        from ddi_l.exceptions import ModelValidationError

        lp = LogicalProduct(
            agency="ag",
            identifier="lp-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        with pytest.raises(ModelValidationError):
            lp.validate()
