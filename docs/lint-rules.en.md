---
description: >-
  Every ddi-l lint rule, generated from the rule registry: what it reports,
  its severity, the profiles that run it, and an example finding.
---

# Lint rule reference

`ddi lint` and `ddi_l.lint.run_lint()` check a document against lint rules,
grouped in profiles. This page is generated from the rule registry, so it
lists every rule the installed version has, with an example of what each one
reports.

Run the default profile, a named profile, or chosen rules:

```bash
ddi lint study.xml
ddi lint export.xml --profile colectica-questionnaire --format table
ddi lint export.xml --rules colectica.condition.empty,text.pipe-malformed
ddi lint --list-rules --list-format table
```

A finding is an `error`, a `warning` or `info`. Only errors make `ddi lint`
exit non-zero, unless `--fail-severity warning` or `--fail-severity info`
asks for a stricter gate. Skip a rule with `--skip-rule RULE`.

## Configure the rules

Rules marked *heuristic* guess at intent from wording or layout, and report a
warning at most. Some rules depend on conventions that vary from one
organisation to the next; their options start empty, so the rule does nothing
until you configure it.

| Option | Used by | Default |
| --- | --- | --- |
| `required_languages` | `i18n.missing-language` | none: the rule is off |
| `placeholder_patterns` | `text.placeholder-unresolved` | `‹‹…››`, `<<…>>`, `«insert…»`, `[insert …]`, "insert survey-specific" |
| `ui_chrome_tokens` | `text.ui-chrome` | none: the rule is off |
| `logic_note_patterns` | `colectica.statement.logic-note` | "Flow condition", "Display condition", "Logic:" and their French equivalents |
| `gate_description_patterns` | `colectica.ifthenelse.partial-gate` | "go to … page", "aller à la page", "passer à la page" |
| `known_names` | `text.pipe-undeclared` | none |
| `variable_code_pattern` | `colectica.domain.label-mismatch` | none: the rule is off |
| `pipe_prefixes` | `text.pipe-malformed` | none |
| `pipe_suffixes` | `text.pipe-undeclared` | none |

From the command line, `--required-language` (repeated) and `--known-names
FILE` (one name per line) set the first two that most projects need, and
`--lint-config FILE` sets any option from a JSON object:

```json
{
  "required_languages": ["en-CA", "fr-CA"],
  "ui_chrome_tokens": ["Previous", "Next", "Save and finish later"],
  "variable_code_pattern": "Q\\d{3}",
  "pipe_suffixes": ["_E", "_F"]
}
```

In Python, `lint_configuration()` takes the same options and gives a
configuration for one call, leaving every other call as it was:

```python
from ddi_l import read_ddi
from ddi_l.lint import lint_configuration, run_lint

document = read_ddi("my-study.xml")
bilingual = lint_configuration(required_languages=["en-CA", "fr-CA"])
findings = run_lint(document, configuration=bilingual)
```

`run_profile()`, `document.lint()` and the `validate_*()` functions take it
too. `configure_lint()` sets the same options as the default for every call
in the process that is not given one.

<!-- lint-rules -->
