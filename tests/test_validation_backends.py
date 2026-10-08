from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable
from contextlib import contextmanager
from typing import Any

import pytest

STRUCTURAL_WARNINGS_XML = """
<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3" xmlns:s="ddi:studyunit:3_3">
  <TopLevelReference>
    <r:Agency>example.agency</r:Agency>
    <r:ID>fragment</r:ID>
    <r:Version>1.0</r:Version>
    <r:TypeOfObject>StudyUnit</r:TypeOfObject>
  </TopLevelReference>
  <Fragment>
    <s:StudyUnit>
      <r:Agency>example.agency</r:Agency>
      <r:ID>study</r:ID>
      <r:Version>1.0</r:Version>
      <r:OtherMaterialReference>
        <r:TypeOfObject> </r:TypeOfObject>
      </r:OtherMaterialReference>
      <r:ConceptReference>
        <r:Agency>example.agency</r:Agency>
        <r:ID>concept</r:ID>
        <r:TypeOfObject>Concept Scheme</r:TypeOfObject>
      </r:ConceptReference>
      <r:InstrumentReference />
    </s:StudyUnit>
  </Fragment>
</FragmentInstance>
""".strip()

FRAGMENT_GAP_XML = """
<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3" xmlns:p="urn:ddi-l:extension:process:1">
  <TopLevelReference>
    <r:Agency>example.agency</r:Agency>
    <r:ID>fragment</r:ID>
    <r:Version>1.0</r:Version>
    <r:TypeOfObject>Process</r:TypeOfObject>
  </TopLevelReference>
  <Fragment>
    <p:Process>
      <r:Agency>example.agency</r:Agency>
      <r:ID>process</r:ID>
      <r:Version>1.0</r:Version>
    </p:Process>
  </Fragment>
</FragmentInstance>
""".strip()


@contextmanager  # type: ignore[arg-type]
def _patched_environment(
    xmlschema_enabled: bool, monkeypatch: pytest.MonkeyPatch
) -> Iterable[None]:
    validation_mod = importlib.import_module("ddi_l.schema_loader._validation")
    loader_mod = importlib.import_module("ddi_l.schema_loader")
    with monkeypatch.context() as patch:
        validation_module = importlib.reload(validation_mod)
        loader = importlib.reload(loader_mod)
        if not xmlschema_enabled:
            patch.setattr(loader, "xmlschema", None)
        elif (
            loader.xmlschema is None
        ):  # pragma: no cover - depends on optional dependency
            pytest.skip("xmlschema backend unavailable")
        yield patch, loader, validation_module  # type: ignore[misc]
    importlib.reload(validation_mod)
    importlib.reload(loader_mod)


def _run_validation(
    xml_payload: str,
    *,
    xmlschema_enabled: bool,
    monkeypatch: pytest.MonkeyPatch,
    configure: Callable[[pytest.MonkeyPatch, Any], None] | None = None,
) -> list[dict[str, object | None]]:
    with _patched_environment(xmlschema_enabled, monkeypatch) as (patch, loader, _):  # type: ignore[var-annotated]
        if configure is not None:
            configure(patch, loader)
        loader.get_schema.cache_clear()
        element = loader.fromstring(xml_payload)
        issues = loader.validate(element, raise_error=False)
        loader.get_schema.cache_clear()
    return [issue.to_dict() for issue in issues]


def _stub_schema(
    patch: pytest.MonkeyPatch, loader: Any, schema_factory: Callable[[], Any]
) -> None:
    class _SchemaFactory:
        def __init__(self, schema: Any) -> None:
            self._schema = schema

        def __call__(self, *args: object, **kwargs: object) -> Any:
            return self._schema

        def cache_clear(self) -> None:  # pragma: no cover - compatibility shim
            return None

    patch.setattr(loader, "get_schema", _SchemaFactory(schema_factory()))


def _configure_structural_warning_stub(patch: pytest.MonkeyPatch, loader: Any) -> None:
    class _StubSchema:
        namespaces: dict[str, str] = {}

        def validate(self, _root: Any) -> None:
            return None

    _stub_schema(patch, loader, _StubSchema)


