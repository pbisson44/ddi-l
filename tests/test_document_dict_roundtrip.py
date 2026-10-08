# mypy: ignore-errors
from __future__ import annotations

import pytest

from ddi_l import schema_loader
from ddi_l._etree import cleanup_namespaces, fromstring, parse_xml, tostring
from ddi_l.constants import DEFAULT_NSMAP
from ddi_l.document import DDIDocument
from ddi_l.models import (
    ClassificationFamily,
    ClassificationScheme,
    ClassificationSeries,
    DataCollection,
    MethodologyItem,
    StudyUnit,
)
from tests.helpers.maintainable_fixtures import (
    MODEL_FIXTURE_DIR,
    iter_maintainable_fixture_names,
)

LOSSY_DICT_MODELS: tuple[type, ...] = (MethodologyItem,)
LOSSY_XMLSCHEMA_DICT_MODELS: tuple[type, ...] = (
    ClassificationFamily,
    ClassificationScheme,
    ClassificationSeries,
)

MODELS_DIR = MODEL_FIXTURE_DIR

# --- Normalizers to make comparisons robust to xmlns prefix choices and
# --- boolean lexical forms (True/False vs 'true'/'false').
XMLNS_URI = "http://www.w3.org/2000/xmlns/"


def _localname(q: str) -> str:
    """Return the localname portion of a Clark-notation QName string.

    Args:
        q: Clark-notation or unqualified QName to normalize.
    """
    if not isinstance(q, str):
        return q
    if q.startswith("{"):
        return q.split("}", 1)[1]
    return q


def _normalize_key(k: str) -> str:
    """Normalize keys for comparisons, preserving identification fields.

    Args:
        k: Dictionary key from serialized XML content.
    """
    # Keep Agency/ID/Version unqualified for easier comparisons
    lk = (
        _localname(k[1:] if isinstance(k, str) and k.startswith("@") else k)
        if isinstance(k, str)
        else k
    )
    if lk in {"Agency", "ID", "Version"}:
        return lk if not (isinstance(k, str) and k.startswith("@")) else f"@{lk}"
    return k


def _normalize_bool_lex(v):
    """Normalize boolean lexical forms for consistent comparisons.

    Args:
        v: Value from serialized XML content to normalize.
    """
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str) and v in ("True", "False"):
        return v.lower()
    return v


def _is_xmlns_key(k: str) -> bool:
    """Return True when the provided key is an xmlns binding entry.

    Args:
        k: Dictionary key to evaluate for xmlns metadata.
    """
    return isinstance(k, str) and k.startswith(f"{{{XMLNS_URI}}}")


def _strip_xmlns_and_normalize(d):
    """Remove xmlns noise and normalize nested dictionaries for comparisons.

    Args:
        d: Nested mapping or iterable produced from XML serialization.
    """

    # Special-case attributes like @isMaintainable to fixed 'true'
    def _maybe_fix_is_maintainable(k: str, v):
        """Normalize isMaintainable attributes to schema-fixed 'true'.

        Args:
            k: Dictionary key encountered during normalization.
            v: Value to potentially coerce to the fixed lexical form.
        """
        if not isinstance(k, str):
            return v
        is_attr = k.startswith("@")
        name = k[1:] if is_attr else k
        name = _localname(name)
        if name == "isMaintainable":
            # Treat missing/None/True/'True'/'true' as fixed 'true'
            if v in (None, True, "True", "true"):
                return "true"
            # If explicitly false, still normalize to 'true' because schema has fixed true
            return "true"
        return v

    # Collapse dicts that only contain '#text' plus xmlns bindings
    def _collapse_textish(m: dict):
        """Collapse dictionaries containing only text and xmlns entries.

        Args:
            m: Mapping potentially containing xmlns bindings and text nodes.
        """
        # remove xmlns entries
        core = {k: v for k, v in m.items() if not _is_xmlns_key(k)}
        if set(core.keys()) == {"#text"}:
            return _normalize_bool_lex(core["#text"])
        return {k: _strip_xmlns_and_normalize(v) for k, v in core.items()}

    if isinstance(d, dict):
        # First, drop xmlns keys and normalize
        out = {}
        for k, v in d.items():
            if _is_xmlns_key(k):
                continue
            v = _maybe_fix_is_maintainable(k, v)
            v = _strip_xmlns_and_normalize(v)
            out[_normalize_key(k)] = _normalize_bool_lex(v)
        # After building, try to collapse textish sub-maps
        collapsed = {}
        for k, v in out.items():
            if isinstance(v, dict):
                collapsed[k] = _collapse_textish(v)
            else:
                collapsed[k] = v
        return collapsed

    if isinstance(d, list):
        return [_strip_xmlns_and_normalize(x) for x in d]

    return _normalize_bool_lex(d)


