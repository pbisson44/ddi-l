---
description: >-
  Schedules, setup checklist, facilitation tips and common mistakes for
  teaching the ddi-l training curriculum.
---

# Instructor guide

This guide helps facilitators deliver the `ddi-l` training curriculum
in classrooms, workshops, or online sessions. It also works for
self-paced learners who want facilitation context.

## Classroom vs. self-paced

The curriculum works in both modes:

- **Classroom**: An instructor demonstrates each concept live, then
  learners complete the exercises. Use the timing and facilitation tips
  below.
- **Self-paced**: Learners read each module, follow the code examples,
  and check their work against the [answer keys](answer-keys.en.md).

## Suggested schedules

The workshop rows add up the instructor-led times the modules give, and the
self-paced row their self-paced times, without breaks or setup. The
[course overview](index.en.md#suggested-schedules) gives both totals for each
format.

| Format | Modules | Time | Covers |
| -------- | --------- | ------------ | ------------ |
| Half-day workshop | 1-5 | 3 h 20 min | What metadata is, setup, a first study, variables, concepts and universes |
| Full-day workshop | 1-9 | 6 h 30 min | All of Tier 1 (including opening files and validation), CSV to DDI and code lists |
| Three-day intensive | 1-17 | 16 h, about 5 h 20 min a day | Full curriculum with capstone |
| Self-paced | One module per session | 12 h 20 min to 12 h 50 min | 17 sessions of 20 to 90 min, about 3 to 4 weeks |

## Using the learning objectives

Every module opens with numbered learning objectives (O1, O2, ...), tags each
exercise and quiz question with the objectives it practises, and ends with a
**Check yourself** list, one line per objective. Use them to run each session:

- **Open with the objectives.** Read the module's objectives aloud, or show
  the box, at the start of the session. Learners then know what they will be
  able to do by the end, and you know what to check.
- **Pick exercises by tag.** Short on time? Choose one exercise per objective
  rather than the first few in the list. If a learner struggles with one
  objective, give them another exercise with the same tag.
- **Close with Check yourself as an exit ticket.** In the last five minutes,
  learners tick the lines they can do. A line many learners leave unticked
  tells you what to revisit at the start of the next session. In Module 17,
  the rubric and the presentation do the same job.

## Environment setup checklist

Before the session, make sure every learner has:

- [ ] Python 3.11 or newer installed
- [ ] `ddi-l` installed (`pip install ddi-l`)
- [ ] `pandas` and `openpyxl` installed (`pip install pandas openpyxl`)
- [ ] A text editor or IDE (VS Code, PyCharm, or even Notepad)
- [ ] The sample CSV file, [`survey_sample.csv`](survey_sample.csv){ download="survey_sample.csv" }
  (capstone tracks also use [`thesis-data.csv`](thesis-data.csv){ download="thesis-data.csv" },
  [`health-survey.csv`](health-survey.csv){ download="health-survey.csv" } and
  [`census-data.csv`](census-data.csv){ download="census-data.csv" })
- [ ] A terminal or command prompt

Have a fallback plan: a cloud notebook (Google Colab, JupyterHub) or a
pre-built container with everything installed.

## Facilitation tips by module

### Module 1: What is metadata?

- Start with the "messy table" exercise *before* defining metadata. Let
  learners discover the problem.
- For NSO audiences, use the census example. For students, use the thesis
  example.
- **FAIR principles:** Walk through the Dr. Chen example in section 4.
  Ask learners which FAIR letter is hardest to achieve without a standard
  like DDI. Most will say Interoperable or Findable; use this to motivate
  the rest of the curriculum.
- Time: 45 min including discussion.

### Module 2: Set up your environment

- Budget 30 min: environment issues are the #1 classroom time sink.
- Walk around and help with PATH issues, wrong Python versions, and
  virtual environments.
- If installs fail, switch to the fallback environment immediately.

### Module 3: Create your first study

- This is the "aha" moment. Type the code live and show the XML output.
- Common mistake: forgetting quotes around strings.
- Section 9 introduces `doc.validate()` and `doc.lint()`. Ask learners to
  run both at the end of every later module, before they save.
- Time: 45 min with live demo.

### Module 4: Variables and questions

- Draw the mental model on a whiteboard: Question → Variable → Data
  column.
- Common mistake: passing the question text string instead of the
  question object to `question=`.
- Time: 40 min.

### Module 5: Concepts and universes

- Use a diagram: Universe = "who", Concept = "what", Variable = "how
  it is measured", Question = "how it is asked".
- Time: 40 min.

### Module 6: Open and modify files

- This is the archivist workflow: receive → inspect → enrich → validate
  → save.
- Time: 40 min.

### Module 7: Validate from the command line

- For NSO audiences, spend extra time on batch validation and exit codes.
- Time: 40 min.

### Module 8: From CSV/Excel to DDI

- This is the most important module for researchers and NSO staff.
  Demonstrate the full workflow: open a CSV, run the script, show the
  DDI XML output.
- Emphasize: the CSV is the data. The DDI XML is documentation *about*
  the data. They are two different files.
- Skip the SQL section for non-technical audiences.
- Time: 60 min with exercises.

### Module 9: Code lists

- Show a real-world code list (ISO country codes, employment
  classifications).
- Common mistake: forgetting to import Category.
- Time: 50 min.

### Module 10: Questionnaire flows

- Start with a paper spec on screen. Have learners circle questions,
  underline skip rules, and box repeat instructions before touching code.
- Draw the flowchart on a whiteboard. Map each box to a DDI construct.
- Key confusion: "Why both a Question and a QuestionConstruct?" Explain
  content vs. flow separation.
- Time: 60 min.

### Module 11: Data lineage

- Use the "recipe" analogy: raw ingredients (collection), cooking
  (production), plated dish (master). Provenance is the recipe.
- Draw the three-file pipeline. For each variable, ask learners to trace
  it back to the original question.
- Clarify: `question_references` = "what was asked",
  `source_variable_references` = "what data was used to compute this".
- The numeric-to-coded derivation (age → age_group) is the most relatable
  example for all audiences.
- For NSO staff: this is audit trail documentation that regulators need.
- Time: 75 min.

### Module 12: Data linkage

- Anchor with the burden argument: reuse the tax file instead of re-asking
  income. Linkage creates new information from existing data.
- Draw two files sharing one column (`anon_id`): the linkage key.
- Contrast deterministic (one reliable key) vs probabilistic (several noisy
  fields, weighted agreement, clerical review).
- Stress that `source_variable_references` crossing study boundaries is the
  technical heart of linkage; the save-time warning is expected.
- For NSO staff: connect to their own organization's linkage environment and
  approval rules (for example, linkages that are pre-approved and those that
  need a review).
- Always end a linkage on de-identification and, often, synthetic data.
- Time: 75 min.

### Module 13: Properties, find, and validate

- Demonstrate that custom properties survive XML round-trips.
- Show passing a code list object as a property value (stores URN).
- Common mistake: trying to `find()` by name instead of by identifier.
- Time: 50 min.

### Module 14: Custom fields

- Open with the "side spreadsheet" problem: local metadata kept outside the
  file always drifts out of sync. Custom fields keep it in the DDI.
- Make the openness point explicit: DDI provides a *standardized* extension
  point. Show the `UserAttributePair` XML so learners see it is still valid DDI.
- Contrast with Module 13: that module taught the `set_property` mechanics;
  this one governs extensions: namespaces, catalogs, controlled values, audit.
- Clarify `UserID` vs custom property: identify vs describe.
- For NSO/archive staff: connect to real governance (retention schedules,
  security classifications, data stewards), and the Section 9 audit loop.
- Caution: do not reinvent built-in DDI; custom fields are for genuine gaps.
- Time: 55 min.

### Module 15: Update and version

- Key module for archivists and NSO staff managing long-running surveys.
- Show the XML before and after versioning so learners see the version
  number and rationale in the file.
- Time: 75 min.

### Module 16: Advanced questionnaire specification

- For spec writers and NSO staff who move from screen designs and workbooks
  to a spec that instruments are checked against.
- Put the missing-answer table of section 2 on the board first, and let
  learners fill in the last row before you show it.
- Stress that a gate kept in the tool's own code is a correct result, and
  that an undocumented format is never guessed: the operators to use are the
  ones the tool's documentation lists.
- Time: 90 min.

### Module 17: Capstone projects

- Let learners choose their persona track. If in a mixed group, form
  teams by role.
- Ask to see each learner's plan (objective O1) before they write code.
- Budget 90 min including the 5-minute presentations at the end (O6).
  Tracks B and D record two techniques each and run longest.
- Score with the self-assessment rubric in the module: 80 points for the
  skills every track shares, and 20 for the track's own techniques (flow,
  lineage, linkage, custom fields or specification).

