---
description: >-
  Install ddi-l from PyPI with pip, uv or Poetry, choose the extras you need,
  or set up a development checkout.
---

# Installation

`ddi-l` requires **Python 3.11 or newer** and is available on PyPI.

## Install from PyPI

Use this unless you want to change `ddi-l` itself.

=== "pip"
    ```bash
    pip install ddi-l
    ddi --help
    ```

=== "uv"
    ```bash
    uv add ddi-l
    uv run ddi --help
    ```

=== "Poetry"
    ```bash
    poetry add ddi-l
    poetry run ddi --help
    ```

!!! tip "Verify the installation"
    - `ddi --help` confirms the CLI entry point is on your `PATH`.
    - `python -c "import ddi_l; print(ddi_l.__version__)"` prints the
      installed version.

### What `pip install ddi-l` gives you

`pip install ddi-l` reads, writes, validates and lints DDI documents with
nothing else installed. It brings the native XML core, the `ddi-l-native`
package at the same version, wherever a compiled wheel exists: Linux (x86_64
and aarch64), macOS and Windows (x64), on CPython 3.11 and later. Anywhere
else pip installs a pure-Python stand-in with the same name, and `ddi-l`
works the same, more slowly. pip never compiles anything.

### Extras: when you need one

An extra adds a feature or a backend most people do not need. Install one when
your work matches its "Install it when" column; combine them as
`pip install 'ddi-l[spec,logic]'`.

| Extra | Install it when | What it adds |
| --- | --- | --- |
| `spec` | You check questionnaires against a spec: `ddi spec`, `ddi conform`, or a YAML or JSON spec read in Python. | PyYAML and jsonschema; see [Check a questionnaire against a spec](spec-conformance.en.md). Without it, `ddi spec` and `ddi conform` say what to install. |
| `logic` | You want gates compared exactly: `equivalent()` and `ddi conform` then decide whether two gates hold for the same respondents and name a respondent who tells them apart, and lint reports constructs no respondent reaches. | The Z3 solver (MIT, about 57 MB installed); see [Check a questionnaire against a spec](spec-conformance.en.md). Without it, gates are compared as written. |
| `server` | You run the HTTP API, `ddi serve`. | Litestar and uvicorn; see [HTTP API](server.en.md). Without it, `ddi serve` says what to install. |
| `full` | Your platform has no compiled native core (Alpine Linux, Windows on ARM, PyPy, free-threaded Python), or you mostly write new documents laid out from scratch (`layout="default"`), which lxml writes faster. | lxml, used when the native core is not there; set `DDI_L_XML_BACKEND=lxml` to use it anyway. |

### XML backends

`ddi-l` reads and writes XML with the first of these that is installed:

1. `native`, from `ddi-l-native` where a compiled wheel exists;
2. `lxml`, from the `full` extra;
3. the standard library, always there.

Each gives the same documents, the same validation issues and the same lint
findings. Set the `DDI_L_XML_BACKEND` environment variable to `native`,
`lxml` or `stdlib` to choose one; it is read once, when `ddi_l` is
imported. `ddi_l._etree.BACKEND` names the backend in use.

The `native` backend also validates against the schema in one pass; see
[how schema validation runs](validation.en.md#how-schema-validation-runs). A
document laid out afresh (a new document, or `layout="default"`) is written
by Python code on the `native` and standard library backends, and is slower
to write there than with lxml.

!!! info "Schemas are already included"
    The DDI 3.1, 3.2, and 3.3 XML Schemas ship inside the package, so
    `doc.validate()` and `ddi validate` work offline with no extra download
    and no network access.

## Install from source

Developers contributing to `ddi-l` should install from a local checkout:

```bash
git clone https://github.com/pbisson44/ddi-l.git
cd ddi-l
pip install -e . ./native/fallback
```

`./native/fallback` is `ddi-l-native`'s pure-Python stand-in. pip does not read
`uv.lock`, and a version of `ddi-l` not released yet has no `ddi-l-native` on
PyPI to install.

Install the development toolchain. The project is managed with
[uv](https://docs.astral.sh/uv/), and `uv.lock` pins every dependency version:

```bash
uv sync --group dev              # Runtime + development dependencies
uv sync --group dev --extra full # ...plus the optional lxml backend
```

Note that `full` is an **extra**, not a dependency group: `--group full`
fails. In a checkout, `ddi-l-native` is its pure-Python stand-in
(`native/fallback/`), so no one needs Rust. To use the native core, build it
over the stand-in; this needs a Rust toolchain ([rustup](https://rustup.rs/))
and, on Windows, Visual Studio Build Tools with the C++ workload. `uv sync` and
`uv run` put the stand-in back, so run commands with `uv run --no-sync`:

```bash
uv pip install --reinstall-package ddi-l-native ./native
uv run --no-sync python -c "import ddi_l._etree as e; print(e.BACKEND)"  # native
```

With plain pip instead (pip 25.1 or later reads dependency groups):

```bash
pip install -e '.[full]' ./native/fallback --group dev
```

For documentation work (`docs` is a dependency group, not an extra):

```bash
uv sync --group docs
# or
pip install -e . ./native/fallback --group docs
```

## Verify with a quick smoke test

```python
import ddi_l as ddi

doc = ddi.new_study(title="Test", agency="example.org")
doc.add_question(text="Does it work?")
print(f"Questions: {len(doc.questions)}")  # -> 1
```

For more details, see the [user guide](user-guide.en.md) or the
[development guide](DEVELOPMENT.en.md).
