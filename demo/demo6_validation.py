#!/usr/bin/env python
"""Demo 6: Validation and Schema Compliance.

This demo shows how to validate DDI documents against the DDI-L schema
and handle validation errors.

Topics covered:
- Schema validation using ``doc.validate()``
- What a schema violation looks like when the XSD rejects one
- Model-level validation
- Validation during document loading
- High-level validation with ``validate_document()``, and how it differs
  from ``doc.validate()``
"""

import os
from pathlib import Path
from uuid import uuid4

import ddi_l as ddi
from ddi_l.exceptions import DDIValidationError, ModelValidationError
from ddi_l.models.base import InternationalString
from ddi_l.models.logicalproduct import Variable
from ddi_l.validation import validate_document

AGENCY = "demo.org"
VERSION = "1.0"


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


def _reorder_variable_name(xml: str) -> str:
    """Move ``l:VariableName`` after ``r:QuestionReference``, breaking the order.

    Every element is still well-formed and correctly spelled; only the sequence
    is wrong, which is exactly the class of mistake hand-editing DDI produces
    and reading it back rarely reveals.
    """
    start = xml.index("<l:VariableName>")
    end = xml.index("</l:VariableName>") + len("</l:VariableName>")
    name_block = xml[start:end]
    without_name = xml[:start] + xml[end:]
    anchor = "</r:QuestionReference>"
    insert_at = without_name.index(anchor) + len(anchor)
    return without_name[:insert_at] + name_block + without_name[insert_at:]


def main():
    print("=" * 60)
    print("Demo 6: Validation and Schema Compliance")
    print("=" * 60)

    # 1. Create a valid document using the simple API
    print("\n1. Creating a valid DDI document...")
    doc = ddi.new_study(title="Validation Demo", agency=AGENCY, version=VERSION)
    q = doc.add_question(text="How old are you?", label="Age question")
    doc.add_variable(name="Age", question=q, label="Age in years")
    print(f"   Questions: {len(doc.questions)}, Variables: {len(doc.variables)}")

    # 2. Validate using doc.validate()
    #
    # `doc.validate()` checks the document against the DDI XSD and nothing
    # else. It needs no extra install: xmlschema is a hard dependency and the
    # 3.1/3.2/3.3 schemas ship inside the package, so this works offline.
    print("\n2. Validating with doc.validate()...")
    issues = doc.validate()
    if issues:
        print(f"   {len(issues)} issue(s) found:")
        for issue in issues[:3]:
            print(f"      [{issue.severity}] {issue.message}")
    else:
        print("   No issues — document is valid!")

    # 2b. What a schema violation actually looks like
    #
    # The interesting case. DDI element order is fixed by the XSD, so moving
    # l:VariableName after r:QuestionReference makes the document invalid even
    # though every piece of it is individually fine. This is the failure the
    # schema exists to catch, and the one worth recognizing on sight.
    print("\n3. Catching a schema violation...")
    valid_xml = doc.to_xml()
    broken_xml = _reorder_variable_name(valid_xml)
    for issue in validate_document(broken_xml).schema_issues:
        print(f"   [{issue.severity}] {issue.message}")
        print(f"      at: {issue.xpath}")

    # 4. Model-level validation
    print("\n4. Model-level validation:")

    print("   Testing valid Variable...")
    valid_var = Variable(
        agency=AGENCY,
        identifier=str(uuid4()),
        version=VERSION,
        labels=[InternationalString(text="A valid variable", lang="en")],
    )
    try:
        valid_var.validate()
        print("   Variable validation passed!")
    except ModelValidationError as e:
        print(f"   Validation failed: {e}")

    print("\n   Testing Variable with missing fields...")
    try:
        invalid_var = Variable(agency=None, identifier=None, version=VERSION)
        invalid_var.validate()
        print("   Validation passed (unexpected)")
    except ModelValidationError as e:
        print(f"   Validation failed (expected): {e}")
    except Exception as e:
        print(f"   Other error: {type(e).__name__}: {e}")

    # 5. Save and reload with validation
    print("\n5. Round-trip with validation:")
    output_dir = _output_dir()
    valid_file = output_dir / "demo6_valid.xml"
    doc.save(valid_file)
    print(f"   Saved to: {valid_file}")

    print("   Reading with validation enabled...")
    try:
        doc2 = ddi.open_ddi(valid_file, validate=True)
        print(f"   Loaded successfully! Questions: {len(doc2.questions)}")
    except DDIValidationError as e:
        print(f"   Validation error: {e}")
    except Exception as e:
        print(f"   Note: {type(e).__name__}: {str(e)[:80]}...")

    # 6. High-level validation function
    #
    # Step 2 said "valid" and this may report findings: they are asking
    # different questions. `doc.validate()` is schema-only, while
    # `validate_document()` runs the schema *and* the linter, which checks
    # house rules the XSD has no opinion about. Findings here are warnings;
    # only errors make a document invalid.
    print("\n6. Using high-level validation:")
    report = validate_document(doc.inner)
    print(f"   Schema issues: {len(report.schema_issues)}")
    print(f"   Lint findings: {len(report.lint_findings)}")
    for finding in report.lint_findings:
        print(f"      [{finding.severity}] {finding.rule_id} at {finding.location}")

    if report.has_errors():
        print("   Document has errors!")
    elif report.has_warnings():
        print("   Document has warnings")
    else:
        print("   No issues found!")

    # 7. Version format validation
    #
    # '1.0.0.0.1' is valid, which surprises people expecting semver. DDI's
    # VersionType is `[0-9]+(\.[0-9]+)*` and its documentation is explicit:
    # a version "can contain as many levels as needed by the agency".
    print("\n7. Version format validation:")
    test_versions = ["1.0", "1.0.0", "2.1.3", "invalid", "1.0.0.0.1"]
    for version in test_versions:
        test_var = Variable(agency=AGENCY, identifier=str(uuid4()), version=version)
        try:
            test_var.validate()
            print(f"   '{version}': Valid")
        except ModelValidationError as e:
            print(f"   '{version}': Invalid - {e}")

    print("\n" + "=" * 60)
    print("Demo 6 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
