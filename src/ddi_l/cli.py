"""Command line interface for ddi-l."""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

import orjson

from . import __version__
from ._schema_versions import (
    DEFAULT_SCHEMA_VERSION,
    SUPPORTED_SCHEMA_VERSIONS,
    get_schema_release,
    iter_schema_versions,
)
from .exceptions import DDIReadError, DDIWriteError
from .server.config import DEFAULT_MAX_BODY_BYTES, DEFAULT_MAX_CONCURRENT_JOBS

if TYPE_CHECKING:
    from .lint import LintFinding


class _LazyModule:
    """Import a module on first attribute access.

    Keeps ``ddi --help`` from loading the model layer and xmlschema.
    """

    def __init__(self, name: str) -> None:
        self._name = name

    def __getattr__(self, attribute: str) -> Any:
        return getattr(importlib.import_module(self._name), attribute)


operations: Any = _LazyModule("ddi_l.operations")
schema_loader: Any = _LazyModule("ddi_l.schema_loader")


def read(*args: Any, **kwargs: Any) -> Any:
    """Forward to :func:`ddi_l.io.read_ddi`."""
    from .io import read_ddi

    return read_ddi(*args, **kwargs)


def write(*args: Any, **kwargs: Any) -> Any:
    """Forward to :func:`ddi_l.io.write_ddi`."""
    from .io import write_ddi

    return write_ddi(*args, **kwargs)


def configure_lint(**kwargs: Any) -> Any:
    """Forward to :func:`ddi_l.lint.configure_lint`."""
    from .lint import configure_lint as _configure_lint

    return _configure_lint(**kwargs)


def iter_registered_profiles() -> Any:
    """Forward to :func:`ddi_l.lint.iter_registered_profiles`."""
    from .lint import iter_registered_profiles as _iter_profiles

    return _iter_profiles()


def iter_registered_rules() -> Any:
    """Forward to :func:`ddi_l.lint.iter_registered_rules`."""
    from .lint import iter_registered_rules as _iter_rules

    return _iter_rules()


def run_profile(*args: Any, **kwargs: Any) -> Any:
    """Forward to :func:`ddi_l.lint.run_profile`."""
    from .lint import run_profile as _run_profile

    return _run_profile(*args, **kwargs)


def run_lint_rules(*args: Any, **kwargs: Any) -> Any:
    """Forward to :func:`ddi_l.lint.run_lint`."""
    from .lint import run_lint

    return run_lint(*args, **kwargs)


def _coerce_json_payload(*args: Any, **kwargs: Any) -> Any:
    """Forward to :func:`ddi_l.operations.coerce_json_payload`."""
    return operations.coerce_json_payload(*args, **kwargs)


def _wrap_element(*args: Any, **kwargs: Any) -> Any:
    """Forward to :func:`ddi_l.operations.wrap_element`."""
    return operations.wrap_element(*args, **kwargs)


SchemaInput = Path | BinaryIO


_SPOOLED_BUFFER_LIMIT = 8 * 1024 * 1024  # 8 MiB keeps typical payloads in memory.


def _ensure_reusable_input(stream: BinaryIO) -> BinaryIO:
    """Return a seekable stream positioned at the start of the payload.

    When ``stream`` is already seekable it is rewound to the beginning. Non-
    seekable streams (for example ``sys.stdin`` in a pipeline) are copied into a
    temporary buffer so they can be consumed multiple times.
    """
    try:
        if stream.seekable():
            stream.seek(0)
            return stream
    except (AttributeError, OSError, ValueError):
        # Fall back to copying the input when ``seekable`` or ``seek`` is
        # unsupported. ``ValueError`` accounts for closed file handles.
        pass

    buffer = tempfile.SpooledTemporaryFile(  # noqa: SIM115
        mode="w+b", max_size=_SPOOLED_BUFFER_LIMIT
    )
    for chunk in iter(lambda: stream.read(io.DEFAULT_BUFFER_SIZE), b""):
        buffer.write(chunk)
    buffer.seek(0)
    return buffer  # type: ignore[return-value]


def _buffer_path_source(path: Path) -> BinaryIO:
    """Materialize a path input into a reusable binary buffer.

    Args:
        path: Filesystem path pointing to the XML payload.

    Returns:
        A seekable binary handle containing the serialized XML document.

    Notes:
        Uses :class:`tempfile.SpooledTemporaryFile` so that small documents stay
        in memory while larger files transparently spill to disk.
    """
    buffer = tempfile.SpooledTemporaryFile(  # noqa: SIM115
        mode="w+b", max_size=_SPOOLED_BUFFER_LIMIT
    )
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(io.DEFAULT_BUFFER_SIZE), b""):
            buffer.write(chunk)
    buffer.seek(0)
    return buffer  # type: ignore[return-value]


def _prepare_cli_source(source: SchemaInput, *, validate: bool) -> SchemaInput:
    """Return a CLI source optimized for the desired validation behaviour.

    Args:
        source: Path or binary stream provided by the CLI.
        validate: ``True`` when the caller intends to validate the payload
            before further processing.

    Returns:
        Either the original ``source`` or a seekable buffer containing the file
        contents when validation requires reusing a filesystem path.
    """
    if validate and isinstance(source, Path):
        return _buffer_path_source(source)
    return source


def _load_source(value: str | None) -> SchemaInput:
    """Return CLI input as either a filesystem path or raw bytes.

    Args:
        value: CLI argument representing a path to an XML document or ``'-'``
            to read from standard input.

    Returns:
        The original string when ``value`` refers to a filesystem path, or the
        binary ``sys.stdin`` stream when ``value`` is ``None`` or ``'-'``.
    """
    if value is None or value == "-":
        return sys.stdin.buffer
    return Path(value)


