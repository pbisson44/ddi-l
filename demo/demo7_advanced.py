#!/usr/bin/env python3
"""Demo 7: Advanced Features.

This demo shows how to:
- Work with References between maintainables
- Use the advanced model layer for complex structures
- Build code lists with Codes, each pointing at a Category
- Link a Variable to its code list with ``set_coded()``
- Use version management features
- Run referential integrity lint rules

Note what the integrity check in step 6 can and cannot tell you: it
verifies that every reference *resolves*, so it catches a pointer to a
missing object but not an object nobody points at. A code list with no
codes passes it comfortably and still says nothing.
"""

import os
from pathlib import Path
from uuid import uuid4

import ddi_l as ddi
from ddi_l.document import DDIDocument
from ddi_l.lint import run_lint
from ddi_l.models import (
    InternationalString,
    Reference,
)
from ddi_l.models.logicalproduct import Category, CodeItem

AGENCY = "demo.org"
VERSION = "1.0"


def _bilingual(en: str, fr: str) -> list[InternationalString]:
    return [
        InternationalString(text=en, lang="en-CA"),
        InternationalString(text=fr, lang="fr-CA"),
    ]


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
    """Run the advanced features demo."""
    print("=" * 60)
    print("Demo 7: Advanced Features")
    print("=" * 60)

    # 1. Create a study using the simple API (avoids validation issues)
    doc = ddi.new_study(title="Advanced Features Demo", agency=AGENCY)

    # 2. Working with References
    #
    # A Reference is built by hand here to show its parts. `to_reference()` on
    # any maintainable does the same thing and is what you would normally use.
    print("\n1. Working with References:")
    age_concept = doc.add_concept(name="Age", label="Age")
    concept_ref = Reference(
        agency=age_concept.agency,
        identifier=age_concept.identifier,
        version=age_concept.version,
        type_of_object="Concept",
    )
    print(f"   Created concept: {age_concept.identifier[:8]}...")
    print(f"   Reference type: {concept_ref.type_of_object}")
    print(f"   Same as to_reference(): {concept_ref == age_concept.to_reference()}")

    # 3. Code lists with categories using add_item()
    print("\n2. Creating categories and code list:")
    categories = [
        doc.add_item(Category, name=name, label=name)
        for name in ("Male", "Female", "Not specified")
    ]

    # The variable below is about gender, so give it a gender concept to point at.
    gender_concept = doc.add_concept(name="Gender", label="Gender")
    cl = doc.add_code_list(name="Gender Codes", label="Gender codes")
    # A code list with no codes is schema-valid and says nothing: the
    # integrity check in step 6 cannot flag what is absent, only what fails to
    # resolve. Each Code carries the stored value and points at the Category
    # that gives it meaning, so the chain actually leads somewhere.
    cl.codes = [
        CodeItem(
            agency=AGENCY,
            identifier=f"{cl.identifier}-{value}",
            version=cl.version,
            value=str(value),
            category=category.to_reference(),
        )
        for value, category in enumerate(categories, start=1)
    ]
    print(f"   Categories: {len(doc.items(Category))}")
    print(f"   Code list: {cl.identifier[:8]}... ({len(cl.codes)} codes)")

    # 4. Create a variable with CodeRepresentation (advanced model layer)
    print("\n3. Creating variable linked to code list:")
    # `set_coded()` writes the code-list link into the document.
    gender_var = doc.add_variable(
        name="Gender", concept=gender_concept, label="Gender of respondent"
    )
    gender_var.set_coded(cl)
    print(f"   Variable: {gender_var.identifier[:8]}...")
    print(f"   Links to code list: {cl.identifier[:8]}...")

    # The Age concept from step 1 is now put to use, so nothing in the saved
    # file is created and then referenced by nobody.
    age_var = doc.add_variable(
        name="Age", concept=age_concept, label="Age in years", lang="en-CA"
    )
    age_var.names.append(InternationalString(text="Âge", lang="fr-CA"))
    age_var.labels.append(InternationalString(text="Âge en années", lang="fr-CA"))
    age_var.set_numeric("Integer", low=0, high=120)
    print(f"   Bilingual variable: {age_var.identifier[:8]}...")

    # 5. Version management: each variable is added to the saved document.
    print("\n4. Version patterns:")
    versions = ["1.0", "1.0.1", "2.0", "2.1.0"]
    for ver in versions:
        var = doc.add_variable(
            name=f"Variable v{ver}",
            label=f"Variable v{ver}",
            identifier=str(uuid4()),
        )
        var.names = _bilingual(f"Variable v{ver}", f"Variable v{ver}")
        var.version = ver
        print(f"   Created variable version: {var.version}")

    # 6. Serialize and save
    print("\n5. Saving document...")
    output_dir = _output_dir()
    output_path = output_dir / "demo7_advanced.xml"
    doc.save(output_path)
    print(f"   Saved to: {output_path}")

    # 7. Verify referential integrity
    print("\n6. Checking referential integrity...")
    doc_check = DDIDocument.from_xml(output_path)
    findings = run_lint(doc_check, rules=["ddi.reference.integrity"])
    if findings:
        for f in findings:
            print(f"   [{f.severity}] {f.message}")
    else:
        print("   All references resolve correctly!")

    # 8. Reference information
    #
    # Read the URN off each object with the public `canonical_urn()`, rather
    # than rebuilding the string from its parts: what gets reported is then
    # the URN actually serialized into the document, not one reconstructed
    # from the same inputs and hoped to match.
    print("\n7. Reference information:")
    print(f"   Concept URN:  {age_concept.canonical_urn()}")
    print(f"   CodeList URN: {cl.canonical_urn()}")

    # 9. Summary
    print("\n8. Summary of advanced features demonstrated:")
    print("   - Creating and using References between maintainables")
    print("   - Using add_item() for categories")
    print("   - Linking Variables to concepts via references")
    print("   - Version management with semantic versioning")
    print("   - Referential integrity validation via lint rules")

    print("\n" + "=" * 60)
    print("Demo 7 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
