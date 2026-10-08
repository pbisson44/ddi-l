# Instructor Guide

This guide helps facilitators deliver the `ddi-l` training curriculum
in classrooms, workshops, or online sessions. It also works for
self-paced learners who want facilitation context.

## Classroom vs. self-paced

The curriculum works in both modes:

- **Classroom**: An instructor demonstrates each concept live, then
  learners complete the exercises. Use the timing and facilitation tips
  below.
- **Self-paced**: Learners read each module, follow the code examples,
  and check their work against the [answer keys](answer-keys.md).

## Suggested schedules

| Format | Modules | Total time |
| -------- | --------- | ------------ |
| Half-day workshop (3 h) | 1-6 | Foundations + CSV-to-DDI |
| Full-day workshop (6 h) | 1-14 | Everything except CLI and capstone |
| Two-day intensive (8 h) | 1-16 | Full curriculum with capstone |
| Self-paced | 1 per session | ~3 weeks at 30-45 min/session |

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

### Module 1: What Is Metadata?

- Start with the "messy table" exercise *before* defining metadata. Let
  learners discover the problem.
- For NSO audiences, use the census example. For students, use the thesis
  example.
- **FAIR principles:** Walk through the Dr. Chen example in section 4.
  Ask learners which FAIR letter is hardest to achieve without a standard
  like DDI. Most will say Interoperable or Findable; use this to motivate
  the rest of the curriculum.
- Time: 45 min including discussion.

### Module 2: Set Up Your Environment

- Budget 30 min: environment issues are the #1 classroom time sink.
- Walk around and help with PATH issues, wrong Python versions, and
  virtual environments.
- If installs fail, switch to the fallback environment immediately.

### Module 3: Create Your First Study

- This is the "aha" moment. Type the code live and show the XML output.
- Common mistake: forgetting quotes around strings.
- Time: 45 min with live demo.

### Module 4: Variables and Questions

- Draw the mental model on a whiteboard: Question → Variable → Data
  column.
- Common mistake: passing the question text string instead of the
  question object to `question=`.
- Time: 40 min.

### Module 5: Concepts and Universes

- Use a diagram: Universe = "who", Concept = "what", Variable = "how
  it is measured", Question = "how it is asked".
- Time: 40 min.

### Module 6: From CSV/Excel to DDI

- This is the most important module for researchers and NSO staff.
  Demonstrate the full workflow: open a CSV, run the script, show the
  DDI XML output.
- Emphasize: the CSV is the data. The DDI XML is documentation *about*
  the data. They are two different files.
- Skip the SQL section for non-technical audiences.
- Time: 60 min with exercises.

### Module 7: Code Lists

- Show a real-world code list (ISO country codes, employment
  classifications).
- Common mistake: forgetting to import Category.
- Time: 50 min.

### Module 8: Questionnaire Flows

- Start with a paper spec on screen. Have learners circle questions,
  underline skip rules, and box repeat instructions before touching code.
- Draw the flowchart on a whiteboard. Map each box to a DDI construct.
- Key confusion: "Why both a Question and a QuestionConstruct?" Explain
  content vs. flow separation.
- Time: 60 min.

### Module 9: Data Lineage

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

### Module 10: Data Linkage

- Anchor with the burden argument: reuse the tax file instead of re-asking
  income. Linkage creates new information from existing data.
- Draw two files sharing one column (`anon_id`): the linkage key.
- Contrast deterministic (one reliable key) vs probabilistic (several noisy
  fields, weighted agreement, clerical review).
- Stress that `source_variable_references` crossing study boundaries is the
  technical heart of linkage; the save-time warning is expected.
- For NSO staff: connect to SDLE, B-LFE, and LEBAF, and to governance
  (pre-approved vs reviewed linkages under the Directive on Microdata Linkage).
- Always end a linkage on de-identification and, often, synthetic data.
- Time: 75 min.

### Module 11: Properties, Find, and Validate

- Demonstrate that custom properties survive XML round-trips.
- Show passing a code list object as a property value (stores URN).
- Common mistake: trying to `find()` by name instead of by identifier.
- Time: 50 min.

### Module 12: Custom Fields

- Open with the "side spreadsheet" problem: local metadata kept outside the
  file always drifts out of sync. Custom fields keep it in the DDI.
