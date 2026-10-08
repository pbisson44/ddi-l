"""The documentation site's build configuration, pinned where it is fragile.

* ``hooks/version_selector.py`` -- the theme resolves the version manifest as
  ``new URL("../versions.json", base)``, which is right under ``mike``
  (``/ddi-l/latest/``) but overshoots on a plain local build (``/ddi-l/``).

* ``hooks/quiet_i18n_logs.py`` -- a logging filter narrow enough that it must
  be shown to drop only the config echoes, never a warning.

* The plugin and hook sets. Every plugin ``mkdocs.yml`` activates needs a
  requirement in the ``docs`` dependency group, and every configured hook path
  has to resolve; either one missing fails ``mkdocs build`` at config time, in
  the deploy job, after merge.
"""

from __future__ import annotations

import importlib.util
import io
import logging
import re
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# This file tests the documentation site: the MkDocs hooks and the version caps
# in pyproject.toml. Neither `hooks/` nor `mkdocs.yml` is shipped in the sdist,
# so from an unpacked tarball there is nothing here to exercise.
pytestmark = pytest.mark.skipif(
    not (PROJECT_ROOT / "hooks").is_dir()
    or not (PROJECT_ROOT / "mkdocs.yml").is_file(),
    reason="docs site sources are not shipped in the sdist",
)


