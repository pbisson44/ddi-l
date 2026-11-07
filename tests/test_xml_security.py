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
    for name in ("XMLSyntaxError", "ParseError"):
        error = getattr(_etree.etree, name, None)
        if isinstance(error, type):
            expected += (error,)
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


DOCTYPE_MESSAGE = "Document type declarations are not permitted in DDI documents."

DOCUMENT_TYPES = [
    b"<!DOCTYPE root><root/>",
    b'<!DOCTYPE root SYSTEM "root.dtd"><root/>',
    b"<!DOCTYPE root [<!ELEMENT root EMPTY>]><root/>",
]


@pytest.mark.parametrize("payload", DOCUMENT_TYPES)
def test_both_backends_refuse_a_document_type(payload, tmp_path):
    path = tmp_path / "typed.xml"
    path.write_bytes(payload)

    with pytest.raises(_etree.PARSER_ERRORS, match=DOCTYPE_MESSAGE):
        _etree.fromstring(payload)
    with pytest.raises(_etree.PARSER_ERRORS, match=DOCTYPE_MESSAGE):
        _etree.parse_xml(path)


def test_read_ddi_refuses_a_document_type():
    from ddi_l import read_ddi
    from ddi_l.exceptions import DDIParseError

    payload = b'<!DOCTYPE DDIInstance><DDIInstance xmlns="ddi:instance:3_3"/>'

    with pytest.raises(DDIParseError, match=DOCTYPE_MESSAGE):
        read_ddi(payload)


@pytest.mark.parametrize("payload", DOCUMENT_TYPES)
def test_iterparse_ddi_refuses_a_document_type(payload):
    import io

    from ddi_l.io import iterparse_ddi

    with pytest.raises(_etree.PARSER_ERRORS, match=DOCTYPE_MESSAGE):
        list(iterparse_ddi(io.BytesIO(payload)))


@pytest.mark.parametrize(
    "option",
    [
        {"resolve_entities": True},
        {"load_dtd": True},
        {"no_network": False},
        {"forbid_dtd": False},
        {"forbid_entities": False},
        {"forbid_external": False},
        {"parser": None},
    ],
)
def test_iterparse_ddi_will_not_weaken_the_parser(option):
    import io

    from ddi_l.io import iterparse_ddi

    with pytest.raises(ValueError, match="iterparse_ddi"):
        list(iterparse_ddi(io.BytesIO(b"<root/>"), **option))
