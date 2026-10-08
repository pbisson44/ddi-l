---
description: >-
  Valider des documents DDI avec les schémas 3.1, 3.2 et 3.3 inclus,
  exécuter les règles de lint et lire les résultats en Python ou en CLI.
---

# Valider et analyser le contenu DDI

`ddi-l` vérifie les documents de deux façons : la validation par rapport aux
XSD DDI, et des règles de lint pour les problèmes que le schéma autorise
(libellés manquants, références brisées, règles d'agence).

!!! info "Prérequis"
    - Python 3.11 ou plus récent avec `ddi-l` installé.
    - Accès aux schémas intégrés (installés automatiquement avec le paquet).

## Valider au chargement

Passez `validate=True` lors de l'ouverture d'un document pour exécuter la
validation de schéma immédiatement :

```python
import ddi_l as ddi

doc = ddi.open_ddi("mon-etude.xml", validate=True)
```

Si le document échoue à la validation, une `DDIValidationError` est levée.

## Valider un document existant

Appelez `doc.validate()` sur n'importe quel `Document` pour le vérifier par
rapport au schéma DDI :

```python
doc = ddi.new_study(title="Test", agency="example.org")
doc.add_question(text="Quel age avez-vous ?")

issues = doc.validate()
if issues:
    for issue in issues:
        print(f"[{issue.severity}] {issue.message}")
else:
    print("Le document est valide !")
```

## Validation de haut niveau

Le module `ddi_l.validation` fournit `validate_document()` pour une
validation combinée schéma et lint :

```python
from ddi_l.validation import validate_document

report = validate_document(doc)
print(f"Problemes de schema : {len(report.schema_issues)}")
print(f"Resultats lint : {len(report.lint_findings)}")
```

## Validation au niveau modèle

Les objets modèles individuels peuvent être valides avec leur méthode
`.validate()` :

```python
from ddi_l.models.logicalproduct import Variable
from ddi_l.models.base import InternationalString

var = Variable(
    agency="example.org",
    identifier="var-1",
    version="1.0",
    labels=[InternationalString(text="Age")],
)
var.validate()  # lève ModelValidationError en cas d'échec
```

## Règles lint

Le moteur lint exécute des règles configurables sur les documents :

```python
from ddi_l.document import DDIDocument
from ddi_l.lint import run_lint

doc = DDIDocument.from_xml("mon-etude.xml")
findings = run_lint(doc, rules=["ddi.reference.integrity"])
for f in findings:
    print(f"[{f.severity}] {f.message}")
```

## Validation par CLI

En ligne de commande :

```bash
ddi validate mon-etude.xml             # Validation de schéma
ddi lint mon-etude.xml                 # Vérifications lint
ddi validate *.xml                     # Valider plusieurs fichiers
```

## Types d'erreurs

| Exception | Quand elle est levée |
| --- | --- |
| `DDIValidationError` | La validation de schéma échoue |
| `ModelValidationError` | Un objet modèle échoue aux règles métier |
| `DDIReadError` | L'instance ne peut pas être lue |
| `DDIParseError` | Le XML est mal forme (un `DDIReadError` ; porte la ligne et la colonne) |
| `DDIWriteError` | La sérialisation ne peut pas aboutir |
| `DDIReferenceError` | Une référence ou un identifiant d'étude est introuvable (un `LookupError`) |
| `DuplicateIdentifierError` | Un élément est ajouté avec un identifiant déjà présent (un `ValueError`) |

`Document.save()` émet aussi un `DDIReferenceWarning` lorsqu'une référence de
l'étude pointe vers un élément absent du document. Filtrez-le comme toute
catégorie d'avertissement :

```python
import warnings

from ddi_l import DDIReferenceWarning

warnings.simplefilter("error", DDIReferenceWarning)  # échouer au lieu d'avertir
```
