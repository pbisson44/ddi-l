---
description: >-
  What changed in each ddi-l release, including breaking changes while the
  version is 0.x.
---

# Release notes

## 0.2.0 (unreleased)

### Behaviour changes

- **The native XML core comes with ddi-l.** `pip install ddi-l` also installs
  `ddi-l-native`, and ddi-l reads and writes XML with it before lxml, so an
  installation with the `full` extra now uses the native core. The results
  are the same; set `DDI_L_XML_BACKEND=lxml` to keep lxml. On a platform with
  no compiled wheel, pip installs a pure-Python stand-in and nothing changes;
  see [which extras you need](installation.en.md#extras-when-you-need-one).
- **A file read is written back as read.** `write_ddi()`, `save()`,
  `to_xml()`, `ddi roundtrip` and `POST /v1/roundtrip` write a document read
  from a file or bytes with every unchanged element as it was read, byte for
  byte: its quotes, character references, CDATA, comments, prefixes and
  indentation. Only new or changed elements are laid out, like the file
  around them (Colectica's layout in a `FragmentInstance`, the file's own
  indentation otherwise). Elements are matched by content, so an item moved,
  copied or rebuilt from its model unchanged keeps its bytes. Before, only a
  `FragmentInstance` already in Colectica's layout came back unchanged, and a
  `DDIInstance` came back in this library's layout. A `DDIInstance` whose
  file binds a DDI namespace to another prefix (`p0`, `ns1`) is still laid
  out afresh by `save()` and `to_xml()`, with the canonical prefixes (`c`,
  `s`...). Pass `layout="colectica"` or `layout="default"` (`--layout`,
  `?layout=`) to lay the whole file out as before; `DDIFragment.save()` now
  defaults to `layout=None` for the same reason. A document keeps the bytes
  it was read from, so it holds the file's size in memory as well.
- **Schema validation reports every error.** `validate()` and everything
  built on it (`ddi validate`, `Document.validate()`, `POST /v1/validate`)
  reported the first schema error and stopped. They now report each one,
  then the warnings. An error found before the schema is read, such as a
  missing identification, is still reported alone. `validate(max_issues=)`
  stops after that many errors with a warning saying so; the HTTP API stops
  at `ServerConfig.max_schema_issues` (100 by default).
- **`conform` decides gates and edits exactly when the `logic` extra is
  installed.** A gate written differently that always agrees with the
  spec's (`PetCount > 0` and `PetCount >= 1`, for a question whose domain has
  no decimals) is no longer `spec.gate.different`, and a page gate is found
  the same way. A `spec.gate.different` or `spec.edit.different` finding
  names a respondent the two disagree on, in its message ("(they differ when
  PetCount is 1)") and in a new `example` field, which JSON output has only
  when it is set. The spec's response domains and variable types say what
  each name is. `ddi conform --semantics syntactic` (`conform(semantics=
  "syntactic")`) compares normal forms, as before; `--semantics smt` needs
  the extra.
- **`equivalent()` calculates when the `logic` extra is installed.** Gates
  written differently that always agree are equivalent: `x + 1 > 3` and
  `x > 2`. `equivalent(exact=False)` compares normal forms only, as before;
  without the extra nothing changes.
- **Lint configuration is per call.** `run_lint()`, `run_profile()`,
  `document.lint()` and the `validate_*()` functions take a `configuration`
  from the new `lint_configuration()`, for that call alone; `configure_lint()`
  still sets the default for calls given none. `ddi lint` no longer changes
  the process default, so calling `cli.main()` twice in one process no longer
  carries the first call's options into the second.
- **Scoped settings stay in their thread or task.** `ddi.configured()`
  changed the process-wide default for the length of its `with` block, so
  other threads saw it. It now applies to its own thread or task only;
  `ddi.configure()` still sets the default for every thread.
- **ddi-l no longer writes ElementTree's namespace registry.** On the
  standard library backend, the prefixes a document registered went to
  `ElementTree.register_namespace`, which the whole process shares: other
  code using ElementTree saw them, and so did other threads. They are now
  kept for the current thread or task, and the writer names namespaces from
  them. Output in one thread is unchanged; a document built in one thread
  and written with a layout in another writes `ns0`, `ns1`... for prefixes
  registered only in the first.
- **The validation backend is chosen per call.** `schema_loader.validate()`
  takes `backend="python"` or `"lxml"`, and the new
  `schema_loader.validation_backend()` scopes one to a `with` block, in its
  own thread or task. `set_validation_backend()` still sets the application
  default, which the new `get_validation_backend()` returns.
  `VALIDATION_IMPLEMENTATION` now names the best backend available, fixed at
  import; it no longer follows `set_validation_backend()`.
- **`lint.ALLOWED_AGENCIES` and `namespaces.NAMESPACE_PROFILES` are
  read-only.** `ALLOWED_AGENCIES` was a set an application could change in
  place, which the agency rule read when the default configuration had no
  list. It is now a frozen view of the default configuration: set the list
  with `configure_lint(allowed_agencies=[...])`.
