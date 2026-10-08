"""Edge cases and error paths in study, conceptualcomponent, group, methodology, dissemination."""

from __future__ import annotations

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import (
    CONCEPTUAL_COMPONENT_NS as CC,
)
from ddi_l.constants import (
    DATA_COLLECTION_NS as DC,
)
from ddi_l.constants import (
    REUSABLE_NS as R,
)
from ddi_l.constants import (
    STUDY_UNIT_NS as S,
)
from ddi_l.models.base import (
    CodeValue,
    InternationalString,
    Reference,
    UserAttributePair,
    UserID,
    VersionRationale,
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


def _make_ref(ident="ref-1"):
    return Reference(agency="ag", identifier=ident, version="1.0.0")


# ============================================================================
# StudyUnit tests
# ============================================================================


class TestStudyUnitToXml:
    """Cover lines 399-504 in study.py — to_xml() optional branches."""

    def _make_study(self, **kwargs):
        from ddi_l.models.study import StudyUnit

        defaults = dict(
            agency="ag",
            identifier="su-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            data_collection_references=[_make_ref("dc-default")],
        )
        defaults.update(kwargs)
        return StudyUnit(**defaults)  # type: ignore[arg-type]

    def test_user_ids(self):
        su = self._make_study(user_ids=[UserID(value="uid1", type_of_user_id="ISNI")])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "UserID")) is not None

    def test_user_attribute_pairs(self):
        su = self._make_study(
            user_attribute_pairs=[UserAttributePair(key="k", value="v")]
        )
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "UserAttributePair")) is not None

    def test_version_responsibility(self):
        su = self._make_study(version_responsibility="org")
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "VersionResponsibility")).text == "org"

    def test_version_rationales(self):
        vr = VersionRationale(
            descriptions=[InternationalString(text="changed", lang="en")]
        )
        su = self._make_study(version_rationales=[vr])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "VersionRationale")) is not None

    def test_type_of_study_unit(self):
        su = self._make_study(type_of_study_unit=CodeValue(text="CrossSection"))
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(S, "TypeOfStudyUnit")) is not None

    def test_citations(self):
        citation = _el(R, "Citation")
        citation.append(_el(R, "Title", "My Study"))
        su = self._make_study(citations=[citation])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "Citation")) is not None

    def test_abstracts(self):
        su = self._make_study(
            abstracts=[InternationalString(text="Abstract text", lang="en")]
        )
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "Abstract")) is not None

    def test_authorization_sources(self):
        auth = _el(R, "AuthorizationSource")
        su = self._make_study(authorization_sources=[auth])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "AuthorizationSource")) is not None

    def test_series_statements(self):
        series = _el(R, "SeriesStatement")
        su = self._make_study(series_statements=[series])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "SeriesStatement")) is not None

    def test_quality_references(self):
        su = self._make_study(
            quality_statement_references=[_make_ref("qs1")],
            quality_scheme_references=[_make_ref("qsch1")],
        )
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "QualityStatementReference")) is not None
        assert xml.find(qn(R, "QualitySchemeReference")) is not None

    def test_universe_references(self):
        su = self._make_study(universe_references=[_make_ref("u1")])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "UniverseReference")) is not None

    def test_funding_information(self):
        fund = _el(R, "FundingInformation")
        su = self._make_study(funding_information=[fund])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "FundingInformation")) is not None

    def test_purposes(self):
        su = self._make_study(
            purposes=[InternationalString(text="Purpose text", lang="en")]
        )
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "Purpose")) is not None

    def test_coverage(self):
        cov = _el(R, "Coverage")
        su = self._make_study(coverage=[cov])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "Coverage")) is not None

    def test_analysis_units(self):
        su = self._make_study(analysis_units=[CodeValue(text="Individual")])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "AnalysisUnit")) is not None

    def test_kind_of_data(self):
        kind = _el(R, "KindOfData", "Survey")
        su = self._make_study(kind_of_data=[kind])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "KindOfData")) is not None

    def test_general_data_formats(self):
        su = self._make_study(general_data_formats=[CodeValue(text="CSV")])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "GeneralDataFormat")) is not None

    def test_embargos(self):
        embargo = _el(R, "Embargo")
        su = self._make_study(embargos=[embargo])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "Embargo")) is not None

    def test_required_resource_packages(self):
        pkg = _el(R, "RequiredResourcePackages")
        su = self._make_study(required_resource_packages=[pkg])
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "RequiredResourcePackages")) is not None

    def test_component_references(self):
        su = self._make_study(
            conceptual_component_references=[_make_ref("cc1")],
            data_collection_references=[_make_ref("dc1")],
            logical_product_references=[_make_ref("lp1")],
            physical_data_product_references=[_make_ref("pdp1")],
            physical_instance_references=[_make_ref("pi1")],
            archive_references=[_make_ref("ar1")],
        )
        xml = su.to_xml(validate_refs=False)
        assert xml.find(qn(R, "ConceptualComponentReference")) is not None
        assert xml.find(qn(R, "DataCollectionReference")) is not None
        assert xml.find(qn(R, "LogicalProductReference")) is not None
        assert xml.find(qn(R, "PhysicalDataProductReference")) is not None
        assert xml.find(qn(R, "PhysicalInstanceReference")) is not None
        assert xml.find(qn(R, "ArchiveReference")) is not None


