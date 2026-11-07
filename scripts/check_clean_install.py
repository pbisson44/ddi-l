"""Install the built wheel into a throwaway venv and exercise it for real.

This is the check that matters before a release. Asserting that files are
present in the archive is not enough: the schemas were once packaged as a
top-level ``schemas`` module that resolved only when the repository root
happened to be on ``sys.path``, so every validation path worked in the
repository and failed from an installed wheel. Validating a document here,
from a venv that has nothing but the wheel, is what catches that.

Run via ``make release-check``, or directly:

    python scripts/check_clean_install.py dist/
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

# Executed inside the throwaway venv, which has only the wheel installed.
SMOKE_TEST = """
from importlib import resources

import ddi_l as ddi

bundle = resources.files("ddi_l.schemas").joinpath("ddi")
assert bundle.is_dir(), bundle

doc = ddi.new_study(title="Release check", agency="example.org")
doc.add_variable(name="Age", question=doc.add_question(text="How old are you?"))

issues = doc.validate()
assert not issues, issues

examples = resources.files("ddi_l").joinpath("examples")
fixtures = examples.joinpath("tests", "fixtures")
assert examples.joinpath("Quality_of_Life.xml").is_file()
assert fixtures.joinpath("minimal_instance.xml").is_file()
assert fixtures.joinpath("invalid_instance_missing_id.xml").is_file()
# Test fixtures travel in the sdist, not the wheel.
assert not fixtures.joinpath("models").is_dir()

# The spec language needs no extra; reading a spec file does.
from ddi_l.spec import compile_condition

spec_files = resources.files("ddi_l.spec")
assert spec_files.joinpath("spec.schema.json").is_file()
assert spec_files.joinpath("examples", "pet-survey.spec.yaml").is_file()
compiled = compile_condition("Pets > 0", subjects={"Pets": "urn:ddi:example.org:p:1"})
assert compiled.fallback_reason is None, compiled

# Only ddi-l-native's stand-in is installed, so ddi-l reads XML with the
# standard library, as it does on a platform with no compiled wheel.
from importlib.metadata import version

from ddi_l import _etree

assert _etree.BACKEND == "stdlib", _etree.BACKEND
assert version("ddi-l-native") == version("ddi-l"), version("ddi-l-native")

print("clean install: schemas resolve, validate() clean, examples present")
"""


def main(argv: list[str]) -> int:
    """Install the wheel from ``argv``'s dist directory and smoke-test it."""
    dist_dir = Path(argv[1] if len(argv) > 1 else "dist")
    try:
        wheel_path = next(dist_dir.glob("ddi_l-*.whl")).resolve()
        stand_in = next(dist_dir.glob("ddi_l_native-*-py3-none-any.whl")).resolve()
    except StopIteration:
        print(
            f"No ddi-l or ddi-l-native stand-in wheel in {dist_dir}/", file=sys.stderr
        )
        return 1

    with tempfile.TemporaryDirectory() as tmp_dir:
        venv_dir = Path(tmp_dir) / "venv"
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

        scripts_dir = "Scripts" if (venv_dir / "Scripts").exists() else "bin"
        python_bin = venv_dir / scripts_dir / "python"

        subprocess.run(
            [python_bin, "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
            check=True,
        )
        # The stand-in first, so the index's compiled ddi-l-native (or its
        # absence, before a release) does not decide what this check runs.
        subprocess.run(
            [python_bin, "-m", "pip", "install", "--quiet", stand_in, wheel_path],
            check=True,
        )

        # Run from a directory that is not the repository, so nothing can be
        # satisfied by a stray path entry pointing back at the source tree.
        subprocess.run([python_bin, "-c", SMOKE_TEST], check=True, cwd=tmp_dir)

        subprocess.run([venv_dir / scripts_dir / "ddi", "--version"], check=True)

        # Without the spec extra, `ddi spec` says what to install.
        spec_run = subprocess.run(
            [venv_dir / scripts_dir / "ddi", "spec", "schema"],
            capture_output=True,
            text=True,
            check=False,
        )
        if spec_run.returncode != 1 or 'pip install "ddi-l[spec]"' not in (
            spec_run.stderr
        ):
            print(f"`ddi spec` without the extra: {spec_run!r}", file=sys.stderr)
            return 1

        stray = venv_dir / scripts_dir / "ddi-iterparse-bench"
        if stray.exists():
            print(
                f"{stray.name} must not be installed: benchmarks are not packaged",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
