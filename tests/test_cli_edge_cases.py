"""Edge cases and error paths in ddi_l.cli."""

import io
import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.models.base import qn

# ---------------------------------------------------------------------------
# _ensure_reusable_input — lines 56-59
# ---------------------------------------------------------------------------


def test_ensure_reusable_input_seekable_raises():
    """Exercise lines 56-59: fallback when seekable() raises."""
    from ddi_l.cli import _ensure_reusable_input

    stream = MagicMock(spec=[])
    stream.seekable = MagicMock(side_effect=AttributeError)
    stream.read = MagicMock(side_effect=[b"<root/>", b""])
    result = _ensure_reusable_input(stream)
    result.seek(0)
    assert result.read() == b"<root/>"


def test_ensure_reusable_input_seekable_value_error():
    """Exercise lines 56-59: fallback when seekable() raises ValueError."""
    from ddi_l.cli import _ensure_reusable_input

    stream = MagicMock(spec=[])
    stream.seekable = MagicMock(side_effect=ValueError("closed"))
    stream.read = MagicMock(side_effect=[b"data", b""])
    result = _ensure_reusable_input(stream)
    result.seek(0)
    assert result.read() == b"data"


# ---------------------------------------------------------------------------
# _encode_json — line 163
# ---------------------------------------------------------------------------


def test_encode_json_custom_indent():
    """Exercise line 163: json.dumps with indent != 2."""
    from ddi_l.cli import _encode_json

    result = _encode_json({"key": "value"}, indent=4)
    assert b'"key"' in result
    decoded = json.loads(result)
    assert decoded["key"] == "value"


# ---------------------------------------------------------------------------
# _print_issues — lines 203-204
# ---------------------------------------------------------------------------


def test_print_issues(capsys):
    """Exercise lines 203-204: _print_issues."""
    from ddi_l.cli import _print_issues
    from ddi_l.schema_loader._validation import SchemaValidationIssue

    issue = SchemaValidationIssue(
        message="bad", xpath="/root", context="ctx", severity="error"
    )
    # Redirect stdout.buffer
    buf = io.BytesIO()
    with patch(
        "sys.stdout", new_callable=lambda: MagicMock(buffer=buf, flush=MagicMock)
    ):
        _print_issues([issue])
    output = buf.getvalue()
    assert b"bad" in output


# ---------------------------------------------------------------------------
# _format_table — line 211 (empty rows)
# ---------------------------------------------------------------------------


def test_format_table_empty():
    """Exercise line 211: _format_table with no rows."""
    from ddi_l.cli import _format_table

    result = _format_table([], ("id", "description"))
    assert "id" in result
    assert "description" in result


def test_format_table_with_rows():
    """Exercise lines 213-225: _format_table with actual rows."""
    from ddi_l.cli import _format_table

    rows = [("rule1", "Check something"), ("rule2", "Check other")]
    result = _format_table(rows, ("id", "description"))
    assert "rule1" in result
    assert "rule2" in result


# ---------------------------------------------------------------------------
# _render_cli_error — line 286
# ---------------------------------------------------------------------------


def test_render_cli_error_empty_message():
    """Exercise line 286: _render_cli_error with empty message."""
    from ddi_l.cli import _render_cli_error

    class EmptyError(Exception):
        def __str__(self):
            return ""

    result = _render_cli_error(EmptyError())
    assert result == "EmptyError"


def test_render_cli_error_normal():
    from ddi_l.cli import _render_cli_error

    result = _render_cli_error(ValueError("something wrong"))
    assert result == "something wrong"


# ---------------------------------------------------------------------------
# _handle_cli_error — line 295-296
# ---------------------------------------------------------------------------


def test_handle_cli_error_with_label():
    from ddi_l.cli import _handle_cli_error

    code = _handle_cli_error(ValueError("bad"), label="test.xml")
    assert code == 1


# ---------------------------------------------------------------------------
# _severity_level — line 325
# ---------------------------------------------------------------------------


def test_severity_level_none():
    """Exercise line 325: _severity_level with None."""
    from ddi_l.cli import _severity_level

    result = _severity_level(None)
    assert result == 2  # max of severity levels


def test_severity_level_unknown():
    """Exercise line 326: _severity_level with unknown string."""
    from ddi_l.cli import _severity_level

    result = _severity_level("info")
    assert result == 2  # max