class TestStudyUnitNsmap:
    """Cover line 399-408 — _nsmap override logic."""

    def test_nsmap_default_namespace_via_from_xml(self):
        """Build StudyUnit from XML that uses default namespace to hit _nsmap."""
        from ddi_l.models.study import StudyUnit

        el = create_element(qn(S, "StudyUnit"))
        el.set("xmlns", S)
        el.append(_el(R, "Agency", "ag"))
        el.append(_el(R, "ID", "su-1"))
        el.append(_el(R, "Version", "1.0.0"))
        # Use a reference instead of inline DataCollection

        dc_ref = create_element(qn(R, "DataCollectionReference"))
        dc_ref.append(_el(R, "ID", "dc-1"))
        el.append(dc_ref)
        su = StudyUnit.from_xml(el)
        xml = su.to_xml(validate_refs=False)
        assert xml.tag == qn(S, "StudyUnit")


class TestStudyUnitQueryMethods:
    """Cover lines 573, 601, 649, 701+ — get_dataset, get_variables, etc."""

    def _make_study_with_data(self):
        from ddi_l.models.logicalproduct import (
            Category,
            LogicalProduct,
            Variable,
        )
        from ddi_l.models.physical import PhysicalStructure
        from ddi_l.models.study import StudyUnit

        var = Variable(
            agency="ag",
            identifier="v1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        cat = Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        lp = LogicalProduct(
            agency="ag",
            identifier="lp1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            categories=[cat],
            variables=[var],
        )
        ps = PhysicalStructure(
            agency="ag",
            identifier="ps1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        return StudyUnit(
            agency="ag",
            identifier="su1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            logical_products=[lp],
            physical_structures=[ps],
        )

    def test_get_dataset_found(self):
        su = self._make_study_with_data()
        ds = su.get_dataset("ps1")
        assert ds is not None and ds.identifier == "ps1"

    def test_get_dataset_not_found(self):
        su = self._make_study_with_data()
        assert su.get_dataset("nope") is None

    def test_get_variables(self):
        su = self._make_study_with_data()
        variables = su.get_variables()
        assert len(variables) == 1
        assert variables[0].identifier == "v1"

    def test_get_datasets(self):
        su = self._make_study_with_data()
        datasets = su.get_datasets()
        assert len(datasets) == 1

    def test_iter_data_collections_filter(self):
        from ddi_l.models.study import StudyUnit

        su = StudyUnit(
            agency="ag",
            identifier="su1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        result = list(su.iter_data_collections(urn="urn:nope"))
        assert result == []


# ============================================================================
# ConceptualComponent tests
# ============================================================================


class TestConceptualComponentToXml:
    """Cover lines 168, 208-285 — scheme wrapping and inline children."""

    def test_to_xml_inline_only_raises(self):
        from ddi_l.models.conceptualcomponent import ConceptualComponent

        cc = ConceptualComponent(
            agency="ag",
            identifier="cc1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            inline_only=True,
        )
        with pytest.raises(ValueError):
            cc.to_xml()

    def test_to_xml_without_schemes(self):
        from ddi_l.models.concept import Concept, Universe
        from ddi_l.models.conceptualcomponent import ConceptualComponent

        concept = Concept(
            agency="ag",
            identifier="con1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        universe = Universe(
            agency="ag",
            identifier="uni1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        cc = ConceptualComponent(
            agency="ag",
            identifier="cc1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            concepts=[concept],
            universes=[universe],
            has_concept_scheme=False,
            has_universe_scheme=False,
        )
        xml = cc.to_xml()
        # Concepts and universes should be inline, not in scheme wrappers
        assert xml.find(qn(CC, "ConceptScheme")) is None
        assert xml.find(qn(CC, "Concept")) is not None

    def test_to_xml_with_schemes(self):
        from ddi_l.models.concept import Concept, Universe
        from ddi_l.models.conceptualcomponent import ConceptualComponent

        concept = Concept(
            agency="ag",
            identifier="con1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        universe = Universe(
            agency="ag",
            identifier="uni1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        cc = ConceptualComponent(
            agency="ag",
            identifier="cc1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            concepts=[concept],
            universes=[universe],
            has_concept_scheme=True,
            has_universe_scheme=True,
        )
        xml = cc.to_xml()
        assert xml.find(qn(CC, "ConceptScheme")) is not None
        assert xml.find(qn(CC, "UniverseScheme")) is not None

    def test_to_xml_scheme_references(self):
        from ddi_l.models.conceptualcomponent import ConceptualComponent

        cc = ConceptualComponent(
            agency="ag",
            identifier="cc1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            concept_scheme_references=[_make_ref("csr")],
            universe_scheme_references=[_make_ref("usr")],
            conceptual_variable_scheme_references=[_make_ref("cvsr")],
            unit_type_scheme_references=[_make_ref("utsr")],
            geographic_location_scheme_references=[_make_ref("glsr")],
            geographic_structure_scheme_references=[_make_ref("gssr")],
        )
        xml = cc.to_xml()
        assert xml.find(qn(R, "ConceptSchemeReference")) is not None
        assert xml.find(qn(R, "UniverseSchemeReference")) is not None
        assert xml.find(qn(R, "ConceptualVariableSchemeReference")) is not None
        assert xml.find(qn(R, "UnitTypeSchemeReference")) is not None
        assert xml.find(qn(R, "GeographicLocationSchemeReference")) is not None
        assert xml.find(qn(R, "GeographicStructureSchemeReference")) is not None

    def test_append_inline_children(self):
        from ddi_l.models.concept import Concept, Universe
        from ddi_l.models.conceptualcomponent import ConceptualComponent

        concept = Concept(
            agency="ag",
            identifier="con1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        universe = Universe(
            agency="ag",
            identifier="uni1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        cc = ConceptualComponent(
            agency="ag",
            identifier="cc1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            concepts=[concept],
            universes=[universe],
            inline_only=True,
            has_concept_scheme=True,
            has_universe_scheme=True,
        )
        parent = create_element("root")
        cc.append_inline_children(parent)
        assert parent.find(qn(CC, "ConceptScheme")) is not None
        assert parent.find(qn(CC, "UniverseScheme")) is not None

    def test_append_inline_without_scheme(self):
        from ddi_l.models.concept import Concept
        from ddi_l.models.conceptualcomponent import ConceptualComponent

        concept = Concept(
            agency="ag",
            identifier="con1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        cc = ConceptualComponent(
            agency="ag",
            identifier="cc1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            concepts=[concept],
            inline_only=True,
            has_concept_scheme=False,
        )
        parent = create_element("root")
        cc.append_inline_children(parent)
        assert parent.find(qn(CC, "ConceptScheme")) is None
        assert parent.find(qn(CC, "Concept")) is not None


class TestConceptualComponentFromXml:
    """Cover lines 113, 121 — inline conceptual_variables and unit_types."""

    def test_from_xml_with_inline_items(self):
        from ddi_l.models.conceptualcomponent import ConceptualComponent

        el = create_element(qn(CC, "ConceptualComponent"))
        el.append(_el(R, "Agency", "ag"))
        el.append(_el(R, "ID", "cc1"))
        el.append(_el(R, "Version", "1.0.0"))
        # Add inline ConceptualVariable
        cv = create_element(qn(CC, "ConceptualVariable"))
        cv.append(_el(R, "Agency", "ag"))
        cv.append(_el(R, "ID", "cv1"))
        cv.append(_el(R, "Version", "1.0.0"))
        el.append(cv)
        # Add inline UnitType
        ut = create_element(qn(CC, "UnitType"))
        ut.append(_el(R, "Agency", "ag"))
        ut.append(_el(R, "ID", "ut1"))
        ut.append(_el(R, "Version", "1.0.0"))
        el.append(ut)
        cc = ConceptualComponent.from_xml(el)
        assert len(cc.conceptual_variables) == 1
        assert len(cc.unit_types) == 1


# ============================================================================
# Group ResourcePackage tests
# ============================================================================


class TestGroupToXml:
    """Cover lines 149-189, 270-274 in group.py."""

    def test_to_xml_with_metadata(self):
        from ddi_l.models.group import Group

        grp = Group(
            agency="ag",
            identifier="g1",
            version="1.0.0",
            labels=[InternationalString(text="Label", lang="en")],
            descriptions=[InternationalString(text="Desc", lang="en")],
            other_elements=[],
            citation=_el(R, "Citation"),
            coverage=_el(R, "Coverage"),
            funding_informations=[_el(R, "FundingInformation")],
            data_collection_references=[_make_ref("dc1")],
            study_unit_references=[_make_ref("su1")],
            group_references=[_make_ref("g2")],
        )
        xml = grp.to_xml()
        assert xml.find(qn(R, "Citation")) is not None
        assert xml.find(qn(R, "Coverage")) is not None
        assert xml.find(qn(R, "FundingInformation")) is not None
        assert xml.find(qn(R, "DataCollectionReference")) is not None
        assert xml.find(qn(R, "StudyUnitReference")) is not None
        assert xml.find(qn(R, "GroupReference")) is not None


# ============================================================================
# Methodology tests
# ============================================================================


class TestMethodology:
    """Cover lines 45-47, 127, 129, 209-210 in methodology.py."""

    def test_methodology_roundtrips_into_the_schema_namespace(self):
        """Methodology is read from either spelling and always written as DDI's.

        DDI 3.3 declares ``<Methodology>`` in ``ddi:datacollection:3_3``. The
        library used to emit it in a namespace of its own, so opening a valid
        file and saving it produced a document no DDI tool could read. Input in
        the old spelling is still accepted so existing files keep loading.
        """
        from ddi_l.constants import DATA_COLLECTION_NS, METHODOLOGY_NS
        from ddi_l.models.methodology import Methodology

        for source_namespace in (METHODOLOGY_NS, DATA_COLLECTION_NS):
            el = create_element(qn(source_namespace, "Methodology"))
            el.append(_el(R, "Agency", "ag"))
            el.append(_el(R, "ID", "m1"))
            el.append(_el(R, "Version", "1.0.0"))

            meth = Methodology.from_xml(el)

            assert meth.identifier == "m1"
            assert meth.to_xml().tag == qn(DATA_COLLECTION_NS, "Methodology")


# ============================================================================
# Dissemination tests
# ============================================================================


class TestDisseminationUsageGuide:
    """Cover lines 487-628 in dissemination.py."""

    def test_usage_guide_roundtrip(self):
        from ddi_l.models.dissemination import UsageGuide

        el = create_element(qn(DC, "UsageGuide"))
        # Add usage example
        example_container = create_element(qn(DC, "UsageExample"))
        s = _el(R, "String", "Example text")
        example_container.append(s)
        el.append(example_container)
        # Add usage restriction
        restriction_container = create_element(qn(DC, "UsageRestrictions"))
        s2 = _el(R, "String", "Restriction text")
        restriction_container.append(s2)
        el.append(restriction_container)
        ug = UsageGuide.from_xml(el)
        assert len(ug.examples) >= 1
        xml = ug.to_xml()
        assert xml.tag == qn(DC, "UsageGuide")


class TestDisseminationStandardWeight:
    """Cover lines 591-628 in dissemination.py."""

    def test_standard_weight_roundtrip(self):
        from ddi_l.models.dissemination import StandardWeight

        el = create_element(qn(DC, "StandardWeight"))
        el.append(_el(R, "Agency", "ag"))
        el.append(_el(R, "ID", "sw1"))
        el.append(_el(R, "Version", "1.0.0"))
        sw_val = _el(DC, "StandardWeightValue", "0.75")
        el.append(sw_val)
        sw = StandardWeight.from_xml(el)
        assert sw.standard_weight_value == pytest.approx(0.75)
        xml = sw.to_xml()
        val_el = xml.find(qn(DC, "StandardWeightValue"))
        assert val_el is not None
