---
description: >-
  Les profils d'espaces de noms DDI 3.x et les liaisons de préfixes de
  ddi_l.namespaces, et leur application à l'écriture du XML.
---

# Profils et liaisons d'espaces de noms

Le module `ddi_l.namespaces` centralise les liaisons d'espaces de noms présentes dans les documents d'instances DDI 3.x. Les profils exposent des ensembles de paires préfixe/URI pour les modules de maintainables courants afin que les outils en aval appliquent des liaisons cohérentes, qu'ils reposent sur l'implémentation XML de la bibliothèque standard ou sur lxml. Les liaisons par défaut ciblent la version 3.3 fournie, tandis que les assistants de `ddi_l.schema_loader` exposent des cartes d'espaces de noms pour 3.1 et 3.2 lorsque vous devez traiter du contenu patrimonial.

## Profils intégrés

| Constante de profil | Préfixes inclus |
| ------------------- | ---------------- |
| `DDI_DEFAULT_PROFILE` | Espace de noms par défaut (``ddi:instance:3_3``), module réutilisable (`r`), XML Schema Instance (`xsi`) |
| `DDI_REUSABLE_PROFILE` | Module réutilisable (`r`) |
| `DDI_STUDY_UNIT_PROFILE` | Study Unit (`s`) et Conceptual Component (`c`) |
| `DDI_DATA_COLLECTION_PROFILE` | Data Collection (`d`) |
| `DDI_LOGICAL_PRODUCT_PROFILE` | Logical Product (`l`) |
| `DDI_PHYSICAL_DATA_PROFILE` | Physical Data Product (`p`) |
| `DDI_ARCHIVE_PROFILE` | Archive (`a`) |
| `DDI_CONCEPTUAL_COMPONENT_PROFILE` | Conceptual Component (`cc`) |
| `DDI_COMPARATIVE_PROFILE` | Comparative (`cmp`) |
| `DDI_PROFILE_PROFILE` | Métadonnées de profil (`pr`) |

Les profils sont regroupés dans le mapping `NAMESPACE_PROFILES` et peuvent être récupérés avec `get_namespace_profile(name)` lorsque vous devez inspecter les liaisons brutes.

## Fusionner des profils

Utilisez `merge_namespace_profiles` pour combiner des profils nommés avec des surcharges ponctuelles. Les liaisons conflictuelles lèvent une `ValueError` par défaut afin de détecter rapidement toute réaffectation accidentelle. Passez `allow_override=True` ou fournissez le mapping `overrides` lorsque vous souhaitez explicitement que les valeurs les plus récentes remplacent les précédentes.

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

Le dictionnaire retourné peut être transmis directement aux constructeurs XML ou enregistré dans des registres d'espaces de noms globaux lorsque vous utilisez la bibliothèque standard.

## Appliquer des profils aux documents

`DDIDocument.ensure_namespace_prefixes` accepte **un** profil (ou un mapping préfixe/URI), auquel s'ajoutent des liaisons ponctuelles passées par le paramètre nommé `extra_namespaces`. La méthode normalise les déclarations d'espaces de noms afin que le XML généré contienne des préfixes cohérents, que lxml soit installé ou non.

```python
import ddi_l as ddi
from ddi_l.namespaces import DDI_STUDY_UNIT_PROFILE

doc = ddi.new_study(title="Demo", agency="example.agency")
doc.inner.ensure_namespace_prefixes(
    DDI_STUDY_UNIT_PROFILE,
    extra_namespaces={"custom": "http://example.com/ns"},
)
```

Pour appliquer plusieurs profils, fusionnez-les d'abord : `merge_namespace_profiles` renvoie un mapping, qui fait partie de ce que la méthode accepte.

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

`extra_namespaces` est appliqué en dernier : les appelants peuvent donc écraser volontairement les liaisons du profil. Les contrôles de conflit (`allow_override`, `overrides`) appartiennent à `merge_namespace_profiles`, pas à cette méthode. Faites la fusion, et son `ValueError` se déclenche avant que le document ne soit touché.

## Utilisation avec lxml et la bibliothèque standard

Les assistants de gestion d'espaces de noms masquent les différences entre les backends stdlib et lxml. Lorsque lxml est disponible, les profils sont fusionnés dans l'attribut `nsmap` de l'élément puis resérialisés via `cleanup_namespaces`. Si seule la bibliothèque standard est présente, les mêmes liaisons sont enregistrées auprès de `xml.etree.ElementTree` afin que le document sérialisé inclue malgré tout les déclarations demandées. Ce module d'assistance garantit ainsi une sortie cohérente quels que soient les environnements.
