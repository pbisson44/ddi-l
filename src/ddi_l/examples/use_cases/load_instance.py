"""Load and inspect the bundled minimal DDI instance."""

from __future__ import annotations

import sys
from importlib import resources
from pathlib import Path

# Resolve paths so ``ddi_l`` can be imported when the script is executed in-place.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
for path in (SRC_PATH, PROJECT_ROOT):
    stringified = str(path)
    if stringified not in sys.path:
        sys.path.insert(0, stringified)

from ddi_l import read_ddi
from ddi_l.constants import REUSABLE_NS
from ddi_l.models.base import qn

EXAMPLES_ROOT = resources.files("ddi_l").joinpath("examples")
EXAMPLE_RESOURCE = EXAMPLES_ROOT.joinpath("tests", "fixtures", "minimal_instance.xml")


def main() -> None:
    """Parse the example instance and print basic identification details."""

    # ``validate=True`` provides schema safety and mirrors production defaults.
    with resources.as_file(EXAMPLE_RESOURCE) as example_path:
        document = read_ddi(example_path, validate=True)
        print(f"Loaded document from {example_path}")

    identification = document.get_identification()
    print("\nInstance identification:")
    for key, value in identification.items():
        print(f"  {key}: {value}")

    citation_title: str | None = None
    # Traverse the reusable namespace to locate a human-friendly title, if any.
    citation = document.root.find(qn(REUSABLE_NS, "Citation"))
    if citation is not None:
        title_element = citation.find(qn(REUSABLE_NS, "Title"))
        if title_element is not None:
            string_element = title_element.find(qn(REUSABLE_NS, "String"))
            if string_element is not None:
                citation_title = string_element.text

    print("\nCitation title:")
    print(f"  {citation_title or 'No title present'}")


if __name__ == "__main__":
    main()
