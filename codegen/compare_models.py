"""Compare XSD-derived type catalog with hand-written ddi_l models.

Produces a structured gap analysis report showing:
1. XSD types that have NO corresponding Python class
2. XSD types that ARE modeled but are MISSING child elements
3. XSD child elements present in Python but NOT in XSD (potential bugs)
4. Summary statistics
"""

from __future__ import annotations

import importlib
import inspect
import re
import sys
from dataclasses import dataclass, field
from dataclasses import fields as dc_fields
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from codegen.xsd_introspect import (
    ChildElement,
    introspect_schemas,
)

# ── Collect hand-written models ──────────────────────────────────────────────


def _collect_handwritten_models() -> dict[str, dict]:
    """Collect all hand-written model classes from ddi_l.models.

    Returns a dict mapping XSD type name → {
        "class": the Python class,
        "tag": the TAG class var,
        "fields": set of field names,
        "module": Python module name,
    }
    """

    # Import all model submodules
    model_modules = [
        "ddi_l.models.base",
        "ddi_l.models.study",
        "ddi_l.models.logicalproduct",
        "ddi_l.models.concept",
        "ddi_l.models.archive",
        "ddi_l.models.physical",
        "ddi_l.models.classification",
        "ddi_l.models.comparison",
        "ddi_l.models.process",
        "ddi_l.models.quality",
        "ddi_l.models.methodology",
        "ddi_l.models.dissemination",
        "ddi_l.models.group",
        "ddi_l.models.reusable",
    ]

    # Try datacollection monolith
    try:
        model_modules.append("ddi_l.models.datacollection._monolith")
    except Exception:
        pass

    classes: dict[str, dict] = {}

    for mod_name in model_modules:
        try:
            mod = importlib.import_module(mod_name)
        except ImportError:
            continue

        for attr_name in dir(mod):
            obj = getattr(mod, attr_name)
            if not isinstance(obj, type):
                continue

            tag = getattr(obj, "TAG", None)
            if tag is None:
                continue

            # Extract local name and namespace from TAG (Clark notation)
            match = re.match(r"\{(.+?)\}(.+)", tag)
            if not match:
                continue
            ns, local = match.groups()

            # Map to XSD type name (convention: LocalNameType)
            xsd_type_name = f"{local}Type"

            # Collect dataclass fields
            try:
                obj_fields = {f.name for f in dc_fields(obj)}
            except TypeError:
                obj_fields = set()

            # Also collect non-field attributes that look like model data
            for parent in inspect.getmro(obj):
                try:
                    for f in dc_fields(parent):
                        obj_fields.add(f.name)
                except TypeError:
                    pass

            classes[xsd_type_name] = {
                "class": obj,
                "class_name": obj.__name__,
                "tag": tag,
                "namespace": ns,
                "local_name": local,
                "fields": obj_fields,
                "module": mod_name,
            }

    return classes


# ── Normalize names for fuzzy matching ───────────────────────────────────────


def _normalize(name: str) -> str:
    """Convert CamelCase or kebab to lowercase for comparison."""
    # Remove Type suffix
    name = re.sub(r"Type$", "", name)
    # CamelCase → lowercase with underscores
    name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)
    return name.lower().replace("-", "_")


def _xsd_child_to_python_name(child: ChildElement) -> str:
    """Convert an XSD child element local name to a likely Python field name.

    E.g., "CategoryScheme" → "category_schemes" (or "category_scheme")
          "VariableSchemeReference" → "variable_scheme_references"
          "r:Label" → "labels"
    """
    local = child.local_name
    # Strip namespace prefix-like patterns
    local = re.sub(r"^[a-z]:", "", local)

    # Convert CamelCase to snake_case
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", local)
    snake = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", snake)
    snake = snake.lower()

    # Pluralize based on cardinality
    if child.max_occurs is None or child.max_occurs > 1:
        if snake.endswith("y") and not snake.endswith("ey"):
            snake = snake[:-1] + "ies"
        elif snake.endswith("s"):
            pass  # already plural
        else:
            snake += "s"

    return snake


# ── Comparison logic ─────────────────────────────────────────────────────────


@dataclass
class GapEntry:
    """A single gap finding."""

    category: str  # "missing_class", "missing_field", "extra_field"
    xsd_type: str
    xsd_module: str
    xsd_namespace: str
    detail: str
    severity: str = "info"  # "info", "warning", "error"


