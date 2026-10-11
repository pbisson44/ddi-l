---
description: >-
  What changed in each ddi-l release, including breaking changes while the
  version is 0.x.
---

# Release notes

## 0.1.1

### Colectica exports

- **Read, edit and write Colectica `FragmentInstance` exports.**
  `ddi.open_fragment()` opens one; `DDIFragment.items()`, `get()`,
  `top_level_item()`, `put()` and `remove()` work with its items as typed
  models; `DDIFragment.save()` writes Colectica Designer's exact layout (UTF-8
  with a byte-order mark, one item per `<Fragment>`, each item declaring its
  module as the default namespace, attributes in schema order), so an export
  opened and saved comes back byte for byte. `DDIFragment.from_items()` builds
  a new export with what Colectica writes on every item. Also
  `write_ddi(..., layout="colectica")`, `ddi roundtrip --layout colectica` and
  the `ddi_l.colectica` module. See *Work with Colectica exports*.
- **A typed model for every fragment item type.** All 161 item types a DDI 3.3
  fragment can carry now parse with `MaintainableBase.from_xml`; the 91 without
  a hand-written class get one from `ddi_l.models.items`. A test builds a
  schema-valid sample of each from the XSDs and checks it round-trips
  exactly.
- **`version_date`** reads and sets `versionDate` on any item.

### Load DDI from spreadsheets

- **Bulk-load a study's metadata from CSV files, a zip of them, or an Excel
  workbook.** One
  table per kind of item, rows linked by `id`, covering what most
  organizations document:
  - the study, its groups, organizations and people (`studies`, `groups`,
    `organizations`, `individuals`);
  - concepts, universes, unit types and the variable cascade
    (`conceptual_variables`, `represented_variables`, `variables`);
  - code lists, including hierarchical classifications (`codes.parent`);
  - questions with instructions, grids, blocks and question groups, worded
    per language and per audience (`question_texts`);
  - questionnaires and their flow (`instruments`, `flow`): sequences,
    statements, if-then-else and loops;
  - variable groups, data files (`datasets`) and n-cubes;
  - methodology, processing events, quality statements and comparison maps.

  Text goes in one column per language (`label@en`, `label@fr`) and
  `custom:<name>` columns are stored as `r:UserAttributePair`.
  `ddi_l.tables.load_tables()` returns typed models; `to_fragment()` writes a
  Colectica `FragmentInstance` holding every item, valid against the DDI 3.3
  schema, and `to_study()` a DDI study for tables a study document can hold.
  The items the rows imply are written too: a data collection per study,
  sequences for the flow, a data relationship per data file. Identifiers are
  derived from the agency and your ids, so loading again gives the same
  items. Every problem is reported at once with its file, row and column.
  Also `ddi tables template` and `ddi tables import`, and
  `Document.attach()` to place an item built elsewhere into a study. Excel
  workbooks are read and written with the standard library: no new
  dependency. See *Load DDI from spreadsheets* and *Spreadsheet templates*,
  which has blank and example templates to download.

### HTTP API

- **Colectica exports round-trip byte for byte.** `POST
  /v1/roundtrip?layout=colectica` writes a `FragmentInstance` as Colectica
  Designer does, so an unchanged export comes back identical and a diff shows
  only what a parse lost. Without it, every Colectica file looked changed.
- **Load metadata tables over HTTP.** `POST /v1/tables/import` takes an
  `.xlsx` workbook or a `.zip` of CSV files and answers with a Colectica
  `FragmentInstance` (or, with `?study=`, a study). Tables with problems are a
  `422` whose `extra` lists every problem with its file, row and column.
  `GET /v1/tables/template` downloads the blank or example tables, and
  `GET /v1/tables` describes every table and column as JSON. Uploads are read
  in memory, within limits on their size, number of files, and rows and
  columns.
- **`load_tables()` also reads a zip of CSV files, or the bytes of a workbook
  or a zip.** So does `ddi tables import`.

### Fixed

- **A study in a fragment no longer warns about its references.**
  `DDIFragment.from_items()` and `put()` reported every reference of a
  `StudyUnit` as unresolved, since in a fragment the items it references sit
  in fragments of their own.
