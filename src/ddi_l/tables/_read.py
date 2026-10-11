"""Read metadata tables: CSV files in a folder or a zip, or an ``.xlsx`` file.

Reading only checks shape -- known tables, known headers, language tags -- and
hands rows on as text. What the values mean is the builder's business.
"""

from __future__ import annotations

import csv
import io
import zipfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from ..exceptions import DDIError
from ._spec import (
    CUSTOM_PREFIX,
    LANGUAGE_TAG,
    TABLES_BY_NAME,
    Header,
    Table,
    is_ignored_header,
)
from ._xlsx import ArchiveBudget, read_workbook


@dataclass(frozen=True)
class TableProblem:
    """One thing wrong in the tables, and where."""

    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.where}: {self.message}"


class TableImportError(DDIError):
    """Raised when tables cannot be loaded; lists every problem found.

    Loading collects problems rather than stopping at the first, so one run
    reports everything to fix: ``error.problems`` holds them, each with the
    file (or sheet), row and column.
    """

    def __init__(
        self,
        message: str,
        *,
        problems: Sequence[TableProblem] = (),
        **kwargs: object,
    ) -> None:
        self.problems = list(problems)
        if self.problems:
            listed = "\n".join(f"  - {problem}" for problem in self.problems)
            message = f"{message}\n{listed}"
        super().__init__(message, **kwargs)  # type: ignore[arg-type]


@dataclass
class Row:
    """A data row: its spreadsheet row number and its non-empty cells."""

    number: int
    cells: dict[str, str]


@dataclass
class RawTable:
    """A table as read: parsed headers and rows of text."""

    table: Table
    source: str
    headers: list[Header] = field(default_factory=list)
    rows: list[Row] = field(default_factory=list)

    def where(self, row: Row | None = None, column: str | None = None) -> str:
        place = self.source
        if row is not None:
            place += f", row {row.number}"
        if column is not None:
            place += f", column {column}"
        return place


#: What tables sent as bytes are called in problems: a workbook, or a zip.
WORKBOOK_NAME = "workbook.xlsx"
ZIP_NAME = "tables.zip"


