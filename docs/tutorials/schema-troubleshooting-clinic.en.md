---
description: >-
  Practise diagnosing DDI schema validation errors from the CLI and Python,
  starting from deliberately broken files.
---

# Schema troubleshooting clinic

Practice diagnosing schema errors with the command line and the Python API.
Each exercise starts from a deliberately broken file: you read the error
output, then fix the file.

!!! note "Before you start"
    Install `ddi-l` with `pip install ddi-l`. The steps below use sample
    files that ship with the package. Run this once in Python to copy them into
    an `examples/` folder in your working directory:

    ```python
    import shutil
    from importlib.resources import files
    from pathlib import Path

    Path("examples").mkdir(exist_ok=True)
    for name in ("Quality_of_Life.xml", "example_instance.xml", "example_fragment.xml"):
        shutil.copy(files("ddi_l.examples") / name, "examples")
    ```

## 1. Trigger a failing validation

1. Run ``mkdir -p clinic`` to create a workspace that keeps the broken
   instance separate from the source samples.
2. Copy ``examples/Quality_of_Life.xml`` to ``clinic/broken-instance.xml``.
3. Remove a required attribute (for example the ``version`` on a
   ``StudyUnit``) using your editor.
4. Run ``ddi validate clinic/broken-instance.xml`` to list each issue with
   its message, line and XPath. Add ``--format json`` for a JSON array instead.
5. Note the XPath and message for the failing node.

## 2. Reproduce the error programmatically

1. Launch a Python session and validate the same file with the schema loader.
   Passing ``raise_error=False`` collects the full error list instead of raising
   on the first failure:

    ```python
    from ddi_l.schema_loader import validate

    errors = validate("clinic/broken-instance.xml", raise_error=False)
    for error in errors:
        print("message:", error.message)
        print("xpath:", error.xpath)
        print("line:", error.line)
        print("column:", error.column)
    ```

2. Compare the output to the CLI JSON structure. Both surfaces expose the same
   error metadata so you can choose whichever fits your tooling.

## 3. Connect findings to lint rules

1. Open ``docs/validation.md`` and identify which lint rules would catch similar
   mistakes (for example, missing agency identifiers).
2. Update your lint profile to include those rules by calling
   ``configure_lint()`` in a Python session or editing your team profile file.
3. Still in Python, execute ``run_profile`` against the broken instance to
   confirm the rule set surfaces the issue before the schema fails:

    ```python
    from ddi_l.io import read
    from ddi_l.lint import DDI_PROFILE_DEFAULT, configure_lint, run_profile

    configure_lint()  # optionally tighten agencies, citation rules, etc.
    document = read("clinic/broken-instance.xml")
    result = run_profile(document, DDI_PROFILE_DEFAULT)
    for finding in result.lint_findings:
        print(finding.rule_id, finding.message)
    ```

## 4. Establish a remediation checklist

- Ensure the failing node's namespace prefix is registered so schema lookups can
  resolve the element correctly.
- Restore required attributes and run ``ddi validate`` until the command reports
  ``Document is valid.``.
- Capture representative examples of the error and fix in your team's runbook so
  future incidents can be triaged faster.
