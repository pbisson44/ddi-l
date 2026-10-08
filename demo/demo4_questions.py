#!/usr/bin/env python3
"""Demo 4: Questions and Data Collection.

This demo shows how to:
- Create questions with ``doc.add_question()``
- Use ``doc.add_item()`` to add instruments and other data collection types
- Wrap each question in a QuestionConstruct and order them in a Sequence
- Point the Instrument at that Sequence, so it administers something
- Build a study with questions linked to variables

An Instrument with a name and no ControlConstructReference is a
questionnaire that asks nothing. The flow is what makes it one.
Module 8 of the curriculum covers the fuller version, with branching.
"""

import os
from pathlib import Path

import ddi_l as ddi
from ddi_l.models.datacollection import Instrument, QuestionConstruct, Sequence
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
    """Run the questions and data collection demo."""
    print("=" * 60)
    print("Demo 4: Questions and Data Collection")
    print("=" * 60)

    # 1. Create study
    doc = ddi.new_study(title="Questions Demo", agency=AGENCY)

    # 2. Add questions
    print("\n1. Adding questions...")
    questions = [
        doc.add_question(text="What is your gender?", label="Gender question"),
        doc.add_question(text="What is your age?", label="Age question"),
        doc.add_question(text="Do you own your home?", label="Home ownership question"),
        doc.add_question(
            text="What is your household income?", label="Income question"
        ),
    ]
    q1, q2, q3, q4 = questions
    print(f"   Questions added: {len(doc.questions)}")

    # 3. Wrap each question in a construct and order them in a sequence
    #
    # A QuestionItem is the question; a QuestionConstruct is that question
    # placed in a questionnaire. The Sequence puts the constructs in order.
    print("\n2. Building the questionnaire flow...")
    constructs = [
        doc.add_item(
            QuestionConstruct,
            name=f"Ask {question.labels[0].text}",
            label=f"Ask {question.labels[0].text}",
            question_reference=question.to_reference(),
        )
        for question in questions
    ]
    flow = doc.add_item(
        Sequence,
        name="Main Flow",
        label="Main questionnaire flow",
        control_construct_references=[c.to_reference() for c in constructs],
    )
    print(f"   QuestionConstructs: {len(constructs)}")
    print(f"   Sequence: {flow.identifier}")

    # 4. Add an instrument, pointed at the flow it administers
    print("\n3. Adding instrument with add_item()...")
    inst = doc.add_item(
        Instrument, name="Household Survey CAWI", label="Household survey (CAWI)"
    )
    inst.control_construct_reference = flow.to_reference()
    print(f"   Instrument: {inst.identifier}")
    print(f"   Administers: {flow.identifier}")

    # 5. Add variables linked to questions
    print("\n4. Adding variables linked to questions...")
    doc.add_variable(name="Gender", question=q1, label="Gender of respondent")
    doc.add_variable(name="Age", question=q2, label="Age in years")
    doc.add_variable(name="Home Ownership", question=q3, label="Owns their home")
    doc.add_variable(
        name="Household Income", question=q4, label="Annual household income"
    )
    print(f"   Variables: {len(doc.variables)}")

    # 6. Show what we have
    print("\n5. Document summary:")
    print(f"   Questions:   {len(doc.questions)}")
    print(f"   Variables:   {len(doc.variables)}")
    print(f"   Instruments: {len(doc.items(Instrument))}")

    # 7. Find and display a specific question
    print("\n6. Finding question by identifier...")
    found = doc.find(q1.identifier)
    if found:
        print(f"   Found: {found.__class__.__name__} ({found.identifier})")

    # 8. Check the result
    print("\n7. Checking the result...")
    report = validate_document(doc.inner)
    print(f"   Schema issues: {len(report.schema_issues)}")
    print(f"   Lint findings: {len(report.lint_findings)}")

    # 9. Save
    output_path = _output_dir() / "demo4_questions.xml"
    print(f"\n8. Saving to: {output_path}")
    doc.save(output_path)
    print("   Done!")

    print("\n" + "=" * 60)
    print("Demo 4 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
