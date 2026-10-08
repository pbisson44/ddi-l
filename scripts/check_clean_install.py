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

print("clean install: schemas resolve, validate() clean, examples present")
"""


def main(argv: list[str]) -> int:
    """Install the wheel from ``argv``'s dist directory and smoke-test it."""
    dist_dir = Path(argv[1] if len(argv) > 1 else "dist")
    try:
        wheel_path = next(dist_dir.glob("*.whl")).resolve()
    except StopIteration:
        print(f"No wheel found in {dist_dir}/", file=sys.stderr)
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
        subprocess.run(
            [python_bin, "-m", "pip", "install", "--quiet", wheel_path], check=True
        )

        # Run from a directory that is not the repository, so nothing can be
        # satisfied by a stray path entry pointing back at the source tree.
        subprocess.run([python_bin, "-c", SMOKE_TEST], check=True, cwd=tmp_dir)

        subprocess.run([venv_dir / scripts_dir / "ddi", "--version"], check=True)

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
