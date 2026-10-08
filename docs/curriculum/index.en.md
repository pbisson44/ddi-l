# Training Curriculum

Welcome to the `ddi-l` training curriculum. This course teaches you how
to document surveys, censuses, and datasets using the DDI standard and
Python. No prior experience with DDI or XML is needed.

!!! info "What this course covers"
    You will learn to turn a CSV or Excel file into a fully documented
    DDI package, complete with questions, variables, concepts, code lists,
    custom properties, versioning, and validation.

## How the course is organized

The curriculum has **16 modules** in three tiers. Each module builds on the
one before it.

| # | Module | Time | Prerequisites |
| --- | -------- | ------ | --------------- |
| **Tier 1: Foundations** | | | |
| 1 | [What Is Metadata?](module-01-what-is-metadata.md) | 30 min | None |
| 2 | [Set Up Your Environment](module-02-setup.md) | 20 min | Module 1 |
| 3 | [Create Your First Study](module-03-first-study.md) | 30 min | Module 2 |
| 4 | [Variables and Questions](module-04-variables.md) | 30 min | Module 3 |
| 5 | [Concepts and Universes](module-05-concepts-universes.md) | 30 min | Module 4 |
| **Tier 2: Real-World Skills** | | | |
| 6 | [From CSV/Excel to DDI](module-06-csv-to-ddi.md) | 45 min | Module 5 |
| 7 | [Code Lists](module-07-code-lists.md) | 40 min | Module 6 |
| 8 | [Questionnaire Flows](module-08-questionnaire-flows.md) | 50 min | Module 7 |
| 9 | [Data Lineage](module-09-data-lineage.md) | 60 min | Module 8 |
| 10 | [Data Linkage](module-10-data-linkage.md) | 60 min | Module 9 |
| 11 | [Properties, Find, and Validate](module-11-properties-find-validate.md) | 40 min | Module 10 |
| 12 | [Custom Fields](module-12-custom-fields.md) | 45 min | Module 11 |
| 13 | [Update and Version](module-13-update-and-version.md) | 40 min | Module 12 |
| **Tier 3: Applied Practice** | | | |
| 14 | [Open and Modify Files](module-14-open-modify.md) | 30 min | Module 13 |
| 15 | [CLI Validation](module-15-cli-validation.md) | 30 min | Module 14 |
| 16 | [Capstone Projects](module-16-capstone.md) | 60-90 min | All |

## Where do I start?

Pick the row that fits you best.

| I am a... | Start at | I can skim |
| ----------- | ---------- | ------------ |
| University student (new to data) | Module 1 | Nothing |
| Researcher (know Python, not DDI) | Module 1 | Module 1 |
| Archivist (know DDI, not Python) | Module 1 | Modules 3-5 |
| NSO staff (know both) | Module 2 | Module 1 |

## The big picture

This is the process you will learn:

```text
CSV / Excel / SQL table
        ↓
  Python script (ddi-l)
        ↓
  DDI XML document
        ↓
  Validate & version
        ↓
  Archive or publish
```

## Suggested schedules

| Format | Modules | Total time |
| -------- | --------- | ------------ |
| Half-day workshop | 1-6 | ~3 hours |
| Full-day workshop | 1-14 | ~6 hours |
| Two-day intensive | 1-16 | ~8 hours |
| Self-paced | 1 per session | 3 weeks |

## Supplementary resources

These existing guides go deeper on specific topics:

- [User guide](../user-guide.md): Full CRUD API reference
- [Validation guide](../validation.md): Schema and lint details
- [CLI recipes](../cli-recipes.md): All CLI commands
- [Models reference](../models.md): Advanced model layer
- [Authoring tutorials](../tutorials/authoring.md): Step-by-step tutorials
- [Instructor guide](instructor-guide.md): Facilitation tips
- [Cheat sheet](cheat-sheet.md): Quick reference for all APIs and imports
- [Answer keys](answer-keys.md): Solutions and quiz answers
