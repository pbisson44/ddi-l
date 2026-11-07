"""No process-global state: a change one caller makes never reaches another.

Every setting a call depends on is an argument or a context-local default.
What is left at module level is either filled at import and never changed
(rule and type registries, schema tables), a cache that gives the same answer
whoever fills it, or an application default that only the application sets
(`configure`, `configure_lint`, `set_validation_backend`), as
`decimal.DefaultContext` is for `decimal`.
"""

from __future__ import annotations

import ast
import importlib
import pkgutil
import threading
from collections.abc import Callable
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any

import pytest

import ddi_l
from ddi_l import lint, schema_loader
from ddi_l.namespaces import NAMESPACE_PROFILES
from ddi_l.schema_loader import _validation

SOURCE = Path(ddi_l.__file__).parent
FIXTURES = Path(__file__).parent / "fixtures"

# The only `global` statements left: application defaults, set on purpose.
APPLICATION_DEFAULTS = {
    ("config.py", "_default"),
    ("lint.py", "_CONFIG"),
    ("schema_loader/_validation.py", "_DEFAULT_BACKEND"),
    ("cli.py", "_DEBUG"),
}


def _in_threads(*work: Callable[[threading.Barrier], Any]) -> list[Any]:
    """Run each function in its own thread, all started together."""
    barrier = threading.Barrier(len(work))
    results: list[Any] = [None] * len(work)
    errors: list[BaseException] = []

    def run(index: int, function: Callable[[threading.Barrier], Any]) -> None:
        try:
            results[index] = function(barrier)
        except BaseException as error:  # pragma: no cover - reported below
            errors.append(error)

    threads = [
        threading.Thread(target=run, args=(index, function))
        for index, function in enumerate(work)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if errors:
        raise errors[0]
    return results


def test_a_scoped_configuration_stays_in_its_thread() -> None:
    ddi_l.configure(version_responsibility="Application")

    def scoped(barrier: threading.Barrier) -> str | None:
        with ddi_l.configured(version_responsibility="Scoped"):
            barrier.wait()  # the other thread reads now
            barrier.wait()
            return ddi_l.get_configuration().version_responsibility

    def other(barrier: threading.Barrier) -> str | None:
        barrier.wait()
        seen = ddi_l.get_configuration().version_responsibility
        barrier.wait()
        return seen

    assert _in_threads(scoped, other) == ["Scoped", "Application"]
    assert ddi_l.get_configuration().version_responsibility == "Application"


def test_the_application_default_reaches_every_thread() -> None:
    ddi_l.configure(version_responsibility="Application")

    def read(_barrier: threading.Barrier) -> str | None:
        return ddi_l.get_configuration().version_responsibility

    assert _in_threads(read, read) == ["Application", "Application"]


def _document() -> ddi_l.DDIDocument:
    return ddi_l.DDIDocument.create(
        agency="int.example", identifier="state-1", version="1"
    )


def test_validate_takes_its_backend_per_call(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*_arguments: object) -> bool:
        raise AssertionError("libxml2 ran")

    monkeypatch.setattr(_validation._libxml2, "is_valid", fail)

    assert schema_loader.validate(_document().root, backend="python") == []
    with pytest.raises(ValueError, match="Unsupported validation backend"):
        schema_loader.validate(_document().root, backend="rust")


def test_a_scoped_validation_backend_stays_in_its_thread() -> None:
    default = schema_loader.get_validation_backend()

    def scoped(barrier: threading.Barrier) -> str:
        with schema_loader.validation_backend("python"):
            barrier.wait()
            barrier.wait()
            return schema_loader.get_validation_backend()

    def other(barrier: threading.Barrier) -> str:
        barrier.wait()
        seen = schema_loader.get_validation_backend()
        barrier.wait()
        return seen

    assert _in_threads(scoped, other) == ["python", default]


def test_setting_the_validation_backend_rebinds_nothing() -> None:
    before = dict(vars(_validation))
    previous = schema_loader.get_validation_backend()
    schema_loader.set_validation_backend("python")
    try:
        assert schema_loader.get_validation_backend() == "python"
        changed = {
            name
            for name, value in vars(_validation).items()
            if before.get(name, object()) is not value
        }
        assert changed <= {"_DEFAULT_BACKEND"}
    finally:
        schema_loader.set_validation_backend(previous)


def test_the_allowed_agencies_are_read_only() -> None:
    lint.configure_lint(allowed_agencies=["one.example"])

    assert frozenset({"one.example"}) == lint.ALLOWED_AGENCIES
    with pytest.raises(AttributeError):
        lint.ALLOWED_AGENCIES.add("two.example")  # type: ignore[attr-defined]
    lint.reset_lint_configuration()
    assert frozenset() == lint.ALLOWED_AGENCIES


def test_the_namespace_profiles_are_read_only() -> None:
    assert isinstance(NAMESPACE_PROFILES, MappingProxyType)
    with pytest.raises(TypeError):
        NAMESPACE_PROFILES["new"] = NAMESPACE_PROFILES["ddi-default"]  # type: ignore[index]


def test_only_application_defaults_use_global_statements() -> None:
    found = set()
    for path in sorted(SOURCE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                for name in node.names:
                    found.add((path.relative_to(SOURCE).as_posix(), name))

    assert found <= APPLICATION_DEFAULTS


# ---- A workload changes no module-level state ------------------------------

# Caches: whoever fills them, they give the same answers.
CACHES = {
    "ddi_l.schema_loader._cache._SCHEMA_CACHE",
    "ddi_l.schema_loader._libxml2._SCHEMAS",
    "ddi_l.schema_loader._validation._FRAGMENT_GAP_CACHE",
}


def _modules() -> list[ModuleType]:
    modules = []
    for info in pkgutil.walk_packages(ddi_l.__path__, "ddi_l."):
        if ".examples" in info.name or info.name.endswith("__main__"):
            continue
        try:
            modules.append(importlib.import_module(info.name))
        except ImportError:  # an extra that is not installed
            continue
    return modules


def _mutable_state() -> dict[str, str]:
    state = {}
    for module in _modules():
        for name, value in vars(module).items():
            if not isinstance(value, (dict, list, set, bytearray)):
                continue
            key = f"{module.__name__}.{name}"
            if key in CACHES:
                continue
            state[key] = (
                repr(sorted(map(repr, value)))
                if isinstance(value, set)
                else repr(value)
            )
    return state


def test_a_workload_changes_no_module_level_state(tmp_path: Path) -> None:
    pytest.importorskip("yaml")
    from ddi_l.spec import conform, load_spec

    # Fill the caches the workload uses before taking the snapshot.
    fragment = ddi_l.open_fragment(FIXTURES / "colectica" / "pets_instrument.ddi33.xml")
    before = _mutable_state()

    fragment = ddi_l.open_fragment(FIXTURES / "colectica" / "pets_instrument.ddi33.xml")
    lint.run_profile(fragment, "colectica-questionnaire")
    schema_loader.validate(fragment.root, raise_error=False)
    schema_loader.to_dict(fragment.root)
    spec = load_spec(FIXTURES / "spec" / "pets_conform.spec.yaml")
    conform(ddi_l.open_fragment(FIXTURES / "spec" / "pets_conform.ddi33.xml"), spec)
    ddi_l.write_ddi(fragment, tmp_path / "out.xml")
    with ddi_l.configured(version_responsibility="Workload"):
        study = ddi_l.new_study(title="State", agency="int.example")
        study.validate()
        study.lint()
        study.save(tmp_path / "study.xml")

    assert _mutable_state() == before


def test_namespace_prefixes_stay_out_of_elementtrees_registry() -> None:
    """ElementTree's registry is left alone; prefixes stay in their thread.

    Building and writing a document leaves the registry as it was, and a
    prefix registered in one thread is not seen in another.
    """
    from xml.etree import ElementTree

    from ddi_l import _etree

    before = dict(ElementTree._namespace_map)  # type: ignore[attr-defined]
    document = ddi_l.new_study(title="Pets", agency="example.org")
    document.to_xml()
    assert dict(ElementTree._namespace_map) == before  # type: ignore[attr-defined]

    if _etree.USING_LXML:
        return
    element = _etree.create_element(
        "{urn:example:pets}Pet", {"pet": "urn:example:pets"}
    )
    assert _etree.unicode_text(element).startswith("<pet:Pet")
    seen: list[str] = []
    other = threading.Thread(target=lambda: seen.append(_etree.unicode_text(element)))
    other.start()
    other.join()
    assert seen[0].startswith("<ns0:Pet")
