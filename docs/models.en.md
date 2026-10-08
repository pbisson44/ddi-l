---
description: >-
  The ddi-l model layer: generated dataclasses for DDI 3.3 types, for when
  the Document API is not fine-grained enough.
---

# Models reference (advanced layer)

The `ddi_l.models` package provides generated dataclass wrappers for
DDI 3.3 types. These are the **advanced layer**. Most users should start
with the [simple CRUD API](user-guide.md) instead.

!!! info "When to use the model layer"
    Use the model classes directly when you need fine-grained control over
    DDI structures that the simple API does not expose, such as custom
    representations, classification hierarchies, or physical data products.

## Key model packages

| Package | DDI module | Example types |
| --- | --- | --- |
| `ddi_l.models.base` | Reusable | `InternationalString`, `Reference`, `MaintainableBase` |
| `ddi_l.models.logicalproduct` | LogicalProduct | `Variable`, `CodeList`, `Category`, `RepresentedVariable` |
| `ddi_l.models.datacollection` | DataCollection | `QuestionItem`, `Instrument`, `CollectionEvent` |
| `ddi_l.models.conceptualcomponent` | ConceptualComponent | `Concept`, `Universe`, `ConceptualVariable`, `UnitType` |
| `ddi_l.models.study` | StudyUnit | `StudyUnit` |
| `ddi_l.models.archive` | Archive | `Archive`, `Organization` |
| `ddi_l.models.physical` | PhysicalDataProduct | `PhysicalStructure`, `PhysicalInstance` |
| `ddi_l.models.methodology` | Methodology | `Methodology`, `MethodologyItem`, `MethodologyScheme` |

## Creating model objects

```python
from ddi_l.models.base import InternationalString
from ddi_l.models.logicalproduct import Variable

var = Variable(
    agency="example.org",
    identifier="var-age",
    version="1.0",
    names=[InternationalString(text="Age", lang="en")],
    labels=[InternationalString(text="Age of respondent", lang="en")],
)
```

## XML round-tripping

Every model class supports `from_xml()` and `to_xml()`:

```python
import ddi_l as ddi
from ddi_l.models.logicalproduct import Variable

study = ddi.new_study(title="Demo", agency="example.org")
study.add_variable(name="age")
study.save("study.xml")

# ddi.read_ddi() works on either XML backend, so this snippet does not depend on
# lxml being installed.
doc = ddi.read_ddi("study.xml")
xml_element = doc.root.find(".//{ddi:logicalproduct:3_3}Variable")
var = Variable.from_xml(xml_element)

new_element = var.to_xml()
```

Unknown XML content is preserved in the `other_elements` list so that
round-tripping does not lose information.

## References

Use `Reference` to link model objects:

```python
from ddi_l.models.base import Reference

ref = Reference(
    agency="example.org",
    identifier="var-age",
    version="1.0",
    type_of_object="Variable",
)
```

## Generated models

Model classes under `ddi_l.models._generated/` are auto-generated from
the DDI 3.3 XSD files. Do not edit them by hand. To regenerate:

```bash
python -m codegen.generate_model_bases
```

See the [development guide](DEVELOPMENT.md) for details on the codegen
pipeline.
