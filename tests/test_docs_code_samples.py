"""Documented ``ddi_l`` usage must match the real package.

Two static checks run over every fenced ``python`` block:

* every ``from ddi_l... import ...`` resolves against the installed package;
* every call to a directly-imported ``ddi_l`` callable binds against that
  callable's real signature.

``tests/test_docs_execution.py`` executes the samples; these checks also
cover reference pages whose samples use placeholder names.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import re
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"

# `docs/` is not shipped in the sdist. Without this guard `_markdown_files()`
# returns just README.md and the suite reports a handful of passing tests that
# checked almost nothing -- a silent hole rather than an honest skip.
pytestmark = pytest.mark.skipif(
    not DOCS_DIR.is_dir(), reason="docs/ is not shipped in the sdist"
)

# The indent group matters: a block nested in a numbered step is still a
# sample, and anchoring the fence to column 0 hid dozens of them across the
# tutorials. The closing fence must match the opening indent so a more deeply
# nested fence cannot end an outer block early.
_FENCED_PYTHON = re.compile(
    r"^(?P<indent>[ \t]*)```(?:python|py)\n(?P<code>.*?)^(?P=indent)```",
    re.MULTILINE | re.DOTALL,
)


def _markdown_files() -> list[Path]:
    files = sorted(DOCS_DIR.rglob("*.md"))
    files.append(PROJECT_ROOT / "README.md")
    return [path for path in files if path.is_file()]


def _iter_ddi_imports(path: Path):
    """Yield (line_number, module, imported_name) for every ddi_l import."""
    text = path.read_text(encoding="utf-8")
    for match in _FENCED_PYTHON.finditer(text):
        block = textwrap.dedent(match.group("code"))
        block_start = text[: match.start()].count("\n") + 2
        try:
            tree = ast.parse(block)
        except SyntaxError:
            # Deliberate fragments and REPL transcripts are not our business.
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.module is None:
                continue
            if not node.module.startswith("ddi_l"):
                continue
            for alias in node.names:
                yield block_start + node.lineno - 1, node.module, alias.name


def _is_importable_submodule(module_name: str, symbol: str) -> bool:
    """Return whether ``from module_name import symbol`` resolves a submodule.

    ``hasattr`` alone is not what ``from X import Y`` does. When ``Y`` is a
    submodule that ``X/__init__.py`` does not itself import, the attribute is
    absent until the import machinery creates it -- so ``from ddi_l import
    examples`` works while ``hasattr(ddi_l, "examples")`` is False. Checking the
    attribute only would report a working documented import as broken.
    """
    try:
        importlib.import_module(f"{module_name}.{symbol}")
    except ImportError:
        return False
    return True


@pytest.mark.parametrize(
    "markdown_path", _markdown_files(), ids=lambda p: str(p.relative_to(PROJECT_ROOT))
)
def test_documented_imports_resolve(markdown_path: Path) -> None:
    """Every documented ``from ddi_l... import X`` names something real."""
    failures: list[str] = []

    for line, module_name, symbol in _iter_ddi_imports(markdown_path):
        try:
            module = importlib.import_module(module_name)
        except ImportError as error:
            failures.append(f"  line {line}: cannot import {module_name!r} ({error})")
            continue
        if not hasattr(module, symbol) and not _is_importable_submodule(
            module_name, symbol
        ):
            failures.append(f"  line {line}: {module_name} has no {symbol!r}")

    assert not failures, (
        f"{markdown_path.relative_to(PROJECT_ROOT)} documents imports that do not "
        "resolve:\n" + "\n".join(failures)
    )


class _Placeholder:
    """Stands in for an argument value we cannot evaluate statically."""


def _iter_ddi_calls(path: Path):
    """Yield (line, dotted_name, call_node) for calls to imported ddi_l names.

    Only names bound by a ``from ddi_l... import X`` *in the same block* are
    considered. Anything reached through an attribute on a runtime object
    (``doc.save(...)``) cannot be resolved without executing the sample, so it
    is skipped rather than guessed at.
    """
    text = path.read_text(encoding="utf-8")
    for match in _FENCED_PYTHON.finditer(text):
        block = textwrap.dedent(match.group("code"))
        block_start = text[: match.start()].count("\n") + 2
        try:
            tree = ast.parse(block)
        except SyntaxError:
            continue

        bound: dict[str, tuple[str, str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                "ddi_l"
            ):
                for alias in node.names:
                    bound[alias.asname or alias.name] = (node.module or "", alias.name)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            target = bound.get(node.func.id)
            if target is not None:
                yield block_start + node.lineno - 1, target, node


@pytest.mark.parametrize(
    "markdown_path", _markdown_files(), ids=lambda p: str(p.relative_to(PROJECT_ROOT))
)
def test_documented_calls_bind_to_real_signatures(markdown_path: Path) -> None:
    """Every documented call to an imported ``ddi_l`` callable is arity-correct."""
    failures: list[str] = []

    for line, (module_name, symbol), call in _iter_ddi_calls(markdown_path):
        try:
            obj = getattr(importlib.import_module(module_name), symbol)
        except (ImportError, AttributeError):
            continue  # already reported by test_documented_imports_resolve
        if not callable(obj):
            continue
        try:
            signature = inspect.signature(obj)
        except (TypeError, ValueError):
            continue  # builtins and C extensions have no introspectable signature

        # ``*args``/``**kwargs`` in the sample make the real arity unknowable.
        if any(isinstance(a, ast.Starred) for a in call.args):
            continue
        if any(kw.arg is None for kw in call.keywords):
            continue

        args = [_Placeholder()] * len(call.args)
        kwargs = {kw.arg: _Placeholder() for kw in call.keywords if kw.arg}
        try:
            signature.bind(*args, **kwargs)
        except TypeError as error:
            failures.append(
                f"  line {line}: {symbol}{signature} rejects this call ({error})"
            )

    assert not failures, (
        f"{markdown_path.relative_to(PROJECT_ROOT)} documents calls that would raise "
        "TypeError:\n" + "\n".join(failures)
    )


def test_the_call_scanner_actually_finds_calls() -> None:
    """Guard against the call scan silently matching nothing and passing vacuously."""
    total = sum(len(list(_iter_ddi_calls(path))) for path in _markdown_files())

    assert total > 50, (
        f"Expected the docs to call ddi_l callables widely, found {total}"
    )


def test_the_scanner_actually_finds_imports() -> None:
    """Guard against the scan silently matching nothing and passing vacuously."""
    total = sum(len(list(_iter_ddi_imports(path))) for path in _markdown_files())

    assert total > 100, f"Expected the docs to import from ddi_l widely, found {total}"