def _iter_sources(values: Sequence[str] | None) -> list[tuple[str, SchemaInput]]:
    """Normalize CLI inputs to reusable sources with descriptive labels.

    Args:
        values: Raw CLI arguments representing filesystem paths or ``'-'`` for
            standard input.

    Returns:
        A list of ``(label, source)`` tuples where ``label`` is a human-readable
        identifier for the source and ``source`` is a :class:`Path` or binary
        stream ready to be consumed by downstream helpers.
    """
    inputs = list(values or ["-"])
    normalized: list[tuple[str, SchemaInput]] = []
    stdin_buffer: BinaryIO | None = None

    for value in inputs:
        source = _load_source(value)

        if source is sys.stdin.buffer:
            stdin_buffer = stdin_buffer or _ensure_reusable_input(sys.stdin.buffer)  # type: ignore[arg-type]  # type: ignore[arg-type]
            source = stdin_buffer
        label = "<stdin>" if value in (None, "-") else str(source)
        normalized.append((label, source))

    return normalized


def _read_source_bytes(source: SchemaInput) -> bytes:
    """Return the raw XML bytes for a CLI source.

    ``ddi_l.operations`` takes bytes rather than paths or streams, so that the
    same function backs the CLI and the HTTP API. This is the adapter.
    """
    if isinstance(source, Path):
        return source.read_bytes()
    stream = _ensure_reusable_input(source)
    return stream.read()


def _encode_json(payload: object, *, indent: int | None) -> bytes:
    """Serialize a payload to JSON bytes with optional indentation."""
    options = orjson.OPT_APPEND_NEWLINE
    if indent is None or indent == 0:
        return orjson.dumps(payload, option=options)
    if indent == 2:
        return orjson.dumps(payload, option=options | orjson.OPT_INDENT_2)

    return (json.dumps(payload, indent=indent) + "\n").encode()


def _write_labeled_payload(
    payload: object,
    *,
    label: str,
    indent: int | None,
    with_labels: bool,
    destination: str | BinaryIO = sys.stdout.buffer,
) -> None:
    """Serialize CLI output with optional source labels."""
    wrapper = {"source": label, "payload": payload} if with_labels else payload
    encoded = _encode_json(wrapper, indent=None if with_labels else indent)

    if destination is sys.stdout.buffer:
        sys.stdout.buffer.write(encoded)  # type: ignore[union-attr]
        sys.stdout.flush()
        return

    path = Path(destination)  # type: ignore[arg-type]  # type: ignore[arg-type]
    with path.open("wb") as handle:
        handle.write(encoded)


def _print_issues(
    issues: Sequence[schema_loader.SchemaValidationIssue],
    *,
    include_context: bool = True,
) -> None:
    """Write validation issues to standard output as JSON.

    Args:
        issues: Validation issues generated by the schema loader.
        include_context: Whether to include contextual snippets in the
            serialized output.

    Notes:
        Serializes JSON to ``sys.stdout``.
    """
    payload = [issue.to_dict(include_context=include_context) for issue in issues]
    sys.stdout.buffer.write(_encode_json(payload, indent=2))


def _render_issues_text(
    issues: Sequence[schema_loader.SchemaValidationIssue], include_context: bool
) -> str:
    """Render validation issues as readable lines for a terminal."""
    if not issues:
        return "Document is valid.\n"
    lines: list[str] = []
    for issue in issues:
        position = ""
        if issue.line is not None:
            position = f" (line {issue.line}"
            position += f", column {issue.column})" if issue.column is not None else ")"
        lines.append(f"{issue.severity}: {issue.message}{position}")
        if issue.xpath:
            lines.append(f"    at {issue.xpath}")
        if include_context and issue.context:
            lines.append(f"    context: {issue.context}")
    count = len(issues)
    lines.append(f"{count} issue{'s' if count != 1 else ''} found.")
    return "\n".join(lines) + "\n"


def _format_table(rows: Sequence[tuple[str, str]], headers: tuple[str, ...]) -> str:
    """Render a simple padded table from ``rows``."""
    if not rows:
        widths = [len(header) for header in headers]
    else:
        widths = [
            max(len(header), *(len(row[i]) for row in rows))
            for i, header in enumerate(headers)
        ]

    def _row(values: Sequence[str]) -> str:
        return "  ".join(
            value.ljust(widths[index]) for index, value in enumerate(values)
        )

    lines = [_row(headers), _row(tuple("-" * width for width in widths))]
    lines.extend(_row(row) for row in rows)
    return "\n".join(lines)


def _run_lint_discovery(args: argparse.Namespace) -> None:
    """List registered lint rules or profiles then exit."""
    list_format = getattr(args, "list_format", "json")

    if args.list_rules:
        items = [
            {
                "id": rule_id,
                **({"description": description} if description else {}),
            }
            for rule_id, description in iter_registered_rules()
        ]
    else:
        items = [
            {
                "id": profile,
                "rules": rules,
                "description": ", ".join(rules),
            }
            for profile, rules in iter_registered_profiles()
        ]

    if list_format == "table":
        rows = [
            (
                item["id"],
                ", ".join(item["rules"])
                if "rules" in item
                else item.get("description", ""),
            )
            for item in items
        ]
        sys.stdout.write(_format_table(rows, ("id", "description")))
        sys.stdout.write("\n")
        return

    for item in items:
        sys.stdout.buffer.write(_encode_json(item, indent=None))


def _cli_exception_types() -> tuple[type[BaseException], ...]:
    """Exceptions reported as one-line errors rather than tracebacks."""
    return (
        FileNotFoundError,
        DDIReadError,
        DDIWriteError,
        schema_loader.SchemaValidationError,
        KeyError,
        OSError,
        RuntimeError,
        ValueError,
    )


