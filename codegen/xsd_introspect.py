"""Introspect DDI 3.3 XSD schemas via xmlschema and produce a structured
catalog of all complex types, their child elements, attributes, cardinalities,
and inheritance chains.

This is the first step of the code-generation pipeline: XSD → structured dict.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import xmlschema
from xmlschema.validators import (
    XMLSchemaBase,
    XsdComplexType,
    XsdElement,
    XsdGroup,
    XsdType,
)

SCHEMA_DIR = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "ddi_l"
    / "schemas"
    / "ddi"
    / "v3_3"
)
ENTRY_SCHEMA = SCHEMA_DIR / "instance_3_3.xsd"

# DDI namespaces we care about (skip XHTML, DC, xml)
DDI_NS_PREFIXES = {
    "ddi:instance:3_3": "instance",
    "ddi:reusable:3_3": "reusable",
    "ddi:studyunit:3_3": "studyunit",
    "ddi:datacollection:3_3": "datacollection",
    "ddi:logicalproduct:3_3": "logicalproduct",
    "ddi:physicaldataproduct:3_3": "physicaldataproduct",
    "ddi:physicalinstance:3_3": "physicalinstance",
    "ddi:archive:3_3": "archive",
    "ddi:group:3_3": "group",
    "ddi:conceptualcomponent:3_3": "conceptualcomponent",
    "ddi:comparative:3_3": "comparative",
    "ddi:dataset:3_3": "dataset",
    "ddi:ddiprofile:3_3": "ddiprofile",
    "ddi:physicaldataproduct_ncube_inline:3_3": "physicaldataproduct_ncube_inline",
    "ddi:physicaldataproduct_ncube_normal:3_3": "physicaldataproduct_ncube_normal",
    "ddi:physicaldataproduct_ncube_tabular:3_3": "physicaldataproduct_ncube_tabular",
    "ddi:physicaldataproduct_proprietary:3_3": "physicaldataproduct_proprietary",
}


@dataclass
class ChildElement:
    """A child element within a complex type."""

    name: str
    namespace: str
    local_name: str
    type_name: str | None
    type_namespace: str | None
    min_occurs: int
    max_occurs: int | None  # None = unbounded
    is_reference: bool  # element name ends with "Reference"
    documentation: str = ""


@dataclass
class Attribute:
    """An attribute on a complex type."""

    name: str
    type_name: str | None
    required: bool
    default: str | None = None


@dataclass
class ComplexTypeInfo:
    """Full description of an XSD complex type."""

    name: str
    namespace: str
    module: str  # e.g., "logicalproduct", "reusable"
    base_type: str | None = None
    base_namespace: str | None = None
    is_abstract: bool = False
    mixed: bool = False
    documentation: str = ""
    children: list[ChildElement] = field(default_factory=list)
    attributes: list[Attribute] = field(default_factory=list)
    # Inheritance chain (immediate base up to root)
    inheritance_chain: list[str] = field(default_factory=list)
    # All child element tags in XSD-declared order (including inherited)
    all_element_order: list[str] = field(default_factory=list)


def _collect_all_schemas(entry: Path) -> dict[str, XMLSchemaBase]:
    """Load the entry schema and recursively collect all imported schemas."""
    root = xmlschema.XMLSchema(str(entry))
    schemas: dict[str, XMLSchemaBase] = {}

    def _walk(s: XMLSchemaBase | None) -> None:
        if s is None:
            return
        ns = s.target_namespace
        if ns in schemas:
            return
        schemas[ns] = s
        for _, imp in s.imports.items():
            _walk(imp)

    _walk(root)
    return schemas


def _get_doc(xsd_obj) -> str:
    """Extract xs:documentation text from an XSD object."""
    ann = getattr(xsd_obj, "annotation", None)
    if ann is None:
        return ""
    doc = getattr(ann, "documentation", None)
    if doc is None:
        return ""
    if isinstance(doc, list):
        parts = []
        for d in doc:
            text = getattr(d, "text", None) or ""
            if text:
                parts.append(text.strip())
        return " ".join(parts)
    text = getattr(doc, "text", None) or str(doc)
    return text.strip() if text else ""


def _resolve_type_name(xsd_type: XsdType | None) -> tuple[str | None, str | None]:
    """Return (type_name, namespace) for an XSD type."""
    if xsd_type is None:
        return None, None
    name = getattr(xsd_type, "local_name", None) or getattr(xsd_type, "name", None)
    ns = getattr(xsd_type, "target_namespace", None)
    return name, ns


_NOT_SET = object()  # Sentinel for "no parent cardinality override"


def _walk_group_elements(
    group: XsdGroup,
    *,
    _parent_unbounded: bool = False,
) -> list[ChildElement]:
    """Recursively walk an XsdGroup (sequence/choice/all) and collect child elements.

    When a choice or sequence group has ``maxOccurs="unbounded"``, propagate
    that to each child element so that the resulting :class:`ChildElement`
    objects accurately reflect that the element can appear many times.
    """
    # Detect if THIS group is unbounded (maxOccurs is None → unbounded)
    group_max = getattr(group, "max_occurs", 1)
    is_unbounded = _parent_unbounded or group_max is None

    children: list[ChildElement] = []
    for item in group:
        if isinstance(item, XsdElement):
            resolved = item
            type_name, type_ns = _resolve_type_name(resolved.type)
            local = resolved.local_name or ""
            ns = resolved.target_namespace or ""
            doc = _get_doc(resolved)

            elem_min = resolved.min_occurs if resolved.min_occurs is not None else 1
            elem_max = resolved.max_occurs

            # Propagate unbounded parent group cardinality
            if is_unbounded and elem_max is not None and elem_max <= 1:
                elem_max = None  # unbounded
                elem_min = 0  # inside an unbounded group, min is effectively 0

            children.append(
                ChildElement(
                    name=f"{{{ns}}}{local}" if ns else local,
                    namespace=ns,
                    local_name=local,
                    type_name=type_name,
                    type_namespace=type_ns,
                    min_occurs=elem_min,
                    max_occurs=elem_max,
                    is_reference=local.endswith("Reference"),
                    documentation=doc[:200] if doc else "",
                )
            )
        elif isinstance(item, XsdGroup):
            children.extend(_walk_group_elements(item, _parent_unbounded=is_unbounded))
    return children


def _extract_attributes(xsd_type: XsdComplexType) -> list[Attribute]:
    """Extract attributes from a complex type."""
    attrs: list[Attribute] = []
    for attr in xsd_type.attributes.values():
        type_name, _ = _resolve_type_name(attr.type)
        attrs.append(
            Attribute(
                name=attr.local_name or "",
                type_name=type_name,
                required=attr.use == "required",
                default=attr.default,
            )
        )
    return attrs


def _build_inheritance_chain(xsd_type: XsdComplexType) -> list[str]:
    """Build the inheritance chain from immediate base to root."""
    chain: list[str] = []
    current = xsd_type.base_type
    visited = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        name = getattr(current, "local_name", None) or getattr(current, "name", None)
        ns = getattr(current, "target_namespace", "")
        if name and not name.startswith("anyType"):
            chain.append(f"{{{ns}}}{name}" if ns else name)
        current = getattr(current, "base_type", None)
    return chain


def _collect_all_element_tags(xsd_type: XsdComplexType) -> list[str]:
    """Collect all child element tags in XSD-declared order, including inherited.

    Walks the full content model (base types first, then extensions) to produce
    an ordered list of ``{namespace}localName`` tags.
    """
    content = xsd_type.content
    if not isinstance(content, XsdGroup):
        return []
    children = _walk_group_elements(content)
    return [c.name for c in children]


def introspect_schemas(entry: Path = ENTRY_SCHEMA) -> dict[str, list[ComplexTypeInfo]]:
    """Introspect all DDI 3.3 schemas and return complex type info grouped by module.

    Returns a dict mapping module name (e.g., "logicalproduct") to a list of
    ComplexTypeInfo objects.
    """
    schemas = _collect_all_schemas(entry)
    result: dict[str, list[ComplexTypeInfo]] = {}

    for ns, schema in sorted(schemas.items()):
        module = DDI_NS_PREFIXES.get(ns)
        if module is None:
            continue

        types_list: list[ComplexTypeInfo] = []
        for type_name, xsd_type in sorted(schema.types.items()):
            if not isinstance(xsd_type, XsdComplexType):
                continue

            base_name, base_ns = _resolve_type_name(xsd_type.base_type)
            doc = _get_doc(xsd_type)

            info = ComplexTypeInfo(
                name=type_name,
                namespace=ns,
                module=module,
                base_type=base_name,
                base_namespace=base_ns,
                is_abstract=xsd_type.abstract,
                mixed=xsd_type.mixed,
                documentation=doc[:300] if doc else "",
                inheritance_chain=_build_inheritance_chain(xsd_type),
                all_element_order=_collect_all_element_tags(xsd_type),
            )

            # Collect child elements from content model
            content = xsd_type.content
            if isinstance(content, XsdGroup):
                info.children = _walk_group_elements(content)

            # Collect attributes
            info.attributes = _extract_attributes(xsd_type)

            types_list.append(info)

        if types_list:
            result[module] = types_list

    return result


LABEL_TAG = "{ddi:reusable:3_3}Label"


def collect_label_slot_tags(entry: Path = ENTRY_SCHEMA) -> list[str]:
    """Return the global element tags whose content model permits ``r:Label``.

    Lint needs to distinguish "this item is missing a label" from "this item
    cannot carry a label at all". For elements backed by a generated model the
    answer is in ``_ELEMENT_ORDER``, but many DDI elements have no model, and
    a duck-type on ``Agency``/``ID``/``Version`` cannot tell a Maintainable
    from any other Identifiable -- ``l:Code`` extends ``r:IdentifiableType``
    and carries all three, yet ``CodeType`` declares no ``r:Label``.

    Returns:
        Sorted ``{namespace}localName`` tags, for elements only. An element
        whose type is simple is omitted: it has no content model to search.
    """
    schemas = _collect_all_schemas(entry)
    tags: set[str] = set()

    for namespace, schema in schemas.items():
        if namespace not in DDI_NS_PREFIXES:
            continue
        for element_name, element in schema.elements.items():
            element_type = element.type
            if not isinstance(element_type, XsdComplexType):
                continue
            if LABEL_TAG in _collect_all_element_tags(element_type):
                tags.add(f"{{{namespace}}}{element_name}")

    return sorted(tags)


def collect_fixed_attributes_by_element(
    entry: Path = ENTRY_SCHEMA,
) -> dict[str, dict[str, list[str]]]:
    """Return, per element tag, the attributes the schema pins to a value.

    Keyed by element rather than by attribute name, because a name alone is not
    enough to decide. ``type`` is pinned to ``"ID"`` on ``r:ID`` and to
    ``"URN"`` on ``r:URN``, but three DDI types (``KindOfDataType``,
    ``RelatedValueType``, ``DataFingerprintType``) declare an ordinary ``type``,
    and the bundled XHTML schema declares one on ``xhtml:a`` whose value is a
    MIME type -- ``type="ID"`` is meaningful there. Dropping by name and value
    would delete all of those.

    Returns:
        ``{element tag: {attribute name: sorted fixed values}}``, for elements
        in DDI namespaces that declare at least one pinned attribute.
    """
    schemas = _collect_all_schemas(entry)
    by_element: dict[str, dict[str, set[str]]] = {}

    for namespace, schema in schemas.items():
        if namespace not in DDI_NS_PREFIXES:
            continue
        for component in schema.iter_components():
            if not isinstance(component, XsdElement):
                continue
            tag = component.name
            if not tag or not tag.startswith("{"):
                continue
            attributes = getattr(component.type, "attributes", None) or {}
            for name, attribute in attributes.items():
                value = getattr(attribute, "fixed", None)
                if name and value is not None:
                    by_element.setdefault(tag, {}).setdefault(name, set()).add(
                        str(value)
                    )

    return {
        tag: {name: sorted(values) for name, values in sorted(attributes.items())}
        for tag, attributes in sorted(by_element.items())
    }


def collect_fixed_attribute_names(entry: Path = ENTRY_SCHEMA) -> dict[str, list[str]]:
    """Return the names of attributes the schema pins to a ``fixed`` value.

    A ``fixed`` attribute can only hold the value the schema mandates, so it
    carries no information. xmlschema materializes them when decoding to JSON;
    this table lets the XML written back from JSON leave them out.

    The value is part of the answer, not just the name: ``type`` is pinned to
    ``"ID"`` on ``IDType`` and ``"URN"`` on ``URNType``, but is an ordinary
    attribute elsewhere. Matching name *and* value means a caller can strip the
    redundant ones without touching a ``type`` that means something.

    Returns:
        Mapping of local attribute name to the sorted fixed values the schema
        pins it to.
    """
    schemas = _collect_all_schemas(entry)
    fixed: dict[str, set[str]] = {}

    for namespace, schema in schemas.items():
        if namespace not in DDI_NS_PREFIXES:
            continue
        for component in schema.iter_components():
            if not isinstance(component, XsdComplexType):
                continue
            attributes = getattr(component, "attributes", None) or {}
            for name, attribute in attributes.items():
                value = getattr(attribute, "fixed", None)
                if name and value is not None:
                    fixed.setdefault(name, set()).add(str(value))

    return {name: sorted(values) for name, values in sorted(fixed.items())}


def introspect_elements(entry: Path = ENTRY_SCHEMA) -> dict[str, list[dict]]:
    """Return a mapping of module → top-level element definitions."""
    schemas = _collect_all_schemas(entry)
    result: dict[str, list[dict]] = {}

    for ns, schema in sorted(schemas.items()):
        module = DDI_NS_PREFIXES.get(ns)
        if module is None:
            continue

        elements: list[dict] = []
        for elem_name, elem in sorted(schema.elements.items()):
            type_name, type_ns = _resolve_type_name(elem.type)
            elements.append(
                {
                    "name": elem_name,
                    "namespace": ns,
                    "type_name": type_name,
                    "type_namespace": type_ns,
                    "substitution_group": (
                        str(elem.substitution_group).rsplit("}", 1)[-1]
                        if elem.substitution_group is not None
                        else None
                    ),
                    "abstract": elem.abstract,
                }
            )
        if elements:
            result[module] = elements

    return result


def catalog_to_json(entry: Path = ENTRY_SCHEMA) -> str:
    """Produce a JSON string of the full XSD catalog."""
    types_by_module = introspect_schemas(entry)
    elements_by_module = introspect_elements(entry)

    output = {
        "types": {
            mod: [asdict(t) for t in types_list]
            for mod, types_list in types_by_module.items()
        },
        "elements": elements_by_module,
    }
    return json.dumps(output, indent=2, default=str)


if __name__ == "__main__":
    types_by_module = introspect_schemas()
    total_types = sum(len(v) for v in types_by_module.values())
    print(
        f"Introspected {total_types} complex types across {len(types_by_module)} modules:\n"
    )
    for module, types_list in sorted(types_by_module.items()):
        print(f"  {module}: {len(types_list)} complex types")
        for t in types_list[:3]:
            children_count = len(t.children)
            base = t.base_type or "(none)"
            print(f"    - {t.name} (base={base}, {children_count} children)")
        if len(types_list) > 3:
            print(f"    ... and {len(types_list) - 3} more")
