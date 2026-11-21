"""The documentation site's build configuration, pinned where it is fragile.

* ``scripts/docs.py`` stages ``docs/`` for Zensical, one language at a time:
  ``page.en.md`` becomes ``page.md`` and every link to a suffixed page has to
  follow, or the built page links to nothing.

* The plugins and the two configs. Every plugin ``zensical.toml`` activates
  needs a requirement in the ``docs`` dependency group, and ``zensical.fr.toml``
  repeats the English config with French text; either one drifting fails the
  build, or splits the two sites apart, in the deploy job, after merge.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"

# This file tests the documentation site: the scripts that build it, its
# configuration and its pages. Neither `docs/` nor `zensical.toml` is shipped in
# the sdist, so from an unpacked tarball there is nothing here to exercise.
pytestmark = pytest.mark.skipif(
    not (PROJECT_ROOT / "docs").is_dir()
    or not (PROJECT_ROOT / "zensical.toml").is_file(),
    reason="docs site sources are not shipped in the sdist",
)


def _load(script_name: str):
    """Import ``scripts/<script_name>.py``, which imports its siblings."""
    path = SCRIPTS / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(f"_{script_name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


@pytest.mark.parametrize(
    ("source", "staged"),
    [
        ("[Install](installation.en.md)", "[Install](installation.md)"),
        ("[Part](../guide.fr.md#part)", "[Part](../guide.md#part)"),
        ("[Angle](<page.en.md>)", "[Angle](<page.md>)"),
        ("[ref]: curriculum/index.en.md", "[ref]: curriculum/index.md"),
        ('<a href="api.en.md#x">', '<a href="api.md#x">'),
        # Not links: a file named in prose or code keeps its suffix.
        ("Edit `index.en.md` first.", "Edit `index.en.md` first."),
        ("See docs/index.en.md on GitHub.", "See docs/index.en.md on GitHub."),
    ],
)
def test_staging_rewrites_links_to_suffixed_pages(source: str, staged: str) -> None:
    """A link to ``page.en.md`` must name ``page.md``, the file Zensical sees."""
    docs = _load("docs")

    assert docs._SUFFIXED_LINK.sub(r"\g<lead>\g<path>.md", source) == staged


def test_staging_keeps_one_language_and_drops_the_suffix(tmp_path, monkeypatch):
    docs = _load("docs")
    source = tmp_path / "docs"
    (source / "guides").mkdir(parents=True)
    (source / "overrides").mkdir()
    (source / "index.en.md").write_text("[Guide](guides/a.en.md)\n", "utf-8")
    (source / "index.fr.md").write_text("[Guide](guides/a.fr.md)\n", "utf-8")
    (source / "guides" / "a.en.md").write_text("# A\n", "utf-8")
    (source / "guides" / "a.fr.md").write_text("# A\n", "utf-8")
    (source / "logo.svg").write_text("<svg/>", "utf-8")
    (source / "overrides" / "main.html").write_text("{# theme #}", "utf-8")
    monkeypatch.setattr(docs, "DOCS", source)
    monkeypatch.setattr(docs, "STAGE", tmp_path / "stage")

    staged = docs.stage("fr")
    (source / "logo.svg").unlink()
    docs.stage("fr")

    files = sorted(p.relative_to(staged).as_posix() for p in staged.rglob("*.*"))
    assert files == ["guides/a.md", "index.md"]
    assert (staged / "index.md").read_text("utf-8") == "[Guide](guides/a.md)\n"


def _config(name: str) -> dict:
    """The ``[project]`` table of a Zensical config file."""
    with (PROJECT_ROOT / name).open("rb") as file:
        return tomllib.load(file)["project"]


# Every plugin zensical.toml activates, mapped to the distribution providing it.
# `search` is built into Zensical and so needs no separate requirement.
_PLUGIN_DISTRIBUTIONS = {
    "mkdocstrings": "mkdocstrings-python",
}


def test_every_activated_plugin_is_in_the_docs_group() -> None:
    """A plugin in zensical.toml with no requirement backing it breaks the deploy.

    Zensical fails at config time when zensical.toml names a plugin the
    ``docs`` group does not provide. uv.lock pins versions; this checks the set
    is complete.
    """
    plugins = set(_config("zensical.toml")["plugins"])
    docs_group = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())[
        "dependency-groups"
    ]["docs"]

    assert any(requirement.startswith("zensical") for requirement in docs_group)
    assert plugins - {"search"} == set(_PLUGIN_DISTRIBUTIONS), (
        "zensical.toml activates other plugins than _PLUGIN_DISTRIBUTIONS lists"
    )
    for plugin, distribution in _PLUGIN_DISTRIBUTIONS.items():
        assert any(
            requirement.startswith(distribution) for requirement in docs_group
        ), (
            f"zensical.toml activates the {plugin!r} plugin but the docs group "
            f"has no {distribution!r} requirement"
        )


def _nav_pages(nav: list) -> list[str]:
    pages: list[str] = []
    for item in nav:
        if isinstance(item, str):
            pages.append(item)
            continue
        ((_, value),) = item.items()
        pages.extend([value] if isinstance(value, str) else _nav_pages(value))
    return pages


def test_the_french_nav_lists_the_english_pages_in_order() -> None:
    """A page added to one site's nav must reach the other's, in the same place."""
    english = _nav_pages(_config("zensical.toml")["nav"])

    assert len(english) > 40
    assert _nav_pages(_config("zensical.fr.toml")["nav"]) == english


# What the French config may change: its text, and where its pages and site
# are. Everything else (theme, extensions, plugins, links) is shared.
_FRENCH_ONLY = {
    "site_description",
    "copyright",
    "site_url",
    "docs_dir",
    "site_dir",
    "nav",
    "theme.language",
    "theme.palette.toggle.name",
    "extra.announce.text",
    "extra.announce.link_label",
}


def _without_french_text(value, path: str = ""):
    """``value`` with the settings in _FRENCH_ONLY removed."""
    if isinstance(value, dict):
        return {
            key: _without_french_text(item, f"{path}{key}.")
            for key, item in value.items()
            if f"{path}{key}" not in _FRENCH_ONLY
        }
    if isinstance(value, list):
        return [_without_french_text(item, path) for item in value]
    return value


def test_the_french_config_differs_only_in_its_text() -> None:
    """zensical.fr.toml repeats zensical.toml: a change to one goes in both."""
    english = _without_french_text(_config("zensical.toml"))
    french = _without_french_text(_config("zensical.fr.toml"))

    assert french == english


def test_the_configs_point_each_language_at_its_staged_pages() -> None:
    for name, lang, prefix in (
        ("zensical.toml", "en", ""),
        ("zensical.fr.toml", "fr", "fr/"),
    ):
        config = _config(name)
        assert config["docs_dir"] == f".docs-build/{lang}"
        assert config["site_dir"] == f".docs-build/site/{lang}"
        assert config["theme"]["language"] == lang
        assert config["site_url"].endswith(f"/latest/{prefix}")


def test_every_nav_page_has_both_languages() -> None:
    for page in _nav_pages(_config("zensical.toml")["nav"]):
        for lang in ("en", "fr"):
            path = PROJECT_ROOT / "docs" / page.replace(".md", f".{lang}.md")
            assert path.is_file(), f"the nav lists {page} but {path.name} is missing"


# An admonition (``!!! note "Title"``) or collapsible block (``??? note``)
# renders as a box only when the marker is followed by a type, an optional
# quoted title, and a body indented under it. Get any of that wrong and the site
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
    extras = (
        "README.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "zensical.toml",
        "zensical.fr.toml",
    )
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


# A link to another page names its file, `installation.en.md`, not
# `installation.md`: the site maps either to the page in its language, but
# GitHub's file view only finds the file.
_PAGE_LINK = re.compile(
    r"\]\(<?(?P<a>[^)\s>#:]+\.md)[#)>\s]"
    r"|^\s{0,3}\[[^\]]+\]:\s*(?P<b>[^\s#:]+\.md)\b"
    r"|\bhref=[\"'](?P<c>[^\"'#:]+\.md)[#\"']"
)


def _missing_link_targets(path: Path) -> list[str]:
    problems: list[str] = []
    fence: str | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            fence = marker if fence is None else (None if marker == fence else fence)
            continue
        if fence is not None:
            continue
        for match in _PAGE_LINK.finditer(re.sub(r"`[^`]*`", "", line)):
            target = next(group for group in match.groups() if group)
            if not (path.parent / target).is_file():
                problems.append(f"{path.name}:{number}: {target}")
    return problems


def test_every_link_to_a_page_names_its_file() -> None:
    pages = sorted((PROJECT_ROOT / "docs").rglob("*.md"))

    problems = [p for page in pages for p in _missing_link_targets(page)]

    assert problems == []


def test_the_link_check_catches_a_link_github_cannot_follow(tmp_path) -> None:
    (tmp_path / "other.en.md").write_text("# Other\n", encoding="utf-8")
    page = tmp_path / "page.en.md"
    page.write_text(
        "[Fine](other.en.md#part) and [missing](other.md#part).\n"
        "[ref]: other.md\n"
        '<a href="other.md">raw</a>\n'
        "`[in code](other.md)` and [a site](https://example.org/x.md)\n"
        "```markdown\n[in a fence](other.md)\n```\n",
        encoding="utf-8",
    )

    problems = _missing_link_targets(page)

    assert problems == [
        "page.en.md:1: other.md",
        "page.en.md:2: other.md",
        "page.en.md:3: other.md",
    ]


# A link to a heading on the same page, `(#part)`, must also work on GitHub
# and in editors (markdownlint's MD051). They keep accents in a heading's
# anchor, `référence`, where the site drops them, `reference`; the site build
# checks its own anchors. A heading can give both the same anchor with `{#id}`.
_SAME_PAGE_LINK = re.compile(r"\]\(#(?P<fragment>[^)\s]+)\)")
_HEADING = re.compile(r"^#{1,6}\s+(?P<text>.*?)\s*(?:\{#(?P<id>[^}\s]+)\})?\s*$")


def _github_anchor(text: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def _broken_fragments(path: Path) -> list[str]:
    anchors: set[str] = set()
    links: list[tuple[int, str]] = []
    fence: str | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            fence = marker if fence is None else (None if marker == fence else fence)
            continue
        if fence is not None:
            continue
        heading = _HEADING.match(line)
        if heading:
            anchor = heading["id"] or _github_anchor(heading["text"])
            suffix = 0
            while (f"{anchor}-{suffix}" if suffix else anchor) in anchors:
                suffix += 1
            anchors.add(f"{anchor}-{suffix}" if suffix else anchor)
        for match in _SAME_PAGE_LINK.finditer(re.sub(r"`[^`]*`", "", line)):
            links.append((number, match["fragment"]))
    return [f"{path.name}:{n}: #{f}" for n, f in links if f not in anchors]


def test_every_same_page_link_finds_its_heading_on_github() -> None:
    pages = sorted((PROJECT_ROOT / "docs").rglob("*.md"))

    problems = [p for page in pages for p in _broken_fragments(page)]

    assert problems == []


def test_the_fragment_check_reads_anchors_as_github_does(tmp_path) -> None:
    page = tmp_path / "page.fr.md"
    page.write_text(
        "## Garder chaque référence à jour\n"
        "## Charger des données {#charger-des-donnees}\n"
        "## Notes\n## Notes\n"
        "```markdown\n## In a fence\n```\n"
        "[a](#garder-chaque-reference-a-jour) [b](#garder-chaque-référence-à-jour)\n"
        "[c](#charger-des-donnees) [d](#notes-1) [e](#in-a-fence)\n",
        encoding="utf-8",
    )

    problems = _broken_fragments(page)

    assert problems == [
        "page.fr.md:8: #garder-chaque-reference-a-jour",
        "page.fr.md:9: #in-a-fence",
    ]


# The curriculum's answer-key page is generated from the modules by
# scripts/docs_answer_keys.py, so the answers under each exercise are the
# only copy.


def _curriculum_modules(lang: str) -> list[Path]:
    return sorted((PROJECT_ROOT / "docs" / "curriculum").glob(f"module-*.{lang}.md"))


@pytest.mark.parametrize("lang", ["en", "fr"])
def test_the_answer_key_page_collects_every_module_answer(lang: str) -> None:
    hook = _load("docs_answer_keys")
    rendered = hook.render(PROJECT_ROOT / "docs" / "curriculum", lang)

    modules = _curriculum_modules(lang)
    answers = sum(
        page.read_text(encoding="utf-8").count("??? success") for page in modules
    )
    exercise_word = {"en": "Exercise", "fr": "Exercice"}[lang]
    exercises = len(re.findall(rf"(?m)^\*\*{exercise_word} \d+\*\*$", rendered))
    loose = len(re.findall(r"(?m)^\*\*[^*\n]+: [^*\n]+\*\*$", rendered)) - len(
        re.findall(r"(?m)^\*\*(Question|Q)\s?\d+", rendered)
    )
    questions = sum(
        page.read_text(encoding="utf-8").count("???+ question") for page in modules
    )

    assert rendered.count("](module-") == len(modules)
    assert len(re.findall(r"(?m)^\*\*(Question|Q)\s?\d+", rendered)) == questions
    # Every success block is either a quiz answer or an exercise/solution entry.
    assert exercises + loose + questions == answers


def test_the_answer_key_pages_carry_the_marker() -> None:
    hook = _load("docs_answer_keys")
    for lang in ("en", "fr"):
        page = PROJECT_ROOT / "docs" / "curriculum" / f"answer-keys.{lang}.md"
        text = page.read_text(encoding="utf-8")
        assert hook.MARKER in text, f"{page.name} lost the {hook.MARKER} marker"
        assert "```" not in text, f"{page.name} should hold no answers of its own"


def test_english_and_french_modules_have_the_same_answers() -> None:
    """A translated module must offer an answer wherever the English one does."""
    for english in _curriculum_modules("en"):
        french = english.with_name(english.name.replace(".en.md", ".fr.md"))
        en_text = english.read_text(encoding="utf-8")
        fr_text = french.read_text(encoding="utf-8")
        assert en_text.count("??? success") == fr_text.count("??? success"), (
            english.name
        )
        assert en_text.count("???+ question") == fr_text.count("???+ question"), (
            english.name
        )
