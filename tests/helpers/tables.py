"""Writing small metadata tables, and reading what loading them gives."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TypeVar

import pytest

from ddi_l._etree import Element
from ddi_l.models.base import MaintainableBase
from ddi_l.tables import TableImport, TableImportError, load_tables

T = TypeVar("T", bound=MaintainableBase)


def write(folder: Path, name: str, rows: list[list[str]], *, sep: str = ",") -> None:
    """Write ``rows`` (header first) as ``<folder>/<name>.csv``, as Excel does."""
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / f"{name}.csv").open("w", encoding="utf-8-sig", newline="") as out:
        csv.writer(out, delimiter=sep, lineterminator="\r\n").writerows(rows)


def settings(folder: Path, agency: str = "example.org") -> None:
    write(folder, "settings", [["setting", "value"], ["agency", agency]])


def tables(folder: Path, **rows: list[list[str]]) -> Path:
    """A folder with ``settings`` and one CSV file per keyword argument."""
    settings(folder)
    for name, table_rows in rows.items():
        write(folder, name, table_rows)
    return folder


def problems(source: Path, **kwargs: str) -> list[str]:
    """The problems loading ``source`` reports; it must fail."""
    with pytest.raises(TableImportError) as raised:
        load_tables(source, **kwargs)
    return [str(problem) for problem in raised.value.problems]


def get(loaded: TableImport, table: str, key: str, kind: type[T]) -> T:
    item = loaded.get(table, key)
    assert isinstance(item, kind)
    return item


def local(element: Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def children(element: Element, name: str) -> list[Element]:
    """``element``'s children whose local name is ``name``."""
    return [child for child in element if local(child) == name]


def child(element: Element, name: str) -> Element:
    found = children(element, name)
    assert len(found) == 1, (name, [local(c) for c in element])
    return found[0]


def text(element: Element, *path: str) -> str | None:
    """The text at ``path`` (local names) below ``element``."""
    for name in path:
        found = children(element, name)
        if not found:
            return None
        element = found[0]
    return element.text


def ref_id(element: Element) -> str | None:
    """The r:ID of a reference element."""
    return text(element, "ID")
