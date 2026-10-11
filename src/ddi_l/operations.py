"""Transport-neutral operations shared by the CLI and the HTTP server.

Everything here takes bytes or plain Python objects and returns objects
(no argparse, printing or request types), so the same function backs
``ddi validate`` and ``POST /v1/validate``.
"""

from __future__ import annotations

import io
import zipfile
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from . import schema_loader
from ._schema_versions import DEFAULT_SCHEMA_VERSION, SUPPORTED_SCHEMA_VERSIONS
from .constants import get_namespace_set
from .io import read, write
from .lint import ProfileResult, run_lint, run_profile
from .models.base import qn
from .schema_loader._versions import detect_version_from_element
from .validation import ValidationReport, validate_document, validate_fragment

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from .document import DDIDocument, DDIFragment
    from .lint import LintFinding

__all__ = [
    "LAYOUTS",
    "TEMPLATE_FORMATS",
    "coerce_json_payload",
    "from_json_payload",
    "lint_source",
    "roundtrip_source",
    "supported_versions",
    "tables_import",
    "tables_spec",
    "tables_template",
    "to_json_payload",
    "to_jsonld_payload",
    "validate_source",
    "wrap_element",
]

#: Output layouts :func:`roundtrip_source` writes.
LAYOUTS = ("default", "colectica")

#: Formats :func:`tables_template` writes, with their media types.
TEMPLATE_FORMATS = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "zip": "application/zip",
}


def wrap_element(element: schema_loader.Element) -> DDIDocument | DDIFragment:
    """Return a document wrapper suitable for serialization.

    Args:
        element: Root XML element generated from JSON input.

    Returns:
        :class:`DDIDocument` or :class:`DDIFragment` depending on the root tag.

    Raises:
        ValueError: When the element is not a valid DDI instance or fragment root.
    """
    from .document import DDIDocument, DDIFragment

    detected_version = detect_version_from_element(element)
    namespace_set = get_namespace_set(detected_version)
    instance_ns = namespace_set["INSTANCE_NS"]

    if element.tag == qn(instance_ns, "DDIInstance"):
        return DDIDocument(element)
    if element.tag == qn(instance_ns, "FragmentInstance"):
        return DDIFragment(element)
    raise ValueError("Root element must be DDIInstance or FragmentInstance.")


def _drop_schema_fixed_attributes(node: object, tag: str | None = None) -> object:
    """Strip attributes the schema pins, so re-encoding does not add them.

    xmlschema materializes ``fixed`` attributes when decoding XML to a dict.
    They belong in the JSON view but not in XML written back from it, or the
    JSON round trip would add attributes the source never had.

    Only attributes the schema pins *on that element* are dropped: ``type``
    is fixed on ``r:ID`` but an ordinary attribute on ``r:KindOfData``. The
    lookup is therefore keyed by element, and ``tag`` carries that context
    down the recursion.
    """
    from .models._generated.fixed_attributes import FIXED_ATTRIBUTES_BY_ELEMENT

    if isinstance(node, dict):
        pinned = FIXED_ATTRIBUTES_BY_ELEMENT.get(tag or "", {})
        result = {}
        for key, value in node.items():
            if isinstance(key, str) and key.startswith("@"):
                allowed = pinned.get(key[1:])
                if allowed is not None and str(value) in allowed:
                    continue
            child_tag = key if isinstance(key, str) and key.startswith("{") else None
            result[key] = _drop_schema_fixed_attributes(value, child_tag)
        return result
    if isinstance(node, list):
        return [_drop_schema_fixed_attributes(item, tag) for item in node]
    return node


def coerce_json_payload(payload: dict, *, version: str | None = None) -> dict:
    """Wrap JSON payloads lacking an explicit root element tag."""

    def _normalize_booleans(node: object) -> object:
        if isinstance(node, bool):
            return "true" if node else "false"
        if isinstance(node, dict):
            return {key: _normalize_booleans(value) for key, value in node.items()}
        if isinstance(node, list):
            return [_normalize_booleans(item) for item in node]
        return node

    payload = _normalize_booleans(payload)  # type: ignore[assignment]

    # `to_dict` returns the root's inner mapping, so strip once the root tag
    # is known: the lookup is keyed by element.
    if len(payload) == 1:
        only = next(iter(payload))
        root = only if isinstance(only, str) and only.startswith("{") else None
        return _drop_schema_fixed_attributes(payload, root)  # type: ignore[return-value]

    namespace_set = get_namespace_set(version)
    instance_namespace = namespace_set["INSTANCE_NS"]

    fragment_keys = {"Fragment", "TopLevelReference"}
    root_tag = "DDIInstance"
    for key in payload:
        if not isinstance(key, str) or not key.startswith("{"):
            continue
        _, _, local = key.partition("}")
        if local in fragment_keys:
            root_tag = "FragmentInstance"
            break

    wrapped = {qn(instance_namespace, root_tag): payload}
    return _drop_schema_fixed_attributes(wrapped)  # type: ignore[return-value]


