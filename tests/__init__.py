"""Test suite package."""

from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "src" / "ddi_l" / "examples"

# The two samples the CLI recipes run, so they ship in the wheel.
SAMPLES_DIR = EXAMPLES_DIR / "tests" / "fixtures"

# Every other fixture. They exist only to exercise the library, so they travel
# in the sdist but not the wheel.
TEST_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
