"""Shared utilities for normalizing XML inputs across the codebase."""

from __future__ import annotations

from pathlib import Path
from typing import IO, Any, Literal, cast, overload

from ._etree import Element, fromstring, parse_xml

FileLike = IO[str] | IO[bytes]
XMLSource = str | Path | bytes | bytearray | Element | FileLike
SourceKind = Literal["element", "bytes", "text", "path", "file"]

__all__ = [
    "FileLike",
    "SourceKind",
    "XMLSource",
    "coerce_element",
    "resolve_xml_source",
    "sniff_bom",
]


def _is_file_like(value: Any) -> bool:
    return hasattr(value, "read") and callable(value.read)


@overload
def resolve_xml_source(
    source: Element, *, require_existing_path: bool = False
) -> tuple[Literal["element"], Element]: ...


@overload
def resolve_xml_source(
    source: bytes | bytearray, *, require_existing_path: bool = False
) -> tuple[Literal["bytes"], bytes]: ...


@overload
def resolve_xml_source(
    source: str, *, require_existing_path: bool = False
) -> tuple[Literal["text", "path"], str | Path]: ...


@overload
def resolve_xml_source(
    source: Path, *, require_existing_path: bool = False
) -> tuple[Literal["path"], Path]: ...


@overload
def resolve_xml_source(
    source: IO[str], *, require_existing_path: bool = False
) -> tuple[Literal["file"], IO[str]]: ...


@overload
def resolve_xml_source(
    source: IO[bytes], *, require_existing_path: bool = False
) -> tuple[Literal["file"], IO[bytes]]: ...


def resolve_xml_source(
    source: XMLSource, *, require_existing_path: bool = False
) -> tuple[SourceKind, Element | bytes | str | Path | FileLike]:
    """Classify ``source`` into a canonical XML input category.

    Args:
        source: XML payload to classify.
        require_existing_path: When ``True`` a `Path` instance
            must resolve to an existing file on disk.

    Returns:
        tuple[SourceKind, payload]: A two-tuple containing the detected kind and
        the value normalized for that category. ``"bytes"`` payloads are always
        ``bytes`` objects, ``"text"`` payloads are ``str`` instances,
        ``"path"`` payloads are `Path` instances, ``"file"`` payloads
        are the original file-like object, and ``"element"`` payloads are the
        original `Element` instance.

    Raises:
        FileNotFoundError: When ``require_existing_path`` is ``True`` and a
            `Path` input does not exist on disk.
        TypeError: If ``source`` cannot be categorized as a supported XML
            payload.
    """
    if isinstance(source, Element):
        return "element", source

    if isinstance(source, (bytes, bytearray)):
        return "bytes", bytes(source)

    if isinstance(source, Path):
        if require_existing_path and not source.exists():
            raise FileNotFoundError(source)
        return "path", source

    if isinstance(source, str):
        stripped = source.lstrip()
        if "\n" in source or "\r" in source or stripped.startswith("<"):
            return "text", source

        potential_path = Path(source)
        path_like = False
        if (
            potential_path.is_absolute()
            or potential_path.suffix
            or any(sep in source for sep in ("/", "\\"))
            or (potential_path.parts and potential_path.parts[0] in {".", ".."})
        ):
            path_like = True

        if potential_path.exists():
            return "path", potential_path

        if require_existing_path and path_like:
            raise FileNotFoundError(potential_path)

        return "text", source

    if _is_file_like(source):
        return "file", source

    raise TypeError("Unsupported XML input type.")


def _is_binary_os_file(handle: object) -> bool:
    """Return whether ``handle`` is a binary stream backed by an OS file."""
    try:
        handle.fileno()  # type: ignore[attr-defined]
    except (AttributeError, OSError, ValueError):
        return False
    return isinstance(handle.read(0), bytes)  # type: ignore[attr-defined]


def coerce_element(
    source: XMLSource, *, require_existing_path: bool = False
) -> Element:
    """Return an `Element` for ``source`` regardless of representation.

    Args:
        source: XML payload in any supported representation.
        require_existing_path: When ``True``, a string or `Path` that
            looks like a filename but does not exist raises
            `FileNotFoundError`. Without it such a string falls through
            to the text branch and the parser reports "Start tag expected",
            which tells a caller who mistyped a filename nothing useful.

    Returns:
        Element: The parsed root element.
    """
    kind, payload = resolve_xml_source(
        source, require_existing_path=require_existing_path
    )

    if kind == "element":
        return cast(Element, payload)
    if kind == "path":
        return parse_xml(cast(Path, payload))
    if kind == "bytes":
        return fromstring(cast(bytes, payload))
    if kind == "text":
        return fromstring(cast(str, payload))
    if kind == "file":
        file_payload = cast(FileLike, payload)
        if _is_binary_os_file(file_payload):
            # Parse open files incrementally instead of buffering them.
            return parse_xml(file_payload)
        data = file_payload.read()
        if isinstance(data, str):
            data = data.encode("utf-8")
        return fromstring(data)

    raise TypeError("Unsupported XML input type.")


_UTF8_BOM = b"\xef\xbb\xbf"


def sniff_bom(source: XMLSource) -> bool | None:
    """Return whether ``source`` starts with a UTF-8 byte-order mark.

    The XML parser drops the mark, so a writer that wants to reproduce the
    input byte for byte has to learn about it before parsing. A stream is
    peeked and rewound, and must therefore be seekable.

    Args:
        source: XML payload in any representation `coerce_element`
            accepts.

    Returns:
        ``True`` or ``False`` when the source says, ``None`` when it cannot:
        an already-parsed `Element`, a stream that cannot be rewound,
        or a source that does not resolve.
    """
    try:
        kind, payload = resolve_xml_source(source)
    except (TypeError, OSError):
        return None
    if kind == "bytes":
        return bytes(cast(bytes, payload)).startswith(_UTF8_BOM)
    if kind == "text":
        return cast(str, payload).startswith("\ufeff")
    if kind == "path":
        try:
            with cast(Path, payload).open("rb") as handle:
                return handle.read(len(_UTF8_BOM)) == _UTF8_BOM
        except OSError:
            return None
    if kind == "file":
        handle = cast(Any, payload)
        try:
            if not handle.seekable():
                return None
            position = handle.tell()
            head = handle.read(len(_UTF8_BOM))
            handle.seek(position)
        except (AttributeError, OSError, ValueError):
            return None
        if isinstance(head, str):
            return head.startswith("\ufeff")
        return bytes(head) == _UTF8_BOM
    return None