def test_severity_level_warning():
    from ddi_l.cli import _severity_level

    assert _severity_level("warning") == 1


# ---------------------------------------------------------------------------
# _wrap_element — lines 533-535
# ---------------------------------------------------------------------------


def test_wrap_element_ddi_instance():
    from ddi_l._etree import create_element
    from ddi_l.cli import _wrap_element

    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    agency = create_element(qn(REUSABLE_NS, "Agency"))
    agency.text = "a"
    root.append(agency)
    id_elem = create_element(qn(REUSABLE_NS, "ID"))
    id_elem.text = "d1"
    root.append(id_elem)
    ver = create_element(qn(REUSABLE_NS, "Version"))
    ver.text = "1.0"
    root.append(ver)

    doc = _wrap_element(root)
    assert doc is not None


def test_wrap_element_fragment():
    """Exercise line 533-534: _wrap_element with FragmentInstance."""
    from ddi_l._etree import create_element
    from ddi_l.cli import _wrap_element

    root = create_element(qn(INSTANCE_NS, "FragmentInstance"))
    frag = _wrap_element(root)
    assert frag is not None


def test_wrap_element_invalid():
    """Exercise line 535: _wrap_element with invalid root."""
    from ddi_l._etree import create_element
    from ddi_l.cli import _wrap_element

    root = create_element("SomeOtherTag")
    with pytest.raises(ValueError, match="DDIInstance or FragmentInstance"):
        _wrap_element(root)


# ---------------------------------------------------------------------------
# _load_json_payload — lines 541-546
# ---------------------------------------------------------------------------


def test_load_json_payload_from_file(tmp_path):
    """Exercise lines 544-546: _load_json_payload from file."""
    from ddi_l.cli import _load_json_payload

    p = tmp_path / "test.json"
    p.write_text('{"key": "value"}')
    result = _load_json_payload(str(p))
    assert result["key"] == "value"


def test_load_json_payload_from_stdin():
    """Exercise line 541-542: _load_json_payload from stdin."""
    from ddi_l.cli import _load_json_payload

    mock_stdin = io.StringIO('{"key": "value"}')
    with patch("sys.stdin", mock_stdin):
        result = _load_json_payload(None)
    assert result["key"] == "value"


# ---------------------------------------------------------------------------
# _coerce_json_payload / _normalize_booleans — lines 574-601
# ---------------------------------------------------------------------------


def test_coerce_json_payload_single_key():
    """Exercise line 585-586: single key passes through."""
    from ddi_l.cli import _coerce_json_payload

    payload = {qn(INSTANCE_NS, "DDIInstance"): {"data": "val"}}
    result = _coerce_json_payload(payload, version=None)
    assert result == payload


def test_coerce_json_payload_wraps_multi_key():
    """Exercise lines 588-601: wraps multi-key payload."""
    from ddi_l.cli import _coerce_json_payload

    payload = {
        qn(REUSABLE_NS, "Agency"): "a",
        qn(REUSABLE_NS, "ID"): "d1",
    }
    result = _coerce_json_payload(payload, version=None)
    assert len(result) == 1


def test_coerce_json_payload_detects_fragment():
    """Exercise lines 596-599: detect FragmentInstance from keys."""
    from ddi_l.cli import _coerce_json_payload

    payload = {
        qn(INSTANCE_NS, "Fragment"): "frag",
        qn(REUSABLE_NS, "Other"): "val",
    }
    result = _coerce_json_payload(payload, version=None)
    keys = list(result.keys())
    assert "FragmentInstance" in keys[0]


def test_normalize_booleans_in_coerce():
    """Exercise lines 574-582: _normalize_booleans."""
    from ddi_l.cli import _coerce_json_payload

    payload = {qn(INSTANCE_NS, "DDIInstance"): {"@flag": True, "items": [False]}}
    result = _coerce_json_payload(payload, version=None)
    root_key = next(iter(result.keys()))
    assert result[root_key]["@flag"] == "true"
    assert result[root_key]["items"] == ["false"]


# ---------------------------------------------------------------------------
# _resolve_destination — lines 707-709
# ---------------------------------------------------------------------------


