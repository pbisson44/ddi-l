---
title: Training curriculum
description: >-
  A 16-module course that teaches you to document surveys and datasets with
  DDI and Python, from a first study to a validated, versioned package.
---

# Training curriculum

Welcome to the `ddi-l` training curriculum. This course teaches you how
to document surveys, censuses, and datasets using the DDI standard and
Python. No prior experience with DDI or XML is needed.

This is the place to learn `ddi-l` step by step. The
[user guide](../user-guide.md) is a one-page reference of the same API, and
the [how-to guides](../validation.md) cover single tasks once you know the
basics.

!!! info "What this course covers"
    You will learn to turn a CSV or Excel file into a fully documented
    DDI package, complete with questions, variables, concepts, code lists,
    custom properties, versioning, and validation.

## How the course is organized

The curriculum has **16 modules** in three tiers. Each module builds on the
one before it. You check your work from Module 3 onwards, and by the end of
Tier 1 you can open, change and validate any DDI file.

| # | Module | Time | Prerequisites |
| --- | -------- | ------ | --------------- |
| **Tier 1: Foundations** | | | |
| 1 | [What is metadata?](module-01-what-is-metadata.md) | 30 min | None |
| 2 | [Set up your environment](module-02-setup.md) | 20 min | Module 1 |
| 3 | [Create your first study](module-03-first-study.md) | 30 min | Module 2 |
| 4 | [Variables and questions](module-04-variables.md) | 30 min | Module 3 |
| 5 | [Concepts and universes](module-05-concepts-universes.md) | 30 min | Module 4 |
| 6 | [Open and modify files](module-06-open-modify.md) | 30 min | Module 5 |
| 7 | [Validate from the command line](module-07-cli-validation.md) | 30 min | Module 6 |
| **Tier 2: Real-world skills** | | | |
| 8 | [From CSV/Excel to DDI](module-08-csv-to-ddi.md) | 45 min | Module 7 |
| 9 | [Code lists](module-09-code-lists.md) | 40 min | Module 8 |
| 10 | [Questionnaire flows](module-10-questionnaire-flows.md) | 50 min | Module 9 |
| 11 | [Data lineage](module-11-data-lineage.md) | 60 min | Module 10 |
| 12 | [Data linkage](module-12-data-linkage.md) | 60 min | Module 11 |
| 13 | [Properties, find, and validate](module-13-properties-find-validate.md) | 40 min | Module 12 |
| 14 | [Custom fields](module-14-custom-fields.md) | 45 min | Module 13 |
| 15 | [Update and version](module-15-update-and-version.md) | 40 min | Module 14 |
| **Tier 3: Applied practice** | | | |
| 16 | [Capstone projects](module-16-capstone.md) | 60-90 min | All |

## Where do I start?

Pick the row that fits you best.

| I am a... | Start at | I can skim | Spend extra time on |
| ----------- | ---------- | ------------ | ------------------- |
| University student (new to data) | Module 1 | Nothing | Modules 3-5 |
| Researcher (know Python, not DDI) | Module 1 | Module 2 | Modules 1, 4 and 5: what DDI calls things |
| Archivist (know DDI, not Python) | Module 1 | Module 1 | Modules 2-7: the Python you need |
| NSO staff (know both) | Module 2 | Modules 1 and 3 | Modules 8-15 |
| Developer automating DDI checks | Module 2 | Modules 1, 4 and 5 | Modules 3 and 7, then the automation track below |

### Automation track

For teams that add DDI validation to pipelines or build services on
`ddi-l`. Take Modules 2, 3 and 7, then work through these guides in order:

| Session | Focus | Pages |
| ------- | ----- | ----- |
| Pipeline foundations (45 min) | Run and configure validation and lint | [Validate and lint DDI content](../validation.md), [CLI recipes](../cli-recipes.md) |
| Automation (45 min) | Script the CLI, keep reports, fail CI on errors | [Command-line automation playbook](../tutorials/automation-playbook.md), [Schema troubleshooting clinic](../tutorials/schema-troubleshooting-clinic.md) |
| Reuse and integration (45 min) | Share fragments, call `ddi-l` from other systems | [Fragment reuse lab](../tutorials/fragment-reuse-lab.md), [HTTP API](../server.md), [Build tools and applications](../tutorials/building-tools.md) |

Review the [performance playbook](../performance.md) before planning large
batch runs.

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
| Half-day workshop | 1-7 | ~3.5 hours |
| Full-day workshop | 1-10 | ~6 hours |
| Two-day intensive | 1-16 | ~11 hours |
| Self-paced | 1 per session | 3 weeks |

## Supplementary resources

- [Instructor guide](instructor-guide.md): Facilitation tips
- [Cheat sheet](cheat-sheet.md): Quick reference for all APIs and imports
- [Answer keys](answer-keys.md): All solutions on one page, for instructors.
  Learners can open the answer under each exercise instead.
- [User guide](../user-guide.md): The `Document` API on one page
- [Validation guide](../validation.md): Schema and lint details
- [CLI recipes](../cli-recipes.md): All CLI commands
- [Models reference](../models.md): Advanced model layer
