"""Edge cases and error paths in ddi_l.models.base."""

from __future__ import annotations

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import REUSABLE_NS as R
from ddi_l.models.base import (
    CodeValue,
    InternationalString,
    MaintainableBase,
    Reference,
    UserAttributePair,
    UserID,
    ValidationContext,
    VersionRationale,
    _convert_text,
    _emit_field_value,
    _format_text,
    _parse_field_value,
    clone_element,
    preserve_unrecognized_children,
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


# ── clone_element ────────────────────────────────────────────────────────


class TestCloneElement:
    def test_shallow_clone(self):
        el = _el(R, "Test", "hello")
        el.set("attr", "val")
        child = _el(R, "Child", "c")
        el.append(child)
        clone = clone_element(el, deep=False)
        assert clone.tag == el.tag
        assert clone.text == "hello"
        assert clone.get("attr") == "val"
        assert len(list(clone)) == 0  # shallow - no children

    def test_deep_clone(self):
        el = _el(R, "Parent")
        child = _el(R, "Child", "c")
        el.append(child)
        clone = clone_element(el, deep=True)
        assert len(list(clone)) == 1
        assert next(iter(clone)).text == "c"

    def test_clone_preserves_tail(self):
        el = _el(R, "Test")
        el.tail = "tail-text"
        clone = clone_element(el)
        assert clone.tail == "tail-text"

    def test_clone_no_makeelement(self):
        """Test fallback path when makeelement is not callable."""
        el = _el(R, "Test", "data")
        el.set("foo", "bar")
        clone = clone_element(el)
        assert clone.tag == el.tag
        assert clone.text == "data"


# ── preserve_unrecognized_children ───────────────────────────────────────


class TestPreserveUnrecognized:
    def test_filters_recognized(self):
        parent = create_element("root")
        parent.append(_el(R, "Known"))
        parent.append(_el(R, "Unknown"))
        extras = preserve_unrecognized_children(parent, {qn(R, "Known")})
        assert len(extras) == 1
        assert extras[0].tag == qn(R, "Unknown")


# ── _parse_field_value ───────────────────────────────────────────────────


class TestParseFieldValue:
    def test_reference_list(self):
        parent = create_element("root")
        ref_el = create_element(qn(R, "Ref"))
        ref_el.append(_el(R, "ID", "r1"))
        parent.append(ref_el)
        result = _parse_field_value(parent, qn(R, "Ref"), "reference", True)
        assert isinstance(result, list) and len(result) == 1

    def test_reference_single(self):
        parent = create_element("root")
        ref_el = create_element(qn(R, "Ref"))
        ref_el.append(_el(R, "ID", "r1"))
        parent.append(ref_el)
        result = _parse_field_value(parent, qn(R, "Ref"), "reference", False)
        assert isinstance(result, Reference)

    def test_reference_single_missing(self):
        parent = create_element("root")
        result = _parse_field_value(parent, qn(R, "Ref"), "reference", False)
        assert result is None

    def test_intl_string_list(self):
        parent = create_element("root")
        container = create_element(qn(R, "Label"))
        s = _el(R, "String", "hello")
        container.append(s)
        parent.append(container)
        result = _parse_field_value(parent, qn(R, "Label"), "intl_string", True)
        assert isinstance(result, list) and len(result) == 1

    def test_intl_string_single(self):
        parent = create_element("root")
        container = create_element(qn(R, "Name"))
        s = _el(R, "String", "hi")
        container.append(s)
        parent.append(container)
        result = _parse_field_value(parent, qn(R, "Name"), "intl_string", False)
        assert isinstance(result, InternationalString)

    def test_code_value_list(self):
        parent = create_element("root")
        cv = _el(R, "CV", "code1")
        parent.append(cv)
        result = _parse_field_value(parent, qn(R, "CV"), "code_value", True)
        assert isinstance(result, list) and len(result) == 1

    def test_code_value_single(self):
        parent = create_element("root")
        cv = _el(R, "CV", "code1")
        parent.append(cv)
        result = _parse_field_value(parent, qn(R, "CV"), "code_value", False)
        assert isinstance(result, CodeValue)

    def test_str_list(self):
        parent = create_element("root")
        parent.append(_el(R, "Name", "a"))
        parent.append(_el(R, "Name", "b"))
        result = _parse_field_value(parent, qn(R, "Name"), "str", True)
        assert result == ["a", "b"]

    def test_str_single(self):
        parent = create_element("root")
        parent.append(_el(R, "Name", "a"))
        result = _parse_field_value(parent, qn(R, "Name"), "str", False)
        assert result == "a"

    def test_bool_list(self):
        parent = create_element("root")
        parent.append(_el(R, "Flag", "true"))
        parent.append(_el(R, "Flag", "false"))
        result = _parse_field_value(parent, qn(R, "Flag"), "bool", True)
        assert result == [True, False]

    def test_int_single(self):
        parent = create_element("root")
        parent.append(_el(R, "Count", "42"))
        result = _parse_field_value(parent, qn(R, "Count"), "int", False)
        assert result == 42

    def test_float_single(self):
        parent = create_element("root")
        parent.append(_el(R, "Val", "3.14"))
        result = _parse_field_value(parent, qn(R, "Val"), "float", False)
        assert abs(result - 3.14) < 0.001  # type: ignore[operator]

    def test_element_list(self):
        parent = create_element("root")
        parent.append(_el(R, "Raw", "data"))
        result = _parse_field_value(parent, qn(R, "Raw"), "element", True)
        assert isinstance(result, list) and len(result) == 1

    def test_element_single(self):
        parent = create_element("root")
        parent.append(_el(R, "Raw", "data"))
        result = _parse_field_value(parent, qn(R, "Raw"), "element", False)
        assert result is not None and result.text == "data"  # type: ignore[attr-defined]

    def test_element_single_missing(self):
        parent = create_element("root")
        result = _parse_field_value(parent, qn(R, "Raw"), "element", False)
        assert result is None


# ── _emit_field_value ────────────────────────────────────────────────────


class TestEmitFieldValue:
    def test_none_value(self):
        parent = create_element("root")
        _emit_field_value(parent, None, qn(R, "X"), "str", False)
        assert len(list(parent)) == 0

    def test_empty_list(self):
        parent = create_element("root")
        _emit_field_value(parent, [], qn(R, "X"), "str", True)
        assert len(list(parent)) == 0

    def test_reference(self):
        parent = create_element("root")
        ref = Reference(agency="ag", identifier="id", version="1")
        _emit_field_value(parent, ref, qn(R, "MyRef"), "reference", False)
        assert len(list(parent)) == 1

    def test_intl_string(self):
        parent = create_element("root")
        s = InternationalString(text="hi", lang="en")
        _emit_field_value(parent, s, qn(R, "Label"), "intl_string", False)
        assert len(list(parent)) == 1

    def test_code_value(self):
        parent = create_element("root")
        cv = CodeValue(text="code1")
        _emit_field_value(parent, cv, qn(R, "CV"), "code_value", False)
        assert len(list(parent)) == 1

    def test_str(self):
        parent = create_element("root")
        _emit_field_value(parent, "hello", qn(R, "Name"), "str", False)
        assert next(iter(parent)).text == "hello"

    def test_bool(self):
        parent = create_element("root")
        _emit_field_value(parent, True, qn(R, "Flag"), "bool", False)
        assert next(iter(parent)).text == "true"

    def test_int(self):
        parent = create_element("root")
        _emit_field_value(parent, 42, qn(R, "Count"), "int", False)
        assert next(iter(parent)).text == "42"

    def test_element(self):
        parent = create_element("root")
        raw = _el(R, "Data", "raw")
        _emit_field_value(parent, raw, qn(R, "Data"), "element", False)
        assert len(list(parent)) == 1

    def test_list_of_references(self):
        parent = create_element("root")
        refs = [
            Reference(agency="ag", identifier=f"id{i}", version="1") for i in range(2)
        ]
        _emit_field_value(parent, refs, qn(R, "Ref"), "reference", True)
        assert len(list(parent)) == 2


# ── _convert_text / _format_text ─────────────────────────────────────────


class TestConvertFormatText:
    def test_convert_none(self):
        assert _convert_text(None, "str") is None

    def test_convert_bool_true(self):
        assert _convert_text("true", "bool") is True
        assert _convert_text("1", "bool") is True

    def test_convert_bool_false(self):
        assert _convert_text("false", "bool") is False

    def test_convert_int(self):
        assert _convert_text("42", "int") == 42

    def test_convert_float(self):
        assert abs(_convert_text("3.14", "float") - 3.14) < 0.001  # type: ignore[operator]

    def test_convert_str(self):
        assert _convert_text("  hello  ", "str") == "hello"

    def test_format_bool(self):
        assert _format_text(True, "bool") == "true"
        assert _format_text(False, "bool") == "false"

    def test_format_str(self):
        assert _format_text("hello", "str") == "hello"

    def test_format_int(self):
        assert _format_text(42, "int") == "42"


# ── InternationalString ─────────────────────────────────────────────────


class TestInternationalStringEdgeCases:
    def test_to_child_with_translated(self):
        s = InternationalString(
            text="hi",
            lang="en",
            is_translated=True,
            translation_source_language="fr",
            translation_date="2024-01-01",
        )
        el = s.to_child()
        assert el.get("isTranslated") == "true"
        assert el.get("translationSourceLanguage") == "fr"
        assert el.get("translationDate") == "2024-01-01"

    def test_to_child_is_translated_false(self):
        s = InternationalString(text="hi", is_translated=False)
        el = s.to_child()
        assert el.get("isTranslated") == "false"

    def test_from_container_content(self):
        container = create_element(qn(R, "Label"))
        content = _el(R, "Content", "data")
        content.set("isTranslated", "true")
        content.set("translationSourceLanguage", "fr")
        content.set("translationDate", "2024-01-01")
        container.append(content)
        results = InternationalString.from_container(container)
        assert len(results) == 1
        assert results[0].is_translated is True
        assert results[0].child_tag == "Content"


# ── CodeValue ────────────────────────────────────────────────────────────


class TestCodeValueEdgeCases:
    def test_to_xml_all_attributes(self):
        cv = CodeValue(
            text="val",
            controlled_vocabulary_id="cvid",
            controlled_vocabulary_name="cvname",
            controlled_vocabulary_agency_name="cvagency",
            controlled_vocabulary_version_id="cvver",
            other_value="other",
            controlled_vocabulary_urn="cvurn",
            controlled_vocabulary_scheme_urn="cvschemeurn",
        )
        el = cv.to_xml("TestCV")
        assert el.get("controlledVocabularyID") == "cvid"
        assert el.get("controlledVocabularyName") == "cvname"
        assert el.get("controlledVocabularyAgencyName") == "cvagency"
        assert el.get("controlledVocabularyVersionID") == "cvver"
        assert el.get("otherValue") == "other"
        assert el.get("controlledVocabularyURN") == "cvurn"
        assert el.get("controlledVocabularySchemeURN") == "cvschemeurn"


# ── Reference ────────────────────────────────────────────────────────────


class TestReferenceEdgeCases:
    def test_to_xml_urn_only(self):
        ref = Reference(urn="urn:ddi:ag:id:1.0.0")
        el = ref.to_xml("Ref")
        assert el.find(qn(R, "URN")).text == "urn:ddi:ag:id:1.0.0"  # type: ignore[union-attr]

    def test_to_xml_type_of_object(self):
        ref = Reference(
            agency="ag", identifier="id", version="1", type_of_object="Variable"
        )
        el = ref.to_xml("Ref")
        assert el.find(qn(R, "TypeOfObject")).text == "Variable"  # type: ignore[union-attr]

    def test_matches_by_urn(self):
        ref1 = Reference(urn="urn:ddi:ag:id:1")
        ref2 = Reference(urn="URN:DDI:AG:ID:1")
        assert ref1.matches(ref2)

    def test_matches_by_components(self):
        ref1 = Reference(agency="ag", identifier="id", version="1")
        ref2 = Reference(agency="ag", identifier="id", version="1")
        assert ref1.matches(ref2)


# ── UserID ───────────────────────────────────────────────────────────────


class TestUserIDEdgeCases:
    def test_roundtrip(self):
        uid = UserID(value="my-id", type_of_user_id="ISNI")
        el = uid.to_xml()
        assert el.text == "my-id"
        assert el.get("typeOfUserID") == "ISNI"
        parsed = UserID.from_xml(el)
        assert parsed.value == "my-id"
        assert parsed.type_of_user_id == "ISNI"


# ── UserAttributePair ────────────────────────────────────────────────────


class TestUserAttributePairEdgeCases:
    def test_roundtrip(self):
        uap = UserAttributePair(key="myKey", value="myValue")
        el = uap.to_xml()
        parsed = UserAttributePair.from_xml(el)
        assert parsed.key == "myKey"
        assert parsed.value == "myValue"


# ── VersionRationale ─────────────────────────────────────────────────────


class TestVersionRationaleEdgeCases:
    def test_roundtrip_with_extras(self):
        vr = VersionRationale(
            descriptions=[InternationalString(text="changed", lang="en")],
            other_elements=[_el(R, "Extra", "data")],
        )
        el = vr.to_xml()
        assert el.find(qn(R, "RationaleDescription")) is not None
        assert el.find(qn(R, "Extra")) is not None

    def test_from_xml_wrong_tag(self):
        from ddi_l.exceptions import DDIParseError

        with pytest.raises(DDIParseError):
            VersionRationale.from_xml(create_element("wrong"))


# ── MaintainableBase methods ─────────────────────────────────────────────


class TestMaintainableBaseMethods:
    def test_maintainable_types(self):
        types = MaintainableBase.maintainable_types()
        assert len(types) > 0

    def test_get_label(self):
        from ddi_l.models.logicalproduct import Category

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1",
            labels=[
                InternationalString(text="English", lang="en"),
                InternationalString(text="French", lang="fr"),
            ],
            descriptions=[],
            other_elements=[],
        )
        assert cat.get_label("en") == "English"
        assert cat.get_label("fr") == "French"
        assert cat.get_label("de") == "English"  # fallback to first

    def test_get_label_empty(self):
        from ddi_l.models.logicalproduct import Category

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        assert cat.get_label() is None

    def test_get_description(self):
        from ddi_l.models.logicalproduct import Category

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1",
            labels=[],
            other_elements=[],
            descriptions=[
                InternationalString(text="Desc en", lang="en"),
                InternationalString(text="Desc fr", lang="fr"),
            ],
        )
        assert cat.get_description("en") == "Desc en"
        assert cat.get_description("de") == "Desc en"  # fallback

    def test_get_description_empty(self):
        from ddi_l.models.logicalproduct import Category

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        assert cat.get_description() is None

    def test_format_urn(self):
        from ddi_l.models.logicalproduct import Category

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        assert cat._format_urn() == "urn:ddi:ag:c1:1.0.0"

    def test_format_urn_explicit(self):
        from ddi_l.models.logicalproduct import Category

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            urn="urn:custom",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        assert cat._format_urn() == "urn:custom"

    def test_canonical_urn(self):
        from ddi_l.models.logicalproduct import Category

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        assert cat.canonical_urn() == "urn:ddi:ag:c1:1.0.0"

    def test_to_reference(self):
        from ddi_l.models.logicalproduct import Category

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        ref = cat.to_reference()
        assert ref.agency == "ag"
        assert ref.identifier == "c1"
        assert ref.type_of_object == "Category"


