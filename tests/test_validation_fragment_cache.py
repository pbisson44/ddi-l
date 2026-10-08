from __future__ import annotations

from collections.abc import Mapping

import pytest

from ddi_l._schema_versions import DEFAULT_SCHEMA_VERSION
from ddi_l.constants import get_namespace_set
from ddi_l.schema_loader import _validation as validation


@pytest.mark.parametrize("version", [DEFAULT_SCHEMA_VERSION])
def test_fragment_gap_sets_use_cached_values(
    version: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    validation._clear_fragment_gap_cache()

    namespace_set: Mapping[str, object] = get_namespace_set(version)
    reusable_namespace = str(namespace_set["REUSABLE_NS"])

    original_namespace_value = validation._namespace_value
    call_count = 0

    def _tracking_namespace_value(namespaces: Mapping[str, object], key: str) -> object:
        nonlocal call_count
        call_count += 1
        return original_namespace_value(namespaces, key)

    with monkeypatch.context() as patch:
        patch.setattr(validation, "_namespace_value", _tracking_namespace_value)

        first_gap_sets = validation._build_fragment_gap_sets(
            namespace_set, reusable_namespace, version=version
        )
        first_call_count = call_count

        second_gap_sets = validation._build_fragment_gap_sets(
            namespace_set, reusable_namespace, version=version
        )

    assert call_count == first_call_count, "cache miss should not access namespaces"
    assert first_gap_sets is second_gap_sets
    assert first_gap_sets[0] is second_gap_sets[0]
    assert first_gap_sets[1] is second_gap_sets[1]