- **The typed models no longer lose content.** Reading an item and writing it
  back used to drop `versionDate`, `r:VersionResponsibility` and the
  `r:BasedOnObject` lineage on hand-written models (Variable, CodeList,
  RepresentedVariable, DataRelationship, StudyUnit and others); split a
  bilingual `r:Label` or name into one element per language; drop
  `audienceLanguage` and `d:ConditionalText` from question text, user
  attribute pairs and attributes inside references, attributes on
  `r:URN`/`r:ID`, controlled-vocabulary attributes, and the scheme-level
  metadata of inline schemes; and wrote some content out of schema order
  (QuestionItem, Sequence), which the schema rejects.
- **`DDIFragment.from_items()` drops every restated reference URN.** It
  skipped the reference after each one it removed, so an item with several
  references kept some `r:URN`s Colectica does not write.
- **References are written as read.** A reference read without an `r:URN`
  no longer gains one; a reference built in code still does.
- **`xs:boolean` `"1"` is true.** Several wrappers read it as false and wrote
  `"false"`. Values keep their original spelling while unchanged.
- **Identifiers read from a file are kept.** `DataCollection` rewrote
  non-UUID `r:ID`s (its own and those of everything inside it) into generated
  UUIDs, breaking references from other items; it now does so only for
  objects built in code.
- **Validation of fragments no longer forgives real errors.** An error inside
  a fragment's `StudyUnit` (and a few other real DDI items) was passed over,
  and validation stopped there, hiding any error after it. Only the library's
  own extension types are exempt now, and every error is checked.
- `ConceptualComponent` always writes concepts, universes, conceptual
  variables and unit types inside their schemes; written bare they were
  invalid.
- `d:Methodology` writes `d:MethodologyName` in the DDI 3.3 namespace.
- `r:ExternalURLReference`, `r:ExternalURNReference` and a few other
  elements named `*Reference` are no longer read as DDI references (which
  emptied them).
- A schema-valid value that does not parse as its declared number type no
  longer stops an item from loading.
- Building a fragment is linear in its size (it was quadratic: 53 s for a
  4,478-item export, now under 3 s).

### Documentation

- **One colour scheme that works in every mode.** The site uses one brand
  blue for the header, links and buttons, with orange only for the keyboard
  focus ring, and every text colour meets WCAG AA in light, dark and high
  contrast. Dark mode now uses the site's own colours rather than Material's
  defaults, and its buttons are readable: the outline buttons were 2.3:1, and
  a download button in a page was 1.1:1, navy on black. High contrast has a
  black header, visible navigation tabs and readable code, and its notes and
  tips are dark like the page instead of white boxes whose tables were white
  on white. The
  logo follows the header colour instead of drawing in black, and the palette
  menu sits in the header beside the light/dark toggle instead of overlapping
  the search icon on phones. The three colour-vision palettes are gone: the
  blue-and-orange scheme already suits those readers.
- **Links without a version no longer 404.** The README and issue template
  link through `/latest/`, and the site root now serves a `404.html` that
  sends any unversioned path (`/ddi-l/server/`) to the same page under
  `/latest/` and maps renamed curriculum pages to their new names.
- **Install from PyPI everywhere.** Pages that said `pip install .` or
  `pip install -e .` now say `pip install ddi-l`, and the install tabs add
  `uv add ddi-l`.
- **One place to learn.** The site is organized as Learn (the curriculum),
  How-to guides, Reference and About. The authoring tutorial, training labs
  and persona tracks are folded into the curriculum, which now has a single
  set of learner profiles and an automation track.
- **Curriculum order.** Opening files and command-line validation move up to
  Modules 6 and 7, and Module 3 now checks its work with `doc.validate()` and
  `doc.lint()`, so learners validate from the start. Modules 6 to 13 become 8
  to 15.
- **Answers under each exercise.** Every exercise has a collapsible answer.
  The answer-key page for instructors is generated from the modules, so it can
  no longer drift from them.
- **Homepage.** A lint-clean first example, what DDI is, DDI 3.1, 3.2 and 3.3
  scope, a study diagram, a Learn tile, an R / HTTP API tile and a "Cite ddi-l"
  section. Every page now has its own search description.

