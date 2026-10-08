<!-- markdownlint-disable-file MD041 -- sections are pasted into PR bodies, which have their own title -->
<!--
Thanks for contributing. CONTRIBUTING.md covers development setup; this
template is just the context a reviewer needs that a diff cannot show.
-->

## What this changes

<!-- The behaviour that differs after this PR, in a sentence or two. -->

## Why

<!--
The problem being solved. If it fixes an issue, link it (`Fixes #123`).
If the reasoning is subtle, prefer putting it in a code comment where it will
be read again later; this repository leans on comments that explain why.
-->

## Checks

- [ ] `uv run pytest` passes
- [ ] `uv run ruff format --check . && uv run ruff check .` passes
- [ ] `uv run mypy src` passes
- [ ] Docs updated (both `.en.md` and `.fr.md` if a page changed)
- [ ] `uv run make release-check` passes (only if packaging, schemas, or
      distribution contents changed)

## Notes for the reviewer

<!--
Anything worth flagging: a deliberate trade-off, a follow-up you chose not to
fold in, output you verified by hand, or a golden file that changed and why.
-->