- **A fragment is linted as a fragment over HTTP too.** `POST /v1/lint` and
  `POST /v1/validate` linted a `FragmentInstance` inside a made-up
  `DDIInstance`, so a dangling reference was an error there and a warning in
  `ddi lint`, and an allowed-agency list checked the made-up container's
  agency. Both now lint the fragment itself, as `ddi lint` does: a fragment
  whose only problem is a dangling reference is now `valid`.
- **Of two copies of one version, the first counts everywhere.** An export
  that holds an item twice at the same version (a shared ID) named the
  second copy in condition explanations, synopses and `ddi conform`, and the
  first everywhere else; it is now the first throughout.
- **Reference findings are split three ways.** `ddi.reference.integrity`
  matched `(agency, id, version)` exactly, so on Colectica exports it reported
  every late-bound parameter reference (written at version 1 while the
  parameter is at, say, 4) and every `BasedOn` link to the item a copy came
  from. On the bundled Colectica sample it reported 116 references, of which 2
  were really unresolved. Now:
  - a `lateBound="true"` reference resolves to any version of its item;
  - **`ddi.reference.version`** (warning) reports a reference whose item is
    present, but not at the version named, and lists the versions that are;
  - **`ddi.reference.provenance-external`** (info) reports a `BasedOn` or
    user-attribute reference to an item outside the file;
  - `ddi.reference.integrity` keeps the rest, at the same severity as before.
- **A new `info` severity.** `info` findings never fail `ddi lint` unless you
  pass `--fail-severity info`, which is now accepted. `ddi lint` used to
  treat any severity other than `warning` as an error. A finding with a
  severity other than `error`, `warning` or `info` now raises `ValueError`.
- **`run_lint()` without `rules=` runs the default profile** rather than every
  registered rule, so rules meant for a named profile (such as the new
  `colectica-questionnaire`) stay out of `ddi lint`. A rule added with
  `register_rule()` still joins the default profile unless you pass
  `default=False`.
- **A minor or subversion increment refuses a whole-number version.**
  `increment_minor_version()` turned `"6"` into `"6.1"`, a version tools that
  number versions with integers, Colectica among them, may not read. It now
  raises `DDIModelError`; `increment_major_version()` gives `"7"`, and
  `allow_dotted=True` keeps the old behaviour. New items start at `"1"`, so a
  minor bump on one now needs `allow_dotted=True` or a three-part version set
  first. `increment_all_versions()` checks every item before changing any.
- **Parameters and bindings of control constructs are typed.** On
  `IfThenElse`, `Loop` and `StatementItem`, `r:InParameter`, `r:OutParameter`
  and `r:Binding` were kept in `other_elements`, as was `r:InParameter` on
  `Sequence`; they are now in `in_parameters`, `out_parameters` and
  `bindings`. `Sequence.bindings` holds `Binding` objects rather than
  elements, and `OutParameter.representation` holds any representation (it
  took only a code or numeric one; the others were in `other_elements`). The
  lists are typed `list[InParameter | Element]` and so on, `Sequence`'s
  `out_parameters` included (it was `list[OutParameter]`), and still accept
  raw elements; code checked with mypy narrows an item with `isinstance()`
  before using it as a parameter.
- **Parameters and bindings of generated constructs are typed too.**
  `ComputationItem` and `QuestionConstruct` read `r:InParameter`,
  `r:OutParameter` and `r:Binding` as `InParameter`, `OutParameter` and
  `Binding` rather than as elements, and so do an `Instruction`'s
  `in_parameters` and the generic item models that have them (`Split`,
  `SplitJoin`, `RepeatUntil`, `RepeatWhile`, `MeasurementItem`,
  `MeasurementConstruct`, `DevelopmentStep`, `SampleStep`, `SamplingStage`).
  Code that read these values as elements calls `to_xml()` on them; one read
  and written back unchanged is still written as read, and the lists still
  take raw elements. The generic models' annotations still say
  `list[Element]`.
- **A language added to a name or label read from a file joins it.** A
  string built in code used to start a container of its own next to the ones
  read, so adding `fr` to a name read in `en` wrote two `d:ConstructName`
  elements. It now joins the last container read when that container has no
  string in its language, keeping the container's attributes; a second
  string in the same language still starts a new container.
- **`IndividualIdentificationFields.individual_names` holds elements.** An
  `a:IndividualName` is made of parts (`a:FirstGiven`, `a:LastFamily`...),
  not of `r:String`s, but the code generator typed it as international
  strings and dropped the parts. The generator now asks whether a name's type
  derives from `r:InternationalStringType`.
- **Bumping a version refreshes `versionDate`.** On an item that has a
  `versionDate`, every increment sets it to now, in Colectica's format; pass
  `touch=False` to keep the old date. Items without one are unchanged.
