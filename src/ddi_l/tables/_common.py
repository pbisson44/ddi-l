"""What every table builder shares: the load context, cell readers, references.

Items are created in two passes. The first gives every row of every item
table its identity (agency, identifier, version), so a reference can point at
any row, in any table, before or after it. The second builds the items.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Protocol

from .._etree import Element, create_element
from ..constants import (
    CONCEPTUAL_COMPONENT_NS,
    DATA_COLLECTION_NS,
    LOGICAL_PRODUCT_NS,
    REUSABLE_NS,
    XML_NS,
)
from ..models.base import (
    InternationalString,
    MaintainableBase,
    Reference,
    UserAttributePair,
    order_by_schema,
    qn,
)
from ..models.logicalproduct import (
    CodeRepresentation,
    DateTimeRepresentation,
    NumberRange,
    NumericRepresentation,
    TextRepresentation,
)
from ._read import RawTable, Row, TableProblem
from ._spec import MULTI_VALUE_SEPARATOR, RESPONSE_TYPES, audience_language

# Identifiers derived from (agency, table, id) live under this namespace, so
# the same workbook always yields the same UUIDs.
_ID_NAMESPACE = uuid.UUID("0f1f2bb6-6c55-4b11-9d3b-9f2a5f1c6e0a")

_TRUE = {"true", "yes", "y", "1", "vrai", "oui", "o"}
_FALSE = {"false", "no", "n", "0", "faux", "non"}

Representation = (
    CodeRepresentation
    | NumericRepresentation
    | TextRepresentation
    | DateTimeRepresentation
)


class Identified(Protocol):
    """What a reference needs of an item: a typed model, or an Identity."""

    @property
    def agency(self) -> str | None: ...
    @property
    def identifier(self) -> str | None: ...
    @property
    def version(self) -> str | None: ...


@dataclass
class Identity:
    """A row's DDI identity, before its item is built."""

    agency: str
    identifier: str
    version: str


@dataclass
class Entry:
    """One row of an item table: what it is now, and where it came from."""

    item: Identified
    raw: RawTable
    row: Row


@dataclass
class Context:
    agency: str
    version: str
    language: str
    problems: list[TableProblem] = field(default_factory=list)
    # table name -> row id -> entry
    index: dict[str, dict[str, Entry]] = field(default_factory=dict)
    # (table, row id) -> the item's element, built in place until every
    # table is read: a group's members come from other tables' rows.
    elements: dict[tuple[str, str], Element] = field(default_factory=dict)
    # Every element, with the table it comes from, in build order.
    out: list[tuple[str, Element]] = field(default_factory=list)
    # (table, row id) of a question or represented variable -> its response,
    # for the variables that take it over
    responses: dict[tuple[str, str], Representation] = field(default_factory=dict)
    # "code_list/value" and shared category keys -> the category
    categories: dict[str, Identity] = field(default_factory=dict)
    # question id -> its wordings from question_texts, as
    # (language, audience, text, where)
    question_texts: dict[str, list[tuple[str, str | None, str, str]]] = field(
        default_factory=dict
    )
    # dataset id -> its variables, in the order of the variables table
    dataset_variables: dict[str, list[Identified]] = field(default_factory=dict)
    # study id -> the data collection and processing event scheme the
    # tables imply for it, made when a row first needs them
    data_collections: dict[str, Element] = field(default_factory=dict)
    processing_schemes: dict[str, Element] = field(default_factory=dict)
    # study id -> the methodologies row that gave its methodology
    methodologies: dict[str, int] = field(default_factory=dict)

    def problem(
        self, raw: RawTable, row: Row | None, column: str | None, message: str
    ) -> None:
        self.problems.append(TableProblem(raw.where(row, column), message))

    def identifier(self, table: str, key: str) -> str:
        return str(uuid.uuid5(_ID_NAMESPACE, f"{self.agency}|{table}|{key}"))

    def identity(self, table: str, key: str) -> Identity:
        """A derived identity for something the tables imply, not a row."""
        return Identity(self.agency, self.identifier(table, key), self.version)

    def emit(self, table: str, element: Element, key: str | None = None) -> Element:
        """Add an item's element to the output, under the table it comes from."""
        self.out.append((table, element))
        if key is not None:
            self.elements[(table, key)] = element
        return element


def check_required_columns(ctx: Context, raw: RawTable) -> None:
    present = {header.column for header in raw.headers}
    for column in raw.table.columns:
        if column.required and column.name not in present:
            ctx.problem(raw, None, column.name, "this required column is missing")


def reserve(ctx: Context, raw: RawTable, row: Row) -> Identity | None:
    """Give a row its identity and index it by ``id``; None if it cannot be."""
    key = row.cells.get("id")
    if not key:
        ctx.problem(raw, row, "id", "is empty")
        return None
    entries = ctx.index.setdefault(raw.table.name, {})
    if key in entries:
        first = entries[key].row
        ctx.problem(raw, row, "id", f"{key!r} is already the id of row {first.number}")
        return None
    identity = Identity(
        ctx.agency,
        row.cells.get("ddi_id") or ctx.identifier(raw.table.name, key),
        row.cells.get("version") or ctx.version,
    )
    entries[key] = Entry(identity, raw, row)
    return identity


