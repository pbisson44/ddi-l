import hashlib
import importlib.util
import io
import ssl
import sys
import types
import zipfile
from pathlib import Path

import pytest

_PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src" / "ddi_l"

_PACKAGE_MODULE = types.ModuleType("ddi_l")
_PACKAGE_MODULE.__path__ = [str(_PACKAGE_ROOT)]
sys.modules.setdefault("ddi_l", _PACKAGE_MODULE)

_SCHEMA_VERSIONS_PATH = _PACKAGE_ROOT / "_schema_versions.py"
_SCHEMA_VERSIONS_SPEC = importlib.util.spec_from_file_location(
    "ddi_l._schema_versions", _SCHEMA_VERSIONS_PATH
)
assert _SCHEMA_VERSIONS_SPEC and _SCHEMA_VERSIONS_SPEC.loader
schema_versions = importlib.util.module_from_spec(_SCHEMA_VERSIONS_SPEC)
sys.modules.setdefault("ddi_l._schema_versions", schema_versions)
_SCHEMA_VERSIONS_SPEC.loader.exec_module(schema_versions)

_SCHEMA_SYNC_PATH = _PACKAGE_ROOT / "schema_sync.py"
_SCHEMA_SYNC_SPEC = importlib.util.spec_from_file_location(
    "ddi_l.schema_sync", _SCHEMA_SYNC_PATH
)
assert _SCHEMA_SYNC_SPEC and _SCHEMA_SYNC_SPEC.loader
schema_sync = importlib.util.module_from_spec(_SCHEMA_SYNC_SPEC)
sys.modules.setdefault("ddi_l.schema_sync", schema_sync)
_SCHEMA_SYNC_SPEC.loader.exec_module(schema_sync)
from urllib import error


class _FakeResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def close(self) -> None:
        pass


def _build_archive(
    version: str, schema_payload: str, *, extras: dict[str, str] | None = None
) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        suffix = version.replace(".", "_")
        archive.writestr(f"ddi/instance_{suffix}.xsd", schema_payload)
        archive.writestr("readme.txt", "DDI schema")
        archive.writestr("license.txt", "License text")
        for name, content in (extras or {}).items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _opener_factory(payload: bytes):
    def _opener(url: str) -> _FakeResponse:
        return _FakeResponse(payload)

    return _opener


def test_build_release_url_normalizes_version():
    """Release URLs follow the expected DDI download pattern."""

    url = schema_sync.build_release_url("3.3")
    assert url.endswith("/3.3/XMLSchema/instance_3_3.zip")


def _install_release_checksum(monkeypatch, version: str, checksum: str) -> None:
    original_get = schema_sync.get_schema_release

    def _patched(requested_version: str | None = None):
        release = dict(original_get(requested_version))
        if requested_version == version:
            release["archive_checksum"] = checksum
        return release

    monkeypatch.setattr(schema_sync, "get_schema_release", _patched)


def test_update_schema_package_writes_files(monkeypatch, tmp_path: Path):
    """update_schema_package extracts archives and verifies the schema."""

    schema_payload = (
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
    )
    data = _build_archive("3.3", schema_payload)
    expected_archive_checksum = hashlib.sha256(data).hexdigest()
    _install_release_checksum(monkeypatch, "3.3", expected_archive_checksum)

    result = schema_sync.update_schema_package(
        "3.3", target_root=tmp_path, opener=_opener_factory(data)
    )

    schema_path = tmp_path / "ddi" / "instance_3_3.xsd"
    assert schema_path.exists()
    assert schema_path.read_text() == schema_payload
    expected_checksum = hashlib.sha256(schema_payload.encode("utf-8")).hexdigest()
    assert result.checksum == expected_checksum
    assert schema_path in result.files


def test_update_schema_package_raises_for_missing_schema(monkeypatch, tmp_path: Path):
    """Missing instance schemas surface as FileNotFoundError."""

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("license.txt", "License text")

    _install_release_checksum(
        monkeypatch, "3.3", hashlib.sha256(buffer.getvalue()).hexdigest()
    )

    with pytest.raises(FileNotFoundError):
        schema_sync.update_schema_package(
            "3.3", target_root=tmp_path, opener=_opener_factory(buffer.getvalue())
        )


def test_update_schema_package_rejects_checksum_mismatch(monkeypatch, tmp_path: Path):
    """Checksum mismatches halt the update before unpacking."""

    schema_payload = (
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
    )
    data = _build_archive("3.3", schema_payload)
    _install_release_checksum(monkeypatch, "3.3", "deadbeef")

    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        schema_sync.update_schema_package(
            "3.3", target_root=tmp_path, opener=_opener_factory(data)
        )


def test_update_schema_package_rejects_path_traversal(monkeypatch, tmp_path: Path):
    """Archives attempting path traversal are refused."""

    schema_payload = (
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
    )
    data = _build_archive(
        "3.3",
        schema_payload,
        extras={"../evil.txt": "owned"},
    )
    expected_archive_checksum = hashlib.sha256(data).hexdigest()
    _install_release_checksum(monkeypatch, "3.3", expected_archive_checksum)

    with pytest.raises(RuntimeError, match="outside"):
        schema_sync.update_schema_package(
            "3.3", target_root=tmp_path, opener=_opener_factory(data)
        )

    assert not (tmp_path.parent / "evil.txt").exists()


