#!/usr/bin/env python3
"""Demo 2: Working with StudyUnits.

This demo shows how to:
- Create a study with metadata using ``ddi.new_study()``
- Add multiple questions and variables
- Link variables to questions via references
- Add concepts and universes
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
    """Run the StudyUnit demo."""
    print("=" * 60)
    print("Demo 2: Working with StudyUnits")
    print("=" * 60)

    # 1. Create document with a study
    print("\n1. Creating study...")
    doc = ddi.new_study(title="Household Survey", agency=AGENCY)

    # 2. Add concepts and a universe
    #
    # The universe says who the study is about. Creating one is half the job:
    # unless something references it, a reader of the file cannot tell who was
    # surveyed. Step 4 attaches it to the study and to each variable.
    print("\n2. Adding conceptual content...")
    gender_concept = doc.add_concept(name="Gender", label="Gender")
    age_concept = doc.add_concept(name="Age", label="Age")
    income_concept = doc.add_concept(name="Household income", label="Household income")
    adults = doc.add_universe(
        name="Canadian adults aged 18+", label="Canadian adults aged 18+"
    )
    print(f"   Concepts: {len(doc.concepts)}")
    print(f"   Universes: {len(doc.universes)}")

    # 3. Add questions
    print("\n3. Adding questions...")
    q_gender = doc.add_question(text="What is your gender?", label="Gender question")
    q_age = doc.add_question(text="What is your age?", label="Age question")
    q_income = doc.add_question(
        text="What is your household income?", label="Income question"
    )
    print(f"   Questions: {len(doc.questions)}")

    # 4. Add variables linked to questions, concepts and the universe
    print("\n4. Adding variables...")
    variables = [
        doc.add_variable(
            name="Gender",
            question=q_gender,
            concept=gender_concept,
            label="Gender of respondent",
        ),
        doc.add_variable(
            name="Age", question=q_age, concept=age_concept, label="Age in years"
        ),
        doc.add_variable(
            name="Household Income",
            question=q_income,
            concept=income_concept,
            label="Annual household income",
        ),
    ]
    # Point the study, and every variable in it, at the population it covers.
    doc.study_unit.universe_references.append(adults.to_reference())
    for variable in variables:
        variable.universe_references.append(adults.to_reference())
    print(f"   Variables: {len(doc.variables)}")

    # 5. Show summary
    print("\n5. Document summary:")
    print(f"   Agency:    {doc.agency}")
    print(f"   Questions: {len(doc.questions)}")
    print(f"   Variables: {len(doc.variables)}")
    print(f"   Concepts:  {len(doc.concepts)}")
    print(f"   Universes: {len(doc.universes)}")

    # 6. Check the result
    print("\n6. Checking the result...")
    report = validate_document(doc.inner)
    print(f"   Schema issues: {len(report.schema_issues)}")
    print(f"   Lint findings: {len(report.lint_findings)}")

    # 7. Save
    output_path = _output_dir() / "demo2_study_unit.xml"
    print(f"\n7. Saving to: {output_path}")
    doc.save(output_path)
    print("   Done!")

    print("\n" + "=" * 60)
    print("Demo 2 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