def validate_source(
    data: bytes, *, version: str | None = None, lint: bool = True
) -> ValidationReport:
    """Validate a DDI document held in memory.

    Args:
        data: The XML document as bytes.
        version: DDI schema version to validate against, or ``None`` for the
            version declared by the document.
        lint: Whether to include lint findings alongside schema issues.

    Returns:
        A :class:`~ddi_l.validation.ValidationReport`, whose ``to_dict()`` is
        already the shape an API response wants.
    """
    from .document import DDIFragment

    document = read(data, version=version)
    # A FragmentInstance has no instance-level Agency or Citation and may
    # reference items outside itself, so it is validated as a fragment.
    if isinstance(document, DDIFragment):
        return validate_fragment(document, include_lint=lint, version=version)
    return validate_document(document, include_lint=lint, version=version)


def lint_source(
    data: bytes, *, version: str | None = None, profile: str | None = None
) -> list[LintFinding] | ProfileResult:
    """Lint a DDI document held in memory.

    Args:
        data: The XML document as bytes.
        version: DDI schema version, or ``None`` to detect it.
        profile: Named lint profile to run; ``None`` runs the default rule set.

    Returns:
        A list of :class:`~ddi_l.lint.LintFinding` when no profile is named, or
        a :class:`~ddi_l.lint.ProfileResult` when one is.
    """
    from .document import DDIFragment

    document = read(data, version=version)
    if isinstance(document, DDIFragment):
        # `run_lint` takes a DDIInstance. `validate_fragment` already knows how
        # to wrap a fragment in the container the rules expect, so route through
        # it rather than building a second one here.
        report = validate_fragment(document, include_lint=True, lint_profile=profile)
        if profile is not None:
            # A profile request returns a ProfileResult for fragments too, so the
            # response shape and the schema issues match those of an instance.
            return ProfileResult(
                schema_issues=report.schema_issues,
                lint_findings=report.lint_findings,
            )
        return report.lint_findings
    if profile is not None:
        return run_profile(document, profile)
    return run_lint(document)


def to_json_payload(data: bytes, *, version: str | None = None) -> dict[str, Any]:
    """Convert a DDI document to its JSON representation."""
    document = read(data, version=version)
    return schema_loader.to_dict(document.root, process_namespaces=True)


def to_jsonld_payload(data: bytes, *, version: str | None = None) -> dict[str, Any]:
    """Convert a DDI document to JSON-LD using the Disco vocabulary.

    Unlike :func:`to_json_payload`, this is a *semantic* rendering rather than a
    transcription of the XML tree: it maps studies, variables, questions and
    universes onto DDI-RDF Discovery terms so the result is linked data.

    That makes it deliberately lossy and one-way: Disco covers a discovery
    subset of DDI-L and its specification states the reverse transformation "is
    not intended". Use :func:`to_json_payload` when the payload has to convert
    back into XML. See :mod:`ddi_l.jsonld`.
    """
    from .document import DDIFragment, Document
    from .jsonld import to_jsonld

    document = read(data, version=version)
    if isinstance(document, DDIFragment):
        raise ValueError(
            "JSON-LD conversion needs a DDIInstance; a FragmentInstance has no "
            "study to describe."
        )
    return to_jsonld(Document(document))


def from_json_payload(payload: dict, *, version: str | None = None) -> bytes:
    """Convert a JSON representation back into DDI XML bytes."""
    coerced = coerce_json_payload(payload, version=version)
    element = schema_loader.from_dict(coerced, version=version)
    document = wrap_element(element)
    return write(document, None)


