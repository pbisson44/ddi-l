---
description: >-
  The ddi-l development guide: environment, quality gates, the XSD code
  generator, architecture, documentation toolchain and releases.
---

# Development guide

Thanks for helping improve `ddi-l`! Two documents cover contributing:

- [`CONTRIBUTING.md`](https://github.com/pbisson44/ddi-l/blob/main/CONTRIBUTING.md)
  on GitHub is the short version: set up, run the checks, open a pull request.
  Start there.
- This guide is the in-depth reference behind it: the architecture, the
  XSD-driven code generator, adding a DDI version, the two XML backends, the
  documentation toolchain, and the release process.

## Set up your environment

**Python 3.11 or newer** is required. The project is managed with
[uv](https://docs.astral.sh/uv/), and `uv.lock` is the single source of truth
for dependency versions; CI installs from it with `--locked`.

```bash
uv sync --group dev              # Runtime + development dependencies
uv sync --group dev --extra full # ...plus the optional lxml backend
uv sync --group docs             # Documentation toolchain
```

Prefix commands with `uv run` (`uv run pytest`), or activate the environment
with `source .venv/bin/activate`.

!!! note "`full` is an extra, not a dependency group"
    The optional `lxml` backend is declared under
    `[project.optional-dependencies]`, so it installs with `--extra full`.
    Asking for it as a group (`--group full`) fails.

If you prefer plain pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[full]' --group dev   # pip 25.1+ reads dependency groups
```

## Quality gates

Run these before opening a pull request:

```bash
uv run ruff format --check .   # Formatting
uv run ruff check .            # Linting (includes Google-style docstrings)
uv run mypy src tests          # Type checking (blocking in CI)
uv run pytest                  # Tests (target: 90% coverage)
uvx pip-audit --strict         # Dependency vulnerability scan
git diff --exit-code           # A test run must not modify tracked files
```

`ruff` and `mypy` are pinned to exact versions in the `dev` group. A new
release of either can change what counts as a violation, so the pin is what
keeps CI reproducible, so bump it deliberately, in its own commit.

The Makefile also provides:

```bash
make release-check             # Build distributions and verify packaging
make docs-build                # Build docs with strict mode
make docs-serve                # Live preview server
```

`make release-check` is the gate that matters before a release. It builds both
distributions, asserts the bundled XSDs and example files are present, asserts
that `ddi_l` is the *only* top-level package in the wheel, then installs the
wheel into a clean virtualenv and validates a document with it.

### Mutation testing

Coverage says a line ran. It does not say a test would notice if the line were
wrong, and the difference matters most in the small predicates that decide
whether a language tag matches or a namespace is used. `mutmut` answers the
second question by changing the code and checking whether the suite complains:

```bash
uv run mutmut run                       # everything in scope
uv run mutmut results                   # what survived
uv run mutmut show <mutant-name>        # the diff for one survivor
uv run mutmut run <mutant-name>         # re-check one after adding a test
```

Scope is set in `[tool.mutmut]` in `pyproject.toml` and is deliberately narrow:
four modules of hand-written decision logic, not the generated dataclasses or
the XML plumbing, whose mutants are overwhelmingly equivalent. Widen it when
you add a module with real branching.

**It is not part of the PR gate**, and `.github/workflows/mutation.yml` says
why at length: a scoped run is ~2,200 mutants and tens of minutes, survivors
need judgement a threshold cannot supply, and results differ between the two
XML backends. It runs weekly and on demand, and the report is something to
read rather than a status to satisfy.

Reading survivors is the skill. Some are real:
`test_tree_uses_namespace_looks_at_tags_and_attributes` exists because
mutating that helper to always answer "no" left the whole suite green, which
meant nothing checked that a document *using* `xsi:schemaLocation` keeps its
declaration. Others cannot be killed and should not be: `getattr(node,
"nsmap", )` behaves exactly like `getattr(node, "nsmap", None)` when every node
has the attribute. Fix the first kind by writing the missing test; leave the
second kind alone.

## Coding standards

- **Line length**: 88 characters.
- **Linting**: `ruff` with `E`, `F`, `W`, `I`, `N`, `UP`, `B`, `SIM`,
  `RUF`, and `D` (Google docstrings) rule sets.
- **Type hints**: `mypy` on `src/` and `tests/`, blocking in CI.
- **Docstrings**: Google style with `Args:`, `Returns:`, `Raises:` sections.
- **Tests**: `pytest` with `pytest-cov`. Coverage target is 90%.
- **Imports**: Ruff's isort integration handles ordering.

## XSD-driven codegen pipeline

All model classes are generated from the DDI 3.3 XSD files. The XSD is the
single source of truth for fields, element ordering, namespaces, and
documentation text.

### How it works

1. `codegen/xsd_introspect.py` extracts the complete content model from the XSD
   (the ordered particle tree, cardinality, namespaces, attributes, mixed
   flag, and `xs:documentation` text.
2. `codegen/generate_model_bases.py` emits field-only base dataclasses under
   `src/ddi_l/models/_generated/`. Each carries its XSD-derived fields plus
   three class-level tables: `_FIELD_XML_MAP` (field name to element tag and
   type), `_ATTR_XML_MAP` (field name to XML attribute), and `_ELEMENT_ORDER`
   (the XSD-declared child order). It also emits
   `_generated/label_slots.py`, a schema-wide table of which elements may carry
   an `r:Label`, used by the `ddi.maintainable.labels` lint rule to avoid
   asking for labels the schema does not allow) and by `ALLOW_LABELS`, which
   is derived from it at class creation rather than kept by hand. A second
   schema-wide table, `_generated/fixed_attributes.py`, records the attributes
   the XSD pins to a `fixed` value; the JSON-to-XML conversion drops them,
   since an attribute the schema pins carries no information and writing it
   back would make the round-trip return more than it was given.
3. The generic XML engine in `MaintainableBase.from_xml()` / `.to_xml()`
   (`src/ddi_l/models/base.py`) drives serialization off those tables, emitting
   children in XSD-declared order. Anything the tables do not name is preserved
   verbatim through the `other_elements` / `other_attributes` passthrough, so
   round-tripping never drops content.
4. Hand-written classes in `src/ddi_l/models/*.py` inherit the generated bases
   and add only helpers, validation, and convenience constructors.

### Regenerating models

```bash
uv run python -m codegen.generate_model_bases
```

CI includes a drift check that fails if generated code differs from what the
XSD would produce:

```bash
uv run python -m codegen.generate_model_bases
git diff --exit-code src/ddi_l/models/_generated/
```

Never edit files under `_generated/` by hand.

### Coverage audit

`uv run python -m codegen.coverage_audit` regenerates
`codegen/COVERAGE_AUDIT.md`, which measures how much of the XSD the generated
layer exposes as named fields versus preserves through passthrough.

## Supporting a new DDI version

This section exists so the next person does not have to reverse-engineer what
is tied to a DDI version. It is deliberately a decision framework rather than a
migration script: DDI 4.0 is not fully released, and a step-by-step plan
written against a specification that has not landed would be fiction.

### What is actually version-coupled

The single most misunderstood thing about this package:

!!! warning "Validation is multi-version. The model layer is 3.3-only."
    `doc.validate(version="3.1")` genuinely works. `ddi_l.models.*` is a
    **DDI 3.3 model** that happens to also validate 3.1 and 3.2 documents.
    Adding `"3.4"` to `SUPPORTED_SCHEMA_VERSIONS` would buy you validation and
    nothing else.

| Coupling point | Where | Notes |
| --- | --- | --- |
| Bundled XSDs | `src/ddi_l/schemas/ddi/v3_1/`, `v3_2/`, `v3_3/` | Shipped in the wheel; resolve via `importlib.resources` |
| Supported versions | `_schema_versions.SUPPORTED_SCHEMA_VERSIONS` | Drives `normalize_version()` and the CLI's `--version` |
| Namespace templates | `_schema_versions._SCHEMA_NAMESPACE_TEMPLATES` | Assumes every namespace is `ddi:{module}:{suffix}` |
| Archive checksums | `_schema_versions.SCHEMA_ARCHIVE_CHECKSUMS` | SHA-256 per release; verified on download |
| Schema refresh | `schema_sync.update_schema_package()` | Downloads and rewrites a `v3_x/` tree |
| Version detection | `schema_loader/_versions.py` | Infers the version from a document's namespace or `schemaLocation` |
| **Codegen entry point** | `codegen/xsd_introspect.py` | **Hardcoded to 3.3**: `SCHEMA_DIR = .../v3_3`, `ENTRY_SCHEMA = instance_3_3.xsd`, and a literal namespace map |

### Path A: a new DDI 3.x minor release

This path is well-trodden; 3.1 and 3.2 were both added this way.

1. Record the release archive's SHA-256 in `SCHEMA_ARCHIVE_CHECKSUMS`.
2. Run `update_schema_package("3.x")` to populate `src/ddi_l/schemas/ddi/v3_x/`.
3. Add the version to `SUPPORTED_SCHEMA_VERSIONS`.
4. Confirm the `ddi:{module}:{suffix}` convention still holds. If the release
   adds a namespace, `tests/test_schema_versions.py` will fail: it derives the
   expected set from the shipped XSDs rather than trusting the hand-written
   list.
5. Decide **explicitly** whether the generated model layer moves to the new
   version. It is not automatic and it is not free: regenerating against a new
   XSD changes `_FIELD_XML_MAP`, `_ATTR_XML_MAP` and `_ELEMENT_ORDER`, which
   changes serialized output, which invalidates every golden fixture under
   `src/ddi_l/examples/tests/fixtures/`. Treat it as a breaking change.

### Path B: DDI 4.0

Do not assume this is Path A with a bigger number. This section records what
the **DDI Lifecycle 4.0 beta 4** model says, read from tag `v4.0-beta.4`
(January 2026) of [ddialliance/ddimodel](https://github.com/ddialliance/ddimodel),
the release the DDI Alliance put forward as the
[last beta before public review](https://ddialliance.org/news/ddi-lifecycle-v4.0-beta-4-review).
These are facts about a beta: recheck each one against the final release before
building on it.

**Generate from the model, not the XSD.** 4.0 is model-first. Its source is a
set of CSV files maintained with COGS (the DDI Alliance's Convention-based
Ontology Generation System), and XML Schema is one of about a dozen formats COGS
generates from them, alongside JSON Schema, OWL, SHACL, ShEx, UML XMI, LinkML
and a C# library. `codegen/xsd_introspect.py` could introspect the published
XSD, but the CSVs carry more:

| Source | What it holds |
| --- | --- |
| `ItemTypes/<Name>/<Name>.csv` | 172 item types (the identifiable objects), one row per property with its type and cardinality |
| `CompositeTypes/<Name>/<Name>.csv` | 320 structured value types |
| `ItemTypes/<Name>/Extends.<Base>` | Inheritance: 72 item types extend `Versionable`, 42 `Maintainable`, the rest one of nine other abstract bases |
| `DeprecatedNamespace`, `DeprecatedElementOrAttribute` columns | For 2,325 of the 2,631 properties, the 3.3 namespace each came from and whether it was an element or an attribute; the other 306 are new in 4.0 |
| `Topics/` | Eight groupings: Agent, Classification, Data Capture, Data Description, Foundational and Study, plus the catch-alls "All Content Items" and "Non-Packaging Items" |

The `Deprecated*` columns matter most to this package: the 3.3 to 4.0 mapping
is part of the model, not something to reverse-engineer.

**The namespace convention does not survive.** The official build publishes the
XSD into one namespace, `ddi:instance:4_0` (`cogs publish-xsd ... --namespace
"ddi:instance:4_0"` in `build/build-windows.bat`), where 3.3 has seventeen.
`_build_release()` formats every namespace from a single `ddi:{module}:{suffix}`
template, and the generator writes one Python module per namespace, so neither
carries over. 4.0 needs its own release description, and the generated modules
need another grouping key: the model's topics, or each type's majority 3.3
namespace from the `Deprecated*` columns, which would keep today's module names.

**Containment becomes reference.** A property whose type is an item type is a
reference, and 635 properties are. A 4.0 `VariableScheme` lists
`VariableReference`s instead of containing `Variable` elements, so items stand
alone and schemes point at them. The hand-written models assume 3.3 nesting (a
`Document` walks `StudyUnit` → `LogicalProduct` → `VariableScheme` →
`Variable`), which makes this the change with the widest reach, well beyond any
rename.

**Identification.** Every 4.0 item has a required `URN` as well as `Agency`,
`ID` and `Version` (`Settings/Identification.csv` and
`Identification.Mixin.csv`). The 3.3 reference machinery maps onto this, but
the URN is no longer optional.

**A successor, with a long overlap.** The DDI Alliance describes 4.0 as the 3.3
content in a structure that supports several syntaxes, so it succeeds 3.3
rather than sitting beside it the way DDI-CDI does. 3.3 files will be in use
for years, so the conclusion is unchanged: add a second model package next to
the existing one rather than migrating `ddi_l.models`, which would break every
consumer for no benefit to people who still have 3.3 data.

**Round-trip fidelity is still open.** The `other_elements` /
`other_attributes` passthrough and the golden fixtures are the guarantees this
package is built on. The model says nothing about how they carry over; answer
that before prototyping.

#### Suggested order of work

1. **Wait for the final release.** Beta properties and types can still change.
2. **Validation only.** Bundle the 4.0 XSD, add a release entry that bypasses
   the 3.x namespace template, teach `schema_loader/_versions.py` the
   `ddi:instance:4_0` namespace, and add `"4.0"` to
   `SUPPORTED_SCHEMA_VERSIONS`. This is Path A plus that one exception, and it
   gives users `validate(version="4.0")` without touching the models. Take the
   file names and entry schema from the published package; they are not in the
   model repository.
3. **Models.** Add a second front end to `codegen/` that reads the COGS CSVs at
   a pinned `ddimodel` tag and writes generated bases into a separate package
   (for example `ddi_l.models_v4`), reusing the type mapping in
   `generate_model_bases.py`. Leave the 3.3 pipeline untouched.
4. **Conversion.** Build a 3.3 ↔ 4.0 property map from the `Deprecated*`
   columns and base conversion on it. The 306 new properties need decisions by
   hand.

### Invariants to defend, whichever path is taken

These are what keep a future migration contained instead of a rewrite:

- **Everything generated stays behind `src/ddi_l/models/_generated/`** and is
  consumed only as base classes. Hand-written code must never import generator
  internals. This seam is why swapping the generator is a contained project.
- **The codegen drift check stays green.** Regenerating on a clean tree must be
  a no-op, so a schema refresh and a generator change are distinguishable in
  review.
- **`SCHEMA_ARCHIVE_CHECKSUMS` stays populated**, for the same reason.
- **One namespace list.** `codegen/xsd_introspect.py` and `_schema_versions.py`
  both enumerate the DDI namespaces; `tests/test_schema_versions.py` checks
  them against the bundled schemas. Run it if you touch either.

### Synthetic namespaces, and the rule that governs them

`_schema_versions._SYNTHETIC_NAMESPACE_TEMPLATES` declares
`urn:ddi-l:extension:process:1` and `urn:ddi-l:extension:methodology:1`. **No
DDI Lifecycle release declares either.** They hold model types DDI 3.3 does not
define: `Process`, `ProcessStep`, `ProcessControl`, `ProcessMethod`, their
schemes, plus `MethodologyItem`, `MethodologyScheme` and `ReviewEvent`. DDI's
own process vocabulary (`ProcessingEvent`, `ProcessingInstruction`,
`ControlConstruct`) lives in `ddi:datacollection:3_3` and is modelled
separately.

**The rule: a type that has a home in the schema must use it.** Synthetic
namespaces are only for content DDI does not define. `Methodology`, for
example, is a DDI 3.3 element and is written in `ddi:datacollection:3_3`.

`tests/test_namespace_provenance.py` enforces both halves: no model may emit a
`ddi:`-shaped namespace that is neither schema-declared nor registered
synthetic, and no type in a synthetic namespace may have a real element of that
name in the XSDs. Adding a new synthetic type requires listing it explicitly,
so it is a decision rather than an accident.

The synthetic namespaces are deliberately **not** `ddi:`-shaped, so nobody
mistakes them for DDI Alliance namespaces, and they carry no DDI version: every
release maps to the same URI. Version detection uses only the `instance`
namespace and the schema filename.

## Architecture overview

```text
src/ddi_l/
  __init__.py                # Public API: new_study, open_ddi, Document
  document.py                # Document, DDIDocument, DDIFragment, StudyCursor
  _document_mixins.py        # Document behaviour split out by concern
  _document_maintainables.py # Maintainable lookup / attachment helpers
  _document_namespaces.py    # Namespace handling for Document
  models/
    base.py                  # InternationalString, Reference, MaintainableBase
                             # and the generic from_xml / to_xml engine
    _generated/              # Generated field-only bases (do not edit)
    datacollection/          # DataCollection types (the one model subpackage)
    logicalproduct.py        # Variables, code lists, categories, NCubes
    conceptualcomponent.py   # Concepts, universes, conceptual variables
    reusable.py, study.py, archive.py, group.py, physical.py, process.py,
    quality.py, comparison.py, methodology.py, classification.py, ...
  schema_loader/             # Schema resolution, validation, JSON conversion
  schemas/                   # Bundled DDI 3.1 / 3.2 / 3.3 XSDs (CC-BY-4.0)
  examples/                  # Packaged sample instances and fixtures
  validation.py              # High-level validation
  lint.py                    # Lint engine and rules
  cli.py                     # CLI entry point (`ddi`)
  io.py                      # Low-level read/write and streaming helpers
  index.py                   # Identifier index for find() / reference checks
  registry/                  # Maintainable type registry
  schema_sync.py             # Refresh the bundled schema bundle
```

Supporting directories outside the package: `codegen/` (build-time generators),
`tests/`, `benchmarks/`, `demo/`, and `docs/`. None of these are packaged, so
nothing in them may back a console script or be imported at runtime.

## The two XML backends

`lxml` is an optional accelerator installed with `ddi-l[full]`. Whether it is
present must not change what `ddi-l` means by a document, and there is a real
difference in how the two resolve prefixes that is worth understanding before
touching serialization:

- **stdlib `ElementTree`** resolves prefixes at *serialization* time, from a
  process-global registry. A prefix registered while writing one document
  affects every later one in the same process.
- **`lxml`** resolves from each element's `nsmap`, which is **fixed when the
  element is created**. It cannot be rebound in place, which is why
  `apply_namespace_map()` returns a root rather than mutating one.

This asymmetry is the most common source of backend-specific behaviour, so
run the suite on both backends when changing serialization.

### What is guaranteed

- **Documents `ddi-l` authors serialize byte-identically on both backends.**
  Every DDI namespace resolves to its canonical prefix, and declarations are
  hoisted onto the root. `tests/test_backend_parity.py` pins this.
- **Round-tripping never changes content**, on either backend: same elements,
  same qualified names, same attributes, same text.

### What is not guaranteed

Round-tripping a third-party file whose namespaces are laid out differently
from ours (a prefixed root plus per-element `xmlns=` redeclarations, as in
the bundled `Quality_of_Life.xml`) can differ in *prefix spelling* between
the backends. lxml echoes the source layout; the stdlib canonicalises it onto
the root. The documents are semantically identical.

Matching byte-for-byte would mean rebuilding every subtree that carries its
own `nsmap` inside `write()`, a real cost on the hottest path for prefix
cosmetics. Any change here must keep the stdlib backend on the canonical
`c:`/`d:`/`l:` prefixes; measure both backends on `Quality_of_Life.xml` and
`example_instance.xml`.

## Bundled schemas

The DDI XSDs ship inside the package at `src/ddi_l/schemas/` so that validation
works offline from a plain `pip install ddi-l`. Always resolve them through
`importlib.resources` (`resources.files("ddi_l.schemas")`), never through a
path relative to the repository root. A repo-relative path works in a clone
and breaks in an installed wheel.

The schemas are licensed CC-BY-4.0 by the DDI Alliance. `license.txt` and
`readme.txt` are redistributed alongside them to satisfy attribution and must
stay in the distribution.

## Documentation

The documentation site uses MkDocs with the Material theme and bilingual
(EN/FR) support. Pages come in `.en.md` / `.fr.md` pairs: **update both** when
you change user-facing content.

```bash
make docs-serve    # Live preview
make docs-build    # Build and validate
```

Prefer the `make` targets over calling `mkdocs` directly: they set
`NO_MKDOCS_2_WARNING`, without which every invocation prints a multi-line
advisory from the Material for MkDocs authors about MkDocs 2.0.

The logo, favicon and their usage rules are described in
[branding assets](assets/README.md).

The curriculum's [answer keys](curriculum/answer-keys.md) page is generated
by `hooks/answer_keys.py` from the `??? success` answers in each module. Add
or change an answer in the module, never on the answer-key page.

### Documentation toolchain versions

`uv.lock` fixes the exact versions; CI and the deploy both install with
`uv sync --locked --group docs`. `mkdocs` and `mkdocs-material` are capped
below their next major in `pyproject.toml` so a new major is adopted
deliberately; Dependabot opens that update as a CI-tested pull request.
`tests/test_docs_site_config.py` checks that every plugin `mkdocs.yml`
activates has a requirement in the `docs` group.

### The version selector only appears under `mike`

`extra.version.provider: mike` makes the theme fetch `versions.json`, resolving
it as `../versions.json` relative to the site base, because `mike` publishes
each version under `<site_url>/<version>/` and keeps the manifest beside them.

That is right in production and wrong locally. A plain `mkdocs serve` builds no
version, so the base stays `/ddi-l/` and `../versions.json` overshoots to
`/versions.json`, which nothing serves: a 404 on every page load, for a
selector that could not work locally anyway.

`hooks/version_selector.py` drops `extra.version` unless `MIKE_DOCS_VERSION` is
set (the variable `mike` exports when it drives a build. If you need to preview
the selector itself, run `uv run mike serve`, or set the variable by hand.

### Why the build log is short

`mkdocs-static-i18n` logs, at INFO, the entire value it overrides each config
key with, once per language, on every rebuild. For `nav` that is the whole
navigation tree, so a build printed several thousand characters of echoed
configuration around the five lines that matter.

`hooks/quiet_i18n_logs.py` filters exactly those `Overriding`/`Updating … config
…` records. `Building '<lang>' documentation to directory: …` is kept, and
nothing at WARNING or above is touched; a genuine `Unknown '<lang>' config
override` still surfaces. Run `mkdocs serve --verbose` to see everything again.

The filter is attached to the *handler* on the `mkdocs` logger, not to the
plugin's logger. Python consults an ancestor logger's handlers when a record
propagates but not its filters, and the plugin logs from submodules, so a
filter on `mkdocs.plugins.mkdocs_static_i18n` silently does nothing.

### `VIRTUAL_ENV does not match the project environment path`

A uv warning, not a project setting: nothing in this repository chooses an
environment path. It means your shell has one virtualenv active while uv
resolves the project's to somewhere else, usually because
`UV_PROJECT_ENVIRONMENT` is set in your profile. Either unset it, point it at
this repository's `.venv`, or pass `--active` to make uv use whatever is
currently activated.

## Releasing

Releases are published to PyPI by `.github/workflows/publish.yml` using
[trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC, no API
token), with PEP 740 attestations.

### One-time setup

1. On [PyPI](https://pypi.org/manage/account/publishing/) and
   [TestPyPI](https://test.pypi.org/manage/account/publishing/), add a pending
   trusted publisher for project `ddi-l`: owner `pbisson44`, repository `ddi`,
   workflow `publish.yml`, environment `pypi` (TestPyPI: `testpypi`).
2. In the GitHub repository settings, create the `pypi` and `testpypi`
   environments. Protect `pypi` with required reviewers.

### Each release

1. Set the version in `pyproject.toml` and `CITATION.cff`, and set
   `date-released` in `CITATION.cff` to the release date.
   `tests/test_release_metadata.py` checks that they agree.
2. Date the heading in `docs/release-notes.en.md` and `docs/release-notes.fr.md`.
3. Run the local gate: `uv run make release-check` and the full test suite.
4. Dry run: trigger **Publish to PyPI** from the Actions tab with target
   `testpypi`, then install from TestPyPI in a clean environment:

    ```bash
    pip install --index-url https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple/ ddi-l
    ```

5. Publish a GitHub Release with tag `vX.Y.Z`. The workflow builds, checks
   that the tag matches the packaged version, and uploads to PyPI; the docs
   workflow publishes the versioned documentation.

## Submitting changes

1. Fork the repository and create a feature branch.
2. Write or update tests alongside code changes.
3. Update both the English and French pages for user-facing changes.
4. Run the quality gates listed above.
5. Commit with clear messages describing the intent.
6. Open a pull request with a summary and related issue references.
