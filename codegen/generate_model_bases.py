"""Generate importable Python base classes from the XSD introspection catalog.

The last step of the code-generation pipeline: produce base dataclasses that live
in ``src/ddi_l/models/_generated/`` and are imported by the hand-written
model modules.  Each generated base class carries **all** XSD-defined fields
with correct Python types;  the hand-written subclass then adds only
``from_xml``, ``to_xml``, validation and helper methods.

Usage::

    python -m codegen.generate_model_bases          # generate all modules
    python -m codegen.generate_model_bases logicalproduct  # single module
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from codegen.xsd_introspect import (
    DDI_NS_PREFIXES,
    ChildElement,
    ComplexTypeInfo,
    collect_fixed_attributes_by_element,
    collect_label_slot_tags,
    introspect_schemas,
)

# ---------------------------------------------------------------------------
# Output directory — inside the importable package
# ---------------------------------------------------------------------------

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent / "src" / "ddi_l" / "models" / "_generated"
)

# ---------------------------------------------------------------------------
# XSD → Python type mapping
# ---------------------------------------------------------------------------

SIMPLE_TYPE_MAP: dict[str, str] = {
    "string": "str",
    "boolean": "bool",
    "int": "int",
    "integer": "int",
    "positiveInteger": "int",
    "nonNegativeInteger": "int",
    "decimal": "float",
    "float": "float",
    "double": "float",
    "date": "str",
    "dateTime": "str",
    "anyURI": "str",
    "language": "str",
    "token": "str",
    "NMTOKEN": "str",
    "ID": "str",
    "IDREF": "str",
    "NCName": "str",
    "QName": "str",
}

# XSD base type → Python base class name
BASE_CLASS_MAP: dict[str, str] = {
    "MaintainableType": "MaintainableBase",
    "VersionableType": "MaintainableBase",
    "IdentifiableType": "MaintainableBase",
    "AbstractMaintainableType": "MaintainableBase",
    "AbstractVersionableType": "MaintainableBase",
    "AbstractIdentifiableType": "MaintainableBase",
}

# DDI namespace → constant name in ddi_l.constants
NS_CONSTANT_MAP: dict[str, str] = {
    "ddi:logicalproduct:3_3": "LOGICAL_PRODUCT_NS",
    "ddi:reusable:3_3": "REUSABLE_NS",
    "ddi:datacollection:3_3": "DATA_COLLECTION_NS",
    "ddi:studyunit:3_3": "STUDY_UNIT_NS",
    "ddi:conceptualcomponent:3_3": "CONCEPTUAL_COMPONENT_NS",
    "ddi:archive:3_3": "ARCHIVE_NS",
    "ddi:comparative:3_3": "COMPARATIVE_NS",
    "ddi:group:3_3": "GROUP_NS",
    "ddi:instance:3_3": "INSTANCE_NS",
    "ddi:physicalinstance:3_3": "PHYSICAL_INSTANCE_NS",
    "ddi:physicaldataproduct:3_3": "PHYSICAL_DATA_PRODUCT_NS",
    "ddi:dataset:3_3": "DATASET_NS",
    "ddi:ddiprofile:3_3": "DDI_PROFILE_NS",
}

# DDI namespace → short prefix for NSMAP
NS_PREFIX_MAP: dict[str, str] = {
    "ddi:logicalproduct:3_3": "l",
    "ddi:reusable:3_3": "r",
    "ddi:datacollection:3_3": "d",
    "ddi:studyunit:3_3": "s",
    "ddi:conceptualcomponent:3_3": "c",
    "ddi:archive:3_3": "a",
    "ddi:comparative:3_3": "cmp",
    "ddi:group:3_3": "g",
    # instance has no short prefix in the namespace map; skip NSMAP
    "ddi:physicalinstance:3_3": "pi",
    "ddi:physicaldataproduct:3_3": "p",
}

# Elements inherited from Identifiable/Versionable/Maintainable — already on
# MaintainableBase, so skip them in the generated fields.
INHERITED_ELEMENTS: set[str] = {
    "Agency",
    "ID",
    "Version",
    "URN",
    "UserID",
    "UserAttributePair",
    "VersionResponsibility",
    "VersionRationale",
    "BasedOnObject",
    "RelatedOtherMaterialReference",
    "Note",
    "Label",
    "Description",
    "Software",
    "MetadataQuality",
    "VersionResponsibilityReference",
    "MaintainableObject",
}

# Inherited attributes to skip
INHERITED_ATTRS: set[str] = {
    "id",
    "urn",
    "agency",
    "version",
    "scope",
    "isIdentifiable",
    "isVersionable",
    "isMaintainable",
    "externalReferenceDefaultURI",
    "isUniversallyUnique",
    "versionableId",
    "typeOfIdentifier",
}


# ---------------------------------------------------------------------------
# Name helpers
# ---------------------------------------------------------------------------


def _to_class_name(xsd_type_name: str) -> str:
    """Convert XSD type name to Python class name, stripping 'Type' suffix."""
    name = xsd_type_name
    if name.endswith("Type"):
        name = name[:-4]
    return name


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    snake = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", snake)
    return snake.lower()


def _to_field_name(child: ChildElement, parent_class_name: str = "") -> str:
    """Convert XSD child element local name to a snake_case Python field name.

    Applies naming conventions that match the hand-written model style:
    - ``{Parent}Name`` → ``names`` (e.g. VariableName → names)
    - ``{Parent}SchemeName`` → ``names``
    - List fields are pluralised
    """
    local = child.local_name.replace("-", "_")

    # Rule 1: Name elements → "names"
    # e.g. VariableName in Variable → names
    # e.g. CategorySchemeName in CategoryScheme → names
    if local.endswith("Name") and local != "Name":
        prefix = local[: -len("Name")]
        # Check if the prefix matches the parent class (or parent + "Scheme")
        if prefix == parent_class_name or prefix == parent_class_name + "Scheme":
            return "names"

    snake = _camel_to_snake(local)

    # Pluralise list fields
    if child.max_occurs is None or child.max_occurs > 1:
        if snake.endswith("y") and not snake.endswith("ey"):
            snake = snake[:-1] + "ies"
        elif not snake.endswith("s"):
            snake += "s"

    return snake


def _python_type_for_child(child: ChildElement) -> str:
    """Determine the Python type annotation string for a child element."""
    kind = _python_kind_for_child(child)

    KIND_TO_TYPE = {
        "reference": "Reference",
        "intl_string": "InternationalString",
        "code_value": "CodeValue",
        "element": "Element",
        "str": "str",
        "bool": "bool",
        "int": "int",
        "float": "float",
    }
    py_type = KIND_TO_TYPE.get(kind, "Element")

    is_list = child.max_occurs is None or child.max_occurs > 1

    if is_list:
        return f"list[{py_type}]"
    else:
        return f"Optional[{py_type}]"


def _python_kind_for_child(child: ChildElement) -> str:
    """Return the serialization kind string for a child element.

    This determines how the generic ``from_xml``/``to_xml`` methods
    parse and emit the field:

    - ``reference`` → ``Reference.from_xml`` / ``Reference.to_xml``
    - ``intl_string`` → ``InternationalString.from_container``
    - ``code_value`` → ``CodeValue.from_xml`` / ``CodeValue.to_xml``
    - ``element`` → raw XML clone
    - ``str``, ``bool``, ``int``, ``float`` → text content conversions
    """
    type_name = child.type_name or "Any"

    if child.is_reference or type_name in ("ReferenceType", "SchemeReferenceType"):
        return "reference"
    if child.local_name.endswith("Name") and (
        type_name.endswith("NameType") or type_name == "NameType"
    ):
        return "intl_string"
    if type_name in SIMPLE_TYPE_MAP:
        return SIMPLE_TYPE_MAP[type_name]  # "str", "bool", "int", "float"
    if type_name in ("CodeValueType", "InternationalCodeValueType"):
        return "code_value"
    return "element"


def _field_default(child: ChildElement) -> str:
    """Return the default value expression for a field."""
    is_list = child.max_occurs is None or child.max_occurs > 1
    if is_list:
        return " = field(default_factory=list)"
    else:
        return " = None"


# ---------------------------------------------------------------------------
# Module generation
# ---------------------------------------------------------------------------


def _generate_module(module_name: str, types: list[ComplexTypeInfo]) -> str:
    """Generate a complete Python module with base dataclasses."""
    ns_constants: set[str] = set()
    needs_element = False
    needs_reference = False
    needs_intl_string = False
    needs_code_value = False

    # Pre-scan to determine imports
    for xsd_type in types:
        ns_const = NS_CONSTANT_MAP.get(xsd_type.namespace)
        if ns_const:
            ns_constants.add(ns_const)
        for child in xsd_type.children:
            if child.local_name in INHERITED_ELEMENTS:
                continue
            # Collect namespace constants for child elements (needed by _FIELD_XML_MAP)
            child_ns_const = NS_CONSTANT_MAP.get(child.namespace)
            if child_ns_const:
                ns_constants.add(child_ns_const)
            py_type = _python_type_for_child(child)
            if "Element" in py_type:
                needs_element = True
            if "Reference" in py_type:
                needs_reference = True
            if "InternationalString" in py_type:
                needs_intl_string = True
            if "CodeValue" in py_type:
                needs_code_value = True

    lines: list[str] = []
    lines.append(
        f'"""AUTO-GENERATED base dataclasses for DDI 3.3 — {module_name} module.'
    )
    lines.append("")
    lines.append("These classes provide field definitions derived from the XSD schema.")
    lines.append("Hand-written model classes inherit from these bases and add")
    lines.append("``from_xml``, ``to_xml``, validation, and helper methods.")
    lines.append("")
    lines.append("**Do not edit manually** — regenerate with:")
    lines.append("    python -m codegen.generate_model_bases")
    lines.append('"""')
    lines.append("")
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from dataclasses import dataclass, field")
    lines.append("from typing import ClassVar, Optional")
    lines.append("")

    # Conditional imports
    if needs_element:
        lines.append("from ddi_l._etree import Element")
    base_imports = ["MaintainableBase"]
    if needs_reference:
        base_imports.append("Reference")
    if needs_intl_string:
        base_imports.append("InternationalString")
    if needs_code_value:
        base_imports.append("CodeValue")
    lines.append(f"from ddi_l.models.base import {', '.join(sorted(base_imports))}")

    if ns_constants:
        lines.append(f"from ddi_l.constants import {', '.join(sorted(ns_constants))}")
    lines.append("from ddi_l.namespaces import NamespaceBindings, build_namespace_map")
    lines.append("from ddi_l.models.base import qn")
    lines.append("")
    lines.append("")

    for xsd_type in types:
        class_name = _to_class_name(xsd_type.name)
        base_name = class_name + "Fields"

        # Determine Python base class
        base = "MaintainableBase"
        if xsd_type.base_type:
            mapped = BASE_CLASS_MAP.get(xsd_type.base_type)
            if mapped:
                base = mapped

        # Docstring
        doc = (
            xsd_type.documentation[:200]
            if xsd_type.documentation
            else f"XSD type: {xsd_type.name}"
        )

        # Filter children — skip inherited
        own_children = [
            c for c in xsd_type.children if c.local_name not in INHERITED_ELEMENTS
        ]

        # Build TAG
        ns_const = NS_CONSTANT_MAP.get(xsd_type.namespace, f'"{xsd_type.namespace}"')
        ns_prefix = NS_PREFIX_MAP.get(xsd_type.namespace)

        lines.append("@dataclass")
        lines.append(f"class {base_name}({base}):")
        lines.append(f'    """{doc}"""')
        lines.append("")
        lines.append(f'    TAG: ClassVar[str] = qn({ns_const}, "{class_name}")')
        if ns_prefix:
            lines.append(
                f'    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("{ns_prefix}")'
            )

        # Build field XML map entries and attribute map entries
        field_map_entries: list[str] = []
        attr_map_entries: list[str] = []
        own_attrs = [a for a in xsd_type.attributes if a.name not in INHERITED_ATTRS]

        if not own_children and not own_attrs:
            lines.append("    pass")
        else:
            seen_fields: set[str] = set()
            for child in own_children:
                fname = _to_field_name(child, parent_class_name=class_name)
                if fname in seen_fields:
                    continue
                seen_fields.add(fname)
                ftype = _python_type_for_child(child)
                default = _field_default(child)
                cardinality = f"[{child.min_occurs}..{'*' if child.max_occurs is None else child.max_occurs}]"
                lines.append(f"    {fname}: {ftype}{default}  # {cardinality}")

                # Build _FIELD_XML_MAP entry
                child_ns_const = NS_CONSTANT_MAP.get(
                    child.namespace, f'"{child.namespace}"'
                )
                kind = _python_kind_for_child(child)
                is_list = child.max_occurs is None or child.max_occurs > 1
                field_map_entries.append(
                    f'        "{fname}": (qn({child_ns_const}, "{child.local_name}"), "{kind}", {is_list}),'
                )

            for attr in own_attrs:
                atype = SIMPLE_TYPE_MAP.get(attr.type_name or "", "str")
                attr_name = attr.name.replace("-", "_")
                if attr_name and not attr_name[0].isalpha() and attr_name[0] != "_":
                    attr_name = f"_{attr_name}"
                lines.append(f"    {attr_name}: Optional[{atype}] = None  # @attr")

                # Build _ATTR_XML_MAP entry
                attr_kind = SIMPLE_TYPE_MAP.get(attr.type_name or "", "str")
                attr_map_entries.append(
                    f'        "{attr_name}": ("{attr.name}", "{attr_kind}"),'
                )

        # Emit _FIELD_XML_MAP
        if field_map_entries:
            lines.append("    _FIELD_XML_MAP: ClassVar[dict] = {")
            lines.extend(field_map_entries)
            lines.append("    }")

        # Emit _ATTR_XML_MAP
        if attr_map_entries:
            lines.append("    _ATTR_XML_MAP: ClassVar[dict] = {")
            lines.extend(attr_map_entries)
            lines.append("    }")

        # Emit _ELEMENT_ORDER — full XSD element ordering including inherited
        if xsd_type.all_element_order:
            order_entries: list[str] = []
            for tag in xsd_type.all_element_order:
                # Parse {ns}local from the tag
                if tag.startswith("{"):
                    close = tag.index("}")
                    tag_ns = tag[1:close]
                    tag_local = tag[close + 1 :]
                else:
                    tag_ns = ""
                    tag_local = tag
                tag_ns_const = NS_CONSTANT_MAP.get(tag_ns, f'"{tag_ns}"')
                order_entries.append(f'        qn({tag_ns_const}, "{tag_local}"),')
            lines.append("    _ELEMENT_ORDER: ClassVar[list[str]] = [")
            lines.extend(order_entries)
            lines.append("    ]")

        # Emit _MIXED flag
        if xsd_type.mixed:
            lines.append("    _MIXED: ClassVar[bool] = True")

        lines.append("")
        lines.append("")

    return "\n".join(lines)


