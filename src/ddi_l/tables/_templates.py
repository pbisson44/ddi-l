"""The blank and example workbooks, written from the table spec.

The downloads on the documentation site are these files; a test regenerates
them and fails if the committed copies differ.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Literal

from ._example import EXAMPLE as _EXAMPLE
from ._example import EXAMPLE_LANGUAGES as _EXAMPLE_LANGUAGES
from ._spec import (
    CUSTOM_PREFIX,
    MULTI_VALUE_SEPARATOR,
    SETTING_NAMES,
    TABLES,
    Table,
    expand_headers,
)
from ._xlsx import write_workbook, write_zip

Layout = Literal["csv", "zip", "xlsx"]

_BLANK_SETTINGS = [
    {"setting": "agency", "value": ""},
    {"setting": "version", "value": "1"},
    {"setting": "language", "value": "en"},
]


def _headers(
    table: Table, languages: tuple[str, ...], rows: list[dict[str, str]]
) -> list[str]:
    headers = expand_headers(table, languages)
    if table.custom:
        # Custom columns the example uses, in first-seen order, after the rest.
        for row in rows:
            for key in row:
                if key.startswith(CUSTOM_PREFIX) and key not in headers:
                    headers.append(key)
    return headers


def table_grids(
    *, example: bool, languages: tuple[str, ...]
) -> list[tuple[Table, list[list[str]]]]:
    """Each table's rows of cells, header first."""
    grids: list[tuple[Table, list[list[str]]]] = []
    for table in TABLES:
        if example:
            rows = _EXAMPLE[table.name]
        elif table.name == "settings":
            rows = _BLANK_SETTINGS
        else:
            rows = []
        headers = _headers(table, languages, rows)
        grid = [headers] + [[row.get(h, "") for h in headers] for row in rows]
        grids.append((table, grid))
    return grids


def readme_rows(languages: tuple[str, ...]) -> list[list[str]]:
    """The README sheet: every table and column, with what goes in it."""
    rows = [["table", "column", "required", "what goes in it"]]
    for table in TABLES:
        rows.append([table.name, "", "", table.help])
        for column in table.columns:
            name = (
                f"{column.name}@<language>  (e.g. "
                + ", ".join(f"{column.name}@{lang}" for lang in languages)
                + ")"
                if column.multilingual
                else column.name
            )
            rows.append(
                [table.name, name, "yes" if column.required else "", column.help]
            )
        if table.custom:
            rows.append(
                [
                    table.name,
                    "custom:<name>",
                    "",
                    "Any property of your own, one column per property. "
                    "Stored as r:UserAttributePair with key extension:<name>.",
                ]
            )
    rows.append(
        [
            "settings",
            "",
            "",
            "Rows: "
            + "; ".join(
                f"{name} ({'required' if required else f'default {default}'}): {help_}"
                for name, (required, default, help_) in SETTING_NAMES.items()
            ),
        ]
    )
    rows.append(
        [
            "(all)",
            "",
            "",
            f"Several ids in one cell are separated by {MULTI_VALUE_SEPARATOR}. "
            "Columns starting with # or _ are notes and are ignored.",
        ]
    )
    return rows


def _csv_bytes(grid: list[list[str]]) -> bytes:
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\r\n").writerows(grid)
    # With a byte-order mark, Excel opens the file as UTF-8, so é and â
    # survive a double-click.
    return buffer.getvalue().encode("utf-8-sig")


def _readme_text(languages: tuple[str, ...]) -> bytes:
    lines = [
        "ddi-l metadata tables",
        "",
        "One CSV file per table. Fill the rows, then load them with",
        "ddi_l.tables.load_tables('this-folder') or `ddi tables import`.",
        "Full guide: https://pbisson44.github.io/ddi-l/latest/spreadsheet-import/",
        "",
    ]
    for table, column, required, help_ in readme_rows(languages)[1:]:
        if not column:
            lines += ["", f"{table}.csv: {help_}"]
        else:
            lines.append(f"  {column}{' (required)' if required else ''}: {help_}")
    return ("\r\n".join(lines) + "\r\n").encode("utf-8-sig")


def write_table_templates(
    destination: str | Path,
    *,
    example: bool = False,
    languages: tuple[str, ...] = _EXAMPLE_LANGUAGES,
    layout: Layout = "csv",
) -> Path:
    """Write the metadata tables to fill in, blank or with an example.

    Args:
        destination: A folder for ``layout="csv"``; a file for ``"zip"`` (the
            CSV files zipped) and ``"xlsx"`` (one sheet per table).
        example: Fill the tables with a small bilingual survey instead of
            leaving them empty. The example is in English and French.
        languages: The languages to give columns such as ``label@en`` for.
        layout: ``"csv"``, ``"zip"`` or ``"xlsx"``.

    Returns:
        The folder or file written.
    """
    target = Path(destination)
    if layout in ("xlsx", "zip"):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(
            table_template_bytes(example=example, languages=languages, layout=layout)
        )
        return target
    if layout != "csv":
        raise ValueError(f"layout must be 'csv', 'zip' or 'xlsx', not {layout!r}")
    target.mkdir(parents=True, exist_ok=True)
    for name, data in _files(_grids(example, languages), tuple(languages)):
        (target / name).write_bytes(data)
    return target


def table_template_bytes(
    *,
    example: bool = False,
    languages: tuple[str, ...] = _EXAMPLE_LANGUAGES,
    layout: Literal["xlsx", "zip"] = "xlsx",
) -> bytes:
    """The tables of :func:`write_table_templates` as bytes, built in memory.

    Args:
        example: The bilingual example instead of empty tables.
        languages: The languages to give columns such as ``label@en`` for.
        layout: ``"xlsx"`` for a workbook, ``"zip"`` for CSV files.
    """
    languages = tuple(languages)
    grids = _grids(example, languages)
    buffer = io.BytesIO()
    if layout == "xlsx":
        sheets = [(table.name, grid, True) for table, grid in grids]
        sheets.insert(0, ("README", readme_rows(languages), True))
        write_workbook(buffer, sheets)
    elif layout == "zip":
        write_zip(buffer, _files(grids, languages))
    else:
        raise ValueError(f"layout must be 'xlsx' or 'zip', not {layout!r}")
    return buffer.getvalue()


def _grids(
    example: bool, languages: tuple[str, ...]
) -> list[tuple[Table, list[list[str]]]]:
    if example and tuple(languages) != _EXAMPLE_LANGUAGES:
        raise ValueError("The example tables are in English and French only.")
    return table_grids(example=example, languages=tuple(languages))


def _files(
    grids: list[tuple[Table, list[list[str]]]], languages: tuple[str, ...]
) -> list[tuple[str, bytes]]:
    files = [(table.file_name, _csv_bytes(grid)) for table, grid in grids]
    files.append(("README.txt", _readme_text(languages)))
    return files