## Common mistakes across all modules

| Mistake | Module | Fix |
| --------- | -------- | ----- |
| Forgetting quotes around strings | 3 | Show the error message and explain |
| Passing text instead of object to `question=` | 4 | Show the difference between `"age"` and `q1` |
| Forgetting to import Category/Instrument | 9, 10 | Show the import line explicitly |
| Confusing Question with QuestionConstruct | 10 | Question = content, QuestionConstruct = flow step |
| Confusing question_references with source_variable_references | 11 | question_ref = what was asked, source_var_ref = what data was used |
| Using `find()` with a name instead of identifier | 13 | Print `item.identifier` first |
| Writing `not x > 30` where `x <= 30` was meant | 16 | Fill in the missing-answer table: they differ when `x` has no answer |
| Not validating before saving | 3 onwards | Make validation a habit: always validate before save |

## Adapting for each audience

| Audience | Emphasize | Skip or skim |
| ---------- | ----------- | ------------- |
| University students | Modules 1 (motivation), 3-7 (basics and checking your work) | SQL section in Module 8 |
| Researchers | Modules 1, 4 and 5 (DDI vocabulary), 8 (CSV workflow), 9-13 (code lists, flows, lineage, linkage, properties) | Module 2 if they already use Python |
| Archivists | Modules 2-7 (Python, open/modify, validation), 14 (custom fields), 15 (versioning) | Module 1 if DDI-experienced |
| NSO staff | Modules 8-16 (full pipeline), especially 10 (flows), 11 (lineage), 12 (linkage), 14 (custom fields), 16 (questionnaire specification) | Modules 1 and 3 |
| Developers automating DDI checks | Modules 3 and 7, then the [automation track](index.en.md#automation-track) | Modules 1, 4 and 5 |

## Assessment approach

- **Quizzes** (Modules 1-16): Formative, to check understanding. Review
  answers as a group in classroom settings.
- **Check yourself** (every module): An exit ticket at the end of each
  session. See [Using the learning objectives](#using-the-learning-objectives).
- **Capstone** (Module 17): Summative. The rubric scores the module's six
  objectives on one dataset, including the plan and the presentation.
- **Reflection questions** (Module 17): No right answer. Use for
  discussion or written feedback.

## Terminology glossary (EN / FR)

| English | French |
| --------- | -------- |
| Metadata | Métadonnées |
| Study | Étude |
| Survey | Enquête |
| Variable | Variable |
| Question | Question |
| Concept | Concept |
| Universe | Univers |
| Code list | Liste de codes |
| Category | Catégorie |
| Validate | Valider |
| Version | Version |
| Custom property | Propriété personnalisée |
| Agency | Agence |
| Identifier | Identifiant |
| Save | Enregistrer |
| Open | Ouvrir |
| Data linkage | Couplage de données |
| Linkage key | Clé de couplage |
| Custom field | Champ personnalisé |
| Extension point | Point d'extension |

## Collecting feedback

After the final session:

1. Ask learners to fill out a short feedback form (3-5 questions).
2. Capture terminal transcripts or notebook checkpoints as onboarding
   references for future cohorts.
3. Hold a 10-minute retrospective: what worked, what did not, what to
   change next time.

## Additional resources

- [Automation track](index.en.md#automation-track): A workshop plan for teams
  that automate validation
- [Answer keys](answer-keys.en.md): Every exercise solution and quiz answer on
  one page
