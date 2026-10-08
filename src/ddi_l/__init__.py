"""ddi-l - Python library for DDI Lifecycle XML documents.

Quick Start::

    import ddi_l as ddi

    doc = ddi.new_study(title="My Survey", agency="example.org")
    q = doc.add_question(text="How old are you?")
    v = doc.add_variable(name="Age", question=q)
    doc.save("my-study.xml")

    doc = ddi.open_ddi("existing-study.xml")
    for v in doc.variables:
        print(v.identifier)

The simple API (``new_study``, ``open_ddi``, ``Document``) is the recommended
entry point. The generated models under ``ddi_l.models`` are the advanced
layer.

Names are imported on first access, so ``import ddi_l`` stays fast and the
``ddi`` command starts without loading the model layer.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__author__ = "Philippe Bisson"

# Public name -> (submodule, attribute).
_LAZY_ATTRIBUTES: dict[str, tuple[str, str]] = {
    # Simple CRUD API and document wrappers
    "DDIDocument": (".document", "DDIDocument"),
    "DDIFragment": (".document", "DDIFragment"),
    "Document": (".document", "Document"),
    "StudyCursor": (".document", "StudyCursor"),
    "new_study": (".document", "new_study"),
    "open_ddi": (".document", "open_ddi"),
    # Exceptions
    "DDIError": (".exceptions", "DDIError"),
    "DDIModelError": (".exceptions", "DDIModelError"),
    "DDIParseError": (".exceptions", "DDIParseError"),
    "DDIReadError": (".exceptions", "DDIReadError"),
    "DDIReferenceError": (".exceptions", "DDIReferenceError"),
    "DDIValidationError": (".exceptions", "DDIValidationError"),
    "DDIWriteError": (".exceptions", "DDIWriteError"),
    "DDIReferenceWarning": (".exceptions", "DDIReferenceWarning"),
    "DuplicateIdentifierError": (".exceptions", "DuplicateIdentifierError"),
    "ErrorLocation": (".exceptions", "ErrorLocation"),
    "ModelBuildError": (".exceptions", "ModelBuildError"),
    "ModelValidationError": (".exceptions", "ModelValidationError"),
    # I/O
    "iter_questions": (".io", "iter_questions"),
    "iter_variables": (".io", "iter_variables"),
    "iterparse_ddi": (".io", "iterparse_ddi"),
    "read_ddi": (".io", "read_ddi"),
    "write_ddi": (".io", "write_ddi"),
    # Common model types
    "CodeList": (".models", "CodeList"),
    "Concept": (".models", "Concept"),
    "DataCollection": (".models", "DataCollection"),
    "LogicalProduct": (".models", "LogicalProduct"),
    "QuestionItem": (".models", "QuestionItem"),
    "StudyUnit": (".models", "StudyUnit"),
    "Universe": (".models", "Universe"),
    "Variable": (".models", "Variable"),
    "InternationalString": (".models.base", "InternationalString"),
    "MaintainableBase": (".models.base", "MaintainableBase"),
    "Reference": (".models.base", "Reference"),
}

__all__ = [
    "CodeList",
    "Concept",
    "DDIDocument",
    "DDIError",
    "DDIFragment",
    "DDIModelError",
    "DDIParseError",
    "DDIReadError",
    "DDIReferenceError",
    "DDIReferenceWarning",
    "DDIValidationError",
    "DDIWriteError",
    "DataCollection",
    "Document",
    "DuplicateIdentifierError",
    "ErrorLocation",
    "InternationalString",
    "LogicalProduct",
    "MaintainableBase",
    "ModelBuildError",
    "ModelValidationError",
    "QuestionItem",
    "Reference",
    "StudyCursor",
    "StudyUnit",
    "Universe",
    "Variable",
    "__author__",
    "__version__",
    "iter_questions",
    "iter_variables",
    "iterparse_ddi",
    "new_study",
    "open_ddi",
    "read_ddi",
    "write_ddi",
]


def _read_version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("ddi-l")
    except PackageNotFoundError:  # pragma: no cover - running from an unbuilt tree
        return "0.0.0.dev0"


def __getattr__(name: str) -> Any:
    """Import public names on first access (PEP 562)."""
    if name == "__version__":
        value: Any = _read_version()
    else:
        try:
            module_name, attribute = _LAZY_ATTRIBUTES[name]
        except KeyError:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            ) from None
        value = getattr(import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *__all__})


if TYPE_CHECKING:
    from .document import (
        DDIDocument,
        DDIFragment,
        Document,
        StudyCursor,
        new_study,
        open_ddi,
    )
    from .exceptions import (
        DDIError,
        DDIModelError,
        DDIParseError,
        DDIReadError,
        DDIReferenceError,
        DDIReferenceWarning,
        DDIValidationError,
        DDIWriteError,
        DuplicateIdentifierError,
        ErrorLocation,
        ModelBuildError,
        ModelValidationError,
    )
    from .io import (
        iter_questions,
        iter_variables,
        iterparse_ddi,
        read_ddi,
        write_ddi,
    )
    from .models import (
        CodeList,
        Concept,
        DataCollection,
        LogicalProduct,
        QuestionItem,
        StudyUnit,
        Universe,
        Variable,
    )
    from .models.base import (
        InternationalString,
        MaintainableBase,
        Reference,
    )

    __version__: str
