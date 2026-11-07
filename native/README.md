# ddi-l-native

The native XML core for [ddi-l](https://github.com/pbisson44/ddi).
`pip install ddi-l` installs it, and ddi-l uses it to read and write XML.
Compiled wheels exist for Linux (x86_64, aarch64), macOS and Windows (x64), for
CPython 3.11 and later. Anywhere else pip installs a pure-Python stand-in
with the same name and version, and ddi-l uses lxml or the standard library.

It parses XML into a tree whose elements behave like those of Python's
`xml.etree.ElementTree`, and keeps the bytes each element was read from, so
ddi-l writes an unchanged element back exactly as it was read.

The parser refuses document type declarations, so it expands no entities
other than the five XML defines and never fetches anything.

Build it from this directory with `maturin build --release`, and the stand-in
with `python -m build --wheel fallback`.
