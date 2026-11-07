"""scripts/check_mutation.py fails on new survivors and on stale baseline entries."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_mutation.py"


def _load(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, results: dict) -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_mutation", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "BASELINE", tmp_path / "baseline.txt")
    monkeypatch.setattr(module, "_results", lambda: results)
    return module


def test_listed_survivors_pass(monkeypatch, tmp_path) -> None:
    results = {"m.a__mutmut_1": "survived", "m.a__mutmut_2": "killed"}
    module = _load(monkeypatch, tmp_path, results)
    module.BASELINE.write_text("# header\nm.a__mutmut_1  # equivalent\n")

    assert module.main([]) == 0


def test_a_new_survivor_fails(monkeypatch, tmp_path, capsys) -> None:
    results = {"m.a__mutmut_1": "survived", "m.a__mutmut_2": "no tests"}
    module = _load(monkeypatch, tmp_path, results)
    module.BASELINE.write_text("m.a__mutmut_1\n")

    assert module.main([]) == 1
    assert "new survivor: m.a__mutmut_2" in capsys.readouterr().out


def test_a_killed_baseline_entry_fails(monkeypatch, tmp_path, capsys) -> None:
    module = _load(monkeypatch, tmp_path, {"m.a__mutmut_1": "killed"})
    module.BASELINE.write_text("m.a__mutmut_1\n")

    assert module.main([]) == 1
    assert "no longer survives: m.a__mutmut_1" in capsys.readouterr().out


def test_an_unfinished_run_fails(monkeypatch, tmp_path) -> None:
    module = _load(monkeypatch, tmp_path, {"m.a__mutmut_1": "not checked"})
    module.BASELINE.write_text("")

    assert module.main([]) == 1


def test_update_keeps_reasons(monkeypatch, tmp_path) -> None:
    results = {"m.a__mutmut_1": "survived", "m.b__mutmut_1": "survived"}
    module = _load(monkeypatch, tmp_path, results)
    module.BASELINE.write_text("m.a__mutmut_1  # equivalent\nm.gone__mutmut_1\n")

    assert module.main(["--update"]) == 0

    lines = module.BASELINE.read_text().splitlines()
    assert [line for line in lines if not line.startswith("#")] == [
        "m.a__mutmut_1  # equivalent",
        "m.b__mutmut_1",
    ]
    assert module.main([]) == 0