def _generate_label_slots() -> str:
    """Emit the set of element tags the schema allows an ``r:Label`` on."""
    tags = collect_label_slot_tags()
    lines = [
        '"""Element tags whose DDI 3.3 content model permits ``r:Label``.',
        "",
        "Generated from the XSDs. Consumed by the ``ddi.maintainable.labels``",
        "lint rule to tell an item that is *missing* a label from one that",
        "cannot carry a label at all -- ``l:Code`` is Identifiable rather than",
        "Maintainable and has no ``r:Label`` slot, but carries the",
        "Agency/ID/Version that a duck-type would match on.",
        "",
        "Regenerate with: python -m codegen.generate_model_bases",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Final",
        "",
        "TAGS_ALLOWING_LABEL: Final[frozenset[str]] = frozenset(",
        "    {",
    ]
    lines.extend(f'        "{tag}",' for tag in tags)
    lines.extend(["    }", ")", ""])
    lines.extend(
        [
            "",
            "# The namespaces the table above describes. A tag outside them is not",
            "# 'known to have no label slot', it is simply not described here -- which",
            "# is the difference between a DDI type and a downstream subclass carrying",
            "# its own namespace. Derived from the schema set rather than from the tags",
            "# above, because a namespace whose elements all lack a label slot still",
            "# belongs here.",
            "SCHEMA_NAMESPACES: Final[frozenset[str]] = frozenset(",
            "    {",
        ]
    )
    lines.extend(f'        "{namespace}",' for namespace in sorted(DDI_NS_PREFIXES))
    lines.extend(["    }", ")", ""])
    return "\n".join(lines)


