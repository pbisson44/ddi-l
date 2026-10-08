"""High-level wrapper for ``pr:DDIProfile`` (DDIInstance-level).

A DDI profile declares which DDI elements an agency/system uses for a given
purpose. Serialization is handled by the generated base (in the
``ddi:ddiprofile:3_3`` namespace); this wrapper adds the ``Used`` / ``NotUsed``
helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import DDI_PROFILE_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.ddiprofile import DDIProfileFields
from .base import qn

__all__ = ["DDI_PROFILE_NS", "DDIProfile"]


@dataclass
class DDIProfile(DDIProfileFields):
    """Declares which DDI elements a system uses (a profile of usage).

    Build one with :meth:`ddi_l.document.Document.add_ddi_profile` and list the
    elements it relies on with :meth:`add_used` / :meth:`add_not_used`.
    """

    TAG: ClassVar[str] = qn(DDI_PROFILE_NS, "DDIProfile")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pr")

    @classmethod
    def from_xml(cls, element: Element) -> DDIProfile:
        """Parse a ``DDIProfile``, normalizing the ddiprofile prefix to ``pr``.

        Documents written before the ``pr`` binding used an auto-generated
        prefix (e.g. ``p0``) for the ddiprofile namespace, which ``from_xml``
        would otherwise preserve in ``_nsmap_override`` and re-emit on save.
        Rebind that namespace to the stable ``pr`` prefix so open/edit/save
        migrates existing profile documents too.
        """
        obj = super().from_xml(element)
        if obj._nsmap_override:
            obj._nsmap_override = {
                prefix: uri
                for prefix, uri in obj._nsmap_override.items()
                if uri != DDI_PROFILE_NS
            }
            obj._nsmap_override["pr"] = DDI_PROFILE_NS
        return obj

    def add_used(self, xpath: str, *, is_required: bool = False) -> Element:
        """Declare that the element at ``xpath`` is used. Returns the element."""
        used = create_element(qn(DDI_PROFILE_NS, "Used"))
        used.set("xpath", xpath)
        if is_required:
            used.set("isRequired", "true")
        self.useds.append(used)
        return used

    def add_not_used(self, xpath: str) -> Element:
        """Declare that the element at ``xpath`` is not used. Returns it."""
        not_used = create_element(qn(DDI_PROFILE_NS, "NotUsed"))
        not_used.set("xpath", xpath)
        self.not_useds.append(not_used)
        return not_used