def entry_of(ctx: Context, raw: RawTable, row: Row) -> Entry | None:
    """The row's entry; None when its id was empty or a duplicate."""
    entry = ctx.index.get(raw.table.name, {}).get(row.cells.get("id", ""))
    if entry is None or entry.row is not row:
        return None
    return entry


def strings(
    raw: RawTable, row: Row, column: str, *, child_tag: str = "Content"
) -> list[InternationalString]:
    """Every ``column@<language>`` value of ``row``, in header order."""
    found: list[InternationalString] = []
    for header in raw.headers:
        if header.column == column and header.raw in row.cells:
            found.append(
                InternationalString(
                    text=row.cells[header.raw],
                    lang=header.language,
                    child_tag=child_tag,
                )
            )
    return found


def values(row: Row, column: str) -> list[str]:
    """The ``|``-separated values of a cell."""
    value = row.cells.get(column)
    if not value:
        return []
    return [part.strip() for part in value.split(MULTI_VALUE_SEPARATOR) if part.strip()]


def custom_pairs(raw: RawTable, row: Row) -> list[UserAttributePair]:
    """``custom:<name>`` cells as r:UserAttributePair.

    The key gets Colectica's ``extension:`` prefix, which is how Colectica
    Designer names its custom fields, unless it already has a prefix.
    """
    pairs: list[UserAttributePair] = []
    for header in raw.headers:
        if header.custom_key is None or header.raw not in row.cells:
            continue
        key = header.custom_key
        if ":" not in key:
            key = f"extension:{key}"
        pairs.append(UserAttributePair(key=key, value=row.cells[header.raw]))
    return pairs


def reference(item: Identified, type_of_object: str) -> Reference:
    return Reference(
        type_of_object=type_of_object,
        agency=item.agency,
        identifier=item.identifier,
        version=item.version,
    )


@dataclass(frozen=True)
class Hit:
    """A resolved reference: the row of ``table`` whose id is ``key``."""

    table: str
    key: str
    item: Identified


def lookup(
    ctx: Context, raw: RawTable, row: Row, column: str, *tables: str
) -> list[Hit]:
    """Resolve the id(s) in ``column`` against ``tables``.

    With several tables, an id must be in exactly one of them.
    """
    found: list[Hit] = []
    for key in values(row, column):
        hits = [
            Hit(table, key, ctx.index[table][key].item)
            for table in tables
            if key in ctx.index.get(table, {})
        ]
        if not hits:
            ctx.problem(
                raw, row, column, f"no row in {' or '.join(tables)} has id {key!r}"
            )
        elif len(hits) > 1:
            ctx.problem(
                raw,
                row,
                column,
                f"{key!r} is an id in {' and '.join(hit.table for hit in hits)}; "
                "use an id that is in one of them only",
            )
        else:
            found.append(hits[0])
    return found


def single(
    ctx: Context, raw: RawTable, row: Row, column: str, *tables: str
) -> Hit | None:
    found = lookup(ctx, raw, row, column, *tables)
    if len(found) > 1:
        ctx.problem(raw, row, column, "takes one id, not several")
    return found[0] if found else None


def boolean(ctx: Context, raw: RawTable, row: Row, column: str) -> bool | None:
    value = row.cells.get(column)
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    ctx.problem(raw, row, column, f"{value!r} is not true or false")
    return None


def is_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


def representation(
    ctx: Context, raw: RawTable, row: Row, kind_column: str
) -> Representation | None:
    """The representation the row's ``kind_column`` and detail columns give."""
    kind = (row.cells.get(kind_column) or "").strip().lower()
    if not kind:
        return None
    if kind not in RESPONSE_TYPES:
        ctx.problem(
            raw,
            row,
            kind_column,
            f"{row.cells[kind_column]!r} is not one of " + ", ".join(RESPONSE_TYPES),
        )
        return None
    if kind == "code":
        code_list = single(ctx, raw, row, "code_list", "code_lists")
        if "code_list" not in row.cells:
            ctx.problem(raw, row, "code_list", f"{kind_column} code needs a code list")
        if code_list is None:
            return None
        return CodeRepresentation(
            code_list_reference=reference(code_list.item, "CodeList")
        )
    if kind == "numeric":
        low, high = row.cells.get("min"), row.cells.get("max")
        for column, value in (("min", low), ("max", high)):
            if value is not None and not is_number(value):
                ctx.problem(raw, row, column, f"{value!r} is not a number")
        numeric_type = row.cells.get("numeric_type")
        if numeric_type is None:
            ctx.problem(
                raw,
                row,
                "numeric_type",
                f"{kind_column} numeric needs a numeric_type, such as Integer",
            )
        return NumericRepresentation(
            number_range=NumberRange(low=low, high=high) if low or high else None,
            numeric_type_code=numeric_type,
        )
    if kind == "text":
        attributes: dict[str, str] = {}
        max_length = row.cells.get("max_length")
        if max_length is not None:
            if max_length.isdigit():
                attributes["maxLength"] = max_length
            else:
                ctx.problem(
                    raw, row, "max_length", f"{max_length!r} is not a whole number"
                )
        return TextRepresentation(other_attributes=attributes)
    date_type = row.cells.get("date_type")
    if date_type is None:
        ctx.problem(
            raw,
            row,
            "date_type",
            f"{kind_column} datetime needs a date_type, such as Date",
        )
    return DateTimeRepresentation(date_type_code=date_type)


