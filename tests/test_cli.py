from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

import pytest

from ddi_l import _schema_versions, cli, schema_loader
from ddi_l import lint as lint_module


@pytest.fixture(scope="module")
def cli_fixtures(fixtures_dir: Path) -> Path:
    """Return the directory containing CLI XML fixtures."""

    return fixtures_dir


@pytest.fixture(scope="module")
def fragment_fixture(cli_fixtures: Path) -> Path:
    """Path to the minimal fragment instance used in CLI tests."""

    return cli_fixtures / "minimal_fragment.xml"


def test_versions_lists_supported_releases(capsys):
    """`versions` surfaces bundled schema metadata and defaults."""

    exit_code = cli.main(["versions"])
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    supported_versions = {entry["version"] for entry in payload["supported"]}

    assert exit_code == 0
    assert payload["default"] == schema_loader.SCHEMA_VERSION
    assert supported_versions == set(_schema_versions.iter_schema_versions())
    assert all(entry["archive_checksum"] for entry in payload["supported"])


class NonSeekableSentinel(io.BytesIO):
    """Bytes buffer that forces the CLI to copy its contents."""

    def __init__(self, payload: bytes):
        super().__init__(payload)
        self._consumed = 0

    def seekable(self) -> bool:  # pragma: no cover - trivial override
        return False

    def seek(self, *args, **kwargs):  # pragma: no cover - should not be called
        raise io.UnsupportedOperation("stream is not seekable")

    def read(self, *args, **kwargs):
        chunk = super().read(*args, **kwargs)
        self._consumed += len(chunk)
        return chunk

    @property
    def consumed(self) -> int:
        return self._consumed


def test_maybe_validate_returns_reusable_stream(cli_fixtures: Path):
    """`_maybe_validate` yields a rewound handle for non-seekable inputs."""

    xml_bytes = (cli_fixtures / "minimal_instance.xml").read_bytes()
    stream = NonSeekableSentinel(xml_bytes)

    issues, reusable = cli._maybe_validate(
        stream,
        label="<stdin>",
        output="-",
        multiple_inputs=False,
        with_labels=False,
        include_context=True,
        version=None,
    )

    assert issues is None
    assert stream.consumed == len(xml_bytes)
    assert reusable is not stream
    assert reusable.read() == xml_bytes  # type: ignore[union-attr]


def test_maybe_validate_reports_issues_for_paths(cli_fixtures: Path, capsys):
    """`_maybe_validate` surfaces validation issues when given a path input."""

    path = cli_fixtures / "invalid_instance_missing_id.xml"

    issues, returned = cli._maybe_validate(
        path,
        label=str(path),
        output="-",
        multiple_inputs=False,
        with_labels=False,
        include_context=True,
        version=None,
    )
    captured = capsys.readouterr()

    assert returned == path
    assert issues
    assert captured.out.strip().startswith("[")


