---
description: >-
  Une référence rapide d'une page de l'API ddi-l et des imports utilisés
  dans le programme de formation.
---

# Aide-mémoire

Cette page est un guide de référence rapide pour le paquet `ddi-l`.
Gardez-la ouverte pendant que vous suivez les modules ou construisez
vos propres projets.

---

## Les bases en 30 secondes

```python
import ddi_l as ddi

doc = ddi.new_study(title="Mon enquete", agency="exemple.org")
q = doc.add_question(text="Quel est votre age ?", label="Question sur l'age")
v = doc.add_variable(name="Age", question=q, label="Age en annees")
doc.save("mon-enquete.xml")
```

Cela suffit pour créer un document DDI valide. Tout ce qui suit ajoute
du détail.

`label=` est optionnel et vaut les quelques caractères : `ddi lint` signale
chaque objet maintenable qui n'en a pas, donc un document écrit sans libellés
arrive en se signalant lui-même. Passez `label_lang=` quand le libellé est dans
une autre langue que le nom.

---

## Créer, ouvrir et enregistrer

| Ce que vous voulez faire | Code |
| -------------------------- | ------ |
| Créer une nouvelle étude | `doc = ddi.new_study(title="...", agency="...")` |
| Ouvrir un fichier existant | `doc = ddi.open_ddi("fichier.xml")` |
| Ouvrir avec validation | `doc = ddi.open_ddi("fichier.xml", validate=True)` |
| Enregistrer sur le disque | `doc.save("fichier.xml")` |
| Valider avant d'enregistrer | `errors = doc.validate()` |

---

## Ajouter des éléments à une étude

```python
# Questions
q = doc.add_question(text="Quel est votre revenu ?")

# Variables (liées à une question)
v = doc.add_variable(name="Revenu", question=q)

# Concepts
c = doc.add_concept(name="Situation economique")

# Univers
u = doc.add_universe(name="Adultes de 18 ans et plus")

# Variables avec concept et univers
v = doc.add_variable(name="Revenu", question=q, concept=c)

# Listes de codes
cl = doc.add_code_list(name="Codes de genre")
```

---

## Types de variables (représentations)

Indiquez quel genre de valeurs une variable contient. Chaque setter renvoie la
variable, donc vous pouvez l'enchaîner après `add_variable` :

```python
doc.add_variable(name="age").set_numeric("Integer", low=0, high=120)
doc.add_variable(name="sex").set_coded(cl)  # valeurs d'une liste de codes
doc.add_variable(name="comment").set_text()  # texte libre
doc.add_variable(name="dob").set_datetime("Date")
```

---

## Compter et lister les éléments

```python
print(len(doc.questions))  # Nombre de questions
print(len(doc.variables))  # Nombre de variables
print(len(doc.concepts))  # Nombre de concepts
print(len(doc.universes))  # Nombre d'univers
print(len(doc.code_lists))  # Nombre de listes de codes

for q in doc.questions:
    print(q.identifier)
```

---

## Chercher, supprimer et ajouter tout type

```python
# Chercher un élément par identifiant
item = doc.find("mon-identifiant")

# Supprimer un élément par identifiant
doc.remove("mon-identifiant")

# Ajouter tout type DDI (Category, Instrument, etc.)
from ddi_l.models.logicalproduct import Category

cat = doc.add_item(Category, name="Homme")

# Lister tous les éléments d'un type
for cat in doc.items(Category):
    print(cat.identifier)
```

---

## Propriétés personnalisées

```python
# Définir une propriété
q.set_property("sensibilite", "haute")

# Lire une propriété
print(q.get_property("sensibilite"))  # "haute"

# Lister toutes les propriétés
print(q.properties)  # {"sensibilite": "haute"}

# Supprimer une propriété
q.remove_property("sensibilite")
```

---

## Champs personnalisés (étendre la norme)

DDI est ouvert : ajoutez des champs propres à l'organisation via les points
d'extension de la norme elle-même ; ils restent dans du DDI valide et font un
aller-retour à l'enregistrement.