def _configure_fragment_gap_stub(patch: pytest.MonkeyPatch, loader: Any) -> None:
    class _FragmentGapError(Exception):
        def __init__(self, invalid_child: Any) -> None:
            super().__init__("fragment gap")
            self.invalid_child = invalid_child
            self.obj = invalid_child
            self.path = None

    class _StubSchema:
        namespaces: dict[str, str] = {}

        def validate(self, root: Any) -> None:
            child = root.find(".//{urn:ddi-l:extension:process:1}Process")
            raise _FragmentGapError(child)

    _stub_schema(patch, loader, _StubSchema)
    patch.setattr(loader, "XMLSchemaValidationError", _FragmentGapError)


def test_structural_warnings_match_python(monkeypatch: pytest.MonkeyPatch) -> None:
    results = _run_validation(
        STRUCTURAL_WARNINGS_XML,
        xmlschema_enabled=False,
        monkeypatch=monkeypatch,
        configure=_configure_structural_warning_stub,
    )

    assert results, "expected structural warnings to be emitted"


def test_fragment_gap_preflight(monkeypatch: pytest.MonkeyPatch) -> None:
    results = _run_validation(
        FRAGMENT_GAP_XML,
        xmlschema_enabled=False,
        monkeypatch=monkeypatch,
        configure=_configure_fragment_gap_stub,
    )

    assert results == []


def test_validation_backend_selector_rejects_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = importlib.import_module("ddi_l.schema_loader._validation")
    loader = importlib.import_module("ddi_l.schema_loader")

    class _DummyElement:
        tag = "{ddi:instance:fake}FragmentInstance"
        attrib: dict[str, str] = {}
        text = ""

        @staticmethod
        def find(_path: str) -> None:
            return None

    with monkeypatch.context() as patch:
        patch.setattr(runtime, "_coerce_element", lambda _document: _DummyElement())
        patch.setattr(runtime, "detect_version_from_element", lambda _root: "3.3")
        runtime.set_validation_backend("python")
        loader.validate(object(), raise_error=False)

    with pytest.raises(ValueError):
        runtime.set_validation_backend("native")


def test_available_validation_backends_follow_lxml() -> None:
    runtime = importlib.import_module("ddi_l.schema_loader._validation")
    from ddi_l._etree import USING_LXML

    expected = ("python", "lxml") if USING_LXML else ("python",)
    assert runtime.get_available_validation_backends() == expected
    assert runtime._default_backend == expected[-1]


def _lxml_only() -> None:
    pytest.importorskip("lxml")
    from ddi_l._etree import USING_LXML

    if not USING_LXML:
        pytest.skip("lxml backend not active")


@contextmanager
def _backend(name: str):
    runtime = importlib.import_module("ddi_l.schema_loader._validation")
    previous = runtime.IMPLEMENTATION
    runtime.set_validation_backend(name)
    try:
        yield runtime
    finally:
        runtime.set_validation_backend(previous)


def test_lxml_backend_skips_xmlschema_for_valid_documents(monkeypatch) -> None:
    _lxml_only()
    import ddi_l as ddi
    from ddi_l import schema_loader

    doc = ddi.new_study(title="Fast", agency="example.org")
    doc.add_variable(name="age", label="Age")
    root = doc.inner.root
    calls: list[int] = []
    schema = schema_loader.get_schema("3.3")
    original = type(schema).validate

    def counting(self, *args, **kwargs):
        calls.append(1)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(type(schema), "validate", counting)
    with _backend("lxml") as runtime:
        assert runtime.validate(root, raise_error=False) == []
    assert calls == []
    with _backend("python") as runtime:
        assert runtime.validate(root, raise_error=False) == []
    assert calls == [1]


def test_backends_report_identical_issues() -> None:
    _lxml_only()
    
    from lxml import etree  # type: ignore[import-untyped]

    import ddi_l as ddi

    doc = ddi.new_study(title="Broken", agency="example.org")
    doc.add_variable(name="age", label="Age")
    root = doc.inner.root
    variable = next(e for e in root.iter() if str(e.tag).endswith("}Variable"))
    variable.append(etree.Element("{ddi:logicalproduct:3_3}Bogus"))

    with _backend("lxml") as runtime:
        fast = [issue.to_dict() for issue in runtime.validate(root, raise_error=False)]
    with _backend("python") as runtime:
        slow = [issue.to_dict() for issue in runtime.validate(root, raise_error=False)]
    assert fast
    assert fast == slow


def test_unknown_backend_is_rejected() -> None:
    from ddi_l import schema_loader

    with pytest.raises(ValueError):
        schema_loader.set_validation_backend("rust")
