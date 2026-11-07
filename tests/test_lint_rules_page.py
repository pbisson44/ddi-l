"""The lint rule reference page is generated from the rule registry.

``hooks/lint_rules.py`` replaces the marker on ``lint-rules.<lang>.md`` with
every registered rule, so the page cannot omit a rule or drift from its code.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from ddi_l.lint import iter_rule_metadata

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS = PROJECT_ROOT / "docs"
HOOK = PROJECT_ROOT / "hooks" / "lint_rules.py"

pytestmark = pytest.mark.skipif(
    not DOCS.is_dir() or not HOOK.is_file(), reason="docs/ is not shipped in the sdist"
)


def _hook():
    spec = importlib.util.spec_from_file_location("lint_rules_hook", HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("lang", ["en", "fr"])
def test_the_page_lists_every_registered_rule(lang: str) -> None:
    rendered = _hook().render(lang)
    for info in iter_rule_metadata():
        assert f"### `{info.rule_id}`" in rendered, info.rule_id
        if info.example:
            assert info.example in rendered
    # Docstring sections are left out: they document the callback, not the rule.
    assert "Yields:" not in rendered
    assert "Args:" not in rendered


def test_the_french_page_uses_french_typography() -> None:
    rendered = _hook().render("fr")
    nbsp = chr(0xA0)  # a non-breaking space comes before a French colon
    assert f"**Gravité{nbsp}:**" in rendered
    assert f"*Exemple de constat{nbsp}:*" in rendered


def test_both_pages_carry_the_marker() -> None:
    hook = _hook()
    for lang in ("en", "fr"):
        text = (DOCS / f"lint-rules.{lang}.md").read_text(encoding="utf-8")
        assert hook.MARKER in text


def test_the_hook_only_touches_its_page() -> None:
    hook = _hook()

    class _File:
        def __init__(self, src_uri: str) -> None:
            self.src_uri = src_uri

    class _Page:
        def __init__(self, src_uri: str) -> None:
            self.file = _File(src_uri)

    class _Config:
        theme = {"language": "en"}

    markdown = f"intro\n\n{hook.MARKER}\n"
    other = hook.on_page_markdown(
        markdown, page=_Page("validation.en.md"), config=_Config(), files=None
    )
    assert other == markdown
    page = hook.on_page_markdown(
        markdown, page=_Page("lint-rules.fr.md"), config=_Config(), files=None
    )
    assert hook.MARKER not in page
    assert "Profil par défaut" in page
