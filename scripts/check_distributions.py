"""Verify the built sdist and wheel carry everything the package needs.

Run via ``make release-check``, which builds the distributions first.

This lives in a script rather than inline in the Makefile because make runs
each recipe line in its own shell, which splits a multi-line heredoc across
shells; the previous inline version could not run at all. Keeping it here also
means the checks can be run directly:

    python scripts/check_distributions.py dist/
"""

from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

# Paths that must be present in the sdist, which mirrors the repository layout.
REQUIRED_SDIST_PATHS = (
    "src/ddi_l/schemas/ddi/v3_1/instance_3_1.xsd",
    "src/ddi_l/schemas/ddi/v3_2/instance_3_2.xsd",
    "src/ddi_l/schemas/ddi/v3_3/instance_3_3.xsd",
    "src/ddi_l/schemas/readme.txt",
    "src/ddi_l/schemas/license.txt",
    "src/ddi_l/examples/Quality_of_Life.xml",
    "src/ddi_l/examples/tests/fixtures/minimal_instance.xml",
    # A redistributor building from the sdist expects to be able to run the
    # suite, and the file we ask people to cite by has to travel with the
    # software it describes. poetry-core ships only the package by default, so
    # these come from the [tool.poetry] include list in pyproject.toml.
    "tests/test_packaged_examples.py",
    "scripts/check_distributions.py",
    # tests/test_roundtrip_fidelity.py imports this at module scope.
    "codegen/coverage_audit.py",
    "Makefile",
    "uv.lock",
    "CHANGELOG.md",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
)

# Paths that must be present in the wheel, which is rooted at the package.
REQUIRED_WHEEL_PATHS = (
    ("ddi_l", "schemas", "ddi", "v3_1", "instance_3_1.xsd"),
    ("ddi_l", "schemas", "ddi", "v3_2", "instance_3_2.xsd"),
    ("ddi_l", "schemas", "ddi", "v3_3", "instance_3_3.xsd"),
    ("ddi_l", "schemas", "ddi", "v3_3", "dataset.xsd"),
    ("ddi_l", "schemas", "readme.txt"),
    ("ddi_l", "schemas", "license.txt"),
    ("ddi_l", "examples", "Quality_of_Life.xml"),
    ("ddi_l", "examples", "tests", "fixtures", "minimal_instance.xml"),
    ("ddi_l", "py.typed"),
)


def check_sdist(path: Path) -> list[str]:
    """Return the required sdist paths that are missing from ``path``."""
    with tarfile.open(path) as archive:
        names = {name.split("/", 1)[-1] for name in archive.getnames()}
    return [required for required in REQUIRED_SDIST_PATHS if required not in names]


def check_sdist_suite_collects(path: Path) -> list[str]:
    """Return problems found collecting the test suite inside the sdist.

    Asserting that a few test *files* are present says nothing about whether the
    suite can start. It could not: `tests/test_roundtrip_fidelity.py` imports
    `codegen` at module scope, and `codegen/` was not shipped, so `pytest`
    aborted during collection before running anything. A redistributor building
    from the tarball -- which is the documented reason those files are included
    at all -- would have hit that immediately.

    Collection is the right depth of check here. Running the suite needs the dev
    dependency group and several minutes; collecting it exercises every
    module-scope import and every skip guard for the cost of a subprocess.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with tarfile.open(path) as archive:
            archive.extractall(root, filter="data")

        unpacked = next((p for p in root.iterdir() if p.is_dir()), None)
        if unpacked is None:
            return ["sdist unpacked to nothing"]

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "--no-cov"],
            cwd=unpacked,
            capture_output=True,
            text=True,
        )
        # Exit code 5 is "no tests collected", which is not what this guards
        # against and would be a legitimate outcome if every guard skipped.
        if result.returncode not in (0, 5):
            tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-12:])
            return [f"test suite does not collect from the sdist:\n{tail}"]

    return []


def check_wheel(path: Path) -> list[str]:
    """Return the problems found in the built wheel at ``path``."""
    problems: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        root = zipfile.Path(archive)

        missing = [
            "/".join(parts)
            for parts in REQUIRED_WHEEL_PATHS
            if not root.joinpath(*parts).exists()
        ]
        if missing:
            problems.append(f"missing from wheel: {', '.join(missing)}")

        # Only ddi_l may claim a top-level import name. A stray `lxml`,
        # `schemas`, `tests`, or `benchmarks` package would shadow or pollute
        # every environment that installs this wheel.
        tops = {name.split("/")[0] for name in names}
        unexpected = sorted(
            top for top in tops if top != "ddi_l" and not top.endswith(".dist-info")
        )
        if unexpected:
            problems.append(f"unexpected top-level entries: {', '.join(unexpected)}")

        if not any(name.endswith(".xsd") for name in names):
            problems.append("no .xsd files in wheel: offline validation would fail")

    return problems


def main(argv: list[str]) -> int:
    """Check the distributions in the directory named by ``argv``."""
    dist_dir = Path(argv[1] if len(argv) > 1 else "dist")

    try:
        sdist_path = next(dist_dir.glob("*.tar.gz"))
        wheel_path = next(dist_dir.glob("*.whl"))
    except StopIteration:
        print(f"No sdist/wheel found in {dist_dir}/", file=sys.stderr)
        return 1

    problems = [f"sdist: {name}" for name in check_sdist(sdist_path)]
    problems += [
        f"sdist: {problem}" for problem in check_sdist_suite_collects(sdist_path)
    ]
    problems += [f"wheel: {problem}" for problem in check_wheel(wheel_path)]

    if problems:
        print("Distribution checks failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"{sdist_path.name}: OK")
    print(f"{wheel_path.name}: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
