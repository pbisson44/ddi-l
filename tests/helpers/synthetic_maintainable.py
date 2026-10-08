"""Helpers for registering temporary maintainable subclasses during tests."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import ClassVar
from uuid import uuid4

import ddi_l.schema_loader as schema_loader
from ddi_l._etree import Element, create_element
from ddi_l.constants import INSTANCE_NS
from ddi_l.models import qn
from ddi_l.models.base import MaintainableBase
from ddi_l.registry import MaintainableRegistry


@contextmanager
def synthetic_maintainable() -> Iterator[type[MaintainableBase]]:
    """Temporarily register a synthetic maintainable type with the registry."""

    tag = qn(INSTANCE_NS, f"SyntheticMaintainable{uuid4().hex}")

    @dataclass
    class _SyntheticMaintainable(MaintainableBase):
        TAG: ClassVar[str] = tag
        value: str | None = None

        @classmethod
        def from_xml(cls, element: Element) -> _SyntheticMaintainable:
            data = cls._collect_common(element)
            value_element = element.find(qn(INSTANCE_NS, "SyntheticValue"))
            value = value_element.text if value_element is not None else None
            return cls(value=value, **data)

        def to_xml(self) -> Element:
            element = super().to_xml()
            if self.value is not None:
                value_element = create_element(qn(INSTANCE_NS, "SyntheticValue"))
                value_element.text = self.value
                element.append(value_element)
            return element

    registered_types = list(MaintainableRegistry._registered_types)
    tag_registry = dict(MaintainableRegistry._tag_to_class)
    try:
        yield _SyntheticMaintainable
    finally:
        MaintainableRegistry._tag_to_class.clear()
        MaintainableRegistry._tag_to_class.update(tag_registry)
        MaintainableRegistry._registered_types.clear()
        MaintainableRegistry._registered_types.extend(registered_types)
        schema_loader.clear_known_type_name_cache()
