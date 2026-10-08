"""Unit tests for logical product representation helpers."""

from __future__ import annotations

from ddi_l._etree import create_element
from ddi_l.constants import REUSABLE_NS
from ddi_l.models.base import Reference, qn
from ddi_l.models.logicalproduct import (
    CodeRepresentation,
    DateTimeRepresentation,
    NumberRange,
    NumericRepresentation,
)


def test_code_representation_preserves_blank_and_reference() -> None:
    """CodeRepresentation round-trips blank flag and reference metadata."""
    element = create_element(CodeRepresentation.TAG)
    element.set("blankIsMissingValue", "true")
    element.set("customAttribute", "kept")
    element.append(
        Reference(
            type_of_object="CodeList",
            agency="demo.agency",
            identifier="codes-affirmative",
            version="1.0",
        ).to_xml("CodeListReference")
    )

    rep = CodeRepresentation.from_xml(element)

    assert rep.blank_is_missing_value is True
    assert rep.other_attributes == {"customAttribute": "kept"}
    assert rep.code_list_reference is not None
    assert rep.code_list_reference.identifier == "codes-affirmative"

    rebuilt = rep.to_xml()
    assert rebuilt.get("blankIsMissingValue") == "true"
    assert rebuilt.get("customAttribute") == "kept"
    assert rebuilt.find(qn(REUSABLE_NS, "CodeListReference")) is not None


def test_numeric_representation_preserves_range_metadata() -> None:
    """NumericRepresentation retains range attributes and type metadata."""
    element = create_element(NumericRepresentation.TAG)
    element.set("blankIsMissingValue", "false")

    range_el = create_element(NumberRange.TAG)
    low_el = create_element(qn(REUSABLE_NS, "Low"))
    low_el.set("isInclusive", "true")
    low_el.text = "0"
    range_el.append(low_el)
    high_el = create_element(qn(REUSABLE_NS, "High"))
    high_el.set("isInclusive", "false")
    high_el.text = "100"
    range_el.append(high_el)
    element.append(range_el)

    numeric_type = create_element(qn(REUSABLE_NS, "NumericTypeCode"))
    numeric_type.text = "Integer"
    element.append(numeric_type)

    rep = NumericRepresentation.from_xml(element)

    assert rep.blank_is_missing_value is False
    assert rep.numeric_type_code == "Integer"
    assert rep.number_range is not None
    assert rep.number_range.low == "0"
    assert rep.number_range.high == "100"
    assert rep.number_range.low_is_inclusive is True
    assert rep.number_range.high_is_inclusive is False

    rebuilt = rep.to_xml()
    assert rebuilt.get("blankIsMissingValue") == "false"
    range_again = rebuilt.find(NumberRange.TAG)
    assert range_again is not None
    low_again = range_again.find(qn(REUSABLE_NS, "Low"))
    high_again = range_again.find(qn(REUSABLE_NS, "High"))
    assert (
        low_again is not None
        and low_again.get("isInclusive") == "true"
        and low_again.text == "0"
    )
    assert (
        high_again is not None
        and high_again.get("isInclusive") == "false"
        and high_again.text == "100"
    )


def test_date_time_representation_preserves_type() -> None:
    """DateTimeRepresentation preserves date type information on round-trip."""
    element = create_element(DateTimeRepresentation.TAG)
    element.set("blankIsMissingValue", "true")
    date_type = create_element(qn(REUSABLE_NS, "DateTypeCode"))
    date_type.text = "YYYY-MM-DD"
    element.append(date_type)

    rep = DateTimeRepresentation.from_xml(element)

    assert rep.blank_is_missing_value is True
    assert rep.date_type_code == "YYYY-MM-DD"

    rebuilt = rep.to_xml()
    assert rebuilt.get("blankIsMissingValue") == "true"
    rebuilt_date_type = rebuilt.find(qn(REUSABLE_NS, "DateTypeCode"))
    assert rebuilt_date_type is not None
    assert rebuilt_date_type.text == "YYYY-MM-DD"
