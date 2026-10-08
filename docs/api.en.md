# API reference

Generated from the docstrings in the source.

This page covers the **public API**: what `import ddi_l` exposes and what
semantic versioning applies to. For the wider model layer, see
[Models reference](models.md) for the guided tour and
[Schema coverage](schema-coverage.md) for what is supported at which level.

!!! info "Where to start"
    `new_study()` and `open_ddi()` return a [`Document`][ddi_l.document.Document],
    which is the front door. `DDIDocument`, `DDIFragment` and `StudyCursor` are
    the advanced layer underneath it. Reach for them when you need to work with
    raw elements, partial instances, or a specific study in a multi-study file.

## Creating and opening documents

::: ddi_l.document.new_study

::: ddi_l.document.open_ddi

## Document

::: ddi_l.document.Document
    options:
      members_order: source
      show_root_heading: true
      heading_level: 3

## StudyCursor

::: ddi_l.document.StudyCursor
    options:
      members_order: source
      show_root_heading: true
      heading_level: 3

## Reading and writing

::: ddi_l.io.read_ddi

::: ddi_l.io.write_ddi

::: ddi_l.io.iterparse_ddi

::: ddi_l.io.iter_variables

::: ddi_l.io.iter_questions

## Validation

::: ddi_l.validation.validate_document

::: ddi_l.validation.validate_fragment

::: ddi_l.validation.ValidationReport
    options:
      show_root_heading: true
      heading_level: 3

::: ddi_l.validation.ValidationMessage
    options:
      show_root_heading: true
      heading_level: 3

## Linting

::: ddi_l.lint.run_lint

::: ddi_l.lint.run_profile

::: ddi_l.lint.configure_lint

::: ddi_l.lint.LintConfiguration
    options:
      show_root_heading: true
      heading_level: 3

::: ddi_l.lint.LintFinding
    options:
      show_root_heading: true
      heading_level: 3

::: ddi_l.lint.register_rule

::: ddi_l.lint.register_profile

## Exceptions

::: ddi_l.exceptions
    options:
      members_order: source
      show_root_heading: false
      heading_level: 3
