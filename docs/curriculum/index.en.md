---
title: Training curriculum
description: >-
  A 17-module course that teaches you to document surveys and datasets with
  DDI and Python, from a first study to a validated, versioned package.
---

# Training curriculum

Welcome to the `ddi-l` training curriculum. This course teaches you how
to document surveys, censuses, and datasets using the DDI standard and
Python. No prior experience with DDI or XML is needed.

This is the place to learn `ddi-l` step by step. The
[user guide](../user-guide.en.md) is a one-page reference of the same API, and
the [how-to guides](../validation.en.md) cover single tasks once you know the
basics.

!!! info "What this course covers"
    You will learn to turn a CSV or Excel file into a fully documented
    DDI package, complete with questions, variables, concepts, code lists,
    custom properties, versioning, and validation.

## How the course is organized

The curriculum has **17 modules** in three tiers. Each module lists its
prerequisites at the top, and the table below repeats them: most modules need
only the one before, but some need more. You check your work from Module 3
onwards, and by the end of Tier 1 you can open, change and validate any DDI
file.

The times are the ones each module gives: working alone (self-paced), or in a
class with an instructor (instructor-led).

| # | Module | Self-paced | Instructor-led | Prerequisites |
| --- | -------- | ------ | ------ | --------------- |
| **Tier 1: Foundations** | | | | |
| 1 | [What is metadata?](module-01-what-is-metadata.en.md) | 30 min | 45 min | None |
| 2 | [Set up your environment](module-02-setup.en.md) | 20 min | 30 min | Module 1 |
| 3 | [Create your first study](module-03-first-study.en.md) | 30 min | 45 min | Module 2 |
| 4 | [Variables and questions](module-04-variables.en.md) | 30 min | 40 min | Module 3 |
| 5 | [Concepts and universes](module-05-concepts-universes.en.md) | 30 min | 40 min | Module 4 |
| 6 | [Open and modify files](module-06-open-modify.en.md) | 30 min | 40 min | Module 5 |
| 7 | [Validate from the command line](module-07-cli-validation.en.md) | 30 min | 40 min | Module 6 |
| **Tier 2: Real-world skills** | | | | |
| 8 | [From CSV/Excel to DDI](module-08-csv-to-ddi.en.md) | 45 min | 60 min | Module 7 |
| 9 | [Code lists](module-09-code-lists.en.md) | 40 min | 50 min | Module 8 |
| 10 | [Questionnaire flows](module-10-questionnaire-flows.en.md) | 50 min | 60 min | Module 9 |
| 11 | [Data lineage](module-11-data-lineage.en.md) | 60 min | 75 min | Module 10 |
| 12 | [Data linkage](module-12-data-linkage.en.md) | 60 min | 75 min | Module 11 |
| 13 | [Properties, find, and validate](module-13-properties-find-validate.en.md) | 40 min | 50 min | Module 12 |
| 14 | [Custom fields](module-14-custom-fields.en.md) | 45 min | 55 min | Module 13 |
| 15 | [Update and version](module-15-update-and-version.en.md) | 65 min | 75 min | Module 14 |
| **Tier 3: Applied practice** | | | | |
| 16 | [Advanced questionnaire specification](module-16-advanced-questionnaire-spec.en.md) | 75 min | 90 min | Modules 7, 10 and 15 |
| 17 | [Capstone projects](module-17-capstone.en.md) | 60-90 min | 90 min | All (1-16) |

Each module starts with numbered **learning objectives** (O1, O2, ...): what
you can do by the end of it, such as write a script or validate a file. Each
exercise and quiz question is tagged with the objectives it practises, for
example **Exercise 2 (O3)**. Each module ends with a **Check yourself** list,
one line per objective. Tick each line before you move on; for a line you
cannot tick, redo the exercises with that tag.

## Where do I start?

Pick the row that fits you best.

| I am a... | Start at | I can skim | Spend extra time on |
| ----------- | ---------- | ------------ | ------------------- |
| University student (new to data) | Module 1 | Nothing | Modules 3-5 |
| Researcher (know Python, not DDI) | Module 1 | Module 2 | Modules 1, 4 and 5: what DDI calls things |
| Archivist (know DDI, not Python) | Module 1 | Module 1 | Modules 2-7: the Python you need |
| NSO staff (know both) | Module 2 | Modules 1 and 3 | Modules 8-16 |
| Developer automating DDI checks | Module 2 | Modules 1, 4 and 5 | Modules 3 and 7, then the automation track below |

### Automation track

For teams that add DDI validation to pipelines or build services on
`ddi-l`. Take Modules 2, 3 and 7, then work through these guides in order:

| Session | Focus | Pages |
| ------- | ----- | ----- |
| Pipeline foundations (45 min) | Run and configure validation and lint | [Validate and lint DDI content](../validation.en.md), [CLI recipes](../cli-recipes.en.md) |
| Automation (45 min) | Script the CLI, keep reports, fail CI on errors | [Command-line automation playbook](../tutorials/automation-playbook.en.md), [Schema troubleshooting clinic](../tutorials/schema-troubleshooting-clinic.en.md) |
| Reuse and integration (45 min) | Share fragments, call `ddi-l` from other systems | [Fragment reuse lab](../tutorials/fragment-reuse-lab.en.md), [HTTP API](../server.en.md), [Build tools and applications](../tutorials/building-tools.en.md) |

Review the [performance playbook](../performance.en.md) before planning large
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

Each total adds up the modules' own times, without breaks or setup.

| Format | Modules | Instructor-led | Self-paced |
| -------- | --------- | ------------ | ------------ |
| Half-day workshop | 1-5 | 3 h 20 min | 2 h 20 min |
| Full-day workshop | 1-9 | 6 h 30 min | 4 h 45 min |
| Three-day intensive | 1-17 | 16 h (about 5 h 20 min a day) | 12 h 20 min to 12 h 50 min |
| Self-paced | One module per session | Not applicable | 12 h 20 min to 12 h 50 min over 17 sessions: 3 to 4 weeks at one session per weekday |

To finish Tier 1 in a workshop, add Modules 6 and 7 to the half-day
(1 h 20 min more, 4 h 40 min in all): that is a short day rather than a
half-day.

## Supplementary resources

- [Instructor guide](instructor-guide.en.md): Facilitation tips
- [Cheat sheet](cheat-sheet.en.md): Quick reference for all APIs and imports
- [Answer keys](answer-keys.en.md): All solutions on one page, for instructors.
  Learners can open the answer under each exercise instead.
- [User guide](../user-guide.en.md): The `Document` API on one page
- [Validation guide](../validation.en.md): Schema and lint details
- [CLI recipes](../cli-recipes.en.md): All CLI commands
- [Models reference](../models.en.md): Advanced model layer
