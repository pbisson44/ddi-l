#!/usr/bin/env python3
"""Demo 5: Reading and Parsing DDI Documents.

This demo shows how to:
- Parse DDI XML from strings and files
- Navigate document structure
- Extract variables using streaming iteration
- Use UUID4 identifiers and bilingual content (EN + FR-CA)
"""

import os
from pathlib import Path
from uuid import uuid4

from ddi_l.document import DDIDocument
from ddi_l.io import iterparse_ddi, read_ddi, write_ddi
from ddi_l.models import Variable

# Pre-generate UUID4 identifiers for the inline XML sample
_DOC_ID = str(uuid4())
_STUDY_ID = str(uuid4())
_LP_ID = str(uuid4())
_VS_ID = str(uuid4())
_VAR_AGE_ID = str(uuid4())
_VAR_GENDER_ID = str(uuid4())
_VAR_INCOME_ID = str(uuid4())

# Sample DDI XML for parsing — note that StudyUnit uses r:Citation
# (not r:Label) per the DDI 3.3 XSD, and LogicalProduct is nested
# inside the StudyUnit.  All IDs are UUID4.
#
# Each variable has ONE l:VariableName holding both languages, which is how
# DDI expects language variants: r:NameType extends r:InternationalStringType,
# whose documentation says "the language designation goes on the individual
# String". Repeating the Name element itself is for *alternative* names -- that
# is what its isPreferred and context attributes are for -- so a second
# VariableName would claim Age and Âge are different names rather than the same
# name in two languages. The r:Title below already does it the right way.
SAMPLE_DDI_XML = f"""<DDIInstance xmlns="ddi:instance:3_3"
             xmlns:r="ddi:reusable:3_3"
             xmlns:l="ddi:logicalproduct:3_3"
             xmlns:s="ddi:studyunit:3_3">
    <r:Agency>demo.org</r:Agency>
    <r:ID>{_DOC_ID}</r:ID>
    <r:Version>1.0</r:Version>
    <r:Citation>
        <r:Title>
            <r:String xml:lang="en-CA">Sample Survey Study</r:String>
            <r:String xml:lang="fr-CA">Étude d'enquête type</r:String>
        </r:Title>
    </r:Citation>
    <s:StudyUnit>
        <r:Agency>demo.org</r:Agency>
        <r:ID>{_STUDY_ID}</r:ID>
        <r:Version>1.0</r:Version>
        <r:Citation>
            <r:Title>
                <r:String xml:lang="en-CA">Sample Survey Study</r:String>
                <r:String xml:lang="fr-CA">Étude d'enquête type</r:String>
            </r:Title>
        </r:Citation>
        <l:LogicalProduct>
            <r:Agency>demo.org</r:Agency>
            <r:ID>{_LP_ID}</r:ID>
            <r:Version>1.0</r:Version>
            <r:Label>
                <r:Content xml:lang="en-CA">Logical product</r:Content>
                <r:Content xml:lang="fr-CA">Produit logique</r:Content>
            </r:Label>
            <l:VariableScheme>
                <r:Agency>demo.org</r:Agency>
                <r:ID>{_VS_ID}</r:ID>
                <r:Version>1.0</r:Version>
                <r:Label>
                    <r:Content xml:lang="en-CA">Variable scheme</r:Content>
                    <r:Content xml:lang="fr-CA">Schéma de variables</r:Content>
                </r:Label>
                <l:Variable>
                    <r:Agency>demo.org</r:Agency>
                    <r:ID>{_VAR_AGE_ID}</r:ID>
                    <r:Version>1.0</r:Version>
                    <l:VariableName>
                        <r:String xml:lang="en-CA">Age</r:String>
                        <r:String xml:lang="fr-CA">Âge</r:String>
                    </l:VariableName>
                    <r:Label>
                        <r:Content xml:lang="en-CA">Age in years</r:Content>
                    </r:Label>
                    <r:Label>
                        <r:Content xml:lang="fr-CA">Âge en années</r:Content>
                    </r:Label>
                </l:Variable>
                <l:Variable>
                    <r:Agency>demo.org</r:Agency>
                    <r:ID>{_VAR_GENDER_ID}</r:ID>
                    <r:Version>1.0</r:Version>
                    <l:VariableName>
                        <r:String xml:lang="en-CA">Gender</r:String>
                        <r:String xml:lang="fr-CA">Genre</r:String>
                    </l:VariableName>
                    <r:Label>
                        <r:Content xml:lang="en-CA">Gender of respondent</r:Content>
                    </r:Label>
                    <r:Label>
                        <r:Content xml:lang="fr-CA">Genre du répondant</r:Content>
                    </r:Label>
                </l:Variable>
                <l:Variable>
                    <r:Agency>demo.org</r:Agency>
                    <r:ID>{_VAR_INCOME_ID}</r:ID>
                    <r:Version>1.0</r:Version>
                    <l:VariableName>
                        <r:String xml:lang="en-CA">Income</r:String>
                        <r:String xml:lang="fr-CA">Revenu</r:String>
                    </l:VariableName>
                    <r:Label>
                        <r:Content xml:lang="en-CA">Annual household income</r:Content>
                    </r:Label>
                    <r:Label>
                        <r:Content xml:lang="fr-CA">Revenu annuel du ménage</r:Content>
                    </r:Label>
                </l:Variable>
            </l:VariableScheme>
        </l:LogicalProduct>
    </s:StudyUnit>
</DDIInstance>
"""


