"""MkDocs hook: build the curriculum answer-key page from the modules.

Each module carries its own answers: a collapsible ``??? success "Answer"``
under every exercise and quiz question, which is what a self-paced learner
wants. Instructors also want every answer on one page. Keeping a second,
hand-written copy is how the old answer-key page drifted: it named files the
exercises never created and quiz letters the modules no longer used.

So the page is generated. ``curriculum/answer-keys.<lang>.md`` holds an
introduction and the ``<!-- answer-keys -->`` marker; this hook replaces the
marker with the answers it finds in ``curriculum/module-*.<lang>.md``:

* every ``??? success`` block in a module's exercises section, labelled with
  the exercise it follows (a ``**Exercise N.**`` paragraph, or the ``N.`` list
  item when the section uses a numbered list);
* every quiz question (``???+ question "..."``) with the answer nested in it;
* any ``??? success`` block elsewhere on a page without an exercises section
  (the capstone's sample solutions), labelled with the heading above it.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:  # pragma: no cover - the annotations are the only use
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page

MARKER = "<!-- answer-keys -->"

_PAGE = re.compile(r"(?:^|/)curriculum/answer-keys(?:\.(?P<lang>[a-z]{2}))?\.md$")
_MODULE = re.compile(r"^module-(?P<number>\d+)-[\w-]+$")


class _Words(NamedTuple):
    exercises_heading: str
    exercises: str
    exercise: str
    quiz: str
    no_answers: str


_WORDS = {
    "en": _Words("Exercises", "Exercises", "Exercise", "Quiz", "No answers."),
    "fr": _Words("Exercices", "Exercices", "Exercice", "Quiz", "Aucune réponse."),
}

_SUCCESS = re.compile(r'^(?P<indent>[ ]*)\?\?\?\+? success "(?P<title>[^"]*)"\s*$')
_QUESTION = re.compile(r'^(?P<indent>[ ]*)\?\?\?\+? question "(?P<title>[^"]*)"\s*$')
_HEADING = re.compile(r"^(?P<hashes>#{1,6}) (?P<text>.+?)\s*$")
_FENCE = re.compile(r"^[ ]*(```|~~~)")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _block(lines: list[str], start: int) -> tuple[str, int]:
    """Return the dedented body of the admonition opened at ``start``.

    The body is every following line that is blank or indented deeper than the
    marker; the second value is the index just past it.
    """
    depth = _indent(lines[start]) + 4
    end = start + 1
    while end < len(lines) and (not lines[end].strip() or _indent(lines[end]) >= depth):
        end += 1
    body = [line[depth:] if line.strip() else "" for line in lines[start + 1 : end]]
    while body and not body[-1]:
        body.pop()
    return "\n".join(body), end


def _sections(lines: list[str]) -> list[tuple[str, int, int]]:
    """Return ``(heading text, first line, end line)`` for each ``##`` section."""
    starts: list[tuple[str, int]] = []
    fenced = False
    for number, line in enumerate(lines):
        if _FENCE.match(line):
            fenced = not fenced
            continue
        match = _HEADING.match(line)
        if not fenced and match and len(match.group("hashes")) == 2:
            starts.append((match.group("text"), number))
    ends = [start for _, start in starts[1:]] + [len(lines)]
    return [(text, start, end) for (text, start), end in zip(starts, ends, strict=True)]


def _exercise_answers(lines: list[str], words: _Words) -> list[tuple[str, str]]:
    bold = re.compile(rf"^\*\*{words.exercise} (\d+)\b")
    numbered = re.compile(r"^(\d+)\. ")
    uses_bold = any(bold.match(line) for line in lines)
    label = words.exercise
    answers: list[tuple[str, str]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        marker = bold.match(line) if uses_bold else numbered.match(line)
        if marker:
            label = f"{words.exercise} {marker.group(1)}"
        if _SUCCESS.match(line):
            body, index = _block(lines, index)
            answers.append((label, body))
            continue
        index += 1
    return answers


def _quiz_answers(lines: list[str]) -> list[tuple[str, str]]:
    answers: list[tuple[str, str]] = []
    index = 0
    while index < len(lines):
        question = _QUESTION.match(lines[index])
        if question is None:
            index += 1
            continue
        body, end = _block(lines, index)
        inner = body.splitlines()
        answer = next(
            (
                _block(inner, i)[0]
                for i, line in enumerate(inner)
                if _SUCCESS.match(line)
            ),
            "",
        )
        answers.append((question.group("title"), answer))
        index = end
    return answers


def _loose_answers(lines: list[str]) -> list[tuple[str, str]]:
    """Answers outside an exercises section, labelled by the heading above."""
    answers: list[tuple[str, str]] = []
    heading = ""
    fenced = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if _FENCE.match(line):
            fenced = not fenced
        match = _HEADING.match(line)
        if not fenced and match and len(match.group("hashes")) == 2:
            heading = match.group("text")
        success = _SUCCESS.match(line)
        if success and not fenced:
            body, index = _block(lines, index)
            answers.append((f"{heading}: {success.group('title')}", body))
            continue
        index += 1
    return answers


def _module_entry(path: Path, words: _Words) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = next(
        (
            m.group("text")
            for line in lines
            if (m := _HEADING.match(line)) and m.group("hashes") == "#"
        ),
        path.stem,
    )
    link = path.name.rsplit(".", 2)[0] + ".md"
    out = [f"## [{title}]({link})", ""]

    sections = _sections(lines)
    exercises = [s for s in sections if s[0] == words.exercises_heading]
    quiz = [s for s in sections if s[0] == words.quiz]

    if exercises:
        _, start, end = exercises[0]
        found = _exercise_answers(lines[start:end], words)
        heading = f"### {words.exercises}"
    else:
        found = _loose_answers(lines)
        heading = ""
    if found:
        if heading:
            out += [heading, ""]
        for label, body in found:
            out += [f"**{label}**", "", body, ""]

    if quiz:
        _, start, end = quiz[0]
        questions = _quiz_answers(lines[start:end])
        if questions:
            out += [f"### {words.quiz}", ""]
            for label, body in questions:
                out += [f"**{label}**", "", body or words.no_answers, ""]

    return "\n".join(out)


def render(curriculum_dir: Path, lang: str) -> str:
    """Return the generated answer-key Markdown for one language."""
    words = _WORDS.get(lang, _WORDS["en"])
    modules = []
    for path in curriculum_dir.glob(f"module-*.{lang}.md"):
        match = _MODULE.match(path.name.rsplit(".", 2)[0])
        if match:
            modules.append((int(match.group("number")), path))
    entries = [_module_entry(path, words) for _, path in sorted(modules)]
    return "\n\n---\n\n".join(entries) + "\n"


def on_page_markdown(
    markdown: str, *, page: Page, config: MkDocsConfig, files: Files
) -> str:
    """Replace the marker on the answer-key page with the generated answers."""
    del files
    match = _PAGE.search(page.file.src_uri)
    if match is None or MARKER not in markdown:
        return markdown
    lang = match.group("lang") or config.theme.get("language", "en")
    curriculum_dir = Path(config.docs_dir) / "curriculum"
    return markdown.replace(MARKER, render(curriculum_dir, lang))