def _generate_fixed_attributes() -> str:
    """Emit, per element, the attributes the schema pins to a ``fixed`` value."""
    by_element = collect_fixed_attributes_by_element()
    lines = [
        '"""Attributes whose DDI 3.3 declaration pins them to a ``fixed`` value.',
        "",
        "Generated from the XSDs. Consumed by the JSON-to-XML conversion, which",
        "drops them: an attribute the schema pins can only ever hold the value",
        "it already mandates, so writing one back carries no information.",
        "xmlschema materializes them when decoding, and re-encoding them grew a",
        "round-tripped document by 36 attributes and 645 bytes.",
        "",
        "Keyed by element, because the attribute name alone does not decide.",
        "``type`` is pinned on ``r:ID`` and ``r:URN``, but ``r:KindOfData``,",
        "``l:RelatedValue`` and ``pi:DataFingerprint`` declare an ordinary one,",
        "and the bundled XHTML schema gives ``xhtml:a`` a ``type`` holding a MIME",
        'type -- where ``type="ID"`` is a value someone meant. Dropping by name',
        "and value alone would delete all of those.",
        "",
        "Regenerate with: python -m codegen.generate_model_bases",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Final",
        "",
        "FIXED_ATTRIBUTES_BY_ELEMENT: Final[dict[str, dict[str, frozenset[str]]]] = {",
    ]
    for tag, attributes in by_element.items():
        rendered = ", ".join(
            f'"{name}": frozenset({{{", ".join(chr(34) + v + chr(34) for v in values)}}})'
            for name, values in attributes.items()
        )
        lines.append(f'    "{tag}": {{{rendered}}},')
    lines.extend(["}", ""])
    return "\n".join(lines)


