---
description: >-
  Measured timings and memory use for ddi-l, and the settings that change
  them: the lxml backend, validation caching and streaming.
---

# Performance

What costs time and memory in ddi-l, with measured numbers and the settings
that change them.

## Indicative timings

A study with 5,000 variables (1.4 MiB of XML), Python 3.11 on a single core,
median of several runs. Treat the numbers as proportions, not guarantees.

| Operation | lxml backend | stdlib backend |
| --- | --- | --- |
| `read_ddi(data)` | 0.02 s | 0.18 s |
| `write_ddi(document)` | 0.06 s | 0.35 s |
| `Document.to_xml()` | 0.6 s | 0.3 s |
| `lint_source(data)` | 0.4 s | 0.2 s |
| `validate_source(data)` (schema only) | 0.05 s | 1.4 s |
| `Document.validate()` | 0.6 s | 3.5 s |
| `import ddi_l` | 0.03 s | 0.03 s |
| `ddi --help` | 0.08 s | 0.08 s |

With lxml installed, a document is first checked by libxml2's C validator,
which confirms a valid document in milliseconds. Only when that check fails
does [xmlschema](https://pypi.org/project/xmlschema/) run, to produce the
detailed issues, so the reported errors are the same on both backends. Without
lxml every validation runs on xmlschema, which is pure Python and dominates
the timings above. `schema_loader.validate(..., backend="python")` turns the
libxml2 check off for one call, and
`schema_loader.set_validation_backend("python")` for the whole application.

## The XML backends on a large export

A 9 MB Colectica export (112,000 elements), Python 3.13, best of five runs on
one machine. `benchmarks/backends_bench.py` measures the same steps on any
file, on the backend `DDI_L_XML_BACKEND` names.

| Step | native | lxml | stdlib |
| --- | --- | --- | --- |
| Parse | 0.05 s (185 MB/s) | 0.07 s (124 MB/s) | 0.22 s (41 MB/s) |
| `read_ddi` | 0.13 s | 0.33 s | 0.29 s |
| First `write_ddi` (builds the source index) | 0.23 s | 1.4 s | 1.7 s |
| `write_ddi` again, unchanged | 0.01 s | 0.28 s | 0.23 s |
| `write_ddi` after changing one attribute | 0.04 s | 0.31 s | 0.28 s |
| `write_ddi(layout="default")` | 0.80 s | 0.26 s | 0.76 s |
| `colectica-questionnaire` profile | 0.67 s | 1.74 s | 0.62 s |

- **Parsing is not bound by memory bandwidth.** Copying the same bytes takes
  1 ms (6.5 GB/s); most of the native parse is making the tree's 112,000
  nodes. Text that needed no decoding stays a range of the source bytes.
- **Writing back costs what changed.** The native tree keeps each element's
  digest and clears it only on the path from a change to the root, so an
  unchanged document is written as its bytes, and an edited one hashes only
  that path.
- **A full layout is Python code** on the native and standard library
  backends (the indentation, the namespace clean-up and ElementTree's
  writer), so a new document, or one written with an explicit `layout`, is
  written about three times faster by lxml.

## What to expect

- **Schemas load once per version.** libxml2 compiles a version's XSDs in
  about 0.1 s. xmlschema takes about 2 s and 20–25 MiB, and is loaded only
  when it is needed; later validations in the same process reuse both.
  `ddi serve` loads the default version at startup.
- **Reading is cheap; the model index is lazy.** `read_ddi` parses the XML and
  stops. The resolver index is built the first time
  `DDIDocument.resolver` is used, or up front with `build_index=True`.
- **`Document` serializes on demand.** `to_xml()`, `save()` and `validate()`
  write the model back into XML each time they are called. Batch your edits
  and serialize once.
- **Reference checks run on `save()` only.** Dangling references are reported
  as a single `DDIReferenceWarning` when saving.

## Large documents

Stream instead of loading the whole tree:

```python
import ddi_l as ddi

for variable in ddi.iter_variables("large-study.xml"):
    print(variable.identifier)
```

`iter_variables` and `iter_questions` clear each element once it has been
turned into an object, so memory stays close to the size of one item (about
190 KiB peak for the 5,000-variable study above). `iterparse_ddi` streams any
maintainable type; request only the types you need, because an element is kept
until the outermost requested element around it has been built.

## Lint and conformance

- **One run builds each index once.** The rules of one `run_lint` or
  `run_profile` call, and the checks of one `conform` call, share what they
  build from the document: its items and their versions, the reference
  resolutions, the bindings and the parsed conditions. The
  `colectica-questionnaire` profile on a 9 MB Colectica export (4,478 items)
  takes 2.0 s; it took 6.1 s when each rule built its own.
- **A later run reads only what changed** (native backend). Each item's
  facts and per-item findings are kept under its content digest, so linting
  the same document again after an edit reads only the edited items. On
  that export the profile takes 0.8 s on a first run and 0.13 s after an
  edit. The rules that follow the whole flow still walk it, which is most of
  what is left.
- **Paths are counted, not walked.** A flow whose pages rejoin after each of
  n gates has 2^n paths from the instrument. `colectica.flow.read-before-computed`
  and `conform` reach each construct once per state that can change what they
  report, so 20 chained gates (a million paths) take milliseconds; 16 took
  9.1 s in `conform`. A flow that loops back on itself is still walked path
  by path.
- **Which constructs a respondent reaches is solved once per flow.**
  `colectica.flow.unreachable` gives the solver one variable per construct,
  however many paths lead to it, settles what it can without it, and marks
  every construct each respondent it finds reaches. 40 chained gates
  (2^40 paths) take 0.16 s; a random flow of 300 constructs, 0.17 s.
- **Exact gate comparison costs about 5 ms a pair.** With the `logic` extra,
  `conform` decides a pair of gates only when their normal forms differ, and
  each pair once, so the Pet fixture compares in about 8 ms with the solver or
  without it. Twenty chained gates take 33 ms with it and 16 ms without.

## HTTP API

`ddi serve` processes at most `--max-jobs` documents at once (default: the
number of CPUs) and answers `503` with `Retry-After` beyond that. Validation
holds the GIL, so more concurrent jobs than cores adds memory, not throughput.
Scale out with more processes behind a load balancer.

## Measuring

The `benchmarks/` directory in the repository contains reproducible scripts:

```bash
uv run python -m benchmarks.iterparse_bench
uv run python -m benchmarks.validation_report_bench
uv run python benchmarks/colectica_profile_bench.py EXPORT.xml
DDI_L_XML_BACKEND=native uv run python benchmarks/backends_bench.py EXPORT.xml
```

- [Schema conversion benchmark](performance/schema_conversion.en.md)