## 0.1.0

The first release of `ddi-l`: a Python toolkit for creating, reading,
updating, and validating [DDI Lifecycle 3.3](https://ddialliance.org/Specification/DDI-Lifecycle/3.3/)
XML documents, with a simple CRUD API over an XSD-generated model layer.

### Authoring

- **Simple CRUD API**: `ddi.new_study()`, `ddi.open_ddi()`, and the
  `Document` class with `add_question()`, `add_variable()`, `add_concept()`,
  `add_universe()`, `add_code_list()`, `add_item()`, `find()`, `remove()`,
  `save()`, and `validate()`. Every `add_*` helper takes an optional `label=`
  (and `label_lang=`), so an item can be labelled where it is created rather
  than in a second pass. That is the difference between output that lints clean and
  output that warns about itself.
- **Generic `add_item()` / `items()`**: 30 DDI item types (QuestionItem,
  Variable, Category, Instrument, Concept, Universe, and more) through a single
  type registry.
- **Variable representations**: `Variable.set_numeric()`, `set_coded()`,
  `set_text()`, and `set_datetime()` declare what kind of values a variable
  holds, with optional numeric ranges (`low_inclusive` / `high_inclusive`),
  `missing_values`, `blank_is_missing_value`, or a code-list reference. The
  setters chain onto `add_variable()`.
- **Custom properties**: `set_property()`, `get_property()`, `properties`,
  and `remove_property()` on any DDI item.
- **Versioning**: `increment_major_version()`, `increment_minor_version()`,
  `increment_subversion()`, version rationales, and version responsibility.
- **Multilingual support**: a `lang=` parameter on every `add_*` method, and
  `InternationalString` for additional translations.

### Study structure

- **Multi-study series**: `doc.add_study()` adds further studies to the
  group. `doc.study(identifier)` returns a `StudyCursor` whose `add_variable()`,
  `add_question()`, and other `add_*` helpers target that specific study, so
  non-primary studies are editable through the high-level API. `doc.study()`
  with no argument targets the primary study.
- **Study groups**: `doc.add_group()` organizes a study into a `<g:Group>`
  (a study series or publication package). The document stays fully editable,
  and group-organized files open and round-trip.
- **Instance-level packages**: `doc.add_resource_package()` and
  `doc.add_local_holding_package()` attach a `ResourcePackage` (reusable
  metadata) or a `LocalHoldingPackage` (a local holding of a deposited study,
  referencing the primary study by default) directly on the `DDIInstance`;
  `doc.resource_packages` / `doc.local_holding_packages` read them back.
- **Archive**: `doc.add_archive()` attaches an `Archive` module (archive
  lifecycle metadata) to the primary study; `doc.archives` reads them back.
- **Translation information**: `doc.add_translation_information(languages=...,
  description=...)` sets the instance's `TranslationInformation`;
  `doc.translation_information` reads it back.
- **Comparisons**: `doc.add_comparison()` records harmonization maps between
  items across studies or versions: `add_variable_map()`, `add_concept_map()`,
  `add_managed_item_map()`, `add_representation_map()`, a `correspondence()`
  builder, and `source_scheme` / `target_scheme` / `correspondence` arguments
  on the map helpers.
- **DDI profiles**: `doc.add_ddi_profile()` attaches a `DDIProfile` declaring
  which DDI elements a system uses, via `add_used()` / `add_not_used()` XPath
  statements.

### Data description

- **Data relationships**: `doc.add_data_relationship()` builds a
  `DataRelationship` whose `add_logical_record()` declares which variables make
  up one case (the rectangular-file default).
- **NCubes**: `doc.add_ncube()` builds a multidimensional cube;
  `add_dimension(variable_ref)` adds an axis, `add_measure(variable_ref)` adds a
  measured value, and `add_attribute()` adds a qualifying variable.
  `add_coordinate_region()` and `add_dimension_value()` describe a region of a
  cube, and `add_attribute(..., attachment_region=)` attaches to one.
- **Physical instances**: `PhysicalInstance` is a first-class `add_item` type
  at the study level, describing a concrete data file with `set_data_file()`,
  `set_record_count()`, and `set_citation_title()`.
- **Record layouts**: `doc.add_record_layout()` maps variables to positions in
  a data file via `add_data_item(variable_ref, start_position=, width=)`, which
  also accepts `storage_format`, `delimiter`, and `decimal_positions`. Pass
  `logical_record=` to tie the backing structure to a modeled logical record.
  `PhysicalStructure.link_logical_record(..., key_variable=)` declares a
  segment key.
- **Inline datasets**: `doc.add_dataset()` stores data values directly in the
  document, in `ItemSet` (`add_item_value()`), `RecordSet`
  (`set_variable_order()` / `add_record()`), or `VariableSet`
  (`add_variable_item()`) form.

### Questionnaires

- **Flow constructs**: `QuestionConstruct`, `Sequence`, `IfThenElse`,
  `StatementItem`, `ComputationItem`, and `Loop` are first-class `add_item()`
  types, stored in a `ControlConstructScheme` that is built, serialized, and
  round-tripped automatically, and linked to one another with `.to_reference()`.

### Validation and quality

- **Offline schema validation**: the DDI 3.1, 3.2, and 3.3 XSDs ship inside
  the package, so `doc.validate()` and `ddi validate` work with no network
  access and no separate download.
- **Reads DDI 3.1, 3.2 and 3.3**: `read_ddi()`, `ddi validate`, `ddi lint`,
  `ddi to-json` and `ddi roundtrip` detect the version a document declares.
  The `Document` authoring API and the typed models target DDI 3.3; 3.1 and
  3.2 documents are worked with as XML through `DDIDocument.root`.
- **Lint engine**: `ddi lint` and `Document.lint()` check reference
  integrity, missing labels and citation completeness. The label rule follows
  the schema: it only asks for a label where the element's content model has
  an `r:Label` slot (174 of DDI 3.3's 1247 elements). The citation-language
  rule matches language ranges per RFC 4647, so a required `en` is satisfied by
  `en`, `en-CA` or `en-Latn-CA`, but not by `eng`.
- **Lint-clean output by default**: the `Document` API labels the modules,
  schemes and physical wrappers it creates, and every `add_*` helper accepts
  `label=`. `set_scheme_label()` labels any generated scheme wrapper. Documents
  you *parse* are never modified.
- **Lint defaults suit a published library**: the agency allow-list is
  opt-in (`configure_lint(allowed_agencies=[...])` or `--allowed-agency`); a
  *missing* agency is always an error. `ddi lint` exits non-zero on errors
  only; pass `--fail-severity warning` for a strict gate.
- **Labels only where the schema allows them**: label support is derived
  from the XSDs. Setting a label on a type with no `r:Label` slot warns
  instead of producing an invalid document.
- **Reference checks**: `Document.save()` reports references to items the
  study does not contain as a single `DDIReferenceWarning`.
- **Clear errors**: malformed XML raises `DDIParseError` with the parser's
  line and column; unresolvable references raise `DDIReferenceError` (a
  `LookupError`); duplicate identifiers raise `DuplicateIdentifierError`, and
  empty or non-string names are rejected when an item is added. Schema
  failures raise `SchemaValidationError`, a `DDIValidationError`, whose
  `.issues` carries the individual problems.
- **Examples that pass our own gates**: the bundled `example_instance.xml`
  and `Quality_of_Life.xml` are schema-valid and free of lint errors;
  `example_instance.xml` has no findings at any severity.
- **`Methodology` uses DDI's own namespace**: `<Methodology>` is written in
  `ddi:datacollection:3_3`, as DDI 3.3 declares it.
- **Extension types are visibly ours**: the few `Process` and `Methodology`
  helper types that no DDI Lifecycle release defines serialize into
  `urn:ddi-l:extension:*`, so nothing can be mistaken for an official DDI
  namespace.
- **Round-trip fidelity**: unknown XML elements and attributes are preserved
  when opening and re-saving files.
- **The `lxml` backend is a speed choice, not a dialect**: documents `ddi-l`
  authors serialize to byte-identical output with and without `ddi-l[full]`.
  A third-party file whose namespaces are laid out differently (a prefixed
  root plus per-element `xmlns=` redeclarations, as in `Quality_of_Life.xml`)
  can differ in prefix spelling between backends; its content is identical.

### Performance

- `import ddi_l` loads names on first use, so importing the package and
  starting the `ddi` command take a few hundredths of a second.
- `read_ddi()` builds its resolver index lazily.
- With `ddi-l[full]`, validation first checks the document with libxml2 and
  runs the detailed xmlschema validator only when that check fails: valid
  documents validate in milliseconds, and reported issues are identical on
  both backends.
- `iter_variables()`, `iter_questions()` and `iterparse_ddi()` stream large
  documents and yield fully populated objects.
- See [Performance](performance.md) for measured timings.

### HTTP API

- **Optional Litestar service**: `pip install 'ddi-l[server]'` then
  `ddi serve` exposes validate, lint and convert over HTTP, with OpenAPI docs at
  `/schema`. Every endpoint is a thin wrapper over `ddi_l.operations`, which the
  CLI also calls, so the two cannot disagree about whether a document is valid.
- **Self-describing OpenAPI**: `/schema` serves Swagger UI, and a browser
  opening the root is redirected there. Every endpoint declares its request
  body, query parameters and a typed response schema with a captured example;
  "Try it out" arrives prefilled with a valid DDI instance.
- **Service-appropriate defaults**: a 32 MiB request body cap, a bounded
  number of concurrent jobs (`--max-jobs`, `503` beyond it), the default
  schema preloaded at startup, no disk writes, CORS off unless origins are
  named, and the same XML hardening as the library.
- **JSON-LD output**: `POST /v1/convert/jsonld` and `ddi to-jsonld` render a
  study as linked data using the DDI Alliance's own DDI-RDF Discovery
  vocabulary ("Disco"), with Dublin Core and SKOS for labels and DDI URNs as
  IRIs. Covers DDI's discovery subset and is one-way by design, as the Disco
  specification intends; `to-json` remains the lossless, round-trippable format
  (XML to JSON and back returns the bytes it was given, and so does
  `/v1/roundtrip`).
- **`ddi_l.operations`**: the transport-neutral core, usable directly when
  embedding ddi-l in another application.

### Model layer

- **XSD-driven model generation**: every model class is generated from the
  official DDI 3.3 XSD, the single source of truth for fields, element
  ordering, namespaces, and documentation. All 508 XSD complex types are
  covered.
- **Generic XML engine**: `from_xml()` / `to_xml()` driven by the generated
  `_FIELD_XML_MAP`, `_ATTR_XML_MAP`, and `_ELEMENT_ORDER` tables, emitting
  children in XSD-declared order.
- **Stable DDI namespace prefixes**: output uses the canonical `r:`, `s:`,
  `d:`, `l:`, `c:`, `a:`, `p:`, `pr:` (ddiprofile), and `prc:` (process)
  prefixes rather than generated `ns0`/`p0` names, and serialization prefers a
  namespace's registered prefix over an auto-generated one.
- **Namespace constants**: exported for every DDI module, including
  `DDI_PROFILE_NS` and `DATASET_NS`.
- **Typed**: ships `py.typed`; the public API is fully annotated.

### Tooling and distribution

- **CLI**: `ddi validate`, `ddi lint`, `ddi to-json`, `ddi to-jsonld`,
  `ddi from-json`, `ddi roundtrip`, `ddi versions`, and `ddi serve`. Commands
  take `-o/--output` and `--ddi-version`; `ddi validate --format json` prints
  a JSON array (empty when valid) for scripts.
- **Optional lxml backend**: `pip install ddi-l[full]` enables faster parsing
  of large documents.
- **Generated API reference** built from the source docstrings, alongside the
  guides.
- **Every documented code sample is executed in CI**, including the R
  examples.
- **Python 3.11, 3.12, 3.13, and 3.14** supported and tested in CI.
- **PyPI publishing** via GitHub OIDC trusted publishing.
- **Bilingual documentation** in English and French, including a guide to
  [using ddi-l from R](r-users.md) through reticulate.
- **Training curriculum**: a 16-module progressive course with exercises,
  quizzes, an instructor guide, answer keys, and a bilingual cheat sheet.
