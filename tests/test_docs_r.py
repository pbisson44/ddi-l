"""The R examples in docs/r-users.*.md run against this package via reticulate.

Each page's ``r`` blocks are joined in order and run with ``Rscript`` in a
temporary directory, with reticulate pointed at the interpreter running the
tests. A line followed by ``# -> value`` is checked against that value. Blocks
preceded by ``<!-- docs-test: skip -->`` (installation steps) are left out.
Skipped when R or reticulate is not installed.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS = PROJECT_ROOT / "docs"
PAGES = sorted(DOCS.glob("r-users.*.md"))
SENTINEL = "DDI-R-DOCS-OK"

pytestmark = [
    pytest.mark.docs,
    pytest.mark.skipif(not DOCS.is_dir(), reason="docs/ is not shipped in the sdist"),
    pytest.mark.skipif(shutil.which("Rscript") is None, reason="R is not installed"),
]

_BLOCK = re.compile(
    r"(?P<preceding>^[^\n]*\n)?^(?P<indent>[ \t]*)```r\n(?P<code>.*?)^(?P=indent)```",
    re.MULTILINE | re.DOTALL,
)
_EXPECTED = re.compile(r"^\s*# -> (?P<value>.*)$")

_PRELUDE = r"""
.ddi_value <- function(x) {
  if (is.atomic(x) && length(x) == 1) return(as.character(x))
  paste(capture.output(print(x)), collapse = "\n")
}
.ddi_expect <- function(x, expected) {
  actual <- .ddi_value(x)
  if (!identical(actual, expected)) {
    stop(sprintf("expected %s, got %s", deparse(expected), deparse(actual)))
  }
  invisible(x)
}
"""


def _r_string(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _script(page: Path) -> str:
    lines: list[str] = []
    for match in _BLOCK.finditer(page.read_text(encoding="utf-8")):
        if "docs-test: skip" in (match.group("preceding") or ""):
            continue
        indent = len(match.group("indent"))
        lines.extend(line[indent:] for line in match.group("code").splitlines())
    for index in range(len(lines) - 1):
        expected = _EXPECTED.match(lines[index + 1])
        code = lines[index]
        if expected and code.strip() and "<-" not in code:
            value = _r_string(expected.group("value"))
            lines[index] = f".ddi_expect({code.strip()}, {value})"
    return "\n".join([_PRELUDE, *lines, f'cat("{SENTINEL}\\n")', ""])


def _reticulate_available() -> bool:
    probe = subprocess.run(
        [
            "Rscript",
            "-e",
            'quit(status = !requireNamespace("reticulate", quietly = TRUE))',
        ],
        capture_output=True,
    )
    return probe.returncode == 0


@pytest.mark.parametrize("page", PAGES, ids=[page.name for page in PAGES])
def test_r_examples_run(page: Path, tmp_path: Path) -> None:
    if not _reticulate_available():
        pytest.skip("the reticulate R package is not installed")
    shutil.copy(DOCS / "curriculum" / "survey_sample.csv", tmp_path)
    script = tmp_path / "examples.R"
    script.write_text(_script(page), encoding="utf-8")

    env = {**os.environ, "RETICULATE_PYTHON": sys.executable}
    result = subprocess.run(
        ["Rscript", str(script)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert SENTINEL in result.stdout


def test_both_languages_have_the_same_examples() -> None:
    blocks = {
        page.name: len(list(_BLOCK.finditer(page.read_text(encoding="utf-8"))))
        for page in PAGES
    }
    assert len(blocks) == 2, blocks
    assert len(set(blocks.values())) == 1, blocks
