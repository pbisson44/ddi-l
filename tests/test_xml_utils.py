import io

import pytest

from ddi_l.xml_utils import coerce_element, resolve_xml_source


def test_resolve_xml_source_path(tmp_path):
    document = tmp_path / "document.xml"
    document.write_text("<root />")

    kind, payload = resolve_xml_source(str(document))

    assert kind == "path"
    assert payload == document


def test_resolve_xml_source_text():
    kind, payload = resolve_xml_source("<root />")

    assert kind == "text"
    assert payload == "<root />"


def test_resolve_xml_source_bytes():
    kind, payload = resolve_xml_source(b"<root />")

    assert kind == "bytes"
    assert isinstance(payload, bytes)


def test_resolve_xml_source_file_like():
    handle = io.BytesIO(b"<root />")

    kind, payload = resolve_xml_source(handle)

    assert kind == "file"
    assert payload is handle


def test_resolve_xml_source_missing_path(tmp_path):
    missing = tmp_path / "missing.xml"

    with pytest.raises(FileNotFoundError):
        resolve_xml_source(missing, require_existing_path=True)


def test_resolve_xml_source_missing_path_from_str(tmp_path):
    missing = tmp_path / "missing.xml"

    with pytest.raises(FileNotFoundError):
        resolve_xml_source(str(missing), require_existing_path=True)


def test_coerce_element_parses_path(tmp_path):
    document = tmp_path / "document.xml"
    document.write_text("<root />")

    element = coerce_element(document)

    assert element.tag == "root"


def test_coerce_element_reads_file_like_text():
    element = coerce_element(io.StringIO("<root />"))

    assert element.tag == "root"


def test_coerce_element_rejects_unknown_type():
    with pytest.raises(TypeError):
        coerce_element(object())  # type: ignore[arg-type]
