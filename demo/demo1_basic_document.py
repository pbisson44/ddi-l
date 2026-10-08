#!/usr/bin/env python
"""Demo 1: Basic DDI Document Creation.

This demo shows how to create a simple DDI-L document using
the high-level ``ddi_l`` API.

Topics covered:
- Creating a new study with ``ddi.new_study()``
- Adding questions and variables
- Serializing to XML
- Saving and re-opening
"""

import os
from pathlib import Path

import ddi_l as ddi
from ddi_l.validation import validate_document

AGENCY = "demo.org"


def _output_dir() -> Path:
    """Return the directory demo artifacts are written to.

    Defaults to ``demo/output/`` so running a demo by hand leaves its result
    next to the script. Tests set ``DDI_DEMO_OUTPUT_DIR`` to a temporary path
    so a test run never modifies tracked files.
    """
    override = os.environ.get("DDI_DEMO_OUTPUT_DIR")
    path = Path(override) if override else Path(__file__).parent / "output"
    path.mkdir(parents=True, exist_ok=True)
    return path


def main():
    print("=" * 60)
    print("Demo 1: Basic DDI Document Creation")
    print("=" * 60)

    # 1. Create a new study document (identifier is auto-generated)
    print("\n1. Creating new study...")
    doc = ddi.new_study(title="ddi-l demo study", agency=AGENCY)
    print(f"   Agency: {doc.agency}")

    # 2. Add a question and a variable
    #
    # `label=` is worth the few extra characters: `ddi lint` reports every
    # maintainable without one, so a document built without labels arrives
    # warning about itself. `set_numeric` says what the variable holds --
    # without a representation, "Age" is a name with no values behind it.
    print("\n2. Adding content...")
    q = doc.add_question(text="What is your age?", label="Age question")
    v = doc.add_variable(name="Age", question=q, label="Age in years")
    v.set_numeric("Integer", low=0, high=120)
    print(f"   Question: {q.identifier}")
    print(f"   Variable: {v.identifier}")

    # 3. Show generated XML (first 1500 chars)
    print("\n3. Generated XML (first 1500 chars):")
    xml_output = doc.to_xml(pretty_print=True)
    print(xml_output[:1500] + "..." if len(xml_output) > 1500 else xml_output)

    # 4. Save to file
    output_path = _output_dir() / "demo1_basic_document.xml"
    print(f"\n4. Saving to: {output_path}")
    doc.save(output_path)
    print("   Done!")

    # 5. Re-open the saved document
    print("\n5. Re-opening the saved document...")
    doc2 = ddi.open_ddi(output_path)
    print(f"   Questions: {len(doc2.questions)}")
    print(f"   Variables: {len(doc2.variables)}")

    # 6. Check it against the tools that ship with the library
    print("\n6. Checking the result...")
    report = validate_document(doc.inner)
    print(f"   Schema issues: {len(report.schema_issues)}")
    print(f"   Lint findings: {len(report.lint_findings)}")

    print("\n" + "=" * 60)
    print("Demo 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
