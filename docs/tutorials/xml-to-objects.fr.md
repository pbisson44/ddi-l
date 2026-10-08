---
description: >-
  Passer du XML DDI brut aux objets Python de ddi-l : ouvrir des fichiers,
  explorer leur contenu et utiliser la couche de modèles.
---

# De XML aux objets

Ce tutoriel montre comment passer entre le XML DDI brut et les objets Python
de `ddi-l`.

## 1. Ouvrir un fichier DDI avec l'API simple

```python
import ddi_l as ddi

doc = ddi.open_ddi("mon-etude.xml")

print(f"Questions : {len(doc.questions)}")
print(f"Variables : {len(doc.variables)}")

for v in doc.variables:
    print(f"  Variable : {v.identifier}")
```

## 2. Ouvrir avec la couche avancée

```python
from ddi_l.document import DDIDocument

instance = DDIDocument.from_xml("mon-etude.xml", validate=True)
```

## 3. Travailler avec les objets modèles

```python
var = doc.variables[0]
print(var.agency, var.identifier, var.version)

xml_element = var.to_xml()
```

## 4. Aller-retour XML

```python
doc = ddi.open_ddi("mon-etude.xml")
doc.add_question(text="Nouvelle question")
doc.save("mon-etude-mise-a-jour.xml")
```

## 5. Aller-retour par CLI

```bash
ddi roundtrip mon-etude.xml sortie.xml --validate
```

## Prochaines étapes

- [Guide d'utilisation](../user-guide.md) pour l'API CRUD complète.
- [Référence des modèles](../models.md) pour tous les types disponibles.