def roundtrip_source(
    data: bytes, *, version: str | None = None, layout: str = "default"
) -> bytes:
    """Parse a document with the model layer and re-serialize it.

    Useful as a smoke test for formatting, namespace or encoding problems
    introduced by hand-editing.

    Args:
        data: The XML document as bytes.
        version: DDI schema version, or ``None`` to detect it.
        layout: ``"default"``, or ``"colectica"`` to write a
            ``FragmentInstance`` the way Colectica Designer does, so an
            unchanged export comes back byte for byte.

    Raises:
        ValueError: ``layout`` is unknown, or is ``"colectica"`` for a
            ``DDIInstance``.
    """
    from .document import DDIFragment

    if layout not in LAYOUTS:
        raise ValueError(
            f"Unknown layout {layout!r}; expected 'default' or 'colectica'."
        )
    document = read(data, version=version)
    if layout == "colectica" and not isinstance(document, DDIFragment):
        raise ValueError(
            "The colectica layout writes a FragmentInstance; this document is a "
            "DDIInstance."
        )
    return write(document, None, layout=layout)


def tables_import(
    data: bytes,
    *,
    agency: str | None = None,
    item_version: str | None = None,
    language: str | None = None,
    study_title: str | None = None,
) -> bytes:
    """Load metadata tables sent as one file and write them as DDI XML.

    Args:
        data: An ``.xlsx`` workbook, or a ``.zip`` of CSV files.
        agency: The agency of every item; overrides ``settings``.
        item_version: The version of items without their own.
        language: The language of names.
        study_title: Write a ``DDIInstance`` with the items inside a study of
            this title instead of a Colectica ``FragmentInstance``.

    Returns:
        The XML: a ``FragmentInstance`` in Colectica's layout, or the study.

    Raises:
        ValueError: ``data`` is neither a workbook nor a zip.
        ddi_l.tables.TableImportError: The tables have problems, listed in
            its ``problems``.
    """
    from .tables import load_tables

    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise ValueError("The body is not an .xlsx workbook or a .zip of CSV files.")
    tables = load_tables(data, agency=agency, version=item_version, language=language)
    if study_title is not None:
        return write(tables.to_study(study_title), None)
    return write(tables.to_fragment(), None, layout="colectica")


def tables_template(
    *,
    template_format: str = "xlsx",
    example: bool = False,
    languages: Sequence[str] = ("en", "fr"),
) -> bytes:
    """The metadata tables to fill in, blank or with the example.

    Args:
        template_format: ``"xlsx"`` for a workbook, ``"zip"`` for CSV files.
        example: The bilingual example instead of empty tables.
        languages: The languages to give columns such as ``label@en`` for.

    Raises:
        ValueError: An unknown format, no language, a malformed language tag,
            or an example in languages other than English and French.
    """
    from .tables._spec import LANGUAGE_TAG
    from .tables._templates import table_template_bytes

    if template_format not in TEMPLATE_FORMATS:
        raise ValueError(
            f"Unknown format {template_format!r}; expected 'xlsx' or 'zip'."
        )
    if not languages:
        raise ValueError("Give at least one language.")
    for language in languages:
        if not LANGUAGE_TAG.match(language):
            raise ValueError(
                f"{language!r} is not a language tag, such as en or fr-CA."
            )
    return table_template_bytes(
        example=example,
        languages=tuple(languages),
        layout=template_format,  # type: ignore[arg-type]
    )


def tables_spec() -> dict[str, Any]:
    """Every metadata table and column, with what goes in it."""
    from .tables._spec import (
        CUSTOM_PREFIX,
        MULTI_VALUE_SEPARATOR,
        SETTING_NAMES,
        TABLES,
    )

    return {
        "tables": [
            {
                "name": table.name,
                "help": table.help,
                "custom_columns": table.custom,
                "columns": [
                    {
                        "name": column.name,
                        "help": column.help,
                        "required": column.required,
                        "multilingual": column.multilingual,
                        "references": column.reference,
                        "multiple": column.multiple,
                    }
                    for column in table.columns
                ],
            }
            for table in TABLES
        ],
        "settings": [
            {"name": name, "required": required, "default": default, "help": help_}
            for name, (required, default, help_) in SETTING_NAMES.items()
        ],
        "multi_value_separator": MULTI_VALUE_SEPARATOR,
        "custom_prefix": CUSTOM_PREFIX,
    }


def supported_versions() -> dict[str, Any]:
    """Return the bundled DDI schema releases and the default."""
    return {
        "default": DEFAULT_SCHEMA_VERSION,
        "supported": list(SUPPORTED_SCHEMA_VERSIONS),
    }
