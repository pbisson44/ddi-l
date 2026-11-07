---
description: >-
  La couche de modèles de ddi-l : des dataclasses générées pour les types
  DDI 3.3, quand l'API Document ne suffit pas.
---

# Référence des modèles (couche avancée)

Le paquet `ddi_l.models` fournit des dataclasses générées pour les types
DDI 3.3. C'est la **couche avancée**. La plupart des utilisateurs devraient
commencer avec l'[API CRUD simple](user-guide.fr.md).

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

## Paramètres et liaisons

Une construction transmet des valeurs par des paramètres : l'`OutParameter`
d'une construction de question porte sa réponse, et une condition (un
`IfThenElse`, un `Loop`) teste ses `InParameter`. Un `Binding` sur la séquence
qui contient les deux relie l'un à l'autre.

```python
from ddi_l.models import Binding, InParameter, OutParameter

answer = OutParameter(
    agency="example.org", identifier="q1-out", version="1", alias="Q1"
)
gate_input = InParameter(
    agency="example.org", identifier="gate-in", version="1", alias="Q1"
)
binding = Binding.between(answer, gate_input, late_bound=True)

reference = binding.target_parameter_reference
print(reference.type_of_object, reference.identifier)
```

`IfThenElse`, `Loop`, `StatementItem` et `Sequence` gardent les leurs dans
`in_parameters`, `out_parameters` et `bindings`, lus d'un fichier sous ces
types, comme les modèles générés qui en ont (`ComputationItem`,
`QuestionConstruct`, `Split`, `RepeatUntil`, ..., et les `in_parameters` d'une
`Instruction`). Ces listes acceptent aussi un élément brut, écrit tel quel. Le
`to_reference()` d'un paramètre et les références que construit
`Binding.between()` n'ont pas d'`r:URN`, comme Colectica les écrit ;
`late_bound=True` les marque `lateBound="true"`, pour qu'elles suivent la
dernière version du paramètre.

## Modèles générés

Les classes sous `ddi_l.models._generated/` sont générées automatiquement
à partir des fichiers XSD DDI 3.3. Ne les éditez pas manuellement. Pour
régénérer :

```bash
python -m codegen.generate_model_bases
```

Consultez le [guide de développement](DEVELOPMENT.fr.md) pour plus de détails sur
le pipeline de génération.