def _render_cli_error(error: BaseException) -> str:
    """Format a concise error message for CLI reporting."""
    if isinstance(error, KeyError) and error.args:
        # KeyError.__str__ is repr(args[0]), which would quote the message.
        message = str(error.args[0]).strip()
    else:
        message = str(error).strip()
    if not message:
        return error.__class__.__name__
    return message


_DEBUG = False


def _split_rule_ids(value: str) -> list[str]:
    """Split a comma-separated ``--rules`` value into rule identifiers."""
    return [item.strip() for item in value.split(",") if item.strip()]


def _handle_cli_error(error: BaseException, *, label: str | None = None) -> int:
    """Write a concise error message to stderr and return a failure code.

    Raises:
        BaseException: ``error`` itself when ``--debug`` is active.
    """
    if _DEBUG:
        raise error
    message = _render_cli_error(error)
    prefix = f"[{label}] " if label else ""
    print(f"Error: {prefix}{message}", file=sys.stderr)
    return 1


def _summarize_statuses(statuses: Sequence[tuple[str, int]]) -> None:
    """Emit a compact summary of per-source exit codes."""
    if len(statuses) <= 1:
        return

    print("Summary:", file=sys.stderr)
    for label, status in statuses:
        outcome = "ok" if status == 0 else f"exit {status}"
        print(f"  {label}: {outcome}", file=sys.stderr)


def _finalize_statuses(statuses: Sequence[tuple[str, int]]) -> int:
    """Summarize per-source statuses and compute the aggregate exit code."""
    _summarize_statuses(statuses)
    return 0 if all(status == 0 for _, status in statuses) else 1


_SEVERITY_LEVELS: dict[str, int] = {"warning": 1, "error": 2}


def _severity_level(value: str | None) -> int:
    """Coerce a severity string to an integer priority."""
    if value is None:
        return max(_SEVERITY_LEVELS.values())
    return _SEVERITY_LEVELS.get(value.lower(), max(_SEVERITY_LEVELS.values()))


def _has_failing_findings(
    schema_issues: Sequence[schema_loader.SchemaValidationIssue],
    lint_findings: Sequence[LintFinding],
    *,
    fail_severity: str,
) -> bool:
    """Return ``True`` when any finding meets or exceeds ``fail_severity``."""
    threshold = _SEVERITY_LEVELS[fail_severity]

    for issue in schema_issues:
        if _severity_level(issue.severity) >= threshold:
            return True

    for finding in lint_findings:
        if _severity_level(finding.severity) >= threshold:
            return True

    return False


def _run_validate(args: argparse.Namespace) -> int:
    """Validate document(s) and report issues via the CLI."""
    include_context = not getattr(args, "redact_context", False)
    with_labels = getattr(args, "with_labels", False)
    text_output = getattr(args, "format", "text") == "text"
    statuses: list[tuple[str, int]] = []
    sources = _iter_sources(getattr(args, "inputs", None))
    multiple_inputs = len(sources) > 1

    for label, source in sources:
        try:
            destination = _resolve_destination_for_source(
                getattr(args, "output", "-"),
                source_label=label,
                multiple_inputs=multiple_inputs,
                fallback_suffix=".validate.json",
                suffix=".validate.json",
            )
            issues = schema_loader.validate(
                source,
                raise_error=False,
                include_context=include_context,
                version=args.version,
            )
            if destination is sys.stdout.buffer and not with_labels and text_output:
                if multiple_inputs:
                    sys.stdout.write(f"{label}:\n")
                sys.stdout.write(_render_issues_text(issues, include_context))
                sys.stdout.flush()
            else:
                payload = [
                    issue.to_dict(include_context=include_context) for issue in issues
                ]
                _write_labeled_payload(
                    payload,
                    label=label,
                    indent=2,
                    with_labels=with_labels,
                    destination=destination,
                )
            statuses.append((label, 1 if issues else 0))
        except _cli_exception_types() as error:
            statuses.append(
                (
                    label,
                    _handle_cli_error(error, label=label if multiple_inputs else None),
                )
            )

    return _finalize_statuses(statuses)


def _maybe_validate(
    source: SchemaInput,
    *,
    label: str,
    output: str,
    multiple_inputs: bool,
    with_labels: bool,
    include_context: bool,
    version: str | None,
) -> tuple[Sequence[schema_loader.SchemaValidationIssue] | None, SchemaInput]:
    """Validate a document and return the validation outcome and readable handle.

    Args:
        source: XML source provided as a path or raw bytes.
        label: Human-readable identifier for the source, used for reporting.
        output: Raw ``--output`` value used to resolve where validation payloads are written.
        multiple_inputs: Whether the CLI is processing multiple sources.
        with_labels: Whether payloads should be wrapped with their source labels.
        include_context: Whether to include contextual snippets in
            reported validation issues.
        version: Optional DDI schema version override for validation.

    Returns:
        A tuple containing the validation issues (or ``None`` when valid) and a
        seekable handle positioned at the beginning of the payload.
    """
    handle: SchemaInput
    handle = source if isinstance(source, Path) else _ensure_reusable_input(source)

    issues = schema_loader.validate(
        handle, raise_error=False, include_context=include_context, version=version
    )

    if not isinstance(handle, Path):
        with contextlib.suppress(AttributeError, OSError, ValueError):
            handle.seek(0)

    if issues:
        destination = _resolve_destination_for_source(
            output,
            source_label=label,
            multiple_inputs=multiple_inputs,
            fallback_suffix=".validate.json",
            suffix=".validate.json",
        )
        payload = [issue.to_dict(include_context=include_context) for issue in issues]
        _write_labeled_payload(
            payload,
            label=label,
            indent=2,
            with_labels=with_labels,
            destination=destination,
        )
        return issues, handle
    return None, handle


