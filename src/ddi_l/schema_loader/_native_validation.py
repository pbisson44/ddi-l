"""Schema validation on the native backend: one native pass, xmlschema's words.

The native validator walks the document once against the schema's IR (see
`ddi_l.schema_loader._ir`) and flags each element that may break the
schema. A document with no flag is valid, and xmlschema is not loaded. For
a flagged element, xmlschema checks that element alone: its attributes and
text against a shallow copy (``LOCAL``), or its whole subtree when its
content model failed or it needs what only xmlschema does (``OPAQUE``,
``WILDCARD``). The errors are xmlschema's own, in its order, and carry the
line each element starts on.
"""

from __future__ import annotations

import contextlib
import gzip
import re
import threading
from collections.abc import Iterator
from importlib import resources
from typing import Any
from xml.etree import ElementTree

from .._etree import NATIVE

__all__ = ["available", "schema_errors", "unflagged"]

_LOCAL, _OPAQUE, _WILDCARD = 0, 1, 2
_DIGEST = re.compile(r'"digest":"([0-9a-f]{64})"')
_LOCK = threading.Lock()
# Per version: the compiled native schema and its IR digest, or None.
_COMPILED: dict[str, tuple[Any, str] | None] = {}
# Per xmlschema schema object: the IR rebuilt from it, to word errors.
_OBJECTS: dict[int, Any] = {}


def available() -> bool:
    """Whether the native validator can run: the native backend is in use."""
    return NATIVE


def _compiled(version: str) -> tuple[Any, str] | None:
    with _LOCK:
        if version not in _COMPILED:
            _COMPILED[version] = _load(version)
        return _COMPILED[version]


def _load(version: str) -> tuple[Any, str] | None:
    import ddi_l_native

    resource = (
        resources.files("ddi_l.schemas")
        / "ir"
        / f"v{version.replace('.', '_')}.json.gz"
    )
    if not resource.is_file():  # pragma: no cover - the IR ships for every version
        return None
    text = gzip.decompress(resource.read_bytes()).decode("utf-8")
    digest = _DIGEST.search(text)
    if digest is None:  # pragma: no cover - written by codegen/schema_ir.py
        return None
    return ddi_l_native.Schema(text), digest.group(1)


def unflagged(root: Any, version: str) -> list[tuple[Any, int, int, int]] | None:
    """The elements the native validator flags; ``None`` when it cannot say.

    An empty list means the document is valid.
    """
    import ddi_l_native

    if not isinstance(root, ddi_l_native.Element):
        return None
    compiled = _compiled(version)
    if compiled is None:  # pragma: no cover - the IR ships for every version
        return None
    found = compiled[0].validate(root)
    return None if found is None else list(found)


def _objects(schema: Any, version: str) -> Any | None:
    """The IR rebuilt from ``schema``, if it is the IR the validator ran."""
    from ._ir import build

    with _LOCK:
        ir = _OBJECTS.get(id(schema))
        if ir is None:
            ir = _OBJECTS[id(schema)] = (schema, build(schema))
    compiled = _compiled(version)
    if compiled is None or ir[1].data["digest"] != compiled[1]:
        return None
    return ir[1]


def _context(schema: Any, root: Any, level: int) -> Any:
    from xmlschema.namespaces import NamespaceMapper
    from xmlschema.validators.validation import ValidationContext

    resource = schema.maps.settings.get_xml_resource(root)
    return ValidationContext(
        source=resource,
        converter=NamespaceMapper(None, source=resource),
        level=level,
        check_identities=True,
        use_defaults=True,
    )


def _stub(element: Any) -> Any:
    """``element`` with its attributes and text, and childless children."""
    stub = ElementTree.Element(element.tag, dict(element.attrib))
    stub.text = element.text
    for child in element:
        ElementTree.SubElement(stub, child.tag).tail = child.tail
    return stub


def _decoded(validator: Any, element: Any, context: Any) -> list[Any]:
    from xmlschema.validators.exceptions import XMLSchemaStopValidation

    # Lax validation goes on after an error; this stops only a hook's stop.
    with contextlib.suppress(XMLSchemaStopValidation):
        validator.raw_decode(element, "lax", context)
    errors = list(context.errors)
    context.errors.clear()
    return errors


def schema_errors(
    schema: Any, root: Any, version: str, found: list[tuple[Any, int, int, int]]
) -> Iterator[Any]:
    """Xmlschema's errors for the elements the native validator flagged.

    They are what ``schema.iter_errors(root)`` yields. When the IR does not
    match ``schema`` (another xmlschema version), xmlschema validates the
    whole document instead.
    """
    ir = _objects(schema, version)
    if ir is None:
        yield from schema.iter_errors(root)
        return
    for element, kind, number, depth in found:
        context = _context(schema, root, depth)
        if kind == _WILDCARD:
            yield from _decoded(ir.wildcard_objects[number], element, context)
            continue
        declaration = ir.element_objects[number]
        if kind == _OPAQUE:
            yield from _decoded(declaration, element, context)
            continue
        stub = _stub(element)
        for error in _decoded(declaration, stub, context):
            if error.elem is None or error.elem is stub:
                error.elem = element
                yield error