def test_resolve_destination_stdout():
    from ddi_l.cli import _resolve_destination

    result = _resolve_destination("-")
    assert result is sys.stdout.buffer


def test_resolve_destination_path():
    from ddi_l.cli import _resolve_destination

    result = _resolve_destination("/tmp/output.json")
    assert result == "/tmp/output.json"


# ---------------------------------------------------------------------------
# _resolve_destination_for_source — lines 733, 742
# ---------------------------------------------------------------------------


def test_resolve_destination_for_source_dir(tmp_path):
    """Exercise line 733: stdin source routed to directory."""
    from ddi_l.cli import _resolve_destination_for_source

    result = _resolve_destination_for_source(
        str(tmp_path),
        source_label="<stdin>",
        multiple_inputs=True,
        fallback_suffix=".json",
    )
    assert "stdin.json" in result


def test_resolve_destination_for_source_multi_error():
    """Exercise line 742: multiple inputs with non-dir output."""
    from ddi_l.cli import _resolve_destination_for_source

    with pytest.raises(ValueError, match="multiple inputs"):
        _resolve_destination_for_source(
            "/tmp/single_file.json",
            source_label="test.xml",
            multiple_inputs=True,
            fallback_suffix=".json",
        )


# ---------------------------------------------------------------------------
# _summarize_statuses / _finalize_statuses
# ---------------------------------------------------------------------------


def test_summarize_statuses_multiple():
    from ddi_l.cli import _finalize_statuses

    result = _finalize_statuses([("a.xml", 0), ("b.xml", 1)])
    assert result == 1


def test_finalize_statuses_all_ok():
    from ddi_l.cli import _finalize_statuses

    result = _finalize_statuses([("a.xml", 0)])
    assert result == 0


# ---------------------------------------------------------------------------
# main — lines 1259-1260
# ---------------------------------------------------------------------------


def test_main_no_command(capsys):
    """Exercise lines 1259-1260: main with no subcommand."""
    from ddi_l.cli import main

    result = main([])
    assert result == 1


# ---------------------------------------------------------------------------
# _configure_backends error path
# ---------------------------------------------------------------------------


def test_configure_backends_error():
    """Exercise lines 1263-1264: _configure_backends RuntimeError path."""
    import argparse

    from ddi_l.cli import _configure_backends

    args = argparse.Namespace(
        validation_backend="nonexistent_backend", conversion_backend=None
    )
    with pytest.raises((RuntimeError, ValueError)):
        _configure_backends(args)


# ---------------------------------------------------------------------------
# _has_failing_findings
# ---------------------------------------------------------------------------


def test_has_failing_findings_warning_threshold():
    from ddi_l.cli import _has_failing_findings
    from ddi_l.lint import LintFinding

    finding = LintFinding(rule_id="r1", message="warn", severity="warning")
    assert _has_failing_findings([], [finding], fail_severity="warning") is True
    assert _has_failing_findings([], [finding], fail_severity="error") is False


# ---------------------------------------------------------------------------
# _iter_sources
# ---------------------------------------------------------------------------


def test_iter_sources_path(tmp_path):
    from ddi_l.cli import _iter_sources

    p = tmp_path / "test.xml"
    p.write_text("<root/>")
    sources = _iter_sources([str(p)])
    assert len(sources) == 1
    assert sources[0][0] == str(p)


# ---------------------------------------------------------------------------
# _buffer_path_source / _prepare_cli_source
# ---------------------------------------------------------------------------


def test_buffer_path_source(tmp_path):
    from ddi_l.cli import _buffer_path_source

    p = tmp_path / "test.xml"
    p.write_bytes(b"<root/>")
    buf = _buffer_path_source(p)
    assert buf.read() == b"<root/>"


def test_prepare_cli_source_validate_path(tmp_path):
    from ddi_l.cli import _prepare_cli_source

    p = tmp_path / "test.xml"
    p.write_bytes(b"<root/>")
    result = _prepare_cli_source(p, validate=True)
    # Should return a buffer, not a Path
    assert hasattr(result, "read")


def test_prepare_cli_source_no_validate(tmp_path):
    from ddi_l.cli import _prepare_cli_source

    p = tmp_path / "test.xml"
    p.write_bytes(b"<root/>")
    result = _prepare_cli_source(p, validate=False)
    assert result == p
