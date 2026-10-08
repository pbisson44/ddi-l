# mypy: ignore-errors
"""Fuzz tests for invalid DDI inputs."""

import textwrap
from collections.abc import Iterable

import pytest

pytest.importorskip("hypothesis")
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from ddi_l import schema_loader
from ddi_l._etree import cleanup_namespaces, fromstring, tostring
from ddi_l.constants import DATA_COLLECTION_NS, INSTANCE_NS, REUSABLE_NS
from ddi_l.document import DDIDocument
from ddi_l.exceptions import DDIParseError
from ddi_l.models.datacollection import DataCollection
from ddi_l.schema_loader import SchemaValidationError

BASE_INSTANCE = (
    textwrap.dedent(
        """
    <DDIInstance xmlns=\"{instance}\" xmlns:r=\"{reusable}\" xmlns:d=\"{data_collection}\">
      <r:Agency>example.agency</r:Agency>
      <r:ID>4534a84b-faa5-59f8-8d96-164d86f82d26</r:ID>
      <r:Version>1.0</r:Version>
      <d:DataCollection>
        <r:Agency>demo.agency</r:Agency>
        <r:ID>8380be57-2b19-54fc-9792-11cafbf238a4</r:ID>
        <r:Version>1.0</r:Version>
      </d:DataCollection>
    </DDIInstance>
    """
    )
    .strip()
    .format(
        instance=INSTANCE_NS,
        reusable=REUSABLE_NS,
        data_collection=DATA_COLLECTION_NS,
    )
)

PREFIX_ALPHABET = st.characters(min_codepoint=97, max_codepoint=122)
PREFIXES = st.text(PREFIX_ALPHABET, min_size=1, max_size=8).filter(
    lambda value: value != "xml"
)


@st.composite
def mutated_instances(draw) -> dict[str, object]:
    """Generate mutated DDI instances missing identification and namespaces.

    Args:
        draw: Hypothesis data drawing helper for composing payload mutations.
    """
    root = fromstring(BASE_INSTANCE)

    missing_root: set[str] = draw(
        st.sets(
            st.sampled_from(["Agency", "ID", "Version"]),
            min_size=1,
            max_size=3,
        )
    )
    for name in missing_root:
        child = root.find(f"{{{REUSABLE_NS}}}{name}")
        if child is not None:
            root.remove(child)

    nsmap_prefixes = getattr(root, "nsmap", {})
    existing_prefixes = {
        prefix for prefix in nsmap_prefixes if prefix not in {None, "xml"}
    }
    nsmap = {None: INSTANCE_NS}

    reusable_prefix = draw(
        PREFIXES.filter(lambda value: value not in existing_prefixes)
    )
    existing_prefixes.add(reusable_prefix)
    nsmap[reusable_prefix] = REUSABLE_NS

    data_prefix = draw(PREFIXES.filter(lambda value: value not in existing_prefixes))
    existing_prefixes.add(data_prefix)
    nsmap[data_prefix] = DATA_COLLECTION_NS

    collection = root.find(f"{{{DATA_COLLECTION_NS}}}DataCollection")
    assert collection is not None, "Base payload must include a DataCollection element"

    missing_collection: set[str] = draw(
        st.sets(
            st.sampled_from(["Agency", "ID", "Version"]),
            min_size=1,
            max_size=3,
        )
    )
    for name in missing_collection:
        child = collection.find(f"{{{REUSABLE_NS}}}{name}")
        if child is not None:
            collection.remove(child)

    alternate_namespace: str | None = None
    if draw(st.booleans()):
        alternate_namespace = draw(
            st.sampled_from(
                [
                    "ddi:datacollection:broken",
                    "http://invalid.example/ddi",
                    "urn:ddi:broken:namespace",
                ]
            )
        )
        bogus_prefix = draw(
            PREFIXES.filter(lambda value: value not in existing_prefixes)
        )
        existing_prefixes.add(bogus_prefix)
        nsmap[bogus_prefix] = alternate_namespace
        collection.tag = f"{{{alternate_namespace}}}DataCollection"

    if draw(st.booleans()):
        target = draw(st.sampled_from([root, collection]))
        attr_name = f"unexpected-{draw(PREFIXES)}"
        attr_value = draw(
            st.text(
                st.characters(min_codepoint=45, max_codepoint=122),
                min_size=1,
                max_size=16,
            )
        )
        target.set(attr_name, attr_value)

    cleanup_namespaces(root, nsmap=nsmap)
    xml = tostring(root, pretty_print=False)
    return {
        "xml": xml,
        "missing_root": missing_root,
        "missing_collection": missing_collection,
        "collection_namespace": alternate_namespace or DATA_COLLECTION_NS,
    }


def _collect_data_collection_elements(xml: str) -> Iterable[tuple[str, str]]:
    """Yield namespace-tagged DataCollection fragments from serialized XML.

    Args:
        xml: Serialized DDI instance containing DataCollection fragments.
    """
    root = fromstring(xml)
    for element in root.iter():
        if element.tag.endswith("}DataCollection") or element.tag == "DataCollection":
            namespace = DATA_COLLECTION_NS
            if element.tag.startswith("{"):
                namespace = element.tag[1:].split("}", 1)[0]
            yield namespace, tostring(element, pretty_print=False)


@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(mutated_instances())
def test_mutated_payloads_surface_structured_errors(payload: dict[str, object]) -> None:
    """Mutated payloads raise structured errors and reveal missing fields.

    Args:
        payload: Generated mutation dictionary describing broken XML payloads.
    """
    xml = payload["xml"]
    missing_root = payload["missing_root"]

    with pytest.raises(SchemaValidationError) as excinfo:
        schema_loader.validate(xml)
    issues = excinfo.value.issues
    assert issues, "Schema validation should surface structured issues"
    primary = issues[0]
    for missing in sorted(missing_root):
        assert missing in primary.message
    assert primary.xpath == "/DDIInstance"

    with pytest.raises(SchemaValidationError) as doc_excinfo:
        DDIDocument.from_xml(xml, validate=True)
    doc_issue = doc_excinfo.value.issues[0]
    for missing in sorted(missing_root):
        assert missing in doc_issue.message
    assert doc_issue.xpath == "/DDIInstance"

    expected_namespace = payload["collection_namespace"]
    for namespace, element_xml in _collect_data_collection_elements(xml):
        element = fromstring(element_xml)
        if namespace != DATA_COLLECTION_NS:
            assert namespace == expected_namespace
            with pytest.raises((ValueError, DDIParseError)) as maintainable_exc:
                DataCollection.from_xml(element)
            assert "DataCollection" in str(maintainable_exc.value)
        else:
            assert expected_namespace == DATA_COLLECTION_NS
            wrapper = DataCollection.from_xml(element)
            missing_collection: set[str] = payload["missing_collection"]
            if "ID" in missing_collection:
                assert wrapper.identifier is None
            if "Agency" in missing_collection:
                assert wrapper.agency is None
            if "Version" in missing_collection:
                assert wrapper.version is None
