# From XML to objects

This tutorial shows how to move between raw DDI XML and the `ddi-l` Python
objects. It covers opening XML files, exploring their contents, and working
with the model layer for fine-grained control.

## 1. Open a DDI file with the simple API

The easiest way to work with existing DDI XML is `ddi.open_ddi()`:

```python
import ddi_l as ddi

doc = ddi.open_ddi("my-study.xml")

print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
print(f"Concepts: {len(doc.concepts)}")

for v in doc.variables:
    print(f"  Variable: {v.identifier}")
```

The `Document` object gives you access to all items through typed properties
and the generic `items()` method.

## 2. Open with the advanced layer

For full control, use `DDIDocument.from_xml()`:

```python
from ddi_l.document import DDIDocument

instance = DDIDocument.from_xml("my-study.xml", validate=True)
print(instance.get_identification())
```

`DDIDocument` gives you access to the raw XML tree and all the model
objects parsed from it.

## 3. Work with model objects

Model objects are thin dataclasses. Each one supports `from_xml()` and
`to_xml()`:

```python
from ddi_l.models.logicalproduct import Variable

# Get a variable from the document
var = doc.variables[0]
print(var.agency, var.identifier, var.version)

# Convert to XML element
xml_element = var.to_xml()
```

## 4. Round-trip XML

You can parse, modify, and re-serialize without losing content:

```python
doc = ddi.open_ddi("my-study.xml")
doc.add_question(text="New question")
doc.save("my-study-updated.xml")
```

Unknown XML elements are preserved in the `other_elements` list, so
round-tripping does not drop content the library does not model.

## 5. CLI round-trip

The CLI also supports round-tripping:

```bash
ddi roundtrip my-study.xml my-study-roundtrip.xml --validate
```

## Next steps

- [User guide](../user-guide.md) for the full CRUD API reference.
- [Models reference](../models.md) for all available model types.
