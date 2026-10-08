"""Every documented Python sample is executed, not just parsed.

``tests/test_docs_code_samples.py`` checks samples statically; this runs
them, so a sample that raises or no longer matches its prose fails.

How the samples are executed
----------------------------

Blocks are executed **per page**, in document order, sharing one namespace and
one working directory. Documentation is written as a narrative: a block creates
``doc``, the next one adds to it, a third saves it and a fourth reopens the file.
Running each block in isolation would fail nearly all of them for reasons that
say nothing about the library. That is also why the parametrization is per page
rather than per block -- the blocks are not independent, so they cannot be
independent test cases.

Each page gets a fresh temporary directory, so samples that write files neither
see each other's output nor touch the repository.

Seeded inputs
-------------

Many samples open a file the reader is assumed to already have -- ``my-study.xml``
in the middle of a tutorial, created by an earlier page. Rather than special-case
those, every ``*.xml`` and ``*.csv`` filename mentioned anywhere in a page's code
is created in that page's sandbox before anything runs: XML as a real DDI
instance built by this library, CSV as the same sample data the curriculum ships.
Seeding is harmless for samples that write the file themselves, since they
overwrite it.

Opting out
----------

Some blocks genuinely cannot run: deliberate fragments that reference an
undefined ``item`` or ``SomeType`` to show a shape, and samples needing data the
reader supplies (an Excel workbook, a populated SQLite database). Mark those with
an HTML comment immediately before the fence, which renders as nothing:

    <!-- docs-test: skip -->
    ```python
    ...
    ```

Prefer that to a comment inside the block, which the reader would see.

When a page's *first* block needs that data, marking it alone is not enough:
blocks share a namespace, so every later block fails on a name the skipped one
would have defined. Put ``<!-- docs-test: skip-page -->`` anywhere on the page
instead, and say why.

Indented fences count
---------------------

A block indented into a numbered step is still a block and is executed.
"""

from __future__ import annotations

import ast
import contextlib
import io
import os
import re
import shutil
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"

pytestmark = [
    pytest.mark.docs,
    pytest.mark.skipif(
        not DOCS_DIR.is_dir(), reason="docs/ is not shipped in the sdist"
    ),
]

# Captures the fence and the line before it (for the opt-out marker). The
# indent group finds fences nested in list items; the closing fence must match
# the opening indent.
_FENCED_PYTHON = re.compile(
    r"(?P<preceding>^[^\n]*\n)?^(?P<indent>[ \t]*)```(?:python|py)\n"
    r"(?P<code>.*?)^(?P=indent)```",
    re.MULTILINE | re.DOTALL,
)

_SKIP_MARKER = "docs-test: skip"

# One marker anywhere on a page opts the whole page out.
_SKIP_PAGE_MARKER = "docs-test: skip-page"

# The curriculum annotates prints with the value the reader should see:
#
#     print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
#
# Executing a sample proves it runs; this proves it still says what the
# surrounding prose claims. A hedged claim -- one containing "(or ..." -- is
# prose, not a value, and is left alone.
_OUTPUT_CLAIM = re.compile(r"#\s*->\s*(?P<expected>.+?)\s*$", re.MULTILINE)


def _output_claims(code: str) -> list[str]:
    """Return the deterministic printed values a block claims."""
    return [
        match.group("expected")
        for match in _OUTPUT_CLAIM.finditer(code)
        if "(or " not in match.group("expected")
    ]


# Filenames a sample might open. Deliberately narrow: matching every quoted
# string would create files for glob patterns and URL fragments too.
_FILENAME = re.compile(r"['\"]([\w][\w./-]*\.(?:xml|csv))['\"]")

_CSV_SEED_PATH = PROJECT_ROOT / "docs" / "curriculum" / "survey_sample.csv"


def _csv_seed() -> str:
    """Read the sample CSV lazily.

    Not a module-level constant: `docs/` is absent from the sdist, and reading
    at import time would fail during collection, before the skip applies.
    """
    return _CSV_SEED_PATH.read_text(encoding="utf-8")


def _english_pages() -> list[Path]:
    """Return the English documentation pages, plus the README.

    French pages carry the same code inside translated prose, so executing them
    doubles the runtime for no additional signal. ``tests/test_docs_code_samples``
    still checks both statically.
    """
    pages = sorted(DOCS_DIR.rglob("*.en.md"))
    pages.append(PROJECT_ROOT / "README.md")
    return [path for path in pages if path.is_file()]