- **Neutral conditions use all of Colectica's operator codes.**
  `Operator(0)` is `NONE`, not `UNKNOWN_0`, and a code that was read as an
  unknown one before (`2`, `4` to `6`, `8` to `10`, `13`, `15` to `17`) is
  now a named member. A `ContainsAny` or `ContainsAll` statement with a value
  but no selected codes reads back as unverifiable, where it read as `=`.
  `compile_condition()` writes `!=`, `<`, `<=`, `>=` and `answered()` as
  `Neutral` where it wrote Blaise.

- **A missing or unreadable schema fails loudly.** If the packaged XSD was
  missing or could not be read, validation fell back to a stand-in that only
  checked the root element and the identification fields, so a broken install
  passed invalid files. `get_schema()` now raises `FileNotFoundError` for a
  missing schema and lets xmlschema's own error through otherwise.
- **An error in an `on_register` callback reaches the caller.** The registry
  ignored it. The class is still registered before the callbacks run.
- **The example builder writes to the current folder.** `python -m
  ddi_l.examples.build_and_validate` wrote into the installed package by
  default, and put the package folder itself on `sys.path`, where
  `ddi_l/io.py` could shadow the standard `io` module. `make example` passes
  the packaged paths, so it still refreshes the bundled files.
- **A `FragmentInstance` is written in Colectica's layout by default.**
  `write_ddi()`, `DDIFragment.to_xml()`, `ddi roundtrip`, `ddi from-json`,
  `POST /v1/roundtrip` and `POST /v1/convert/xml` wrote this library's layout,
  so a Colectica export written back through them changed (declaration,
  prefixes, byte-order mark) though nothing was lost. Only `save()` wrote
  Colectica's. Now the root decides: a `FragmentInstance` gets Colectica's
  layout and a `DDIInstance` this library's. `layout="default"`
  (`--layout default`, `?layout=default`) gives the old output, as do
  `pretty_print=False`, `xml_declaration=False` or an encoding other than
  UTF-8, which only that layout has.

### Colectica exports

- **Read, edit and write Colectica `FragmentInstance` exports.**
  `ddi.open_fragment()` opens one; `DDIFragment.items()`, `get()`,
  `top_level_item()`, `put()` and `remove()` work with its items as typed
  models; `DDIFragment.save()` writes Colectica Designer's exact layout (UTF-8
  with a byte-order mark, one item per `<Fragment>`, each item declaring its
  module as the default namespace, attributes in schema order), so an export
  opened and saved comes back byte for byte. `DDIFragment.from_items()` builds
  a new export with what Colectica writes on every item. Every other way of
  writing a `FragmentInstance` uses the same layout by default (see *Behaviour
  changes*), and so does the `ddi_l.colectica` module. See *Work with
  Colectica exports*.
- **A typed model for every fragment item type.** All 161 item types a DDI 3.3
  fragment can carry now parse with `MaintainableBase.from_xml`; the 91 without
  a hand-written class get one from `ddi_l.models.items`. A test builds a
  schema-valid sample of each from the XSDs and checks it round-trips
  exactly.
- **`version_date`** reads and sets `versionDate` on any item.
- **Exports without a byte-order mark round-trip byte for byte.** The
  Colectica layout always wrote a mark. Now `DDIFragment.source_bom` records
  whether the file had one and `save()`, `to_colectica_bytes()`,
  `write_ddi(..., layout="colectica")` and `ddi roundtrip --layout colectica`
  write the same; pass `bom=` to choose.
- **Inline XHTML keeps its spaces.** In `<b>Kind</b> <i>of</i> pet` the
  space between the elements is text. It was read as indentation: lxml read
  "Kindof pet", and the stdlib backend wrote such a file differently. Both
  backends now keep it and write it back as read, with the default layout as
  with Colectica's; whitespace between XHTML blocks is layout. Such a file is
  parsed twice on lxml, so reading it takes up to twice as long.
  A `<br>` separates words, and text under `xml:space="preserve"` is written
  as read.
  `iterparse_ddi()` reads items as `read_ddi()` does. See *Layout* on the Colectica page.
- **`ddi lint --profile colectica-questionnaire`** for Colectica exports. Its
  `colectica.maintainable.labels` accepts an item's name (`ConstructName`,
  `QuestionItemName`, `r:Name`) as well as `r:Label`, provided it holds text.
- **Read, edit and explain Colectica conditions.** `ddi_l.colectica_logic`
  parses the logic Colectica stores in an `r:Command`: the `Neutral` JSON of
  its condition editor (`Condition`, with groups and statements), the fields
  of a `Blaise5DataLookup` (`DataLookup`), and native code kept as text
  (`NativeCondition`). It reads the condition of an `IfThenElse` and of each
  of its `ElseIf` branches, of a `ComputationItem`, and of a `Loop`,
  `RepeatUntil` or `RepeatWhile` (`which=` reaches a `Loop`'s `InitialValue`
  and `StepValue`). An unchanged condition is written back byte for byte,
  and an edited one as Colectica writes JSON. The operator codes (all 18)
  and join codes are Colectica's; a code not listed is kept as read.
  `render_synopsis()` describes a condition from its logic, naming subjects
  after their questions and codes by value, where Colectica's stored synopsis
  can be stale and numbers codes by position. `ddi explain-condition FILE ID`
  shows both, the condition's description, and its used and unused inputs.
