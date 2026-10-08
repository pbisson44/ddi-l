"""Unit tests for MaintainableBase version increment helpers."""

import pytest

from ddi_l.exceptions import ModelValidationError
from ddi_l.models.base import MaintainableBase


def test_increment_major_version_resets_lower_components() -> None:
    maintainable = MaintainableBase(version="1.2.3")

    maintainable.increment_major_version()

    assert maintainable.version == "2.0.0"


def test_increment_minor_version_extends_missing_segment() -> None:
    maintainable = MaintainableBase(version="1")

    maintainable.increment_minor_version()

    assert maintainable.version == "1.1"


def test_increment_minor_version_resets_lower_components() -> None:
    maintainable = MaintainableBase(version="3.4.5")

    maintainable.increment_minor_version()

    assert maintainable.version == "3.5.0"


def test_increment_subversion_adds_missing_segment() -> None:
    maintainable = MaintainableBase(version="0.9")

    maintainable.increment_subversion()

    assert maintainable.version == "0.9.1"


def test_increment_keeps_an_explicit_urn_in_step_with_the_version() -> None:
    """A URN read from a file ends with the version; a bump must not leave it
    naming the old one, in the item's r:URN or in its references."""
    maintainable = MaintainableBase(
        agency="example.org",
        identifier="q-1",
        version="1",
        urn="urn:ddi:example.org:q-1:1",
    )

    maintainable.increment_subversion()

    assert maintainable.urn == "urn:ddi:example.org:q-1:1.0.1"
    assert maintainable.to_reference().urn == "urn:ddi:example.org:q-1:1.0.1"


def test_increment_leaves_a_urn_without_the_version_suffix_alone() -> None:
    # ":11" ends with "1" but not with ":1", so it is not this version.
    maintainable = MaintainableBase(version="1", urn="urn:ddi:example.org:q-1:11")

    maintainable.increment_major_version()

    assert maintainable.version == "2"
    assert maintainable.urn == "urn:ddi:example.org:q-1:11"


@pytest.mark.parametrize(
    "method_name",
    [
        "increment_major_version",
        "increment_minor_version",
        "increment_subversion",
    ],
)
def test_increment_version_without_existing_value_raises(method_name: str) -> None:
    maintainable = MaintainableBase()

    with pytest.raises(ModelValidationError, match="does not have a version"):
        getattr(maintainable, method_name)()


def test_increment_version_with_non_numeric_segment_raises() -> None:
    maintainable = MaintainableBase(version="1.a.0")

    with pytest.raises(ModelValidationError, match="non-numeric segment"):
        maintainable.increment_minor_version()


@pytest.mark.parametrize("version", ["1", "1.0", "1.0.0", "2.1.3", "1.0.0.0.1"])
def test_validate_accepts_schema_conforming_versions(version: str) -> None:
    from ddi_l.models.logicalproduct import Variable

    Variable(agency="example.agency", identifier="v1", version=version).validate()


@pytest.mark.parametrize("version", ["invalid", "1.a.0", "1.", ".1", "v1.0", "1.0-rc1"])
def test_validate_rejects_versions_the_schema_would_reject(version: str) -> None:
    """Model validation must not bless what the XSD rejects.

    DDI 3.3 restricts ``r:VersionType`` to ``[0-9]+(\\.[0-9]+)*``.
    """
    from ddi_l.models.logicalproduct import Variable

    variable = Variable(agency="example.agency", identifier="v1", version=version)
    with pytest.raises(ModelValidationError, match="version"):
        variable.validate()