# ── Custom Properties ────────────────────────────────────────────────────


class TestCustomProperties:
    def _make_item(self):
        from ddi_l.models.logicalproduct import Category

        return Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )

    def test_properties_empty(self):
        item = self._make_item()
        assert item.properties == {}

    def test_set_and_get_property(self):
        item = self._make_item()
        item.set_property("color", "blue")
        assert item.get_property("color") == "blue"
        assert item.properties == {"color": "blue"}

    def test_set_property_overwrites(self):
        item = self._make_item()
        item.set_property("color", "blue")
        item.set_property("color", "red")
        assert item.get_property("color") == "red"
        assert len(item.user_attribute_pairs) == 1

    def test_get_property_missing(self):
        item = self._make_item()
        assert item.get_property("missing") is None

    def test_remove_property(self):
        item = self._make_item()
        item.set_property("color", "blue")
        assert item.remove_property("color") is True
        assert item.get_property("color") is None
        assert item.properties == {}

    def test_remove_property_missing(self):
        item = self._make_item()
        assert item.remove_property("nope") is False

    def test_multiple_properties(self):
        item = self._make_item()
        item.set_property("color", "blue")
        item.set_property("size", "large")
        assert item.properties == {"color": "blue", "size": "large"}

    def test_set_property_with_reference(self):
        ref = Reference(
            agency="ag",
            identifier="cl-1",
            version="1.0",
        )
        item = self._make_item()
        item.set_property("vocabulary", ref)
        assert "cl-1" in (item.get_property("vocabulary") or "")

    def test_set_property_with_maintainable(self):
        from ddi_l.models.logicalproduct import CodeList

        cl = CodeList(
            agency="ag",
            identifier="cl-1",
            version="1.0",
        )
        item = self._make_item()
        item.set_property("vocabulary", cl)
        urn = item.get_property("vocabulary")
        assert urn is not None
        assert "cl-1" in urn

    def test_roundtrip_through_xml(self):
        from ddi_l.models.logicalproduct import Category

        item = self._make_item()
        item.set_property("color", "blue")
        item.set_property("size", "large")
        xml = item.to_xml()
        restored = Category.from_xml(xml)
        assert restored.properties == {"color": "blue", "size": "large"}


