"""Central registry for resolving maintainable DDI types by name."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Protocol, TypeAlias

from .models.base import MaintainableBase, Reference

ResolveIdentifier: TypeAlias = (
    MaintainableBase | Reference | str | tuple[str | None, str | None, str | None]
)


class MaintainableResolver(Protocol):
    """Callable protocol for resolving maintainable identifiers."""

    def __call__(  # noqa: D102
        self,
        identifier: ResolveIdentifier,
    ) -> MaintainableBase | None: ...


def normalize_maintainable_type_name(type_name: str) -> str:
    """Normalise a maintainable type name to the alias lookup key."""
    normalized = type_name.split(":")[-1]
    normalized = normalized.split(".")[-1]
    return normalized.lower()


@dataclass
class _MaintainableRegistryState:
    """Internal state container for the maintainable type registry."""

    aliases: dict[str, type[MaintainableBase]] = field(default_factory=dict)
    registered_types: set[type[MaintainableBase]] = field(default_factory=set)
    instances_by_urn: dict[str, MaintainableBase] = field(default_factory=dict)
    instances_by_key: dict[tuple[str | None, str, str | None], MaintainableBase] = (
        field(default_factory=dict)
    )


class MaintainableRegistry:
    """Lookup registry for resolving maintainable DDI classes by alias."""

    def __init__(self) -> None:
        self._state = _MaintainableRegistryState()

    # ------------------------------------------------------------------
    # Alias registration and lookups
    # ------------------------------------------------------------------

    def register_alias(
        self, alias: str, maintainable_type: type[MaintainableBase]
    ) -> None:
        """Register ``alias`` for ``maintainable_type``."""
        self._state.aliases[normalize_maintainable_type_name(alias)] = maintainable_type

    def _ensure_defaults(self) -> None:
        """Populate the registry with the core maintainable classes."""
        for maintainable_type in MaintainableBase.maintainable_types():
            if maintainable_type in self._state.registered_types:
                continue
            self._state.registered_types.add(maintainable_type)
            alias = maintainable_type.__name__
            normalized = normalize_maintainable_type_name(alias)
            self._state.aliases.setdefault(normalized, maintainable_type)

    def resolve_type(self, type_name: str) -> type[MaintainableBase] | None:
        """Return the maintainable class registered under ``type_name``."""
        if not type_name:
            return None
        self._ensure_defaults()
        return self._state.aliases.get(normalize_maintainable_type_name(type_name))

    # ------------------------------------------------------------------
    # Instance registration and lookups
    # ------------------------------------------------------------------

    def register_instance(self, maintainable: MaintainableBase) -> MaintainableBase:
        """Register ``maintainable`` for instance level resolution."""
        if not isinstance(maintainable, MaintainableBase):
            raise TypeError("maintainable must inherit from MaintainableBase.")

        urn = maintainable._format_urn()
        if urn:
            existing = self._state.instances_by_urn.get(urn)
            if existing is not None and existing is not maintainable:
                raise ValueError(
                    f"Maintainable with URN {urn!r} is already"
                    f" registered as {existing.__class__.__name__}."
                )
            self._state.instances_by_urn[urn] = maintainable

        identifier = maintainable.identifier
        if identifier:
            key = (maintainable.agency, identifier, maintainable.version)
            existing = self._state.instances_by_key.get(key)
            if existing is not None and existing is not maintainable:
                raise ValueError(
                    "Maintainable with agency/ID/version "
                    f"{key!r} is already registered as {existing.__class__.__name__}."
                )
            self._state.instances_by_key[key] = maintainable
        return maintainable

    def register_instances(self, maintainables: Iterable[MaintainableBase]) -> None:
        """Register each maintainable contained in ``maintainables``."""
        for maintainable in maintainables:
            self.register_instance(maintainable)

    def unregister_instance(self, maintainable: MaintainableBase) -> None:
        """Remove ``maintainable`` from the instance registry when present."""
        urn = maintainable._format_urn()
        if urn and urn in self._state.instances_by_urn:
            self._state.instances_by_urn.pop(urn, None)

        identifier = maintainable.identifier
        if identifier:
            key = (maintainable.agency, identifier, maintainable.version)
            self._state.instances_by_key.pop(key, None)

    def clear_instances(self) -> None:
        """Remove all registered maintainable instances."""
        self._state.instances_by_urn.clear()
        self._state.instances_by_key.clear()

    def _resolve_by_key(
        self, key: tuple[str | None, str | None, str | None]
    ) -> MaintainableBase | None:
        identifier = key[1]
        if identifier is None:
            return None

        # Prefer an exact match for agency and version when present.
        exact = self._state.instances_by_key.get((key[0], identifier, key[2]))
        if exact is not None:
            return exact

        for candidate_key, maintainable in self._state.instances_by_key.items():
            if candidate_key[1] != identifier:
                continue
            if key[2] is not None and candidate_key[2] != key[2]:
                continue
            if key[0] is not None and candidate_key[0] != key[0]:
                continue
            return maintainable
        return None

    def resolve(self, identifier: ResolveIdentifier) -> MaintainableBase | None:
        """Resolve ``identifier`` into a registered maintainable instance."""
        if isinstance(identifier, MaintainableBase):
            return identifier

        if isinstance(identifier, Reference):
            if identifier.urn:
                resolved = self._state.instances_by_urn.get(identifier.urn)
                if resolved is not None:
                    return resolved
            key = None
            if identifier.identifier:
                key = (identifier.agency, identifier.identifier, identifier.version)
            if key is not None:
                return self._resolve_by_key(key)
            return None

        if isinstance(identifier, str):
            return self._state.instances_by_urn.get(identifier)

        if isinstance(identifier, tuple):
            if len(identifier) != 3:
                raise ValueError(
                    "Identifier tuples must contain (agency, identifier, version)."
                )
            return self._resolve_by_key(identifier)

        raise TypeError(
            f"Unsupported maintainable identifier type: {type(identifier).__name__}."
        )


_REGISTRY = MaintainableRegistry()


def register_maintainable_alias(
    alias: str, maintainable_type: type[MaintainableBase]
) -> None:
    """Expose alias registration for maintainable classes."""
    _REGISTRY.register_alias(alias, maintainable_type)


def maintainable_type_from_name(type_name: str) -> type[MaintainableBase] | None:
    """Resolve ``type_name`` into the corresponding maintainable class."""
    return _REGISTRY.resolve_type(type_name)


def register_maintainable(maintainable: MaintainableBase) -> MaintainableBase:
    """Register ``maintainable`` for instance-level lookups."""
    return _REGISTRY.register_instance(maintainable)


def register_maintainables(maintainables: Iterable[MaintainableBase]) -> None:
    """Register each maintainable in ``maintainables`` for lookups."""
    _REGISTRY.register_instances(maintainables)


def unregister_maintainable(maintainable: MaintainableBase) -> None:
    """Remove ``maintainable`` from the registry when registered."""
    _REGISTRY.unregister_instance(maintainable)


def clear_registered_maintainables() -> None:
    """Clear all maintainable instances currently tracked by the registry."""
    _REGISTRY.clear_instances()


def resolve(identifier: ResolveIdentifier) -> MaintainableBase | None:
    """Return the maintainable registered for ``identifier`` when available."""
    return _REGISTRY.resolve(identifier)


def _register_default_aliases() -> None:
    """Register built-in shorthand aliases used throughout the project."""
    from .models.datacollection import QuestionItem
    from .models.study import StudyUnit

    register_maintainable_alias("studyu", StudyUnit)
    register_maintainable_alias("question", QuestionItem)


_register_default_aliases()
