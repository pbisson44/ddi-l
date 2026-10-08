"""Write a DDI instance back to disk with ``ddi_l.write``."""

from __future__ import annotations

import argparse
import sys
from importlib import resources
from pathlib import Path

# Ensure the package is importable without installing the project.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
for path in (SRC_PATH, PROJECT_ROOT):
    stringified = str(path)
    if stringified not in sys.path:
        sys.path.insert(0, stringified)

from ddi_l import read_ddi, write_ddi

EXAMPLES_ROOT = resources.files("ddi_l").joinpath("examples")
EXAMPLE_RESOURCE = EXAMPLES_ROOT.joinpath("tests", "fixtures", "minimal_instance.xml")


def main() -> None:
    """Copy the bundled instance to ``destination`` using ``write``."""

    # Allow callers to override the default destination on the command line.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        default=Path.cwd() / "quality_of_life_copy.xml",
        help="Where to write the serialized XML document.",
    )
    args = parser.parse_args()

    with resources.as_file(EXAMPLE_RESOURCE) as example_path:
        print(f"Loading {example_path}")
        # Validate on read so the serialized output is backed by a compliant model.
        document = read_ddi(example_path, validate=True)
    destination = args.destination
    # Create the output directory so ``write`` does not fail on missing parents.
    destination.parent.mkdir(parents=True, exist_ok=True)

    write_ddi(document, destination)
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()
