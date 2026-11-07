"""Marks shared by several test modules."""

from __future__ import annotations

import pytest

#: The test's items refer to items its document does not hold (a study's
#: data collection kept elsewhere, a lone item read from a fixture), so
#: serializing them raises `DDIReferenceWarning`. Any other test fails on that
#: warning (see ``filterwarnings`` in pyproject.toml).
refers_outside = pytest.mark.filterwarnings(
    "ignore::ddi_l.exceptions.DDIReferenceWarning"
)
