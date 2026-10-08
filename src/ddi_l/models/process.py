"""Process module maintainable wrappers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, ClassVar

from .._etree import Element, create_element
from ..constants import PROCESS_NS, REUSABLE_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from .base import InternationalString, MaintainableBase, Reference, clone_element, qn
from .datacollection import VersionableMaintainableBase

__all__ = [
    "Process",
    "ProcessControl",
    "ProcessControlScheme",
    "ProcessMethod",
    "ProcessMethodScheme",
    "ProcessScheme",
    "ProcessStep",
    "ProcessStepScheme",
]


@dataclass
class _ProcessMaintainableBase(VersionableMaintainableBase):
    """Shared helpers for Process maintainables with name containers."""

    names: list[InternationalString] = field(default_factory=list)

    NAME_TAG: ClassVar[str]

    @classmethod
    def _collect_process_common(
        cls,
        element: Element,
        *,
        recognized_children: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        name_tag = qn(PROCESS_NS, cls.NAME_TAG)
        recognized = {name_tag}
        if recognized_children:
            recognized.update(recognized_children)
        data: dict[str, Any] = dict(
            cls._collect_versionable_common(element, recognized_children=recognized)
        )
        names: list[InternationalString] = []
        for container in element.findall(name_tag):
            names.extend(InternationalString.from_container(container))
        data["names"] = names
        return data

    def _append_process_common(self, element: Element) -> None:
        self._append_versionable_common(element)
        for name in self.names:
            container = create_element(qn(PROCESS_NS, self.NAME_TAG))
            container.append(name.to_child(child_tag="String"))
            element.append(container)


@dataclass
class ProcessControl(_ProcessMaintainableBase):
    """Representation of ``pr:ProcessControl`` maintainables."""

    type_of_process_control: str | None = None
    command_codes: list[Element] = field(default_factory=list)

    TAG: ClassVar[str] = qn(PROCESS_NS, "ProcessControl")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("prc")
    NAME_TAG: ClassVar[str] = "ProcessControlName"

    @classmethod
    def from_xml(cls, element: Element) -> ProcessControl:
        recognized = {
            qn(PROCESS_NS, "TypeOfProcessControl"),
            qn(REUSABLE_NS, "CommandCode"),
        }
        data = cls._collect_process_common(element, recognized_children=recognized)
        type_el = element.find(qn(PROCESS_NS, "TypeOfProcessControl"))
        command_codes = [
            clone_element(node)
            for node in element.findall(qn(REUSABLE_NS, "CommandCode"))
        ]
        return cls(
            type_of_process_control=type_el.text if type_el is not None else None,
            command_codes=command_codes,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_process_common(element)
        if self.type_of_process_control:
            type_el = create_element(qn(PROCESS_NS, "TypeOfProcessControl"))
            type_el.text = self.type_of_process_control
            element.append(type_el)
        for node in self.command_codes:
            element.append(clone_element(node))
        self._append_other_elements(element)
        return element


@dataclass
class ProcessMethod(_ProcessMaintainableBase):
    """Representation of ``pr:ProcessMethod`` maintainables."""

    method_type: str | None = None
    command_codes: list[Element] = field(default_factory=list)

    TAG: ClassVar[str] = qn(PROCESS_NS, "ProcessMethod")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("prc")
    NAME_TAG: ClassVar[str] = "ProcessMethodName"

    @classmethod
    def from_xml(cls, element: Element) -> ProcessMethod:
        recognized = {
            qn(PROCESS_NS, "TypeOfMethod"),
            qn(REUSABLE_NS, "CommandCode"),
        }
        data = cls._collect_process_common(element, recognized_children=recognized)
        method_type_el = element.find(qn(PROCESS_NS, "TypeOfMethod"))
        command_codes = [
            clone_element(node)
            for node in element.findall(qn(REUSABLE_NS, "CommandCode"))
        ]
        return cls(
            method_type=method_type_el.text if method_type_el is not None else None,
            command_codes=command_codes,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_process_common(element)
        if self.method_type:
            method_el = create_element(qn(PROCESS_NS, "TypeOfMethod"))
            method_el.text = self.method_type
            element.append(method_el)
        for node in self.command_codes:
            element.append(clone_element(node))
        self._append_other_elements(element)
        return element


@dataclass
class ProcessStep(_ProcessMaintainableBase):
    """Representation of ``pr:ProcessStep`` maintainables."""

    process_methods: list[ProcessMethod] = field(default_factory=list)
    process_method_references: list[Reference] = field(default_factory=list)
    process_controls: list[ProcessControl] = field(default_factory=list)
    process_control_references: list[Reference] = field(default_factory=list)
    process_step_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(PROCESS_NS, "ProcessStep")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("prc")
    NAME_TAG: ClassVar[str] = "ProcessStepName"

    @classmethod
    def from_xml(cls, element: Element) -> ProcessStep:
        recognized = {
            qn(PROCESS_NS, "ProcessMethod"),
            qn(PROCESS_NS, "ProcessMethodReference"),
            qn(PROCESS_NS, "ProcessControl"),
            qn(PROCESS_NS, "ProcessControlReference"),
            qn(PROCESS_NS, "ProcessStepReference"),
        }
        data = cls._collect_process_common(element, recognized_children=recognized)
        methods = [
            ProcessMethod.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessMethod"))
        ]
        method_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessMethodReference"))
        ]
        controls = [
            ProcessControl.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessControl"))
        ]
        control_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessControlReference"))
        ]
        step_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessStepReference"))
        ]
        return cls(
            process_methods=methods,
            process_method_references=method_refs,
            process_controls=controls,
            process_control_references=control_refs,
            process_step_references=step_refs,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_process_common(element)
        for process_method in self.process_methods:
            element.append(process_method.to_xml())
        for reference in self.process_method_references:
            element.append(
                reference.to_xml("ProcessMethodReference", namespace=PROCESS_NS)
            )
        for process_control in self.process_controls:
            element.append(process_control.to_xml())
        for reference in self.process_control_references:
            element.append(
                reference.to_xml("ProcessControlReference", namespace=PROCESS_NS)
            )
        for reference in self.process_step_references:
            element.append(
                reference.to_xml("ProcessStepReference", namespace=PROCESS_NS)
            )
        self._append_other_elements(element)
        return element


@dataclass
class Process(_ProcessMaintainableBase):
    """Representation of ``pr:Process`` maintainables."""

    process_steps: list[ProcessStep] = field(default_factory=list)
    process_step_references: list[Reference] = field(default_factory=list)
    process_methods: list[ProcessMethod] = field(default_factory=list)
    process_method_references: list[Reference] = field(default_factory=list)
    process_controls: list[ProcessControl] = field(default_factory=list)
    process_control_references: list[Reference] = field(default_factory=list)
    process_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(PROCESS_NS, "Process")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("prc")
    NAME_TAG: ClassVar[str] = "ProcessName"

    @classmethod
    def from_xml(cls, element: Element) -> Process:
        recognized = {
            qn(PROCESS_NS, "ProcessStep"),
            qn(PROCESS_NS, "ProcessStepReference"),
            qn(PROCESS_NS, "ProcessMethod"),
            qn(PROCESS_NS, "ProcessMethodReference"),
            qn(PROCESS_NS, "ProcessControl"),
            qn(PROCESS_NS, "ProcessControlReference"),
            qn(PROCESS_NS, "ProcessReference"),
        }
        data = cls._collect_process_common(element, recognized_children=recognized)
        steps = [
            ProcessStep.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessStep"))
        ]
        step_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessStepReference"))
        ]
        methods = [
            ProcessMethod.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessMethod"))
        ]
        method_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessMethodReference"))
        ]
        controls = [
            ProcessControl.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessControl"))
        ]
        control_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessControlReference"))
        ]
        process_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessReference"))
        ]
        return cls(
            process_steps=steps,
            process_step_references=step_refs,
            process_methods=methods,
            process_method_references=method_refs,
            process_controls=controls,
            process_control_references=control_refs,
            process_references=process_refs,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_process_common(element)
        for step in self.process_steps:
            element.append(step.to_xml())
        for reference in self.process_step_references:
            element.append(
                reference.to_xml("ProcessStepReference", namespace=PROCESS_NS)
            )
        for method in self.process_methods:
            element.append(method.to_xml())
        for reference in self.process_method_references:
            element.append(
                reference.to_xml("ProcessMethodReference", namespace=PROCESS_NS)
            )
        for control in self.process_controls:
            element.append(control.to_xml())
        for reference in self.process_control_references:
            element.append(
                reference.to_xml("ProcessControlReference", namespace=PROCESS_NS)
            )
        for reference in self.process_references:
            element.append(reference.to_xml("ProcessReference", namespace=PROCESS_NS))
        self._append_other_elements(element)
        return element


@dataclass
class _ProcessSchemeBase(MaintainableBase):
    """Shared helpers for Process scheme maintainables."""

    names: list[InternationalString] = field(default_factory=list)
    NAME_TAG: ClassVar[str]

    @classmethod
    def _collect_scheme_common(
        cls,
        element: Element,
        *,
        recognized_children: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        name_tag = qn(PROCESS_NS, cls.NAME_TAG)
        recognized = {name_tag}
        if recognized_children:
            recognized.update(recognized_children)
        data: dict[str, Any] = dict(
            cls._collect_common(element, recognized_children=recognized)
        )
        names: list[InternationalString] = []
        for container in element.findall(name_tag):
            names.extend(InternationalString.from_container(container))
        data["names"] = names
        return data

    def _append_scheme_common(self, element: Element) -> None:
        for name in self.names:
            container = create_element(qn(PROCESS_NS, self.NAME_TAG))
            container.append(name.to_child(child_tag="String"))
            element.append(container)


@dataclass
class ProcessControlScheme(_ProcessSchemeBase):
    """Maintainable wrapper for ``pr:ProcessControlScheme`` structures."""

    process_controls: list[ProcessControl] = field(default_factory=list)
    process_control_references: list[Reference] = field(default_factory=list)
    scheme_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(PROCESS_NS, "ProcessControlScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("prc")
    NAME_TAG: ClassVar[str] = "ProcessControlSchemeName"

    def __post_init__(self) -> None:
        self._propagate_child_identification(
            self.process_controls,
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "process-control", index
            ),
        )

    @classmethod
    def from_xml(cls, element: Element) -> ProcessControlScheme:
        recognized = {
            qn(PROCESS_NS, "ProcessControlSchemeReference"),
            qn(PROCESS_NS, "ProcessControl"),
            qn(PROCESS_NS, "ProcessControlReference"),
        }
        data = cls._collect_scheme_common(element, recognized_children=recognized)
        controls = [
            ProcessControl.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessControl"))
        ]
        control_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessControlReference"))
        ]
        scheme_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessControlSchemeReference"))
        ]
        return cls(
            process_controls=controls,
            process_control_references=control_refs,
            scheme_references=scheme_refs,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_scheme_common(element)
        for control in self.process_controls:
            element.append(control.to_xml())
        for reference in self.process_control_references:
            element.append(
                reference.to_xml("ProcessControlReference", namespace=PROCESS_NS)
            )
        for reference in self.scheme_references:
            element.append(
                reference.to_xml("ProcessControlSchemeReference", namespace=PROCESS_NS)
            )
        self._append_other_elements(element)
        return element


@dataclass
class ProcessMethodScheme(_ProcessSchemeBase):
    """Maintainable wrapper for ``pr:ProcessMethodScheme`` structures."""

    process_methods: list[ProcessMethod] = field(default_factory=list)
    process_method_references: list[Reference] = field(default_factory=list)
    scheme_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(PROCESS_NS, "ProcessMethodScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("prc")
    NAME_TAG: ClassVar[str] = "ProcessMethodSchemeName"

    def __post_init__(self) -> None:
        self._propagate_child_identification(
            self.process_methods,
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "process-method", index
            ),
        )

    @classmethod
    def from_xml(cls, element: Element) -> ProcessMethodScheme:
        recognized = {
            qn(PROCESS_NS, "ProcessMethodSchemeReference"),
            qn(PROCESS_NS, "ProcessMethod"),
            qn(PROCESS_NS, "ProcessMethodReference"),
        }
        data = cls._collect_scheme_common(element, recognized_children=recognized)
        methods = [
            ProcessMethod.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessMethod"))
        ]
        method_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessMethodReference"))
        ]
        scheme_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessMethodSchemeReference"))
        ]
        return cls(
            process_methods=methods,
            process_method_references=method_refs,
            scheme_references=scheme_refs,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_scheme_common(element)
        for method in self.process_methods:
            element.append(method.to_xml())
        for reference in self.process_method_references:
            element.append(
                reference.to_xml("ProcessMethodReference", namespace=PROCESS_NS)
            )
        for reference in self.scheme_references:
            element.append(
                reference.to_xml("ProcessMethodSchemeReference", namespace=PROCESS_NS)
            )
        self._append_other_elements(element)
        return element


@dataclass
class ProcessStepScheme(_ProcessSchemeBase):
    """Maintainable wrapper for ``pr:ProcessStepScheme`` structures."""

    process_steps: list[ProcessStep] = field(default_factory=list)
    process_step_references: list[Reference] = field(default_factory=list)
    scheme_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(PROCESS_NS, "ProcessStepScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("prc")
    NAME_TAG: ClassVar[str] = "ProcessStepSchemeName"

    def __post_init__(self) -> None:
        self._propagate_child_identification(
            self.process_steps,
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "process-step", index
            ),
        )

    @classmethod
    def from_xml(cls, element: Element) -> ProcessStepScheme:
        recognized = {
            qn(PROCESS_NS, "ProcessStepSchemeReference"),
            qn(PROCESS_NS, "ProcessStep"),
            qn(PROCESS_NS, "ProcessStepReference"),
        }
        data = cls._collect_scheme_common(element, recognized_children=recognized)
        steps = [
            ProcessStep.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessStep"))
        ]
        step_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessStepReference"))
        ]
        scheme_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessStepSchemeReference"))
        ]
        return cls(
            process_steps=steps,
            process_step_references=step_refs,
            scheme_references=scheme_refs,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_scheme_common(element)
        for step in self.process_steps:
            element.append(step.to_xml())
        for reference in self.process_step_references:
            element.append(
                reference.to_xml("ProcessStepReference", namespace=PROCESS_NS)
            )
        for reference in self.scheme_references:
            element.append(
                reference.to_xml("ProcessStepSchemeReference", namespace=PROCESS_NS)
            )
        self._append_other_elements(element)
        return element


@dataclass
class ProcessScheme(_ProcessSchemeBase):
    """Maintainable wrapper for ``pr:ProcessScheme`` structures."""

    processes: list[Process] = field(default_factory=list)
    process_references: list[Reference] = field(default_factory=list)
    scheme_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(PROCESS_NS, "ProcessScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("prc")
    NAME_TAG: ClassVar[str] = "ProcessSchemeName"

    def __post_init__(self) -> None:
        self._propagate_child_identification(
            self.processes,
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "process", index
            ),
        )

    @classmethod
    def from_xml(cls, element: Element) -> ProcessScheme:
        recognized = {
            qn(PROCESS_NS, "ProcessSchemeReference"),
            qn(PROCESS_NS, "Process"),
            qn(PROCESS_NS, "ProcessReference"),
        }
        data = cls._collect_scheme_common(element, recognized_children=recognized)
        processes = [
            Process.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "Process"))
        ]
        process_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessReference"))
        ]
        scheme_refs = [
            Reference.from_xml(node)
            for node in element.findall(qn(PROCESS_NS, "ProcessSchemeReference"))
        ]
        return cls(
            processes=processes,
            process_references=process_refs,
            scheme_references=scheme_refs,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_scheme_common(element)
        for process in self.processes:
            element.append(process.to_xml())
        for reference in self.process_references:
            element.append(reference.to_xml("ProcessReference", namespace=PROCESS_NS))
        for reference in self.scheme_references:
            element.append(
                reference.to_xml("ProcessSchemeReference", namespace=PROCESS_NS)
            )
        self._append_other_elements(element)
        return element
