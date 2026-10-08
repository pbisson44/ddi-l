"""Validate a DDI instance and display any schema or lint findings."""

from __future__ import annotations

import sys
from importlib import resources
from pathlib import Path

# Add the project directories so the example works without installation.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
for path in (SRC_PATH, PROJECT_ROOT):
    stringified = str(path)
    if stringified not in sys.path:
        sys.path.insert(0, stringified)

from ddi_l import validation

EXAMPLES_ROOT = resources.files("ddi_l").joinpath("examples")
EXAMPLE_RESOURCE = EXAMPLES_ROOT.joinpath("tests", "fixtures", "minimal_instance.xml")


def main() -> None:
    """Validate the bundled instance and print a concise summary."""

    with resources.as_file(EXAMPLE_RESOURCE) as example_path:
        print(f"Validating {example_path}")
        # ``validate_document`` returns a rich report we can inspect programmatically.
        report = validation.validate_document(example_path)

    if not report.schema_issues and not report.lint_findings:
        print("Document is schema compliant and lint clean.")
        return

    print("Schema issues:")
    if report.schema_issues:
        for issue in report.schema_issues:
            print(f"  [{issue.severity}] {issue.message} (xpath={issue.xpath})")
    else:
        print("  None")

    print("\nLint findings:")
    if report.lint_findings:
        for finding in report.lint_findings:
            print(f"  [{finding.severity}] {finding.message} (rule={finding.rule_id})")
    else:
        print("  None")


if __name__ == "__main__":
    main()