def test_update_schema_package_preserves_readme(monkeypatch, tmp_path: Path):
    """Existing documentation files remain untouched during refresh."""

    schema_payload = (
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
    )
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Tracked README")

    data = _build_archive(
        "3.3",
        schema_payload,
        extras={"README.md": "Archive README"},
    )
    expected_archive_checksum = hashlib.sha256(data).hexdigest()
    _install_release_checksum(monkeypatch, "3.3", expected_archive_checksum)

    result = schema_sync.update_schema_package(
        "3.3", target_root=tmp_path, opener=_opener_factory(data)
    )

    assert readme_path.read_text() == "Tracked README"
    assert readme_path not in result.files


def test_update_schema_package_preserves_seeded_metadata(monkeypatch, tmp_path: Path):
    """Existing preserved files remain in place after an update."""

    schema_payload = (
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
    )
    readme_path = tmp_path / "README.md"
    readme_path.write_text("Project README")
    license_path = tmp_path / "license.txt"
    license_path.write_text("Bundled License")

    data = _build_archive("3.3", schema_payload)
    expected_archive_checksum = hashlib.sha256(data).hexdigest()
    _install_release_checksum(monkeypatch, "3.3", expected_archive_checksum)

    schema_sync.update_schema_package(
        "3.3", target_root=tmp_path, opener=_opener_factory(data)
    )

    assert readme_path.exists()
    assert readme_path.read_text() == "Project README"
    assert license_path.exists()
    assert license_path.read_text() == "Bundled License"


def test_update_schema_package_requires_recorded_checksum(monkeypatch, tmp_path: Path):
    """A missing checksum manifest entry surfaces a clear error."""

    schema_payload = (
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
    )
    data = _build_archive("3.3", schema_payload)

    original_get = schema_sync.get_schema_release

    def _patched(version: str | None = None):
        release = dict(original_get(version))
        release["archive_checksum"] = ""
        return release

    monkeypatch.setattr(schema_sync, "get_schema_release", _patched)

    with pytest.raises(RuntimeError, match="No recorded checksum"):
        schema_sync.update_schema_package(
            "3.3", target_root=tmp_path, opener=_opener_factory(data)
        )


def test_recorded_archive_checksums_align_with_expected(monkeypatch, tmp_path: Path):
    """Smoke-test the recorded archive digests against the known releases."""

    expected = {
        "3.1": "30f49976d2c16477733b3150aae8932ad9a6bee335408274662c0db2afd86732",
        "3.2": "1042769ddbdf7023e03347443ca203d13bf5ad33771ed9286f02ba210a4b0fc4",
        "3.3": "42712412d8309a08c6292c4bb7d178f3176b58070249866da2e2637a3fce8771",
    }

    assert dict(schema_versions.SCHEMA_ARCHIVE_CHECKSUMS) == expected

    version = "3.3"
    schema_payload = (
        "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'></xs:schema>"
    )
    archive_bytes = _build_archive(version, schema_payload)

    _install_release_checksum(monkeypatch, version, expected[version])

    real_sha256 = schema_sync.hashlib.sha256
    call_count = {"value": 0}

    def _fake_sha256(data: bytes = b""):
        if call_count["value"] == 0:
            call_count["value"] += 1

            class _ArchiveDigest:
                @staticmethod
                def hexdigest() -> str:
                    return expected[version]

            return _ArchiveDigest()

        call_count["value"] += 1
        return real_sha256(data)

    monkeypatch.setattr(schema_sync.hashlib, "sha256", _fake_sha256)

    result = schema_sync.update_schema_package(
        version, target_root=tmp_path, opener=_opener_factory(archive_bytes)
    )

    assert result.version == version
    assert call_count["value"] >= 2


def test_download_release_raises_for_ssl_failure():
    """SSL certificate failures surface as clear RuntimeErrors."""

    def _opener(url: str):  # pragma: no cover - simple helper
        raise error.URLError(ssl.SSLCertVerificationError("certificate verify failed"))

    with pytest.raises(RuntimeError, match="HTTPS certificate validation failed"):
        schema_sync.download_release("3.3", opener=_opener)


def test_clear_target_directory_preserves_files(tmp_path: Path):
    """_clear_target_directory keeps preserved files and removes others."""

    keep_path = tmp_path / "README.md"
    keep_path.write_text("keep")
    remove_path = tmp_path / "obsolete.txt"
    remove_path.write_text("remove")

    preserved = schema_sync._clear_target_directory(
        tmp_path,
        preserve={keep_path: False},
    )

    assert keep_path.exists()
    assert not remove_path.exists()
    assert preserved == {keep_path: False}


def test_write_archive_respects_preserve_flags(tmp_path: Path):
    """_write_archive skips existing files when overwrite is disallowed."""

    keep_path = tmp_path / "README.md"
    keep_path.write_text("original readme")
    replace_path = tmp_path / "license.txt"
    replace_path.write_text("original license")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("README.md", "new readme")
        archive.writestr("license.txt", "new license")

    with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as archive:
        written = schema_sync._write_archive(
            archive,
            tmp_path,
            {keep_path: False, replace_path: True},
        )

    assert keep_path.read_text() == "original readme"
    assert replace_path.read_text() == "new license"
    assert written == [replace_path]
