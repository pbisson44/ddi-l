#!/usr/bin/env python3
"""Demo 3: Variables, Code Lists, and Categories.

This demo shows how to use the generic ``add_item()`` API for
types beyond the basic five (questions, variables, concepts,
universes, code lists). It demonstrates:

- Using ``doc.add_item()`` for Category and RepresentedVariable
- Using ``doc.items()`` to query any registered type
- Using ``doc.find()`` and ``doc.remove()`` across all types
- Building code lists with the explicit ``add_code_list()`` method
- Putting Codes in a code list, each pointing at a Category
- Linking a Variable to its code list with ``set_coded()``

The linking is the point. A CodeList with no Codes is schema-valid
and says nothing -- validation cannot catch it, so a demo that stops
at "create the objects" teaches a file that looks like DDI and means
nothing.
"""

import os
from pathlib import Path

import ddi_l as ddi
from ddi_l.models.logicalproduct import Category, CodeItem, RepresentedVariable
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
    """Run the variables and code lists demo."""
    print("=" * 60)
    print("Demo 3: Variables, Code Lists, and Categories")
    print("=" * 60)

    # 1. Create document
    doc = ddi.new_study(title="Variables and Code Lists Demo", agency=AGENCY)

    # 2. Create categories using add_item()
    #
    # A Category is one allowed answer. On its own it is inert -- it becomes
    # meaningful when a Code in a code list points at it, which is step 3.
    print("\n1. Creating categories with add_item()...")
    male = doc.add_item(Category, name="Male", label="Male")
    female = doc.add_item(Category, name="Female", label="Female")
    cat_other = doc.add_item(
        Category, name="Not specified", label="Not specified"
    )  # removed later
    print(f"   Categories: {len(doc.items(Category))}")

    # 3. Create code lists, and put codes in them
    #
    # `add_code_list` creates the list; the codes are what make it useful.
    # Each Code carries the value that lands in the data and a reference to
    # the Category that says what the value means.
    print("\n2. Creating code lists...")
    gender_codes = doc.add_code_list(name="Gender Code List", label="Gender codes")
    gender_codes.codes = [
        CodeItem(
            agency=AGENCY,
            identifier=f"{gender_codes.identifier}-{value}",
            version=gender_codes.version,
            value=str(value),
            category=category.to_reference(),
        )
        for value, category in enumerate((male, female), start=1)
    ]
    age_groups = doc.add_code_list(name="Age Group Code List", label="Age group codes")
    print(f"   Code lists: {len(doc.code_lists)}")
    print(f"   Codes in '{gender_codes.names[0].text}': {len(gender_codes.codes)}")

    # 4. Create represented variables using add_item()
    print("\n3. Creating represented variables with add_item()...")
    gender_representation = doc.add_item(
        RepresentedVariable,
        name="Gender Representation",
        label="Gender representation",
    )
    print(f"   RepresentedVariables: {len(doc.items(RepresentedVariable))}")

    # 5. Create variables, and say what values they hold
    #
    # `set_coded()` writes the link into the document: the Variable gets a
    # CodeRepresentation pointing at the code list. Without it the variable
    # is a name, and the code list beside it is unreachable.
    print("\n4. Creating variables...")
    gender = doc.add_variable(name="Gender", label="Gender of respondent")
    gender.set_coded(gender_codes)
    gender.represented_variable_reference = gender_representation.to_reference()
    age_group = doc.add_variable(name="Age Group", label="Age group of respondent")
    age_group.set_coded(age_groups)
    print(f"   Variables: {len(doc.variables)}")

    # 6. Demonstrate find()
    print("\n5. Finding items by identifier...")
    found = doc.find(cat_other.identifier)
    print(f"   Found: {found.__class__.__name__} ({found.identifier})")

    # 7. Demonstrate remove()
    print("\n6. Removing 'Not specified' category...")
    doc.remove(cat_other.identifier)
    print(f"   Categories remaining: {len(doc.items(Category))}")

    # 8. Display structure
    print("\n7. Final document structure:")
    print(f"   Categories:          {len(doc.items(Category))}")
    print(f"   Code Lists:          {len(doc.code_lists)}")
    print(f"   RepresentedVars:     {len(doc.items(RepresentedVariable))}")
    print(f"   Variables:           {len(doc.variables)}")

    # 9. Check the links actually landed in the document
    print("\n8. Checking the result...")
    report = validate_document(doc.inner)
    print(f"   Schema issues: {len(report.schema_issues)}")
    print(f"   Lint findings: {len(report.lint_findings)}")

    # 10. Save
    output_path = _output_dir() / "demo3_variables.xml"
    print(f"\n9. Saving to: {output_path}")
    doc.save(output_path)
    print("   Done!")

    print("\n" + "=" * 60)
    print("Demo 3 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
