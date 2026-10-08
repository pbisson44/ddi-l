import pytest

from ddi_l.constants import (
    CONCEPTUAL_COMPONENT_NS,
    DDI_PROFILE_NS,
    INSTANCE_NS,
    PROCESS_NS,
    REUSABLE_NS,
    STUDY_UNIT_NS,
)
from ddi_l.namespaces import (
    DDI_DEFAULT_PROFILE,
    DDI_PROFILE_PROFILE,
    DDI_STUDY_UNIT_PROFILE,
    NAMESPACE_PREFIXES,
    build_namespace_map,
    get_namespace_profile,
    merge_namespace_profiles,
)


def test_pr_prefix_binds_ddiprofile_not_process():
    """``pr`` is the ddiprofile prefix (per instance_3_3.xsd); process uses ``prc``."""
    assert NAMESPACE_PREFIXES["pr"] == DDI_PROFILE_NS
    assert NAMESPACE_PREFIXES["prc"] == PROCESS_NS
    assert DDI_PROFILE_NS != PROCESS_NS
    # The named ddiprofile profile agrees with the global registry.
    assert get_namespace_profile(DDI_PROFILE_PROFILE)["pr"] == DDI_PROFILE_NS
    assert build_namespace_map("pr")["pr"] == DDI_PROFILE_NS
    assert build_namespace_map("prc")["prc"] == PROCESS_NS


def test_merge_namespace_profiles_combines_named_profiles():
    """Merge default and study unit profiles to ensure bindings combine."""
    bindings = merge_namespace_profiles(DDI_DEFAULT_PROFILE, DDI_STUDY_UNIT_PROFILE)
    assert bindings[None] == INSTANCE_NS
    assert bindings["r"] == REUSABLE_NS
    assert bindings["s"] == STUDY_UNIT_NS
    assert bindings["c"] == CONCEPTUAL_COMPONENT_NS


def test_merge_namespace_profiles_conflict_detection():
    """Conflicting bindings raise ValueError when overrides disabled."""
    with pytest.raises(ValueError):
        merge_namespace_profiles({"pr": "one"}, {"pr": "two"})


def test_merge_namespace_profiles_allow_override():
    """allow_override prefers later bindings and merges extra overrides."""
    bindings = merge_namespace_profiles(
        {"pr": "one"},
        {"pr": "two"},
        allow_override=True,
        overrides={"extra": "value"},
    )
    assert bindings["pr"] == "two"
    assert bindings["extra"] == "value"


def test_merge_namespace_profiles_overrides_parameter():
    """overrides parameter injects custom bindings into merged profile."""
    bindings = merge_namespace_profiles(DDI_PROFILE_PROFILE, overrides={"pr": "custom"})
    assert bindings["pr"] == "custom"