def _run_to_json(args: argparse.Namespace) -> int:
    """Convert one or more DDI documents to JSON, optionally validating first."""
    include_context = not getattr(args, "redact_context", False)
    statuses: list[tuple[str, int]] = []

    sources = _iter_sources(getattr(args, "inputs", None))
    multiple_inputs = len(sources) > 1
    for label, source in sources:
        try:
            prepared = _prepare_cli_source(source, validate=args.validate)
            if args.validate:
                issues, prepared = _maybe_validate(
                    prepared,
                    label=label,
                    output=args.output,
                    multiple_inputs=multiple_inputs,
                    with_labels=getattr(args, "with_labels", False),
                    include_context=include_context,
                    version=args.version,
                )
                if issues:
                    statuses.append((label, 1))
                    continue
            document = read(prepared, version=args.version)
            data = schema_loader.to_dict(document.root, process_namespaces=True)
            destination = _resolve_destination_for_source(
                args.output,
                source_label=label,
                multiple_inputs=multiple_inputs,
                fallback_suffix=".json",
                suffix=".json",
            )
            _write_labeled_payload(
                data,
                label=label,
                indent=args.indent,
                with_labels=getattr(args, "with_labels", False),
                destination=destination,
            )
            statuses.append((label, 0))
        except _cli_exception_types() as error:
            statuses.append(
                (
                    label,
                    _handle_cli_error(error, label=label if len(sources) > 1 else None),
                )
            )

    return _finalize_statuses(statuses)


def _load_json_payload(value: str | None) -> dict:
    """Parse JSON input from a path or stdin."""
    if value is None or value == "-":
        return json.load(sys.stdin)

    path = Path(value)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _iter_json_payloads(values: Sequence[str] | None) -> list[tuple[str, dict]]:
    """Load JSON payloads from multiple sources, caching stdin when needed."""
    inputs = list(values or ["-"])
    normalized: list[tuple[str, dict]] = []
    stdin_text: str | None = None

    for value in inputs:
        if value in (None, "-"):
            if stdin_text is None:
                stdin_text = sys.stdin.read()
            payload = json.loads(stdin_text)
            normalized.append(("<stdin>", payload))
            continue

        path = Path(value)
        with path.open("r", encoding="utf-8") as handle:
            normalized.append((str(path), json.load(handle)))

    return normalized


def _run_from_json(args: argparse.Namespace) -> int:
    """Convert JSON payload(s) into DDI XML, optionally validating the output."""
    include_context = not getattr(args, "redact_context", False)
    payloads = _iter_json_payloads(getattr(args, "inputs", None))
    multiple_inputs = len(payloads) > 1
    statuses: list[tuple[str, int]] = []

    for label, payload in payloads:
        try:
            coerced_payload = _coerce_json_payload(payload, version=args.version)
            element = schema_loader.from_dict(
                coerced_payload, process_namespaces=True, version=args.version
            )
            document = _wrap_element(element)

            if args.validate:
                issues = schema_loader.validate(
                    document.root,
                    raise_error=False,
                    include_context=include_context,
                    version=args.version,
                )
                if issues:
                    payload = [  # type: ignore[assignment]
                        issue.to_dict(include_context=include_context)
                        for issue in issues
                    ]
                    destination = _resolve_destination_for_source(
                        args.output,
                        source_label=label,
                        multiple_inputs=multiple_inputs,
                        fallback_suffix=".validate.json",
                        suffix=".validate.json",
                    )
                    _write_labeled_payload(
                        payload,
                        label=label,
                        indent=2,
                        with_labels=getattr(args, "with_labels", False),
                        destination=destination,
                    )
                    statuses.append((label, 1))
                    continue

            destination = _resolve_destination_for_source(
                args.output,
                source_label=label,
                multiple_inputs=multiple_inputs,
                fallback_suffix=".xml",
            )
            if getattr(args, "with_labels", False):
                buffer = io.BytesIO()
                write(
                    document,
                    destination=buffer,
                    pretty_print=not args.no_pretty_print,
                    xml_declaration=not args.no_declaration,
                    encoding=args.encoding,
                    version=args.version,
                )
                buffer.seek(0)
                payload = buffer.read().decode(args.encoding)  # type: ignore[assignment]
                _write_labeled_payload(
                    payload,
                    label=label,
                    indent=args.indent if hasattr(args, "indent") else None,
                    with_labels=True,
                    destination=destination,
                )
            else:
                write(
                    document,
                    destination=destination,
                    pretty_print=not args.no_pretty_print,
                    xml_declaration=not args.no_declaration,
                    encoding=args.encoding,
                    version=args.version,
                )
                if destination is sys.stdout.buffer:
                    sys.stdout.flush()
            statuses.append((label, 0))
        except _cli_exception_types() as error:
            statuses.append(
                (
                    label,
                    _handle_cli_error(error, label=label if multiple_inputs else None),
                )
            )

    return _finalize_statuses(statuses)


def _resolve_destination(value: str) -> str | BinaryIO:
    """Normalize the destination argument for writing output.

    Args:
        value: Destination path or ``'-'`` to indicate standard output.

    Returns:
        Either the original path or ``sys.stdout.buffer`` when writing to stdout.
    """
    if value == "-":
        return sys.stdout.buffer
    return value


