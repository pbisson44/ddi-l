"""MkDocs hook: only advertise the version selector on a real ``mike`` build.

``extra.version.provider: mike`` makes the theme fetch ``versions.json``. The
theme resolves that URL as ``new URL("../versions.json", base)`` -- one level
*above* the site base -- because ``mike`` publishes each version under
``<site_url>/<version>/`` and keeps the manifest beside those directories.

That arithmetic is right in production. ``mike``'s own MkDocs plugin rewrites
``site_url`` to ``https://…/ddi-l/<version>`` when it drives the build, so the
base is ``/ddi-l/latest/`` and ``../versions.json`` lands on ``/ddi-l/versions.json``.

Plain ``mkdocs serve`` builds no version at all, so the base stays ``/ddi-l/``
and the same expression overshoots to ``/versions.json`` -- a 404 on every
single page load, and a version selector that cannot work locally because
nothing has generated a manifest.

``mike`` announces itself through ``MIKE_DOCS_VERSION`` (``mike.mkdocs_utils``
sets it before invoking MkDocs, and its plugin reads the same variable to
rewrite ``site_url``). Keying off it means the selector appears exactly when
there is something for it to select, and local previews are quiet.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - the annotation is the only use
    # Imported for typing only: the test suite runs without the `docs`
    # dependency group, and a module-scope import would make this hook
    # unimportable there.
    from mkdocs.config.defaults import MkDocsConfig

# The variable ``mike`` exports when it drives a build. Read rather than
# imported so the hook does not make ``mike`` a hard requirement for building
# the documentation.
_MIKE_VERSION_VAR = "MIKE_DOCS_VERSION"


def on_config(config: MkDocsConfig, **kwargs) -> MkDocsConfig:  # noqa: D103
    if os.environ.get(_MIKE_VERSION_VAR):
        return config

    extra = config.get("extra")
    if extra is not None:
        # Mutate in place. ``extra`` is not a plain dict -- mkdocs-static-i18n
        # sets attributes on it (``alternate``) that the theme templates read,
        # and swapping in a replacement mapping loses them.
        extra.pop("version", None)

    return config
