"""OpenAPI render plugins that serve the schema in a non-default locale.

Litestar hands every render plugin the *serialized* schema dict, which makes
translation a wrapper rather than a fork: the plugin below substitutes the
prose and then lets the stock Swagger or JSON renderer do its job. Nothing
about the spec's structure is duplicated here, so an endpoint added tomorrow
appears in the French UI with no change to this module.

Swagger embeds the spec inline rather than fetching it, so translating the dict
also translates the page's ``<title>``.
"""

from __future__ import annotations

from typing import Any

from litestar import Request
from litestar.openapi.plugins import JsonRenderPlugin, SwaggerRenderPlugin

from .i18n import translate_schema

__all__ = ["LocalizedJsonRenderPlugin", "LocalizedSwaggerRenderPlugin"]


class _Localized:
    """Holds the locale and memoizes the translated schema.

    Litestar builds the schema once per application and hands the same dict to
    every render call, so translating on each request would rebuild an
    identical document (a deep copy plus a full walk) for every page view.
    """

    def __init__(self, *, locale: str, **kwargs: Any) -> None:
        self.locale = locale
        self._translated: dict[str, Any] | None = None
        super().__init__(**kwargs)

    def _localized(self, openapi_schema: dict[str, Any]) -> dict[str, Any]:
        if self._translated is None:
            self._translated = translate_schema(openapi_schema, self.locale)
        return self._translated


class LocalizedSwaggerRenderPlugin(_Localized, SwaggerRenderPlugin):
    """Swagger UI rendering a translated spec."""

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Render the Swagger page against the localized schema."""
        return super().render(request, self._localized(openapi_schema))


class LocalizedJsonRenderPlugin(_Localized, JsonRenderPlugin):
    """The raw OpenAPI document, translated, for client generators."""

    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        """Serialize the localized schema as JSON."""
        return super().render(request, self._localized(openapi_schema))
