from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pytest

from ddi_l.constants import REUSABLE_NS
from ddi_l.maintainable_registry import MaintainableRegistry
from ddi_l.models.base import MaintainableBase, qn


@dataclass
class _RegistryMaintainable(MaintainableBase):
    TAG: ClassVar[str] = qn(REUSABLE_NS, "RegistryMaintainable")


def test_register_instance_rejects_duplicate_urn() -> None:
    """Registering two maintainables with the same URN fails."""

    registry = MaintainableRegistry()
    first = _RegistryMaintainable(
        urn="urn:ddi:demo.agency:duplicate:1.0",
        agency="demo.agency",
        identifier="duplicate",
        version="1.0",
    )
    second = _RegistryMaintainable(
        urn="urn:ddi:demo.agency:duplicate:1.0",
        agency="demo.agency",
        identifier="other",
        version="1.0",
    )

    registry.register_instance(first)
    with pytest.raises(ValueError, match="already registered"):
        registry.register_instance(second)


def test_register_instance_rejects_duplicate_identifier_tuple() -> None:
    """Duplicate agency/ID/version tuples are not allowed."""

    registry = MaintainableRegistry()
    first = _RegistryMaintainable(
        agency="demo.agency",
        identifier="duplicate",
        version="1.0",
    )
    second = _RegistryMaintainable(
        agency="demo.agency",
        identifier="duplicate",
        version="1.0",
    )

    registry.register_instance(first)
    with pytest.raises(ValueError, match="already registered"):
        registry.register_instance(second)


def test_register_instance_allows_same_object_multiple_times() -> None:
    """Re-registering the same maintainable instance is a no-op."""

    registry = MaintainableRegistry()
    maintainable = _RegistryMaintainable(
        urn="urn:ddi:demo.agency:re-register:1.0",
        agency="demo.agency",
        identifier="re-register",
        version="1.0",
    )

    registry.register_instance(maintainable)
    registry.register_instance(maintainable)