def upload_name(data: bytes) -> str:
    """:data:`WORKBOOK_NAME` or :data:`ZIP_NAME`: what ``data`` holds.

    Both are zip archives; a workbook has ``xl/workbook.xml``.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = archive.namelist()
    except zipfile.BadZipFile as error:
        raise TableImportError(
            "The data is not an .xlsx workbook or a .zip of CSV files."
        ) from error
    return WORKBOOK_NAME if "xl/workbook.xml" in names else ZIP_NAME


def read_tables(
    source: Path | bytes,
) -> tuple[dict[str, RawTable], list[TableProblem]]:
    """Read ``source`` into raw tables, with any shape problems found.

    ``source`` is a folder, a ``.zip`` or ``.xlsx`` file, or the bytes of
    either, read in memory.
    """
    problems: list[TableProblem] = []
    grids: dict[str, tuple[str, list[list[str]]]] = {}
    if isinstance(source, bytes):
        label = upload_name(source)
        archive: Path | io.BytesIO = io.BytesIO(source)
        suffix = Path(label).suffix
    else:
        label, archive, suffix = source.name, source, source.suffix.lower()
    if isinstance(archive, Path) and archive.is_dir():
        for table in TABLES_BY_NAME.values():
            path = archive / table.file_name
            if path.is_file():
                grids[table.name] = (path.name, _read_csv(path))
    elif suffix == ".xlsx":
        for sheet, rows in _workbook(archive, label).items():
            name = sheet.strip()
            if name.lower() == "readme" or name.startswith("_"):
                continue
            if name not in TABLES_BY_NAME:
                problems.append(
                    TableProblem(
                        f"{label}, sheet {sheet}",
                        "not a known table; expected one of "
                        + ", ".join(TABLES_BY_NAME)
                        + " (or README, or a name starting with _ to ignore it)",
                    )
                )
                continue
            grids[name] = (f"{label}, sheet {name}", rows)
    elif suffix == ".zip":
        grids = _read_zip(archive, label, problems)
    else:
        raise TableImportError(
            f"{label} is neither a folder of CSV files, a .zip of them, nor an "
            ".xlsx workbook."
        )

    tables: dict[str, RawTable] = {}
    for name, (place, grid) in grids.items():
        raw = RawTable(TABLES_BY_NAME[name], place)
        _parse_grid(raw, grid, problems)
        tables[name] = raw
    return tables, problems


# What a damaged or hostile archive can raise while being read.
_UNREADABLE = (zipfile.BadZipFile, KeyError, ValueError, IndexError, SyntaxError)


def _workbook(source: Path | io.BytesIO, label: str) -> dict[str, list[list[str]]]:
    try:
        return read_workbook(source)
    except _UNREADABLE as error:
        # ElementTree's ParseError is a SyntaxError.
        raise TableImportError(
            f"{label} is not a readable .xlsx workbook: {error}"
        ) from error


def _read_zip(
    source: Path | io.BytesIO, label: str, problems: list[TableProblem]
) -> dict[str, tuple[str, list[list[str]]]]:
    """The CSV files of a zip, at its top or in one folder, by table name.

    Other files (``README.txt``, notes, a ``__MACOSX`` folder) are ignored,
    as in a folder; a ``.csv`` that is no table is reported.
    """
    grids: dict[str, tuple[str, list[list[str]]]] = {}
    try:
        with zipfile.ZipFile(source) as archive:
            budget = ArchiveBudget(archive)
            for info in archive.infolist():
                path = info.filename
                name = path.rsplit("/", 1)[-1]
                if (
                    info.is_dir()
                    or path.startswith("__MACOSX/")
                    or name.startswith((".", "_"))
                    or not name.lower().endswith(".csv")
                ):
                    continue
                table = name[: -len(".csv")]
                if table not in TABLES_BY_NAME:
                    problems.append(
                        TableProblem(
                            path,
                            "not a known table; expected one of "
                            + ", ".join(t.file_name for t in TABLES_BY_NAME.values()),
                        )
                    )
                    continue
                if table in grids:
                    problems.append(
                        TableProblem(
                            path, f"a second {name}; the first is {grids[table][0]}"
                        )
                    )
                    continue
                try:
                    text = budget.read(path).decode("utf-8-sig")
                except UnicodeDecodeError:
                    problems.append(
                        TableProblem(path, "is not UTF-8 text; save it as CSV UTF-8")
                    )
                    continue
                grids[table] = (path, _parse_csv(text))
    except _UNREADABLE as error:
        raise TableImportError(
            f"{label} is not a readable .zip of CSV files: {error}"
        ) from error
    return grids


def _read_csv(path: Path) -> list[list[str]]:
    # utf-8-sig: Excel writes a byte-order mark on "CSV UTF-8".
    return _parse_csv(path.read_text(encoding="utf-8-sig"))


def _parse_csv(text: str) -> list[list[str]]:
    first_line = text.split("\n", 1)[0]
    # A French-locale Excel saves CSV with semicolons; read either.
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    return list(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter))


def _parse_grid(
    raw: RawTable, grid: list[list[str]], problems: list[TableProblem]
) -> None:
    if not grid:
        return
    raw.headers = [_parse_header(raw, h.strip(), problems) for h in grid[0]]
    names = [header.raw for header in raw.headers if header.column]
    for duplicate in sorted({name for name in names if names.count(name) > 1}):
        problems.append(TableProblem(raw.where(), f"column {duplicate} appears twice"))
    for offset, cells in enumerate(grid[1:], start=2):
        values: dict[str, str] = {}
        for header, cell in zip(raw.headers, cells, strict=False):
            value = cell.strip()
            if header.column and value:
                values[header.raw] = value
        if len(cells) > len(raw.headers) and any(
            c.strip() for c in cells[len(raw.headers) :]
        ):
            problems.append(
                TableProblem(raw.where(Row(offset, {})), "has values under no header")
            )
        if values:
            raw.rows.append(Row(offset, values))


def _parse_header(raw: RawTable, text: str, problems: list[TableProblem]) -> Header:
    table = raw.table
    if is_ignored_header(text):
        return Header(text, "")
    if text.startswith(CUSTOM_PREFIX):
        key = text[len(CUSTOM_PREFIX) :].strip()
        if not table.custom:
            problems.append(
                TableProblem(
                    raw.where(column=text), f"{table.name} takes no custom columns"
                )
            )
            return Header(text, "")
        if not key:
            problems.append(
                TableProblem(
                    raw.where(column=text), "custom: needs a name after the colon"
                )
            )
            return Header(text, "")
        return Header(text, "custom", custom_key=key)
    name, _, language = text.partition("@")
    column = table.columns_by_name.get(name)
    if column is None:
        problems.append(
            TableProblem(
                raw.where(column=text),
                f"not a column of {table.name}; expected "
                + ", ".join(
                    f"{c.name}@<language>" if c.multilingual else c.name
                    for c in table.columns
                )
                + (", custom:<name>" if table.custom else "")
                + ", or a notes column starting with # or _",
            )
        )
        return Header(text, "")
    if column.multilingual:
        if not language:
            problems.append(
                TableProblem(
                    raw.where(column=text),
                    f"needs a language, as in {name}@en or {name}@fr-CA",
                )
            )
            return Header(text, "")
        if not LANGUAGE_TAG.match(language):
            problems.append(
                TableProblem(
                    raw.where(column=text), f"{language!r} is not a language tag"
                )
            )
            return Header(text, "")
        return Header(text, name, language=language)
    if language:
        problems.append(
            TableProblem(raw.where(column=text), f"{name} does not take a language")
        )
        return Header(text, "")
    return Header(text, name)
