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
the timings above. `schema_loader.set_validation_backend("python")` turns the
libxml2 check off.

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
```

- [Schema conversion benchmark](performance/schema_conversion.md)
