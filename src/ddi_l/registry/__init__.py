"""Centralized registry for maintainable types - breaks circular imports.

This module provides a clean separation between type registration and
the model implementations, allowing models to register themselves without
creating circular import dependencies.
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar, TypeVar

if TYPE_CHECKING:
    from ..models.base import MaintainableBase

__all__ = [
    "MaintainableRegistry",
    "clear_registry",
    "get_all_maintainable_classes",
    "get_maintainable_class",
    "register_maintainable",
]


T = TypeVar("T", bound="MaintainableBase")


class MaintainableRegistry:
    """Central registry mapping XML tags to maintainable classes.

    This registry allows maintainable classes to register themselves
    during import, enabling dynamic lookup by tag name without requiring
    all models to be imported upfront.

    Example:
        >>> @MaintainableRegistry.register("{http://ddi.../instance}DDIInstance")
        ... class DDIInstance(MaintainableBase):
        ...     pass

        >>> cls = MaintainableRegistry.get("...")
    """

    _tag_to_class: ClassVar[dict[str, type[MaintainableBase]]] = {}
    _registered_types: ClassVar[list[type[MaintainableBase]]] = []
    _on_register_callbacks: ClassVar[
        list[Callable[[type[MaintainableBase]], None]]
    ] = []

    @classmethod
    def register(cls, tag: str) -> Callable[[type[T]], type[T]]:
        """Decorator to register a maintainable class for a given XML tag.

        Args:
            tag: The fully-qualified XML tag (Clark notation) for this class.

        Returns:
            A decorator that registers the class and returns it unchanged.

        Example:
            >>> @MaintainableRegistry.register("{http://example.org}MyElement")
            ... @dataclass
            ... class MyElement(MaintainableBase):
            ...     TAG = "{http://example.org}MyElement"
        """

        def decorator(model_class: type[T]) -> type[T]:
            cls._tag_to_class[tag] = model_class
            if model_class not in cls._registered_types:
                cls._registered_types.append(model_class)

            # Notify any listeners (e.g., schema_loader cache invalidation)
            for callback in cls._on_register_callbacks:
                with contextlib.suppress(Exception):
                    callback(model_class)

            return model_class

        return decorator

    @classmethod
    def register_class(cls, tag: str, model_class: type[MaintainableBase]) -> None:
        """Programmatically register a maintainable class.

        This is an alternative to the decorator for cases where
        decoration isn't convenient.

        Args:
            tag: The fully-qualified XML tag (Clark notation).
            model_class: The maintainable class to register.
        """
        cls._tag_to_class[tag] = model_class
        if model_class not in cls._registered_types:
            cls._registered_types.append(model_class)

        for callback in cls._on_register_callbacks:
            with contextlib.suppress(Exception):
                callback(model_class)

    @classmethod
    def get(cls, tag: str) -> type[MaintainableBase] | None:
        """Look up the maintainable class for a given XML tag.

        Args:
            tag: The fully-qualified XML tag (Clark notation).

        Returns:
            The registered class, or None if no class is registered.
        """
        return cls._tag_to_class.get(tag)

    @classmethod
    def get_all(cls) -> tuple[type[MaintainableBase], ...]:
        """Return all registered maintainable classes.

        Returns:
            A tuple of all registered maintainable classes in registration order.
        """
        return tuple(cls._registered_types)

    @classmethod
    def get_tags(cls) -> tuple[str, ...]:
        """Return all registered XML tags.

        Returns:
            A tuple of all registered XML tags.
        """
        return tuple(cls._tag_to_class.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registrations. Primarily for testing."""
        cls._tag_to_class.clear()
        cls._registered_types.clear()

    @classmethod
    def on_register(cls, callback: Callable[[type[MaintainableBase]], None]) -> None:
        """Register a callback to be invoked when new classes are registered.

        This is used by schema_loader to invalidate caches when new
        maintainable types become available.

        Args:
            callback: Function called with the newly registered class.
        """
        cls._on_register_callbacks.append(callback)

    @classmethod
    def remove_callback(
        cls, callback: Callable[[type[MaintainableBase]], None]
    ) -> None:
        """Remove a previously registered callback."""
        with contextlib.suppress(ValueError):
            cls._on_register_callbacks.remove(callback)


# Convenience functions for module-level access
def register_maintainable(tag: str) -> Callable[[type[T]], type[T]]:
    """Decorator to register a maintainable class. See MaintainableRegistry.register."""
    return MaintainableRegistry.register(tag)


def get_maintainable_class(tag: str) -> type[MaintainableBase] | None:
    """Look up maintainable class by tag. See MaintainableRegistry.get."""
    return MaintainableRegistry.get(tag)


def get_all_maintainable_classes() -> tuple[type[MaintainableBase], ...]:
    """Get all registered classes. See MaintainableRegistry.get_all."""
    return MaintainableRegistry.get_all()


def clear_registry() -> None:
    """Clear all registrations. See MaintainableRegistry.clear."""
    MaintainableRegistry.clear()