def _blocks(path: Path) -> list[tuple[int, str]]:
    """Return ``(line_number, source)`` for each executable block in ``path``."""
    text = path.read_text(encoding="utf-8")
    if _SKIP_PAGE_MARKER in text:
        return []
    found: list[tuple[int, str]] = []
    for match in _FENCED_PYTHON.finditer(text):
        if _SKIP_MARKER in (match.group("preceding") or ""):
            continue
        # Dedent, or a block indented into a list item is a syntax error before
        # it is anything else.
        code = textwrap.dedent(match.group("code"))
        try:
            ast.parse(code)
        except SyntaxError:
            # REPL transcripts and deliberate fragments are not executable and
            # are not our business -- the static test skips them for the same
            # reason.
            continue
        line = text[: match.start("code")].count("\n") + 1
        found.append((line, code))
    return found


def _seed_sandbox(sandbox: Path, blocks: list[tuple[int, str]]) -> None:
    """Create every XML/CSV file the page's samples refer to by name."""
    import ddi_l as ddi

    names = {name for _, code in blocks for name in _FILENAME.findall(code)}
    for name in sorted(names):
        target = sandbox / name
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix == ".csv":
            # A sample that names one of the curriculum's own data files gets
            # that file, so its columns and values are the ones the reader
            # downloads.
            shipped = DOCS_DIR / "curriculum" / Path(name).name
            seed = (
                shipped.read_text(encoding="utf-8")
                if shipped.is_file()
                else _csv_seed()
            )
            target.write_text(seed, encoding="utf-8")
        elif "fragment" in name.lower():
            # A fragment is a different root element, and a sample that opens
            # one with DDIFragment.from_xml is rejected by a seeded DDIInstance
            # -- "Root element must be FragmentInstance". Seed what the name
            # says it is.
            from ddi_l.document import DDIFragment
            from ddi_l.io import write_ddi

            study = ddi.new_study(title="Seeded Study", agency="example.org")
            # A StudyUnit will not serialize without a DataCollection, so give
            # the seeded one something to hold.
            study.add_question(text="How old are you?", label="Age question")
            study.add_variable(name="Age", label="Age in years")
            fragment = DDIFragment.create()
            fragment.add_fragment(study.study_unit)
            write_ddi(fragment, target)
        else:
            # Built by the library rather than pasted in, so a seeded document
            # is always a valid instance of the current schema.
            document = ddi.new_study(title="Seeded Study", agency="example.org")
            question = document.add_question(text="How old are you?")
            document.add_variable(name="Age", question=question)
            document.save(target)


def _page_cases():
    """One case per page that has Python to run.

    A page with no Python fence is not a case at all, so it cannot show up as a
    skip and bury the skips that matter. A page that opts out with the
    skip-page marker stays a case, marked skipped, so the opt-out is visible.
    """
    for page in _english_pages():
        text = page.read_text(encoding="utf-8")
        if not _FENCED_PYTHON.search(text):
            continue
        marks = []
        if _SKIP_PAGE_MARKER in text:
            marks.append(pytest.mark.skip(reason=f"page is marked {_SKIP_PAGE_MARKER}"))
        yield pytest.param(page, marks=marks, id=str(page.relative_to(PROJECT_ROOT)))


@pytest.mark.parametrize("page", list(_page_cases()))
def test_documented_samples_execute(page: Path, tmp_path: Path) -> None:
    """Run every executable block on ``page`` in order, in a sandbox."""
    blocks = _blocks(page)
    if not blocks:
        pytest.skip(f"every Python block on the page is marked {_SKIP_MARKER}")

    _seed_sandbox(tmp_path, blocks)

    namespace: dict[str, object] = {"__name__": "__ddi_docs_sample__"}
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        for line, code in blocks:
            location = f"{page.relative_to(PROJECT_ROOT)}:{line}"
            captured = io.StringIO()
            try:
                # Samples print for the reader's benefit. That output is noise
                # on success, but it is exactly what the `# ->` claims below are
                # checked against.
                with (
                    contextlib.redirect_stdout(captured),
                    contextlib.redirect_stderr(io.StringIO()),
                ):
                    exec(compile(code, location, "exec"), namespace)
            except Exception as error:
                raise AssertionError(
                    f"documented sample at {location} raised "
                    f"{type(error).__name__}: {error}\n\n"
                    f"Fix the sample, or mark it with an HTML comment "
                    f"'<!-- {_SKIP_MARKER} -->' immediately before the fence if "
                    f"it is deliberately not runnable.\n\n{code}"
                ) from error

            printed = captured.getvalue()
            for expected in _output_claims(code):
                assert expected in printed, (
                    f"documented sample at {location} claims it prints "
                    f"{expected!r}, but it printed:\n{printed or '(nothing)'}"
                )
    finally:
        os.chdir(original_cwd)
        # `shutil` is imported for this: a sample may chdir into a directory it
        # created, and pytest cannot clean up a tree it cannot enter.
        shutil.rmtree(tmp_path, ignore_errors=True)
