"""MkDocs hook: stop mkdocs-static-i18n from dumping whole configs at INFO.

For each of the two languages, ``mkdocs-static-i18n`` logs the *entire* value it
overrides a config key with. For ``nav`` that is the full navigation tree --
every module, tutorial and reference page -- and for ``extra`` the whole
per-language mapping. Both are re-printed on every rebuild, so a single
``mkdocs serve`` session buries the lines that matter (the build result, and any
warning) under several thousand characters of echoed configuration.

The messages are not actionable: they restate what ``mkdocs.yml`` already says,
in a form nobody reads. Only the ``Overriding``/``Updating`` config echoes are
dropped. ``Building '<lang>' documentation to directory: …`` stays -- it is
short and tells you which language is being built -- and nothing at WARNING or
above is touched, so a genuine ``Unknown '<lang>' config override`` still
surfaces.

Run ``mkdocs serve --verbose`` to see them again.
"""

from __future__ import annotations

import logging
import re
from typing import Literal

# ``get_plugin_logger`` names plugin loggers ``mkdocs.plugins.<module>``. The
# plugin logs from its submodules, so match on the shared prefix.
_I18N_LOGGER_PREFIX = "mkdocs.plugins.mkdocs_static_i18n"

# ``Overriding 'en' config 'nav' with '[…]'`` / ``Updating 'en' config 'extra'…``
_CONFIG_ECHO = re.compile(r"(Overriding|Updating) '[^']*' config '")

_FILTER_INSTALLED = "_ddi_l_quiet_filter"


class _DropConfigEchoes(logging.Filter):
    """Drop the per-language config dumps, and only those."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not record.name.startswith(_I18N_LOGGER_PREFIX):
            return True
        if record.levelno > logging.INFO:
            return True
        return _CONFIG_ECHO.search(record.getMessage()) is None


def on_startup(
    *, command: Literal["build", "gh-deploy", "serve"], dirty: bool, **kwargs
) -> None:
    """Install the filter before any plugin has had a chance to log.

    ``on_startup`` is the right event rather than ``on_config``: hooks are
    appended after the configured plugins, so a hook's ``on_config`` runs
    *after* ``mkdocs-static-i18n`` has already logged the first build's echoes.
    """
    del command, dirty, kwargs

    # ``--verbose`` drops the mkdocs logger to DEBUG; someone who asked for more
    # output should not have it filtered back out.
    logger = logging.getLogger("mkdocs")
    if logger.getEffectiveLevel() <= logging.DEBUG:
        return

    # The filter goes on the *handler*, not on the plugin's logger. The plugin
    # logs to descendants of ``mkdocs.plugins.mkdocs_static_i18n``, and Python
    # consults an ancestor logger's handlers when a record propagates but not
    # its filters -- so a filter added to the plugin's logger silently does
    # nothing. mkdocs installs its stderr handler on the ``mkdocs`` logger,
    # which every one of these records passes through.
    for handler in logger.handlers:
        # ``serve`` rebuilds in-process and re-enters this hook; without the
        # sentinel every rebuild would stack another identical filter.
        if getattr(handler, _FILTER_INSTALLED, False):
            continue
        handler.addFilter(_DropConfigEchoes())
        setattr(handler, _FILTER_INSTALLED, True)
