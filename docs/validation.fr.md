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

### Déroulement de la validation par schéma

Chaque erreur est signalée, avec le même message et le même chemin quelle que
soit la façon de valider. `schema_loader.validate(..., backend=...)` choisit
la façon pour un appel ; la meilleure disponible est celle par défaut :

- **`native`**, avec le [moteur natif](installation.fr.md#moteurs-xml) : une
  seule passe sur le document le vérifie contre une forme compilée du schéma.
  Un document valide s'arrête là ; xmlschema n'est même pas chargé. Pour
  chaque élément qui peut être fautif, xmlschema vérifie cet élément seul et
  rédige ses erreurs, qui portent aussi la ligne où l'élément commence. Sur
  un export de 9 Mo : 0,09 s s'il est valide, 0,13 s avec une erreur (2,6 s
  au premier appel, qui charge xmlschema).
- **`lxml`**, avec lxml installé : libxml2 confirme vite un document valide ;
  s'il trouve un problème, xmlschema valide de nouveau tout le document pour
  le signaler (6,5 s avec une erreur sur le même export).
- **`python`** : xmlschema valide tout le document.

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

Sans `rules=`, `run_lint()` exécute le profil par défaut,
`DDI_PROFILE_DEFAULT`. `run_profile(doc, nom)` exécute plutôt un profil
nommé ; `ddi lint --list-profiles` les énumère.

| Règle | Gravité | Signale |
| --- | --- | --- |
| `ddi.agency.allowed` | error | Une agence absente, ou hors de la liste autorisée configurée |
| `ddi.citation.present` | error | Une `DDIInstance` sans citation |
| `ddi.citation.title.present` | error | Une citation sans titre |
| `ddi.citation.title.languages` | warning | Un titre de citation auquel manque une langue requise |
| `ddi.maintainable.labels` | warning | Un élément sans `r:Label` |
| `ddi.reference.integrity` | error (warning dans un fragment) | Une référence dont l'élément n'est pas dans le fichier |
| `ddi.reference.version` | warning | Une référence dont l'élément est dans le fichier, mais pas dans la version nommée |
| `ddi.reference.provenance-external` | info | Une référence `BasedOn` ou d'attribut utilisateur vers un élément hors du fichier |
| `colectica.maintainable.labels` | warning | Un élément sans libellé ni nom contenant du texte (profil `colectica-questionnaire` seulement) |

Chaque constat a l'une de trois gravités : `error`, `warning` ou `info`.
`info` signale quelque chose d'utile à savoir qui n'est pas un défaut, et ne
fait jamais échouer `ddi lint`, sauf si vous passez `--fail-severity info`.
Une règle qui produit une autre gravité lève `ValueError`.

Une règle ajoutée avec `register_rule()` rejoint le profil par défaut, sauf si
vous passez `default=False` pour une règle destinée seulement à un profil
nommé. Le profil `colectica-questionnaire` sert aux exports Colectica ; voir
[Travailler avec les exports Colectica](colectica.fr.md#verifier-un-export-avec-lint).
La [référence des règles lint](lint-rules.fr.md) énumère toutes les règles.

## Validation par CLI

En ligne de commande :

```bash
ddi validate mon-etude.xml             # Validation de schéma
ddi lint mon-etude.xml                 # Vérifications lint
ddi lint export.xml --profile colectica-questionnaire
ddi lint mon-etude.xml --fail-severity warning  # Échouer aussi sur les avertissements
ddi validate *.xml                     # Valider plusieurs fichiers
```

`ddi lint` se termine avec un code non nul quand un constat atteint
`--fail-severity` : `error` (par défaut), `warning` ou `info`.

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
