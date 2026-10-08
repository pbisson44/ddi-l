"""Convenience methods for querying and manipulating DDI documents.

This module provides mixin classes that add high-level query and
manipulation capabilities to DDIDocument.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
)

if TYPE_CHECKING:
    from ._etree import Element
    from .index import Index
    from .models.base import MaintainableBase, Reference
    from .models.concept import Concept
    from .models.datacollection import QuestionItem
    from .models.logicalproduct import CodeList, Variable

__all__ = [
    "DocumentManipulationMixin",
    "DocumentQueryMixin",
]

T = TypeVar("T", bound="MaintainableBase")


class DocumentQueryMixin:
    """Mixin providing query convenience methods for DDI documents.

    This mixin adds methods for finding maintainables by various criteria,
    resolving references, and navigating document structure.

    Requires:
        - self._root: Element
        - self._index: Optional[Index]
        - self.iter_maintainables(): Iterator[MaintainableBase]
    """

    # These are defined by the class this mixin is added to
    _root: Element
    _index: Index | None

    def iter_maintainables(
        self, *types: type[MaintainableBase]
    ) -> Iterator[MaintainableBase]:
        """Iterate over maintainables, optionally filtered by type."""
        raise NotImplementedError("Subclass must implement iter_maintainables")

    # ========== Find by identifier ==========

    def find_by_identifier(
        self,
        identifier: str,
        type_filter: type[T] | None = None,
    ) -> T | None:
        """Find a maintainable by its identifier.

        Args:
            identifier: The identifier to search for.
            type_filter: Optional type to restrict search.

        Returns:
            The matching maintainable, or None if not found.

        Example:
            >>> var = doc.find_by_identifier("age-var", Variable)
        """
        types = (type_filter,) if type_filter else ()
        for maintainable in self.iter_maintainables(*types):
            if maintainable.identifier == identifier:
                return maintainable  # type: ignore
        return None

    def find_by_urn(
        self,
        urn: str,
        type_filter: type[T] | None = None,
    ) -> T | None:
        """Find a maintainable by its URN.

        Args:
            urn: The URN to search for.
            type_filter: Optional type to restrict search.

        Returns:
            The matching maintainable, or None if not found.
        """
        types = (type_filter,) if type_filter else ()
        for maintainable in self.iter_maintainables(*types):
            if maintainable.urn == urn:
                return maintainable  # type: ignore
            # Check computed URN
            if maintainable.agency and maintainable.identifier and maintainable.version:
                computed = (
                    f"urn:ddi:{maintainable.agency}"
                    f":{maintainable.identifier}"
                    f":{maintainable.version}"
                )
                if computed.lower() == urn.lower():
                    return maintainable  # type: ignore
        return None

    # ========== Find by label/text ==========

    def find_by_label(
        self,
        text: str,
        type_filter: type[T] | None = None,
        *,
        exact: bool = False,
        case_sensitive: bool = False,
    ) -> list[T]:
        """Find maintainables with matching label text.

        Args:
            text: The text to search for in labels.
            type_filter: Optional type to restrict search.
            exact: If True, require exact match. If False, search as substring.
            case_sensitive: Whether to match case.

        Returns:
            List of matching maintainables.

        Example:
            >>> vars = doc.find_by_label("age", Variable)
            >>> vars = doc.find_by_label(
            ...     "Age", Variable, exact=True, case_sensitive=True
            ... )
        """
        results: list[T] = []
        types = (type_filter,) if type_filter else ()

        search_text = text if case_sensitive else text.lower()

        for maintainable in self.iter_maintainables(*types):
            for label in getattr(maintainable, "labels", []):
                label_text = getattr(label, "text", "") or ""
                compare_text = label_text if case_sensitive else label_text.lower()

                if exact:
                    if compare_text == search_text:
                        results.append(maintainable)  # type: ignore
                        break
                else:
                    if search_text in compare_text:
                        results.append(maintainable)  # type: ignore
                        break

        return results

    def find_by_name(
        self,
        text: str,
        type_filter: type[T] | None = None,
        *,
        exact: bool = False,
        case_sensitive: bool = False,
    ) -> list[T]:
        """Find maintainables with matching name text.

        Similar to find_by_label but searches the 'names' attribute
        common on Concept, Variable, etc.

        Args:
            text: The text to search for in names.
            type_filter: Optional type to restrict search.
            exact: If True, require exact match.
            case_sensitive: Whether to match case.

        Returns:
            List of matching maintainables.
        """
        results: list[T] = []
        types = (type_filter,) if type_filter else ()

        search_text = text if case_sensitive else text.lower()

        for maintainable in self.iter_maintainables(*types):
            for name in getattr(maintainable, "names", []):
                name_text = getattr(name, "text", "") or ""
                compare_text = name_text if case_sensitive else name_text.lower()

                if exact:
                    if compare_text == search_text:
                        results.append(maintainable)  # type: ignore
                        break
                else:
                    if search_text in compare_text:
                        results.append(maintainable)  # type: ignore
                        break

        return results

    # ========== Type-specific shortcuts ==========

    @property
    def variables(self) -> MaintainableAccessor[Variable]:
        """Access variables in the document.

        Example:
            >>> var = doc.variables["age"]  # by identifier
            >>> all_vars = list(doc.variables)  # iterate all
            >>> count = len(doc.variables)  # count
        """
        from .models.logicalproduct import Variable

        return MaintainableAccessor(self, Variable)

    @property
    def questions(self) -> MaintainableAccessor[QuestionItem]:
        """Access questions in the document.

        Example:
            >>> q = doc.questions["q1"]
            >>> all_qs = list(doc.questions)
        """
        from .models.datacollection import QuestionItem

        return MaintainableAccessor(self, QuestionItem)

    @property
    def concepts(self) -> MaintainableAccessor[Concept]:
        """Access concepts in the document."""
        from .models.concept import Concept

        return MaintainableAccessor(self, Concept)

    @property
    def code_lists(self) -> MaintainableAccessor[CodeList]:
        """Access code lists in the document."""
        from .models.logicalproduct import CodeList

        return MaintainableAccessor(self, CodeList)

    # ========== Reference resolution ==========

    def resolve_reference(
        self,
        ref: Reference,
    ) -> MaintainableBase | None:
        """Resolve a reference to its target maintainable.

        Args:
            ref: The reference to resolve.

        Returns:
            The target maintainable, or None if not found.

        Example:
            >>> concept = doc.resolve_reference(variable.concept_reference)
        """
        if ref.urn:
            return self.find_by_urn(ref.urn)

        if ref.identifier:
            # Try to find by identifier with version matching
            for maintainable in self.iter_maintainables():
                if maintainable.identifier != ref.identifier:
                    continue
                if ref.agency and maintainable.agency != ref.agency:
                    continue
                if ref.version and maintainable.version != ref.version:
                    continue
                return maintainable

        return None

    def find_references_to(
        self,
        target: MaintainableBase,
    ) -> list[Reference]:
        """Find all references pointing to a maintainable.

        Args:
            target: The maintainable to find references to.

        Returns:
            List of References that point to the target.
        """
        from .models.base import Reference

        target_urn = target.urn
        if not target_urn and target.agency and target.identifier and target.version:
            target_urn = f"urn:ddi:{target.agency}:{target.identifier}:{target.version}"

        references: list[Reference] = []

        def _check_reference(ref: Reference) -> bool:
            if ref.urn and target_urn and ref.urn.lower() == target_urn.lower():
                return True
            return bool(
                ref.agency == target.agency
                and ref.identifier == target.identifier
                and ref.version == target.version
            )

        def _scan_object(obj: Any, seen: set[int]) -> None:
            obj_id = id(obj)
            if obj_id in seen:
                return
            seen.add(obj_id)

            if isinstance(obj, Reference):
                if _check_reference(obj):
                    references.append(obj)
                return

            if hasattr(obj, "__dataclass_fields__"):
                for field_name in obj.__dataclass_fields__:
                    value = getattr(obj, field_name, None)
                    _scan_object(value, seen)
            elif isinstance(obj, list):
                for item in obj:
                    _scan_object(item, seen)
            elif isinstance(obj, dict):
                for value in obj.values():
                    _scan_object(value, seen)

        for maintainable in self.iter_maintainables():
            if maintainable is target:
                continue
            _scan_object(maintainable, set())

        return references

    # ========== Filtering ==========

    def filter(
        self,
        predicate: Callable[[MaintainableBase], bool],
        type_filter: type[T] | None = None,
    ) -> list[T]:
        """Filter maintainables using a predicate function.

        Args:
            predicate: Function that returns True for matching items.
            type_filter: Optional type to restrict search.

        Returns:
            List of matching maintainables.

        Example:
            >>> recent = doc.filter(lambda m: m.version.startswith("2."))
            >>> labeled = doc.filter(lambda m: len(m.labels) > 0, Variable)
        """
        types = (type_filter,) if type_filter else ()
        return [m for m in self.iter_maintainables(*types) if predicate(m)]  # type: ignore

    def filter_by_agency(
        self,
        agency: str,
        type_filter: type[T] | None = None,
    ) -> list[T]:
        """Find all maintainables from a specific agency."""
        return self.filter(lambda m: m.agency == agency, type_filter)

    def filter_by_version(
        self,
        version: str,
        type_filter: type[T] | None = None,
    ) -> list[T]:
        """Find all maintainables with a specific version."""
        return self.filter(lambda m: m.version == version, type_filter)


class MaintainableAccessor(Generic[T]):
    """Dictionary-like accessor for maintainables of a specific type.

    Provides convenient access patterns:
        accessor["id"]      # Get by identifier
        accessor.get("id")  # Get with None default
        iter(accessor)      # Iterate all
        len(accessor)       # Count
        "id" in accessor    # Check existence
    """

    def __init__(self, document: DocumentQueryMixin, type_class: type[T]):
        self._document = document
        self._type_class = type_class

    def __getitem__(self, identifier: str) -> T:
        """Get maintainable by identifier, raising KeyError if not found."""
        result = self._document.find_by_identifier(identifier, self._type_class)
        if result is None:
            raise KeyError(f"{self._type_class.__name__} not found: {identifier}")
        return result

    def get(self, identifier: str, default: T | None = None) -> T | None:
        """Get maintainable by identifier with default."""
        return (
            self._document.find_by_identifier(identifier, self._type_class) or default
        )

    def __iter__(self) -> Iterator[T]:
        """Iterate all maintainables of this type."""
        return iter(self._document.iter_maintainables(self._type_class))  # type: ignore

    def __len__(self) -> int:
        """Count maintainables of this type."""
        return sum(1 for _ in self._document.iter_maintainables(self._type_class))

    def __contains__(self, identifier: str) -> bool:
        """Check if an identifier exists."""
        return (
            self._document.find_by_identifier(identifier, self._type_class) is not None
        )

    def find(self, text: str, *, exact: bool = False) -> list[T]:
        """Find by label text."""
        return self._document.find_by_label(text, self._type_class, exact=exact)

    def all(self) -> list[T]:
        """Get all maintainables of this type as a list."""
        return list(self)


class DocumentManipulationMixin:
    """Mixin providing manipulation convenience methods for DDI documents.

    This mixin adds methods for bulk operations, transformations,
    and document-level changes.

    Requires:
        - self._root: Element
        - self.add_maintainable()
        - self.remove_maintainable()
        - self.iter_maintainables()
    """

    _root: Element

    def iter_maintainables(
        self, *types: type[MaintainableBase]
    ) -> Iterator[MaintainableBase]:
        """Iterate over maintainables, optionally filtered by type."""
        raise NotImplementedError("Subclass must implement iter_maintainables")

    def remove_maintainable(self, maintainable: MaintainableBase) -> bool:
        """Remove a maintainable from the document."""
        raise NotImplementedError("Subclass must implement remove_maintainable")

    def bulk_update_agency(
        self,
        old_agency: str,
        new_agency: str,
        *,
        update_references: bool = True,
    ) -> int:
        """Update agency for all maintainables from old to new.

        Args:
            old_agency: The agency to replace.
            new_agency: The new agency value.
            update_references: Also update references to these maintainables.

        Returns:
            Number of maintainables updated.
        """
        count = 0

        for maintainable in self.iter_maintainables():
            if maintainable.agency == old_agency:
                maintainable.agency = new_agency
                count += 1

                # Update URN if present
                if maintainable.urn:
                    parts = maintainable.urn.split(":")
                    if len(parts) >= 3:
                        parts[2] = new_agency
                        maintainable.urn = ":".join(parts)

        if update_references:
            self._update_references_agency(old_agency, new_agency)

        return count

    def _update_references_agency(self, old_agency: str, new_agency: str) -> None:
        """Update agency in all references."""
        from .models.base import Reference

        def _update(obj: Any, seen: set[int]) -> None:
            obj_id = id(obj)
            if obj_id in seen:
                return
            seen.add(obj_id)

            if isinstance(obj, Reference):
                if obj.agency == old_agency:
                    obj.agency = new_agency
                return

            if hasattr(obj, "__dataclass_fields__"):
                for field_name in obj.__dataclass_fields__:
                    value = getattr(obj, field_name, None)
                    _update(value, seen)
            elif isinstance(obj, list):
                for item in obj:
                    _update(item, seen)

        for maintainable in self.iter_maintainables():
            _update(maintainable, set())

    def increment_all_versions(
        self,
        component: str = "minor",
        type_filter: type | None = None,
    ) -> int:
        """Increment version for all (or filtered) maintainables.

        Args:
            component: Which version component: "major", "minor", or "patch".
            type_filter: Optional type to restrict update.

        Returns:
            Number of maintainables updated.
        """
        count = 0
        types = (type_filter,) if type_filter else ()

        for maintainable in self.iter_maintainables(*types):
            if component == "major":
                maintainable.increment_major_version()
            elif component == "minor":
                maintainable.increment_minor_version()
            else:
                maintainable.increment_subversion()
            count += 1

        return count

    def remove_by_identifier(
        self,
        identifier: str,
        type_filter: type | None = None,
    ) -> bool:
        """Remove a maintainable by identifier.

        Args:
            identifier: The identifier to remove.
            type_filter: Optional type restriction.

        Returns:
            True if removed, False if not found.
        """
        target = None
        types = (type_filter,) if type_filter else ()

        for maintainable in self.iter_maintainables(*types):
            if maintainable.identifier == identifier:
                target = maintainable
                break

        if target:
            return self.remove_maintainable(target)
        return False

    def remove_all(
        self,
        type_filter: type,
    ) -> int:
        """Remove all maintainables of a specific type.

        Args:
            type_filter: The type of maintainables to remove.

        Returns:
            Number of maintainables removed.
        """
        to_remove = list(self.iter_maintainables(type_filter))
        count = 0
        for maintainable in to_remove:
            if self.remove_maintainable(maintainable):
                count += 1
        return count

    def clone_maintainable(
        self,
        source: MaintainableBase,
        *,
        new_identifier: str | None = None,
        new_version: str | None = None,
        add_to_document: bool = True,
    ) -> MaintainableBase:
        """Create a copy of a maintainable with new identification.

        Args:
            source: The maintainable to clone.
            new_identifier: New identifier (generates UUID if not provided).
            new_version: New version (defaults to "1.0").
            add_to_document: Whether to add the clone to this document.

        Returns:
            The cloned maintainable.
        """
        import copy
        from uuid import uuid4

        clone = copy.deepcopy(source)
        clone.identifier = new_identifier or str(uuid4())
        clone.version = new_version or "1.0"
        clone.urn = None  # Clear URN so it's regenerated

        if add_to_document:
            self.add_maintainable(clone)

        return clone

    def add_maintainable(self, maintainable: MaintainableBase) -> None:
        """Add a maintainable to the document."""
        raise NotImplementedError("Subclass must implement add_maintainable")

    def merge_from(
        self,
        other_document: DocumentManipulationMixin,
        *,
        overwrite: bool = False,
        type_filter: type | None = None,
    ) -> int:
        """Merge maintainables from another document.

        Args:
            other_document: The source document to merge from.
            overwrite: If True, overwrite existing maintainables with same ID.
            type_filter: Optional type to restrict what's merged.

        Returns:
            Number of maintainables added/updated.
        """
        import copy

        count = 0
        types = (type_filter,) if type_filter else ()

        for maintainable in other_document.iter_maintainables(*types):
            existing = None
            for m in self.iter_maintainables():
                if (
                    m.identifier == maintainable.identifier
                    and m.agency == maintainable.agency
                ):
                    existing = m
                    break

            if existing:
                if overwrite:
                    self.remove_maintainable(existing)
                    self.add_maintainable(copy.deepcopy(maintainable))
                    count += 1
            else:
                self.add_maintainable(copy.deepcopy(maintainable))
                count += 1

        return count


class DocumentStatsMixin:
    """Mixin providing statistics and summary methods."""

    def iter_maintainables(
        self, *types: type[MaintainableBase]
    ) -> Iterator[MaintainableBase]:
        """Iterate over maintainables, optionally filtered by type."""
        raise NotImplementedError("Subclass must implement iter_maintainables")

    def summary(self) -> dict[str, Any]:
        """Generate a summary of document contents.

        Returns:
            Dictionary with counts and basic statistics.
        """
        from collections import Counter

        type_counts: Counter[str] = Counter()
        agency_counts: Counter[str] = Counter()
        version_counts: Counter[str] = Counter()
        total = 0

        for maintainable in self.iter_maintainables():
            type_name = type(maintainable).__name__
            type_counts[type_name] += 1

            if maintainable.agency:
                agency_counts[maintainable.agency] += 1
            if maintainable.version:
                version_counts[maintainable.version] += 1

            total += 1

        return {
            "total_maintainables": total,
            "by_type": dict(type_counts),
            "by_agency": dict(agency_counts),
            "by_version": dict(version_counts),
            "unique_agencies": len(agency_counts),
            "unique_versions": len(version_counts),
        }

    def type_counts(self) -> dict[str, int]:
        """Get counts of each maintainable type."""
        from collections import Counter

        counts: Counter[str] = Counter()
        for maintainable in self.iter_maintainables():
            counts[type(maintainable).__name__] += 1
        return dict(counts)

    def print_summary(self) -> None:
        """Print a human-readable summary to stdout."""
        stats = self.summary()

        print("DDI Document Summary")
        print("=" * 40)
        print(f"Total maintainables: {stats['total_maintainables']}")
        print(f"Unique agencies: {stats['unique_agencies']}")
        print(f"Unique versions: {stats['unique_versions']}")
        print()
        print("By Type:")
        for type_name, count in sorted(stats["by_type"].items()):
            print(f"  {type_name}: {count}")
