"""Check a questionnaire against a spec of what it should contain.

A spec lists a survey's modules, questions, response domains, gates and edit
checks in YAML or JSON (`load_spec`); `conform` compares an
instrument with it. The expression language of gates and edits
(`ddi_l.spec.expression`) and its compilers to Colectica's condition
JSON and to Blaise (`ddi_l.spec.compile`) need nothing beyond the
standard library; reading a spec file needs the ``spec`` extra
(``pip install "ddi-l[spec]"``). Deciding whether two expressions hold for
the same respondents (`decide`) needs the ``logic`` extra
(``pip install "ddi-l[logic]"``).
"""

from __future__ import annotations

from .compile import (
    BlaiseDialect,
    CompiledCondition,
    UnverifiableConditionError,
    comparable,
    compile_condition,
    condition_to_expression,
    parse_blaise,
)
from .conform import (
    EDIT_MODES,
    SEMANTICS,
    ConformError,
    ConformFinding,
    ConformReport,
    ModuleResult,
    conform,
)
from .expression import (
    ExpressionError,
    equivalent,
    format_expression,
    identifiers,
    normalise,
    parse_expression,
    walk,
)
from .model import (
    DomainSpec,
    EditSpec,
    MatchOptions,
    ModuleSpec,
    QuestionSpec,
    Spec,
    SpecDependencyError,
    SpecError,
    SpecProblem,
    VariableSpec,
    example_spec,
    load_spec,
    spec_from_data,
    spec_schema,
    validate_spec,
)
from .rules import RULES, SpecRule
from .semantics import (
    Answer,
    Example,
    LogicDependencyError,
    Verdict,
    decide,
    evaluate,
)

__all__ = [
    "EDIT_MODES",
    "RULES",
    "SEMANTICS",
    "Answer",
    "BlaiseDialect",
    "CompiledCondition",
    "ConformError",
    "ConformFinding",
    "ConformReport",
    "DomainSpec",
    "EditSpec",
    "Example",
    "ExpressionError",
    "LogicDependencyError",
    "MatchOptions",
    "ModuleResult",
    "ModuleSpec",
    "QuestionSpec",
    "Spec",
    "SpecDependencyError",
    "SpecError",
    "SpecProblem",
    "SpecRule",
    "UnverifiableConditionError",
    "VariableSpec",
    "Verdict",
    "comparable",
    "compile_condition",
    "condition_to_expression",
    "conform",
    "decide",
    "equivalent",
    "evaluate",
    "example_spec",
    "format_expression",
    "identifiers",
    "load_spec",
    "normalise",
    "parse_blaise",
    "parse_expression",
    "spec_from_data",
    "spec_schema",
    "validate_spec",
    "walk",
]
