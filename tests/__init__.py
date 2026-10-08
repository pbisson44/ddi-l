"""Test suite package."""

from pathlib import Path

PACKAGE_FIXTURES_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ddi_l"
    / "examples"
    / "tests"
    / "fixtures"
)

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "src" / "ddi_l" / "examples"

# Large fixtures that exist only to exercise the library, not to be read by
# users. `Canadian_Survey_on_Business_conditions.xml` is 8.5 MB -- more than
# half the installed package -- and was shipped inside `ddi_l/examples/` while
# being referenced solely by this suite and by `benchmarks/`. It lives here so
# it still travels in the sdist and still runs in CI, without every user
# downloading and storing it.
TEST_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
