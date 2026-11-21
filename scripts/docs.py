"""Build and preview the bilingual documentation site with Zensical.

Every page under ``docs/`` exists twice, ``page.en.md`` and ``page.fr.md``.
Zensical builds one language per run and has no build hooks, so
this script stages each language before Zensical sees it:

* the pages of that language lose their suffix (``index.en.md`` becomes
  ``index.md``), and links to suffixed pages are rewritten to match;
* every other file (styles, images, downloads) is copied as it is;
* the answer-key and lint-rule pages are generated where their markers are.

``zensical.toml`` configures the English site and ``zensical.fr.toml`` the
French one. ``build`` writes both into ``site/``, English at the root
and French under ``fr/``; ``serve`` previews one language and stages again
whenever a file under ``docs/`` changes.

    uv run python scripts/docs.py build --strict
    uv run python scripts/docs.py serve            # English
    uv run python scripts/docs.py serve --lang fr  # French
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import docs_answer_keys
import docs_lint_rules

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
STAGE = ROOT / ".docs-build"
SITE = ROOT / "site"

# Each language: its Zensical config, and where its site goes under site/.
LANGUAGES = {"en": ("zensical.toml", ""), "fr": ("zensical.fr.toml", "fr")}

# docs/overrides is the theme's custom_dir, read in place; it is not a page.
_NOT_STAGED = {"overrides"}

# A link to a suffixed page, in Markdown (`](page.en.md#part)`, `]: page.en.md`)
# or in raw HTML (`href="page.en.md"`). Only links are rewritten: a file name
# quoted in prose or code keeps its suffix.
_SUFFIXED_LINK = re.compile(
    r"(?P<lead>\]\(\s*<?|\]:\s*|(?:href|src)=\")"
    r"(?P<path>[^\s()<>\"#]*?)\.(?:en|fr)\.md(?=[#)\s>\"]|$)"
)


def _page_text(source: Path, lang: str) -> str:
    """The staged text of one page: generated parts filled, links rewritten."""
    text = source.read_text(encoding="utf-8")
    if docs_answer_keys.MARKER in text:
        text = text.replace(
            docs_answer_keys.MARKER, docs_answer_keys.render(source.parent, lang)
        )
    if docs_lint_rules.MARKER in text:
        text = text.replace(docs_lint_rules.MARKER, docs_lint_rules.render(lang))
    return _SUFFIXED_LINK.sub(r"\g<lead>\g<path>.md", text)


def _write(path: Path, data: bytes) -> None:
    """Write ``data`` unless the file already holds it.

    A preview then rebuilds only the pages that changed.
    """
    if path.is_file() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def stage(lang: str) -> Path:
    """Stage ``docs/`` for one language; return the staged folder."""
    target = STAGE / lang
    others = tuple(f".{other}.md" for other in LANGUAGES if other != lang)
    own = f".{lang}.md"
    wanted: set[Path] = set()
    for source in sorted(DOCS.rglob("*")):
        relative = source.relative_to(DOCS)
        if source.is_dir() or relative.parts[0] in _NOT_STAGED:
            continue
        if source.name.endswith(others):
            continue
        if source.name.endswith(own):
            staged = relative.with_name(source.name[: -len(own)] + ".md")
            data = _page_text(source, lang).encode("utf-8")
        else:
            staged = relative
            data = source.read_bytes()
        wanted.add(staged)
        _write(target / staged, data)
    # A page deleted or renamed in docs/ goes from the staged copy too.
    if target.is_dir():
        for path in sorted(target.rglob("*"), reverse=True):
            relative = path.relative_to(target)
            if path.is_file() and relative not in wanted:
                path.unlink()
            elif path.is_dir() and not any(path.iterdir()):
                path.rmdir()
    return target


def _zensical(command: str, lang: str, *options: str) -> subprocess.Popen[bytes]:
    config = ROOT / LANGUAGES[lang][0]
    return subprocess.Popen(
        [sys.executable, "-m", "zensical", command, "-f", str(config), *options],
        cwd=ROOT,
    )


def build(strict: bool) -> int:
    """Build every language and assemble ``site/``; return the exit status."""
    options = ["--clean", *(["--strict"] if strict else [])]
    for lang in LANGUAGES:
        stage(lang)
        status = _zensical("build", lang, *options).wait()
        if status:
            print(f"docs: the {lang} build failed", file=sys.stderr)
            return status
    if SITE.exists():
        shutil.rmtree(SITE)
    for lang, (_, prefix) in LANGUAGES.items():
        shutil.copytree(STAGE / "site" / lang, SITE / prefix, dirs_exist_ok=True)
    print(f"docs: wrote {SITE.relative_to(ROOT)}/ ({', '.join(LANGUAGES)})")
    return 0


def _snapshot() -> dict[Path, int]:
    return {path: path.stat().st_mtime_ns for path in DOCS.rglob("*") if path.is_file()}


def serve(lang: str, address: str | None) -> int:
    """Preview one language, staging again when a file under docs/ changes."""
    stage(lang)
    server = _zensical("serve", lang, *(["--dev-addr", address] if address else []))
    seen = _snapshot()
    try:
        while server.poll() is None:
            time.sleep(1)
            now = _snapshot()
            if now != seen:
                seen = now
                stage(lang)
    except KeyboardInterrupt:
        pass
    finally:
        server.terminate()
        server.wait()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface; return the exit status."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    built = commands.add_parser("build", help="build every language into site/")
    built.add_argument("--strict", action="store_true", help="fail on warnings")
    served = commands.add_parser("serve", help="preview one language")
    served.add_argument("--lang", choices=sorted(LANGUAGES), default="en")
    served.add_argument("--dev-addr", help="address to serve on, as IP:PORT")
    staged = commands.add_parser("stage", help="stage the pages only")
    staged.add_argument("--lang", choices=sorted(LANGUAGES))
    args = parser.parse_args(argv)
    if args.command == "build":
        return build(args.strict)
    if args.command == "serve":
        return serve(args.lang, args.dev_addr)
    for lang in [args.lang] if args.lang else LANGUAGES:
        print(stage(lang).relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
