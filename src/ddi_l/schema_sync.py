"""Utilities to download and refresh bundled DDI XML Schema resources."""

from __future__ import annotations

import hashlib
import io
import ssl
import zipfile
from collections.abc import Callable, Mapping
from contextlib import closing, suppress
from dataclasses import dataclass
from pathlib import Path
from typing import IO
from urllib import error, request

from ._etree import fromstring
from ._schema_versions import get_schema_release

SchemaOpener = Callable[[str], IO[bytes]]

_DEFAULT_SCHEMA_ROOT = Path(__file__).resolve().parent / "schemas"


def build_release_url(version: str) -> str:
    """Return the expected download URL for a DDI Lifecycle release archive."""
    normalized = version.strip()
    suffix = normalized.replace(".", "_")
    return f"https://ddialliance.org/Specification/DDI-Lifecycle/{normalized}/XMLSchema/instance_{suffix}.zip"


def download_release(version: str, *, opener: SchemaOpener | None = None) -> bytes:
    """Fetch a DDI schema release as raw bytes."""
    opener = opener or request.urlopen
    url = build_release_url(version)
    try:
        with closing(opener(url)) as response:
            data = response.read()
    except error.URLError as exc:
        reason = getattr(exc, "reason", None)
        if isinstance(reason, ssl.SSLCertVerificationError):
            raise RuntimeError(
                "Failed to download DDI schema release:"
                " HTTPS certificate validation failed."
            ) from exc
        raise
    if not data:
        raise RuntimeError(f"Downloaded archive for version {version} is empty.")
    return data


_DEFAULT_PRESERVE: Mapping[Path, bool] = {
    Path("__init__.py"): True,
    Path("README.md"): False,
    Path("readme.txt"): False,
    Path("license.txt"): False,
}


def _resolve_preserve(
    root: Path, preserve: Mapping[Path, bool] | None
) -> dict[Path, bool]:
    resolved: dict[Path, bool] = {}
    if not preserve:
        return resolved
    for entry, allow_overwrite in preserve.items():
        absolute = entry if entry.is_absolute() else root / entry
        resolved[absolute] = allow_overwrite
    return resolved


def _clear_target_directory(
    root: Path, *, preserve: Mapping[Path, bool] | None = None
) -> dict[Path, bool]:
    if not root.exists():
        return _resolve_preserve(root, preserve)

    preserved = _resolve_preserve(root, preserve)
    for path in sorted(
        root.rglob("*"),
        key=lambda item: (item.is_file(), len(item.parts)),
        reverse=True,
    ):
        if path.is_dir():
            if path == root:
                continue
            with suppress(OSError):
                path.rmdir()
        else:
            if path in preserved:
                continue
            path.unlink()
    return preserved


def _write_archive(
    archive: zipfile.ZipFile,
    root: Path,
    preserved: Mapping[Path, bool] | None = None,
) -> list[Path]:
    written: list[Path] = []
    root = root.resolve()
    preserved_map = {
        Path(path).resolve(): allow for path, allow in (preserved or {}).items()
    }
    for info in archive.infolist():
        if info.is_dir():
            continue
        if info.filename.startswith("__MACOSX"):
            continue
        relative = Path(info.filename)
        if relative.is_absolute():
            raise RuntimeError(
                f"Archive entry {info.filename!r} specifies an absolute path."
            )
        destination = root / relative
        normalized = destination.resolve()
        try:
            normalized.relative_to(root)
        except ValueError as exc:
            raise RuntimeError(
                f"Archive entry {info.filename!r} would be written outside of {root}."
            ) from exc
        allow_overwrite = preserved_map.get(normalized, True)
        if not allow_overwrite and normalized.exists():
            continue
        normalized.parent.mkdir(parents=True, exist_ok=True)
        data = archive.read(info)
        normalized.write_bytes(data)
        written.append(normalized)
    return written


@dataclass(frozen=True)
class SchemaUpdateResult:
    """Metadata describing the outcome of a schema refresh."""

    version: str
    target_root: Path
    files: list[Path]
    checksum: str

    def to_dict(self) -> dict:  # noqa: D102
        return {
            "version": self.version,
            "target_root": str(self.target_root),
            "checksum": self.checksum,
            "files": [str(path) for path in self.files],
        }


def update_schema_package(
    version: str,
    *,
    target_root: Path | None = None,
    opener: SchemaOpener | None = None,
) -> SchemaUpdateResult:
    """Download and unpack a DDI schema release into the bundled resources."""
    archive_bytes = download_release(version, opener=opener)
    release = get_schema_release(version)
    expected_archive_checksum = release.get("archive_checksum", "")
    if not expected_archive_checksum:
        raise RuntimeError(
            "No recorded checksum for DDI schema archive version "
            f"{version}. Update SCHEMA_ARCHIVE_CHECKSUMS before syncing."
        )

    archive_checksum = hashlib.sha256(archive_bytes).hexdigest()
    if archive_checksum != expected_archive_checksum:
        raise RuntimeError(
            "Checksum mismatch for DDI schema archive version "
            f"{version}. Expected {expected_archive_checksum}, got {archive_checksum}."
        )

    target_root = target_root or _DEFAULT_SCHEMA_ROOT
    target_root.mkdir(parents=True, exist_ok=True)
    preserve_spec = {
        target_root / path: allow for path, allow in _DEFAULT_PRESERVE.items()
    }
    preserved = _clear_target_directory(target_root, preserve=preserve_spec)

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        written = _write_archive(archive, target_root, preserved)

    suffix = version.replace(".", "_")
    schema_path = target_root / "ddi" / f"instance_{suffix}.xsd"
    if not schema_path.exists():
        raise FileNotFoundError(
            f"Archive for version {version} did not contain {schema_path.name}."
        )

    # Ensure the schema parses before considering the update successful.
    fromstring(schema_path.read_bytes())

    checksum = hashlib.sha256(schema_path.read_bytes()).hexdigest()
    return SchemaUpdateResult(
        version=version,
        target_root=target_root,
        files=sorted(written),
        checksum=checksum,
    )


__all__ = [
    "SchemaUpdateResult",
    "build_release_url",
    "download_release",
    "update_schema_package",
]