@dataclass
class ComparisonReport:
    """Full comparison report."""

    total_xsd_types: int = 0
    total_modeled_types: int = 0
    total_unmodeled_types: int = 0
    total_missing_fields: int = 0
    total_extra_fields: int = 0
    gaps: list[GapEntry] = field(default_factory=list)
    coverage_by_module: dict[str, dict] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            "=" * 80,
            "DDI 3.3 XSD vs ddi_l Hand-Written Models — Gap Analysis",
            "=" * 80,
            "",
            f"Total XSD complex types:      {self.total_xsd_types}",
            f"Modeled in ddi_l:          {self.total_modeled_types}",
            f"NOT modeled (missing class):  {self.total_unmodeled_types}",
            f"Missing child fields:         {self.total_missing_fields}",
            f"Coverage:                     {self.total_modeled_types / max(self.total_xsd_types, 1) * 100:.1f}%",
            "",
            "─" * 80,
            "Coverage by Module:",
            "─" * 80,
        ]
        for mod, stats in sorted(self.coverage_by_module.items()):
            pct = stats["modeled"] / max(stats["total"], 1) * 100
            lines.append(
                f"  {mod:45s} {stats['modeled']:3d}/{stats['total']:3d} ({pct:5.1f}%)"
            )

        return "\n".join(lines)

    def full_report(self) -> str:
        sections = [self.summary(), ""]

        # Group gaps by category
        by_cat: dict[str, list[GapEntry]] = {}
        for g in self.gaps:
            by_cat.setdefault(g.category, []).append(g)

        # Missing classes
        if "missing_class" in by_cat:
            items = by_cat["missing_class"]
            sections.append("")
            sections.append("=" * 80)
            sections.append(f"UNMODELED XSD TYPES ({len(items)} types)")
            sections.append("=" * 80)
            sections.append("")
            # Group by module
            by_mod: dict[str, list[GapEntry]] = {}
            for g in items:
                by_mod.setdefault(g.xsd_module, []).append(g)
            for mod, mod_items in sorted(by_mod.items()):
                sections.append(f"── {mod} ({len(mod_items)} missing) ──")
                for g in sorted(mod_items, key=lambda x: x.xsd_type):
                    sections.append(f"  - {g.xsd_type}: {g.detail}")
                sections.append("")

        # Missing fields on modeled types
        if "missing_field" in by_cat:
            items = by_cat["missing_field"]
            sections.append("")
            sections.append("=" * 80)
            sections.append(
                f"MISSING CHILD ELEMENTS ON MODELED TYPES ({len(items)} fields)"
            )
            sections.append("=" * 80)
            sections.append("")
            # Group by xsd_type
            by_type: dict[str, list[GapEntry]] = {}
            for g in items:
                by_type.setdefault(g.xsd_type, []).append(g)
            for type_name, type_items in sorted(by_type.items()):
                mod = type_items[0].xsd_module
                sections.append(f"── {type_name} ({mod}) ──")
                for g in type_items:
                    sections.append(f"  - {g.detail}")
                sections.append("")

        return "\n".join(sections)


def compare(
    skip_base_fields: bool = True,
    skip_reference_elements: bool = False,
) -> ComparisonReport:
    """Run the full comparison and return a report."""
    xsd_types = introspect_schemas()
    handwritten = _collect_handwritten_models()
    report = ComparisonReport()

    # Fields inherited from MaintainableBase that we should not flag as missing

    # XSD inherited elements to skip (from IdentifiableType, VersionableType, MaintainableType)
    XSD_INHERITED_ELEMENTS = {
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
        # Common elements on most maintainables handled by base
        "Label",
        "Description",
    }

    for module, types_list in xsd_types.items():
        mod_total = len(types_list)
        mod_modeled = 0

        for xsd_type in types_list:
            report.total_xsd_types += 1

            # Try to find matching handwritten class
            matched = handwritten.get(xsd_type.name)

            if matched is None:
                report.total_unmodeled_types += 1
                report.gaps.append(
                    GapEntry(
                        category="missing_class",
                        xsd_type=xsd_type.name,
                        xsd_module=module,
                        xsd_namespace=xsd_type.namespace,
                        detail=f"base={xsd_type.base_type or 'none'}, "
                        f"{len(xsd_type.children)} children, "
                        f"abstract={xsd_type.is_abstract}",
                        severity="warning" if not xsd_type.is_abstract else "info",
                    )
                )
                continue

            report.total_modeled_types += 1
            mod_modeled += 1

            # Compare child elements
            python_fields = matched["fields"]
            python_fields_lower = {f.lower() for f in python_fields}

            for child in xsd_type.children:
                if skip_reference_elements and child.is_reference:
                    continue

                # Skip inherited base elements
                if skip_base_fields and child.local_name in XSD_INHERITED_ELEMENTS:
                    continue

                # Generate expected Python field name
                expected_name = _xsd_child_to_python_name(child)
                alt_names = {
                    expected_name,
                    expected_name.rstrip("s"),
                    expected_name + "s",
                    re.sub(r"_references?$", "_reference", expected_name),
                    re.sub(r"_reference$", "_references", expected_name),
                    child.local_name.lower(),
                    _normalize(child.local_name),
                    _normalize(child.local_name) + "s",
                }

                # Check if any variant matches
                found = False
                for alt in alt_names:
                    if alt in python_fields_lower:
                        found = True
                        break

                if not found:
                    report.total_missing_fields += 1
                    cardinality = f"[{child.min_occurs}..{'*' if child.max_occurs is None else child.max_occurs}]"
                    report.gaps.append(
                        GapEntry(
                            category="missing_field",
                            xsd_type=xsd_type.name,
                            xsd_module=module,
                            xsd_namespace=xsd_type.namespace,
                            detail=(
                                f"{child.local_name} {cardinality} "
                                f"(expected Python field: '{expected_name}')"
                            ),
                            severity="warning",
                        )
                    )

        report.coverage_by_module[module] = {
            "total": mod_total,
            "modeled": mod_modeled,
        }

    return report


if __name__ == "__main__":
    report = compare()
    print(report.full_report())
