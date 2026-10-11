---
description: >-
  Download blank and example spreadsheet templates for loading DDI metadata in
  bulk: CSV files or an Excel workbook, bilingual, with a study, its
  questionnaire, variables, data files and custom properties.
---

# Spreadsheet templates

Templates for the tables described in
[Load DDI from spreadsheets](spreadsheet-import.md). Each comes as an Excel
workbook (one sheet per table, plus a README sheet listing every column) and as
a zip of CSV files (one file per table, plus `README.txt`).

## Example

A small bilingual (English and French) labour survey with every table filled
in: the study with its series, agency and manager; concepts, a universe, a
unit type and the variable cascade; code lists sharing a "Not stated"
category and a two-level occupation classification; questions with proxy and
interviewer wordings, an instruction, a grid, a block and modules; a web
questionnaire with a sequence, nested conditions and a loop; variables in
groups and in a data file; an n-cube; methodology, processing and quality;
a concept comparison across cycles; and custom properties.

[:material-microsoft-excel: Example workbook](downloads/ddi-tables-example.xlsx){ .md-button .md-button--primary download="ddi-tables-example.xlsx" }
[:material-folder-zip: Example CSV files](downloads/ddi-tables-example.zip){ .md-button download="ddi-tables-example.zip" }

Load it as it is to see what each row becomes:

```bash
ddi tables import ddi-tables-example.xlsx -o example.xml
ddi tables import ddi-tables-example.zip -o example.xml   # the zip loads as it is
```

## Blank

The same tables with headers only, with `label`, `description` and `text`
columns for English and French. Fill `agency` in `settings`, delete the tables
you do not need, and add rows.

[:material-microsoft-excel: Blank workbook](downloads/ddi-tables-template.xlsx){ .md-button .md-button--primary download="ddi-tables-template.xlsx" }
[:material-folder-zip: Blank CSV files](downloads/ddi-tables-template.zip){ .md-button download="ddi-tables-template.zip" }

## Other languages

For other languages, generate the blank tables with the columns you need:

```bash
ddi tables template my-tables --lang en --lang fr --lang iu --format xlsx
```

Or from Python:

```python
from ddi_l.tables import write_table_templates

write_table_templates("my-tables", languages=("en", "es"))
```

`--format` (or `layout=`) is `csv` for a folder of CSV files, `zip` for the
same zipped, or `xlsx` for a workbook.

## What is in a template

| Sheet or file | One row per |
| --- | --- |
| `README` | column, with what goes in it (workbook only; `README.txt` in the zip) |
| `settings` | setting: `agency`, `version`, `language` |
| `studies` | study |
| `groups` | group of studies |
| `organizations` | organization |
| `individuals` | person |
| `concepts` | concept |
| `universes` | universe |
| `unit_types` | kind of unit |
| `conceptual_variables` | conceptual variable |
| `represented_variables` | represented variable |
| `code_lists` | code list |
| `codes` | code |
| `instructions` | instruction |
| `questions` | question |
| `question_texts` | extra wording of a question, by language and audience |
| `question_grids` | grid question |
| `question_blocks` | block of questions |
| `question_groups` | question group or module |
| `instruments` | questionnaire |
| `flow` | step of a questionnaire |
| `variables` | variable |
| `variable_groups` | variable group |
| `datasets` | data file |
| `ncubes` | n-cube |
| `methodologies` | methodology |
| `processing_events` | processing event |
| `quality_statements` | quality statement |
| `comparisons` | pair of compared items |

Every cell of the workbooks is formatted as text, so codes such as `01` keep
their leading zero. The CSV files are UTF-8 with a byte-order mark, so Excel
opens accented letters correctly.
