"""Bulk-load DDI items from spreadsheets: a folder of CSV files or one workbook.

Each table (``studies``, ``concepts``, ``questions``, ``flow``,
``variables``, ``datasets`` and the others in :data:`TABLES`, plus
``settings``) is one CSV file, or one sheet of an ``.xlsx`` workbook. Rows
point at each other by ``id``: a variable's ``question`` column holds a
question's ``id``. Text in several languages goes in one column per language
(``label@en``, ``label@fr``); properties of your own go in ``custom:<name>``
columns.

::

    from ddi_l.tables import load_tables, write_table_templates

    write_table_templates("my-survey", example=True)   # start from the example
    tables = load_tables("my-survey")
    tables.to_fragment().save("my-survey.xml")         # for Colectica

The guide, with every column, is the "Load DDI from spreadsheets" page of the
documentation; the templates are on the "Spreadsheet templates" page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from ..models.base import MaintainableBase, Reference
from ._build import FRAGMENT_ONLY, build, read_settings
from ._read import TableImportError, TableProblem, read_tables, upload_name
from ._spec import TABLES, Column, Table
from ._templates import write_table_templates

if TYPE_CHECKING:
    from ..document import DDIFragment, Document
    from ..models.concept import Concept, Universe
    from ..models.datacollection import QuestionItem
    from ..models.logicalproduct import Category, CodeList, Variable

__all__ = [
    "TABLES",
    "Column",
    "Table",
    "TableImport",
    "TableImportError",
    "TableProblem",
    "load_tables",
    "write_table_templates",
]


@dataclass
class TableImport:
    """The DDI items a set of tables describes.

    Every item is a typed model (``Concept``, ``Variable``, ...) that can be
    edited before it is written.
    """

    agency: str
    version: str
    language: str
    tables: dict[str, list[MaintainableBase]] = field(default_factory=dict)
    """Items by the table they come from, in row order. Items a table implies
    are listed under it: the categories of ``codes``, the data collection of
    ``studies``, the sequences of ``flow``, the data relationships of
    ``datasets``, the processing event schemes of ``processing_events``."""
    _keys: dict[str, dict[str, MaintainableBase]] = field(
        default_factory=dict, repr=False
    )

    @property
    def items(self) -> list[MaintainableBase]:
        """Every item, in the order of the tables."""
        return [item for table in TABLES for item in self.tables.get(table.name, [])]

    @property
    def concepts(self) -> list[Concept]:
        """Items of ``concepts``."""
        return self._of("concepts")  # type: ignore[return-value]

    @property
    def universes(self) -> list[Universe]:
        """Items of ``universes``."""
        return self._of("universes")  # type: ignore[return-value]

    @property
    def categories(self) -> list[Category]:
        """The categories of ``codes``."""
        return self._of("codes")  # type: ignore[return-value]

    @property
    def code_lists(self) -> list[CodeList]:
        """Items of ``code_lists``, holding their codes."""
        return self._of("code_lists")  # type: ignore[return-value]

    @property
    def questions(self) -> list[QuestionItem]:
        """Items of ``questions``."""
        return self._of("questions")  # type: ignore[return-value]

    @property
    def variables(self) -> list[Variable]:
        """Items of ``variables``."""
        return self._of("variables")  # type: ignore[return-value]

    def _of(self, table: str) -> list[MaintainableBase]:
        return list(self.tables.get(table, []))

    def get(self, table: str, key: str) -> MaintainableBase:
        """The item built from the row of ``table`` whose ``id`` is ``key``.

        Raises:
            KeyError: If ``table`` has no row with that ``id``.
        """
        return self._keys[table][key]

    def to_fragment(
        self,
        *,
        top_level: MaintainableBase | Reference | None = None,
        version_date: str | None = None,
    ) -> DDIFragment:
        """The items as a ``FragmentInstance``, one item per fragment.

        Written the way Colectica Designer writes an export, so the file
        imports into a Colectica repository. Without ``top_level`` the
        fragment names the only study, or the only group, as its top-level
        item, and otherwise none.
        """
        from ..document import DDIFragment

        if top_level is None:
            for table in ("groups", "studies"):
                rows = self._keys.get(table, {})
                if len(rows) == 1:
                    top_level = next(iter(rows.values()))
                    break
        fragment = DDIFragment.from_items(
            self.items, top_level=top_level, version_date=version_date
        )
        if top_level is None:
            fragment.set_top_level_reference(None)
        return fragment

    def to_study(self, title: str, *, lang: str | None = None) -> Document:
        """The items inside a new study, as a ``DDIInstance`` document.

        A study document has one study, so the tables that describe studies
        themselves, their groups, people, variable groups, processing,
        quality or comparisons do not fit in it: load those with
        :meth:`to_fragment`.

        Raises:
            TableImportError: If such a table has rows.
        """
        from ..document import new_study

        problems = [
            TableProblem(table, "has rows; a study document has no place for them")
            for table in FRAGMENT_ONLY
            if self.tables.get(table)
        ]
        if problems:
            raise TableImportError(
                "These tables need to_fragment() (ddi tables import without --study):",
                problems=problems,
            )
        document = new_study(
            title=title,
            agency=self.agency,
            version=self.version,
            lang=lang or self.language,
        )
        for item in self.items:
            document.attach(item)
        return document


def load_tables(
    source: str | Path | bytes,
    *,
    agency: str | None = None,
    version: str | None = None,
    language: str | None = None,
) -> TableImport:
    """Load the metadata tables in ``source`` as DDI items.

    Args:
        source: A folder of CSV files (``concepts.csv``, ``variables.csv``,
            ...), a ``.zip`` of them (at its top or in one folder), or an
            ``.xlsx`` workbook with one sheet per table. Tables you do not
            need can be left out. The bytes of a workbook or a zip are read
            in memory, and problems name them ``workbook.xlsx`` or
            ``tables.zip``.
        agency: The agency of every item; overrides ``settings``.
        version: The version of items without their own; overrides
            ``settings``.
        language: The language of names; overrides ``settings``.

    Returns:
        The items, as typed models.

    Raises:
        TableImportError: Listing every problem found, each with its file,
            row and column.
    """
    if isinstance(source, bytes):
        tables, problems = read_tables(source)
        label = upload_name(source)
    else:
        path = Path(source)
        if not path.exists():
            raise TableImportError(f"{path} does not exist.")
        tables, problems = read_tables(path)
        label = str(path)
    if not any(raw.rows for name, raw in tables.items() if name != "settings"):
        problems.append(
            TableProblem(
                Path(label).name,
                "no rows found; expected files or sheets named "
                + ", ".join(table.name for table in TABLES),
            )
        )
    resolved = read_settings(
        tables, agency=agency, version=version, language=language, problems=problems
    )
    built = build(
        tables,
        agency=resolved[0],
        version=resolved[1],
        language=resolved[2],
        problems=problems,
    )
    if problems:
        count = len(problems)
        raise TableImportError(
            f"{label} has {count} problem{'s' if count != 1 else ''}:",
            problems=problems,
        )
    return TableImport(
        agency=built.agency,
        version=built.version,
        language=built.language,
        tables=built.tables,
        _keys=built.keys,
    )