def _output_dir() -> Path:
    """Return the directory demo artifacts are written to.

    Defaults to ``demo/output/`` so running a demo by hand leaves its result
    next to the script. Tests set ``DDI_DEMO_OUTPUT_DIR`` to a temporary path
    so a test run never modifies tracked files.
    """
    override = os.environ.get("DDI_DEMO_OUTPUT_DIR")
    path = Path(override) if override else Path(__file__).parent / "output"
    path.mkdir(parents=True, exist_ok=True)
    return path


def main():
    """Run the reading demo."""
    print("=" * 60)
    print("Demo 5: Reading and Parsing DDI Documents")
    print("=" * 60)

    # 1. Parse from XML string
    print("\n1. Parsing DDI from XML string...")
    doc = read_ddi(SAMPLE_DDI_XML)

    ident = doc.get_identification()
    print(f"   Agency:     {ident['agency']}")
    print(f"   Identifier: {ident['id']}")
    print(f"   Version:    {ident['version']}")

    # 2. Document structure info
    print("\n2. Document structure:")
    xml_str = doc.to_xml(pretty_print=False)
    print(f"   XML length: {len(xml_str)} characters")

    # 3. Iterate over variables using streaming parser
    print("\n3. Variables found (using iterparse_ddi):")
    variables = list(iterparse_ddi(SAMPLE_DDI_XML, maintainable_types=(Variable,)))
    print(f"   Total variables: {len(variables)}")

    for var in variables:
        names_en = [n.text for n in var.names if n.lang == "en-CA"]
        names_fr = [n.text for n in var.names if n.lang == "fr-CA"]
        label_en = next(
            (lb.text for lb in var.labels if lb.lang == "en-CA"),
            "(no label)",
        )
        en = names_en[0] if names_en else "?"
        fr = names_fr[0] if names_fr else "?"
        print(f"   - {var.identifier[:8]}...: {en} / {fr} - {label_en}")

    # 4. Save parsed document to file
    print("\n4. Saving parsed document...")
    output_dir = _output_dir()
    output_path = output_dir / "demo5_parsed.xml"

    write_ddi(doc, output_path)
    print(f"   Saved to: {output_path}")

    # 5. Re-read the saved file
    print("\n5. Re-reading saved file...")
    doc2 = DDIDocument.from_xml(output_path)
    ident2 = doc2.get_identification()
    print(f"   Re-parsed agency: {ident2['agency']}")
    print(f"   Re-parsed ID: {ident2['id']}")

    # 6. Show variable access patterns
    #
    # Two of the three, to keep the output short -- the third reads the same.
    print("\n6. Variable access patterns (first 2 of 3):")
    for var in variables[:2]:
        print(f"\n   Variable: {var.identifier}")
        print(f"      Agency: {var.agency}")
        print(f"      Version: {var.version}")
        for n in var.names:
            print(f"      Name [{n.lang}]: {n.text}")
        for label in var.labels:
            print(f"      Label [{label.lang}]: {label.text}")

    print("\n" + "=" * 60)
    print("Demo 5 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
