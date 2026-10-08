# mypy: ignore-errors
"""Tests for registry/__init__.py — MaintainableRegistry class-level registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pytest

from ddi_l.models.base import MaintainableBase
from ddi_l.registry import (
    MaintainableRegistry,
    clear_registry,
    get_all_maintainable_classes,
    get_maintainable_class,
    register_maintainable,
)


# Save and restore registry state around tests
@pytest.fixture(autouse=True)
def _preserve_registry():
    """Save and restore the registry state around each test."""
    saved_tags = dict(MaintainableRegistry._tag_to_class)
    saved_types = list(MaintainableRegistry._registered_types)
    saved_callbacks = list(MaintainableRegistry._on_register_callbacks)
    yield
    MaintainableRegistry._tag_to_class.clear()
    MaintainableRegistry._tag_to_class.update(saved_tags)
    MaintainableRegistry._registered_types.clear()
    MaintainableRegistry._registered_types.extend(saved_types)
    MaintainableRegistry._on_register_callbacks.clear()
    MaintainableRegistry._on_register_callbacks.extend(saved_callbacks)


TAG_A = "{http://test}TypeA"
TAG_B = "{http://test}TypeB"


@dataclass
class _TypeA(MaintainableBase):
    TAG: ClassVar[str] = TAG_A


@dataclass
class _TypeB(MaintainableBase):
    TAG: ClassVar[str] = TAG_B


class TestRegisterDecorator:
    def test_register_and_lookup(self):
        MaintainableRegistry.register(TAG_A)(_TypeA)
        assert MaintainableRegistry.get(TAG_A) is _TypeA

    def test_register_dedup(self):
        MaintainableRegistry.register(TAG_A)(_TypeA)
        MaintainableRegistry.register(TAG_A)(_TypeA)  # re-register same
        assert MaintainableRegistry._registered_types.count(_TypeA) == 1

    def test_register_notifies_callbacks(self):
        received = []
        MaintainableRegistry.on_register(lambda cls: received.append(cls))
        MaintainableRegistry.register(TAG_A)(_TypeA)
        assert _TypeA in received

    def test_callback_exception_does_not_break_registration(self):
        def bad_callback(cls):
            raise RuntimeError("boom")

        MaintainableRegistry.on_register(bad_callback)
        # Should not raise
        MaintainableRegistry.register(TAG_A)(_TypeA)
        assert MaintainableRegistry.get(TAG_A) is _TypeA


class TestRegisterClass:
    def test_register_class(self):
        MaintainableRegistry.register_class(TAG_B, _TypeB)
        assert MaintainableRegistry.get(TAG_B) is _TypeB

    def test_register_class_dedup(self):
        MaintainableRegistry.register_class(TAG_B, _TypeB)
        MaintainableRegistry.register_class(TAG_B, _TypeB)
        count = MaintainableRegistry._registered_types.count(_TypeB)
        assert count == 1

    def test_register_class_notifies_callbacks(self):
        received = []
        MaintainableRegistry.on_register(lambda cls: received.append(cls))
        MaintainableRegistry.register_class(TAG_B, _TypeB)
        assert _TypeB in received

    def test_callback_exception_ignored(self):
        MaintainableRegistry.on_register(lambda cls: 1 / 0)
        MaintainableRegistry.register_class(TAG_B, _TypeB)
        assert MaintainableRegistry.get(TAG_B) is _TypeB


class TestGetMethods:
    def test_get_missing(self):
        assert MaintainableRegistry.get("{http://test}Missing") is None

    def test_get_all(self):
        MaintainableRegistry.register(TAG_A)(_TypeA)
        MaintainableRegistry.register(TAG_B)(_TypeB)
        all_types = MaintainableRegistry.get_all()
        assert _TypeA in all_types
        assert _TypeB in all_types

    def test_get_tags(self):
        MaintainableRegistry.register(TAG_A)(_TypeA)
        tags = MaintainableRegistry.get_tags()
        assert TAG_A in tags


class TestClear:
    def test_clear(self):
        MaintainableRegistry.register(TAG_A)(_TypeA)
        MaintainableRegistry.clear()
        assert MaintainableRegistry.get(TAG_A) is None
        assert len(MaintainableRegistry.get_all()) == 0


class TestCallbackManagement:
    def test_on_register(self):
        calls = []

        def cb(cls):
            return calls.append(cls)

        MaintainableRegistry.on_register(cb)
        assert cb in MaintainableRegistry._on_register_callbacks

    def test_remove_callback(self):
        def cb(cls):
            return None

        MaintainableRegistry.on_register(cb)
        MaintainableRegistry.remove_callback(cb)
        assert cb not in MaintainableRegistry._on_register_callbacks

    def test_remove_callback_not_present(self):
        def cb(cls):
            return None

        # Should not raise
        MaintainableRegistry.remove_callback(cb)


class TestConvenienceFunctions:
    def test_register_maintainable(self):
        register_maintainable(TAG_A)(_TypeA)
        assert get_maintainable_class(TAG_A) is _TypeA

    def test_get_maintainable_class_missing(self):
        assert get_maintainable_class("{http://test}Missing") is None

    def test_get_all_maintainable_classes(self):
        register_maintainable(TAG_A)(_TypeA)
        result = get_all_maintainable_classes()
        assert _TypeA in result

    def test_clear_registry(self):
        register_maintainable(TAG_A)(_TypeA)
        clear_registry()
        assert get_maintainable_class(TAG_A) is None