- **25 lint rules for Colectica questionnaires**, in the
  `colectica-questionnaire` profile: shared identifiers, dangling bindings,
  malformed, empty, impossible or native-invalid conditions (of every
  `ElseIf` branch and loop as well; a `ComputationItem` with outputs holds a
  program, which may span lines and assign them), unused inputs,
  stale synopses, gates wrapping only part of a page, code domains without a
  code list, domain labels and wording that do not fit the item, missing
  translations, template placeholders, pasted user-interface text, malformed
  or undeclared pipes, duplicate or suspicious lookup fields, lookup outputs
  their field list does not hold, compounded or
  malformed aliases, design notes shown as statements, values read before the
  flow asks or computes them (on each path to a reused page), and gates on one
  answer of a question with several, which Designer's routing view reports as
  broken. Heuristic rules
  report warnings at most; rules depending on an organisation's conventions
  are off until configured with the new `LintConfiguration` options
  (`required_languages`, `known_names`, `ui_chrome_tokens`, ...).
- **`colectica.flow.unreachable`: constructs no respondent reaches.** With
  the `logic` extra, the solver works out each construct's ask-condition, the
  disjunction over the ways to it of the gates' conjunction, with the parts
  of the flow that many paths share encoded once, and reports a construct
  for which no answers meet it (`PetAge > 10 and PetAge < 1`, or a gate inside
  a branch it contradicts). Only the first construct on a way is reported. A
  condition it cannot read may hold or not. Without the extra, a flow with a
  gate gets one `info` finding saying it was not checked.
- **`colectica.flow.read-before-computed` names a respondent.** With the
  `logic` extra, a finding adds a respondent who reaches the item before the
  question or computation ("For example, when PetCount is 0."). When there
  is none, because every way that reaches it first is ruled out, the finding
  is `info`: only Designer's routing view is affected. Each respondent given
  is checked by walking the flow with `evaluate`.
- **`ddi lint --format table`**, `--required-language`, `--known-names FILE`
  and `--lint-config FILE`. `configure_lint()` accepts any `LintConfiguration`
  field by name.
- **A generated lint rule reference.** The *Lint rule reference* page lists
  every registered rule with its severity, profiles and an example finding;
  `register_rule()` takes `severity=` and `example=`, and
  `iter_rule_metadata()` reports them.
- **Edit a questionnaire without leaving its references behind.**
  `DDIFragment.revise()` gives items a new version and, with `cascade`, every
  item pinning them, up to the instrument, leaving late-bound references
  alone; `dry_run=True` returns the plan only. It versions as Colectica does:
  what an item declares (its parameters, its codes) takes the item's new
  version, a reference pinning one of those is re-pointed too, and the items
  of one call share one `versionDate` (`version_date=` sets it). `rationale=`
  records why, as every revised item's `r:VersionRationale`, as Colectica
  records a save's message; the rationale an item carried, which explained its
  previous version, is dropped. New items record the configured
  responsibility. `move_construct()`,
  `insert_construct()` and `wrap_in_condition()` edit sequences and return
  the items to revise.
  `duplicate()` copies an item with new IDs for everything it declares, and
  `repair_shared_identifiables()` (a dry run by default) re-identifies the
  copies of a shared parameter, reporting references it cannot attribute.
- **Typed parameters and bindings.** `InParameter` and `Binding` join
  `OutParameter` in `ddi_l.models`. `IfThenElse`, `Loop`, `StatementItem` and
  `Sequence` hold theirs in `in_parameters`, `out_parameters` and `bindings`,
  so a new gate can declare the inputs its condition tests.
  `Binding.between(source, target, late_bound=False)` links two parameters,
  and `to_reference()` refers to one without an `r:URN`, as Colectica writes
  it. A parameter reads its `r:ParameterName`, `r:Description`,
  `r:DefaultValue`, `isArray` and any representation.
- **Record who changed a version.** The `increment_*` methods take
  `responsibility=`, and `ddi.configure(version_responsibility=...)` sets a
  default for it. `ddi.configured()` scopes a setting to a `with` block, and
  `ddi.reset_configuration()` restores the defaults.

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

### Spec conformance

