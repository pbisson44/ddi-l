"""Mixins encapsulating namespace utilities for DDI documents."""

from __future__ import annotations

from collections.abc import Mapping

from ._etree import Element
from .constants import DEFAULT_NSMAP
from .namespace_utils import apply_namespace_map, build_namespace_map
from .namespaces import NamespaceProfileLike


class NamespaceManagementMixin:
    """Provide namespace synchronisation helpers for document-like wrappers."""

    _root: Element

    def ensure_namespace_prefixes(
        self,
        profile_or_map: NamespaceProfileLike | Mapping[str | None, str] | None = None,
        *,
        extra_namespaces: Mapping[str | None, str] | None = None,
    ) -> None:
        """Ensure namespace prefixes exist on the document root.

        Args:
            profile_or_map: Either a namespace profile identifier, a
                :class:`~ddi_l.namespaces.NamespaceProfileLike`, or a mapping
                of prefix-to-URI bindings that should be declared on the
                instance root.
            extra_namespaces: Additional prefix-to-URI bindings to merge on top
                of the defaults and ``profile_or_map`` values.

        Returns:
            None: The document is updated in place to include the required
                namespace declarations.
        """
        default_nsmap: Mapping[str | None, str] = DEFAULT_NSMAP

        nsmap = build_namespace_map(
            profile_or_map,
            extra_namespaces=extra_namespaces,
            base=default_nsmap,
        )

        self._root = apply_namespace_map(self._root, nsmap, preserve_existing=True)
        self._declared_namespaces = dict(nsmap)


__all__ = ["NamespaceManagementMixin"]