def _resolve_destination_for_source(
    value: str,
    *,
    source_label: str,
    multiple_inputs: bool,
    fallback_suffix: str,
    suffix: str | None = None,
) -> str | BinaryIO:
    """Route output to stdout, a single path, or a directory per source."""
    if value == "-":
        return sys.stdout.buffer

    destination = Path(value)
    if not multiple_inputs and not destination.is_dir():
        return value

    if value.endswith(("/", "\\")) or destination.suffix == "":
        destination.mkdir(parents=True, exist_ok=True)
    if destination.is_dir():
        if source_label == "<stdin>":
            filename = f"stdin{suffix or fallback_suffix}"
        else:
            source_path = Path(source_label)
            resolved_suffix = (
                suffix if suffix is not None else source_path.suffix or fallback_suffix
            )
            filename = source_path.with_suffix(resolved_suffix).name
        return str(destination / filename)

    raise ValueError(
        "When providing multiple inputs the output must be '-' or a directory."
    )


def _run_versions(args: argparse.Namespace) -> int:
    """List the bundled DDI schema releases available to the CLI."""
    payload = {
        "default": DEFAULT_SCHEMA_VERSION,
        "supported": [
            {
                "version": version,
                "suffix": release["suffix"],
                "schema_filename": release["schema_filename"],
                "archive_checksum": release["archive_checksum"],
            }
            for version in iter_schema_versions()
            for release in (get_schema_release(version),)
        ],
    }

    sys.stdout.buffer.write(_encode_json(payload, indent=args.indent))
    return 0


def _run_roundtrip(args: argparse.Namespace) -> int:
    """Read and rewrite DDI document(s), optionally validating the input."""
    include_context = not getattr(args, "redact_context", False)
    sources = _iter_sources(getattr(args, "inputs", None))
    multiple_inputs = len(sources) > 1
    statuses: list[tuple[str, int]] = []

    for label, source in sources:
        try:
            prepared = _prepare_cli_source(source, validate=args.validate)
            if args.validate:
                issues, prepared = _maybe_validate(
                    prepared,
                    label=label,
                    output=args.output,
                    multiple_inputs=multiple_inputs,
                    with_labels=False,
                    include_context=include_context,
                    version=args.version,
                )
                if issues:
                    statuses.append((label, 1))
                    continue
            document = read(prepared, version=args.version)
            fallback_suffix = "" if label == "<stdin>" else Path(label).suffix
            destination = _resolve_destination_for_source(
                args.output,
                source_label=label,
                multiple_inputs=multiple_inputs,
                fallback_suffix=fallback_suffix or ".xml",
            )
            write(
                document,
                destination=destination,
                pretty_print=not args.no_pretty_print,
                xml_declaration=not args.no_declaration,
                encoding=args.encoding,
                version=args.version,
            )
            if destination is sys.stdout.buffer:
                sys.stdout.flush()
            statuses.append((label, 0))
        except _cli_exception_types() as error:
            statuses.append(
                (
                    label,
                    _handle_cli_error(error, label=label if multiple_inputs else None),
                )
            )

    return _finalize_statuses(statuses)


def _run_lint(args: argparse.Namespace) -> int:
    """Run lint rules against document(s) and emit findings as JSON."""
    if getattr(args, "list_rules", False) or getattr(args, "list_profiles", False):
        _run_lint_discovery(args)
        return 0

    include_context = not getattr(args, "redact_context", False)
    lint_configuration_updates: dict[str, object] = {}

    if getattr(args, "no_allowed_agencies", False):
        lint_configuration_updates["allowed_agencies"] = None
    elif getattr(args, "allowed_agency", None):
        lint_configuration_updates["allowed_agencies"] = tuple(args.allowed_agency)

    if getattr(args, "require_citation", None) is not None:
        lint_configuration_updates["require_citation"] = bool(args.require_citation)

    if getattr(args, "require_citation_title", None) is not None:
        lint_configuration_updates["require_citation_title"] = bool(
            args.require_citation_title
        )

    if getattr(args, "required_citation_language", None):
        lint_configuration_updates["required_citation_languages"] = tuple(
            args.required_citation_language
        )

    if lint_configuration_updates:
        configure_lint(**lint_configuration_updates)

    sources = _iter_sources(getattr(args, "inputs", None))
    multiple_inputs = len(sources) > 1
    statuses: list[tuple[str, int]] = []
    ignored_rules = set(getattr(args, "skip_rule", None) or ())
    selected_rules = (
        [rule for group in args.rules for rule in group] if args.rules else None
    )

    for label, source in sources:
        try:
            document = read(source, version=args.version)

            lint_findings = []
            schema_issues: Sequence[schema_loader.SchemaValidationIssue] = []

            if args.profile is not None:
                profile_result = run_profile(
                    document,
                    args.profile,
                    include_schema=args.validate,
                )
                lint_findings = [
                    finding
                    for finding in profile_result.lint_findings
                    if finding.rule_id not in ignored_rules
                ]
                schema_issues = profile_result.schema_issues
            else:
                if args.validate:
                    schema_issues = schema_loader.validate(
                        document.root,
                        raise_error=False,
                        include_context=include_context,
                        version=args.version,
                    )
                lint_findings = [
                    finding
                    for finding in run_lint_rules(document, rules=selected_rules)
                    if finding.rule_id not in ignored_rules
                ]

            payload = {
                "schema_issues": [
                    issue.to_dict(include_context=include_context)
                    for issue in schema_issues
                ],
                "lint_findings": [finding.as_dict() for finding in lint_findings],
            }
            destination = _resolve_destination_for_source(
                getattr(args, "output", "-"),
                source_label=label,
                multiple_inputs=multiple_inputs,
                fallback_suffix=".lint.json",
                suffix=".lint.json",
            )
            _write_labeled_payload(
                payload,
                label=label,
                indent=args.indent,
                with_labels=getattr(args, "with_labels", False),
                destination=destination,
            )

            should_fail = _has_failing_findings(
                schema_issues, lint_findings, fail_severity=args.fail_severity
            )
            statuses.append((label, 1 if should_fail else 0))
        except _cli_exception_types() as error:
            statuses.append(
                (
                    label,
                    _handle_cli_error(error, label=label if len(sources) > 1 else None),
                )
            )

    return _finalize_statuses(statuses)


