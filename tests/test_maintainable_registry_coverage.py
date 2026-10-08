"""Edge cases and error paths in ddi_l.maintainable_registry."""

import pytest

from ddi_l.maintainable_registry import (
    MaintainableRegistry,
    _register_default_aliases,
    clear_registered_maintainables,
    maintainable_type_from_name,
    normalize_maintainable_type_name,
    register_maintainable,
    register_maintainable_alias,
    register_maintainables,
    resolve,
    unregister_maintainable,
)
from ddi_l.models.base import Reference
from ddi_l.models.datacollection import QuestionItem
from ddi_l.models.logicalproduct import Variable
from ddi_l.models.study import StudyUnit

# ---------------------------------------------------------------------------
# normalize_maintainable_type_name
# ---------------------------------------------------------------------------


def test_normalize_with_colon():
    assert normalize_maintainable_type_name("ddi:Variable") == "variable"


def test_normalize_with_dot():
    assert normalize_maintainable_type_name("ddi.Variable") == "variable"


def test_normalize_plain():
    assert normalize_maintainable_type_name("Variable") == "variable"


# ---------------------------------------------------------------------------
# MaintainableRegistry — resolve_type
# ---------------------------------------------------------------------------


def test_resolve_type_empty_name():
    reg = MaintainableRegistry()
    assert reg.resolve_type("") is None


def test_resolve_type_known():
    reg = MaintainableRegistry()
    result = reg.resolve_type("Variable")
    assert result is Variable


def test_resolve_type_unknown():
    reg = MaintainableRegistry()
    assert reg.resolve_type("NonExistentType") is None


def test_resolve_type_custom_alias():
    reg = MaintainableRegistry()
    reg.register_alias("myvar", Variable)
    assert reg.resolve_type("myvar") is Variable


# ---------------------------------------------------------------------------
# MaintainableRegistry — register/unregister instances
# ---------------------------------------------------------------------------


def _make_variable(agency="test.org", identifier="v1", version="1.0"):
    return Variable(agency=agency, identifier=identifier, version=version)


def test_register_instance_success():
    reg = MaintainableRegistry()
    v = _make_variable()
    result = reg.register_instance(v)
    assert result is v


def test_register_instance_not_maintainable():
    reg = MaintainableRegistry()
    with pytest.raises(TypeError, match="MaintainableBase"):
        reg.register_instance("not a maintainable")  # type: ignore[arg-type]


def test_register_instance_duplicate_urn():
    reg = MaintainableRegistry()
    v1 = _make_variable()
    v2 = _make_variable()
    reg.register_instance(v1)
    with pytest.raises(ValueError, match="URN"):
        reg.register_instance(v2)


def test_register_instance_same_object_twice():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    # Registering the same object is fine
    reg.register_instance(v)


def test_register_instance_duplicate_key():
    reg = MaintainableRegistry()
    v1 = Variable(agency="test.org", identifier="v1", version="1.0")
    v2 = Variable(agency="test.org", identifier="v1", version="1.0")
    reg.register_instance(v1)
    with pytest.raises(ValueError):
        reg.register_instance(v2)


def test_register_instances():
    reg = MaintainableRegistry()
    v1 = Variable(agency="test.org", identifier="v1", version="1.0")
    v2 = Variable(agency="test.org", identifier="v2", version="1.0")
    reg.register_instances([v1, v2])
    assert reg.resolve(("test.org", "v1", "1.0")) is v1
    assert reg.resolve(("test.org", "v2", "1.0")) is v2


def test_unregister_instance():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    reg.unregister_instance(v)
    assert reg.resolve(("test.org", "v1", "1.0")) is None


def test_unregister_instance_not_registered():
    reg = MaintainableRegistry()
    v = _make_variable()
    # Should not raise
    reg.unregister_instance(v)


def test_clear_instances():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    reg.clear_instances()
    assert reg.resolve(("test.org", "v1", "1.0")) is None


# ---------------------------------------------------------------------------
# MaintainableRegistry — _resolve_by_key
# ---------------------------------------------------------------------------


def test_resolve_by_key_exact():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    assert reg._resolve_by_key(("test.org", "v1", "1.0")) is v


def test_resolve_by_key_no_identifier():
    reg = MaintainableRegistry()
    assert reg._resolve_by_key((None, None, None)) is None


def test_resolve_by_key_fuzzy_no_agency():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    assert reg._resolve_by_key((None, "v1", None)) is v


def test_resolve_by_key_fuzzy_version_mismatch():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    assert reg._resolve_by_key(("test.org", "v1", "2.0")) is None


def test_resolve_by_key_fuzzy_agency_mismatch():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    assert reg._resolve_by_key(("other.org", "v1", None)) is None


# ---------------------------------------------------------------------------
# MaintainableRegistry — resolve
# ---------------------------------------------------------------------------


def test_resolve_maintainable_passthrough():
    reg = MaintainableRegistry()
    v = _make_variable()
    assert reg.resolve(v) is v


def test_resolve_reference_by_urn():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    urn = v._format_urn()
    ref = Reference(urn=urn, type_of_object="Variable")
    assert reg.resolve(ref) is v


def test_resolve_reference_by_key():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    ref = Reference(
        agency="test.org", identifier="v1", version="1.0", type_of_object="Variable"
    )
    assert reg.resolve(ref) is v


def test_resolve_reference_no_urn_no_key():
    reg = MaintainableRegistry()
    ref = Reference(type_of_object="Variable")
    assert reg.resolve(ref) is None


def test_resolve_string_urn():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    urn = v._format_urn()
    assert reg.resolve(urn) is v


def test_resolve_string_not_found():
    reg = MaintainableRegistry()
    assert reg.resolve("urn:ddi:nonexistent:1:1.0") is None


def test_resolve_tuple():
    reg = MaintainableRegistry()
    v = _make_variable()
    reg.register_instance(v)
    assert reg.resolve(("test.org", "v1", "1.0")) is v


def test_resolve_tuple_wrong_length():
    reg = MaintainableRegistry()
    with pytest.raises(ValueError, match="agency, identifier, version"):
        reg.resolve(("a", "b"))  # type: ignore[arg-type]


def test_resolve_unsupported_type():
    reg = MaintainableRegistry()
    with pytest.raises(TypeError, match="Unsupported"):
        reg.resolve(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------


def test_module_register_and_resolve():
    v = Variable(agency="mod.org", identifier="modv1", version="1.0")
    try:
        register_maintainable(v)
        urn = v._format_urn()
        assert resolve(urn) is v  # type: ignore[arg-type]
    finally:
        unregister_maintainable(v)
        clear_registered_maintainables()


def test_module_register_maintainables():
    v1 = Variable(agency="mod.org", identifier="modv2", version="1.0")
    v2 = Variable(agency="mod.org", identifier="modv3", version="1.0")
    try:
        register_maintainables([v1, v2])
        assert resolve(("mod.org", "modv2", "1.0")) is v1
    finally:
        unregister_maintainable(v1)
        unregister_maintainable(v2)
        clear_registered_maintainables()


def test_maintainable_type_from_name():
    assert maintainable_type_from_name("Variable") is Variable
    assert maintainable_type_from_name("") is None


def test_register_default_aliases():
    # Should not raise
    _register_default_aliases()
    # Verify short aliases work
    assert maintainable_type_from_name("studyu") is StudyUnit
    assert maintainable_type_from_name("question") is QuestionItem


def test_register_maintainable_alias():
    register_maintainable_alias("testvar", Variable)
    assert maintainable_type_from_name("testvar") is Variable