def generate_all(
    modules: list[str] | None = None,
) -> dict[str, Path]:
    """Generate base dataclass modules and write to _generated/ directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    types_by_module = introspect_schemas()

    written: dict[str, Path] = {}
    for module_name, types_list in sorted(types_by_module.items()):
        if modules and module_name not in modules:
            continue
        code = _generate_module(module_name, types_list)
        out_path = OUTPUT_DIR / f"{module_name}.py"
        out_path.write_text(code, encoding="utf-8")
        written[module_name] = out_path
        print(
            f"  Generated {out_path.name}: {len(types_list)} types, {len(code)} bytes"
        )

    # The label-slot table is schema-wide rather than per-module, so it is
    # always regenerated even when a single module was requested.
    label_slots_path = OUTPUT_DIR / "label_slots.py"
    label_slots_path.write_text(_generate_label_slots(), encoding="utf-8")
    written["label_slots"] = label_slots_path
    print(f"  Generated {label_slots_path.name}")

    fixed_attributes_path = OUTPUT_DIR / "fixed_attributes.py"
    fixed_attributes_path.write_text(_generate_fixed_attributes(), encoding="utf-8")
    written["fixed_attributes"] = fixed_attributes_path
    print(f"  Generated {fixed_attributes_path.name}")

    # Write __init__.py
    init_path = OUTPUT_DIR / "__init__.py"
    init_lines = [
        '"""Auto-generated DDI 3.3 base dataclasses.',
        "",
        "Hand-written model classes inherit from these bases.",
        "Regenerate with: python -m codegen.generate_model_bases",
        '"""',
    ]
    init_path.write_text("\n".join(init_lines) + "\n", encoding="utf-8")
    written["__init__"] = init_path

    return written


if __name__ == "__main__":
    target_modules = sys.argv[1:] if len(sys.argv) > 1 else None
    print("Generating DDI 3.3 base dataclasses...\n")
    files = generate_all(modules=target_modules)
    print(f"\nGenerated {len(files)} files into {OUTPUT_DIR}")
