"""DDI model classes representing maintainable elements.

This package provides dataclass-style wrappers for DDI maintainable
elements, organized by DDI module.
"""

from __future__ import annotations

# Archive module
from .archive import Archive, Organization

# Base types - always available
from .base import (
    CodeValue,
    InternationalString,
    MaintainableBase,
    Reference,
    ReferenceWarning,
    UserAttributePair,
    UserID,
    ValidationContext,
    VersionRationale,
    clone_element,
    qn,
)

# Classification module
from .classification import (
    ClassificationFamily,
    ClassificationItem,
    ClassificationScheme,
    ClassificationSeries,
)

# Comparison module
from .comparison import Comparison

# Concept module
from .concept import Concept, ConceptualVariable, UnitType, Universe

# Conceptual component module
from .conceptualcomponent import ConceptualComponent

# Data collection - all exports from datacollection package
from .datacollection import (
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
    VersionableMaintainableBase,
)
from .dataset import DataSet

# Dissemination module
from .dissemination import (
    ConceptMap,
    PhysicalInstanceGroup,
    QuestionMap,
    VariableMap,
    Weighting,
    WeightingMethodology,
)

# Group module
from .group import Group, LocalHoldingPackage, ResourcePackage

# Instance module
from .instance import TranslationInformation

# Logical product module
from .logicalproduct import (
    Category,
    CategoryScheme,
    CodeItem,
    CodeList,
    CodeRepresentation,
    DateTimeRepresentation,
    LogicalProduct,
    NumberRange,
    NumericRepresentation,
    RepresentedVariable,
    TextRepresentation,
    Variable,
    VariableGroup,
    VariableRepresentation,
)

# Methodology module
from .methodology import (
    Methodology,
    MethodologyItem,
    MethodologyScheme,
    ReviewEvent,
)

# Physical module
from .physical import PhysicalInstance, PhysicalStructure

# Process module
from .process import (
    Process,
    ProcessControl,
    ProcessControlScheme,
    ProcessMethod,
    ProcessMethodScheme,
    ProcessScheme,
    ProcessStep,
    ProcessStepScheme,
)
from .profile import DDIProfile

# Quality module
from .quality import (
    QualityScheme,
    QualityStandard,
    QualityStandardGroup,
    QualityStatement,
    QualityStatementGroup,
)

# Reusable module
from .reusable import InformationClassification, ManagedMissingValuesRepresentation

# Study module
from .study import StudyUnit

__all__ = [
    # Archive
    "Archive",
    # Logical product
    "Category",
    "CategoryScheme",
    # Classification
    "ClassificationFamily",
    "ClassificationItem",
    "ClassificationScheme",
    "ClassificationSeries",
    "CodeItem",
    "CodeList",
    "CodeRepresentation",
    "CodeValue",
    # Data collection
    "CollectionActivity",
    "CollectionEvent",
    # Comparison
    "Comparison",
    "ComputationItem",
    # Concept
    "Concept",
    # Dissemination
    "ConceptMap",
    # Conceptual component
    "ConceptualComponent",
    "ConceptualVariable",
    "ControlConstructBase",
    "DDIProfile",
    "DataCaptureDevelopment",
    "DataCaptureMethod",
    "DataCollection",
    # Group
    "DataSet",
    "DateTimeRepresentation",
    "DynamicText",
    "ElseIf",
    "GeneralInstruction",
    "GenerationInstruction",
    "GridDimension",
    "Group",
    "IfThenElse",
    # Reusable
    "InformationClassification",
    "Instruction",
    "InstructionGroup",
    "Instrument",
    "InternationalString",
    "InterviewerInstructionReference",
    "InterviewerInstructionScheme",
    "LocalHoldingPackage",
    "LogicalProduct",
    # Base
    "MaintainableBase",
    "ManagedMissingValuesRepresentation",
    # Methodology
    "Methodology",
    "MethodologyItem",
    "MethodologyScheme",
    "NumberRange",
    "NumericRepresentation",
    "ObservationPlan",
    "Organization",
    "OutParameter",
    # Physical
    "PhysicalInstance",
    "PhysicalInstanceGroup",
    "PhysicalStructure",
    # Process
    "Process",
    "ProcessControl",
    "ProcessControlScheme",
    "ProcessMethod",
    "ProcessMethodScheme",
    "ProcessScheme",
    "ProcessStep",
    "ProcessStepScheme",
    "ProcessingEvent",
    "ProcessingEventScheme",
    "ProcessingInstructionGroup",
    "ProcessingInstructionScheme",
    # Quality
    "QualityScheme",
    "QualityStandard",
    "QualityStandardGroup",
    "QualityStatement",
    "QualityStatementGroup",
    "QuestionBlock",
    "QuestionConstruct",
    "QuestionGrid",
    "QuestionGroup",
    "QuestionItem",
    "QuestionMaintainableBase",
    "QuestionMap",
    "QuestionScheme",
    "Reference",
    "ReferenceWarning",
    "RepresentedVariable",
    "ResourcePackage",
    "ReviewEvent",
    "SamplingInformationGroup",
    "SamplingInformationScheme",
    "SamplingPlan",
    "Sequence",
    "SourceReference",
    "StatementItem",
    # Study
    "StudyUnit",
    "TextRepresentation",
    "TranslationInformation",
    "UnitType",
    "Universe",
    "UserAttributePair",
    "UserID",
    "ValidationContext",
    "Variable",
    "VariableGroup",
    "VariableMap",
    "VariableRepresentation",
    "VersionRationale",
    "VersionableMaintainableBase",
    "Weighting",
    "WeightingMethodology",
    "clone_element",
    "qn",
]
