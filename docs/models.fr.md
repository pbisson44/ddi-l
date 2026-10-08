# Référence des modèles (couche avancée)

Le paquet `ddi_l.models` fournit des dataclasses générées pour les types
DDI 3.3. C'est la **couche avancée**. La plupart des utilisateurs devraient
commencer avec l'[API CRUD simple](user-guide.md).

!!! info "Quand utiliser la couche modèles"
    Utilisez les classes de modèles directement lorsque vous avez besoin d'un
    contrôle fin sur des structures DDI que l'API simple n'expose pas, comme les
    représentations personnalisées, les hiérarchies de classification ou les
    produits de données physiques.

## Principaux paquets de modèles

| Paquet | Module DDI | Types exemples |
| --- | --- | --- |
| `ddi_l.models.base` | Reusable | `InternationalString`, `Reference`, `MaintainableBase` |
| `ddi_l.models.logicalproduct` | LogicalProduct | `Variable`, `CodeList`, `Category`, `RepresentedVariable` |
| `ddi_l.models.datacollection` | DataCollection | `QuestionItem`, `Instrument`, `CollectionEvent` |
| `ddi_l.models.conceptualcomponent` | ConceptualComponent | `Concept`, `Universe`, `ConceptualVariable`, `UnitType` |
| `ddi_l.models.study` | StudyUnit | `StudyUnit` |
| `ddi_l.models.archive` | Archive | `Archive`, `Organization` |
| `ddi_l.models.physical` | PhysicalDataProduct | `PhysicalStructure`, `PhysicalInstance` |
| `ddi_l.models.methodology` | Methodology | `Methodology`, `MethodologyItem`, `MethodologyScheme` |

## Créer des objets modèles

```python
from ddi_l.models.base import InternationalString
from ddi_l.models.logicalproduct import Variable

var = Variable(
    agency="example.org",
    identifier="var-age",
    version="1.0",
    names=[InternationalString(text="Age", lang="en")],
)
```

## Aller-retour XML

Chaque classe de modèle supporte `from_xml()` et `to_xml()` :

```python
import ddi_l as ddi
from ddi_l.models.logicalproduct import Variable

# ddi.read_ddi() fonctionne avec les deux backends XML : cet exemple ne dépend
# donc pas de la présence de lxml.
doc = ddi.read_ddi("study.xml")
xml_element = doc.root.find(".//{ddi:logicalproduct:3_3}Variable")
var = Variable.from_xml(xml_element)
new_element = var.to_xml()
```

Le contenu XML inconnu est préservé dans la liste `other_elements` pour que
les allers-retours ne perdent pas d'information.

## Références

Utilisez `Reference` pour lier des objets modèles entre eux :

```python
from ddi_l.models.base import Reference

ref = Reference(
    agency="example.org",
    identifier="var-age",
    version="1.0",
    type_of_object="Variable",
)
```

## Modèles générés

Les classes sous `ddi_l.models._generated/` sont générées automatiquement
à partir des fichiers XSD DDI 3.3. Ne les éditez pas manuellement. Pour
régénérer :

```bash
python -m codegen.generate_model_bases
```

Consultez le [guide du contributeur](DEVELOPMENT.md) pour plus de détails sur
le pipeline de génération.