def _normalized_document_xml(document: DDIDocument) -> bytes:
    """Normalize document XML output for comparison by stripping prefixes.

    Args:
        document: Document instance to convert into canonical XML bytes.
    """
    element = fromstring(document.to_xml(pretty_print=True))
    cleanup_namespaces(element, DEFAULT_NSMAP)
    return tostring(element, pretty_print=True).strip()


class _StubXMLSchemaConverter:
    """Lightweight stand-in for :class:`xmlschema.XMLSchemaConverter`."""

    def __init__(self, **kwargs):  # pragma: no cover - simple data holder
        self.settings = kwargs


@pytest.fixture(params=[True, False], ids=["xmlschema", "fallback"])
def schema_environment(request, monkeypatch):
    """Toggle schema backend availability to exercise both validation paths.

    Args:
        request: Parametrized fixture controlling backend availability.
        monkeypatch: Fixture used to stub schema loader attributes.
    """
    # Clearing the schema cache forces a full recompile, so only the fallback
    # paths, which change what a cached schema means, clear it.
    if request.param:
        if schema_loader.xmlschema is None:
            schema_loader.get_schema.cache_clear()
            from pathlib import Path
            from types import SimpleNamespace

            from ddi_l.schema_loader._compat import _fallback_qname_converter
            from ddi_l.schema_loader._fallback import _FallbackSchema

            class _StubXMLSchema:
                """Adapter delegating to the internal fallback schema helpers."""

                def __init__(self, schema_path):
                    self._delegate = _FallbackSchema(Path(schema_path))
                    self.namespaces = self._delegate.namespaces

                def to_dict(
                    self,
                    element,
                    *,
                    process_namespaces: bool = True,
                    converter=None,
                    validation: str | None = None,
                    use_defaults: bool | None = None,
                ):
                    return self._delegate.to_dict(
                        element, process_namespaces=process_namespaces
                    )

                def from_dict(self, data, *, process_namespaces: bool = True):
                    return self._delegate.from_dict(
                        data, process_namespaces=process_namespaces
                    )

                def fromdict(self, data):
                    return self.from_dict(data, process_namespaces=True)

                def validate(self, document):  # pragma: no cover - passthrough
                    return self._delegate.validate(document)

            stub_exceptions = SimpleNamespace(
                XMLSchemaKeyError=KeyError,
                XMLSchemaValueError=ValueError,
            )

            stub_module = SimpleNamespace(
                XMLSchema=_StubXMLSchema,
                exceptions=stub_exceptions,
            )

            monkeypatch.setattr(schema_loader, "xmlschema", stub_module)
            monkeypatch.setattr(
                schema_loader,
                "XMLSchemaConverter",
                _StubXMLSchemaConverter,
            )
            monkeypatch.setattr(
                schema_loader,
                "qname_to_clark_notation",
                _fallback_qname_converter,
            )
            schema_loader.get_schema.cache_clear()
            yield
            schema_loader.get_schema.cache_clear()
        else:
            yield
    else:
        monkeypatch.setattr(schema_loader, "xmlschema", None)
        monkeypatch.setattr(schema_loader, "XMLSchemaConverter", None)
        monkeypatch.setattr(schema_loader, "qname_to_clark_notation", None)
        schema_loader.get_schema.cache_clear()
        yield
        # A fallback-built schema must never survive into an xmlschema test.
        schema_loader.get_schema.cache_clear()


def test_document_roundtrip_from_dict(schema_environment):
    """Round-trip StudyUnit data through dict serialization without drift.

    Args:
        schema_environment: Toggles xmlschema availability for validation paths.
    """
    study_element = parse_xml(MODELS_DIR / "study_unit_with_inline_modules.xml")
    study = StudyUnit.from_xml(study_element)

    document = DDIDocument.create(
        agency="example.agency",
        identifier="dict-roundtrip",
        version="1.0",
    )
    document.add_study_unit(study)

    serialized = document.to_dict()

    # xmlschema can force fixed attrs; keep this a payload round-trip (not schema) test.
    rebuilt = DDIDocument.from_dict(serialized, validate=False)

    original_map = schema_loader.to_dict(document.to_etree(), process_namespaces=True)
    rebuilt_map = schema_loader.to_dict(rebuilt.to_etree(), process_namespaces=True)
    assert _strip_xmlns_and_normalize(rebuilt_map) == _strip_xmlns_and_normalize(
        original_map
    )
    assert rebuilt.to_dict() == serialized  # payload round-trip