- **Check a questionnaire against a spec.** A spec lists, in YAML or JSON, a
  survey's modules, the questions and statements in each, their response
  domains and code lists, the gates on modules and questions, the edit
  checks, and the variables a data lookup supplies or the instrument
  computes. `ddi conform INSTRUMENT --spec SPEC` (and
  `ddi_l.spec.conform()`) compares an instrument with it and reports, with a
  rule id and a severity, modules and items that are missing, extra,
  misplaced or ambiguous, codes and labels, languages, domains, gates and
  edits that differ. Output is JSON or a table; `--fail-severity` sets what
  fails the run, and exit code 2 means it could not run. Ids are found where
  the spec's `match` block says, and an id found on several constructs is
  reported, never guessed. An item reached by several paths is compared
  where the spec puts it, a gate is read from the bindings of each item's
  latest version, and referenced and mixed domains are compared. With
  `gate_scope: page`, each statement of the module must sit under its page
  gate too. See *Check a questionnaire against a spec*.
- **`ddi spec validate|schema|example`** checks a spec against its JSON
  Schema and against itself (every problem with its path, in document
  order), writes the schema, or writes the example (a fictional Pet survey).
  YAML is read as YAML 1.2: repeated keys and merge keys are errors.
- **An expression language for gates and edits** (`ddi_l.spec.expression`):
  comparisons, `and`, `or`, `not`, arithmetic, dates and the predicates
  `answered()`, `missing()`, `empty()`, `refused()` and `today()`.
  `normalise()` compares two gates without calculating: `x > 3` and
  `x >= 4` stay different. So does `equivalent()` without the `logic`
  extra (below). An answer test beside a
  comparison of the same question is dropped (`answered(x) and x > 3` is
  `x > 3`), so such a gate compiles to `Neutral`.
- **Compile a gate for Colectica** (`compile_condition()`): a `Neutral`
  condition when Colectica's operator codes can hold it, else Blaise code with
  `fallback_reason` saying why. `!=`, `<`, `<=` and `>=` have codes of their
  own, `answered(x)` is `NotEmpty` and `NotRefused`, and `x != 2` on a coded
  question is `ContainsNone`; a `not` in front of a comparison, dates,
  arithmetic, two questions compared and `and` and `or` mixed in a group are
  still Blaise. Reading a condition back has a branch for every code, and a
  `DontKnow` test is reported as unverifiable. The Blaise words for empty, refused,
  today and dates have no defaults: a `BlaiseDialect` or the spec's `blaise`
  block sets them, and a date template must read back without doubt.
  `parse_blaise()` and `condition_to_expression()` read either form back;
  `comparable()` makes a quoted plain number that number, since `Neutral`
  stores `"2"` and `2` alike. Numbers keep every digit, however long. A
  choice among one coded question's codes is one `ContainsAny` statement
  wherever it sits, so `a and (x = 2 or x = 3) or b` compiles to `Neutral`.
  Each compiled condition is read back and compared with the gate, by
  normal form and then with the `logic` extra when it is installed:
  `CompiledCondition.verified` records the result, and
  `compile_condition(validate=True)` raises when they differ, naming a
  respondent they disagree on.
- **Edits are reported as not verifiable by default**, since where an
  instrument stores them is not known in general; `--edits strict` compares
  them once the spec's `match.edits` says how they are marked.
