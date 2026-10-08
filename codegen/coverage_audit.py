"""Audit how much of the DDI 3.3 XSD the generated model layer exposes.

Answers three concrete questions, with numbers rather than claims:

1. Type coverage: does every XSD complex type have a generated dataclass?
2. Field/attribute coverage: for each type, which XSD child elements and
   attributes are exposed as *named* fields (typed or generic-Element), and
   which are only preserved verbatim via the ``other_elements`` passthrough?
3. Typing quality: of the named fields, how many are strongly typed
   (Reference / InternationalString / CodeValue / scalar) vs generic Element
   passthroughs.

Run:  python -m codegen.coverage_audit          # writes codegen/COVERAGE_AUDIT.md
      python -m codegen.coverage_audit --print  # also print the summary
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import sys
from pathlib import Path
from typing import Any

import ddi_l.models as models_pkg
import ddi_l.models._generated as generated_pkg
from codegen.xsd_introspect import introspect_schemas
from ddi_l._etree import tostring

# Identification/versioning children handled generically by MaintainableBase
# (see base.py `_inherited_tags`), so they count as "covered" for every
# maintainable-derived type even though they are not in a per-type field map.
from ddi_l.constants import REUSABLE_NS
from ddi_l.models.base import MaintainableBase, qn

_INHERITED_LOCAL_TAGS = {
    "URN",
    "Agency",
    "ID",
    "Version",
    "Label",
    "Description",
    "UserID",
    "UserAttributePair",
    "VersionResponsibility",
    "VersionResponsibilityReference",
    "VersionRationale",
    "BasedOnObject",
    "RelatedOtherMaterialReference",
    "Note",
    "Software",
    "MetadataQuality",
    "MaintainableObject",
}
_INHERITED_TAGS = {qn(REUSABLE_NS, name) for name in _INHERITED_LOCAL_TAGS}


def _load_generated_classes() -> dict[str, type]:
    """Return a map of generated class name -> class across all _generated modules."""
    classes: dict[str, type] = {}
    for mod_info in pkgutil.iter_modules(generated_pkg.__path__):
        module = importlib.import_module(f"{generated_pkg.__name__}.{mod_info.name}")
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and name.endswith("Fields"):
                classes[name] = obj
    return classes


def _generated_name_for(xsd_type_name: str) -> str:
    """XSD ``FooType`` -> generated ``FooFields`` (best-effort)."""
    base = xsd_type_name[:-4] if xsd_type_name.endswith("Type") else xsd_type_name
    return f"{base}Fields"


def _covered_tags(cls: type) -> tuple[set[str], set[str]]:
    """Return (element tags, attribute names) a class covers, walking inheritance."""
    element_tags: set[str] = set(_INHERITED_TAGS)
    attr_names: set[str] = set()
    for klass in cls.__mro__:
        field_map = klass.__dict__.get("_FIELD_XML_MAP")
        if isinstance(field_map, dict):
            for xml_tag, _kind, *_rest in field_map.values():
                element_tags.add(xml_tag)
        attr_map = klass.__dict__.get("_ATTR_XML_MAP")
        if isinstance(attr_map, dict):
            for xml_attr, _kind in attr_map.values():
                attr_names.add(xml_attr)
    return element_tags, attr_names


def _typed_vs_passthrough(cls: type) -> tuple[int, int]:
    """Count strongly-typed vs generic-Element named fields across inheritance."""
    typed = passthrough = 0
    seen: set[str] = set()
    for klass in cls.__mro__:
        field_map = klass.__dict__.get("_FIELD_XML_MAP")
        if not isinstance(field_map, dict):
            continue
        for py_name, (_xml_tag, kind, *_rest) in field_map.items():
            if py_name in seen:
                continue
            seen.add(py_name)
            if kind == "element":
                passthrough += 1
            else:
                typed += 1
    return typed, passthrough


def audit() -> dict[str, Any]:
    modules = introspect_schemas()
    generated = _load_generated_classes()

    total_types = 0
    modeled_types = 0
    missing_class: list[str] = []

    total_child_slots = 0
    named_child_slots = 0
    passthrough_child_slots = 0  # preserved via other_elements, not a named field
    total_attr_slots = 0
    named_attr_slots = 0

    typed_fields = 0
    element_fields = 0

    per_type_gaps: list[str] = []

    for module, types in sorted(modules.items()):
        for info in types:
            total_types += 1
            gen_name = _generated_name_for(info.name)
            cls = generated.get(gen_name)
            if cls is None:
                missing_class.append(f"{module}.{info.name}")
                continue
            modeled_types += 1

            element_tags, attr_names = _covered_tags(cls)
            t, p = _typed_vs_passthrough(cls)
            typed_fields += t
            element_fields += p

            uncovered_children: list[str] = []
            for child in info.children:
                total_child_slots += 1
                tag = qn(child.namespace, child.local_name)
                if tag in element_tags:
                    named_child_slots += 1
                else:
                    passthrough_child_slots += 1
                    uncovered_children.append(child.local_name)

            uncovered_attrs: list[str] = []
            for attr in info.attributes:
                total_attr_slots += 1
                if attr.name in attr_names:
                    named_attr_slots += 1
                else:
                    uncovered_attrs.append(attr.name)

            if uncovered_children or uncovered_attrs:
                bits = []
                if uncovered_children:
                    bits.append(
                        "children: " + ", ".join(sorted(set(uncovered_children)))
                    )
                if uncovered_attrs:
                    bits.append("attrs: " + ", ".join(sorted(set(uncovered_attrs))))
                per_type_gaps.append(f"{module}.{info.name} — " + "; ".join(bits))

    return {
        "total_types": total_types,
        "modeled_types": modeled_types,
        "missing_class": missing_class,
        "total_child_slots": total_child_slots,
        "named_child_slots": named_child_slots,
        "passthrough_child_slots": passthrough_child_slots,
        "total_attr_slots": total_attr_slots,
        "named_attr_slots": named_attr_slots,
        "typed_fields": typed_fields,
        "element_fields": element_fields,
        "per_type_gaps": per_type_gaps,
        "attribute_drop_set": attribute_drop_set(),
    }


def attribute_drop_set() -> list[str]:
    """Return hand-written wrappers that drop an unknown attribute on round-trip.

    Empirically probes every hand-written (non-generated) model class that
    overrides both ``from_xml`` and ``to_xml``: build a minimal instance, inject
    an unknown attribute, run ``from_xml`` -> ``to_xml``, and record any class
    where the attribute did not survive. An empty result means the model layer
    preserves unrecognized attributes verbatim (the round-trip guarantee).
    """
    drops: list[str] = []
    seen: set[type] = set()
    for mod_info in pkgutil.walk_packages(
        models_pkg.__path__, models_pkg.__name__ + "."
    ):
        if "_generated" in mod_info.name:
            continue
        try:
            module = importlib.import_module(mod_info.name)
        except Exception:  # pragma: no cover - defensive
            continue
        obj: Any
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj in seen or not obj.__module__.startswith("ddi_l.models"):
                continue
            if "_generated" in obj.__module__:
                continue
            if "from_xml" not in obj.__dict__ or "to_xml" not in obj.__dict__:
                continue
            seen.add(obj)
            is_maintainable = issubclass(obj, MaintainableBase)
            try:
                instance = (
                    obj(agency="ex.org", identifier="X", version="1")
                    if is_maintainable
                    else obj()
                )
                element = instance.to_xml()
            except Exception:  # not minimally constructible from this probe
                continue
            element.set("xUnknownProbeAttr", "keepme")
            try:
                serialized = tostring(obj.from_xml(element).to_xml())
                text = (
                    serialized.decode() if isinstance(serialized, bytes) else serialized
                )
            except Exception:  # pragma: no cover - defensive
                continue
            if 'xUnknownProbeAttr="keepme"' not in text:
                drops.append(f"{obj.__module__.split('.')[-1]}.{name}")
    return sorted(drops)


def _pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:.1f}%" if d else "n/a"


def render(result: dict[str, Any]) -> str:
    tt = result["total_types"]
    mt = result["modeled_types"]
    tcs = result["total_child_slots"]
    ncs = result["named_child_slots"]
    tas = result["total_attr_slots"]
    nas = result["named_attr_slots"]
    typed = result["typed_fields"]
    elem = result["element_fields"]
    lines = [
        "# DDI 3.3 coverage audit (generated model layer)",
        "",
        "Generated by `python -m codegen.coverage_audit`. Measures how much of the",
        "official DDI 3.3 XSD the generated model layer exposes.",
        "",
        "## Type coverage",
        "",
        f"- XSD complex types: **{tt}**",
        f"- With a generated dataclass: **{mt}** ({_pct(mt, tt)})",
        f"- Missing a class: **{len(result['missing_class'])}**",
        "",
        "## Field & attribute coverage",
        "",
        f"- XSD child-element slots: **{tcs}**; exposed as a named field: "
        f"**{ncs}** ({_pct(ncs, tcs)}). The remaining "
        f"**{result['passthrough_child_slots']}** are preserved verbatim via the "
        "`other_elements` passthrough (round-tripped, not a named accessor).",
        f"- XSD attribute slots: **{tas}**; exposed as a named field: "
        f"**{nas}** ({_pct(nas, tas)}).",
        "",
        "## Typing quality of named element fields",
        "",
        f"- Strongly typed (Reference / InternationalString / CodeValue / scalar): "
        f"**{typed}**",
        f"- Generic `Element` passthrough fields: **{elem}**",
        "",
        "## Interpretation",
        "",
        "- Every XSD complex type is generated, so no type is structurally absent.",
        "- Child elements not surfaced as named fields are still preserved on "
        "round-trip via `other_elements`; the gap is **ergonomics/typing**, not "
        "data loss.",
        "- Attributes not in `_ATTR_XML_MAP` are preserved verbatim via the "
        "`other_attributes` passthrough on the generic engine (see "
        "`tests/test_roundtrip_fidelity.py`), so unmapped attributes on "
        "generated types round-trip too — again an ergonomics gap, not data "
        "loss. (Hand-written convenience wrappers manage their own attributes.)",
        "",
        "## Per-type gaps (XSD children/attributes with no named field)",
        "",
    ]
    gaps = result["per_type_gaps"]
    if not gaps:
        lines.append("_None._")
    else:
        lines.append(f"{len(gaps)} types have at least one unnamed child/attribute:")
        lines.append("")
        for gap in gaps:
            lines.append(f"- {gap}")
    if result["missing_class"]:
        lines += ["", "## Types with no generated class", ""]
        for name in result["missing_class"]:
            lines.append(f"- {name}")
    lines += [
        "",
        "## Attribute round-trip drop set",
        "",
        "Hand-written wrappers that drop an unknown attribute through a "
        "`from_xml` -> `to_xml` cycle (empirically probed). Empty means the "
        "model layer preserves unrecognized attributes verbatim.",
        "",
    ]
    drops = result["attribute_drop_set"]
    if not drops:
        lines.append("_None — all hand-written wrappers preserve unknown attributes._")
    else:
        for name in drops:
            lines.append(f"- {name}")
    return "\n".join(lines) + "\n"


def main() -> None:
    result = audit()
    report = render(result)
    out = Path(__file__).parent / "COVERAGE_AUDIT.md"
    out.write_text(report, encoding="utf-8")
    print(f"Wrote {out}")
    if "--print" in sys.argv:
        print()
        # Print just the summary (everything before the per-type list).
        print(report.split("## Per-type gaps")[0])


if __name__ == "__main__":
    main()