- Make the openness point explicit: DDI provides a *standardized* extension
  point. Show the `UserAttributePair` XML so learners see it is still valid DDI.
- Contrast with Module 11: that module taught the `set_property` mechanics;
  this one governs extensions: namespaces, catalogs, controlled values, audit.
- Clarify `UserID` vs custom property: identify vs describe.
- For NSO/archive staff: connect to real governance (retention schedules,
  security classifications, data stewards), and the Section 9 audit loop.
- Caution: do not reinvent built-in DDI; custom fields are for genuine gaps.
- Time: 55 min.

### Module 13: Update and Version

- Key module for archivists and NSO staff managing long-running surveys.
- Show the XML before and after versioning so learners see the version
  number and rationale in the file.
- Time: 50 min.

### Module 14: Open and Modify Files

- This is the archivist workflow: receive → inspect → enrich → validate
  → save.
- Time: 40 min.

### Module 15: CLI Validation

- For NSO audiences, spend extra time on batch validation and exit codes.
- Time: 40 min.

### Module 16: Capstone Projects

- Let learners choose their persona track. If in a mixed group, form
  teams by role.
- Budget 90 min including a short presentation at the end.
- Grade using the self-assessment rubric in the module.

## Common mistakes across all modules

| Mistake | Module | Fix |
| --------- | -------- | ----- |
| Forgetting quotes around strings | 3 | Show the error message and explain |
| Passing text instead of object to `question=` | 4 | Show the difference between `"age"` and `q1` |
| Forgetting to import Category/Instrument | 7 | Show the import line explicitly |
| Confusing Question with QuestionConstruct | 8 | Question = content, QuestionConstruct = flow step |
| Confusing question_references with source_variable_references | 9 | question_ref = what was asked, source_var_ref = what data was used |
| Using `find()` with a name instead of identifier | 11 | Print `item.identifier` first |
| Not validating before saving | 11-13 | Make validation a habit: always validate before save |

## Adapting for each audience

| Audience | Emphasize | Skip or skim |
| ---------- | ----------- | ------------- |
| University students | Modules 1 (motivation), 3-6 (basics) | SQL section in Module 6 |
| Researchers | Modules 6 (CSV workflow), 7-11 (code lists, flows, lineage, linkage, properties) | Module 1 if they know metadata |
| Archivists | Modules 13-14 (versioning, open/modify), 12 (custom fields) | Modules 3-5 if DDI-experienced |
| NSO staff | Modules 6-13 (full pipeline), 8 (flows), 9 (lineage), 10 (linkage), 12 (custom fields), 15 (CLI) | Module 1 if DDI-experienced |

## Assessment approach

- **Quizzes** (Modules 1-15): Formative, to check understanding. Review
  answers as a group in classroom settings.
- **Capstone** (Module 16): Summative, to evaluate the complete skill set.
  Use the rubric in the module.
- **Reflection questions** (Module 16): No right answer. Use for
  discussion or written feedback.

## Terminology glossary (EN / FR)

| English | French |
| --------- | -------- |
| Metadata | Metadonnees |
| Study | Etude |
| Survey | Enquete |
| Variable | Variable |
| Question | Question |
| Concept | Concept |
| Universe | Univers |
| Code list | Liste de codes |
| Category | Categorie |
| Validate | Valider |
| Version | Version |
| Custom property | Propriete personnalisee |
| Agency | Agence |
| Identifier | Identifiant |
| Save | Enregistrer |
| Open | Ouvrir |
| Data linkage | Couplage de donnees |
| Linkage key | Cle de couplage |
| Custom field | Champ personnalise |
| Extension point | Point d'extension |

## Collecting feedback

After the final session:

1. Ask learners to fill out a short feedback form (3-5 questions).
2. Capture terminal transcripts or notebook checkpoints as onboarding
   references for future cohorts.
3. Hold a 10-minute retrospective: what worked, what did not, what to
   change next time.

## Additional resources

- [Persona-based learning tracks](../tutorials/persona-learning-paths.md):
  Additional workshop formats
- [Authoring tutorials](../tutorials/authoring.md): Standalone exercises
- [Training labs](../tutorials/training-labs.md): Interactive labs
