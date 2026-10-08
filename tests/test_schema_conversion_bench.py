from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from tests import PACKAGE_FIXTURES_DIR

FIXTURE_PATH = PACKAGE_FIXTURES_DIR / "minimal_fragment.xml"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# The subprocess this test drives imports `benchmarks.schema_conversion_bench`.
# `benchmarks/` is a development directory and is not shipped in the sdist, so
# from an unpacked tarball the child would fail on the import rather than
# measuring anything.
pytestmark = pytest.mark.skipif(
    not (PROJECT_ROOT / "benchmarks").is_dir(),
    reason="benchmarks/ is not shipped in the sdist",
)


def _write_sitecustomize(tmp_path: Path) -> Path:
    """Create a sitecustomize module that patches ``Timer.repeat``."""

    sitecustomize_dir = tmp_path / "schema_bench_sitecustomize"
    sitecustomize_dir.mkdir()

    sitecustomize_path = sitecustomize_dir / "sitecustomize.py"
    sitecustomize_path.write_text(
        textwrap.dedent(
            f"""
            import atexit
            import json
            import os
            import sys
            from pathlib import Path

            sys.path.insert(0, {str(PROJECT_ROOT)!r})
            from benchmarks import schema_conversion_bench


            _records = []


            def _fake_repeat(self, repeat=3, number=1000000):
                _records.append({{"repeat": repeat, "number": number}})
                return [0.0123] * repeat


            schema_conversion_bench.Timer.repeat = _fake_repeat


            def _flush_records() -> None:
                destination = os.environ.get("SCHEMA_BENCH_TIMER_RESULT")
                if destination:
                    Path(destination).write_text(json.dumps(_records))


            atexit.register(_flush_records)
            """
        )
    )

    return sitecustomize_dir


def _run_benchmark(
    tmp_path: Path, backend: str
) -> tuple[subprocess.CompletedProcess[str], list[dict[str, int]]]:
    """Execute the benchmark entry point under controlled timing conditions."""

    results_path = tmp_path / "timer_calls.json"
    sitecustomize_dir = _write_sitecustomize(tmp_path)

    env = os.environ.copy()
    env["SCHEMA_BENCH_TIMER_RESULT"] = str(results_path)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(sitecustomize_dir)
        if not existing_pythonpath
        else os.pathsep.join((str(sitecustomize_dir), existing_pythonpath))
    )

    command = [
        sys.executable,
        "-m",
        "benchmarks.schema_conversion_bench",
        str(FIXTURE_PATH),
        "--backend",
        backend,
        "--repeats",
        "1",
        "--iterations",
        "1",
    ]

    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    records = json.loads(results_path.read_text()) if results_path.exists() else []
    return completed, records


def test_schema_conversion_bench_python(tmp_path: Path) -> None:
    completed, records = _run_benchmark(tmp_path, "python")

    assert "Backend: python" in completed.stdout
    assert "Fixtures:" in completed.stdout
    assert records == [{"repeat": 1, "number": 1}, {"repeat": 1, "number": 1}]
