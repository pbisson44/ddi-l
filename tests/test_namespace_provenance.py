"""Every ``ddi:``-shaped namespace we emit must be one DDI actually declares.

``ddi:process:3_3`` and ``ddi:methodology:3_3`` look exactly like official DDI
namespaces. Neither is: no DDI Lifecycle release declares them. They were
synthesized by formatting ``ddi:{module}:{suffix}`` for model classes with no
counterpart in the schema, and the shape is the problem -- a recipient reading
one has every reason to assume the DDI Alliance defined it.

``Methodology`` was the case where this actually corrupted data: it *is* a real
DDI 3.3 element in ``ddi:datacollection:3_3``, so opening a valid file and
saving it produced a document no DDI tool could read. That is fixed, and this
pins the general rule so the next invented type has to be a deliberate choice.
"""

from __future__ import annotations

import inspect
import re
from functools import lru_cache
from pathlib import Path

import pytest

import ddi_l.models as models_module
from ddi_l._schema_versions import (
    _SCHEMA_NAMESPACE_TEMPLATES,
    _SYNTHETIC_NAMESPACE_TEMPLATES,
)
from ddi_l.models import MaintainableBase

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PROJECT_ROOT / "src" / "ddi_l" / "schemas" / "ddi" / "v3_3"

# Types the library models that DDI 3.3 does not define at all -- not as an
# element, not as a complexType. They keep a namespace of their own so they
# cannot collide with schema-defined content; see "Supporting a new DDI
# version" in docs/DEVELOPMENT.en.md.
KNOWN_SYNTHETIC_LOCAL_NAMES = frozenset(
    {
        "Process",
        "ProcessControl",
        "ProcessControlScheme",
        "ProcessMethod",
        "ProcessMethodScheme",
        "ProcessScheme",
        "ProcessStep",
        "ProcessStepScheme",
        "MethodologyItem",
        "MethodologyScheme",
        "ReviewEvent",
    }
)


@lru_cache(maxsize=1)
def _declared_elements() -> dict[str, frozenset[str]]:
    """Map every DDI 3.3 global element name to the namespaces declaring it.

    Cached: this is parametrized over every maintainable model, and re-reading
    two dozen XSDs per case made the whole suite measurably slower.
    """
    declared: dict[str, set[str]] = {}
    for path in SCHEMA_DIR.glob("*.xsd"):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r'targetNamespace="([^"]+)"', text)
        if match is None:
            continue
        namespace = match.group(1)
        for name in re.findall(r'<xs:element name="([A-Za-z0-9_]+)"', text):
            declared.setdefault(name, set()).add(namespace)
    return {name: frozenset(spaces) for name, spaces in declared.items()}


def _maintainable_models():
    seen: set[type] = set()
    for name in dir(models_module):
        candidate = getattr(models_module, name)
        if not inspect.isclass(candidate):
            continue
        if not issubclass(candidate, MaintainableBase) or candidate is MaintainableBase:
            continue
        if candidate not in seen:
            seen.add(candidate)
            yield candidate


def test_no_model_claims_a_ddi_namespace_the_schema_does_not_declare() -> None:
    """A model's TAG namespace is either a real DDI one or a declared synthetic."""
    real = {
        template.format(suffix="3_3")
        for template in _SCHEMA_NAMESPACE_TEMPLATES.values()
    }
    synthetic = {
        template.format(suffix="3_3")
        for template in _SYNTHETIC_NAMESPACE_TEMPLATES.values()
    }

    offenders = []
    for model in _maintainable_models():
        tag = getattr(model, "TAG", None)
        if not isinstance(tag, str) or not tag.startswith("{"):
            continue
        namespace = tag[1:].split("}")[0]
        if not namespace.startswith("ddi:"):
            continue
        if namespace not in real and namespace not in synthetic:
            offenders.append(f"{model.__name__} -> {namespace}")

    assert offenders == [], (
        "models emit ddi:-shaped namespaces that are neither declared by the "
        f"schemas nor registered as synthetic: {offenders}"
    )


def _synthetic_namespaces() -> set[str]:
    return {
        template.format(suffix="3_3")
        for template in _SYNTHETIC_NAMESPACE_TEMPLATES.values()
    }


def _models_in_synthetic_namespaces() -> list[type]:
    """Return only the models this check has anything to say about.

    Parametrizing over every maintainable and skipping the ones in a real DDI
    namespace would report ~70 skips per run -- noise that buries the handful
    of cases that matter and makes a genuine skip elsewhere easy to miss.
    """
    selected = []
    for model in _maintainable_models():
        tag = getattr(model, "TAG", None)
        if not isinstance(tag, str) or not tag.startswith("{"):
            continue
        if tag[1:].split("}")[0] in _synthetic_namespaces():
            selected.append(model)
    return sorted(selected, key=lambda cls: cls.__name__)


@pytest.mark.parametrize(
    "model", _models_in_synthetic_namespaces(), ids=lambda cls: cls.__name__
)
def test_models_in_a_synthetic_namespace_really_have_no_schema_home(model) -> None:
    """A type with a real DDI element must use the real namespace, not ours.

    ``Methodology``, for instance, belongs in ``ddi:datacollection:3_3``;
    emitting it elsewhere would break interoperability.
    """
    namespace, local_name = model.TAG[1:].split("}")
    declared_in: frozenset[str] | set[str] = _declared_elements().get(local_name, set())

    assert not declared_in, (
        f"{model.__name__} emits <{local_name}> in the synthetic namespace "
        f"{namespace!r}, but DDI 3.3 declares that element in "
        f"{sorted(declared_in)}. Use the schema's namespace."
    )
    assert local_name in KNOWN_SYNTHETIC_LOCAL_NAMES, (
        f"{local_name} is newly synthetic. If that is deliberate, add it to "
        "KNOWN_SYNTHETIC_LOCAL_NAMES and say why in the contributor guide."
    )


def test_synthetic_namespaces_do_not_impersonate_ddi() -> None:
    """A namespace we invented must not be spelled like one DDI defines.

    These were once ``ddi:process:3_3`` and ``ddi:methodology:3_3``. Nothing was
    mis-serialized by that -- the types they carry exist in no DDI release -- but
    the spelling gave a recipient no way to tell our invention from an official
    namespace. Provenance should be readable straight off the URI.
    """
    offenders = [
        template
        for template in _SYNTHETIC_NAMESPACE_TEMPLATES.values()
        if template.startswith("ddi:")
    ]

    assert offenders == [], (
        f"synthetic namespaces spelled like official DDI ones: {offenders}"
    )


def test_the_synthetic_model_selection_is_not_empty() -> None:
    """A selection that silently matched nothing would pass vacuously."""
    selected = _models_in_synthetic_namespaces()

    assert len(selected) >= 10, (
        f"expected the Process/Methodology extension types, found {selected}"
    )
