"""Read and write the cells of ``.xlsx`` workbooks with the standard library.

A workbook is a zip of XML parts, and a metadata workbook is plain text
cells, so neither openpyxl nor pandas is needed. Only what the tables use is
supported: text, numbers and booleans, one header row, no formulas.
"""

from __future__ import annotations

import re
import zipfile
from collections.abc import Iterable
from pathlib import Path
from typing import IO
from xml.sax.saxutils import escape

from defusedxml import ElementTree  # type: ignore[import-untyped]

_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"

_CELL_REF = re.compile(r"^([A-Z]+)(\d+)$")

# A workbook can come from anyone (``POST /v1/tables/import``), so what it may
# make the reader do is bounded. Excel itself stops at 1,048,576 rows and
# 16,384 columns; a cell beyond them is not one a spreadsheet wrote.
MAX_ROWS = 1_048_576
MAX_COLUMNS = 16_384
# What every part read may expand to, together. A table of metadata is a few
# megabytes; this leaves room while refusing a zip bomb.
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_ENTRIES = 10_000


class ArchiveBudget:
    """Read zip entries while their declared sizes stay within the limits.

    ``zipfile`` never inflates an entry past its declared size, so checking
    the declared sizes bounds what reading can allocate.
    """

    def __init__(self, archive: zipfile.ZipFile) -> None:
        if len(archive.infolist()) > MAX_ENTRIES:
            raise ValueError(f"it holds more than {MAX_ENTRIES:,} files")
        self._archive = archive
        self._left = MAX_UNCOMPRESSED_BYTES

    def read(self, name: str) -> bytes:
        size = self._archive.getinfo(name).file_size
        if size > self._left:
            raise ValueError(
                f"it expands to more than {MAX_UNCOMPRESSED_BYTES // 2**20} MiB"
            )
        self._left -= size
        return self._archive.read(name)


def _q(local: str, namespace: str = _MAIN) -> str:
    return f"{{{namespace}}}{local}"


def _column_index(letters: str) -> int:
    index = 0
    for letter in letters:
        index = index * 26 + (ord(letter) - ord("A") + 1)
    return index - 1


def _column_letters(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def _number_text(value: str) -> str:
    """Excel stores 2 as "2" but some writers store "2.0"; keep it 2."""
    if re.fullmatch(r"-?\d+\.0+", value):
        return value.split(".", 1)[0]
    return value


def read_workbook(path: Path | IO[bytes]) -> dict[str, list[list[str]]]:
    """Return each sheet's rows of cell text, keyed by sheet name.

    Raises:
        ValueError: The file is not a workbook this reader can read, or goes
            beyond the limits above. ``zipfile.BadZipFile``, ``KeyError`` and
            XML parse errors may also escape; callers report them all as an
            unreadable workbook.
    """
    with zipfile.ZipFile(path) as archive:
        budget = ArchiveBudget(archive)
        names = set(archive.namelist())
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ElementTree.fromstring(budget.read("xl/sharedStrings.xml"))
            for item in root.iter(_q("si")):
                # Rich text splits a string into runs; join their text.
                shared.append("".join(t.text or "" for t in item.iter(_q("t"))))
        rels_root = ElementTree.fromstring(budget.read("xl/_rels/workbook.xml.rels"))
        targets = {
            rel.get("Id"): rel.get("Target", "")
            for rel in rels_root.iter(_q("Relationship", _PKG_REL))
        }
        workbook = ElementTree.fromstring(budget.read("xl/workbook.xml"))
        sheets: dict[str, list[list[str]]] = {}
        for sheet in workbook.iter(_q("sheet")):
            target = targets[sheet.get(_q("id", _REL))]
            part = target.lstrip("/") if target.startswith("/") else f"xl/{target}"
            sheets[sheet.get("name", "")] = _read_sheet(budget.read(part), shared)
        return sheets


def _read_sheet(data: bytes, shared: list[str]) -> list[list[str]]:
    root = ElementTree.fromstring(data)
    rows: list[list[str]] = []
    for row in root.iter(_q("row")):
        cells: dict[int, str] = {}
        for position, cell in enumerate(row.iter(_q("c"))):
            reference = cell.get("r")
            match = _CELL_REF.match(reference or "")
            column = _column_index(match.group(1)) if match else position
            if column >= MAX_COLUMNS:
                raise ValueError(f"cell {reference} is beyond Excel's last column")
            kind = cell.get("t")
            value_el = cell.find(_q("v"))
            raw = value_el.text if value_el is not None and value_el.text else ""
            if kind == "s":
                text = shared[int(raw)] if raw else ""
            elif kind == "inlineStr":
                text = "".join(t.text or "" for t in cell.iter(_q("t")))
            elif kind == "b":
                text = "true" if raw == "1" else "false"
            elif kind in ("str", "e"):
                text = raw
            else:
                text = _number_text(raw)
            cells[column] = text
        width = max(cells, default=-1) + 1
        index = int(row.get("r", len(rows) + 1)) - 1
        if not 0 <= index < MAX_ROWS:
            raise ValueError(f"row {index + 1} is beyond Excel's last row")
        # Keep spreadsheet row numbers: pad skipped rows with empty ones.
        while len(rows) < index:
            rows.append([])
        rows.append([cells.get(i, "") for i in range(width)])
    return rows


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

# Cell styles: 0 is Excel's default, 1 is text (number format 49, "@"), 2 is
# bold text for the header row. Text is the point: a code typed as 01 stays
# 01 instead of becoming the number 1.
_STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    f'<styleSheet xmlns="{_MAIN}">'
    '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
    '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
    '<fills count="2"><fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill></fills>'
    '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/>'
    "</border></borders>"
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
    'borderId="0"/></cellStyleXfs>'
    '<cellXfs count="3">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="49" fontId="0" fillId="0" borderId="0" xfId="0" '
    'applyNumberFormat="1"/>'
    '<xf numFmtId="49" fontId="1" fillId="0" borderId="0" xfId="0" '
    'applyNumberFormat="1" applyFont="1"/>'
    "</cellXfs>"
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/>'
    "</cellStyles></styleSheet>"
)


