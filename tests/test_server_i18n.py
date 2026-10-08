"""The French OpenAPI rendering must translate prose and nothing else.

A localized spec has two ways to go wrong, and only one of them is visible by
looking at the page. The obvious one is prose left in English. The dangerous one
is a translation that reaches past the prose into the contract -- a field name,
an enum value, a sample document -- because that produces a French spec
describing an API that does not exist, and a generated client that does not
work.

So these tests assert the translation is *complete* and *confined*: every string
the spec exposes has an entry, and everything a client parses is byte-identical
between locales.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest

pytest.importorskip("litestar", reason="requires the 'server' extra")

from litestar.testing import TestClient

from ddi_l.server.app import create_app
from ddi_l.server.i18n import (
    DEFAULT_LOCALE,
    LOCALES,
    TRANSLATABLE_KEYS,
    missing_translations,
    translate_schema,
    unused_translations,
)

EN_JSON = "/schema/openapi.json"
FR_JSON = "/schema/openapi.fr.json"


@pytest.fixture
def client() -> Any:
    with TestClient(app=create_app()) as test_client:
        yield test_client


@pytest.fixture
def schema() -> dict[str, Any]:
    """The English schema, as the render plugins receive it."""
    return create_app().openapi_schema.to_schema()


def _strip_prose(node: Any) -> Any:
    """Return ``node`` with every translatable field removed.

    What survives is the part of the document a client actually consumes:
    paths, operation ids, field names, types, enums and examples. Two locales
    must be identical here or the French spec describes a different API.
    """
    if isinstance(node, dict):
        return {
            key: _strip_prose(value)
            for key, value in node.items()
            if key not in TRANSLATABLE_KEYS
        }
    if isinstance(node, list):
        return [_strip_prose(item) for item in node]
    return node


# --------------------------------------------------------------------------
# The catalog tracks the spec
# --------------------------------------------------------------------------


@pytest.mark.parametrize("locale", sorted(LOCALES))
def test_every_string_in_the_spec_is_translated(
    schema: dict[str, Any], locale: str
) -> None:
    """A new endpoint must arrive with its translation, or French readers see English."""
    missing = missing_translations(schema, locale)
    assert missing == [], (
        f"{len(missing)} string(s) have no {locale} translation. Add them to "
        f"LOCALES[{locale!r}] in ddi_l.server.i18n:\n  "
        + "\n  ".join(repr(text) for text in missing)
    )


@pytest.mark.parametrize("locale", sorted(LOCALES))
def test_no_translation_outlives_its_english_source(
    schema: dict[str, Any], locale: str
) -> None:
    """Rewording English leaves a stale entry behind; this is what finds it."""
    orphans = unused_translations(schema, locale)
    assert orphans == [], (
        f"{len(orphans)} {locale} translation(s) no longer match any string in "
        f"the spec -- the English was reworded or removed. Delete or re-key "
        f"them in ddi_l.server.i18n:\n  " + "\n  ".join(repr(text) for text in orphans)
    )


# --------------------------------------------------------------------------
# The translation is confined to prose
# --------------------------------------------------------------------------


def test_the_contract_is_identical_across_locales(schema: dict[str, Any]) -> None:
    """Strip the prose and the two specs must be the same document."""
    french = translate_schema(schema, "fr")
    assert _strip_prose(french) == _strip_prose(schema)


def test_example_documents_are_never_translated(schema: dict[str, Any]) -> None:
    """The samples are real DDI the service must accept, not prose."""
    french = translate_schema(schema, "fr")

    def examples(node: Any, found: list[Any]) -> list[Any]:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"value", "example"}:
                    found.append(value)
                else:
                    examples(value, found)
        elif isinstance(node, list):
            for item in node:
                examples(item, found)
        return found

    english_examples = examples(schema, [])
    assert english_examples, "no examples found -- the test is not checking anything"
    assert examples(french, []) == english_examples


def test_the_package_name_is_not_translated(schema: dict[str, Any]) -> None:
    french = translate_schema(schema, "fr")
    assert french["info"]["title"] == schema["info"]["title"] == "ddi-l"


def test_translating_does_not_mutate_the_source(schema: dict[str, Any]) -> None:
    """Litestar caches one schema object; translating in place would poison it."""
    before = copy.deepcopy(schema)
    translate_schema(schema, "fr")
    assert schema == before


# --------------------------------------------------------------------------
# Locale selection
# --------------------------------------------------------------------------


def test_the_default_locale_is_returned_untouched(schema: dict[str, Any]) -> None:
    assert translate_schema(schema, DEFAULT_LOCALE) is schema


def test_an_unknown_locale_falls_back_to_english(schema: dict[str, Any]) -> None:
    """A bad locale is a missing translation, not a 500."""
    assert translate_schema(schema, "xx-nonexistent") is schema


# --------------------------------------------------------------------------
# What the service actually serves
# --------------------------------------------------------------------------


def test_both_locales_are_served(client: Any) -> None:
    assert client.get(EN_JSON).status_code == 200
    assert client.get(FR_JSON).status_code == 200


def test_the_served_french_spec_is_french(client: Any) -> None:
    english = client.get(EN_JSON).json()
    french = client.get(FR_JSON).json()

    assert english["paths"]["/v1/validate"]["post"]["summary"] == (
        "Validate a DDI document"
    )
    assert french["paths"]["/v1/validate"]["post"]["summary"] == (
        "Valider un document DDI"
    )
    assert french["paths"].keys() == english["paths"].keys()


def test_requesting_french_does_not_change_what_english_serves(client: Any) -> None:
    """The memoized French copy must not leak into the shared schema."""
    before = client.get(EN_JSON).json()
    client.get(FR_JSON)
    assert client.get(EN_JSON).json() == before


def test_the_french_swagger_page_renders_french(client: Any) -> None:
    """Swagger embeds the spec inline, so the page carries the translation."""
    page = client.get("/schema/fr")

    assert page.status_code == 200
    assert "Valider un document DDI" in page.text
    assert "Validate a DDI document" not in page.text


def test_the_bare_schema_path_stays_english(client: Any) -> None:
    """An unaccompanied /schema link should resolve to the source language."""
    page = client.get("/schema")

    assert "Validate a DDI document" in page.text
    assert "Valider un document DDI" not in page.text


def test_the_french_spec_is_valid_json_for_generators(client: Any) -> None:
    """The point of the .json path is that a client generator can consume it."""
    document = json.loads(client.get(FR_JSON).content)

    assert document["openapi"].startswith("3.")
    assert document["info"]["version"]
    assert "/v1/validate" in document["paths"]
