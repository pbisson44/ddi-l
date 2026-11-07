"""A compact, checked-in form of a DDI schema for the native validator.

`build` reads a schema compiled by xmlschema and returns its intermediate
representation (IR): every element declaration, complex and simple type,
and each content model as a position automaton (Glushkov), all numbered in
one deterministic walk. ``codegen/schema_ir.py`` writes it to
``ddi_l/schemas/ir/``; the native validator reads it without loading
xmlschema. When a document has errors, the same walk gives the xmlschema
object behind each number, so xmlschema words them.

The automaton is exact for the language of a content model: occurrence
bounds are unrolled, substitution groups are name sets, and a subset
construction makes it deterministic. A model where one child could be
declared two ways is refused, and so are ``all`` groups, which DDI does not
use.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from typing import Any

__all__ = ["IR_FORMAT", "SchemaIR", "UnsupportedSchemaError", "build"]

# Bumped when the layout below changes.
IR_FORMAT = 1
_XSD = "{http://www.w3.org/2001/XMLSchema}"
_FACETS = {
    "length",
    "minLength",
    "maxLength",
    "minInclusive",
    "maxInclusive",
    "minExclusive",
    "maxExclusive",
    "totalDigits",
    "fractionDigits",
}


class UnsupportedSchemaError(ValueError):
    """The schema uses something the IR does not represent."""


class SchemaIR:
    """The IR as data (``data``) and the xmlschema object behind each number."""

    def __init__(self) -> None:
        self.names: list[str] = []
        self._name_ids: dict[str, int] = {}
        self.name_sets: list[list[int]] = []
        self._name_set_ids: dict[tuple[int, ...], int] = {}
        self.elements: list[dict[str, Any]] = []
        self.element_objects: list[Any] = []
        self.complex: list[dict[str, Any]] = []
        self.complex_objects: list[Any] = []
        self.simple: list[dict[str, Any]] = []
        self.simple_objects: list[Any] = []
        self.models: list[dict[str, Any]] = []
        self.model_objects: list[Any] = []
        self.wildcards: list[dict[str, Any]] = []
        self.wildcard_objects: list[Any] = []
        self._ids: dict[int, int] = {}
        self.roots: dict[int, int] = {}
        self.attributes: dict[int, int] = {}
        self.data: dict[str, Any] = {}
        self._schema: Any = None

    # ---- numbering ------------------------------------------------------------

    def name(self, text: str) -> int:
        found = self._name_ids.get(text)
        if found is None:
            found = self._name_ids[text] = len(self.names)
            self.names.append(text)
        return found

    def name_set(self, texts: Iterator[str] | list[str]) -> int:
        # Numbered in name order: substitution groups are sets, whose order
        # changes from one process to the next.
        key = tuple(sorted({self.name(text) for text in sorted(set(texts))}))
        found = self._name_set_ids.get(key)
        if found is None:
            found = self._name_set_ids[key] = len(self.name_sets)
            self.name_sets.append(list(key))
        return found

    def _number(self, obj: Any, table: list[Any], objects: list[Any]) -> int | None:
        found = self._ids.get(id(obj))
        if found is not None:
            return found
        self._ids[id(obj)] = len(table)
        objects.append(obj)
        table.append({})
        return None

    # ---- components -----------------------------------------------------------

    def element(self, xsd_element: Any) -> int:
        found = self._number(xsd_element, self.elements, self.element_objects)
        if found is not None:
            return found
        index = len(self.elements) - 1
        xsd_type = xsd_element.type
        entry: dict[str, Any] = {
            "name": self.name(xsd_element.name),
            "abstract": bool(xsd_element.abstract),
            "nillable": bool(xsd_element.nillable),
            "fixed": xsd_element.fixed,
            "default": xsd_element.default,
        }
        if xsd_element.abstract:
            entry["subst"] = self.name_set(
                e.name for e in xsd_element.iter_substitutes()
            )
        if xsd_element.alternatives:
            raise UnsupportedSchemaError(f"type alternatives on {xsd_element.name}")
        self.elements[index] = entry
        entry["type"] = (
            ["s", self.simple_type(xsd_type)]
            if xsd_type.is_simple()
            else ["c", self.complex_type(xsd_type)]
        )
        return index

    def complex_type(self, xsd_type: Any) -> int:
        found = self._number(xsd_type, self.complex, self.complex_objects)
        if found is not None:
            return found
        index = len(self.complex) - 1
        entry: dict[str, Any] = {"abstract": bool(xsd_type.abstract)}
        self.complex[index] = entry
        if xsd_type.assertions:
            raise UnsupportedSchemaError(f"assertions on {xsd_type.name}")
        attributes: dict[str, Any] = {}
        for name in sorted(key for key in xsd_type.attributes if key is not None):
            attribute = xsd_type.attributes[name]
            attributes[str(self.name(name))] = {
                "type": self.simple_type(attribute.type),
                "use": attribute.use,
                "fixed": attribute.fixed,
                "default": attribute.default,
            }
        entry["attrs"] = attributes
        wildcard = xsd_type.attributes.get(None)
        entry["any_attr"] = self.wildcard(wildcard) if wildcard is not None else None
        if xsd_type.has_simple_content():
            entry["content"] = "simple"
            entry["simple"] = self.simple_type(xsd_type.content)
        else:
            entry["content"] = "empty" if xsd_type.is_empty() else "elements"
            entry["mixed"] = bool(xsd_type.mixed)
            entry["model"] = self.model(xsd_type.content)
        return index

    def wildcard(self, wildcard: Any) -> int:
        found = self._number(wildcard, self.wildcards, self.wildcard_objects)
        if found is not None:
            return found
        index = len(self.wildcards) - 1
        if getattr(wildcard, "not_qname", None) or getattr(
            wildcard, "not_namespace", None
        ):
            raise UnsupportedSchemaError("XSD 1.1 wildcard constraints")
        self.wildcards[index] = {
            "namespaces": sorted(wildcard.namespace),
            "process": wildcard.process_contents,
        }
        return index

    def simple_type(self, xsd_type: Any) -> int:
        found = self._number(xsd_type, self.simple, self.simple_objects)
        if found is not None:
            return found
        index = len(self.simple) - 1
        entry: dict[str, Any] = {"ws": getattr(xsd_type, "white_space", None)}
        self.simple[index] = entry
        steps = []  # restrictions from this type down to its list, union or builtin
        base = xsd_type
        while True:
            if base.is_list() and hasattr(base, "item_type"):
                entry["variety"] = "list"
                entry["item"] = self.simple_type(base.item_type)
                break
            if base.is_union() and hasattr(base, "member_types"):
                entry["variety"] = "union"
                entry["members"] = [self.simple_type(m) for m in base.member_types]
                break
            if base.__class__.__name__ == "XsdAtomicBuiltin" or base.name in (
                f"{_XSD}anySimpleType",
                f"{_XSD}anyAtomicType",
            ):
                entry["variety"] = "atomic"
                entry["builtin"] = base.name.replace(_XSD, "xs:")
                break
            steps.append(base)
            base = base.base_type
            if base is None:  # pragma: no cover - every simple type has a base
                raise UnsupportedSchemaError(
                    f"simple type {xsd_type!r} without a builtin"
                )
        entry["facets"] = _facets(steps)
        return index

    def model(self, group: Any) -> int:
        found = self._number(group, self.models, self.model_objects)
        if found is not None:
            return found
        index = len(self.models) - 1
        particles: list[Any] = []
        tree = self._unroll(group, particles)
        follow: list[set[int]] = [set() for _ in particles]
        nullable, first, last = _glushkov(tree, follow)
        positions = [self._position(particle) for particle in particles]
        # Subset construction: a state is a set of positions; the start state
        # is the empty set, before any child.
        states: list[frozenset[int]] = [frozenset()]
        numbers: dict[frozenset[int], int] = {frozenset(): 0}
        table: list[dict[str, Any]] = []
        while len(table) < len(states):
            state = states[len(table)]
            reachable = first if not state else set().union(*(follow[p] for p in state))
            accept = nullable if not state else bool(state & last)
            edges, wild = self._edges(sorted(reachable), positions)
            row: dict[str, Any] = {"accept": accept, "edges": [], "wild": []}
            for (target, element), names in edges.items():
                if target not in numbers:
                    numbers[target] = len(states)
                    states.append(target)
                row["edges"].append([self.name_set(names), numbers[target], element])
            for wildcard, target in wild:
                if target not in numbers:
                    numbers[target] = len(states)
                    states.append(target)
                row["wild"].append([wildcard, numbers[target]])
            table.append(row)
        self.models[index] = {
            "states": table,
            "fallback": [
                self._position(particle) for particle in group.iter_elements()
            ],
            "cdata_ok": len(group) == 1 and _is_wildcard(group[0]),
            "empty_choice": not len(group)
            and group.model == "choice"
            and group.min_occurs > 0,
        }
        return index

    def _edges(
        self, reachable: list[int], positions: list[list[int]]
    ) -> tuple[
        dict[tuple[frozenset[int], int], list[str]], list[tuple[int, frozenset[int]]]
    ]:
        """The transitions from a state that can reach ``reachable``.

        Each child name goes to the set of positions it matches; every one of
        them must declare the child the same way, or the model is ambiguous.
        """
        by_name: dict[str, set[int]] = {}
        declared: dict[str, int] = {}
        wild: dict[int, set[int]] = {}
        for position in reachable:
            kind, number, names = positions[position]
            if kind:
                wild.setdefault(number, set()).add(position)
                continue
            particle_name = self.elements[number]["name"]
            for name_id in self.name_sets[names]:
                name = self.names[name_id]
                element = number if name_id == particle_name else self._global(name)
                if declared.setdefault(name, element) != element:
                    raise UnsupportedSchemaError(f"ambiguous content model at {name}")
                by_name.setdefault(name, set()).add(position)
        edges: dict[tuple[frozenset[int], int], list[str]] = {}
        for name, targets in by_name.items():
            edges.setdefault((frozenset(targets), declared[name]), []).append(name)
        return edges, [(number, frozenset(targets)) for number, targets in wild.items()]

    def _global(self, name: str) -> int:
        return self.element(self._schema.maps.elements[name])

    # ---- content models -------------------------------------------------------

    def _position(self, particle: Any) -> list[int]:
        if _is_wildcard(particle):
            return [1, self.wildcard(particle), -1]
        names = [particle.name, *sorted(particle.substitutes)]
        return [0, self.element(particle), self.name_set(names)]

    def _unroll(self, particle: Any, positions: list[Any]) -> Any:
        """``particle`` as a regular expression over positions, its bounds unrolled."""
        if particle.max_occurs == 0:
            return ("eps",)
        if hasattr(particle, "model"):  # a group
            if particle.model == "all":
                raise UnsupportedSchemaError("'all' model groups")
            kind = "seq" if particle.model == "sequence" else "alt"

            def make() -> Any:
                return (kind, [self._unroll(p, positions) for p in particle.content])

        else:

            def make() -> Any:
                positions.append(particle)
                return ("pos", len(positions) - 1)

        low, high = particle.min_occurs, particle.max_occurs
        if low > 64 or (high is not None and high - low > 64):
            raise UnsupportedSchemaError(f"occurrence bounds {low}..{high}")
        parts = [make() for _ in range(low)]
        if high is None:
            parts.append(("star", make()))
        else:
            tail: Any = ("eps",)
            for _ in range(high - low):
                tail = ("opt", ("seq", [make(), tail]))
            parts.append(tail)
        return ("seq", parts)


def _is_wildcard(particle: Any) -> bool:
    from xmlschema.validators import XsdAnyElement

    return isinstance(particle, XsdAnyElement)


def _facets(steps: list[Any]) -> dict[str, Any]:
    """The facets of each restriction step, in a form the validator reads.

    Patterns are a list per step (any one must match, and every step must
    match); bounds and lengths are kept from every step.
    """
    found: dict[str, Any] = {}
    for step in steps:
        for key, facet in (getattr(step, "facets", None) or {}).items():
            if key is None:
                continue
            local = key.replace(_XSD, "")
            if local == "pattern":
                found.setdefault("patterns", []).append(
                    [pattern.pattern for pattern in facet.patterns]
                )
            elif local == "enumeration":
                found.setdefault("enumerations", []).append(
                    [str(value) for value in facet.enumeration]
                )
            elif local in _FACETS:
                found.setdefault(local, []).append(str(facet.value))
            elif local not in ("whiteSpace", "assertion"):
                found.setdefault("other", []).append(local)
    return found


def _glushkov(tree: Any, follow: list[set[int]]) -> tuple[bool, set[int], set[int]]:
    """``(nullable, first, last)`` of ``tree``, filling ``follow``."""
    kind = tree[0]
    if kind == "eps":
        return True, set(), set()
    if kind == "pos":
        return False, {tree[1]}, {tree[1]}
    if kind in ("star", "opt"):
        _, first, last = _glushkov(tree[1], follow)
        if kind == "star":
            for position in last:
                follow[position] |= first
        return True, first, last
    if kind == "alt":
        nullable, first, last = False, set(), set()
        for part in tree[1]:
            n, f, la = _glushkov(part, follow)
            nullable, first, last = nullable or n, first | f, last | la
        return nullable, first, last
    # a sequence
    nullable, first, last = True, set(), set()
    for part in tree[1]:
        n, f, la = _glushkov(part, follow)
        for position in last:
            follow[position] |= f
        if nullable:
            first |= f
        last = (last | la) if n else la
        nullable = nullable and n
    return nullable, first, last


def build(schema: Any) -> SchemaIR:
    """The IR of ``schema``, an `xmlschema.XMLSchema`, numbered deterministically."""
    import xmlschema

    ir = SchemaIR()
    ir._schema = schema
    for name in sorted(schema.maps.elements):
        if not name.startswith(_XSD):
            ir.roots[ir.name(name)] = ir.element(schema.maps.elements[name])
    for name in sorted(schema.maps.attributes):
        ir.attributes[ir.name(name)] = ir.simple_type(schema.maps.attributes[name].type)
    data: dict[str, Any] = {
        "format": IR_FORMAT,
        "xmlschema": xmlschema.__version__,
        "names": ir.names,
        "name_sets": ir.name_sets,
        "roots": {str(k): v for k, v in sorted(ir.roots.items())},
        "attributes": {str(k): v for k, v in sorted(ir.attributes.items())},
        "elements": ir.elements,
        "complex": ir.complex,
        "simple": ir.simple,
        "models": ir.models,
        "wildcards": ir.wildcards,
    }
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
    data["digest"] = hashlib.sha256(encoded.encode()).hexdigest()
    ir.data = data
    return ir
