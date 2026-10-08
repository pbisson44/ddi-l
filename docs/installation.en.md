---
description: >-
  Install ddi-l from PyPI with pip, uv or Poetry, add the lxml and HTTP API
  extras, or set up a development checkout.
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

### Optional dependencies

| Need | Command | What it unlocks |
| --- | --- | --- |
| Accelerated XML parsing | `pip install 'ddi-l[full]'` | Enables the `lxml` backend: faster parsing, and near-instant validation of valid documents. |
| HTTP API | `pip install 'ddi-l[server]'` | Adds the Litestar service behind `ddi serve`; see [HTTP API](server.md). |

!!! info "Schemas are already included"
    The DDI 3.1, 3.2, and 3.3 XML Schemas ship inside the package, so
    `doc.validate()` and `ddi validate` work offline with no extra download
    and no network access.

## Install from source

Developers contributing to `ddi-l` should install from a local checkout:

```bash
git clone https://github.com/pbisson44/ddi-l.git
cd ddi-l
pip install -e .
```

Install the development toolchain. The project is managed with
[uv](https://docs.astral.sh/uv/), and `uv.lock` pins every dependency version:

```bash
uv sync --group dev              # Runtime + development dependencies
uv sync --group dev --extra full # ...plus the optional lxml backend
```

Note that `full` is an **extra**, not a dependency group: `--group full`
fails.

With plain pip instead (pip 25.1 or later reads dependency groups):

```bash
pip install -e '.[full]' --group dev
```

For documentation work (`docs` is a dependency group, not an extra):

```bash
uv sync --group docs
# or
pip install -e . --group docs
```

## Verify with a quick smoke test

```python
import ddi_l as ddi

doc = ddi.new_study(title="Test", agency="example.org")
doc.add_question(text="Does it work?")
print(f"Questions: {len(doc.questions)}")  # -> 1
```

For more details, see the [user guide](user-guide.md) or the
[development guide](DEVELOPMENT.md).
