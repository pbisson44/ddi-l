# Persona-based learning tracks

Two suggested workshop plans: one for people new to DDI, and one for teams
that automate validation. Each plan lists the sessions, the pages to use, and
optional extensions.

## New integrators

!!! info "Audience"
    Engineers or analysts using DDI for the first time, who need to install
    the package, create studies and validate them.

### Learning objectives

- Install the toolkit and create a study with `ddi.new_study()`.
- Add questions, variables, concepts, and universes using the CRUD API.
- Validate documents and navigate the CLI.

### Recommended sequence

| Session | Focus | Primary resources | Checkpoints |
| ------- | ----- | ----------------- | ----------- |
| Kick-off (30 min) | Environment setup and first study | [Install ddi-l](../installation.md), [User guide](../user-guide.md) | Learners can create a study with `ddi.new_study()`, add questions, and save to XML. |
| Guided authoring (45 min) | Build a study with variables, concepts, and code lists | [Authoring workflows](authoring.md), Lab 1 from the [training exercises](training-labs.md) | Teams can create a study with linked questions and variables and validate it. |
| CLI practice (30 min) | Validate and convert content from the shell | [Browse CLI recipes](../cli-recipes.md), Lab 3 from the [training exercises](training-labs.md) | Participants can run `ddi validate` and `ddi to-json` and interpret the output. |

### Extension ideas

- Pair learners to experiment with `add_item()` for different DDI types
  (Category, Instrument, etc.) and compare the XML output.
- Encourage learners to draft a checklist of the API methods they used during
  the workshop.

## Advanced automation teams

!!! info "Audience"
    Platform or tooling teams adding DDI validation to CI/CD pipelines, who
    need configurable linting, reusable fragments and scripts.

### Learning objectives

- Customize lint profiles and configuration to match your organization's rules.
- Automate validation as part of continuous integration.
- Collect structured output that other systems can consume.

### Recommended sequence

| Session | Focus | Primary resources | Checkpoints |
| ------- | ----- | ----------------- | ----------- |
| Pipeline foundations (45 min) | Run and customize validation | [Validate and lint](../validation.md), Lab 2 from the [training exercises](training-labs.md) | Teams can validate documents programmatically and from the CLI. |
| Fragment automation (30 min) | Maintain reusable fragments alongside instances | [Authoring workflows](authoring.md), [Fragment reuse lab](fragment-reuse-lab.md) | Learners can create and validate DDI documents in automated workflows. |
| Service integration (45 min) | Capture results for downstream tooling | [Command-line automation playbook](automation-playbook.md), [Build tools](building-tools.md) | Participants can batch-validate files and capture structured output. |

### Extension ideas

- Prototype a thin wrapper that uses `ddi.open_ddi()` and `doc.validate()` to
  expose validation results over HTTP.
- Review the [performance playbook](../performance.md) when planning large
  batch operations.

## Facilitation tips

- Start each session by restating what the group should be able to do by the
  end of it.
- Capture artifacts (terminal transcripts, JSON output, or notebook
  checkpoints) so teams can reuse them as onboarding references.
- Ask for feedback after the final session; learners can use the "Learner
  feedback" issue template.
