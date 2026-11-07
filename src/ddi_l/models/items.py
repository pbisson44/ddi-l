"""Typed models for the Fragment item types with no hand-written model.

A ``ddi:Fragment`` can carry 161 kinds of item in DDI 3.3 -- every type a
Colectica repository can export. The hand-written models cover the common
ones; this module gives each of the rest a model built on its generated base,
so any item parses with `MaintainableBase.from_xml` and writes back
with ``to_xml``, read through the same generic engine as every
generated field.

Each model is registered for its tag, so
``MaintainableBase.for_tag("{ddi:conceptualcomponent:3_3}ConceptScheme")``
finds it. Most are exported here under the element's own name
(``ConceptScheme``, ``ManagedNumericRepresentation``, ...); where two
namespaces define an element of the same name (the four ``RecordLayout``
variants), the name carries its module (``NCubeInlineRecordLayout``).
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass

from ..constants import REUSABLE_NS
from ..registry import MaintainableRegistry
from ._generated.fragment_items import FRAGMENT_ITEM_TYPES
from .base import MaintainableBase, qn

__all__ = ["GENERIC_ITEM_MODELS", "generic_item_model"]

GENERIC_ITEM_MODELS: dict[str, type[MaintainableBase]] = {}

_MODULE_PREFIXES = {
    "physicaldataproduct_ncube_inline": "NCubeInline",
    "physicaldataproduct_ncube_normal": "NCubeNormal",
    "physicaldataproduct_ncube_tabular": "NCubeTabular",
    "physicaldataproduct_proprietary": "Proprietary",
}


# A Fragment may carry a whole DDIInstance, but that is the document wrapper
# (DDIDocument), not an item: registering it would make every reader that
# walks registered types (iterparse_ddi, the index) report the document itself.
_NOT_ITEMS = frozenset({"{ddi:instance:3_3}DDIInstance"})


def generic_item_model(tag: str) -> type[MaintainableBase] | None:
    """Return the generic model registered for ``tag``, if there is one."""
    return GENERIC_ITEM_MODELS.get(tag)


def _register() -> None:
    # Imported here: ddi_l.models imports this module after datacollection.
    from .datacollection import Binding, InParameter, OutParameter

    typed_parameters: dict[str, type] = {
        qn(REUSABLE_NS, "InParameter"): InParameter,
        qn(REUSABLE_NS, "OutParameter"): OutParameter,
        qn(REUSABLE_NS, "Binding"): Binding,
    }
    local_names: dict[str, int] = {}
    for tag in FRAGMENT_ITEM_TYPES:
        local = tag.split("}", 1)[1]
        local_names[local] = local_names.get(local, 0) + 1

    for tag, (module, class_name) in FRAGMENT_ITEM_TYPES.items():
        if MaintainableRegistry.get(tag) is not None or tag in _NOT_ITEMS:
            continue
        generated = importlib.import_module(f"{__package__}._generated.{module}")
        base = getattr(generated, class_name, None)
        if base is None:  # pragma: no cover - guarded by the codegen drift check
            continue
        local = tag.split("}", 1)[1]
        name = local
        if local_names[local] > 1 or local in globals():
            name = _MODULE_PREFIXES.get(module, module.title()) + local
        namespace: dict[str, object] = {
            "TAG": tag,
            "__module__": __name__,
            "__qualname__": name,
            "__doc__": f"Typed model for ``{local}`` items (``{tag}``).",
        }
        # Parameters and bindings are read as the typed models, as on the
        # hand-written constructs (the annotations stay list[Element]).
        typed = {
            field_name: typed_parameters[child_tag]
            for field_name, (child_tag, _kind, _is_list) in getattr(
                base, "_FIELD_XML_MAP", {}
            ).items()
            if child_tag in typed_parameters
        }
        if typed:
            namespace["_TYPED_CHILDREN"] = typed
        model = type(name, (base,), namespace)
        model = dataclass(model)
        GENERIC_ITEM_MODELS[tag] = model
        globals()[name] = model
        __all__.append(name)


_register()
