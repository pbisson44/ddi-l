---
description: >-
  Utiliser ddi-l comme base pour des tableaux de bord, des services web, des
  outils en ligne de commande et des pipelines de données.
---

# Construire des outils et applications avec ddi-l

Ce guide est destiné aux développeurs qui souhaitent utiliser `ddi-l` comme
base pour leurs propres produits : tableaux de bord, services web, utilitaires
CLI ou pipelines de données.

!!! info "Prérequis"
    - Python 3.11+ avec `ddi-l` installé.
    - Connaissance du [guide d'utilisation](../user-guide.md).

## Lire et interroger des documents

```python
import ddi_l as ddi

doc = ddi.open_ddi("etude.xml")

for q in doc.questions:
    print(q.identifier)

item = doc.find("un-identifiant")
```

## Créer des documents par programme

```python
doc = ddi.new_study(title="Enquete generee", agency="app.org")

questions = ["Age", "Genre", "Revenu"]
for texte in questions:
    q = doc.add_question(text=f"Quel est votre {texte.lower()} ?")
    doc.add_variable(name=texte, question=q)

doc.save("enquete-generee.xml")
```

## Intégrer la validation

```python
doc = ddi.open_ddi("entree.xml", validate=True)

issues = doc.validate()
if issues:
    for issue in issues:
        print(f"[{issue.severity}] {issue.message}")
```

## Utiliser la couche de modèles avancée

Pour un contrôle fin, utilisez directement les classes de modèles :

```python
from ddi_l.document import DDIDocument
from ddi_l.models.logicalproduct import Variable

instance = DDIDocument.from_xml("study.xml")

# Accéder au XML brut
root = instance.root

# Construire un index pour résoudre les références croisées
index = instance.build_index()
```

## Intégration CLI

```bash
ddi validate *.xml
ddi to-json etude.xml --indent 2
ddi roundtrip entree.xml sortie.xml
```

## Conseils d'architecture

- Utilisez `ddi.new_study()` et `ddi.open_ddi()` pour la plupart des flux de
  travail. Ne descendez vers `DDIDocument` que si vous avez besoin de l'arbre
  XML brut.
- Les méthodes génériques `add_item()` / `items()` couvrent les 30 types
  d'éléments DDI, ce qui permet d'écrire du code indépendant du type.
- Toutes les classes de modèles préservent le XML inconnu dans
  `other_elements` : les allers-retours restent donc sans perte, même pour du
  contenu que la bibliothèque ne modélise pas.