def _run_to_jsonld(args: argparse.Namespace) -> int:
    """Convert one or more DDI documents to JSON-LD."""
    statuses: list[tuple[str, int]] = []
    sources = _iter_sources(getattr(args, "inputs", None))
    multiple_inputs = len(sources) > 1

    for label, source in sources:
        try:
            payload = operations.to_jsonld_payload(
                _read_source_bytes(source), version=args.version
            )
            destination = _resolve_destination_for_source(
                args.output,
                source_label=label,
                multiple_inputs=multiple_inputs,
                fallback_suffix=".jsonld",
                suffix=".jsonld",
            )
            _write_labeled_payload(
                payload,
                label=label,
                indent=args.indent,
                with_labels=False,
                destination=destination,
            )
            statuses.append((label, 0))
        except _cli_exception_types() as error:
            statuses.append(
                (
                    label,
                    _handle_cli_error(error, label=label if len(sources) > 1 else None),
                )
            )

    return _finalize_statuses(statuses)


def _run_serve(args: argparse.Namespace) -> int:
    """Run the HTTP API with uvicorn.

    The ``server`` extra is optional; its absence is reported as one
    actionable line.
    """
    try:
        import uvicorn

        from .server import ServerConfig, create_app
    except ImportError as error:  # pragma: no cover - depends on the extra
        print(
            "`ddi serve` needs the server extra: pip install 'ddi-l[server]'\n"
            f"({error})",
            file=sys.stderr,
        )
        return 1

    if args.max_body_mb <= 0:
        print("Error: --max-body-mb must be positive.", file=sys.stderr)
        return 2
    if args.max_jobs <= 0:
        print("Error: --max-jobs must be positive.", file=sys.stderr)
        return 2
    config = ServerConfig(
        max_body_bytes=int(args.max_body_mb * 1024 * 1024),
        max_concurrent_jobs=args.max_jobs,
        cors_allow_origins=tuple(getattr(args, "cors_allow_origins", None) or ()),
        enable_openapi=not getattr(args, "no_openapi", False),
    )

    # Check the port first so a bind failure gets an actionable message
    # instead of uvicorn's startup log followed by an OSError. The check is
    # advisory: uvicorn still performs the real bind.
    import socket

    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind((args.host, args.port))
        except OSError as error:
            print(
                f"Cannot bind {args.host}:{args.port} — {error.strerror or error}.\n"
                f"Something else is probably already listening. Try another port:\n"
                f"\n    ddi serve --port {args.port + 1}\n",
                file=sys.stderr,
            )
            return 1

    # Point the reader at the interactive docs, not just the bind address.
    display_host = (
        "localhost" if args.host in {"0.0.0.0", "127.0.0.1", "::"} else args.host
    )
    if config.enable_openapi:
        print(
            f"Interactive API docs: http://{display_host}:{args.port}/schema\n"
            f"OpenAPI document:     http://{display_host}:{args.port}/schema/openapi.json"
        )
    else:
        print(f"Service index: http://{display_host}:{args.port}/  (docs disabled)")

    uvicorn.run(create_app(config), host=args.host, port=args.port)
    return 0