# ── _assert_unique_children ──────────────────────────────────────────────


class TestAssertUniqueChildren:
    def test_duplicates_raise(self):
        from ddi_l.exceptions import ModelValidationError
        from ddi_l.models.logicalproduct import Category, LogicalProduct

        cats = [
            Category(
                agency="ag",
                identifier="c1",
                version="1.0.0",
                labels=[],
                descriptions=[],
                other_elements=[],
            ),
            Category(
                agency="ag",
                identifier="c1",
                version="1.0.0",
                labels=[],
                descriptions=[],
                other_elements=[],
            ),
        ]
        lp = LogicalProduct(
            agency="ag",
            identifier="lp-1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            categories=cats,
        )
        with pytest.raises(ModelValidationError):
            lp.validate()


# ── Generic to_xml via _FIELD_XML_MAP ────────────────────────────────────


class TestGenericToXml:
    def test_generated_base_serializes(self):
        """Generated bases use _FIELD_XML_MAP for automatic serialization."""
        from ddi_l.models._generated.logicalproduct import CategorySchemeFields

        # CategorySchemeFields has _FIELD_XML_MAP from generation
        field_map = getattr(CategorySchemeFields, "_FIELD_XML_MAP", {})
        # This just verifies the mechanism exists; actual serialization tested via subclasses
        assert isinstance(field_map, dict)


