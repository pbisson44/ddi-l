"""Lightweight linting helpers for DDI instance documents."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, replace
from typing import (
    TYPE_CHECKING,
    Any,
    TypeAlias,
    cast,
)

from . import schema_loader
from ._etree import USING_LXML, Element
from .constants import XML_NS, NamespaceSet, get_namespace_set
from .models import InternationalString, MaintainableBase, qn
from .models._generated.label_slots import TAGS_ALLOWING_LABEL

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from .document import DDIDocument, DDIFragment


_HAS_GETROOTTREE = hasattr(Element, "getroottree")


if (
    USING_LXML and _HAS_GETROOTTREE
):  # pragma: no cover - helper relies on lxml when available

    def _element_path(element: Element) -> str:
        """Return a stable path for ``element`` within the document tree.

        Args:
            element: The element whose location should be described.

        Returns:
            str: An absolute XPath representing the element's position when
            lxml is available, derived from the element's root tree.

        Note:
            When running with the lxml backend the location is calculated using
            :meth:`lxml.etree.ElementTree.getpath`, providing an absolute XPath.
            The stdlib backend falls back to returning only the element tag (see
            the alternate implementation below).
        """
        return element.getroottree().getpath(element)

else:  # pragma: no cover - stdlib fallback exercised in tests

    def _element_path(element: Element) -> str:
        """Return a best-effort description of ``element`` within the tree.

        Args:
            element: The element whose location should be described.

        Returns:
            str: The tag name of the element, used by stdlib ``xml`` where the
            richer path information provided by lxml is unavailable.
        """
        return element.tag


# Lint rules accept a full instance or a fragment; both expose ``root``.
LintTarget: TypeAlias = "DDIDocument | DDIFragment"
DocumentRule = Callable[["DDIDocument"], Iterable["LintFinding"]]
ElementRule = Callable[[Element], Iterable["LintFinding"]]


_UNSET = object()


@dataclass(frozen=True)
class LintFinding:
    """Container describing a single lint finding."""

    rule_id: str
    message: str
    severity: str = "error"
    location: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        """Return a JSON-serialisable representation of the finding."""
        return {
            "rule_id": self.rule_id,
            "message": self.message,
            "severity": self.severity,
            "location": self.location,
        }


def _normalize_sequence(values: Sequence[str]) -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for value in values:
        if value:
            seen.setdefault(value, None)
    return tuple(seen)


@dataclass(frozen=True)
class LintConfiguration:
    """Collection of options governing built-in lint behaviour."""

    allowed_agencies: tuple[str, ...] | None = None
    require_citation: bool = True
    require_citation_title: bool = True
    required_citation_languages: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.allowed_agencies is not None:
            object.__setattr__(
                self, "allowed_agencies", _normalize_sequence(self.allowed_agencies)
            )
        object.__setattr__(
            self,
            "required_citation_languages",
            _normalize_sequence(self.required_citation_languages),
        )


@dataclass
class _LintRule:
    rule_id: str
    callback: DocumentRule | ElementRule
    target: str

    def run(self, document: LintTarget) -> Iterator[LintFinding]:
        target = document if self.target == "document" else document.root
        for finding in self.callback(target):  # type: ignore[arg-type]
            if finding.rule_id != self.rule_id:
                finding = LintFinding(
                    rule_id=self.rule_id,
                    message=finding.message,
                    severity=finding.severity,
                    location=finding.location,
                )
            yield finding


_REGISTRY: dict[str, _LintRule] = {}
_PROFILE_REGISTRY: dict[str, tuple[str, ...]] = {}

DDI_PROFILE_DEFAULT = "DDI_PROFILE_DEFAULT"

# The allowed-agency check is opt-in: only a deployment knows which agency
# identifiers are acceptable. Populate it with
# `configure_lint(allowed_agencies=[...])` or `--allowed-agency`. While it is
# empty the rule still reports a *missing* agency.
ALLOWED_AGENCIES: set[str] = set()

_DEFAULT_CONFIGURATION = LintConfiguration(
    allowed_agencies=None,
    require_citation=True,
    require_citation_title=True,
    required_citation_languages=("en",),
)
_CONFIG = _DEFAULT_CONFIGURATION


def get_lint_configuration() -> LintConfiguration:
    """Return the active :class:`LintConfiguration`."""
    return _CONFIG


def _update_allowed_agencies(values: Sequence[str] | None) -> None:
    ALLOWED_AGENCIES.clear()
    if values is not None:
        ALLOWED_AGENCIES.update(values)


def set_lint_configuration(configuration: LintConfiguration) -> LintConfiguration:
    """Replace the active lint configuration."""
    global _CONFIG
    _update_allowed_agencies(configuration.allowed_agencies)
    _CONFIG = configuration
    return _CONFIG


def reset_lint_configuration() -> LintConfiguration:
    """Restore the default lint configuration."""
    return set_lint_configuration(_DEFAULT_CONFIGURATION)


def configure_lint(
    *,
    allowed_agencies: Sequence[str] | object | None = _UNSET,
    require_citation: bool | object | None = _UNSET,
    require_citation_title: bool | object | None = _UNSET,
    required_citation_languages: Sequence[str] | object | None = _UNSET,
) -> LintConfiguration:
    """Update and return the active :class:`LintConfiguration`.

    Only options explicitly provided are modified.  ``allowed_agencies`` accepts
    ``None`` to disable the built-in agency allow-list and any other sequence to
    replace it.  ``required_citation_languages`` expects an iterable of BCP 47
    language identifiers that must be present on citation titles.
    """
    updates: dict[str, Any] = {}
    if allowed_agencies is not _UNSET:
        agencies = cast(Sequence[str] | None, allowed_agencies)
        if agencies is None:
            updates["allowed_agencies"] = None
        else:
            updates["allowed_agencies"] = _normalize_sequence(tuple(agencies))
    if require_citation is not _UNSET and require_citation is not None:
        updates["require_citation"] = bool(require_citation)
    if require_citation_title is not _UNSET and require_citation_title is not None:
        updates["require_citation_title"] = bool(require_citation_title)
    if (
        required_citation_languages is not _UNSET
        and required_citation_languages is not None
    ):
        languages = cast(Sequence[str], required_citation_languages)
        updates["required_citation_languages"] = _normalize_sequence(tuple(languages))

    if not updates:
        return _CONFIG

    configuration = replace(_CONFIG, **updates)
    return set_lint_configuration(configuration)


def register_rule(
    rule_id: str,
    callback: DocumentRule | ElementRule,
    *,
    target: str = "document",
) -> None:
    """Register a linting rule.

    ``target`` determines whether ``callback`` receives the whole
    :class:`DDIDocument` or the root :class:`Element` of the document.
    """
    if rule_id in _REGISTRY:
        raise ValueError(f"Rule {rule_id!r} is already registered.")
    if target not in {"document", "element"}:
        raise ValueError("target must be 'document' or 'element'.")
    _REGISTRY[rule_id] = _LintRule(rule_id=rule_id, callback=callback, target=target)


def iter_registered_rules() -> Iterator[tuple[str, str | None]]:
    """Yield the registered lint rules and any available descriptions."""
    for rule_id, rule in _REGISTRY.items():
        description = None
        if rule.callback.__doc__:
            description = rule.callback.__doc__.strip().splitlines()[0]
        yield rule_id, description


def register_profile(profile_name: str, rules: Sequence[str]) -> None:
    """Register a named collection of lint rules."""
    if profile_name in _PROFILE_REGISTRY:
        raise ValueError(f"Profile {profile_name!r} is already registered.")

    missing = [rule for rule in rules if rule not in _REGISTRY]
    if missing:
        raise KeyError(f"Unknown lint rules requested: {', '.join(missing)}")

    _PROFILE_REGISTRY[profile_name] = tuple(rules)


def iter_registered_profiles() -> Iterator[tuple[str, tuple[str, ...]]]:
    """Yield the registered lint profiles and their member rules."""
    yield from _PROFILE_REGISTRY.items()


def run_lint(
    document: LintTarget, rules: Sequence[str] | None = None
) -> list[LintFinding]:
    """Execute lint rules against ``document`` and return all findings."""
    selected: Iterable[_LintRule]
    if rules is None:
        selected = _REGISTRY.values()
    else:
        missing = [rule for rule in rules if rule not in _REGISTRY]
        if missing:
            raise KeyError(f"Unknown lint rules requested: {', '.join(missing)}")
        selected = (_REGISTRY[rule_id] for rule_id in rules)

    findings: list[LintFinding] = []
    for rule in selected:
        findings.extend(list(rule.run(document)))
    return findings


@dataclass(frozen=True)
class ProfileResult:
    """Container describing the combined result of running a lint profile."""

    schema_issues: list[schema_loader.SchemaValidationIssue]
    lint_findings: list[LintFinding]

    def as_dict(self) -> dict[str, list[dict[str, object]]]:
        """Return a JSON-serialisable representation of the results."""
        schema_payload: list[dict[str, object]] = [
            cast(dict[str, object], issue.to_dict()) for issue in self.schema_issues
        ]
        lint_payload: list[dict[str, object]] = [
            cast(dict[str, object], finding.as_dict()) for finding in self.lint_findings
        ]
        return {"schema_issues": schema_payload, "lint_findings": lint_payload}


def run_profile(
    document: LintTarget,
    profile_name: str,
    *,
    include_schema: bool = True,
) -> ProfileResult:
    """Validate and lint ``document`` using a named profile."""
    if profile_name not in _PROFILE_REGISTRY:
        raise KeyError(f"Unknown lint profile requested: {profile_name}")

    rules = _PROFILE_REGISTRY[profile_name]

    schema_issues: list[schema_loader.SchemaValidationIssue] = []
    if include_schema:
        schema_issues = schema_loader.validate(document.to_etree(), raise_error=False)

    lint_findings = run_lint(document, rules=rules)

    return ProfileResult(schema_issues=schema_issues, lint_findings=lint_findings)


def _allowed_agencies() -> Iterable[str] | None:
    configuration = get_lint_configuration()
    if configuration.allowed_agencies is not None:
        return configuration.allowed_agencies
    if not ALLOWED_AGENCIES:
        return None
    return tuple(ALLOWED_AGENCIES)


def _namespaces(root: Element) -> NamespaceSet:
    """Return the namespace set for the DDI version ``root`` declares."""
    from .schema_loader._versions import detect_version_from_element

    return get_namespace_set(detect_version_from_element(root))


def _is_fragment_instance(document: LintTarget) -> bool:
    """Return whether the document root is a ``FragmentInstance``.

    A ``FragmentInstance`` is DDI's container for a *partial* set of
    maintainables addressed by URN. It carries a ``TopLevelReference`` instead
    of the instance-level ``Agency`` and ``Citation``, and its references
    legitimately point at items held in other fragments. Rules that assume a
    self-contained ``DDIInstance`` do not apply to one.
    """
    instance_ns = _namespaces(document.root)["INSTANCE_NS"]
    return document.root.tag == qn(instance_ns, "FragmentInstance")


def _check_allowed_agency(document: LintTarget) -> Iterable[LintFinding]:
    """Validate that the document agency identifier is present and allowed.

    Args:
        document: The parsed DDI document whose agency metadata will be
            inspected.

    Yields:
        LintFinding: Findings describing missing or disallowed agencies. Each
        finding includes the location derived from :func:`_element_path` when an
        agency element is present.
    """
    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    agency_element = document.root.find(qn(reusable_ns, "Agency"))
    location = _element_path(agency_element) if agency_element is not None else None
    agency = agency_element.text if agency_element is not None else None
    allowed = _allowed_agencies()
    if agency is None:
        # A FragmentInstance identifies itself through TopLevelReference, not
        # an instance-level Agency, so its absence is not a defect there.
        if _is_fragment_instance(document):
            return
        yield LintFinding(
            rule_id="ddi.agency.allowed",
            message="DDIInstance is missing an agency identifier.",
            severity="error",
            location=location,
        )
    elif allowed and agency not in allowed:
        yield LintFinding(
            rule_id="ddi.agency.allowed",
            message=f"Agency '{agency}' is not an allowed value.",
            severity="error",
            location=location,
        )


def _check_citation_present(document: LintTarget) -> Iterable[LintFinding]:
    """Ensure the root document contains a citation element when required."""
    configuration = get_lint_configuration()
    if not configuration.require_citation:
        return []

    # A FragmentInstance is a transport container for maintainables; the
    # citation belongs to the instance that assembles them.
    if _is_fragment_instance(document):
        return []

    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    citation = document.root.find(qn(reusable_ns, "Citation"))
    if citation is None:
        return [
            LintFinding(
                rule_id="ddi.citation.present",
                message="DDIInstance is missing a <Citation> element.",
                severity="error",
                location=_element_path(document.root),
            )
        ]
    return []


def _check_citation_title_present(document: LintTarget) -> Iterable[LintFinding]:
    """Validate that a citation includes a human-readable title when required."""
    configuration = get_lint_configuration()
    if not configuration.require_citation_title:
        return []

    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    citation = document.root.find(qn(reusable_ns, "Citation"))
    if citation is None:
        return []

    title_tag = qn(reusable_ns, "Title")
    if citation.find(title_tag) is None:
        return [
            LintFinding(
                rule_id="ddi.citation.title.present",
                message="Citation is missing a <Title> element.",
                severity="error",
                location=_element_path(citation),
            )
        ]
    return []


def _collect_title_languages(citation: Element) -> tuple[str, ...]:
    title_languages: dict[str, None] = {}
    reusable_ns = citation.tag[1:].split("}", 1)[0]
    title_tag = qn(reusable_ns, "Title")
    for title in citation.findall(title_tag):
        values = InternationalString.from_container(title)
        if values:
            for value in values:
                if value.lang:
                    title_languages.setdefault(value.lang, None)
            continue
        language = title.get(qn(XML_NS, "lang"))
        if language:
            title_languages.setdefault(language, None)
    return tuple(title_languages)


def _language_range_matches(required: str, available: str) -> bool:
    """Return whether ``available`` satisfies the language range ``required``.

    RFC 4647 basic filtering: a range matches a tag that equals it or extends it
    at a subtag boundary, compared case-insensitively. A required ``en`` is
    satisfied by ``en``, ``en-CA`` and ``en-Latn-CA``, but not by ``eng``.
    """
    required = required.casefold()
    available = available.casefold()
    if required == available:
        return True
    return available.startswith(f"{required}-")


def _check_citation_title_languages(document: LintTarget) -> Iterable[LintFinding]:
    """Ensure citation titles cover the configured set of languages."""
    configuration = get_lint_configuration()
    required_languages = configuration.required_citation_languages
    if not required_languages:
        return []

    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    citation = document.root.find(qn(reusable_ns, "Citation"))
    if citation is None:
        return []

    if citation.find(qn(reusable_ns, "Title")) is None:
        return []

    available_languages = _collect_title_languages(citation)
    missing = [
        lang
        for lang in required_languages
        if not any(
            _language_range_matches(lang, available)
            for available in available_languages
        )
    ]
    if not missing:
        return []

    return [
        LintFinding(
            rule_id="ddi.citation.title.languages",
            message=f"Citation title is missing required language '{language}'.",
            severity="warning",
            location=_element_path(citation),
        )
        for language in missing
    ]


def _check_maintainable_labels(document: LintTarget) -> Iterable[LintFinding]:
    """Ensure maintainable elements include human-readable labels.

    Args:
        document: The parsed DDI document to inspect for maintainable
            structures.

    Yields:
        LintFinding: Warnings for maintainable elements missing a ``Label``
        child. Each finding includes the element location derived from
        :func:`_element_path`.
    """
    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    maintainable_tags = {
        qn(reusable_ns, "Agency"),
        qn(reusable_ns, "ID"),
        qn(reusable_ns, "Version"),
    }
    label_tag = qn(reusable_ns, "Label")
    for element in document.root.iter():
        if element is document.root:
            continue
        tag = element.tag
        if not isinstance(tag, str):
            continue
        # Only elements whose schema type has an ``r:Label`` slot can carry a
        # label; ``l:Code``, for example, is identifiable but has none.
        if tag not in TAGS_ALLOWING_LABEL:
            continue
        maintainable_cls = MaintainableBase.for_tag(tag)
        if maintainable_cls is not None:
            # A separate question from the schema's: ``ALLOW_LABELS`` says
            # whether this model round-trips a Label it parses.
            if not maintainable_cls.ALLOW_LABELS:
                continue
        elif not maintainable_tags.issubset({child.tag for child in element}):
            continue
        if element.find(label_tag) is None:
            yield LintFinding(
                rule_id="ddi.maintainable.labels",
                message="Maintainable element is missing a label.",
                severity="warning",
                location=_element_path(element),
            )


def _collect_identifiable_items(root: Element) -> set[tuple[str, str, str]]:
    """Build a set of (agency, identifier, version) tuples.

    Walks the raw XML rather than relying on the :class:`Index`, ensuring
    that items inside elements not yet natively supported by the library (e.g.
    ``CategoryScheme``) are still discoverable for reference checking.
    """
    reusable_ns = _namespaces(root)["REUSABLE_NS"]
    agency_tag = qn(reusable_ns, "Agency")
    id_tag = qn(reusable_ns, "ID")
    version_tag = qn(reusable_ns, "Version")

    items: set[tuple[str, str, str]] = set()
    for element in root.iter():
        # Skip Reference elements — they contain r:Agency/ID/Version to
        # describe what they point at, not to declare a new item.
        tag = element.tag
        if isinstance(tag, str) and tag.endswith("Reference"):
            continue
        agency_el = element.find(agency_tag)
        id_el = element.find(id_tag)
        version_el = element.find(version_tag)
        if agency_el is not None and id_el is not None and version_el is not None:
            agency = agency_el.text or ""
            identifier = id_el.text or ""
            version = version_el.text or ""
            if agency and identifier and version:
                items.add((agency, identifier, version))
    return items


def _check_reference_integrity(document: LintTarget) -> Iterable[LintFinding]:
    """Validate that all Reference elements resolve to items present in the document.

    Iterates every element whose tag ends with ``Reference`` and whose payload
    includes a ``TypeOfObject`` child (the DDI convention for typed references).
    Each reference is checked against the set of identifiable items found by
    walking the raw XML tree, ensuring coverage of elements not yet natively
    modelled by the library (e.g. Category inside CategoryScheme).
    """
    from .models.base import Reference

    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    known_items = _collect_identifiable_items(document.root)
    type_of_object_tag = qn(reusable_ns, "TypeOfObject")

    # A fragment holds a partial set of maintainables and is expected to
    # reference items living in sibling fragments, so an unresolved reference
    # is informational there rather than a defect. In a self-contained
    # DDIInstance it is a real integrity error.
    fragment = _is_fragment_instance(document)
    severity = "warning" if fragment else "error"
    scope = "this fragment" if fragment else "the document"

    for element in document.root.iter():
        tag = element.tag
        if not isinstance(tag, str) or not tag.endswith("Reference"):
            continue
        # Only process DDI typed references (those with r:TypeOfObject)
        type_el = element.find(type_of_object_tag)
        if type_el is None:
            continue

        ref = Reference.from_xml(element)
        if not ref.identifier and not ref.urn:
            continue

        # Check if the referenced item exists in the document
        if (
            ref.agency
            and ref.identifier
            and ref.version
            and (ref.agency, ref.identifier, ref.version) in known_items
        ):
            continue

        ref_label = ref.identifier or ref.urn or "(unknown)"
        ref_type = ref.type_of_object or "unknown"
        yield LintFinding(
            rule_id="ddi.reference.integrity",
            message=(
                f"Reference to {ref_type} '{ref_label}' cannot be resolved "
                f"to an item in {scope}."
            ),
            severity=severity,
            location=_element_path(element),
        )


register_rule("ddi.agency.allowed", _check_allowed_agency)
register_rule("ddi.citation.present", _check_citation_present)
register_rule("ddi.citation.title.present", _check_citation_title_present)
register_rule("ddi.citation.title.languages", _check_citation_title_languages)
register_rule("ddi.maintainable.labels", _check_maintainable_labels)
register_rule("ddi.reference.integrity", _check_reference_integrity)
register_profile(DDI_PROFILE_DEFAULT, tuple(_REGISTRY))


__all__ = [
    "ALLOWED_AGENCIES",
    "DDI_PROFILE_DEFAULT",
    "LintConfiguration",
    "LintFinding",
    "ProfileResult",
    "configure_lint",
    "get_lint_configuration",
    "register_profile",
    "register_rule",
    "reset_lint_configuration",
    "run_lint",
    "run_profile",
    "set_lint_configuration",
]