- **Decide whether two gates hold for the same respondents** (`decide()`,
  with the new `logic` extra, `pip install 'ddi-l[logic]'`, which adds the
  Z3 solver). When they do not, the verdict gives a respondent they disagree
  on: `x > 3` and `x >= 4` differ when `x` is 3.25, and agree with
  `types={"x": "integer"}`. A respondent leaves each question empty, refuses
  it or answers it, and an answer may have no value to compare (a
  don't-know); a comparison holds only when the questions it reads have
  values. What cannot be modelled, such as text compared by order, is
  `unknown`, with the reason. `evaluate()` tells whether an expression holds
  for one respondent, and each `different` verdict is checked with it. A
  work limit, not a clock, bounds the solver, so a verdict is the same on
  every run, and `import ddi_l.spec` does not load it.
- **A new `spec` extra**, `pip install 'ddi-l[spec]'`, adds PyYAML and
  jsonschema to read specs. The expression language and its compilers need
  only the standard library, and `import ddi_l` loads none of it.

### HTTP API

- **Lint options per request.** `POST /v1/lint` takes `?rule=`,
  `?skip_rule=` and `?lint_config=` (the JSON object `--lint-config` reads),
  and `POST /v1/validate` takes `?lint_config=`. They apply to that request
  alone, so concurrent requests no longer share one process-wide setting.
- **Colectica exports round-trip byte for byte.** `POST /v1/roundtrip` writes
  a `FragmentInstance` as Colectica Designer does, so an unchanged export comes
  back identical and a diff shows only what a parse lost. Before, every
  Colectica file looked changed; `?layout=default` gives this library's
  layout.
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

### Native XML core

- **`pip install ddi-l` brings a compiled XML core**, the `ddi-l-native`
  package (Rust, built with PyO3), which ddi-l uses before lxml. It has
  wheels for Linux (x86_64, aarch64), macOS and Windows (x64), on CPython
  3.11 and later; anywhere else pip installs a pure-Python stand-in of the
  same name and version, which ddi-l does without, so installing ddi-l never
  compiles anything. Its parser builds the tree the standard
  library's builds and its elements behave like the standard library's; the
  tree keeps the bytes it was read from and caches each element's content
  digest, cleared only on the path from a change to the root.
  `DDI_L_XML_BACKEND=native|lxml|stdlib` picks a backend; see
  [Installation](installation.en.md#xml-backends).
- **The same results on every backend.** The whole test suite runs on the
  native backend. The parser is checked against the standard library's on
  every fixture, on crafted inputs and on random and damaged XML: it reads
  the same documents into the same trees and refuses the same ones, and it
  also refuses any document type declaration. Its digests and its source
  index are checked against the pure-Python ones after random edits, and the
  writer writes the same bytes with either.
- **Faster where it counts.** On a 9 MB export: `read_ddi` 0.13 s (lxml
  0.33 s); writing it back unchanged 0.01 s (0.28 s), or after an edit
  0.04 s (0.31 s); the `colectica-questionnaire` profile 0.67 s (1.74 s).
  The parse runs at 185 MB/s (lxml 124 MB/s, standard library 41 MB/s), far
  from memory bandwidth: making the tree's nodes costs most of it. Writing a
  document with a fresh layout is slower than with lxml (0.80 s against
  0.26 s); see [Performance](performance.en.md).
- **Schema validation in one pass, with lines, on the native backend.**
  A new `native` validation backend, the default there, checks a document
  in one pass against a compiled form of the schema (`ddi_l/schemas/ir/`,
  made by `codegen/schema_ir.py` from the bundled XSDs). A valid document
  never loads xmlschema. Each element that may be wrong is checked by
  xmlschema alone, so the messages and paths are xmlschema's, and the
  issues carry the line each element starts on, as on the lxml backend. On
  a 9 MB export: 0.09 s valid; 0.13 s with an error (2.6 s on the first
  call), where libxml2 then xmlschema take 6.5 s. Tested against xmlschema
  on every fixture and on 300 randomly damaged documents per run: the same
  errors, in the same order.
- **Linting again costs what changed, on the native backend.** A lint run
  keeps what it read from each item under the item's content digest, and a
  later run on the same document reads again only the items whose digest
  changed. On a 9 MB export, the `colectica-questionnaire` profile takes
  0.13 s after an edit, against 0.8 s for a first run, with the same
  findings. Rules that follow the whole flow
  (`colectica.flow.read-before-computed`, `colectica.ifthenelse.partial-gate`)
  still walk it each time. A first run costs about 0.04 s more: it works out
  the digests, which a later write reuses. Tested after random edits against
  a run that reads everything.

### Performance

- **`revise` no longer scans every item for each item it revises.** It
  finds who refers to a revised item in an index built once per call (kept
  per item on the native backend), and a dry run makes its changes and takes
  them back instead of copying the fragment; `repair_shared_identifiables`
  does the same. On a 9 MB export, revising one question with its six
  ancestors takes 0.02 s on the native backend (0.20 s before; a
  dry run 0.38 s) and 0.14 s on lxml (0.41 s; a dry run 0.49 s).
  Tested after random edits against the cascade as it was: the same plan and
  the same document.
- **One lint run builds each index once.** The rules of a run share what
  they build from the document: its items and their latest versions, the
  reference resolutions, the bindings and the parsed conditions; `conform`
  does the same. Each was rebuilt by every rule that needed it, and the
  innermost items of a `DDIInstance` were found by searching every item's
  subtree. The `colectica-questionnaire` profile on a 9 MB export (4,478
  items) went from 6.1 s to 2.0 s, with the same findings.
- **`colectica.flow.read-before-computed` no longer walks every path.** A
  page reached by several paths was walked again on each, so a flow of
  chained gates took time doubling with every gate. A construct reached
  again now replays what it found the first time, for the same bindings
  above it; the findings are the same. A flow with 20 chained gates (a
  million paths) takes milliseconds. A flow that loops back on itself is
  still walked path by path.
- **`conform` no longer walks every path to a construct.** A construct is
  one node for each run of sequences above it, which counts the paths to
  it and keeps the gates of the first; whether the paths agree on a gate is
  found without walking them one by one. The reports are the same. A
  question below 16 chained gates (65,536 paths) took 9.1 s and now takes
  13 ms; below 20 gates, 17 ms. An instrument that loops back on itself is
  still walked path by path.

### Fixed

- **`DDIReferenceWarning` can be made again from its arguments**, as `pickle`,
  `copy` and pytest-xdist do: its argument is the records, and its text is
  unchanged.
- **An attribute set in code on a new `<Fragment>` is written.** Colectica's
  layout wrote every `<Fragment>` start tag from a template, so an attribute
  on a copied or added one was lost; one on a fragment read from a file was
  kept.
- **A dry run of `revise` given an element picks the item the real run
  picks.** It looked the item up by its ID alone, so with two items of that
  ID under different agencies it could plan for the other one.
- **A document type declaration is refused on both backends.** The stdlib
  backend accepted `<!DOCTYPE root><root/>`, which lxml refused; both now
  refuse it with the same message. `iterparse_ddi` refuses one too, and a
  caller can no longer relax its parser: `resolve_entities=True`,
  `load_dtd=True`, `no_network=False`, a `forbid_*=False` or a `parser`
  raise `ValueError`.
- **Questions added to an opened file are saved.** A data collection or
  question scheme read from a file wrote back only the questions it was read
  with: one added after `open_ddi()` was dropped on save with no warning, and
  one removed came back.
- `validate_document(doc)` on a `Document` no longer detaches the models the
  caller holds; edits made to them afterwards were lost on save.
- `--debug` works on every command; `tables`, `spec`, `conform`,
  `explain-condition`, `versions` and `serve` rejected it.
- `ddi.citation.title.languages` is registered, listed and documented as the
  `warning` it reports, not as an `error`.
- `DDIDocument.validate(raise_error=True)` is documented as raising
  `DDIValidationError`, which it does.
- **`colectica.statement.logic-note` skips Notes.** A statement Colectica
  types as a Note (`extension:TypeOfStatement` = `Note`) is not shown, so a
  flow condition written in one is where it belongs, and is no longer
  reported as shown to respondents.
- **A `str` is read as the text it is.** `read_ddi()` reads XML given as a
  string whatever encoding its declaration names; it was decoded again under
  that encoding, or refused.
- **Names built in code are schema-valid.** A name set in code
  (`construct_names`, `names` and every other `…Name` field of a generated
  model) was written with `r:Content`, which the schema forbids in a name,
  so `validate()` rejected items such as `ComputationItem`,
  `QuestionConstruct`, `Category`, `Universe` and every scheme and group.
  Names are written with `r:String`. A name read from a file keeps its tag,
  unless it was the invalid `r:Content`.
- **`ConceptualComponent` keeps its module names.** A
  `c:ConceptualComponentModuleName` set in code was never written, and one
  read from a file was kept only as unmapped content; both now go through
  `conceptual_component_module_names`.
- **Two item types can no longer silently share one generated ID.** A
  `DataCollection` gives each item built with a non-UUID identifier the ID
  `uuid5(agency:identifier)`, so a `DataCollection` and a `CollectionEvent`
  both called `main` came out with the same `r:ID`, as did a `CollectionEvent`
  called `main` added to that `DataCollection` after reading it back.
  Serializing now raises `ModelValidationError` naming both types. Versions
  of one item still share their ID, and identifiers an item already has are
  written as given.
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
- **Text with markup is kept.** A label, description or other multilingual
  text whose `r:Content` holds XHTML (`<b>Kind</b> of pet`) was cut to the
  text before its first element whenever its item was written from its model
  (`put()`, `to_xml()`), and its blocks could be reordered (a `<ul>` moved
  before the `<p>` it followed). Such a string now holds its whole text
  (`"Kind of pet"`, with a space between blocks) and is written back as read
  while unchanged; an edited
  one is written as its text, and the other languages keep their markup.
  Parameters keep the attributes of their `r:URN` when edited.
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

- **A page on working with other tools.** "Work with other tools" shows,
  with examples that run, how ddi-l exchanges metadata with XML and schema
  tools (`xmllint`), linked-data tools (`rdflib` and SPARQL), JSON, spreadsheets,
  R, any language over HTTP, DDI Codebook files (for example Dataverse's export,
  converted through the tables import), DDI 3.2 tools and open-source
  questionnaire generators, and what to check before exchanging a file.
- **Measurable learning objectives in every module.** Each of the 17 modules
  opens with three to six objectives that say what the learner can do
  ("write a script that...", "run `ddi lint` and name one finding"), tags
  every exercise and quiz question with the objective it practises, gives the
  expected output of each exercise, and ends with a "Check yourself" list.
  Every objective now has an exercise and a quiz question; quiz answers are
  spread across A to D (B was the answer to 42 of 72 questions). Modules 12,
  14, 15 and 16 keep six objectives or fewer and move the rest to "Going
  further". The capstone rubric scores each track's techniques, and all four
  tracks have a sample solution. Ten stale copies of renumbered modules, in
  both languages, are removed.
- **Cross-references render on the API page.** Docstrings wrote them as
  Sphinx roles (`:func:`...``), which showed raw; they are now code spans.
- **A curriculum module on advanced questionnaire specification.** Module 16
  teaches spec writers to write a questionnaire spec, give gates and edit
  checks the meaning they intend on a missing answer, replace "go to" and
  "otherwise" with gates, fit gates to a tool's condition editor without
  changing their meaning, keep one variable per idea in two languages, and check an instrument with
  `ddi conform`. The capstone projects are now Module 17, and the old
  address redirects to them.
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

### Tooling and packaging

- **Tests run on every core.** `pytest` runs with pytest-xdist (`-n auto`, a
  new dev dependency); `-n 0` runs in one process. On four cores the lxml
  suite takes 58 s instead of 3 min 20 s (without coverage); with coverage,
  lxml takes 1 min 43 s, the standard library 2 min 49 s and native
  3 min 45 s.
- **The test suite runs without warnings.** A test whose items refer to items
  outside its document now says so, and any other `DDIReferenceWarning` fails
  it; the two curriculum pages that warn on purpose must still warn. Five
  skips are gone: two generator bugs (a fixed element value, a content model
  that must occur twice) left three item types untested, and a deliberately
  truncated fixture is no longer fed to tests that need well-formed XML. The
  skips left depend on the environment (no R, no native core, the other XML
  backend) or on the generic engine not reading substitution-group members.
- **Python 3.15.** ddi-l is tested on Python 3.15 too: a pull request tests
  3.11 and 3.15, a push to `main` tests 3.11 to 3.15, both XML backends each
  time. CI pins uv 0.13.7, the first uv series that installs 3.15.
- **One command sets the version.** `scripts/set_version.py 0.3.0` (or
  `patch`, `minor`, `major`) writes the version in all 11 files that state
  it, with the release date and the citations' year, then runs `uv lock`;
  it writes nothing unless every file matches. A test fails when another
  file starts stating the version.
- **A link to a missing heading fails the docs build.** `mkdocs build
  --strict` now checks anchors (`validation: anchors: warn`). It found two
  cheat-sheet links to a Module 15 section that had moved, now fixed.
- **Mutation runs draw fewer examples, the same each time.** Under mutmut a
  property test draws at most 30 examples, derandomized, instead of 300 (or
  Hypothesis's 100), since it runs once for each mutant it covers; a mutant
  is caught on every run or none. The suite still draws 300.
- **The native core in CI and releases.** A CI job checks the Rust code
  (`cargo fmt`, `cargo clippy`) and runs the whole suite on the native
  backend. A release builds `ddi-l-native` wheels (one stable-ABI wheel per
  platform: Linux x86_64 and aarch64, macOS universal2, Windows x64) and its
  sdist, plus the pure-Python stand-in wheel (`native/fallback/`), and
  publishes them with ddi-l; PyPI needs this repository set up as a trusted
  publisher for the `ddi-l-native` project too. The monthly job fuzzes the
  parser against the standard library's, 300,000 inputs per test. In the
  repository, `uv.lock` installs the stand-in, so no contributor needs Rust;
  the ddi-l sdist carries it and the crate's sources.
- **Test fixtures ship in the sdist only.** The wheel carried 250 test files
  under `ddi_l/examples/tests/`. It keeps the two samples the CLI recipes run;
  the rest live in `tests/fixtures/`, and `scripts/check_distributions.py`
  fails if they reach the wheel again.
- **A mutation-testing gate.** `mutmut` now covers fifteen modules, and the
  monthly job fails when a mutant survives that `tests/mutation_baseline.txt`
  does not list, or when a listed one no longer survives
  (`scripts/check_mutation.py`, `make mutation`). The latest full run caught
  12,290 of 14,542 mutants (84.5 %). The list holds the 2,252 survivors: 239
  with the reason no test can catch them, and 2,013 not looked at yet. New
  tests caught about 500 survivors, most in validation, the operations, the
  condition compiler, I/O and conformance. In the four modules new in this
  release (the fact base, the instrument index, the evaluator and the solver
  encoding), 1,237 of 1,282 mutants are caught, and each of the 45 survivors
  has its reason.
- Ruff and the dependency audit run once in CI instead of on all eight test
  legs.
- A pull request tests Python 3.11 and 3.14 on both backends; a push to
  `main` still tests all four versions.
- Removed code nothing used, merged five copies of the version sort key, and
  replaced the serializer's strategy classes with one function.

### Known issues

- `ddi validate` exits 1 when it reports any issue, including one of
  `warning` severity.
- A study moved into a `Group` (`Document.add_group()`) is missing from
  `iter_study_units()`, and so from the index built from it.
- Without lxml, output written with `pretty_print=False` spells empty elements
  `<tag />`, where lxml writes `<tag/>`.
- A DDI 3.2 `DDIInstance` is written back with generated prefixes (`ns0:`
  with lxml, `p0:` without) and with `r:` bound to the 3.3 namespace. The XML
  means the same, but no longer reads as the source did. A 3.2
  `FragmentInstance` is written in Colectica's layout, with `r:` and `ddi:`
  bound to the 3.2 namespaces.

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
- See [Performance](performance.en.md) for measured timings.

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
  [using ddi-l from R](r-users.en.md) through reticulate.
- **Training curriculum**: a 16-module progressive course with exercises,
  quizzes, an instructor guide, answer keys, and a bilingual cheat sheet.