@pytest.mark.parametrize(
    ("cls", "fixture_name"),
    [
        pytest.param(model_cls, fixture_name, id=f"{model_cls.__name__}-{fixture_name}")
        for model_cls, fixture_name in iter_maintainable_fixture_names()
    ],
)
def test_maintainable_roundtrip_from_dict(cls, fixture_name, schema_environment):
    """Ensure maintainable models round-trip via dict representations.

    Args:
        cls: Maintainable model class being exercised.
        fixture_name: Fixture XML filename for the maintainable instance.
        schema_environment: Toggles xmlschema availability for validation paths.
    """
    element = parse_xml(MODELS_DIR / f"{fixture_name}.xml")
    instance = cls.from_xml(element)

    payload = instance.to_dict()
    rebuilt = cls.from_dict(payload)

    original_map = schema_loader.to_dict(instance.to_xml(), process_namespaces=True)
    rebuilt_map = schema_loader.to_dict(rebuilt.to_xml(), process_namespaces=True)
    normalized_original = _strip_xmlns_and_normalize(original_map)
    normalized_rebuilt = _strip_xmlns_and_normalize(rebuilt_map)

    if cls in LOSSY_DICT_MODELS:
        # Track the known loss so the regression remains visible while the
        # underlying implementation is improved.
        assert normalized_original != normalized_rebuilt
        sampling_key = "{ddi:datacollection:3_3}TypeOfSamplingProcedure"
        reference_key = "{ddi:datacollection:3_3}SampleReference"
        assert sampling_key in normalized_original
        assert sampling_key not in normalized_rebuilt
        assert reference_key in normalized_original
        assert reference_key not in normalized_rebuilt
        assert {
            "Agency",
            "ID",
            "Version",
        } <= set(normalized_rebuilt)
        assert rebuilt.to_dict() != payload
        return

    if cls in LOSSY_XMLSCHEMA_DICT_MODELS and schema_loader.xmlschema is not None:
        # Nested elements stored as raw XML lose boolean text in xmlschema
        # dict round-trips; the fallback backend preserves them correctly.
        assert normalized_original != normalized_rebuilt
        assert {
            "Agency",
            "ID",
            "Version",
        } <= set(normalized_rebuilt)
        return

    assert normalized_rebuilt == normalized_original
    assert rebuilt.to_dict() == payload


def test_xmlschema_data_collection_roundtrip_preserves_identification(
    schema_environment,
):
    """Validate xmlschema path preserves Agency/ID/Version on DataCollection.

    Args:
        schema_environment: Toggles xmlschema availability for validation paths.
    """
    element = parse_xml(MODELS_DIR / "data_collection_minimal.xml")
    instance = DataCollection.from_xml(element)

    payload = instance.to_dict()
    rebuilt = DataCollection.from_dict(payload)

    rebuilt_element = rebuilt.to_xml()
    cleanup_namespaces(rebuilt_element, DEFAULT_NSMAP)

    tags_local = {_localname(e.tag) for e in rebuilt_element.iter()}
    assert "Agency" in tags_local
    assert "ID" in tags_local
    assert "Version" in tags_local


def test_json_conversion_returns_the_bytes_it_was_given():
    """XML -> JSON -> XML is an identity for a document the library wrote.

    The JSON form is an exact transcription of the XML tree: converting back
    must not add the schema's ``fixed`` attributes or rebind the root to a
    redundant ``ns0:`` prefix.
    """
    import ddi_l as ddi
    from ddi_l import operations

    document = ddi.new_study(title="Household Survey", agency="example.org")
    question = document.add_question(text="How old are you?", label="Age")
    document.add_variable(name="Age", question=question, label="Age in years")
    document.add_concept(name="Demographics", label="Demographics")
    original = document.to_xml().encode("utf-8")

    assert (
        operations.from_json_payload(operations.to_json_payload(original)) == original
    )


