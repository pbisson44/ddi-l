"""Typed ``r:InParameter``, ``r:OutParameter`` and ``r:Binding``.

A control construct's parameters and bindings parse into :class:`InParameter`,
:class:`OutParameter` and :class:`Binding`; one read and written back
unchanged comes out as read, and one built in code is written in the order
``r:ParameterType`` sets.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

import ddi_l
from ddi_l._etree import Element, fromstring, tostring
from ddi_l.colectica_logic import explain_condition
from ddi_l.models import (
    Binding,
    ComputationItem,
    IfThenElse,
    InParameter,
    Instruction,
    InternationalString,
    OutParameter,
    QuestionConstruct,
    Sequence,
    StatementItem,
    items,
)
from ddi_l.models.base import Reference, qn
from ddi_l.models.datacollection import Loop

R = "ddi:reusable:3_3"
D = "ddi:datacollection:3_3"
CONDITIONS = (
    Path(__file__).parent / "fixtures" / "colectica" / "pets_conditions.ddi33.xml"
)


def _id(n: int) -> str:
    return f"22222222-2222-4222-8222-{n:012d}"


def _local_names(element: Element) -> list[str]:
    return [child.tag.rsplit("}", 1)[-1] for child in element]


def _without_tail(element: Element) -> str:
    # tostring() includes the tail, which the layout of the parent sets.
    copied = copy.deepcopy(element)
    copied.tail = None
    return tostring(copied)


IN_PARAMETER = (
    f'<r:InParameter xmlns:r="{R}" isArray="true" limitArrayIndex="1 2">'
    f"<r:URN>urn:ddi:int.example:{_id(901)}:1</r:URN>"
    f"<r:Agency>int.example</r:Agency><r:ID>{_id(901)}</r:ID><r:Version>1</r:Version>"
    '<r:ParameterName><r:String xml:lang="en">Pet count</r:String></r:ParameterName>'
    "<r:Alias>Count</r:Alias>"
    '<r:Description><r:Content xml:lang="en">How many pets.</r:Content>'
    "</r:Description>"
    "<r:NumericRepresentation><r:NumericTypeCode>Integer</r:NumericTypeCode>"
    "</r:NumericRepresentation>"
    "<r:DefaultValue>0</r:DefaultValue>"
    "</r:InParameter>"
)


def test_an_in_parameter_reads_every_part() -> None:
    parameter = InParameter.from_xml(fromstring(IN_PARAMETER))
    assert (parameter.agency, parameter.identifier, parameter.version) == (
        "int.example",
        _id(901),
        "1",
    )
    assert parameter.alias == "Count"
    assert [(n.text, n.lang) for n in parameter.parameter_names] == [
        ("Pet count", "en")
    ]
    assert [(d.text, d.lang) for d in parameter.descriptions] == [
        ("How many pets.", "en")
    ]
    assert parameter.representation is not None
    assert parameter.representation.tag == qn(R, "NumericRepresentation")
    assert parameter.default_value == "0"
    assert parameter.is_array is True
    assert parameter.limit_array_index == "1 2"
    assert parameter.other_elements == []
    assert parameter.other_attributes == {}


def test_an_unchanged_in_parameter_is_written_as_read() -> None:
    source = fromstring(IN_PARAMETER)
    parameter = InParameter.from_xml(source)
    assert tostring(parameter.to_xml()) == tostring(source)


def test_an_edited_in_parameter_keeps_the_schema_order() -> None:
    parameter = InParameter.from_xml(fromstring(IN_PARAMETER))
    parameter.alias = "Pets"
    parameter.is_array = False
    element = parameter.to_xml()
    assert _local_names(element) == [
        "URN",
        "Agency",
        "ID",
        "Version",
        "ParameterName",
        "Alias",
        "Description",
        "NumericRepresentation",
        "DefaultValue",
    ]
    assert element.findtext(qn(R, "Alias")) == "Pets"
    assert element.get("isArray") == "false"
    assert element.get("limitArrayIndex") == "1 2"
    (name,) = element.findall(qn(R, "ParameterName"))
    assert [child.tag for child in name] == [qn(R, "String")]


def test_content_kept_unmapped_follows_the_version() -> None:
    parameter = InParameter(
        agency="int.example",
        identifier=_id(901),
        version="1",
        alias="Count",
        other_elements=[
            fromstring(f'<r:UserID xmlns:r="{R}" typeOfUserID="local">P1</r:UserID>')
        ],
    )
    assert _local_names(parameter.to_xml()) == [
        "Agency",
        "ID",
        "Version",
        "UserID",
        "Alias",
    ]


@pytest.mark.parametrize(
    "representation",
    [
        "TextRepresentation",
        "DateTimeRepresentation",
        "CodeRepresentation",
        "NumericRepresentationReference",
    ],
)
def test_an_out_parameter_reads_any_representation(representation: str) -> None:
    source = fromstring(
        f'<r:OutParameter xmlns:r="{R}"><r:Agency>int.example</r:Agency>'
        f"<r:ID>{_id(902)}</r:ID><r:Version>1</r:Version><r:Alias>Answer</r:Alias>"
        f"<r:{representation}/></r:OutParameter>"
    )
    parameter = OutParameter.from_xml(source)
    assert parameter.representation is not None
    assert parameter.representation.tag == qn(R, representation)
    assert parameter.other_elements == []
    assert tostring(parameter.to_xml()) == tostring(source)


def test_a_parameter_needs_an_element_of_its_own_kind() -> None:
    with pytest.raises(ValueError, match="reusable:InParameter"):
        InParameter.from_xml(fromstring(IN_PARAMETER.replace("InParameter", "Other")))
    with pytest.raises(ValueError, match="reusable:Binding"):
        Binding.from_xml(fromstring(f'<r:Other xmlns:r="{R}"/>'))


def test_a_reference_to_a_parameter_has_no_urn() -> None:
    parameter = InParameter.from_xml(fromstring(IN_PARAMETER))
    reference = parameter.to_reference()
    assert reference.type_of_object == "InParameter"
    element = reference.to_xml("TargetParameterReference")
    assert element.find(qn(R, "URN")) is None
    assert element.findtext(qn(R, "ID")) == _id(901)
    with pytest.raises(ValueError, match="agency, ID and version"):
        OutParameter(alias="Answer").to_reference()


def test_a_binding_between_two_parameters() -> None:
    answer = OutParameter(
        agency="int.example", identifier=_id(902), version="3", alias="Answer"
    )
    gate_input = InParameter.from_xml(fromstring(IN_PARAMETER))
    binding = Binding.between(answer, gate_input)
    element = binding.to_xml()
    assert _local_names(element) == [
        "SourceParameterReference",
        "TargetParameterReference",
    ]
    source, target = element
    assert source.findtext(qn(R, "TypeOfObject")) == "OutParameter"
    assert source.findtext(qn(R, "Version")) == "3"
    assert target.findtext(qn(R, "TypeOfObject")) == "InParameter"
    assert source.find(qn(R, "URN")) is None and target.find(qn(R, "URN")) is None
    assert source.get("lateBound") is None

    late = Binding.between(answer.to_reference(), gate_input, late_bound=True)
    assert [end.get("lateBound") for end in late.to_xml()] == ["true", "true"]


def test_a_binding_read_from_a_file_is_written_as_read() -> None:
    source = fromstring(
        f'<r:Binding xmlns:r="{R}"><r:SourceParameterReference lateBound="true">'
        f"<r:Agency>int.example</r:Agency><r:ID>{_id(902)}</r:ID>"
        "<r:Version>1</r:Version><r:TypeOfObject>OutParameter</r:TypeOfObject>"
        "</r:SourceParameterReference><r:TargetParameterReference>"
        f"<r:Agency>int.example</r:Agency><r:ID>{_id(901)}</r:ID>"
        "<r:Version>1</r:Version><r:TypeOfObject>InParameter</r:TypeOfObject>"
        "</r:TargetParameterReference></r:Binding>"
    )
    binding = Binding.from_xml(source)
    assert binding.source_parameter_reference is not None
    assert binding.source_parameter_reference.identifier == _id(902)
    assert tostring(binding.to_xml()) == tostring(source)
    binding.target_parameter_reference = Reference(
        type_of_object="InParameter",
        agency="int.example",
        identifier=_id(903),
        version="1",
    )
    target = binding.to_xml().find(qn(R, "TargetParameterReference"))
    assert target is not None and target.findtext(qn(R, "ID")) == _id(903)


# ---- On control constructs ---------------------------------------------------


def _construct_xml(tag: str, body: str = "") -> str:
    return (
        f'<d:{tag} xmlns:d="{D}" xmlns:r="{R}" isUniversallyUnique="true">'
        f"<r:Agency>int.example</r:Agency><r:ID>{_id(910)}</r:ID>"
        "<r:Version>1</r:Version>"
        '<d:ConstructName><r:String xml:lang="en">X</r:String></d:ConstructName>'
        + IN_PARAMETER.replace(f' xmlns:r="{R}"', "")
        + f"<r:OutParameter><r:Agency>int.example</r:Agency><r:ID>{_id(902)}</r:ID>"
        "<r:Version>1</r:Version><r:Alias>Answer</r:Alias></r:OutParameter>"
        "<r:Binding><r:SourceParameterReference><r:Agency>int.example</r:Agency>"
        f"<r:ID>{_id(902)}</r:ID><r:Version>1</r:Version>"
        "<r:TypeOfObject>OutParameter</r:TypeOfObject></r:SourceParameterReference>"
        "<r:TargetParameterReference><r:Agency>int.example</r:Agency>"
        f"<r:ID>{_id(901)}</r:ID><r:Version>1</r:Version>"
        "<r:TypeOfObject>InParameter</r:TypeOfObject></r:TargetParameterReference>"
        f"</r:Binding>{body}</d:{tag}>"
    )


@pytest.mark.parametrize(
    ("cls", "body"),
    [
        (
            IfThenElse,
            "<d:IfCondition><r:Command><r:ProgramLanguage>Blaise</r:ProgramLanguage>"
            "<r:CommandContent>Count &gt; 0</r:CommandContent></r:Command>"
            "</d:IfCondition>",
        ),
        (Loop, ""),
        (StatementItem, ""),
        (Sequence, ""),
    ],
)
def test_a_control_construct_types_its_parameters_and_bindings(
    cls: type[IfThenElse | Loop | StatementItem | Sequence], body: str
) -> None:
    source = fromstring(_construct_xml(cls.__name__, body))
    construct = cls.from_xml(source)
    assert [type(value) for value in construct.in_parameters] == [InParameter]
    assert [type(value) for value in construct.out_parameters] == [OutParameter]
    assert [type(value) for value in construct.bindings] == [Binding]
    held = {qn(R, "InParameter"), qn(R, "OutParameter"), qn(R, "Binding")}
    assert not [child for child in construct.other_elements if child.tag in held]

    element = construct.to_xml()
    names = _local_names(element)
    assert names.index("InParameter") < names.index("OutParameter")
    assert names.index("OutParameter") < names.index("Binding")
    assert names.index("ConstructName") < names.index("InParameter")
    parameter = element.find(qn(R, "InParameter"))
    assert parameter is not None and parameter.get("limitArrayIndex") == "1 2"


GENERATED_CONSTRUCTS = [
    ComputationItem,
    QuestionConstruct,
    *(
        getattr(items, name)
        for name in (
            "Split",
            "SplitJoin",
            "RepeatUntil",
            "RepeatWhile",
            "MeasurementItem",
            "MeasurementConstruct",
            "DevelopmentStep",
            "SampleStep",
            "SamplingStage",
        )
    ),
]


def _generated_construct_xml(tag: str) -> str:
    # Name-less, so the same body fits a MeasurementItem (d:MeasurementItemName).
    xml = _construct_xml(tag)
    return xml.replace(
        '<d:ConstructName><r:String xml:lang="en">X</r:String></d:ConstructName>', ""
    )


@pytest.mark.parametrize("cls", GENERATED_CONSTRUCTS, ids=lambda cls: cls.__name__)
def test_a_generated_construct_types_its_parameters_and_bindings(
    cls: type[Any],
) -> None:
    source = fromstring(_generated_construct_xml(cls.__name__))
    construct = cls.from_xml(source)
    assert [type(value) for value in construct.in_parameters] == [InParameter]
    assert [type(value) for value in construct.out_parameters] == [OutParameter]
    assert [type(value) for value in construct.bindings] == [Binding]
    assert tostring(construct.to_xml()) == tostring(source)

    construct.in_parameters[0].alias = "Pets"
    element = construct.to_xml()
    assert element.findtext(f"{{{R}}}InParameter/{{{R}}}Alias") == "Pets"
    for tag in ("OutParameter", "Binding"):
        (written,) = element.findall(qn(R, tag))
        (read,) = source.findall(qn(R, tag))
        assert _without_tail(written) == _without_tail(read)
    assert _local_names(element) == _local_names(source)


def test_an_instruction_types_its_parameters() -> None:
    source = fromstring(
        f'<d:Instruction xmlns:d="{D}" xmlns:r="{R}" isUniversallyUnique="true">'
        f"<r:Agency>int.example</r:Agency><r:ID>{_id(914)}</r:ID>"
        "<r:Version>1</r:Version>"
        + IN_PARAMETER.replace(f' xmlns:r="{R}"', "")
        + '<d:InstructionText><d:LiteralText><d:Text xml:lang="en">Count them.'
        "</d:Text></d:LiteralText></d:InstructionText></d:Instruction>"
    )
    instruction = Instruction.from_xml(source)
    assert [type(value) for value in instruction.in_parameters] == [InParameter]
    assert tostring(instruction.to_xml()) == tostring(source)


def test_a_question_read_from_a_colectica_file_has_typed_parameters() -> None:
    # Byte identity through put() is test_parsed_items_stay_byte_identical.
    fragment = ddi_l.open_fragment(CONDITIONS)
    constructs = [
        item for item in fragment.items() if isinstance(item, QuestionConstruct)
    ]
    assert len(constructs) == 2
    for construct in constructs:
        assert [type(value) for value in construct.out_parameters] == [OutParameter]
        assert [type(value) for value in construct.bindings] == [Binding]


def test_raw_elements_and_typed_values_mix() -> None:
    raw = fromstring(
        f'<r:OutParameter xmlns:r="{R}"><r:Agency>int.example</r:Agency>'
        f"<r:ID>{_id(904)}</r:ID><r:Version>1</r:Version></r:OutParameter>"
    )
    sequence = Sequence(
        agency="int.example",
        identifier=_id(911),
        version="1",
        out_parameters=[OutParameter.from_xml(raw), raw],
    )
    assert len(sequence.to_xml().findall(qn(R, "OutParameter"))) == 2

    # The generated models (ComputationItem, QuestionConstruct...) read typed
    # values and also take a parameter's element, written as it is.
    parameter = InParameter.from_xml(fromstring(IN_PARAMETER))
    computation = ComputationItem(
        agency="int.example",
        identifier=_id(912),
        version="1",
        in_parameters=[parameter.to_xml()],
        out_parameters=[raw],
    )
    element = computation.to_xml()
    assert element.findtext(f"{{{R}}}InParameter/{{{R}}}Alias") == "Count"
    assert element.find(qn(R, "OutParameter")) is not None
    construct = QuestionConstruct(
        agency="int.example", identifier=_id(913), version="1"
    )
    typed: list[Any] = [
        Binding.between(
            OutParameter(agency="int.example", identifier=_id(904), version="1"),
            parameter,
        )
    ]
    construct.bindings = typed
    assert construct.to_xml().find(qn(R, "Binding")) is not None


def test_a_gate_built_with_typed_parameters_validates() -> None:
    fragment = ddi_l.open_fragment(CONDITIONS)
    pet_count = OutParameter(
        agency="int.example", identifier=_id(23), version="1"
    ).to_reference()
    gate_input = InParameter(
        agency="int.example", identifier=_id(920), version="1", alias="Pets"
    )
    gate = IfThenElse(
        agency="int.example",
        identifier=_id(921),
        version="1",
        construct_names=[InternationalString("Has pets", lang="en-CA")],
        in_parameters=[gate_input],
    )
    if_condition = fromstring(
        f'<d:IfCondition xmlns:d="{D}" xmlns:r="{R}"><r:Command>'
        "<r:ProgramLanguage>Blaise</r:ProgramLanguage>"
        "<r:CommandContent>Pets &gt; 0</r:CommandContent></r:Command></d:IfCondition>"
    )
    gate.if_condition = if_condition
    fragment.put(gate)
    survey = fragment.get(_id(70))
    assert isinstance(survey, Sequence)
    survey.bindings.append(Binding.between(pet_count, gate_input, late_bound=True))
    survey.control_construct_references.append(gate.to_reference())
    fragment.put(survey)
    assert fragment.validate() == []
    explanation = explain_condition(fragment, _id(921))
    assert explanation.used_inputs == ("Pets",)


def test_parsed_items_stay_byte_identical() -> None:
    source = CONDITIONS.read_bytes()
    fragment = ddi_l.open_fragment(CONDITIONS)
    for item in list(fragment.items()):
        fragment.put(item)
    assert fragment.to_colectica_bytes() == source


# ---- Review regressions -----------------------------------------------------------

XHTML = "http://www.w3.org/1999/xhtml"


def test_an_unchanged_parameter_keeps_mixed_content_whitespace() -> None:
    # The space between two inline XHTML elements is text, not indentation.
    # The gate's PetKind input (the first PetKind aliases are its question's).
    text = CONDITIONS.read_text(encoding="utf-8")
    alias = "<r:Alias>PetKind</r:Alias>"
    at = text.index(alias, text.index("<IfThenElse"))
    description = (
        '\n      <r:Description>\n        <r:Content xml:lang="en-CA">Kind '
        f'<b xmlns="{XHTML}">of</b> <i xmlns="{XHTML}">pet</i></r:Content>'
        "\n      </r:Description>"
    )
    end = at + len(alias)
    marked = (text[:end] + description + text[end:]).encode()
    fragment = ddi_l.read_ddi(marked)
    assert isinstance(fragment, ddi_l.DDIFragment)
    as_read = fragment.to_colectica_bytes()
    for item in list(fragment.items()):
        fragment.put(item)
    assert fragment.to_colectica_bytes() == as_read
    assert b"of</b> <i" in as_read


def test_inline_xhtml_that_starts_with_an_element_keeps_its_space() -> None:
    # colectica.md, Layout: with no text before the first element, the space
    # between inline elements is still text, on both backends.
    text = CONDITIONS.read_text(encoding="utf-8")
    alias = "<r:Alias>PetKind</r:Alias>"
    end = text.index(alias, text.index("<IfThenElse")) + len(alias)
    content = f'<b xmlns="{XHTML}">Kind</b> <i xmlns="{XHTML}">of pet</i>'
    description = (
        "\n      <r:Description>\n        "
        f'<r:Content xml:lang="en-CA">{content}</r:Content>'
        "\n      </r:Description>"
    )
    fragment = ddi_l.read_ddi((text[:end] + description + text[end:]).encode())
    assert isinstance(fragment, ddi_l.DDIFragment)
    written = fragment.to_colectica_bytes()
    assert content.encode() in written
    for item in list(fragment.items()):
        fragment.put(item)
    assert fragment.to_colectica_bytes() == written


def test_an_edited_parameter_keeps_a_marked_up_description() -> None:
    source = fromstring(
        f'<r:OutParameter xmlns:r="{R}" xmlns:x="{XHTML}">'
        f"<r:Agency>int.example</r:Agency><r:ID>{_id(902)}</r:ID>"
        "<r:Version>1</r:Version><r:Alias>A</r:Alias>"
        '<r:Description><r:Content xml:lang="en">Desc <x:b>bold</x:b> tail'
        "</r:Content></r:Description></r:OutParameter>"
    )
    parameter = OutParameter.from_xml(source)
    # The text is the whole string; the markup is written back while unchanged.
    assert [(d.text, d.lang) for d in parameter.descriptions] == [
        ("Desc bold tail", "en")
    ]
    parameter.alias = "B"
    content = parameter.to_xml().find(f"{{{R}}}Description/{{{R}}}Content")
    assert content is not None and content.text == "Desc "
    (bold,) = list(content)
    assert (bold.text, bold.tail) == ("bold", " tail")
    # Editing descriptions writes them; clearing them removes the description.
    parameter.descriptions = [InternationalString("Plain", lang="en")]
    descriptions = parameter.to_xml().findall(qn(R, "Description"))
    assert [d.findtext(qn(R, "Content")) for d in descriptions] == ["Plain"]
    parameter.descriptions = []
    assert parameter.to_xml().find(qn(R, "Description")) is None


def test_a_marked_up_language_leaves_its_siblings_visible() -> None:
    parameter = OutParameter.from_xml(
        fromstring(
            f'<r:OutParameter xmlns:r="{R}" xmlns:x="{XHTML}">'
            f"<r:Agency>int.example</r:Agency><r:ID>{_id(902)}</r:ID>"
            "<r:Version>1</r:Version><r:Description>"
            '<r:Content xml:lang="en">Plain English</r:Content>'
            '<r:Content xml:lang="fr">Du <x:b>gras</x:b></r:Content>'
            "</r:Description></r:OutParameter>"
        )
    )
    assert [d.lang for d in parameter.descriptions] == ["en", "fr"]
    parameter.descriptions[0].text = "Plain English, edited"
    contents = parameter.to_xml().findall(f"{{{R}}}Description/{{{R}}}Content")
    assert [c.text for c in contents] == ["Plain English, edited", "Du "]
    assert [len(c) for c in contents] == [0, 1]


@pytest.mark.parametrize(
    ("lexical", "value"), [(" true ", True), ("1", True), ("0", False)]
)
def test_is_array_reads_every_boolean_spelling_and_keeps_it(
    lexical: str, value: bool
) -> None:
    parameter = InParameter.from_xml(
        fromstring(IN_PARAMETER.replace('isArray="true"', f'isArray="{lexical}"'))
    )
    assert parameter.is_array is value
    parameter.alias = "Pets"
    assert parameter.to_xml().get("isArray") == lexical
    parameter.is_array = not value
    assert parameter.to_xml().get("isArray") == ("false" if value else "true")


def test_an_empty_default_value_survives_an_edit() -> None:
    parameter = InParameter.from_xml(
        fromstring(
            IN_PARAMETER.replace(
                "<r:DefaultValue>0</r:DefaultValue>",
                '<r:DefaultValue xml:space="preserve"></r:DefaultValue>',
            )
        )
    )
    assert parameter.default_value == ""
    parameter.alias = "Pets"
    default = parameter.to_xml().find(qn(R, "DefaultValue"))
    assert default is not None
    assert default.get("{http://www.w3.org/XML/1998/namespace}space") == "preserve"


def test_a_reference_to_a_parameter_gets_no_generated_urn() -> None:
    from ddi_l.models.datacollection._monolith import _maybe_generate_reference_urn

    to_parameter = Reference(
        type_of_object="OutParameter",
        agency="int.example",
        identifier="q1-out",
        version="1",
    )
    assert _maybe_generate_reference_urn(to_parameter) is None
    assert to_parameter.urn is None
    # A reference to an item named in code is given the item's generated ID.
    to_item = Reference(
        type_of_object="QuestionItem",
        agency="int.example",
        identifier="q1",
        version="1",
    )
    _maybe_generate_reference_urn(to_item)
    assert to_item.urn is not None and ":q1:" not in to_item.urn


@pytest.mark.parametrize(
    ("lexical", "value", "written"), [("yes", False, "false"), ("TRUE", True, "true")]
)
def test_an_invalid_is_array_spelling_is_not_written_back(
    lexical: str, value: bool, written: str
) -> None:
    parameter = InParameter.from_xml(
        fromstring(IN_PARAMETER.replace('isArray="true"', f'isArray="{lexical}"'))
    )
    assert parameter.is_array is value
    parameter.alias = "Pets"
    assert parameter.to_xml().get("isArray") == written


def test_whitespace_between_xhtml_blocks_is_layout() -> None:
    from ddi_l.models.base import _without_indentation

    blocks = fromstring(
        f'<r:Content xmlns:r="{R}" xmlns:x="{XHTML}">\n  <x:p>a</x:p>\n  '
        "<x:p>b</x:p>\n</r:Content>"
    )
    _without_indentation(blocks)
    assert blocks.text is None and all(p.tail is None for p in blocks)
    inline = fromstring(
        f'<r:Content xmlns:r="{R}" xmlns:x="{XHTML}"><x:b>a</x:b> <x:i>b</x:i>'
        "</r:Content>"
    )
    _without_indentation(inline)
    assert inline[0].tail == " "


def test_a_parameter_has_one_description_whatever_its_strings() -> None:
    parameter = InParameter(
        agency="int.example",
        identifier=_id(905),
        version="1",
        alias="Count",
        descriptions=[
            InternationalString("How many pets.", lang="en"),
            InternationalString("Number of pets.", lang="en"),
            InternationalString("Combien d'animaux.", lang="fr"),
        ],
    )
    (description,) = parameter.to_xml().findall(qn(R, "Description"))
    assert [c.text for c in description] == [
        "How many pets.",
        "Number of pets.",
        "Combien d'animaux.",
    ]