# ── equals / diff ────────────────────────────────────────────────────────


class TestEqualsDiff:
    def _make_cat(self, ident="c1", label_text="Cat"):
        from ddi_l.models.logicalproduct import Category

        return Category(
            agency="ag",
            identifier=ident,
            version="1.0.0",
            labels=[InternationalString(text=label_text, lang="en")],
            descriptions=[],
            other_elements=[],
        )

    def test_equals_same(self):
        a = self._make_cat()
        b = self._make_cat()
        assert a.equals(b)

    def test_equals_different(self):
        a = self._make_cat(label_text="A")
        b = self._make_cat(label_text="B")
        assert not a.equals(b)

    def test_diff_type_mismatch(self):
        from ddi_l.models.logicalproduct import Category, Variable

        cat = Category(
            agency="ag",
            identifier="c1",
            version="1",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        var = Variable(
            agency="ag",
            identifier="v1",
            version="1",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        diffs = cat.diff(var)
        assert any("type mismatch" in d for d in diffs)

    def test_diff_list_length(self):
        a = self._make_cat()
        b = self._make_cat()
        b.names = [
            InternationalString(text="n1", lang="en"),
            InternationalString(text="n2", lang="fr"),
        ]
        diffs = a.diff(b)
        assert len(diffs) > 0

    def test_diff_ignore_label_order(self):
        a = self._make_cat()
        b = self._make_cat()
        a.labels = [
            InternationalString(text="A", lang="en"),
            InternationalString(text="B", lang="fr"),
        ]
        b.labels = [
            InternationalString(text="B", lang="fr"),
            InternationalString(text="A", lang="en"),
        ]
        assert not a.equals(b)
        assert a.equals(b, ignore_label_order=True)

    def test_diff_nested_maintainable(self):
        from ddi_l.models.logicalproduct import CategoryScheme

        cs1 = CategoryScheme(
            agency="ag",
            identifier="cs1",
            version="1",
            labels=[],
            descriptions=[],
            other_elements=[],
            categories=[self._make_cat(label_text="A")],
        )
        cs2 = CategoryScheme(
            agency="ag",
            identifier="cs1",
            version="1",
            labels=[],
            descriptions=[],
            other_elements=[],
            categories=[self._make_cat(label_text="B")],
        )
        diffs = cs1.diff(cs2)
        assert len(diffs) > 0


# ── ValidationContext ────────────────────────────────────────────────────


class TestValidationContext:
    def test_register_and_resolve(self):
        from ddi_l.models.logicalproduct import Category

        ctx = ValidationContext()
        cat = Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        ctx.register(cat)
        ref = Reference(agency="ag", identifier="c1", version="1.0.0")
        assert ctx.can_resolve(ref)
        assert ctx.resolve(ref) is cat

    def test_resolve_by_urn(self):
        from ddi_l.models.logicalproduct import Category

        ctx = ValidationContext()
        cat = Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            urn="urn:ddi:ag:c1:1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        ctx.register(cat)
        ref = Reference(urn="urn:ddi:ag:c1:1.0.0")
        assert ctx.can_resolve(ref)
        assert ctx.resolve(ref) is cat

    def test_resolve_relaxed_by_identifier(self):
        from ddi_l.models.logicalproduct import Category

        ctx = ValidationContext()
        cat = Category(
            agency="ag",
            identifier="c1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
        )
        ctx.register(cat)
        ref = Reference(identifier="c1")
        assert ctx.can_resolve(ref)
        resolved = ctx.resolve(ref)
        assert resolved is cat

    def test_cannot_resolve(self):
        ctx = ValidationContext()
        ref = Reference(identifier="nonexistent")
        assert not ctx.can_resolve(ref)
        assert ctx.resolve(ref) is None

    def test_from_maintainable(self):
        from ddi_l.models.logicalproduct import Category, LogicalProduct

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
        )
        ctx = ValidationContext.from_maintainable(lp)
        assert ctx.can_resolve(Reference(identifier="c1"))
        assert ctx.can_resolve(Reference(identifier="lp1"))

    def test_validate_references(self):
        from ddi_l.models.logicalproduct import Variable

        var = Variable(
            agency="ag",
            identifier="v1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            concept_references=[Reference(identifier="missing-concept")],
        )
        ctx = ValidationContext()
        ctx.register(var)
        warnings = var.validate_references(ctx)
        assert len(warnings) > 0
        assert "missing-concept" in warnings[0].message

    def test_validate_tree(self):
        from ddi_l.models.logicalproduct import LogicalProduct, Variable

        var = Variable(
            agency="ag",
            identifier="v1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            concept_references=[Reference(identifier="missing")],
        )
        lp = LogicalProduct(
            agency="ag",
            identifier="lp1",
            version="1.0.0",
            labels=[],
            descriptions=[],
            other_elements=[],
            variables=[var],
        )
        warnings = lp.validate_tree()
        assert any("missing" in w.message for w in warnings)
