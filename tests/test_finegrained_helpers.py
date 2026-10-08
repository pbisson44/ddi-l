"""Round-trip tests for the fine-grained per-module fluent helpers."""

from __future__ import annotations

from ddi_l import new_study, open_ddi
from ddi_l.constants import DATASET_NS
from ddi_l.models.base import Reference, qn
from ddi_l.models.dataset import DataSet


def test_ncube_coordinate_region_and_attribute(tmp_path):
    """A1: a CoordinateRegion plus an attribute attached to it round-trips."""
    doc = new_study(title="T", agency="ex.org")
    age = doc.add_variable(name="age")
    sex = doc.add_variable(name="sex")
    count = doc.add_variable(name="count")
    ncube = doc.add_ncube(name="cube")
    ncube.add_dimension(age.to_reference())
    ncube.add_dimension(sex.to_reference())
    ncube.add_measure(count.to_reference())
    region = ncube.add_coordinate_region()
    ncube.add_dimension_value(
        region,
        rank=2,
        code_references=[
            Reference(
                agency="ex.org", identifier="c1", version="1", type_of_object="Code"
            )
        ],
    )
    attribute = ncube.add_attribute(count.to_reference(), attachment_region=region)
    assert attribute.get("attachmentLevel") == "CoordinateRegion"
    assert doc.validate() == []

    path = tmp_path / "ncube.xml"
    doc.save(path)
    assert open_ddi(path).validate() == []


def test_physical_record_segment_key(tmp_path):
    """A2: a PhysicalRecordSegment key (hasSegmentKey + KeyVariableReference)."""
    doc = new_study(title="T", agency="ex.org")
    hhid = doc.add_variable(name="hhid")
    relationship = doc.add_data_relationship()
    record = relationship.add_logical_record()
    doc.add_record_layout(logical_record=record)

    structure = doc._get_study().physical_structures[0]
    structure.gross_record_structures.clear()
    gross = structure.link_logical_record(
        record.to_reference(),
        segment_identifier="seg-1",
        key_variable=hhid.to_reference(),
        key_value="1",
    )
    from ddi_l.constants import PHYSICAL_DATA_PRODUCT_NS as P

    segment = gross.find(qn(P, "PhysicalRecordSegment"))
    assert segment is not None
    assert segment.get("hasSegmentKey") == "true"
    assert segment.find(qn(P, "KeyVariableReference")) is not None
    assert doc.validate() == []

    path = tmp_path / "segment.xml"
    doc.save(path)
    assert open_ddi(path).validate() == []


def test_data_item_physical_location_extras(tmp_path):
    """A3: StorageFormat, Delimiter, and DecimalPositions on a data item."""
    doc = new_study(title="T", agency="ex.org")
    age = doc.add_variable(name="age")
    relationship = doc.add_data_relationship()
    record = relationship.add_logical_record()
    layout = doc.add_record_layout(logical_record=record)
    layout.add_data_item(
        age.to_reference(),
        start_position=1,
        width=3,
        storage_format="ASCII",
        delimiter="comma",
        decimal_positions=2,
    )
    assert doc.validate() == []

    path = tmp_path / "location.xml"
    doc.save(path)
    assert open_ddi(path).validate() == []


def _find_dataset(document) -> DataSet:
    element = next(document._inner._root.iter(qn(DATASET_NS, "DataSet")))
    return DataSet.from_xml(element)


def test_dataset_record_set(tmp_path):
    """A4: a RecordSet (variable order plus records) round-trips."""
    doc = new_study(title="T", agency="ex.org")
    age = doc.add_variable(name="age")
    sex = doc.add_variable(name="sex")
    dataset = doc.add_dataset(name="rows")
    dataset.set_variable_order([age.to_reference(), sex.to_reference()])
    dataset.add_record(["42", "M"])
    dataset.add_record(["37", "F"])
    assert doc.validate() == []

    path = tmp_path / "recordset.xml"
    doc.save(path)
    reopened = open_ddi(path)
    assert reopened.validate() == []
    loaded = _find_dataset(reopened)
    assert len(loaded.records) == 2
    assert len(loaded.variable_order) == 2


def test_dataset_variable_set(tmp_path):
    """A4: a VariableSet (one column of values per variable) round-trips."""
    doc = new_study(title="T", agency="ex.org")
    age = doc.add_variable(name="age")
    dataset = doc.add_dataset(name="cols")
    dataset.add_variable_item(age.to_reference(), ["42", "37", "55"])
    assert doc.validate() == []

    path = tmp_path / "variableset.xml"
    doc.save(path)
    reopened = open_ddi(path)
    assert reopened.validate() == []
    loaded = _find_dataset(reopened)
    assert len(loaded.variable_items) == 1


def test_numeric_representation_inclusivity_and_missing_values(tmp_path):
    """A5: NumberRange inclusivity flags and missing values round-trip."""
    doc = new_study(title="T", agency="ex.org")
    age = doc.add_variable(name="age")
    age.set_numeric(
        "Integer",
        low=0,
        high=120,
        low_inclusive=True,
        high_inclusive=False,
        missing_values=["-9", "-8"],
        blank_is_missing_value=True,
    )
    assert doc.validate() == []

    path = tmp_path / "numeric.xml"
    doc.save(path)
    reopened = open_ddi(path)
    assert reopened.validate() == []
    variable_representation = reopened.variables[0].variable_representation
    assert variable_representation is not None
    representation = variable_representation.numeric_representation
    assert representation is not None
    number_range = representation.number_range
    assert number_range is not None
    assert number_range.low_is_inclusive is True
    assert number_range.high_is_inclusive is False
    assert representation.other_attributes.get("missingValue") == "-9 -8"
    assert representation.blank_is_missing_value is True


def test_comparison_maps(tmp_path):
    """A6: managed item maps, representation maps, scheme refs, correspondence."""
    doc = new_study(title="T", agency="ex.org")
    v1 = doc.add_variable(name="age_2020")
    v2 = doc.add_variable(name="age_2021")
    cl1 = doc.add_code_list(name="cl1")
    cl2 = doc.add_code_list(name="cl2")
    comparison = doc.add_comparison(name="maps")

    correspondence = comparison.correspondence(
        commonality="Both measure age in years",
        difference="Different waves",
        weight=0.9,
    )
    comparison.add_variable_map(
        v1.to_reference(),
        v2.to_reference(),
        source_scheme=Reference(
            agency="ex.org",
            identifier="vs1",
            version="1",
            type_of_object="VariableScheme",
        ),
        correspondence=correspondence,
    )
    comparison.add_managed_item_map(
        [(v1.to_reference(), v2.to_reference())],
        type_of_mapped_item="Variable",
        source_scheme=Reference(
            agency="ex.org",
            identifier="vs1",
            version="1",
            type_of_object="VariableScheme",
        ),
        target_scheme=Reference(
            agency="ex.org",
            identifier="vs2",
            version="1",
            type_of_object="VariableScheme",
        ),
    )
    comparison.add_representation_map(
        cl1.to_reference(),
        cl2.to_reference(),
        Reference(
            agency="ex.org",
            identifier="gi1",
            version="1",
            type_of_object="GenerationInstruction",
        ),
    )
    assert doc.validate() == []

    path = tmp_path / "comparison.xml"
    doc.save(path)
    reopened = open_ddi(path)
    assert reopened.validate() == []
    loaded = reopened.comparisons[0]
    assert len(loaded.variable_maps) == 1
    assert len(loaded.managed_item_maps) == 1
    assert len(loaded.representation_maps) == 1
