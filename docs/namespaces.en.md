---
description: >-
  DDI 3.x namespace profiles and prefix bindings in ddi_l.namespaces, and
  how ddi-l applies them when it writes XML.
---

# Namespace profiles and bindings

The `ddi_l.namespaces` module centralizes the namespace bindings that appear
throughout DDI 3.x instance documents. Profiles expose curated collections of
prefix/URI pairs for common maintainable modules so downstream tooling can apply
consistent bindings regardless of whether they rely on the stdlib or lxml XML
backends. The default bindings target the bundled 3.3 release, while helpers in
`ddi_l.schema_loader` expose namespace maps for 3.1 and 3.2 when legacy
content needs to be processed.

## Built-in profiles

| Profile constant | Included prefixes |
| ---------------- | ----------------- |
| `DDI_DEFAULT_PROFILE` | Default namespace (``ddi:instance:3_3``), reusable (`r`), XML Schema Instance (`xsi`) |
| `DDI_REUSABLE_PROFILE` | Reusable (`r`) |
| `DDI_STUDY_UNIT_PROFILE` | Study Unit (`s`) and Conceptual Component (`c`) |
| `DDI_DATA_COLLECTION_PROFILE` | Data Collection (`d`) |
| `DDI_LOGICAL_PRODUCT_PROFILE` | Logical Product (`l`) |
| `DDI_PHYSICAL_DATA_PROFILE` | Physical Data Product (`p`) |
| `DDI_ARCHIVE_PROFILE` | Archive (`a`) |
| `DDI_CONCEPTUAL_COMPONENT_PROFILE` | Conceptual Component (`cc`) |
| `DDI_COMPARATIVE_PROFILE` | Comparative (`cmp`) |
| `DDI_PROFILE_PROFILE` | Profile metadata (`pr`) |

Profiles live in the `NAMESPACE_PROFILES` mapping and can be retrieved with
`get_namespace_profile(name)` when you need to inspect the raw bindings.

## Merging profiles

Use `merge_namespace_profiles` to combine named profiles with ad-hoc overrides.
Conflicting bindings raise a `ValueError` by default so accidental rebinding is
caught early.  Pass `allow_override=True` or supply the `overrides` mapping when
you intentionally want later values to replace earlier ones.

```python
from ddi_l.namespaces import (
    DDI_DEFAULT_PROFILE,
    DDI_STUDY_UNIT_PROFILE,
    merge_namespace_profiles,
)

bindings = merge_namespace_profiles(
    DDI_DEFAULT_PROFILE,
    DDI_STUDY_UNIT_PROFILE,
    overrides={"custom": "http://example.com/ns"},
)
```

The returned dictionary can be supplied directly to XML builders or registered
with global namespace registries when using the stdlib backend.

## Applying profiles to documents

`DDIDocument.ensure_namespace_prefixes` takes a single profile (or a
prefix-to-URI mapping) plus optional ad-hoc bindings passed as the keyword-only
`extra_namespaces`.  The method normalizes the namespace declarations so the
resulting XML contains consistent prefixes whether lxml is installed or not.

```python
import ddi_l as ddi
from ddi_l.namespaces import DDI_STUDY_UNIT_PROFILE

doc = ddi.new_study(title="Demo", agency="example.agency")
doc.inner.ensure_namespace_prefixes(
    DDI_STUDY_UNIT_PROFILE,
    extra_namespaces={"custom": "http://example.com/ns"},
)
```

To apply more than one profile, merge them first. `merge_namespace_profiles`
returns a mapping, which is one of the things the method accepts:

```python
from ddi_l.namespaces import (
    DDI_PROFILE_PROFILE,
    DDI_STUDY_UNIT_PROFILE,
    merge_namespace_profiles,
)

doc.inner.ensure_namespace_prefixes(
    merge_namespace_profiles(DDI_PROFILE_PROFILE, DDI_STUDY_UNIT_PROFILE),
    extra_namespaces={"custom": "http://example.com/ns"},
)
```

`extra_namespaces` is applied last, so callers can override the profile's
bindings deliberately.  The conflict-detection controls (`allow_override`,
`overrides`) belong to `merge_namespace_profiles`, not to this method. Do the
merge, and its `ValueError` fires before the document is touched.

## Working with lxml and stdlib

The namespace helpers hide the small differences between the stdlib and lxml
backends.  When lxml is available, the profiles are merged into the element
`nsmap` and round-tripped through `cleanup_namespaces`.  When only the stdlib is
present the same bindings are registered with `xml.etree.ElementTree` so the
serialized document still includes the requested declarations.  The new helper
module therefore ensures consistent output across environments.
