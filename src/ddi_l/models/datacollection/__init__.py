"""Data Collection module wrappers.

This package contains maintainable wrappers for the DDI DataCollection
module, providing classes for questions, instruments, instructions,
sampling, and data collection containers.

Example:
    >>> from ddi_l.models.datacollection import (
    ...     DataCollection,
    ...     QuestionItem,
    ...     QuestionScheme,
    ...     Instrument,
    ... )
    >>>
    >>> q = QuestionItem(
    ...     agency="example.org",
    ...     identifier="age-q",
    ...     version="1.0",
    ...     question_texts=[InternationalString("What is your age?")],
    ... )
"""

from __future__ import annotations

# Re-export the public classes defined in the implementation module.
from ._monolith import (
    # Internal but used by tests
    _REFERENCE_NAMESPACE,  # noqa: F401
    # Exported in __all__
    CollectionActivity,
    CollectionEvent,
    ComputationItem,
    ControlConstructBase,
    DataCaptureDevelopment,
    DataCaptureMethod,
    DataCollection,
    DynamicText,
    ElseIf,
    GeneralInstruction,
    GenerationInstruction,
    GridDimension,
    IfThenElse,
    Instruction,
    InstructionGroup,
    Instrument,
    InterviewerInstructionReference,
    InterviewerInstructionScheme,
    Loop,
    ObservationPlan,
    OutParameter,
    ProcessingEvent,
    ProcessingEventScheme,
    ProcessingInstructionGroup,
    ProcessingInstructionScheme,
    QuestionBlock,
    QuestionConstruct,
    QuestionGrid,
    QuestionGroup,
    QuestionItem,
    QuestionMaintainableBase,
    QuestionScheme,
    SamplingInformationGroup,
    SamplingInformationScheme,
    SamplingPlan,
    Sequence,
    SourceReference,
    StatementItem,
    # Base classes (not in __all__ but needed for type hints/subclassing)
    VersionableInitData,
    VersionableMaintainableBase,
    make_if_condition,
)

__all__ = [
    "CollectionActivity",
    "CollectionEvent",
    "ComputationItem",
    "ControlConstructBase",
    "DataCaptureDevelopment",
    "DataCaptureMethod",
    "DataCollection",
    "DynamicText",
    "ElseIf",
    "GeneralInstruction",
    "GenerationInstruction",
    "GridDimension",
    "IfThenElse",
    "Instruction",
    "InstructionGroup",
    "Instrument",
    "InterviewerInstructionReference",
    "InterviewerInstructionScheme",
    "Loop",
    "ObservationPlan",
    "OutParameter",
    "ProcessingEvent",
    "ProcessingEventScheme",
    "ProcessingInstructionGroup",
    "ProcessingInstructionScheme",
    "QuestionBlock",
    "QuestionConstruct",
    "QuestionGrid",
    "QuestionGroup",
    "QuestionItem",
    "QuestionMaintainableBase",
    "QuestionScheme",
    "SamplingInformationGroup",
    "SamplingInformationScheme",
    "SamplingPlan",
    "Sequence",
    "SourceReference",
    "StatementItem",
    # Base classes for subclassing
    "VersionableInitData",
    "VersionableMaintainableBase",
    "make_if_condition",
]