def _sheet_xml(rows: list[list[str]], *, header: bool) -> str:
    width = max((len(row) for row in rows), default=1)
    # Every column is text, including cells typed in later.
    cols = (
        f'<cols><col min="1" max="{max(width, 1)}" width="24" style="1" '
        'customWidth="1"/></cols>'
    )
    pane = (
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" '
        'topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        "</sheetView></sheetViews>"
        if header
        else '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
    )
    body: list[str] = []
    for row_number, row in enumerate(rows, start=1):
        style = "2" if header and row_number == 1 else "1"
        cells = "".join(
            f'<c r="{_column_letters(i)}{row_number}" s="{style}" t="inlineStr">'
            f'<is><t xml:space="preserve">{escape(value)}</t></is></c>'
            for i, value in enumerate(row)
            if value != ""
        )
        body.append(f'<row r="{row_number}">{cells}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<worksheet xmlns="{_MAIN}" xmlns:r="{_REL}">{pane}{cols}'
        f"<sheetData>{''.join(body)}</sheetData></worksheet>"
    )


def write_workbook(
    path: Path | IO[bytes], sheets: Iterable[tuple[str, list[list[str]], bool]]
) -> None:
    """Write ``(name, rows, has_header)`` sheets to ``path``, byte-stable.

    Every zip entry gets a fixed timestamp, so writing the same sheets twice
    gives the same bytes.
    """
    sheets = list(sheets)
    parts: list[tuple[str, str]] = []
    overrides = [
        '<Override PartName="/xl/workbook.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
    ]
    workbook_sheets: list[str] = []
    workbook_rels: list[str] = []
    for number, (name, rows, header) in enumerate(sheets, start=1):
        parts.append(
            (f"xl/worksheets/sheet{number}.xml", _sheet_xml(rows, header=header))
        )
        overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{number}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>'
        )
        workbook_sheets.append(
            f'<sheet name="{escape(name)}" sheetId="{number}" r:id="rId{number}"/>'
        )
        workbook_rels.append(
            f'<Relationship Id="rId{number}" Type="{_REL}/worksheet" '
            f'Target="worksheets/sheet{number}.xml"/>'
        )
    workbook_rels.append(
        f'<Relationship Id="rId{len(sheets) + 1}" Type="{_REL}/styles" '
        'Target="styles.xml"/>'
    )
    declaration = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    parts = [
        (
            "[Content_Types].xml",
            declaration
            + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
            'content-types"><Default Extension="rels" ContentType="application/'
            'vnd.openxmlformats-package.relationships+xml"/><Default '
            'Extension="xml" ContentType="application/xml"/>'
            + "".join(overrides)
            + "</Types>",
        ),
        (
            "_rels/.rels",
            declaration + f'<Relationships xmlns="{_PKG_REL}"><Relationship Id="rId1" '
            f'Type="{_REL}/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        ),
        (
            "xl/workbook.xml",
            declaration
            + f'<workbook xmlns="{_MAIN}" xmlns:r="{_REL}"><sheets>'
            + "".join(workbook_sheets)
            + "</sheets></workbook>",
        ),
        (
            "xl/_rels/workbook.xml.rels",
            declaration
            + f'<Relationships xmlns="{_PKG_REL}">'
            + "".join(workbook_rels)
            + "</Relationships>",
        ),
        ("xl/styles.xml", _STYLES),
        *parts,
    ]
    write_zip(path, [(name, text.encode("utf-8")) for name, text in parts])


def write_zip(path: Path | IO[bytes], entries: Iterable[tuple[str, bytes]]) -> None:
    """Write a zip whose bytes depend only on ``entries``."""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