def _configure_backends(args: argparse.Namespace) -> None:
    """Apply requested validation and conversion backends before executing commands."""
    validation_backend = getattr(args, "validation_backend", None)
    if validation_backend:
        schema_loader.set_validation_backend(validation_backend)

    conversion_backend = getattr(args, "conversion_backend", None)
    if conversion_backend:
        schema_loader.set_conversion_backend(conversion_backend)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for DDI utilities.

    Returns:
        Configured argument parser with subcommands for core CLI operations.
    """
    parser = argparse.ArgumentParser(
        prog="ddi", description="Utilities for DDI instance documents."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"ddi-l {__version__} (DDI Lifecycle {DEFAULT_SCHEMA_VERSION})",
        help="Show the ddi-l version and exit.",
    )
    backend_options = argparse.ArgumentParser(add_help=False)
    backend_options.add_argument(
        "--debug",
        action="store_true",
        help="Re-raise unexpected errors with a full traceback.",
    )
    # Only the "python" backend ships today; the options stay accepted for
    # scripts and plugins but are hidden from --help.
    backend_options.add_argument("--validation-backend", help=argparse.SUPPRESS)
    backend_options.add_argument("--conversion-backend", help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="command")

    version_help = "DDI schema version to use instead of the one the document declares."

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate an XML document against the DDI schema.",
        parents=[backend_options],
    )
    validate_parser.add_argument(
        "inputs",
        nargs="*",
        default=["-"],
        help="Path(s) to XML documents or '-' for stdin.",
    )
    validate_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help=(
            "Output on stdout: readable text (default) or a JSON array of issues. "
            "Files and --with-labels always receive JSON."
        ),
    )
    validate_parser.add_argument(
        "--output",
        default="-",
        help=(
            "Destination path or '-' for stdout; use a directory to capture per-source validation results."
        ),
    )
    validate_parser.add_argument(
        "--with-labels",
        action="store_true",
        help=(
            "Wrap validation results with their source labels as newline-delimited objects for streaming consumers."
        ),
    )
    validate_parser.add_argument(
        "--ddi-version",
        dest="version",
        choices=SUPPORTED_SCHEMA_VERSIONS,
        help=version_help,
    )
    validate_parser.add_argument(
        "--redact-context",
        action="store_true",
        help="Omit the contextual snippet from reported validation issues.",
    )
    validate_parser.set_defaults(func=_run_validate)

    to_json_parser = subparsers.add_parser(
        "to-json",
        help="Convert a DDI instance document to JSON.",
        parents=[backend_options],
    )
    to_json_parser.add_argument(
        "inputs",
        nargs="*",
        default=["-"],
        help="Path(s) to XML documents or '-' for stdin.",
    )
    to_json_parser.add_argument(
        "--output",
        default="-",
        help="Destination path or '-' for stdout; use a directory for multiple inputs.",
    )
    to_json_parser.add_argument(
        "--indent", type=int, default=2, help="Indentation to use for JSON output."
    )
    to_json_parser.add_argument(
        "--with-labels",
        action="store_true",
        help=(
            "Wrap each JSON payload with its source label as newline-delimited objects for streaming."
        ),
    )
    to_json_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the document before converting.",
    )
    to_json_parser.add_argument(
        "--ddi-version",
        dest="version",
        choices=SUPPORTED_SCHEMA_VERSIONS,
        help=version_help,
    )
    to_json_parser.add_argument(
        "--redact-context",
        action="store_true",
        help="Omit contextual snippets when validation issues are reported.",
    )
    to_json_parser.set_defaults(func=_run_to_json)

    from_json_parser = subparsers.add_parser(
        "from-json",
        help="Convert a JSON representation of a DDI document to XML.",
        parents=[backend_options],
    )
    from_json_parser.add_argument(
        "inputs",
        nargs="*",
        default=["-"],
        help="Path(s) to the JSON payload(s) or '-' for stdin.",
    )
    from_json_parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="Destination path or '-' for stdout; use a directory for multiple inputs.",
    )
    from_json_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the generated XML before writing.",
    )
    from_json_parser.add_argument(
        "--ddi-version",
        dest="version",
        choices=SUPPORTED_SCHEMA_VERSIONS,
        help=version_help,
    )
    from_json_parser.add_argument(
        "--no-pretty-print",
        action="store_true",
        help="Disable pretty printed XML output.",
    )
    from_json_parser.add_argument(
        "--no-declaration", action="store_true", help="Omit the XML declaration."
    )
    from_json_parser.add_argument(
        "--encoding", default="utf-8", help="Encoding to use when writing XML output."
    )
    from_json_parser.add_argument(
        "--redact-context",
        action="store_true",
        help="Omit contextual snippets when validation issues are reported.",
    )
    from_json_parser.add_argument(
        "--with-labels",
        action="store_true",
        help=(
            "Emit newline-delimited objects pairing each source label with the generated"
            " XML, supporting stdout or per-source outputs when writing to a directory."
        ),
    )
    from_json_parser.set_defaults(func=_run_from_json)

    roundtrip_parser = subparsers.add_parser(
        "roundtrip",
        help="Read and re-serialize a DDI XML document.",
        parents=[backend_options],
    )
    roundtrip_parser.add_argument(
        "inputs",
        nargs="*",
        default=["-"],
        help="Path(s) to the XML document(s) or '-' for stdin.",
    )
    roundtrip_parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="Destination path or '-' for stdout; use a directory for multiple inputs.",
    )
    roundtrip_parser.add_argument(
        "--validate", action="store_true", help="Validate the document before writing."
    )
    roundtrip_parser.add_argument(
        "--no-pretty-print",
        action="store_true",
        help="Disable pretty printed XML output.",
    )
    roundtrip_parser.add_argument(
        "--no-declaration", action="store_true", help="Omit the XML declaration."
    )
    roundtrip_parser.add_argument(
        "--encoding", default="utf-8", help="Encoding to use when writing XML output."
    )
    roundtrip_parser.add_argument(
        "--ddi-version",
        dest="version",
        choices=SUPPORTED_SCHEMA_VERSIONS,
        help=version_help,
    )
    roundtrip_parser.add_argument(
        "--redact-context",
        action="store_true",
        help="Omit contextual snippets when validation issues are reported.",
    )
    roundtrip_parser.set_defaults(func=_run_roundtrip)

    lint_parser = subparsers.add_parser(
        "lint",
        help="Lint a DDI document and report findings as JSON.",
        parents=[backend_options],
    )
    lint_parser.add_argument(
        "inputs",
        nargs="*",
        default=["-"],
        help="Path(s) to the XML document(s) or '-' for stdin.",
    )
    lint_parser.add_argument(
        "--output",
        default="-",
        help=(
            "Destination path or '-' for stdout; use a directory to capture per-source lint results."
        ),
    )
    lint_parser.add_argument(
        "--ddi-version",
        dest="version",
        choices=SUPPORTED_SCHEMA_VERSIONS,
        help=version_help,
    )
    lint_group = lint_parser.add_mutually_exclusive_group()
    lint_group.add_argument(
        "--profile", help="Named lint profile to run instead of individual rules."
    )
    lint_group.add_argument(
        "--rules",
        action="append",
        type=_split_rule_ids,
        help=(
            "Lint rule identifiers to execute instead of the default profile; "
            "comma-separated or repeated."
        ),
    )
    lint_list_group = lint_parser.add_mutually_exclusive_group()
    lint_list_group.add_argument(
        "--list-rules",
        action="store_true",
        help="List available lint rules and exit without running validation.",
    )
    lint_list_group.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available lint profiles and exit without running validation.",
    )
    lint_parser.add_argument(
        "--list-format",
        choices=("json", "table"),
        default="json",
        help=(
            "Output format for --list-rules/--list-profiles. "
            "Use 'json' for newline-delimited objects or 'table' for human-readable columns."
        ),
    )
    lint_parser.add_argument(
        "--allowed-agency",
        action="append",
        dest="allowed_agency",
        help=(
            "Restrict agencies to this allow-list; repeat to supply multiple values. The check "
            "is off by default and only runs once at least one value is supplied."
        ),
    )
    lint_parser.add_argument(
        "--no-allowed-agencies",
        action="store_true",
        help="Clear any configured agency allow-list, disabling the check.",
    )
    lint_parser.add_argument(
        "--require-citation",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Toggle the rule that requires <Citation> on the instance root (enabled by default).",
    )
    lint_parser.add_argument(
        "--require-citation-title",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Toggle the rule that requires a <Title> within <Citation> (enabled by default).",
    )
    lint_parser.add_argument(
        "--required-citation-language",
        action="append",
        dest="required_citation_language",
        help=(
            "BCP 47 language tag that must appear on citation titles; repeat to replace the defaults."
        ),
    )
    lint_parser.add_argument(
        "--skip-rule",
        "--disable-rule",
        action="append",
        dest="skip_rule",
        default=None,
        help="Rule identifier to exclude from lint results; repeat to ignore multiple rules.",
    )
    lint_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the document against the schema and include issues in the output.",
    )
    lint_parser.add_argument(
        "--indent", type=int, default=2, help="Indentation to use for JSON output."
    )
    lint_parser.add_argument(
        "--with-labels",
        action="store_true",
        help=(
            "Wrap lint results with their source labels as newline-delimited objects for streaming consumers."
        ),
    )
    lint_parser.add_argument(
        "--redact-context",
        action="store_true",
        help="Omit contextual snippets when schema issues are reported.",
    )
    lint_parser.add_argument(
        "--fail-severity",
        choices=tuple(_SEVERITY_LEVELS),
        default="error",
        # Errors fail, warnings are reported, as in most linters. Pass
        # `--fail-severity warning` for a strict CI gate.
        help=(
            "Minimum severity that produces a non-zero exit status (default: error); "
            "use 'warning' to fail on warnings too."
        ),
    )
    lint_parser.set_defaults(func=_run_lint)

    versions_parser = subparsers.add_parser(
        "versions", help="List supported DDI schema releases."
    )
    versions_parser.add_argument(
        "--indent", type=int, default=2, help="Indentation to use for JSON output."
    )
    versions_parser.set_defaults(func=_run_versions)

    to_jsonld_parser = subparsers.add_parser(
        "to-jsonld",
        help="Convert a DDI instance to JSON-LD (DDI-RDF Discovery vocabulary).",
        description=(
            "Render a document as linked data using DDI-RDF Discovery (Disco). "
            "This is a semantic mapping of the discovery subset -- studies, "
            "variables, questions, universes -- not a transcription of the XML, "
            "so it is lossy and does not convert back. Use `to-json` when the "
            "payload has to return to XML."
        ),
        parents=[backend_options],
    )
    to_jsonld_parser.add_argument(
        "inputs",
        nargs="*",
        default=["-"],
        help="Path(s) to XML documents or '-' for stdin.",
    )
    to_jsonld_parser.add_argument(
        "--output",
        default="-",
        help="Destination path or '-' for stdout; use a directory for multiple inputs.",
    )
    to_jsonld_parser.add_argument(
        "--indent", type=int, default=2, help="Indentation to use for JSON output."
    )
    to_jsonld_parser.add_argument(
        "--ddi-version",
        dest="version",
        choices=SUPPORTED_SCHEMA_VERSIONS,
        help=version_help,
    )
    to_jsonld_parser.set_defaults(func=_run_to_jsonld)

    serve_parser = subparsers.add_parser(
        "serve",
        help="Run the HTTP API (requires the 'server' extra).",
        description=(
            "Serve the same validate/lint/convert operations over HTTP. "
            "Interactive documentation is served at /schema, and a browser "
            "opening the root is redirected there. "
            "Install with: pip install 'ddi-l[server]'"
        ),
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help=(
            "Interface to bind (default: 127.0.0.1, i.e. this machine only). "
            "Use 0.0.0.0 to accept connections from the network."
        ),
    )
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind (default: 8000)."
    )
    serve_parser.add_argument(
        "--max-body-mb",
        type=float,
        default=DEFAULT_MAX_BODY_BYTES / (1024 * 1024),
        help="Largest request body to accept, in MiB (default: %(default)g).",
    )
    serve_parser.add_argument(
        "--max-jobs",
        type=int,
        default=DEFAULT_MAX_CONCURRENT_JOBS,
        help=(
            "Documents to process at once; further requests get 503 "
            "(default: number of CPUs, %(default)s)."
        ),
    )
    serve_parser.add_argument(
        "--cors-allow-origin",
        action="append",
        dest="cors_allow_origins",
        help=(
            "Allow browser requests from this origin; repeat for several. "
            "Off by default."
        ),
    )
    serve_parser.add_argument(
        "--no-openapi",
        action="store_true",
        help="Do not serve the OpenAPI schema and docs UI at /schema.",
    )
    serve_parser.set_defaults(func=_run_serve)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the DDI CLI.

    Args:
        argv: Optional command-line arguments to parse instead of ``sys.argv``.

    Returns:
        Exit status code from the selected subcommand or ``1`` when no command is provided.

    Notes:
        Parses command-line arguments and writes help text or command output to ``sys.stdout``.
    """
    global _DEBUG
    parser = build_parser()
    args = parser.parse_args(argv)
    _DEBUG = bool(getattr(args, "debug", False))
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    try:
        _configure_backends(args)
    except (RuntimeError, ValueError) as error:
        return _handle_cli_error(error)
    try:
        return args.func(args)
    except KeyboardInterrupt:  # pragma: no cover - interactive interrupt
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as error:  # last-resort CLI boundary
        # A command-line tool reports failures as one line on stderr, not as a
        # traceback. `--debug` re-raises for troubleshooting.
        if getattr(args, "debug", False):
            raise
        return _handle_cli_error(error)


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