def test_validate_success(cli_fixtures: Path, capsys):
    """Validate command exits successfully for a valid XML instance.

    Args:
        capsys: Captures CLI stdout/stderr for assertions.
    """
    path = cli_fixtures / "minimal_instance.xml"
    exit_code = cli.main(["validate", str(path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "Document is valid."


def test_validate_version_override(cli_fixtures: Path, capsys):
    """`--version` directs validation to the requested schema release."""

    path = cli_fixtures / "minimal_instance_3_1.xml"
    exit_code = cli.main(["validate", str(path), "--ddi-version", "3.1"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.strip() == "Document is valid."


def test_validate_failure_reports_issues(cli_fixtures: Path, capsys):
    """Validate command surfaces validation issues for invalid XML.

    Args:
        capsys: Captures CLI stdout/stderr for assertions.
    """
    path = cli_fixtures / "invalid_instance_missing_id.xml"
    exit_code = cli.main(["validate", str(path)])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ID" in captured.out


def test_validate_unsupported_version(cli_fixtures: Path, capsys):
    """Unsupported schema overrides are surfaced as CLI errors."""

    path = cli_fixtures / "minimal_instance.xml"
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["validate", str(path), "--ddi-version", "2.5"])
    captured = capsys.readouterr()

    assert excinfo.value.code == 2
    assert "invalid choice" in captured.err.lower()


def test_validate_redact_context_removes_field(cli_fixtures: Path, capsys):
    """`--redact-context` omits contextual snippets from CLI output."""

    path = cli_fixtures / "invalid_instance_missing_id.xml"
    exit_code = cli.main(
        ["validate", str(path), "--redact-context", "--format", "json"]
    )
    captured = capsys.readouterr()

    assert exit_code == 1

    payload = json.loads(captured.out)
    assert isinstance(payload, list) and payload
    assert "context" not in payload[0]

    assert cli.main(["validate", str(path), "--redact-context"]) == 1
    assert "context:" not in capsys.readouterr().out


def test_validate_multiple_inputs_summarizes_status(cli_fixtures: Path, capsys):
    """`validate` accepts multiple inputs and reports a summary."""

    valid = cli_fixtures / "minimal_instance.xml"
    invalid = cli_fixtures / "invalid_instance_missing_id.xml"

    exit_code = cli.main(["validate", str(valid), str(invalid)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Missing required identification element" in captured.out
    assert "Summary:" in captured.err
    assert str(valid) in captured.err
    assert str(invalid) in captured.err
    assert f"{invalid}:" in captured.out
    assert "1 issue found." in captured.out


def test_validate_writes_per_source_payloads(
    cli_fixtures: Path, tmp_path: Path
) -> None:
    """`--output` writes per-source validation results when given a directory."""

    valid = cli_fixtures / "minimal_instance.xml"
    invalid = cli_fixtures / "invalid_instance_missing_id.xml"

    exit_code = cli.main(
        [
            "validate",
            str(valid),
            str(invalid),
            "--output",
            str(tmp_path / "reports"),
        ]
    )

    assert exit_code == 1

    valid_report = tmp_path / "reports" / "minimal_instance.validate.json"
    invalid_report = tmp_path / "reports" / "invalid_instance_missing_id.validate.json"

    assert json.loads(valid_report.read_text()) == []

    invalid_payload = json.loads(invalid_report.read_text())
    assert isinstance(invalid_payload, list) and invalid_payload
    assert invalid_payload[0]["message"]


def test_validate_writes_single_file(cli_fixtures: Path, tmp_path: Path, capsys):
    """`--output` writes validation results to a single file for valid inputs."""

    source = cli_fixtures / "minimal_instance.xml"
    destination = tmp_path / "report.json"

    exit_code = cli.main(["validate", str(source), "--output", str(destination)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ""

    payload = json.loads(destination.read_text())
    assert payload == []


def test_validate_with_labels_wraps_payload(cli_fixtures: Path, capsys):
    """`--with-labels` wraps validation payloads with their source labels."""

    path = cli_fixtures / "invalid_instance_missing_id.xml"

    exit_code = cli.main(["validate", str(path), "--with-labels"])
    captured = capsys.readouterr()

    assert exit_code == 1

    wrapped = json.loads(captured.out)
    assert wrapped["source"] == str(path)
    assert isinstance(wrapped["payload"], list) and wrapped["payload"]


def test_to_json_contains_reusable_agency_key(cli_fixtures: Path, capsys):
    """`to-json` command emits reusable agency key in output.

    Args:
        capsys: Captures CLI stdout/stderr for assertions.
    """
    path = cli_fixtures / "minimal_instance.xml"
    exit_code = cli.main(["to-json", str(path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "{ddi:reusable:3_3}Agency" in captured.out


def test_to_json_with_version_override(cli_fixtures: Path, capsys):
    """`to-json` honours explicit schema version overrides."""

    path = cli_fixtures / "minimal_instance_3_1.xml"
    exit_code = cli.main(
        [
            "to-json",
            str(path),
            "--validate",
            "--ddi-version",
            "3.1",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "{ddi:reusable:3_1}Agency" in captured.out


def test_to_json_rejects_unsupported_version(cli_fixtures: Path, capsys):
    """Explicit schema overrides must be supported for conversion."""

    path = cli_fixtures / "minimal_instance.xml"
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["to-json", str(path), "--ddi-version", "9.9"])
    captured = capsys.readouterr()

    assert excinfo.value.code == 2
    assert "invalid choice" in captured.err.lower()


def _build_instance_mapping(path: Path) -> dict:
    element = schema_loader.fromstring(path.read_bytes())
    return schema_loader.to_dict(element, process_namespaces=True)


def test_from_json_writes_valid_xml(cli_fixtures: Path, tmp_path: Path, capsys):
    """`from-json` converts JSON input to valid XML output."""

    mapping = _build_instance_mapping(cli_fixtures / "minimal_instance.xml")
    json_path = tmp_path / "instance.json"
    output = tmp_path / "output.xml"
    json_path.write_text(json.dumps(mapping))

    exit_code = cli.main(
        ["from-json", str(json_path), "--output", str(output), "--validate"]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert output.exists()
    assert schema_loader.validate(str(output), raise_error=False) == []


def test_from_json_validation_reports_issues(
    cli_fixtures: Path, tmp_path: Path, capsys
):
    """`from-json` surfaces validation failures from generated XML."""

    mapping = _build_instance_mapping(cli_fixtures / "minimal_instance.xml")
    mapping.pop("{ddi:reusable:3_3}ID", None)
    json_path = tmp_path / "invalid.json"
    output = tmp_path / "output.validate.json"
    json_path.write_text(json.dumps(mapping))

    exit_code = cli.main(
        ["from-json", str(json_path), "--output", str(output), "--validate"]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    payload = json.loads(output.read_text())
    assert any("id" in json.dumps(issue).lower() for issue in payload)


def test_from_json_writes_to_stdout(cli_fixtures: Path, monkeypatch, capsys):
    """`from-json` accepts stdin input and writes XML to stdout."""

    mapping = _build_instance_mapping(cli_fixtures / "minimal_instance.xml")

    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(json.dumps(mapping)))

    exit_code = cli.main(["from-json", "-", "--output", "-", "--validate"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert captured.out.lstrip().startswith("<?xml")


def test_from_json_validation_uses_output_directory(cli_fixtures: Path, tmp_path: Path):
    """Validation issues respect directory outputs for multiple sources."""

    mapping = _build_instance_mapping(cli_fixtures / "minimal_instance.xml")
    mapping.pop("{ddi:reusable:3_3}ID", None)

    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(mapping))
    second.write_text(json.dumps(mapping))

    output_dir = tmp_path / "output"
    exit_code = cli.main(
        [
            "from-json",
            str(first),
            str(second),
            "--output",
            str(output_dir),
            "--validate",
        ]
    )

    first_payload = json.loads((output_dir / "first.validate.json").read_text())
    second_payload = json.loads((output_dir / "second.validate.json").read_text())

    assert exit_code == 1
    assert any("id" in json.dumps(issue).lower() for issue in first_payload)
    assert any("id" in json.dumps(issue).lower() for issue in second_payload)


def test_from_json_validation_with_labels(cli_fixtures: Path, tmp_path: Path, capsys):
    """Validation output honours ``--with-labels`` just like conversion results."""

    mapping = _build_instance_mapping(cli_fixtures / "minimal_instance.xml")
    mapping.pop("{ddi:reusable:3_3}ID", None)

    json_path = tmp_path / "invalid.json"
    json_path.write_text(json.dumps(mapping))

    exit_code = cli.main(
        ["from-json", str(json_path), "--output", "-", "--validate", "--with-labels"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["source"] == str(json_path)
    assert any("id" in json.dumps(issue).lower() for issue in payload["payload"])


def test_from_json_with_labels_writes_labeled_outputs(
    cli_fixtures: Path, tmp_path: Path, capsys
):
    """`from-json` writes labeled NDJSON to stdout or per-source outputs."""

    mapping = _build_instance_mapping(cli_fixtures / "minimal_instance.xml")

    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(mapping))
    second.write_text(json.dumps(mapping))

    output_dir = tmp_path / "output"

    exit_code = cli.main(
        [
            "from-json",
            str(first),
            str(second),
            "--output",
            str(output_dir),
            "--with-labels",
        ]
    )
    captured = capsys.readouterr()

    first_payload = json.loads((output_dir / "first.json").read_text())
    second_payload = json.loads((output_dir / "second.json").read_text())

    assert exit_code == 0
    assert captured.out == ""
    assert first_payload["source"] == str(first)
    assert first_payload["payload"].lstrip().startswith("<?xml")
    assert second_payload["source"] == str(second)
    assert second_payload["payload"].lstrip().startswith("<?xml")


def test_to_json_validate_opens_input_once(cli_fixtures: Path, monkeypatch, capsys):
    """Validation buffers path inputs so the source file is opened once."""

    path = cli_fixtures / "minimal_instance.xml"
    recorded_calls = 0
    original_open = Path.open

    def tracked_open(self, *args, **kwargs):
        nonlocal recorded_calls
        if self == path:
            recorded_calls += 1
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", tracked_open)

    exit_code = cli.main(["to-json", str(path), "--validate"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert recorded_calls == 1


def test_to_json_validation_writes_labeled_outputs(
    cli_fixtures: Path, tmp_path: Path, capsys
):
    """`to-json --validate` writes labeled payloads per source when requested."""

    valid = cli_fixtures / "minimal_instance.xml"
    invalid = cli_fixtures / "invalid_instance_missing_id.xml"

    exit_code = cli.main(
        [
            "to-json",
            str(valid),
            str(invalid),
            "--validate",
            "--with-labels",
            "--output",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "Summary:" in captured.err

    valid_output = tmp_path / "minimal_instance.json"
    invalid_report = tmp_path / "invalid_instance_missing_id.validate.json"

    valid_payload = json.loads(valid_output.read_text())
    assert valid_payload["source"] == str(valid)
    assert isinstance(valid_payload["payload"], dict)

    invalid_payload = json.loads(invalid_report.read_text())
    assert invalid_payload["source"] == str(invalid)
    assert isinstance(invalid_payload["payload"], list) and invalid_payload["payload"]


def test_roundtrip_writes_valid_output(cli_fixtures: Path, tmp_path, capsys):
    """Roundtrip command writes valid XML output to disk.

    Args:
        tmp_path: Temporary directory for roundtrip output.
        capsys: Captures CLI stdout/stderr for assertions.
    """
    path = cli_fixtures / "minimal_instance.xml"
    output = tmp_path / "roundtrip.xml"
    exit_code = cli.main(
        ["roundtrip", str(path), "--output", str(output), "--validate"]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert output.exists()
    issues = schema_loader.validate(str(output), raise_error=False)
    assert issues == []


def test_roundtrip_with_version_override(cli_fixtures: Path, tmp_path: Path, capsys):
    """Roundtrip accepts explicit schema version overrides."""

    path = cli_fixtures / "minimal_instance_3_2.xml"
    output = tmp_path / "roundtrip.xml"
    exit_code = cli.main(
        [
            "roundtrip",
            str(path),
            "--output",
            str(output),
            "--validate",
            "--ddi-version",
            "3.2",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert output.exists()


def test_roundtrip_rejects_unsupported_version(
    cli_fixtures: Path, tmp_path: Path, capsys
):
    """Roundtrip fails fast for unsupported schema overrides."""

    path = cli_fixtures / "minimal_instance.xml"
    output = tmp_path / "roundtrip.xml"
    with pytest.raises(SystemExit) as excinfo:
        cli.main(
            ["roundtrip", str(path), "--output", str(output), "--ddi-version", "0.1"]
        )
    captured = capsys.readouterr()

    assert excinfo.value.code == 2
    assert "invalid choice" in captured.err.lower()


def test_roundtrip_supports_multiple_inputs(cli_fixtures: Path, tmp_path: Path, capsys):
    """Roundtrip can emit multiple inputs into a destination directory."""

    first = cli_fixtures / "minimal_instance.xml"
    second = cli_fixtures / "minimal_fragment.xml"
    destination_dir = tmp_path / "roundtripped"

    exit_code = cli.main(
        ["roundtrip", str(first), str(second), "--output", str(destination_dir)]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert (destination_dir / first.name).exists()
    assert (destination_dir / second.name).exists()
    assert "Summary:" in captured.err


def test_roundtrip_validation_writes_per_file_reports(
    cli_fixtures: Path, tmp_path: Path, capsys
):
    """Roundtrip writes validation issues beside other outputs for each source."""

    valid = cli_fixtures / "minimal_instance.xml"
    invalid = cli_fixtures / "invalid_instance_missing_id.xml"
    destination_dir = tmp_path / "roundtripped"

    exit_code = cli.main(
        [
            "roundtrip",
            str(valid),
            str(invalid),
            "--output",
            str(destination_dir),
            "--validate",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Summary:" in captured.err

    valid_output = destination_dir / valid.name
    invalid_report = destination_dir / "invalid_instance_missing_id.validate.json"

    assert valid_output.exists()
    issues = json.loads(invalid_report.read_text())
    assert isinstance(issues, list) and issues


def test_roundtrip_validate_opens_input_once(
    cli_fixtures: Path, monkeypatch, tmp_path, capsys
):
    """Roundtrip validation buffers path inputs to avoid reopening files."""

    path = cli_fixtures / "minimal_instance.xml"
    output = tmp_path / "roundtrip.xml"
    recorded_calls = 0
    original_open = Path.open

    def tracked_open(self, *args, **kwargs):
        nonlocal recorded_calls
        if self == path:
            recorded_calls += 1
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", tracked_open)

    exit_code = cli.main(
        ["roundtrip", str(path), "--output", str(output), "--validate"]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert output.exists()
    assert recorded_calls == 1


def test_roundtrip_handles_fragment_instances(fragment_fixture: Path, tmp_path, capsys):
    """Roundtrip validates fragment instances written from CLI.

    Args:
        tmp_path: Temporary directory for roundtrip output.
        capsys: Captures CLI stdout/stderr for assertions.
    """
    output = tmp_path / "fragment.xml"
    exit_code = cli.main(
        ["roundtrip", str(fragment_fixture), "--output", str(output), "--validate"]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert output.exists()
    issues = schema_loader.validate(str(output), raise_error=False)
    assert issues == []


def test_validate_missing_file_exits_cleanly(cli_fixtures: Path, capsys):
    """Validate command reports missing files without raising tracebacks."""

    path = cli_fixtures / "does-not-exist.xml"
    exit_code = cli.main(["validate", str(path)])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert "Error:" in captured.err


def test_to_json_malformed_input_exits_cleanly(cli_fixtures: Path, capsys):
    """`to-json` command surfaces parser failures without stack traces."""

    path = cli_fixtures / "malformed_instance.xml"
    exit_code = cli.main(["to-json", str(path)])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert "Error:" in captured.err


def test_roundtrip_missing_input_exits_cleanly(tmp_path, capsys):
    """Roundtrip command handles missing input files with concise errors."""

    missing = tmp_path / "missing.xml"
    output = tmp_path / "roundtrip.xml"
    exit_code = cli.main(["roundtrip", str(missing), "--output", str(output)])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert "Error:" in captured.err


def test_load_source_returns_stdin_buffer(monkeypatch):
    """`_load_source` should yield the stdin buffer without consuming it."""

    class SentinelBuffer:
        def read(self, *args, **kwargs):  # pragma: no cover - should not be invoked
            raise AssertionError("stdin buffer should not be read eagerly")

    sentinel = SentinelBuffer()

    class DummyStdin:
        def __init__(self, buffer):
            self.buffer = buffer

    monkeypatch.setattr(cli.sys, "stdin", DummyStdin(sentinel))

    assert cli._load_source("-") is sentinel
    assert cli._load_source(None) is sentinel


def test_ensure_reusable_input_spools_with_max_size(monkeypatch):
    """Non-seekable streams are buffered with an explicit spool size limit."""

    recorded_kwargs = {}

    def fake_spooled_tempfile(*args, **kwargs):
        recorded_kwargs["args"] = args
        recorded_kwargs["kwargs"] = kwargs  # type: ignore[assignment]
        return io.BytesIO()

    monkeypatch.setattr(tempfile, "SpooledTemporaryFile", fake_spooled_tempfile)

    class NonSeekable(io.BytesIO):
        def seekable(self):
            return False

    reusable = cli._ensure_reusable_input(NonSeekable(b"payload"))

    assert recorded_kwargs["kwargs"]["max_size"] == cli._SPOOLED_BUFFER_LIMIT  # type: ignore[call-overload]
    reusable.seek(0)
    assert reusable.read() == b"payload"


def test_to_json_from_stdin_with_validation(cli_fixtures: Path, monkeypatch, capsys):
    """`to-json` reads XML bytes from stdin, validates, and emits JSON."""

    xml_bytes = (cli_fixtures / "minimal_instance.xml").read_bytes()

    class DummyStdin:
        def __init__(self, buffer):
            self.buffer = buffer

    monkeypatch.setattr(cli.sys, "stdin", DummyStdin(io.BytesIO(xml_bytes)))

    exit_code = cli.main(["to-json", "-", "--validate", "--indent", "2"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    payload = json.loads(captured.out)
    assert "@isMaintainable" in payload
    assert captured.out.startswith("{\n")


def test_to_json_writes_output_files(cli_fixtures: Path, tmp_path: Path, capsys):
    """`to-json` writes per-source JSON payloads to the requested directory."""

    inputs = [
        cli_fixtures / "minimal_instance.xml",
        cli_fixtures / "minimal_fragment.xml",
    ]

    exit_code = cli.main(["to-json", *map(str, inputs), "--output", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ""
    assert "Summary:" in captured.err

    first_payload = json.loads((tmp_path / "minimal_instance.json").read_text())
    assert first_payload["{ddi:reusable:3_3}Agency"] == "example.agency"

    second_payload = json.loads((tmp_path / "minimal_fragment.json").read_text())
    assert second_payload


def test_cli_configures_requested_backends(cli_fixtures: Path, monkeypatch, capsys):
    """CLI applies requested backends before executing subcommands."""

    validation_calls: list[str] = []
    conversion_calls: list[str] = []

    original_set_validation_backend = schema_loader.set_validation_backend
    original_set_conversion_backend = schema_loader.set_conversion_backend

    monkeypatch.setattr(
        schema_loader,
        "set_validation_backend",
        lambda backend: (
            validation_calls.append(backend) or original_set_validation_backend(backend)  # type: ignore[func-returns-value]
        ),
    )
    monkeypatch.setattr(
        schema_loader,
        "set_conversion_backend",
        lambda backend: (
            conversion_calls.append(backend) or original_set_conversion_backend(backend)  # type: ignore[func-returns-value]
        ),
    )

    path = cli_fixtures / "minimal_instance.xml"
    exit_code = cli.main(
        [
            "to-json",
            str(path),
            "--validation-backend",
            "python",
            "--conversion-backend",
            "python",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert validation_calls == ["python"]
    assert conversion_calls == ["python"]


def test_cli_reports_unavailable_backend(monkeypatch, cli_fixtures: Path, capsys):
    """Unavailable backend requests surface concise CLI errors."""

    monkeypatch.setattr(
        cli.schema_loader, "get_available_conversion_backends", lambda: ("python",)
    )

    def failing_backend(backend: str) -> None:
        if backend == "python":
            raise RuntimeError("Python conversion backend is unavailable")

    monkeypatch.setattr(cli.schema_loader, "set_conversion_backend", failing_backend)

    path = cli_fixtures / "minimal_instance.xml"
    exit_code = cli.main(["to-json", str(path), "--conversion-backend", "python"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "unavailable" in captured.err.lower()


@pytest.mark.parametrize(
    "stream_factory", [io.BytesIO, NonSeekableSentinel], ids=["seekable", "nonseekable"]
)
def test_validate_from_stdin_consumes_stream(
    cli_fixtures: Path, monkeypatch, capsys, stream_factory
):
    """`validate` reads stdin exactly once for both seekable and non-seekable streams."""

    xml_bytes = (cli_fixtures / "minimal_instance.xml").read_bytes()
    stream = stream_factory(xml_bytes)

    class DummyStdin:
        def __init__(self, buffer):
            self.buffer = buffer

    monkeypatch.setattr(cli.sys, "stdin", DummyStdin(stream))

    exit_code = cli.main(["validate", "-"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.strip() == "Document is valid."

    if isinstance(stream, NonSeekableSentinel):
        assert stream.consumed == len(xml_bytes)
    else:
        assert stream.tell() == len(xml_bytes)


def test_to_json_from_nonseekable_stdin(cli_fixtures: Path, monkeypatch, capsys):
    """`to-json` copies non-seekable stdin before validation consumes it."""

    xml_bytes = (cli_fixtures / "minimal_instance.xml").read_bytes()
    stream = NonSeekableSentinel(xml_bytes)

    class DummyStdin:
        def __init__(self, buffer):
            self.buffer = buffer

    monkeypatch.setattr(cli.sys, "stdin", DummyStdin(stream))

    exit_code = cli.main(["to-json", "-", "--validate"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert stream.consumed == len(xml_bytes)

    payload = json.loads(captured.out)
    assert "@isMaintainable" in payload


def test_roundtrip_from_stdin_emits_valid_xml(
    cli_fixtures: Path, monkeypatch, tmp_path, capsys
):
    """Roundtrip command processes stdin and writes validated XML to stdout."""

    xml_bytes = (cli_fixtures / "minimal_instance.xml").read_bytes()

    class DummyStdin:
        def __init__(self, buffer):
            self.buffer = buffer

    monkeypatch.setattr(cli.sys, "stdin", DummyStdin(io.BytesIO(xml_bytes)))

    exit_code = cli.main(["roundtrip", "-", "--output", "-", "--validate"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    output_path = tmp_path / "stdin_roundtrip.xml"
    output_path.write_text(captured.out)

    issues = schema_loader.validate(str(output_path), raise_error=False)
    assert issues == []
    assert captured.out.lstrip().startswith("<?xml")


def test_roundtrip_from_nonseekable_stdin(cli_fixtures: Path, monkeypatch, capsys):
    """Roundtrip rewrites XML from a non-seekable stdin stream."""

    xml_bytes = (cli_fixtures / "minimal_instance.xml").read_bytes()
    stream = NonSeekableSentinel(xml_bytes)

    class DummyStdin:
        def __init__(self, buffer):
            self.buffer = buffer

    monkeypatch.setattr(cli.sys, "stdin", DummyStdin(stream))

    exit_code = cli.main(["roundtrip", "-", "--output", "-", "--validate"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert stream.consumed == len(xml_bytes)

    assert captured.out.lstrip().startswith("<?xml")


def test_lint_reports_findings_when_rules_fail(
    cli_fixtures: Path, tmp_path: Path, capsys
):
    """`lint` returns lint findings and a failing exit status when rules fail."""

    payload = (cli_fixtures / "minimal_instance.xml").read_text()
    failing_path = tmp_path / "lint_failure.xml"
    failing_path.write_text(payload.replace("example.agency", "unknown.agency"))

    # The allow-list is opt-in, so the rule only has something to enforce once
    # --allowed-agency supplies one.
    exit_code = cli.main(
        [
            "lint",
            str(failing_path),
            "--rules",
            "ddi.agency.allowed",
            "--allowed-agency",
            "example.agency",
            "--indent",
            "2",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1

    payload = json.loads(captured.out)
    assert payload["schema_issues"] == []
    assert payload["lint_findings"]
    assert payload["lint_findings"][0]["rule_id"] == "ddi.agency.allowed"


def test_lint_writes_output_to_file(cli_fixtures: Path, tmp_path: Path, capsys):
    """`lint` can route JSON results to a file when requested."""

    path = cli_fixtures / "minimal_instance.xml"
    destination = tmp_path / "lint_results.json"

    exit_code = cli.main(
        [
            "lint",
            str(path),
            "--rules",
            "ddi.agency.allowed",
            "--output",
            str(destination),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""

    payload = json.loads(destination.read_text())
    assert payload["schema_issues"] == []
    assert payload["lint_findings"] == []


_UNLABELLED_CODE_LIST = """<?xml version="1.0" encoding="utf-8"?>
<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3"
                  xmlns:l="ddi:logicalproduct:3_3">
  <TopLevelReference>
    <r:Agency>example.agency</r:Agency>
    <r:ID>Census2026</r:ID>
    <r:Version>1.0</r:Version>
    <r:TypeOfObject>CodeList</r:TypeOfObject>
  </TopLevelReference>
  <Fragment>
    <l:CodeList>
      <r:Agency>example.agency</r:Agency>
      <r:ID>code-list-1</r:ID>
      <r:Version>1.0</r:Version>
    </l:CodeList>
  </Fragment>
</FragmentInstance>
"""


def test_lint_warning_severity_allows_success(tmp_path: Path, capsys):
    """Warnings do not force a failure when the threshold is raised to ``error``.

    The document has to be one the rule actually fires on. ``CodeListType``
    declares an ``r:Label`` slot, so an unlabelled code list is a genuine
    finding -- unlike ``StudyUnit``, which the schema gives no label slot at
    all, or a ``Reference``, which is not a maintainable.
    """

    path = tmp_path / "unlabelled_code_list.xml"
    path.write_text(_UNLABELLED_CODE_LIST)

    exit_code = cli.main(
        [
            "lint",
            str(path),
            "--rules",
            "ddi.maintainable.labels",
            "--fail-severity",
            "error",
            "--indent",
            "2",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0

    payload = json.loads(captured.out)
    assert payload["schema_issues"] == []
    assert payload["lint_findings"]
    assert all(finding["severity"] == "warning" for finding in payload["lint_findings"])


def test_lint_error_severity_triggers_failure(
    cli_fixtures: Path, tmp_path: Path, capsys
):
    """Errors still produce a failing exit status when configured for ``error`` only."""

    payload = (cli_fixtures / "minimal_instance.xml").read_text()
    failing_path = tmp_path / "lint_failure.xml"
    failing_path.write_text(payload.replace("example.agency", "unknown.agency"))

    exit_code = cli.main(
        [
            "lint",
            str(failing_path),
            "--rules",
            "ddi.agency.allowed",
            "--allowed-agency",
            "example.agency",
            "--fail-severity",
            "error",
            "--indent",
            "2",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1

    payload = json.loads(captured.out)
    assert payload["schema_issues"] == []
    assert payload["lint_findings"]
    assert payload["lint_findings"][0]["severity"].lower() == "error"


def test_lint_profile_includes_schema_issues(cli_fixtures: Path, capsys):
    """Profiles can include schema validation issues when requested."""

    path = cli_fixtures / "invalid_instance_missing_id.xml"
    exit_code = cli.main(
        [
            "lint",
            str(path),
            "--profile",
            lint_module.DDI_PROFILE_DEFAULT,
            "--validate",
            "--redact-context",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1

    payload = json.loads(captured.out)
    assert payload["lint_findings"]
    assert payload["schema_issues"]
    assert "context" not in payload["schema_issues"][0]


def test_lint_unknown_profile_exits_cleanly(cli_fixtures: Path, capsys):
    """Unknown lint profiles surface concise CLI errors."""

    path = cli_fixtures / "minimal_instance.xml"
    exit_code = cli.main(["lint", str(path), "--profile", "does-not-exist"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "Error:" in captured.err


def test_lint_unknown_rule_exits_cleanly(cli_fixtures: Path, capsys):
    """Unknown lint rules are reported without tracebacks."""

    path = cli_fixtures / "minimal_instance.xml"
    exit_code = cli.main(["lint", str(path), "--rules", "does.not.exist"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "Error:" in captured.err


def test_lint_can_list_rules(capsys):
    """Lint rules can be enumerated without running validation."""

    exit_code = cli.main(["lint", "--list-rules"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    records = [json.loads(line) for line in captured.out.strip().splitlines()]
    assert any(record.get("id") == "ddi.agency.allowed" for record in records)


def test_lint_can_list_profiles_as_table(capsys):
    """Lint profiles can be displayed as a simple table."""

    exit_code = cli.main(["lint", "--list-profiles", "--list-format", "table"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert "ddi_profile_default" in captured.out.lower()


def test_lint_skip_rule_excludes_findings(cli_fixtures: Path, capsys):
    """`--skip-rule` can be repeated and drops the named rules."""

    path = cli_fixtures / "minimal_instance.xml"
    exit_code = cli.main(
        [
            "lint",
            "--skip-rule",
            "ddi.agency.allowed",
            "--disable-rule",
            "ddi.citation.present",
            str(path),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0, captured.err
    assert json.loads(captured.out)["lint_findings"] == []


def test_lint_rules_accepts_comma_separated_and_repeated(cli_fixtures: Path, capsys):
    """`--rules` takes comma-separated ids and does not swallow the input path."""

    path = cli_fixtures / "minimal_instance.xml"
    exit_code = cli.main(
        [
            "lint",
            "--rules",
            "ddi.agency.allowed,ddi.citation.present",
            "--rules",
            "ddi.maintainable.labels",
            str(path),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0, captured.err
    assert json.loads(captured.out)["lint_findings"] == []


def test_debug_reraises_per_source_errors(tmp_path: Path):
    """`--debug` shows the underlying exception instead of a one-line error."""

    with pytest.raises(FileNotFoundError):
        cli.main(["lint", "--debug", str(tmp_path / "missing.xml")])


def test_errors_are_one_line_without_debug(tmp_path: Path, capsys):
    exit_code = cli.main(["lint", str(tmp_path / "missing.xml")])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.err.startswith("Error:")
    assert "Traceback" not in captured.err


def test_validate_json_format_is_consistent(cli_fixtures: Path, capsys):
    """`--format json` prints a JSON array for valid and invalid documents alike."""

    assert (
        cli.main(
            ["validate", "--format", "json", str(cli_fixtures / "minimal_instance.xml")]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out) == []

    invalid = cli_fixtures / "invalid_instance_missing_id.xml"
    assert cli.main(["validate", "--format", "json", str(invalid)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload and payload[0]["severity"] == "error"


def test_validate_text_format_is_readable(cli_fixtures: Path, capsys):
    invalid = cli_fixtures / "invalid_instance_missing_id.xml"
    assert cli.main(["validate", str(invalid)]) == 1
    out = capsys.readouterr().out
    assert out.startswith("error: Missing required identification element")
    assert "    at /DDIInstance" in out
    assert out.rstrip().endswith("1 issue found.")