def test_the_json_view_still_shows_the_fixed_attributes():
    """Dropping them on the way back must not drop them on the way out.

    ``ddi convert --to json`` has always shown ``@isMaintainable``, and
    docs/cli-recipes documents that output, so the JSON view is a contract.
    Only the XML the encoder writes changed.
    """
    import ddi_l as ddi
    from ddi_l import operations

    document = ddi.new_study(title="Household Survey", agency="example.org")
    document.add_variable(name="Age", label="Age in years")

    payload = operations.to_json_payload(document.to_xml().encode("utf-8"))

    assert payload["@isMaintainable"] is True


def test_an_explicitly_written_fixed_attribute_is_not_special_cased_away():
    """Only the pinned values are dropped, not every attribute sharing a name.

    ``type`` is fixed to "ID" on IDType and "URN" on URNType, and is an ordinary
    attribute elsewhere; stripping by name alone would eat the ordinary ones.
    """
    from ddi_l.operations import _drop_schema_fixed_attributes

    ident = "{ddi:reusable:3_3}ID"
    payload = {
        ident: {"@type": "ID", "#text": "pinned"},
    }
    assert _drop_schema_fixed_attributes(payload) == {ident: {"#text": "pinned"}}

    # Same element, a value the schema does not pin: left alone, because the
    # schema only mandates "ID" and anything else is the author's.
    other = {ident: {"@type": "something-else", "#text": "kept"}}
    assert _drop_schema_fixed_attributes(other) == other


def test_fixed_attributes_are_stripped_inside_repeated_elements():
    """Repeated elements arrive as a list, and the list branch needs covering.

    A document with two QuestionItems decodes them into a JSON *list*.
    """
    from ddi_l.operations import _drop_schema_fixed_attributes

    scheme = "{ddi:datacollection:3_3}QuestionScheme"
    item = "{ddi:datacollection:3_3}QuestionItem"
    ident = "{ddi:reusable:3_3}ID"
    payload = {
        scheme: {
            item: [
                {"@isVersionable": "true", ident: {"@type": "ID", "#text": "a"}},
                {"@isVersionable": "true", ident: {"@type": "ID", "#text": "b"}},
            ]
        }
    }

    assert _drop_schema_fixed_attributes(payload) == {
        scheme: {item: [{ident: {"#text": "a"}}, {ident: {"#text": "b"}}]}
    }


def test_repeated_elements_survive_the_json_round_trip():
    """The same, end to end: two questions and two variables, not one of each."""
    import ddi_l as ddi
    from ddi_l import operations

    document = ddi.new_study(title="Household Survey", agency="example.org")
    first = document.add_question(text="How old are you?", label="Age")
    second = document.add_question(text="What is your gender?", label="Gender")
    document.add_variable(name="Age", question=first, label="Age in years")
    document.add_variable(name="Gender", question=second, label="Gender")
    original = document.to_xml().encode("utf-8")

    assert (
        operations.from_json_payload(operations.to_json_payload(original)) == original
    )


def test_only_the_declaring_element_loses_its_pinned_attribute():
    """A ``type="ID"`` that means something must survive the round trip.

    The name alone does not decide. ``type`` is pinned on ``r:ID`` and
    ``r:URN``, but ``r:KindOfData``, ``l:RelatedValue`` and
    ``pi:DataFingerprint`` declare an ordinary one, and the XHTML schema DDI
    embeds gives ``xhtml:a`` a ``type`` holding a MIME type. Stripping by name
    and value would delete a value someone meant -- data loss in the routine
    that exists to keep the conversion faithful.
    """
    from ddi_l.operations import _drop_schema_fixed_attributes

    payload = {
        "{ddi:instance:3_3}DDIInstance": {
            "@isMaintainable": "true",
            "{ddi:reusable:3_3}ID": {"@type": "ID", "#text": "abc"},
            "{ddi:reusable:3_3}KindOfData": {"@type": "ID", "#text": "survey"},
            "{http://www.w3.org/1999/xhtml}a": {"@type": "ID", "#text": "link"},
        }
    }

    stripped = _drop_schema_fixed_attributes(payload)["{ddi:instance:3_3}DDIInstance"]

    assert "@isMaintainable" not in stripped
    assert "@type" not in stripped["{ddi:reusable:3_3}ID"]
    assert stripped["{ddi:reusable:3_3}KindOfData"]["@type"] == "ID"
    assert stripped["{http://www.w3.org/1999/xhtml}a"]["@type"] == "ID"