```python
from ddi_l.models.base import UserID

# Préfixez vos clés pour qu'elles n'entrent jamais en collision
v.set_property("myorg:retention_policy", "destroy after 7 years")
v.set_property("myorg:source_system", "CRM-2024")

# Adosser un champ à un vocabulaire contrôle (référence l'URN de la liste)
quality = doc.add_code_list(
    name="Quality Flag Codes"
)  # une liste de codes = le vocabulaire
v.set_property("myorg:quality_flag", "validated")  # une valeur du vocabulaire
v.set_property("myorg:quality_flag_codes", quality)  # référence la liste de codes

# Un identifiant externe propre à l'organisation (valeur + type)
v.user_ids.append(UserID(value="CAT-000734", type_of_user_id="InternalCatalogue"))

# Auditer quels éléments portent vos champs personnalisés
tagged = [x for x in doc.variables if any(k.startswith("myorg:") for k in x.properties)]
```

Les champs personnalisés se sérialisent en `r:UserAttributePair` (et `r:UserID`),
ce qui reste du DDI valide. Voir [Module 14](module-14-custom-fields.md).

---

## Versionnage

```python
item = doc.add_variable(name="age")  # ou n'importe quel élément DDI

# Lire la version actuelle
print(item.version)  # "1" : les éléments créés démarrent à "1"

# Définir une version en trois parties si vous voulez majeur/mineur/correctif
item.version = "1.0.0"

# Incrémenter la version
item.increment_major_version()  # 1.0.0 → 2.0.0
item.increment_minor_version()  # 1.0.0 → 1.1.0
item.increment_subversion()  # 1.0.0 → 1.0.1

# Documenter pourquoi vous avez fait un changement
from ddi_l.models.base import VersionRationale, InternationalString

item.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(
                text="Ajout de la question sur le revenu pour la vague 2024"
            )
        ]
    )
)
item.version_responsibility = "Equipe de conception d'enquete"
```

Modifier un élément déjà présent dans le fichier, puis le versionner (voir le Module 15, sections 6 et 7) :

<!-- docs-test: skip -- fragment: `question`, `variable` and `new_code_list` are the reader's own items -->
```python
question.question_texts[0].text = "In a typical week, do you work from home?"
question.increment_subversion()
variable.set_coded(new_code_list)  # passer à une autre liste de codes
variable.increment_major_version()

# Après une augmentation de version, pointer les références vers la nouvelle version
variable.question_references = [
    question.to_reference() if ref.identifier == question.identifier else ref
    for ref in variable.question_references
]
```

---

## Constructions de flux de questionnaire

Le flux du questionnaire (l'ordre des questions et les règles de « saut » ou
de « branchement ») se construit à partir de ces constructions de contrôle :

| Construct | Ce qu'il fait |
| ----------- | --------------- |
| `QuestionConstruct` | Enveloppe une question pour qu'elle entre dans un flux |
| `Sequence` | Exécute les étapes dans l'ordre (étape 1, étape 2, étape 3) |
| `IfThenElse` | Bifurque selon une condition (logique de saut) |
| `StatementItem` | Affiche un message au lieu de poser une question |
| `Instrument` | Le questionnaire complet ; pointe vers la séquence principale |

Vous ajoutez chacune avec `doc.add_item(...)`, et vous les reliez avec
`.to_reference()` :

```python
from ddi_l.models.datacollection import (
    QuestionConstruct,
    Sequence,
    IfThenElse,
    StatementItem,
    Instrument,
)

q = doc.add_question(text="Quel est votre age ?")

# Envelopper une question, puis grouper les constructs en section ordonnée
qc_age = doc.add_item(
    QuestionConstruct, name="Demander l'age", question_reference=q.to_reference()
)
section_a = doc.add_item(
    Sequence, name="Section A", control_construct_references=[qc_age.to_reference()]
)
section_c = doc.add_item(Sequence, name="Section C")

# Branchement : section A si vrai, section C si faux
porte = doc.add_item(IfThenElse, name="Filtre d'age")
porte.then_construct_reference = section_a.to_reference()
porte.else_construct_reference = section_c.to_reference()

# Afficher un message ; tout relier avec un Instrument
doc.add_item(StatementItem, name="Bienvenue a l'enquete")
doc.add_item(Instrument, name="Instrument d'enquete")
```

`Loop` fonctionne de la même façon (`doc.add_item(Loop, name="...")`), avec
sa section répétée définie via `loop.control_construct_reference`. Voir le
[Module 10](module-10-questionnaire-flows.md) pour l'exemple complet.

