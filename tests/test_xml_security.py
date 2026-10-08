from __future__ import annotations

import pytest

from ddi_l import _etree
from ddi_l.xml_utils import coerce_element


def _expected_entity_errors() -> tuple[type[BaseException], ...]:
    """Collect the exception types a backend may raise on entity declarations.

    ``coerce_element`` parses through :mod:`ddi_l._etree`, which uses lxml when
    installed, a bundled ``lxml`` shim otherwise, and finally defusedxml/stdlib.
    Each backend signals a blocked entity declaration with its own exception
    type, so the test accepts whichever applies to the active backend.
    """
    expected: tuple[type[BaseException], ...] = ()
    xml_syntax_error = getattr(_etree.etree, "XMLSyntaxError", None)
    if isinstance(xml_syntax_error, type):
        expected += (xml_syntax_error,)
    try:  # pragma: no cover - depends on installed backend
        from defusedxml.common import (  # type: ignore[import-untyped]
            DefusedXmlException,
        )

        expected += (DefusedXmlException,)
    except ModuleNotFoundError:  # pragma: no cover - defusedxml is a dependency
        pass
    return expected


def test_coerce_element_blocks_entity_expansion():
    payload = (
        "<?xml version='1.0'?>\n<!DOCTYPE root [\n<!ENTITY spam '"
        + "spam" * 50
        + "'>\n]><root>&spam;</root>\n"
    )

    expected = _expected_entity_errors()
    assert expected, "no XML backend exposed an entity-declaration error type"

    with pytest.raises(expected):
        coerce_element(payload)
