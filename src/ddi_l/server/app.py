"""Litestar application factory."""

from __future__ import annotations

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.datastructures import State
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import (
    JsonRenderPlugin,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
    YamlRenderPlugin,
)

from .. import __version__
from .config import ServerConfig
from .openapi import document_request_bodies
from .render import LocalizedJsonRenderPlugin, LocalizedSwaggerRenderPlugin
from .routes import ROUTE_HANDLERS


async def _preload_default_schema() -> None:
    """Load the default DDI schema in a worker thread before serving."""
    import anyio.to_thread

    from .. import schema_loader
    from ..schema_loader import _libxml2
    from ..schema_loader._constants import SCHEMA_VERSION

    await anyio.to_thread.run_sync(schema_loader.get_schema)
    await anyio.to_thread.run_sync(_libxml2.get_libxml2_schema, SCHEMA_VERSION)


def create_app(config: ServerConfig | None = None) -> Litestar:
    """Build the application.

    Args:
        config: Runtime limits and exposure settings. Defaults to
            :class:`~ddi_l.server.config.ServerConfig`, which is conservative: a
            32 MiB body cap, a 60-second bound on how long a client waits, and
            CORS off. See ``ServerConfig`` for what the timeout does and does
            not cover.

    Returns:
        A configured :class:`litestar.Litestar` instance.
    """
    config = config or ServerConfig()

    openapi_config = None
    if config.enable_openapi:
        openapi_config = OpenAPIConfig(
            title="ddi-l",
            version=__version__,
            description=(
                "Validate, lint and convert DDI Lifecycle XML. Every endpoint is "
                "a thin wrapper over the same functions the `ddi` CLI calls."
            ),
            path="/schema",
            # The first plugin is served at the bare /schema path: Swagger UI, whose
            # "Try it out" lets a reader post a document. The other UIs stay under
            # /schema/<name>. The French pair (/schema/fr, /schema/openapi.fr.json)
            # comes last so the bare path stays English; see ddi_l.server.i18n.
            render_plugins=[
                SwaggerRenderPlugin(),
                RedocRenderPlugin(),
                StoplightRenderPlugin(),
                RapidocRenderPlugin(),
                JsonRenderPlugin(),
                YamlRenderPlugin(),
                LocalizedSwaggerRenderPlugin(locale="fr", path="/fr"),
                LocalizedJsonRenderPlugin(locale="fr", path="/openapi.fr.json"),
            ],
        )

    app = Litestar(
        route_handlers=ROUTE_HANDLERS,
        on_startup=[_preload_default_schema] if config.preload_schema else [],
        openapi_config=openapi_config,
        # Handlers read their limits from `request.app.state.ddi_config`.
        state=State({"ddi_config": config}),
        cors_config=(
            CORSConfig(allow_origins=list(config.cors_allow_origins))
            if config.cors_allow_origins
            else None
        ),
        # Bounds the work each request can cause.
        request_max_body_size=config.max_body_bytes,
        # All parsing goes through ddi_l._etree, so XXE and entity-expansion
        # protection is the library's; the server adds no parse path of its own.
        debug=False,
    )

    if openapi_config is not None:
        # Build the spec now so `document_request_bodies` checks the documented
        # routes at startup rather than on the first request to /schema.
        document_request_bodies(app.openapi_schema)

    return app
