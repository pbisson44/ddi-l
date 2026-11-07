"""Lightweight linting helpers for DDI instance documents."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Iterator, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, fields, replace
from typing import (
    TYPE_CHECKING,
    Any,
    TypeAlias,
    cast,
)

from . import _incremental, schema_loader
from ._etree import USING_LXML, Element
from ._facts import run_scope, shared
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
            `lxml.etree.ElementTree.getpath`, providing an absolute XPath.
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

# The severities a finding can carry, least severe first. ``info`` reports
# something worth knowing that is not a defect; it never fails ``ddi lint``
# unless ``--fail-severity info`` asks it to.
SEVERITIES: tuple[str, ...] = ("info", "warning", "error")


def _check_severity(severity: str) -> None:
    if severity not in SEVERITIES:
        raise ValueError(
            f"Unknown lint severity {severity!r}; expected one of "
            f"{', '.join(SEVERITIES)}."
        )


@dataclass(frozen=True)
class LintFinding:
    """Container describing a single lint finding.

    Raises:
        ValueError: If ``severity`` is not one of `SEVERITIES`.
    """

    rule_id: str
    message: str
    severity: str = "error"
    location: str | None = None

    def __post_init__(self) -> None:
        _check_severity(self.severity)

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


# Text left over from a template: a placeholder still waiting for its
# content. Neutral defaults; replace them with your own conventions.
DEFAULT_PLACEHOLDER_PATTERNS: tuple[str, ...] = (
    # Doubled single guillemets (U+2039, U+203A), written as escapes.
    "\u2039\u2039[^\u203a]*\u203a\u203a",
    r"<<[^<>]*>>",
    r"«\s*(?i:insert)[^»]*»",
    r"\[\s*(?i:insert)\b[^\]]*\]",
    r"(?i)\binsert (?:survey|study)-specific\b",
)
# Names or texts of a statement that is a design note rather than content.
DEFAULT_LOGIC_NOTE_PATTERNS: tuple[str, ...] = (
    r"(?i)^\s*(?:flow|display|skip|routing) (?:condition|logic|instruction)s?\b",
    r"(?i)^\s*logic\s*:",
    r"(?i)^\s*condition (?:d'affichage|de cheminement|de filtrage)\b",
    r"(?i)^\s*logique\s*:",
)
# A condition's description saying it routes to another page.
DEFAULT_GATE_DESCRIPTION_PATTERNS: tuple[str, ...] = (
    r"(?i)\bgo to\b.{0,80}\bpage\b",
    r"(?i)\b(?:aller|passer) à la page\b",
)

_PATTERN_FIELDS = (
    "placeholder_patterns",
    "logic_note_patterns",
    "gate_description_patterns",
)
_SEQUENCE_FIELDS = (
    "required_citation_languages",
    "required_languages",
    *_PATTERN_FIELDS,
    "ui_chrome_tokens",
    "known_names",
    "pipe_prefixes",
    "pipe_suffixes",
)


@dataclass(frozen=True)
class LintConfiguration:
    """Collection of options governing built-in lint behaviour.

    The options after ``required_citation_languages`` drive the
    ``colectica-questionnaire`` rules. Anything specific to one organisation
    (its languages, the names its systems supply at run time, its variable
    naming scheme, the user-interface words its mock-ups contain) has an
    empty default, so the rule using it does nothing until configured.

    Attributes:
        allowed_agencies: Agency identifiers ``ddi.agency.allowed`` accepts.
        require_citation: Whether ``ddi.citation.present`` runs.
        require_citation_title: Whether ``ddi.citation.title.present`` runs.
        required_citation_languages: Languages a citation title must have.
        required_languages: Languages question texts, statements, category
            and domain labels must have (``i18n.missing-language``).
        placeholder_patterns: Regular expressions for unresolved template
            placeholders (``text.placeholder-unresolved``).
        ui_chrome_tokens: User-interface words pasted from mock-ups into
            content, matched as whole tokens (``text.ui-chrome``).
        logic_note_patterns: Regular expressions for statements that are
            design notes (``colectica.statement.logic-note``).
        gate_description_patterns: Regular expressions for a condition
            description that routes to another page
            (``colectica.ifthenelse.partial-gate``).
        known_names: Names text may pipe (``#{name}``) that the run-time
            system supplies, beyond the file's lookup fields and parameter
            aliases (``text.pipe-undeclared``).
        variable_code_pattern: A regular expression for variable codes,
            enabling ``colectica.domain.label-mismatch``.
        pipe_prefixes: Prefixes a piped name must not stop at
            (``#{DT}`` for the prefix ``DT_``; ``text.pipe-malformed``).
        pipe_suffixes: Suffixes stripped from a piped name before it is
            looked up (a per-language ``_E``, say; ``text.pipe-undeclared``).

    Raises:
        ValueError: If a pattern is not a valid regular expression.
    """

    allowed_agencies: tuple[str, ...] | None = None
    require_citation: bool = True
    require_citation_title: bool = True
    required_citation_languages: tuple[str, ...] = ()
    required_languages: tuple[str, ...] = ()
    placeholder_patterns: tuple[str, ...] = DEFAULT_PLACEHOLDER_PATTERNS
    ui_chrome_tokens: tuple[str, ...] = ()
    logic_note_patterns: tuple[str, ...] = DEFAULT_LOGIC_NOTE_PATTERNS
    gate_description_patterns: tuple[str, ...] = DEFAULT_GATE_DESCRIPTION_PATTERNS
    known_names: tuple[str, ...] = ()
    variable_code_pattern: str | None = None
    pipe_prefixes: tuple[str, ...] = ()
    pipe_suffixes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.allowed_agencies is not None:
            object.__setattr__(
                self, "allowed_agencies", _normalize_sequence(self.allowed_agencies)
            )
        for name in _SEQUENCE_FIELDS:
            value = getattr(self, name)
            if isinstance(value, str):
                raise TypeError(f"{name} takes a sequence of strings, not a string.")
            object.__setattr__(self, name, _normalize_sequence(tuple(value)))
        patterns = [
            pattern for name in _PATTERN_FIELDS for pattern in getattr(self, name)
        ]
        if self.variable_code_pattern:
            patterns.append(self.variable_code_pattern)
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as error:
                raise ValueError(
                    f"Invalid lint pattern {pattern!r}: {error}"
                ) from error


@dataclass
class _LintRule:
    rule_id: str
    callback: DocumentRule | ElementRule
    target: str
    default: bool = True
    severity: str | None = None
    example: str | None = None
    # ddi-l's own rules whose findings about an item depend on that item
    # alone (and the configuration): `ddi_l._incremental` keeps them per item.
    per_item: bool = False

    def run(self, document: LintTarget) -> Iterator[LintFinding]:
        target = document if self.target == "document" else document.root
        for finding in self.callback(target):  # type: ignore[arg-type]
            # A callback may yield any object shaped like a finding; check it
            # here too so an unknown severity never reaches a caller.
            _check_severity(finding.severity)
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

_DEFAULT_CONFIGURATION = LintConfiguration(
    allowed_agencies=None,
    require_citation=True,
    require_citation_title=True,
    required_citation_languages=("en",),
)
_CONFIG = _DEFAULT_CONFIGURATION

# The configuration passed to the `run_lint` or `run_profile` call under way,
# for the rules it runs; each thread and task sees only its own.
_CALL_CONFIG: ContextVar[LintConfiguration | None] = ContextVar(
    "ddi_l_lint_configuration", default=None
)


def get_lint_configuration() -> LintConfiguration:
    """Return the active `LintConfiguration`.

    That is the configuration passed to the `run_lint` or `run_profile` call
    under way, else the process default `configure_lint` sets.
    """
    return _CALL_CONFIG.get() or _CONFIG


@contextmanager
def _configured(configuration: LintConfiguration | None) -> Iterator[None]:
    """Make ``configuration`` the one rules read, for the ``with`` block."""
    if configuration is None:
        yield
        return
    token = _CALL_CONFIG.set(configuration)
    try:
        yield
    finally:
        _CALL_CONFIG.reset(token)


def __getattr__(name: str) -> object:
    # ALLOWED_AGENCIES: the allowed-agency check is opt-in, since only a
    # deployment knows which agency identifiers are acceptable. It reads the
    # application default, set with `configure_lint(allowed_agencies=[...])`
    # or `--allowed-agency`; while it is empty the rule still reports a
    # *missing* agency.
    if name == "ALLOWED_AGENCIES":
        return frozenset(_CONFIG.allowed_agencies or ())
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def set_lint_configuration(configuration: LintConfiguration) -> LintConfiguration:
    """Replace the application default lint configuration."""
    global _CONFIG
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
    **options: Any,
) -> LintConfiguration:
    """Update and return the process default `LintConfiguration`.

    Only options explicitly provided are modified.  ``allowed_agencies`` accepts
    ``None`` to disable the built-in agency allow-list and any other sequence to
    replace it.  ``required_citation_languages`` expects an iterable of BCP 47
    language identifiers that must be present on citation titles. Any other
    `LintConfiguration` field can be passed by name, for example
    ``configure_lint(required_languages=["en", "fr"])``.

    The default applies to every call that is not given a configuration of
    its own. To configure one call, pass `lint_configuration` to it instead.

    Raises:
        TypeError: If an option is not a `LintConfiguration` field.
    """
    updates = _updates(
        allowed_agencies=allowed_agencies,
        require_citation=require_citation,
        require_citation_title=require_citation_title,
        required_citation_languages=required_citation_languages,
        **options,
    )
    if not updates:
        return _CONFIG

    configuration = replace(_CONFIG, **updates)
    return set_lint_configuration(configuration)


def lint_configuration(**options: Any) -> LintConfiguration:
    """Return the default `LintConfiguration` with ``options`` applied.

    It takes the options `configure_lint` takes and changes nothing global:
    pass the result to `run_lint`, `run_profile` or a document's ``lint``,
    for that call alone. The default it starts from requires English
    citation titles, as the process default does.

    Raises:
        TypeError: If an option is not a `LintConfiguration` field.
        ValueError: If a pattern is not a valid regular expression.
    """
    return replace(_DEFAULT_CONFIGURATION, **_updates(**options))


def _updates(
    *,
    allowed_agencies: Sequence[str] | object | None = _UNSET,
    require_citation: bool | object | None = _UNSET,
    require_citation_title: bool | object | None = _UNSET,
    required_citation_languages: Sequence[str] | object | None = _UNSET,
    **options: Any,
) -> dict[str, Any]:
    """The `LintConfiguration` fields the options of `configure_lint` set."""
    known = {field.name for field in fields(LintConfiguration)}
    unknown = sorted(set(options) - known)
    if unknown:
        raise TypeError(f"Unknown lint option(s): {', '.join(unknown)}.")
    updates: dict[str, Any] = dict(options)
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
    return updates


def register_rule(
    rule_id: str,
    callback: DocumentRule | ElementRule,
    *,
    target: str = "document",
    default: bool = True,
    severity: str | None = None,
    example: str | None = None,
) -> None:
    """Register a linting rule.

    ``target`` determines whether ``callback`` receives the whole
    `DDIDocument` or the root `Element` of the document.

    ``default`` adds the rule to `DDI_PROFILE_DEFAULT`, which is what
    `run_lint` and ``ddi lint`` run when no rules or profile are named.
    Pass ``False`` for a rule meant only for a named profile.

    ``severity`` (the severity the rule reports, or ``"error/info"`` when it
    varies) and ``example`` (a sample finding message) only document the rule;
    see `iter_rule_metadata`.
    """
    if rule_id in _REGISTRY:
        raise ValueError(f"Rule {rule_id!r} is already registered.")
    if target not in {"document", "element"}:
        raise ValueError("target must be 'document' or 'element'.")
    _REGISTRY[rule_id] = _LintRule(
        rule_id=rule_id,
        callback=callback,
        target=target,
        default=default,
        severity=severity,
        example=example,
    )
    if default and DDI_PROFILE_DEFAULT in _PROFILE_REGISTRY:
        _PROFILE_REGISTRY[DDI_PROFILE_DEFAULT] += (rule_id,)


def iter_registered_rules() -> Iterator[tuple[str, str | None]]:
    """Yield the registered lint rules and any available descriptions."""
    for rule_id, rule in _REGISTRY.items():
        description = None
        if rule.callback.__doc__:
            description = rule.callback.__doc__.strip().splitlines()[0]
        yield rule_id, description


@dataclass(frozen=True)
class RuleInfo:
    """What `iter_rule_metadata` reports about one registered rule.

    Attributes:
        rule_id: The rule's identifier.
        summary: The first line of the rule's docstring.
        description: The rule's whole docstring, dedented.
        severity: The severity it reports, as registered.
        example: A sample finding message, as registered.
        default: Whether it runs in `DDI_PROFILE_DEFAULT`.
        profiles: The named profiles that include it.
    """

    rule_id: str
    summary: str | None
    description: str | None
    severity: str | None
    example: str | None
    default: bool
    profiles: tuple[str, ...]


def iter_rule_metadata() -> Iterator[RuleInfo]:
    """Yield what is known about each registered rule, in registration order."""
    import inspect

    for rule_id, rule in _REGISTRY.items():
        doc = inspect.getdoc(rule.callback)
        yield RuleInfo(
            rule_id=rule_id,
            summary=doc.splitlines()[0] if doc else None,
            description=doc,
            severity=rule.severity,
            example=rule.example,
            default=rule_id in _PROFILE_REGISTRY.get(DDI_PROFILE_DEFAULT, ()),
            profiles=tuple(
                name
                for name, members in _PROFILE_REGISTRY.items()
                if rule_id in members and name != DDI_PROFILE_DEFAULT
            ),
        )


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
    document: LintTarget,
    rules: Sequence[str] | None = None,
    *,
    configuration: LintConfiguration | None = None,
) -> list[LintFinding]:
    """Execute lint rules against ``document`` and return all findings.

    Args:
        document: The instance or fragment to lint.
        rules: Rule identifiers to run. By default, the rules of
            `DDI_PROFILE_DEFAULT`: every rule registered with
            ``default=True``, but not those meant only for a named profile
            such as ``colectica-questionnaire``.
        configuration: The configuration the rules read during this call,
            from `lint_configuration`; ``None`` keeps the process default.
    """
    selected: Iterable[_LintRule]
    if rules is None:
        selected = (
            _REGISTRY[rule_id] for rule_id in _PROFILE_REGISTRY[DDI_PROFILE_DEFAULT]
        )
    else:
        missing = [rule for rule in rules if rule not in _REGISTRY]
        if missing:
            raise KeyError(f"Unknown lint rules requested: {', '.join(missing)}")
        selected = (_REGISTRY[rule_id] for rule_id in rules)

    findings: list[LintFinding] = []
    # The rules share what they build from the document (`ddi_l._facts`).
    with _configured(configuration), run_scope():
        for rule in selected:
            if rule.per_item:
                findings.extend(_incremental.findings(document, rule))
            else:
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
    configuration: LintConfiguration | None = None,
    version: str | None = None,
) -> ProfileResult:
    """Validate and lint ``document`` using a named profile.

    Args:
        document: The instance or fragment to lint.
        profile_name: The registered profile whose rules run.
        include_schema: Whether to validate against the schema first.
        configuration: As for `run_lint`.
        version: DDI schema version to validate against; ``None`` uses the
            version the document declares.
    """
    if profile_name not in _PROFILE_REGISTRY:
        raise KeyError(f"Unknown lint profile requested: {profile_name}")

    rules = _PROFILE_REGISTRY[profile_name]

    schema_issues: list[schema_loader.SchemaValidationIssue] = []
    if include_schema:
        schema_issues = schema_loader.validate(
            document.to_etree(), raise_error=False, version=version
        )

    lint_findings = run_lint(document, rules=rules, configuration=configuration)

    return ProfileResult(schema_issues=schema_issues, lint_findings=lint_findings)


def _allowed_agencies() -> Iterable[str] | None:
    return get_lint_configuration().allowed_agencies


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
        finding includes the location derived from `_element_path` when an
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


def _iter_label_candidates(document: LintTarget) -> Iterator[Element]:
    """Yield the elements that should carry a human-readable label.

    These are the maintainables and identifiables whose schema type has an
    ``r:Label`` slot, skipping models that opt out of round-tripping labels.
    """
    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    for chunk in document.root:
        yield from _label_candidates(chunk, reusable_ns)


def _label_candidates(top: Element, reusable_ns: str) -> Iterator[Element]:
    """`_iter_label_candidates` in ``top``, ``top`` included."""
    maintainable_tags = {
        qn(reusable_ns, "Agency"),
        qn(reusable_ns, "ID"),
        qn(reusable_ns, "Version"),
    }
    for element in top.iter():
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
        yield element


def _check_maintainable_labels(document: LintTarget) -> Iterable[LintFinding]:
    """Ensure maintainable elements include human-readable labels.

    Args:
        document: The parsed DDI document to inspect for maintainable
            structures.

    Yields:
        LintFinding: Warnings for maintainable elements missing a ``Label``
        child. Each finding includes the element location derived from
        `_element_path`.
    """
    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    for found in _incremental.per_chunk(
        document,
        "ddi.maintainable.labels",
        lambda chunk: list(_unlabelled_items(chunk, reusable_ns)),
    ):
        yield from found


def _unlabelled_items(top: Element, reusable_ns: str) -> Iterator[LintFinding]:
    """The ``ddi.maintainable.labels`` findings in ``top``."""
    label_tag = qn(reusable_ns, "Label")
    for element in _label_candidates(top, reusable_ns):
        if element.find(label_tag) is None:
            yield LintFinding(
                rule_id="ddi.maintainable.labels",
                message="Maintainable element is missing a label.",
                severity="warning",
                location=_element_path(element),
            )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _has_text(element: Element) -> bool:
    return any(
        (node.text or "").strip()
        for node in element.iter()
        if isinstance(node.tag, str)
    )


def _check_colectica_labels(document: LintTarget) -> Iterable[LintFinding]:
    """Ensure items carry a label or a name, as Colectica content does.

    Colectica items routinely carry a ``ConstructName``, ``QuestionItemName``
    or ``r:Name`` instead of an ``r:Label``. Any of them satisfies the rule,
    provided it holds text. Used by the ``colectica-questionnaire`` profile
    in place of ``ddi.maintainable.labels``.
    """
    reusable_ns = _namespaces(document.root)["REUSABLE_NS"]
    # Each child of the root is read once while it is unchanged.
    for found in _incremental.per_chunk(
        document,
        "colectica.maintainable.labels",
        lambda chunk: list(_unnamed_items(chunk, reusable_ns)),
    ):
        yield from found


def _unnamed_items(top: Element, reusable_ns: str) -> Iterator[LintFinding]:
    """The ``colectica.maintainable.labels`` findings in ``top``."""
    label_tag = qn(reusable_ns, "Label")
    id_tag = qn(reusable_ns, "ID")
    for element in _label_candidates(top, reusable_ns):
        named = any(
            isinstance(child.tag, str)
            and (child.tag == label_tag or _local_name(child.tag).endswith("Name"))
            and _has_text(child)
            for child in element
        )
        if not named:
            short_id = (element.findtext(id_tag) or "")[:8]
            yield LintFinding(
                rule_id="colectica.maintainable.labels",
                message=(
                    f"{_local_name(element.tag)} {short_id} has no label or "
                    "name with text."
                ),
                severity="warning",
                location=_element_path(element),
            )


@dataclass(frozen=True)
class _IdentifiableIndex:
    """The identifiable items of a document, by exact triple and by ID."""

    exact: frozenset[tuple[str, str, str]]
    versions: dict[tuple[str, str], frozenset[str]]


def _identification(element: Element, reusable_ns: str) -> set[tuple[str, str, str]]:
    """``element``'s own (agency, identifier, version), if it has all three."""
    if isinstance(element.tag, str) and element.tag.endswith("Reference"):
        return set()
    found: dict[str, str] = {}
    for child in element:
        found.setdefault(child.tag, child.text or "")
    names = ("Agency", "ID", "Version")
    triple = tuple(found.get(qn(reusable_ns, name)) for name in names)
    return {triple} if all(triple) else set()  # type: ignore[arg-type]


def _collect_identifiable_items(
    root: Element, reusable_ns: str | None = None
) -> set[tuple[str, str, str]]:
    """Build a set of (agency, identifier, version) tuples.

    Walks the raw XML rather than relying on the `Index`, ensuring
    that items inside elements not yet natively supported by the library (e.g.
    ``CategoryScheme``) are still discoverable for reference checking.
    """
    reusable_ns = reusable_ns or _namespaces(root)["REUSABLE_NS"]
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
        # The first of each child, read in one pass over the children.
        found: dict[str, str] = {}
        for child in element:
            if child.tag in (agency_tag, id_tag, version_tag):
                found.setdefault(child.tag, child.text or "")
        agency = found.get(agency_tag)
        identifier = found.get(id_tag)
        version = found.get(version_tag)
        if agency and identifier and version:
            items.add((agency, identifier, version))
    return items


def _index_identifiable_items(document: LintTarget) -> _IdentifiableIndex:
    """The identifiable items of ``document``, built once per run."""
    return shared("identifiables", document.root, lambda: _identifiable_index(document))


def _identifiable_index(document: LintTarget) -> _IdentifiableIndex:
    # Each child of the root is read once while it is unchanged
    # (`_incremental.per_chunk`); the root's own identification each time.
    root = document.root
    reusable_ns = _namespaces(root)["REUSABLE_NS"]
    exact = _identification(root, reusable_ns)
    for triples in _incremental.per_chunk(
        document,
        "identifiables",
        lambda chunk: _collect_identifiable_items(chunk, reusable_ns),
    ):
        exact |= triples
    versions: dict[tuple[str, str], set[str]] = {}
    for agency, identifier, version in exact:
        versions.setdefault((agency, identifier), set()).add(version)
    return _IdentifiableIndex(
        exact=frozenset(exact),
        versions={key: frozenset(value) for key, value in versions.items()},
    )


# References that record where an item came from rather than what it uses.
# Their target routinely lives outside the file (the source a copy was made
# from), so an unresolved one is information, not a broken link.
_PROVENANCE_CONTAINERS = ("BasedOnObject", "UserAttributePair")


def _iter_typed_references(
    root: Element, reusable_ns: str | None = None
) -> Iterator[tuple[Element, bool]]:
    """Yield each typed reference and whether it records provenance.

    A typed reference is an element whose tag ends with ``Reference`` and
    which has an ``r:TypeOfObject`` child, the DDI convention.
    """
    reusable_ns = reusable_ns or _namespaces(root)["REUSABLE_NS"]
    type_of_object_tag = qn(reusable_ns, "TypeOfObject")
    provenance_tags = {qn(reusable_ns, name) for name in _PROVENANCE_CONTAINERS}

    stack: list[tuple[Element, bool]] = [(root, False)]
    while stack:
        element, provenance = stack.pop()
        tag = element.tag
        if not isinstance(tag, str):
            continue
        provenance = provenance or tag in provenance_tags
        if tag.endswith("Reference") and element.find(type_of_object_tag) is not None:
            yield element, provenance
        stack.extend((child, provenance) for child in reversed(list(element)))


# How a reference resolves against the document, worked out once per
# reference so the three reference rules agree.
_RESOLVED = "resolved"
_VERSION_MISSING = "version-missing"
_VERSION_AHEAD = "version-ahead"
_VERSION_RESTRICTED = "version-restricted"
_UNRESOLVED = "unresolved"


def _resolve_reference(
    element: Element, index: _IdentifiableIndex
) -> tuple[str, Any, frozenset[str]]:
    """Classify a typed reference against ``index``.

    Returns:
        The status, the parsed `Reference`, and the
        versions of its ``(agency, id)`` present in the document.
    """
    from .models.base import Reference

    late = element.get("lateBound") in ("true", "1")
    restriction = (element.get("lateBoundRestriction") or "").strip()
    return _classify(Reference.from_xml(element), late, restriction, index)


def _classify(
    ref: Any, late: bool, restriction: str, index: _IdentifiableIndex
) -> tuple[str, Any, frozenset[str]]:
    """`_resolve_reference` for a reference already read."""
    from .colectica_logic import _version_rank

    available: frozenset[str] = frozenset()
    if ref.agency and ref.identifier:
        available = index.versions.get((ref.agency, ref.identifier), frozenset())
    # xs:boolean: "1" means true as well as "true".
    if late:
        # A late-bound reference means "the latest version", so any version
        # present resolves it. Colectica writes late-bound parameter
        # references at version 1 while the parameter itself is at, say, 4.
        if not available:
            return _UNRESOLVED, ref, available
        # lateBoundRestriction="4" asks for the latest version within major
        # version 4: only versions whose leading components match qualify.
        candidates = available
        if restriction:
            prefix = restriction.split(".")
            candidates = frozenset(
                version
                for version in available
                if version.split(".")[: len(prefix)] == prefix
            )
            if not candidates:
                return _VERSION_RESTRICTED, ref, available
        if ref.version and _version_rank(ref.version) > max(
            _version_rank(version) for version in candidates
        ):
            return _VERSION_AHEAD, ref, available
        return _RESOLVED, ref, available
    if (
        ref.agency
        and ref.identifier
        and ref.version
        and (ref.agency, ref.identifier, ref.version) in index.exact
    ):
        return _RESOLVED, ref, available
    if ref.version and available:
        return _VERSION_MISSING, ref, available
    return _UNRESOLVED, ref, available


def _iter_reference_resolutions(
    document: LintTarget,
) -> Iterator[tuple[Element, bool, str, Any, frozenset[str]]]:
    """How each typed reference resolves, worked out once per run."""
    root = document.root
    yield from shared("references", root, lambda: _reference_resolutions(document))


def _read_references(
    chunk: Element, reusable_ns: str
) -> list[tuple[Element, bool, Any, bool, str]]:
    """Each typed reference in ``chunk``, read.

    Each is the element, its provenance, the reference, whether it is
    late-bound, and its ``lateBoundRestriction``.
    """
    from .models.base import Reference

    found = []
    for element, provenance in _iter_typed_references(chunk, reusable_ns):
        ref = Reference.from_xml(element)
        if not ref.identifier and not ref.urn:
            continue
        late = element.get("lateBound") in ("true", "1")
        restriction = (element.get("lateBoundRestriction") or "").strip()
        found.append((element, provenance, ref, late, restriction))
    return found


def _reference_resolutions(
    document: LintTarget,
) -> list[tuple[Element, bool, str, Any, frozenset[str]]]:
    root = document.root
    reusable_ns = _namespaces(root)["REUSABLE_NS"]
    index = _index_identifiable_items(document)
    resolutions = []
    # The root itself is not a typed reference; each child is read once
    # while it is unchanged, and classified against this run's index.
    for read in _incremental.per_chunk(
        document, "references", lambda chunk: _read_references(chunk, reusable_ns)
    ):
        for element, provenance, ref, late, restriction in read:
            status, ref, available = _classify(ref, late, restriction, index)
            resolutions.append((element, provenance, status, ref, available))
    return resolutions


def _sorted_versions(versions: Iterable[str]) -> str:
    from .colectica_logic import _version_rank

    return ", ".join(sorted(versions, key=_version_rank))


def _check_reference_integrity(document: LintTarget) -> Iterable[LintFinding]:
    """Validate that all Reference elements resolve to items present in the document.

    Iterates every element whose tag ends with ``Reference`` and whose payload
    includes a ``TypeOfObject`` child (the DDI convention for typed references).
    Each reference is checked against the identifiable items found by walking
    the raw XML tree, ensuring coverage of elements not yet natively modelled
    by the library (e.g. Category inside CategoryScheme).

    A ``lateBound="true"`` reference resolves to any version of its item. A
    reference whose item is present at other versions only is reported by
    ``ddi.reference.version``, and one recording provenance (inside
    ``r:BasedOnObject`` or ``r:UserAttributePair``) by
    ``ddi.reference.provenance-external``.
    """
    # A fragment holds a partial set of maintainables and is expected to
    # reference items living in sibling fragments, so an unresolved reference
    # is informational there rather than a defect. In a self-contained
    # DDIInstance it is a real integrity error.
    fragment = _is_fragment_instance(document)
    severity = "warning" if fragment else "error"
    scope = "this fragment" if fragment else "the document"

    for element, provenance, status, ref, _ in _iter_reference_resolutions(document):
        if provenance or status != _UNRESOLVED:
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


def _check_reference_version(document: LintTarget) -> Iterable[LintFinding]:
    """Report references whose item is present, but not at the version named.

    An exact reference to a version the document does not hold; a late-bound
    one naming a version newer than any it holds; or a late-bound one whose
    ``lateBoundRestriction`` (latest within major version 4, say) matches no
    version it holds.
    """
    for element, provenance, status, ref, available in _iter_reference_resolutions(
        document
    ):
        if provenance or status not in (
            _VERSION_MISSING,
            _VERSION_AHEAD,
            _VERSION_RESTRICTED,
        ):
            continue
        ref_type = ref.type_of_object or "unknown"
        if status == _VERSION_RESTRICTED:
            restriction = element.get("lateBoundRestriction")
            detail = f"is late-bound within version {restriction}, which is not present"
        elif status == _VERSION_AHEAD:
            detail = f"is late-bound at version {ref.version}, newer than any present"
        else:
            detail = f"resolves to its ID, but version {ref.version} is not present"
        yield LintFinding(
            rule_id="ddi.reference.version",
            message=(
                f"Reference to {ref_type} '{ref.identifier}' {detail}; "
                f"available: {_sorted_versions(available)}."
            ),
            severity="warning",
            location=_element_path(element),
        )


def _check_reference_provenance(document: LintTarget) -> Iterable[LintFinding]:
    """Note provenance references whose item is not in the document.

    ``r:BasedOnReference`` and references inside ``r:UserAttributePair``
    record where an item came from; the source usually lives elsewhere.
    """
    for element, provenance, status, ref, available in _iter_reference_resolutions(
        document
    ):
        if not provenance or status == _RESOLVED:
            continue
        ref_label = ref.identifier or ref.urn or "(unknown)"
        ref_type = ref.type_of_object or "unknown"
        if available:
            detail = (
                f"names version {ref.version}, which is not in this file; "
                f"available: {_sorted_versions(available)}"
            )
        else:
            detail = "points outside this file"
        yield LintFinding(
            rule_id="ddi.reference.provenance-external",
            message=f"Provenance reference to {ref_type} '{ref_label}' {detail}.",
            severity="info",
            location=_element_path(element),
        )


COLECTICA_QUESTIONNAIRE_PROFILE = "colectica-questionnaire"

register_rule(
    "ddi.agency.allowed",
    _check_allowed_agency,
    severity="error",
    example="Agency 'example.com' is not an allowed value.",
)
register_rule(
    "ddi.citation.present",
    _check_citation_present,
    severity="error",
    example="DDIInstance is missing a <Citation> element.",
)
register_rule(
    "ddi.citation.title.present",
    _check_citation_title_present,
    severity="error",
    example="Citation is missing a <Title> element.",
)
register_rule(
    "ddi.citation.title.languages",
    _check_citation_title_languages,
    severity="warning",
    example="Citation title is missing required language 'fr'.",
)
register_rule(
    "ddi.maintainable.labels",
    _check_maintainable_labels,
    severity="warning",
    example="Maintainable element is missing a label.",
)
register_rule(
    "ddi.reference.integrity",
    _check_reference_integrity,
    severity="error (warning in a fragment)",
    example=(
        "Reference to OutParameter '99999999-9999-4999-8999-999999999999' "
        "cannot be resolved to an item in this fragment."
    ),
)
register_rule(
    "ddi.reference.version",
    _check_reference_version,
    severity="warning",
    example=(
        "Reference to QuestionItem '11111111-1111-4111-8111-000000000001' "
        "resolves to its ID, but version 3 is not present; available: 4."
    ),
)
register_rule(
    "ddi.reference.provenance-external",
    _check_reference_provenance,
    severity="info",
    example=(
        "Provenance reference to QuestionItem "
        "'11111111-1111-4111-8111-0000000000ff' points outside this file."
    ),
)
register_profile(DDI_PROFILE_DEFAULT, tuple(_REGISTRY))
register_rule(
    "colectica.maintainable.labels",
    _check_colectica_labels,
    default=False,
    severity="warning",
    example="QuestionConstruct 11111111 has no label or name with text.",
)


__all__ = [
    "ALLOWED_AGENCIES",  # noqa: F822 - served by the module __getattr__
    "COLECTICA_QUESTIONNAIRE_PROFILE",
    "DDI_PROFILE_DEFAULT",
    "SEVERITIES",
    "LintConfiguration",
    "LintFinding",
    "ProfileResult",
    "RuleInfo",
    "configure_lint",
    "get_lint_configuration",
    "iter_rule_metadata",
    "lint_configuration",
    "register_profile",
    "register_rule",
    "reset_lint_configuration",
    "run_lint",
    "run_profile",
    "set_lint_configuration",
]

# The colectica-questionnaire rules and profile; imported last because the
# module builds on the names above.
from . import colectica_lint as _colectica_lint  # noqa: E402, F401
