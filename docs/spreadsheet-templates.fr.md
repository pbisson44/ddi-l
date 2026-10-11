---
description: >-
  Télécharger des modèles de tableurs vides et d'exemple pour charger des
  métadonnées DDI en lot : fichiers CSV ou classeur Excel, bilingues, avec
  une étude, son questionnaire, ses variables, ses fichiers de données et des
  propriétés personnalisées.
---

# Modèles de tableurs

Des modèles pour les tableaux décrits dans
[Charger du DDI depuis des tableurs](spreadsheet-import.md). Chacun existe en
classeur Excel (une feuille par tableau, plus une feuille README qui décrit
chaque colonne) et en archive zip de fichiers CSV (un fichier par tableau,
plus `README.txt`).

## Exemple

Une petite enquête bilingue (anglais et français) sur le travail dont tous
les tableaux sont remplis : l'étude avec sa série, son agence et sa
gestionnaire ; des concepts, un univers, un type d'unité et la cascade des
variables ; des listes de codes qui partagent une catégorie « Non déclaré »
et une classification des professions à deux niveaux ; des questions avec
des libellés pour mandataire et pour intervieweur, une instruction, une
grille, un bloc et des modules ; un questionnaire Web avec une séquence, des
conditions imbriquées et une boucle ; des variables en groupes et dans un
fichier de données ; un n-cube ; méthodologie, traitements et qualité ; une
comparaison de concepts entre cycles ; et des propriétés personnalisées.

[:material-microsoft-excel: Classeur d'exemple](downloads/ddi-tables-example.xlsx){ .md-button .md-button--primary download="ddi-tables-example.xlsx" }
[:material-folder-zip: Fichiers CSV d'exemple](downloads/ddi-tables-example.zip){ .md-button download="ddi-tables-example.zip" }

Chargez-le tel quel pour voir ce que devient chaque ligne :

```bash
ddi tables import ddi-tables-example.xlsx -o exemple.xml
ddi tables import ddi-tables-example.zip -o exemple.xml   # le zip se charge tel quel
```

## Vide

Les mêmes tableaux, avec seulement les en-têtes et des colonnes `label`,
`description` et `text` pour l'anglais et le français. Remplissez `agency`
dans `settings`, supprimez les tableaux inutiles et ajoutez vos lignes.

[:material-microsoft-excel: Classeur vide](downloads/ddi-tables-template.xlsx){ .md-button .md-button--primary download="ddi-tables-template.xlsx" }
[:material-folder-zip: Fichiers CSV vides](downloads/ddi-tables-template.zip){ .md-button download="ddi-tables-template.zip" }

## Autres langues

Pour d'autres langues, produisez les tableaux vides avec les colonnes voulues :

```bash
ddi tables template mes-tableaux --lang en --lang fr --lang iu --format xlsx
```

Ou en Python :

```python
from ddi_l.tables import write_table_templates

write_table_templates("mes-tableaux", languages=("fr", "es"))
```

`--format` (ou `layout=`) vaut `csv` pour un dossier de fichiers CSV, `zip`
pour le même dossier compressé, ou `xlsx` pour un classeur.

## Contenu d'un modèle

| Feuille ou fichier | Une ligne par |
| --- | --- |
| `README` | colonne, avec son contenu (classeur seulement ; `README.txt` dans le zip) |
| `settings` | paramètre : `agency`, `version`, `language` |
| `studies` | étude |
| `groups` | groupe d'études |
| `organizations` | organisation |
| `individuals` | personne |
| `concepts` | concept |
| `universes` | univers |
| `unit_types` | type d'unité |
| `conceptual_variables` | variable conceptuelle |
| `represented_variables` | variable représentée |
| `code_lists` | liste de codes |
| `codes` | code |
| `instructions` | instruction |
| `questions` | question |
| `question_texts` | libellé supplémentaire d'une question, par langue et par public |
| `question_grids` | question en grille |
| `question_blocks` | bloc de questions |
| `question_groups` | groupe de questions ou module |
| `instruments` | questionnaire |
| `flow` | étape d'un questionnaire |
| `variables` | variable |
| `variable_groups` | groupe de variables |
| `datasets` | fichier de données |
| `ncubes` | n-cube |
| `methodologies` | méthodologie |
| `processing_events` | traitement |
| `quality_statements` | énoncé de qualité |
| `comparisons` | paire d'éléments comparés |

Chaque cellule des classeurs est au format texte : les codes comme `01`
gardent leur zéro initial. Les fichiers CSV sont en UTF-8 avec indicateur
d'ordre des octets, pour qu'Excel affiche correctement les accents.
