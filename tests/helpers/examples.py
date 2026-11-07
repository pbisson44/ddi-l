"""How many examples a property test draws.

A property test that matters draws 300 examples. Under mutation testing
(mutmut sets ``MUTANT_UNDER_TEST``) each test runs once for every mutant it
covers, so it draws at most `MUTATION_EXAMPLES`, and the same ones on every
run (see ``tests/conftest.py``): a mutant is caught on every run or on none.
"""

from __future__ import annotations

import os

from hypothesis import HealthCheck, settings

UNDER_MUTATION = "MUTANT_UNDER_TEST" in os.environ
MUTATION_EXAMPLES = 30


def examples(count: int, *, under_mutation: int = MUTATION_EXAMPLES) -> settings:
    """Settings for a property test drawing ``count`` examples.

    ``under_mutation`` is what it draws under mutation testing: more for an
    oracle whose rare cases only many examples reach.
    """
    return settings(
        max_examples=min(count, under_mutation) if UNDER_MUTATION else count,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow],
    )