---

## Fichiers de données (instances physiques)

Un `PhysicalInstance` décrit un vrai fichier de données : où il se trouve et
sa taille. Ajoutez-le comme tout autre élément ; il vit au niveau de l'étude.

```python
from ddi_l.models.physical import PhysicalInstance

pi = doc.add_item(PhysicalInstance, name="2021 Microdata File")
pi.set_data_file("https://example.org/health-2021.csv")  # où est le fichier
pi.set_record_count(15000)  # combien d'enregistrements
```

`name` devient le titre de citation du fichier (une instance physique n'a pas
d'élément Name en DDI).

Pour indiquer *où se trouve chaque variable* dans ce fichier, ajoutez une
disposition d'enregistrements :

```python
rl = doc.add_record_layout()
rl.add_data_item(age.to_reference(), start_position=1, width=2)
rl.add_data_item(income.to_reference(), start_position=3, width=8)
```

Omettez les positions pour un fichier délimité (virgule/tabulation).

Pour mettre à jour plusieurs variables à partir d'un nouveau fichier de données, en versionnant chaque changement, voir le
[Module 15, section 8](module-15-update-and-version.md#8-mettre-a-jour-plusieurs-variables-a-partir-dun-nouveau-fichier-de-donnees).

---

## Enregistrements logiques et cubes

```python
# Un enregistrement logique = quelles variables composent un cas (une ligne)
dr = doc.add_data_relationship()
dr.add_logical_record()  # toutes les variables, le fichier rectangulaire usuel

# Un NCube = données multidimensionnelles (cube) : axes + valeurs mesurées
cube = doc.add_ncube(name="Population par année et région")
cube.add_dimension(year.to_reference())
cube.add_dimension(region.to_reference())
cube.add_measure(population.to_reference())

# Attacher un attribut à une région précise du cube
region = cube.add_coordinate_region()
cube.add_dimension_value(region, rank=1, code_references=[code_2020.to_reference()])
cube.add_attribute(footnote.to_reference(), attachment_region=region)
```

Formes fines pour le physique et les données en ligne :

```python
# Plage numérique avec bornes inclusives et valeurs manquantes
age.set_numeric(
    "Integer",
    low=0,
    high=120,
    low_inclusive=True,
    high_inclusive=False,
    missing_values=["-9", "-8"],
)

# Détails de stockage d'un item dans un fichier à largeur fixe / délimité
layout.add_data_item(
    age.to_reference(),
    start_position=1,
    width=3,
    storage_format="ASCII",
    delimiter="comma",
    decimal_positions=2,
)

# Données en ligne : RecordSet (lignes) ou VariableSet (colonnes)
ds = doc.add_dataset(name="Lignes d'exemple")
ds.set_variable_order([age.to_reference(), sex.to_reference()])
ds.add_record(["42", "M"])
ds.add_variable_item(age.to_reference(), ["42", "37"])  # forme en colonne

# Harmonisation : mappage schéma-à-schéma et mappage de représentation
cmp = doc.add_comparison(name="2020 vers 2021")
cmp.add_managed_item_map(
    [(age_2020.to_reference(), age_2021.to_reference())], type_of_mapped_item="Variable"
)
cmp.add_representation_map(
    codes_2020.to_reference(), codes_2021.to_reference(), recode.to_reference()
)
```

---

## Organiser une étude en groupe

```python
# Envelopper l'étude dans un Group (série d'études / paquet de publication)
doc.add_group()
# Le document reste modifiable ; ceci atteint toujours l'étude groupée
doc.add_variable(name="region")

# Ajouter d'autres études à la série, et relier les items entre elles
vague2 = doc.add_study(title="Vague 2")
# Modifier une étude précise via son curseur (doc.study() cible la primaire)
doc.study(vague2.identifier).add_variable(name="revenu")
cmp = doc.add_comparison(name="2020 vers 2021")
cmp.add_variable_map(age_2020.to_reference(), age_2021.to_reference())
```

---

## Paquets au niveau de l'instance et traduction

```python
# Métadonnées d'archivage propres à l'étude (cycle de vie)
doc.add_archive()

# Métadonnées réutilisables partagées entre études (un ResourcePackage)
doc.add_resource_package()

# Une conservation locale d'une étude déposée (réfère l'étude primaire par défaut)
doc.add_local_holding_package()

# Enregistrer les langues de traduction de l'instance
doc.add_translation_information(
    languages=["en", "fr"], description="Traduit du francais."
)
```

---

## Traçabilité des données (dérivation de variables)

```python
# Variable de collecte, liée à une question
v_age = doc.add_variable(name="age", question=q_age)

# Variable dérivée, liée à ses variable(s) source
from ddi_l.models.base import Reference

v_groupe_age = doc.add_variable(name="groupe_age")
v_groupe_age.source_variable_references = [
    Reference(agency="stats.exemple.org", identifier=v_age.identifier, version="1"),
]

# Dérivation multi-sources
v_imc = doc.add_variable(name="imc")
v_imc.source_variable_references = [
    Reference(agency="stats.exemple.org", identifier=v_taille.identifier, version="1"),
    Reference(agency="stats.exemple.org", identifier=v_poids.identifier, version="1"),
]
```

---

## Couplage de données (combiner des jeux de données)

Couplez des enregistrements de deux sources qui partagent une variable commune
(la *clé de couplage*). Chaque source est sa propre étude dans un groupe, une
`Comparison` enregistre comment les clés se correspondent, et les variables
couplées remontent vers les deux sources.

```python
import ddi_l as ddi
from ddi_l.models.base import Reference

# Source 1 : enquête (l'étude primaire)
doc = ddi.new_study(title="Survey", agency="statcan.gc.ca")
survey_key = doc.add_variable(name="anon_id")
survey_key.set_property("linkage_role", "key")  # étiqueter la clé commune
survey_health = doc.add_variable(name="health_rating")

# Source 2 : registre administratif (une deuxième étude du groupe)
admin = doc.add_study(title="Admin register")
admin_ds = doc.study(admin.identifier)
admin_key = admin_ds.add_variable(name="anon_id")
admin_key.set_property("linkage_role", "key")
admin_visits = admin_ds.add_variable(name="hospital_visits")

# Cartographier les clés ; enregistrer la méthode et la qualité du couplage
cmp = doc.add_comparison(name="Survey-to-Admin Linkage")
match = cmp.correspondence(commonality="Shared anonymized id.", weight=1.0)
cmp.add_variable_map(
    survey_key.to_reference(), admin_key.to_reference(), correspondence=match
)
cmp.set_property("linkage_method", "deterministic")  # ou "probabilistic"
cmp.set_property("match_rate", "0.94")

# Variable couplée : provenance vers LES DEUX sources
linked = doc.add_variable(name="health_by_hospital_use")
linked.source_variable_references = [
    Reference(agency="statcan.gc.ca", identifier=survey_health.identifier, version="1"),
    Reference(agency="statcan.gc.ca", identifier=admin_visits.identifier, version="1"),
]
```

Les `source_variable_references` inter-études émettent un avertissement à
l'enregistrement. C'est attendu pour le couplage. Voir
[Module 12](module-12-data-linkage.md).

---

## Support multilingue

```python
from ddi_l.models.base import InternationalString

# Créer une question en anglais (par défaut)
q = doc.add_question(text="What is your age?", lang="en")

# Ajouter une traduction française
q.question_texts.append(InternationalString(text="Quel est votre age ?", lang="fr"))
```

---

## Lire des données depuis un CSV ou Excel

Fichier d'exemple : [`survey_sample.csv`](survey_sample.csv){ download="survey_sample.csv" }

```python
import csv
import ddi_l as ddi

# Depuis un CSV
with open("survey_sample.csv") as f:
    colonnes = csv.DictReader(f).fieldnames

# Libellés tirés du questionnaire ; les colonnes absentes n'ont pas de question
QUESTIONS = {
    "age": "Quel âge avez-vous ?",
    "gender": "Quel est votre genre ?",
    "income": "Quel a été votre revenu total l'an dernier, avant impôts ?",
    "education_level": "Quel est le plus haut niveau de scolarité que vous avez atteint ?",
}

doc = ddi.new_study(title="Enquete", agency="exemple.org")
for col in colonnes:
    q = doc.add_question(text=QUESTIONS[col], lang="fr") if col in QUESTIONS else None
    doc.add_variable(name=col, question=q)
doc.save("enquete.xml")

# Depuis Excel (nécessite pandas + openpyxl)
import pandas as pd

df = pd.read_excel("enquete.xlsx")
for col in df.columns:
    doc.add_variable(name=col)
```

---

## Commandes CLI

Exécutez ces commandes dans votre terminal.

| Commande | Ce qu'elle fait |
| ---------- | ---------------- |
| `ddi validate fichier.xml` | Vérifier un fichier contre le schéma DDI |
| `ddi lint fichier.xml` | Exécuter des vérifications de bonnes pratiques |
| `ddi to-json fichier.xml` | Convertir du DDI XML en JSON |
| `ddi from-json fichier.json -o fichier.xml` | Convertir du JSON en DDI XML |
| `ddi roundtrip in.xml -o out.xml` | Lire et réécrire (teste la fidélité) |
| `ddi versions fichier.xml` | Afficher les informations de version du fichier |

Le code de sortie `0` signifie succès. Le code de sortie `1` signifie échec.

---

## Tous les chemins d'import

Le tableau ci-dessous liste chaque import dont vous pourriez avoir besoin.
La colonne **Quand vous en avez besoin** vous dit pour quelle tâche
l'import sert.

### Paquet principal

Vous obtenez ceux-ci avec `import ddi_l as ddi`.

| Ce que vous tapez | Ce que cela vous donne |
| ------------------- | ------------------------ |
| `ddi.new_study()` | Créer un nouveau document d'étude DDI |
| `ddi.open_ddi()` | Ouvrir un fichier DDI XML depuis le disque |
| `ddi.Document` | L'objet document (renvoyé par `new_study` et `open_ddi`) |
| `ddi.DDIDocument` | Avancé : instance DDI complète avec indexation |
| `ddi.DDIFragment` | Avancé : un fragment DDI (document partiel) |
| `ddi.read_ddi()` | Avancé : analyser du DDI depuis un fichier, bytes ou chaîne |
| `ddi.write_ddi()` | Avancé : sérialiser du DDI vers un fichier ou bytes |
| `ddi.iter_variables()` | Avancé : parcourir les variables d'un gros fichier |
| `ddi.iter_questions()` | Avancé : parcourir les questions d'un gros fichier |
| `ddi.iterparse_ddi()` | Avancé : analyse en flux à faible mémoire |
| `ddi.__version__` | Le numéro de version installé |

### Types de base : `ddi_l.models.base`

Ce sont les briques utilisées dans tous les types DDI.

```python
from ddi_l.models.base import InternationalString
from ddi_l.models.base import Reference
from ddi_l.models.base import MaintainableBase
from ddi_l.models.base import VersionRationale
from ddi_l.models.base import CodeValue
from ddi_l.models.base import UserID
from ddi_l.models.base import UserAttributePair
```

| Classe | Quand vous en avez besoin |
| -------- | -------------------------- |
| `InternationalString` | Ajouter du texte multilingue aux questions, variables ou concepts |
| `Reference` | Créer un lien d'un élément DDI vers un autre |
| `MaintainableBase` | Classe de base pour tous les éléments DDI (rarement utilisé directement) |
| `VersionRationale` | Documenter pourquoi une version a été modifiée |
| `CodeValue` | Représenter une paire code-valeur |
| `UserID` | Attacher un identifiant défini par l'utilisateur à un élément |
| `UserAttributePair` | Attacher une paire clé-valeur personnalisée à un élément |

### Variables et listes de codes : `ddi_l.models.logicalproduct`

```python
from ddi_l.models.logicalproduct import Variable
from ddi_l.models.logicalproduct import CodeList
from ddi_l.models.logicalproduct import Category
from ddi_l.models.logicalproduct import CodeItem
from ddi_l.models.logicalproduct import RepresentedVariable
from ddi_l.models.logicalproduct import VariableRepresentation
from ddi_l.models.logicalproduct import NumericRepresentation
from ddi_l.models.logicalproduct import CodeRepresentation
from ddi_l.models.logicalproduct import TextRepresentation
from ddi_l.models.logicalproduct import DateTimeRepresentation
from ddi_l.models.logicalproduct import NumberRange
```

| Classe | Quand vous en avez besoin |
| -------- | -------------------------- |
| `Variable` | Travailler directement avec un objet variable |
| `CodeList` | Un ensemble de réponses permises (p. ex. codes de genre) |
| `Category` | Une réponse dans une liste de codes (p. ex. « Homme ») |
| `CodeItem` | Une paire code-valeur dans une liste de codes |
| `RepresentedVariable` | Une variable avec son type de mesure défini |
| `VariableRepresentation` | Décrire quel type de valeurs une variable contient |
| `NumericRepresentation` | La variable contient des nombres (entier, décimal) |
| `CodeRepresentation` | La variable contient des codes d'une liste de codes |
| `TextRepresentation` | La variable contient du texte libre |
| `DateTimeRepresentation` | La variable contient des dates ou heures |
| `NumberRange` | Définir un intervalle min/max pour une variable numérique |

### Questions et instruments : `ddi_l.models.datacollection`

```python
from ddi_l.models.datacollection import QuestionItem
from ddi_l.models.datacollection import QuestionConstruct
from ddi_l.models.datacollection import Sequence
from ddi_l.models.datacollection import IfThenElse
from ddi_l.models.datacollection import ElseIf
from ddi_l.models.datacollection import StatementItem
from ddi_l.models.datacollection import ComputationItem
from ddi_l.models.datacollection import Instrument
from ddi_l.models.datacollection import CollectionEvent
from ddi_l.models.methodology import Methodology
from ddi_l.models.datacollection import DataCollection
from ddi_l.models.datacollection import GenerationInstruction
from ddi_l.models.datacollection import GeneralInstruction
```

| Classe | Quand vous en avez besoin |
| -------- | -------------------------- |
| `QuestionItem` | Une question d'enquête |
| `QuestionConstruct` | Envelopper une question pour qu'elle puisse apparaître dans un flux |
| `Sequence` | Exécuter des constructs dans l'ordre (étape 1, étape 2, étape 3) |
| `IfThenElse` | Sauter ou bifurquer selon une condition |
| `ElseIf` | Ajouter des branches supplémentaires à un `IfThenElse` |
| `StatementItem` | Afficher un message ou une instruction (pas une question) |
| `ComputationItem` | Effectuer un calcul dans le flux |
| `Instrument` | Le questionnaire complet (contient la séquence principale) |
| `CollectionEvent` | Quand et comment les données ont été collectées |
| `Methodology` | Comment l'étude a été conçue |
| `DataCollection` | Conteneur pour toutes les métadonnées de collecte de données |
| `GenerationInstruction` | Instruction pour générer des données |
| `GeneralInstruction` | Texte d'instruction générale |

### Concepts et univers : `ddi_l.models.conceptualcomponent`

```python
from ddi_l.models.conceptualcomponent import Concept
from ddi_l.models.conceptualcomponent import Universe
from ddi_l.models.conceptualcomponent import ConceptualVariable
from ddi_l.models.conceptualcomponent import UnitType
```

| Classe | Quand vous en avez besoin |
| -------- | -------------------------- |
| `Concept` | Un sujet que votre variable mesure (p. ex. « Revenu ») |
| `Universe` | La population que votre étude couvre (p. ex. « Adultes 18+ ») |
| `ConceptualVariable` | Une variable abstraite avant la mesure |
| `UnitType` | Le type de chose mesurée (personne, ménage) |

### Étude : `ddi_l.models.study`

```python
from ddi_l.models.study import StudyUnit
```

| Classe      | Quand vous en avez besoin                                      |
| ----------- | -------------------------------------------------------------- |
| `StudyUnit` | Le conteneur principal pour une étude (titre, agence, contenu) |

### Validation : `ddi_l.validation`

```python
from ddi_l.validation import validate_document
from ddi_l.validation import validate_fragment
from ddi_l.validation import validate_maintainable
from ddi_l.validation import ValidationReport
from ddi_l.validation import ValidationMessage
```

| Classe / Fonction | Quand vous en avez besoin |
| ------------------- | -------------------------- |
| `validate_document()` | Valider un document DDI complet contre le schéma |
| `validate_fragment()` | Valider un fragment DDI |
| `validate_maintainable()` | Valider un seul élément maintainable |
| `ValidationReport` | L'objet résultat de la validation |
| `ValidationMessage` | Une erreur ou un avertissement de la validation |

### Analyse statique : `ddi_l.lint`

```python
from ddi_l.lint import run_lint
from ddi_l.lint import LintFinding
```

| Classe / Fonction | Quand vous en avez besoin |
| ------------------- | -------------------------- |
| `run_lint()` | Exécuter des vérifications de bonnes pratiques sur un document |
| `LintFinding` | Un constat d'une vérification lint |

### Espaces de noms : `ddi_l.namespaces`

```python
from ddi_l.namespaces import DDI_STUDY_UNIT_PROFILE
from ddi_l.namespaces import DDI_DATA_COLLECTION_PROFILE
from ddi_l.namespaces import DDI_LOGICAL_PRODUCT_PROFILE
```

| Constante | Quand vous en avez besoin |
| ----------- | -------------------------- |
| `DDI_STUDY_UNIT_PROFILE` | Liaisons d'espaces de noms pour les documents study-unit |
| `DDI_DATA_COLLECTION_PROFILE` | Liaisons d'espaces de noms pour les documents data-collection |
| `DDI_LOGICAL_PRODUCT_PROFILE` | Liaisons d'espaces de noms pour les documents logical-product |

### Exceptions : `ddi_l.exceptions`

```python
from ddi_l.exceptions import DDIError
from ddi_l.exceptions import DDIParseError
from ddi_l.exceptions import DDIValidationError
from ddi_l.exceptions import DDIReadError
from ddi_l.exceptions import DDIWriteError
```

| Classe | Quand vous en avez besoin |
| -------- | -------------------------- |
| `DDIError` | Attraper toute erreur de `ddi-l` |
| `DDIParseError` | Le XML n'a pas pu être analyse |
| `DDIValidationError` | Le document a échoué à la validation du schéma |
| `DDIReadError` | Le fichier n'a pas pu être lu |
| `DDIWriteError` | Le fichier n'a pas pu être écrit |

---

## Exemples courants

### Construire une étude complète depuis un CSV

```python
import csv
import ddi_l as ddi
from ddi_l.models.logicalproduct import Category

doc = ddi.new_study(title="Enquete menages", agency="stats.exemple.org")
univers = doc.add_universe(name="Tous les menages au Canada")

QUESTIONS = {
    "age": "Quel âge avez-vous ?",
    "gender": "Quel est votre genre ?",
    "income": "Quel a été votre revenu total l'an dernier, avant impôts ?",
    "education_level": "Quel est le plus haut niveau de scolarité que vous avez atteint ?",
}

with open("survey_sample.csv") as f:
    reader = csv.DictReader(f)
    for col in reader.fieldnames:
        q = (
            doc.add_question(text=QUESTIONS[col], lang="fr")
            if col in QUESTIONS
            else None
        )
        concept = doc.add_concept(name=col.replace("_", " ").title())
        doc.add_variable(name=col, question=q, concept=concept)

errors = doc.validate()
if not errors:
    doc.save("enquete-menages.xml")
    print("Enregistre et valide.")
```

### Ouvrir, enrichir, versionner et re-enregistrer

```python
import ddi_l as ddi
from ddi_l.models.base import VersionRationale, InternationalString

doc = ddi.open_ddi("enquete-v1.xml")

q = doc.add_question(text="Quelle est votre adresse courriel ?")
doc.add_variable(name="Courriel", question=q)

study = doc.study_unit
study.increment_minor_version()
study.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Ajout de la question courriel pour la vague 2")
        ]
    )
)
study.version_responsibility = "Equipe d'enquete"

doc.validate()
doc.save("enquete-v2.xml")
```

### Validation par lot depuis la ligne de commande

```bash
for fichier in donnees/*.xml; do
    echo "Verification de $fichier..."
    ddi validate "$fichier" || echo "ECHEC : $fichier"
done
```

---

## Pour en savoir plus

- [Guide d'utilisation](../user-guide.md) : Parcours complet de l'API
- [Guide de validation](../validation.md) : Détails sur le schéma et le linting
- [Recettes CLI](../cli-recipes.md) : Tous les exemples en ligne de commande
- [Référence des modèles](../models.md) : Couche de modèles avancée
- [Modules de formation](index.md) : Programme pas à pas
