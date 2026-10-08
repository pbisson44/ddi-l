"""MkDocs hook: distribute ``sitemap.xml`` to every output sub-directory.

The mkdocs-material theme fetches ``sitemap.xml`` relative to every
``<link rel="alternate">`` URL it finds on the page.  Because those links
resolve to per-page paths (e.g. ``/installation/``, ``/fr/tutorials/…``),
the theme ends up requesting ``sitemap.xml`` from each of those directories.
MkDocs only generates a single root ``sitemap.xml``, so the sub-directory
requests return 404 and produce warnings in ``mkdocs serve``.

This hook runs after the full build and places a copy of the root
``sitemap.xml`` into every sub-directory of the built site so that all
those requests succeed.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig

# Directories that are not documentation pages and should be skipped.
_SKIP = {"assets", "search", "css", "js", "img", "images", "fonts"}


def on_post_build(config: MkDocsConfig, **kwargs) -> None:  # noqa: D103
    site_dir = Path(config["site_dir"])
    root_sitemap = site_dir / "sitemap.xml"
    if not root_sitemap.exists():
        return

    for sub in site_dir.rglob("*"):
        if not sub.is_dir():
            continue
        # Skip asset / non-page directories.
        if sub.name in _SKIP or any(
            p.name in _SKIP for p in sub.relative_to(site_dir).parents
        ):
            continue
        dest = sub / "sitemap.xml"
        if not dest.exists():
            shutil.copy2(root_sitemap, dest)