def _load(hook_name: str):
    path = PROJECT_ROOT / "hooks" / f"{hook_name}.py"
    spec = importlib.util.spec_from_file_location(f"_{hook_name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_hook():
    return _load("version_selector")


@pytest.fixture
def mkdocs_logging():
    """Stand in for mkdocs' own logging setup: one stderr handler at INFO."""
    logger = logging.getLogger("mkdocs")
    saved_handlers, saved_level = logger.handlers, logger.level

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    try:
        yield logger, handler, stream
    finally:
        logger.handlers, logger.level = saved_handlers, saved_level


def test_the_version_selector_is_dropped_outside_a_mike_build(monkeypatch):
    """No ``mike`` in the environment means no ``versions.json`` request."""
    monkeypatch.delenv("MIKE_DOCS_VERSION", raising=False)
    config = {"extra": {"version": {"provider": "mike"}, "generator": False}}

    result = _load_hook().on_config(config)

    assert "version" not in result["extra"]
    assert result["extra"]["generator"] is False, "unrelated keys must survive"


def test_the_version_selector_survives_a_mike_build(monkeypatch):
    """``mike`` sets ``MIKE_DOCS_VERSION``; the selector must reach production."""
    monkeypatch.setenv("MIKE_DOCS_VERSION", "latest")
    config = {"extra": {"version": {"provider": "mike"}}}

    result = _load_hook().on_config(config)

    assert result["extra"]["version"] == {"provider": "mike"}


def test_the_hook_mutates_extra_rather_than_replacing_it(monkeypatch):
    """mkdocs-static-i18n sets attributes on ``extra`` that templates read.

    Swapping in a replacement mapping drops them, and the build fails with
    ``'dict' object has no attribute 'alternate'``.
    """
    monkeypatch.delenv("MIKE_DOCS_VERSION", raising=False)

    class ExtraWithAttributes(dict):
        alternate = ("en", "fr")

    extra = ExtraWithAttributes(version={"provider": "mike"})
    config = {"extra": extra}

    result = _load_hook().on_config(config)

    assert result["extra"] is extra
    assert result["extra"].alternate == ("en", "fr")


# Every plugin mkdocs.yml activates, mapped to the distribution providing it.
# `search` ships inside mkdocs itself and so needs no separate requirement.
_PLUGIN_DISTRIBUTIONS = {
    "mike": "mike",
    "i18n": "mkdocs-static-i18n",
}


def test_every_activated_plugin_is_in_the_docs_group() -> None:
    """A plugin in mkdocs.yml with no requirement backing it breaks the deploy.

    ``mkdocs build`` fails at config time when mkdocs.yml names a plugin the
    ``docs`` group does not provide. uv.lock pins versions; this checks the set
    is complete.
    """
    config = (PROJECT_ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    docs_group = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())[
        "dependency-groups"
    ]["docs"]

    for plugin, distribution in _PLUGIN_DISTRIBUTIONS.items():
        assert f"\n  - {plugin}:" in config, (
            f"{plugin} is no longer activated in mkdocs.yml; drop it from "
            "_PLUGIN_DISTRIBUTIONS too"
        )
        assert any(
            requirement.startswith(distribution) for requirement in docs_group
        ), (
            f"mkdocs.yml activates the {plugin!r} plugin but the docs group has "
            f"no {distribution!r} requirement"
        )


def test_every_configured_hook_exists() -> None:
    """A hook path that does not resolve fails the build at config time."""
    config = (PROJECT_ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    hooks = [
        line.strip().removeprefix("- ")
        for line in config.splitlines()
        if line.startswith("  - hooks/")
    ]

    assert hooks, "expected mkdocs.yml to configure hooks"
    for hook in hooks:
        assert (PROJECT_ROOT / hook).is_file(), f"missing hook file: {hook}"


def _i18n_log(level: int, message: str) -> None:
    logging.getLogger("mkdocs.plugins.mkdocs_static_i18n.reconfigure").log(
        level, message
    )


def test_the_i18n_config_dumps_are_dropped(mkdocs_logging):
    """The per-language `nav`/`extra` echoes are several KB and say nothing.

    mkdocs-static-i18n logs the entire value it overrides each config key with,
    once per language, on every rebuild -- burying the build result and any
    warning under the whole navigation tree printed twice.
    """
    _, _, stream = mkdocs_logging
    _load("quiet_i18n_logs").on_startup(command="build", dirty=False)

    _i18n_log(logging.INFO, "Overriding 'en' config 'nav' with '[...]'")
    _i18n_log(logging.INFO, "Updating 'fr' config 'extra' with '{...}'")

    assert stream.getvalue() == ""


def test_the_useful_i18n_lines_survive(mkdocs_logging):
    """Only the config echoes go. A warning must never be swallowed."""
    _, _, stream = mkdocs_logging
    _load("quiet_i18n_logs").on_startup(command="build", dirty=False)

    _i18n_log(logging.INFO, "Building 'en' documentation to directory: /site")
    _i18n_log(logging.WARNING, "Unknown 'en' config override 'bogus'")
    logging.getLogger("mkdocs.commands.build").info(
        "Documentation built in 3.00 seconds"
    )

    emitted = stream.getvalue()
    assert "Building 'en' documentation" in emitted
    assert "Unknown 'en' config override" in emitted
    assert "Documentation built" in emitted


def test_the_filter_is_installed_once_across_rebuilds(mkdocs_logging):
    """``mkdocs serve`` re-enters the hook on every rebuild."""
    _, handler, _ = mkdocs_logging
    hook = _load("quiet_i18n_logs")

    for _ in range(3):
        hook.on_startup(command="serve", dirty=False)

    assert len(handler.filters) == 1


def test_verbose_keeps_every_line(mkdocs_logging):
    """``mkdocs --verbose`` means someone asked for the noise."""
    logger, _, stream = mkdocs_logging
    logger.setLevel(logging.DEBUG)

    _load("quiet_i18n_logs").on_startup(command="build", dirty=False)
    _i18n_log(logging.INFO, "Overriding 'en' config 'nav' with '[...]'")

    assert "Overriding 'en' config 'nav'" in stream.getvalue()


# An admonition (``!!! note "Title"``) or collapsible block (``??? note``)
# renders as a box only when the marker is followed by a type, an optional
# quoted title, and a body indented under it. Get any of that wrong and MkDocs
# prints the marker as a paragraph of text instead, without a build warning.
_ADMONITION_MARKER = re.compile(r"^(?P<indent>[ ]*)(?:!!!|\?\?\?\+?)(?P<rest>.*)$")
_WELL_FORMED_REST = re.compile(r'^ [a-z][\w-]*(?: [\w-]+)*(?: "[^"]*")?$')


def _admonition_problems(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    problems: list[str] = []
    fence: str | None = None
    for number, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is not None:
            continue
        match = _ADMONITION_MARKER.match(line)
        if match is None:
            continue
        if not _WELL_FORMED_REST.match(match.group("rest")):
            problems.append(f"{path.name}:{number}: malformed marker {line.strip()!r}")
            continue
        body = next((later for later in lines[number:] if later.strip()), "")
        if len(body) - len(body.lstrip(" ")) < len(match.group("indent")) + 4:
            problems.append(f"{path.name}:{number}: body is not indented 4 spaces")
    return problems


def test_every_admonition_is_well_formed() -> None:
    """Each ``!!!`` / ``???`` block in docs/ renders as a box, not literal text."""
    pages = sorted((PROJECT_ROOT / "docs").rglob("*.md"))
    assert pages, "no documentation pages found"

    problems = [problem for page in pages for problem in _admonition_problems(page)]

    assert problems == []


def test_the_admonition_check_catches_the_usual_mistakes(tmp_path) -> None:
    page = tmp_path / "page.md"
    page.write_text(
        '!!! info "Fine"\n    Body.\n\n'
        "!!!note\n    No space.\n\n"
        '!!! warning "Flush body"\nNot indented.\n\n'
        "```text\n!!! inside a fence is ignored\n```\n",
        encoding="utf-8",
    )

    problems = _admonition_problems(page)

    assert [problem.split(": ", 1)[0] for problem in problems] == [
        "page.md:4",
        "page.md:7",
    ]


# The documentation uses no em dashes: not the character, and not the `---` /
# `--` spellings a Markdown "smarty" extension would turn into one. Hyphenated
# words, CLI flags (`--strict`), rules (`---` alone on a line) and table
# separators are not dashes and are allowed.
_DASH_PUNCTUATION = re.compile(r"(?<=\s)---?(?=\s)|(?<=\s)---?$")


def _documentation_files() -> list[Path]:
    pages = sorted((PROJECT_ROOT / "docs").rglob("*.md"))
    extras = ("README.md", "CONTRIBUTING.md", "SECURITY.md", "mkdocs.yml")
    return pages + [PROJECT_ROOT / name for name in extras]


def _em_dash_problems(path: Path) -> list[str]:
    problems: list[str] = []
    fence: str | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        where = f"{path.name}:{number}"
        if "—" in line or "&mdash;" in line:
            problems.append(f"{where}: em dash")
            continue
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            fence = marker if fence is None else (None if marker == fence else fence)
            continue
        if fence is not None or re.fullmatch(r"[-|:\s]*", stripped):
            continue
        prose = re.sub(r"`[^`]*`|<!--[\s\S]*?-->", "", line)
        if _DASH_PUNCTUATION.search(prose):
            problems.append(f"{where}: dash used as punctuation")
    return problems


def test_the_documentation_has_no_em_dashes() -> None:
    problems = [p for path in _documentation_files() for p in _em_dash_problems(path)]

    assert problems == []


def test_the_em_dash_check_catches_each_spelling(tmp_path) -> None:
    page = tmp_path / "page.md"
    page.write_text(
        "A sentence — with the character.\n"
        "A sentence --- with three hyphens.\n"
        "A sentence -- with two.\n"
        "Fine: `ddi validate --strict`, a well-known word, and --flags.\n"
        "<!-- docs-test: skip -- an HTML comment is fine -->\n"
        "---\n"
        "| a | b |\n| --- | --- |\n"
        '```bash\necho "--- $f ---"\n```\n',
        encoding="utf-8",
    )

    problems = _em_dash_problems(page)

    assert [problem.split(": ", 1)[0] for problem in problems] == [
        "page.md:1",
        "page.md:2",
        "page.md:3",
    ]
