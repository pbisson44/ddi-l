"""Non-maintainable wrappers for DDIInstance-level content."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import INSTANCE_NS, REUSABLE_NS, XML_NS
from .base import (
    InternationalString,
    apply_other_attributes,
    collect_other_attributes,
    qn,
)

__all__ = ["TranslationInformation"]


@dataclass
class TranslationInformation:
    """Wrapper for the DDIInstance ``TranslationInformation`` element.

    Describes which languages are involved in translating the instance and,
    optionally, a human-readable description of the translation. This is not a
    maintainable (it has no agency/identifier/version); it is a single optional
    element on the ``DDIInstance``.

    Attributes:
        languages: ISO language codes carried as ``r:Language`` children.
        description: Optional description of the translation process.
        description_lang: Language tag for ``description``.
        lang: Optional ``xml:lang`` on the element itself.
    """

    languages: list[str] = field(default_factory=list)
    description: str | None = None
    description_lang: str = "en"
    lang: str | None = None
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(INSTANCE_NS, "TranslationInformation")

    @classmethod
    def from_xml(cls, element: Element) -> TranslationInformation:
        if element.tag != cls.TAG:
            raise ValueError("Expected an instance:TranslationInformation element.")
        languages = [
            (child.text or "").strip()
            for child in element.findall(qn(REUSABLE_NS, "Language"))
            if child.text and child.text.strip()
        ]
        description: str | None = None
        description_lang = "en"
        desc_el = element.find(qn(REUSABLE_NS, "Description"))
        if desc_el is not None:
            contents = InternationalString.from_container(desc_el)
            if contents:
                description = contents[0].text
                description_lang = contents[0].lang or "en"
        return cls(
            languages=languages,
            description=description,
            description_lang=description_lang,
            lang=element.get(qn(XML_NS, "lang")),
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.lang:
            element.set(qn(XML_NS, "lang"), self.lang)
        for language in self.languages:
            lang_el = create_element(qn(REUSABLE_NS, "Language"))
            lang_el.text = language
            element.append(lang_el)
        if self.description is not None:
            element.append(
                InternationalString(
                    text=self.description,
                    lang=self.description_lang,
                    child_tag="Content",
                    is_plain_text=True,
                ).to_element(qn(REUSABLE_NS, "Description"))
            )
        apply_other_attributes(element, self.other_attributes)
        return element