_DOMAIN_TAGS = {
    "CodeRepresentation": "CodeDomain",
    "NumericRepresentation": "NumericDomain",
    "TextRepresentation": "TextDomain",
    "DateTimeRepresentation": "DateTimeDomain",
}


def as_response_domain(representation_element: Element) -> Element:
    """A variable representation as a question's response domain.

    d:CodeDomain and its siblings extend the same r:*RepresentationBaseType
    as r:CodeRepresentation, so only the element name changes.
    """
    local = representation_element.tag.rsplit("}", 1)[-1]
    domain = create_element(qn(DATA_COLLECTION_NS, _DOMAIN_TAGS[local]))
    for name, value in representation_element.attrib.items():
        domain.set(name, value)
    for child in list(representation_element):
        domain.append(child)
    return domain


# ---------------------------------------------------------------------------
# Writing XML
# ---------------------------------------------------------------------------


def el(
    tag: str, *children: Element | None, text: str | None = None, **attrs: str
) -> Element:
    """An element with ``children`` (None skipped), ``text`` and ``attrs``."""
    element = create_element(tag)
    for name, value in attrs.items():
        element.set(name, value)
    if text is not None:
        element.text = text
    for child in children:
        if child is not None:
            element.append(child)
    return element


def r(local: str) -> str:
    return qn(REUSABLE_NS, local)


def d(local: str) -> str:
    return qn(DATA_COLLECTION_NS, local)


def lp(local: str) -> str:
    return qn(LOGICAL_PRODUCT_NS, local)


def cc(local: str) -> str:
    return qn(CONCEPTUAL_COMPONENT_NS, local)


def identification(item: Identified) -> list[Element]:
    """r:Agency, r:ID and r:Version of ``item``."""
    return [
        el(r("Agency"), text=item.agency),
        el(r("ID"), text=item.identifier),
        el(r("Version"), text=item.version),
    ]


def ref(tag: str, item: Identified, type_of_object: str) -> Element:
    """A reference element ``tag`` (Clark notation) to ``item``."""
    namespace, local = tag[1:].split("}", 1)
    return reference(item, type_of_object).to_xml(local, namespace=namespace)


def multilingual(
    tag: str, found: list[InternationalString], *, child_tag: str = "Content"
) -> Element | None:
    """``tag`` holding one ``r:<child_tag>`` per language; None if empty."""
    if not found:
        return None
    container = create_element(tag)
    for string in found:
        container.append(string.to_child(child_tag))
    return container


def name_element(tag: str, ctx: Context, row: Row) -> Element:
    """A Name element holding ``name`` (or ``id``) in the names language."""
    string = InternationalString(
        text=row.cells.get("name") or row.cells["id"], lang=ctx.language
    )
    return el(tag, string.to_child("String"))


def literal_text(
    tag: str, text: str, language: str, audience: str | None = None
) -> Element:
    """``tag`` (a d:DynamicTextType) holding ``text``, as Colectica writes it.

    One element per language and audience, each with ``audienceLanguage``.
    """
    inner = el(d("Text"), text=text, **{qn(XML_NS, "lang"): language})
    return el(
        tag,
        el(d("LiteralText"), inner),
        audienceLanguage=audience_language(language, audience),
    )


def literal_texts(
    tag: str, found: Iterable[InternationalString], default_language: str
) -> list[Element]:
    """:func:`literal_text` for each of ``found``."""
    return [
        literal_text(tag, string.text, string.lang or default_language)
        for string in found
    ]


def item_element(
    tag: str, identity: Identified, raw: RawTable | None, row: Row | None
) -> Element:
    """An item's root with identification, custom pairs, labels, descriptions.

    Builders append the other children in any order: :func:`typed` puts them
    in schema order.
    """
    root = el(tag, *identification(identity))
    if raw is not None and row is not None:
        for pair in custom_pairs(raw, row):
            root.append(pair.to_xml())
        for column, child in (("label", "Label"), ("description", "Description")):
            container = multilingual(r(child), strings(raw, row, column))
            if container is not None:
                root.append(container)
    return root


def typed(element: Element) -> MaintainableBase:
    """The typed model of a built item element, its children in schema order."""
    order_by_schema(element)
    MaintainableBase.maintainable_types()
    model = MaintainableBase.for_tag(element.tag)
    if model is None:  # pragma: no cover - every Fragment item type has one
        raise TypeError(f"no typed model for {element.tag}")
    return model.from_xml(element)
