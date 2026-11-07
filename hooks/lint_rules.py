"""MkDocs hook: build the lint rule reference from the rule registry.

``lint-rules.<lang>.md`` holds an introduction and the ``<!-- lint-rules -->``
marker; this hook replaces the marker with every rule
:func:`ddi_l.lint.iter_rule_metadata` reports: its severity, the profiles that
run it, its docstring and an example finding. A rule added to the registry
appears on the page without anyone editing it, and a rule's documentation
cannot drift from its code.

Rule descriptions are the docstrings, which are in English; the French page
translates the headings around them.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:  # pragma: no cover - the annotations are the only use
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page

    from ddi_l.lint import RuleInfo

MARKER = "<!-- lint-rules -->"

_PAGE = re.compile(r"(?:^|/)lint-rules(?:\.(?P<lang>[a-z]{2}))?\.md$")


class _Words(NamedTuple):
    default_heading: str
    profile_heading: str
    severity: str
    profiles: str
    default_profile: str
    example: str
    summary_rule: str
    summary_severity: str


_WORDS = {
    "en": _Words(
        "Default profile",
        "Profile `{name}`",
        "Severity:",
        "Profiles:",
        "default",
        "Example finding:",
        "Rule",
        "Severity",
    ),
    "fr": _Words(
        "Profil par défaut",
        "Profil `{name}`",
        # French puts a non-breaking space before a colon.
        "Gravité\u00a0:",
        "Profils\u00a0:",
        "par défaut",
        "Exemple de constat\u00a0:",
        "Règle",
        "Gravité",
    ),
}


def _section(info: RuleInfo, words: _Words) -> str:
    profiles = [words.default_profile] if info.default else []
    profiles += [f"`{name}`" for name in info.profiles]
    lines = [
        f"### `{info.rule_id}`",
        "",
        f"**{words.severity}** {info.severity or '—'} · "
        f"**{words.profiles}** {', '.join(profiles) or '—'}",
        "",
    ]
    prose = _prose(info.description or "")
    if prose:
        lines += [prose, ""]
    if info.example:
        lines += [f"*{words.example}*", "", "```text", info.example, "```", ""]
    return "\n".join(lines)


def render(lang: str = "en") -> str:
    """The rule reference, in ``lang`` (``en`` or ``fr``)."""
    from ddi_l.lint import COLECTICA_QUESTIONNAIRE_PROFILE, iter_rule_metadata

    words = _WORDS.get(lang, _WORDS["en"])
    infos = list(iter_rule_metadata())
    groups = [
        (words.default_heading, [info for info in infos if info.default]),
        (
            words.profile_heading.format(name=COLECTICA_QUESTIONNAIRE_PROFILE),
            [
                info
                for info in infos
                if not info.default and COLECTICA_QUESTIONNAIRE_PROFILE in info.profiles
            ],
        ),
    ]
    listed = {info.rule_id for _, members in groups for info in members}
    others = [info for info in infos if info.rule_id not in listed]
    if others:
        groups.append(("Other rules" if lang == "en" else "Autres règles", others))

    parts = []
    for heading, members in groups:
        if not members:
            continue
        table = [
            f"| {words.summary_rule} | {words.summary_severity} |",
            "| --- | --- |",
            *(
                f"| [`{info.rule_id}`](#{_anchor(info.rule_id)}) "
                f"| {info.severity or '—'} |"
                for info in members
            ),
        ]
        parts.append(f"## {heading}\n\n" + "\n".join(table) + "\n")
        parts.extend(_section(info, words) for info in members)
    return "\n".join(parts)


_SECTION = re.compile(
    r"^(Args|Arguments|Returns|Yields|Raises|Note|Notes|Example):\s*$"
)


def _prose(docstring: str) -> str:
    """A docstring without its Google-style sections (``Args:``, ``Yields:``...)."""
    kept: list[str] = []
    for line in docstring.splitlines():
        if _SECTION.match(line):
            break
        kept.append(line)
    return "\n".join(kept).strip()


def _anchor(rule_id: str) -> str:
    """The anchor Python-Markdown's toc gives a ``### `rule.id` `` heading."""
    return re.sub(r"[^\w-]", "", rule_id.lower().replace(" ", "-"))


def on_page_markdown(
    markdown: str, *, page: Page, config: MkDocsConfig, files: Files
) -> str:
    """Replace the marker on the rule reference page with the rules."""
    del files
    match = _PAGE.search(page.file.src_uri)
    if match is None or MARKER not in markdown:
        return markdown
    lang = match.group("lang") or config.theme.get("language", "en")
    return markdown.replace(MARKER, render(lang))
