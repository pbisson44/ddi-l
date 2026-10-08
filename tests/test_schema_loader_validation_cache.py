from __future__ import annotations

from ddi_l import schema_loader
from ddi_l.models.base import MaintainableBase
from ddi_l.registry import MaintainableRegistry
from ddi_l.schema_loader import _validation


def test_validate_refreshes_known_type_cache(monkeypatch) -> None:
    """Validation should reuse the refreshed known-type cache after registration."""

    original_registry = dict(MaintainableRegistry._tag_to_class)
    original_registered = list(MaintainableRegistry._registered_types)

    schema_loader.clear_known_type_name_cache()
    baseline = _validation._resolve_known_type_names()

    temporary_tag = "{ddi:reusable:3_3}TemporaryMaintainable"

    class TemporaryMaintainable(MaintainableBase):
        TAG = temporary_tag

    try:
        assert _validation._local_name(temporary_tag) not in baseline

        xml = """
        <FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">
          <TopLevelReference>
            <r:Agency>example.agency</r:Agency>
            <r:ID>fragment</r:ID>
            <r:Version>1.0</r:Version>
            <r:TypeOfObject>TemporaryMaintainable</r:TypeOfObject>
          </TopLevelReference>
          <Fragment>
            <r:TemporaryMaintainable>
              <r:Agency>example.agency</r:Agency>
              <r:ID>temporary</r:ID>
              <r:Version>1.0</r:Version>
            </r:TemporaryMaintainable>
          </Fragment>
        </FragmentInstance>
        """.strip()

        element = schema_loader.fromstring(xml)

        monkeypatch.setattr(schema_loader, "xmlschema", None)

        first_pass = schema_loader.validate(element, raise_error=False)
        second_pass = schema_loader.validate(element, raise_error=False)

        first_warnings = [
            issue.message for issue in first_pass if issue.severity == "warning"
        ]
        second_warnings = [
            issue.message for issue in second_pass if issue.severity == "warning"
        ]

        assert first_warnings == []
        assert second_warnings == []

        refreshed = _validation._resolve_known_type_names()
        assert _validation._local_name(temporary_tag) in refreshed
    finally:
        MaintainableRegistry._tag_to_class.clear()
        MaintainableRegistry._tag_to_class.update(original_registry)
        MaintainableRegistry._registered_types.clear()
        MaintainableRegistry._registered_types.extend(original_registered)
        schema_loader.clear_known_type_name_cache()
