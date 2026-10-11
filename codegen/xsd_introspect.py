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
    is_reference: bool  # type is r:ReferenceType or derives from it
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


_REFERENCE_TYPE = "{ddi:reusable:3_3}ReferenceType"


def _is_reference_type(xsd_type: XsdType | None) -> bool:
    """Whether ``xsd_type`` is ``r:ReferenceType`` or derives from it.

    The name is not enough: ``r:ExternalURLReference`` is an ``xs:anyURI`` and
    ``r:ExternalURNReference`` an ``xs:string``, and reading either as a DDI
    reference emptied them.
    """
    seen: set[int] = set()
    while xsd_type is not None and id(xsd_type) not in seen:
        seen.add(id(xsd_type))
        if getattr(xsd_type, "name", None) == _REFERENCE_TYPE:
            return True
        xsd_type = getattr(xsd_type, "base_type", None)
    return False


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
                    is_reference=_is_reference_type(resolved.type),
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


def collect_element_layout(
    entry: Path = ENTRY_SCHEMA,
) -> tuple[list[str], dict[str, list[str]]]:
    """Return what a writer needs to lay elements out as the schema declares.

    Colectica (and any serializer generated from the XSDs) writes attributes in
    declaration order, base type first, and spells an empty element by its
    type: ``<r:UserID typeOfUserID="x"></r:UserID>`` for one with text
    content, ``<r:ResponseCardinality ... />`` for one that only carries
    attributes. A parsed tree keeps neither fact, so both come from here.

    Returns:
        ``(text_tags, attribute_order)``: the sorted tags of elements whose type
        is simple, has simple content or is mixed, and, for every element
        declaring two or more attributes, their names in declaration order.
    """
    schemas = _collect_all_schemas(entry)
    text_tags: set[str] = set()
    attribute_order: dict[str, list[str]] = {}

    for namespace, schema in schemas.items():
        if namespace not in DDI_NS_PREFIXES:
            continue
        for component in schema.iter_components():
            if not isinstance(component, XsdElement):
                continue
            tag = component.name
            if not tag or not tag.startswith("{"):
                continue
            element_type = component.type
            if (
                element_type.is_simple()
                or element_type.has_simple_content()
                or getattr(element_type, "mixed", False)
            ):
                text_tags.add(tag)
            names = [
                name
                for name in (getattr(element_type, "attributes", None) or {})
                if name
            ]
            if len(names) > 1:
                attribute_order.setdefault(tag, names)

    return sorted(text_tags), dict(sorted(attribute_order.items()))


def collect_child_ranks(
    entry: Path = ENTRY_SCHEMA,
) -> tuple[dict[str, list[list[str]]], dict[str, str]]:
    """Return the order each content model gives its children.

    Every DDI complex type with element content maps to its child tags grouped
    by rank: tags in one group may appear in any order relative to each other,
    and groups must appear in list order. Members of a repeating group
    (``xs:choice maxOccurs="unbounded"``, a repeating ``xs:sequence``) share a
    group, because interleaving them is valid and must survive -- the
    identification choice in ``r:ReferenceType`` (``maxOccurs="2"``) is one.

    Returns:
        ``(ranks_by_type, type_by_element)``: rank groups per type key, and
        the type key of every element declaration whose type has element
        content. An anonymous type is keyed by its element.
    """
    schemas = _collect_all_schemas(entry)
    ranks_by_type: dict[str, list[list[str]]] = {}
    type_by_element: dict[str, str] = {}

    def walk(group: XsdGroup, groups: list[list[str]], shared: int | None) -> None:
        for particle in group:
            if isinstance(particle, XsdGroup):
                repeating = particle.max_occurs is None or particle.max_occurs > 1
                if shared is None and repeating:
                    groups.append([])
                    walk(particle, groups, len(groups) - 1)
                else:
                    walk(particle, groups, shared)
            elif isinstance(particle, XsdElement) and particle.name:
                if any(particle.name in members for members in groups):
                    continue
                if shared is None:
                    groups.append([particle.name])
                else:
                    groups[shared].append(particle.name)

    for namespace, schema in schemas.items():
        if namespace not in DDI_NS_PREFIXES:
            continue
        for component in schema.iter_components():
            if not isinstance(component, XsdElement) or not component.name:
                continue
            element_type = component.type
            if not isinstance(element_type, XsdComplexType):
                continue
            if not isinstance(element_type.content, XsdGroup):
                continue
            key = element_type.name or component.name
            type_by_element.setdefault(component.name, key)
            if key not in ranks_by_type:
                groups: list[list[str]] = []
                walk(element_type.content, groups, None)
                ranks_by_type[key] = [members for members in groups if members]

    return (
        dict(sorted(ranks_by_type.items())),
        dict(sorted(type_by_element.items())),
    )


def collect_substitution_heads(entry: Path = ENTRY_SCHEMA) -> dict[str, str]:
    """Return ``{member tag: head tag}`` for every substitution group.

    A content model names the head (``d:ResponseDomain``,
    ``l:BaseLogicalProduct``) while documents carry a member
    (``d:CodeDomain``, ``l:LogicalProduct``). Ordering children by the
    content model needs the member to sit where its head is declared.
    Chains are resolved to the head a content model can name.
    """
    schema = xmlschema.XMLSchema(str(entry))
    direct: dict[str, str] = {}
    for head_name, members in schema.maps.substitution_groups.items():
        for member in members:
            if member.name and member.name != head_name:
                direct[member.name] = head_name
    resolved: dict[str, str] = {}
    for member_name, head in direct.items():
        seen = {member_name}
        while head in direct and head not in seen:
            seen.add(head)
            head = direct[head]
        resolved[member_name] = head
    return dict(sorted(resolved.items()))


def collect_fragment_items(
    entry: Path = ENTRY_SCHEMA,
) -> dict[str, tuple[str, str]]:
    """Return every element a ``ddi:Fragment`` may carry, with its XSD type.

    These are the item types a repository such as Colectica exchanges one per
    fragment. Each maps to ``(module, type name)`` -- the generated module and
    the complex type -- because several elements share a type (``CategoryMap``
    and ``UniverseMap`` are both a ``MapType``), so the element name alone does
    not name its generated base.

    Returns:
        ``{element tag: (module, XSD type local name)}``, sorted by tag.
    """
    schemas = _collect_all_schemas(entry)
    instance = schemas["ddi:instance:3_3"]
    fragment_type = instance.types["FragmentType"]
    if not isinstance(fragment_type, XsdComplexType) or not isinstance(
        fragment_type.content, XsdGroup
    ):
        raise TypeError("ddi:FragmentType is expected to have element content.")
    items: dict[str, tuple[str, str]] = {}
    for element in fragment_type.content.iter_elements():
        tag = element.name
        element_type = element.type
        if not tag or not isinstance(element_type, XsdComplexType):
            continue
        type_name = element_type.name
        if not type_name or not type_name.startswith("{"):
            continue
        namespace, _, local = type_name[1:].partition("}")
        module = DDI_NS_PREFIXES.get(namespace)
        if module is None:
            continue
        items[tag] = (module, local)
    return dict(sorted(items.items()))


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
