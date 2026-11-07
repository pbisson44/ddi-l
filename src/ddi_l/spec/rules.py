"""The rules `ddi_l.spec.conform` reports, with their default severity.

A spec's ``severities:`` block changes a rule's severity.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["RULES", "RULE_SEVERITIES", "SpecRule"]


@dataclass(frozen=True)
class SpecRule:
    """One conformance rule.

    Attributes:
        rule_id: The id findings carry (``spec.item.missing``).
        severity: The default severity.
        summary: What a finding of the rule means.
    """

    rule_id: str
    severity: str
    summary: str


RULES: tuple[SpecRule, ...] = (
    SpecRule(
        "spec.instrument.missing",
        "error",
        "No instrument in the file matches the spec's `instrument`, or the file "
        "has none.",
    ),
    SpecRule(
        "spec.instrument.ambiguous",
        "error",
        "Several instruments match; name one with `instrument` or --instrument.",
    ),
    SpecRule(
        "spec.module.missing", "error", "A required module is not in the instrument."
    ),
    SpecRule(
        "spec.module.ambiguous",
        "error",
        "Several sequences carry a module's id.",
    ),
    SpecRule(
        "spec.module.extra",
        "warning",
        "A sequence at the modules' depth that the spec does not list.",
    ),
    SpecRule("spec.item.missing", "error", "A question or statement is not found."),
    SpecRule(
        "spec.item.ambiguous",
        "error",
        "Several constructs carry a question's or statement's id.",
    ),
    SpecRule(
        "spec.item.extra",
        "warning",
        "A question or statement in a module that the spec does not list there, "
        "or lists in another module.",
    ),
    SpecRule(
        "spec.item.misplaced",
        "warning",
        "A question or statement found only in other modules than the spec's.",
    ),
    SpecRule(
        "spec.item.id-sources-differ",
        "info",
        "The id sources of a question disagree (its construct name and its "
        "item name, say).",
    ),
    SpecRule("spec.code.missing", "error", "A code the spec lists is not offered."),
    SpecRule("spec.code.extra", "error", "A code is offered the spec does not list."),
    SpecRule(
        "spec.code.label",
        "warning",
        "A code's category label differs from the spec's, in one language.",
    ),
    SpecRule(
        "spec.language.missing",
        "warning",
        "A question's text or a code's label lacks one of the spec's languages.",
    ),
    SpecRule(
        "spec.domain.type",
        "error",
        "The response domain is of another kind (code, numeric, text, date), "
        "or a mixed domain holds none of the spec's kind.",
    ),
    SpecRule(
        "spec.domain.length",
        "error",
        "A text domain's minimum or maximum length differs.",
    ),
    SpecRule(
        "spec.domain.range",
        "error",
        "A numeric domain's bounds, or whether they are included, differ.",
    ),
    SpecRule("spec.domain.decimals", "warning", "A numeric domain's decimals differ."),
    SpecRule(
        "spec.domain.unverifiable",
        "info",
        "The question's domain cannot be read (several, a mixed domain with "
        "several of the spec's kind, a reference not in the file, a code list "
        "that cannot be resolved).",
    ),
    SpecRule(
        "spec.gate.missing",
        "error",
        "The spec gates a module or question, and nothing gates it.",
    ),
    SpecRule(
        "spec.gate.different",
        "error",
        "The gate differs from the spec's; both normal forms are shown.",
    ),
    SpecRule(
        "spec.gate.extra",
        "warning",
        "A module or question is gated, and the spec gates it with nothing.",
    ),
    SpecRule(
        "spec.gate.scope",
        "error",
        "The gate wraps each page where the spec says the module, or the reverse.",
    ),
    SpecRule(
        "spec.gate.unverifiable",
        "warning",
        "The stored gate cannot be read back into an expression (an operator "
        "code not listed, a don't-know test, and and or mixed, malformed Neutral "
        "JSON, native code this reader does not know), or paths to the item carry "
        "different gates.",
    ),
    SpecRule(
        "spec.edit.unverifiable",
        "info",
        "Not verifiable (edit storage unknown): reported for each edit unless "
        "--edits strict or off.",
    ),
    SpecRule(
        "spec.edit.missing",
        "error",
        "With --edits strict, no edit check carries the edit's id.",
    ),
    SpecRule(
        "spec.edit.different",
        "error",
        "With --edits strict, the edit check's condition differs from `when`.",
    ),
    SpecRule(
        "spec.variable.import-undeclared",
        "error",
        "An imported variable is not a field of any data lookup the instrument "
        "reaches.",
    ),
    SpecRule(
        "spec.variable.import-type",
        "warning",
        "An imported variable's lookup field type differs (with `match.lookup_types`).",
    ),
    SpecRule(
        "spec.variable.derived-is-lookup",
        "error",
        "A derived variable is a data lookup field: it is imported, not computed.",
    ),
)

RULE_SEVERITIES: dict[str, str] = {rule.rule_id: rule.severity for rule in RULES}
