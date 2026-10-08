# Corrigés

Cette page contient les solutions de tous les exercices et quiz du
programme. Utilisez-la pour vérifier votre travail après chaque module.

---

## Module 1 : Qu'est-ce que les métadonnées ?

### Solutions des exercices

**Exercice 1** : Trois choses qu'une nouvelle personne aurait besoin de savoir :

1. Ce que chaque colonne signifie (qu'est-ce que « âge » ? En années ? En mois ?)
2. Qui a été interrogé (des étudiants ? Des adultes ? Tout le monde ?)
3. Quand les données ont été collectées

**Exercice 2** : D'après le site de DDI Alliance : « The Data Documentation
Initiative (DDI) is an international standard for describing data from
the social, behavioral, economic, and health sciences. »

### Réponses au quiz

1. **(B) Des informations sur les données.** Les métadonnées décrivent vos
   données : ce qu'elles contiennent, qui les a collectées et comment.
2. **(C) Sans elle, les gens ne peuvent pas comprendre les données.**
   Sans documentation, personne ne sait ce que les chiffres signifient.
3. **(B) Findable, Accessible, Interopérable, Re-usable.** Ces quatre
   principes guident la façon dont les données devraient être partagées.
   Les métadonnées DDI vous aident à respecter les quatre.
4. **(B) Un outil Python qui crée, lit, modifie et valide des documents
   DDI.** ddi-l gère le XML pour que vous puissiez vous concentrer
   sur vos données.

---

## Module 2 : Préparez votre environnement

### Solutions des exercices

**Exercice 1** : La dernière ligne de la sortie de `pip install` devrait
afficher « Successfully installed ddi-l-... » (la version peut varier).

**Exercice 2** :

```python
import ddi_l as ddi

print(ddi.__version__)
# Output: 0.1.0 (or the current version)
```

**Exercice 3** : Le nombre de commandes varie selon la version. En
général, 4 à 6 commandes sont listées.

### Réponses au quiz

1. **(b) 3.11.** ddi-l nécessite Python 3.11 ou plus récent.
2. **(a) `ddi --help`.** Cela affiche toutes les commandes CLI
   disponibles.
3. **(a) Télécharge et installe le package ddi-l.** pip est le
   gestionnaire de packages de Python.

---

## Module 3 : Créez votre première étude

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")
doc.save("well-being.xml")
print(f"Questions: {len(doc.questions)}")
```

Résultat attendu : `Questions: 3`

**Exercice 2** : Ouvrez `well-being.xml` dans un éditeur de texte.
Cherchez `<r:Content>What is your age?</r:Content>` dans le XML.

**Exercice 3** :

```python
from ddi_l.models.base import InternationalString

q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
doc.save("well-being.xml")
```

Ouvrez le XML. Vous devriez voir à la fois `xml:lang="en"` et
`xml:lang="fr"` pour la première question.

### Réponses au quiz

1. **(B) Un objet Document.** Le Document contient votre étude et tout
   son contenu.
2. **(B) Ajoute une question à l'étude.** La question est stockée dans
   un QuestionScheme dans le module DataCollection.
3. **(C) Écrit le document DDI dans un fichier XML.** Le fichier utilise
   les préfixes d'espace de noms DDI corrects.
4. **(B) Ajouter un InternationalString avec lang="fr".** Les deux
   versions linguistiques sont stockées dans le même élément question.
5. **(B) `len(doc.questions)`.** La propriété `questions` retourne une
   liste.

---

## Module 4 : Variables et questions

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")

doc.add_variable(name="Age", question=q1)
doc.add_variable(name="HealthRating", question=q2)
doc.add_variable(name="SleepHours", question=q3)

print(f"Variables: {len(doc.variables)}")
```

Résultat attendu : `Variables: 3`

**Exercice 2** :

```python
for v in doc.variables:
    print(v.identifier)
```

Chaque identifiant est un UUID comme `a1b2c3d4-...`.

**Exercice 3** : Enregistrez et comparez. Le fichier XML est maintenant
plus gros car il contient les sections QuestionScheme et VariableScheme.

### Réponses au quiz

1. **(a) Lie la variable à cette question.** Cela crée un élément de
   référence DDI.
2. **(a) `doc.variables`.** Retourne une liste de tous les objets
   Variable.
3. **(a) Colonne.** Une variable est comme une colonne dans un tableur.

---

## Module 5 : Concepts et univers

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.new_study(title="Health Survey", agency="health.gc.ca")

q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="What is your weight?")
q3 = doc.add_question(text="How often do you exercise per week?")
q4 = doc.add_question(text="How many fruit servings do you eat per day?")

demo = doc.add_concept(name="Demographics")
activity = doc.add_concept(name="Physical Activity")
nutrition = doc.add_concept(name="Nutrition")

doc.add_universe(name="Adults aged 18+ in Canada")

doc.add_variable(name="Age", question=q1, concept=demo)
doc.add_variable(name="Weight", question=q2, concept=demo)
doc.add_variable(name="ExerciseFrequency", question=q3, concept=activity)
doc.add_variable(name="FruitServings", question=q4, concept=nutrition)

print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
print(f"Concepts: {len(doc.concepts)}")
print(f"Universes: {len(doc.universes)}")
```

Résultat attendu :

```text
Questions: 4
Variables: 4
Concepts: 3
Universes: 1
```

### Réponses au quiz

1. **(a) Une idée abstraite qu'une variable mesure.** Par exemple, « Âge »
   le concept est mesure par « Âge » la variable.
2. **(a) Le groupe de personnes ou de choses étudiées.** Par exemple,
   « Adultes de 18 ans et plus au Canada ».
3. **(a) Passer `concept=` lors de l'appel à `add_variable()`.** Cela
   crée un lien de référence dans le document DDI.

---

## Module 6 : Du CSV/Excel au DDI

### Solutions des exercices

**Exercice 1** :

```python
import csv
import ddi_l as ddi

with open("survey_sample.csv") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames

# La question que chaque colonne enregistre, formulée comme les répondants l'ont lue
QUESTIONS = {
    "age": "Quel âge avez-vous ?",
    "gender": "Quel est votre genre ?",
    "income": "Quel a été votre revenu total l'an dernier, avant impôts ?",
    "education_level": "Quel est le plus haut niveau de scolarité que vous avez atteint ?",
}

doc = ddi.new_study(title="Household Survey", agency="research.org")
for col in columns:
    libelle = QUESTIONS.get(col)
    # Une colonne qu'on n'a demandée à personne, comme respondent_id, n'a pas de question
    q = doc.add_question(text=libelle, lang="fr") if libelle else None
    doc.add_variable(name=col, question=q)

doc.save("household-survey.xml")
print(f"Variables: {len(doc.variables)}")
```

Résultat attendu : `Variables: 5`

**Exercice 2** (pandas) :

```python
import pandas as pd
import ddi_l as ddi

df = pd.read_csv("survey_sample.csv")
doc = ddi.new_study(title="Household Survey", agency="research.org")
for col in df.columns:
    doc.add_variable(name=col)
doc.save("household-survey-pandas.xml")
print(f"Variables: {len(doc.variables)}")
```

Résultat attendu : `Variables: 5`

**Exercice 3** (enrichi) :

```python
doc.add_concept(name="Demographics")
doc.add_concept(name="Socioeconomic Status")
doc.add_universe(name="Canadian households")
issues = doc.validate()
print(f"Valid: {not issues}")
doc.save("household-survey-enriched.xml")
```

### Réponses au quiz

1. **(a) Une liste de noms de colonnes.** `reader.fieldnames` vous donne
   la ligne d'en-tête du CSV.
2. **(b) `df.columns`.** Cela retourne les noms de colonnes du
   DataFrame.
3. **(a) Un fichier DDI XML avec une variable par colonne.** Le script
   lit les noms de colonnes et crée des métadonnées DDI.
4. **(a) Parce que les noms de colonnes seuls ne sont pas des métadonnées
   utiles.** Les concepts, les univers et les listes de codes ajoutent
   du sens.

---

## Module 7 : Listes de codes

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi
from ddi_l.models.logicalproduct import Category

doc = ddi.new_study(title="Census", agency="statcan.gc.ca")

doc.add_code_list(name="Gender Codes")
doc.add_item(Category, name="Male")
doc.add_item(Category, name="Female")
doc.add_item(Category, name="Other")

doc.add_code_list(name="Employment Status")
doc.add_item(Category, name="Employed")
doc.add_item(Category, name="Unemployed")
doc.add_item(Category, name="Retired")
doc.add_item(Category, name="Student")

doc.add_code_list(name="Housing Type")
doc.add_item(Category, name="House")
doc.add_item(Category, name="Apartment")
doc.add_item(Category, name="Other")

print(f"Code lists: {len(doc.code_lists)}")
print(f"Categories: {len(doc.items(Category))}")
```

Résultat attendu :

```text
Code lists: 3
Categories: 10
```

**Exercice 2** :

```python
for cat in doc.items(Category):
    print(cat.identifier)
```

**Exercice 3** :

```python
from ddi_l.models.datacollection import Instrument

doc.add_item(Instrument, name="Census Form")
```

### Réponses au quiz

1. **(b) Un ensemble de choix de réponses prédéfinis.** Comme
   « Male / Female / Other » pour le genre.
2. **(b) `doc.add_item(Category, name="...")`.** La méthode `add_item`
   fonctionne pour tout type DDI.
3. **(c) `doc.items(Category)`.** Retourne toutes les catégories du
   document.
4. **(c) Elles rendent les réponses cohérentes entre les enquêtes.** Tout
   le monde utilise les mêmes codes.

---

## Module 8 : Flux de questionnaire

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")
q_age = doc.add_question(text="What is your age?")
q_gender = doc.add_question(text="What is your gender?")
q_employed = doc.add_question(text="Are you currently employed?")
q_occupation = doc.add_question(text="What is your occupation?")
q_health = doc.add_question(text="How would you rate your general health?")
q_smoke = doc.add_question(text="Do you smoke?")
print(f"Questions: {len(doc.questions)}")
```

Résultat : `Questions: 6`

**Exercice 2** :

```python
from ddi_l.models.datacollection import QuestionConstruct, Sequence

for q in doc.questions:
    doc.add_item(QuestionConstruct, name="Ask", question_reference=q.to_reference())

doc.add_item(Sequence, name="Section A - Demographics")
doc.add_item(Sequence, name="Section B - Employment")
doc.add_item(Sequence, name="Section C - Health")

print(f"QuestionConstructs: {len(doc.items(QuestionConstruct))}")
print(f"Sequences: {len(doc.items(Sequence))}")
```

Résultat :

```text
QuestionConstructs: 6
Sequences: 3
```

**Exercice 3** :

```python
from ddi_l.models.datacollection import IfThenElse

doc.add_item(IfThenElse, name="Age gate for employment")
doc.add_item(IfThenElse, name="Occupation routing")
print(f"IfThenElse: {len(doc.items(IfThenElse))}")
```

Résultat : `IfThenElse: 2`

**Exercice 4** :

```python
from ddi_l.models.datacollection import StatementItem, Instrument

doc.add_item(Sequence, name="Main Survey Flow")
doc.add_item(StatementItem, name="Welcome")
doc.add_item(Instrument, name="Health Survey Instrument")

print(f"Sequences: {len(doc.items(Sequence))}")
print(f"StatementItems: {len(doc.items(StatementItem))}")
print(f"Instruments: {len(doc.items(Instrument))}")
```

Résultat :

```text
Sequences: 4
StatementItems: 1
Instruments: 1
```

### Réponses au quiz

1. **(b) Séquence.** Regroupe des étapes dans l'ordre, comme une section.
2. **(c) IfThenElse avec une condition sur l'âge.** Dirige le répondant.
3. **(b) Il enveloppe une question pour l'utiliser dans une Séquence.**
   Sépare le contenu du flux.
4. **(d) Loop.** Répète une section pour chaque élément d'une liste.
5. **(c) Lister toutes les questions et créer des QuestionConstructs.**
   Puis construire le flux autour d'elles.

---

## Module 9 : Traçabilité des données

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")

q_age = doc.add_question(text="What is your age?")
q_gender = doc.add_question(text="What is your gender?")
q_employed = doc.add_question(text="Are you currently employed?")
q_occupation = doc.add_question(text="What is your occupation?")
q_health = doc.add_question(text="How would you rate your general health?")
q_smoke = doc.add_question(text="Do you smoke?")

v_age = doc.add_variable(name="age", question=q_age)
v_gender = doc.add_variable(name="gender", question=q_gender)
v_employed = doc.add_variable(name="employed", question=q_employed)
v_occupation = doc.add_variable(name="occupation", question=q_occupation)
v_health = doc.add_variable(name="health_rating", question=q_health)
v_smoke = doc.add_variable(name="smoker", question=q_smoke)

print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
```

Sortie :

```text
Questions: 6
Variables: 6
```

**Exercice 2** :

```python
from ddi_l.models.logicalproduct import Category
from ddi_l.models.base import Reference

cl = doc.add_code_list(name="Age Group Codes")
doc.add_item(Category, name="0-15")
doc.add_item(Category, name="16-24")
doc.add_item(Category, name="25-44")
doc.add_item(Category, name="45-64")
doc.add_item(Category, name="65+")

v_age_group = doc.add_variable(name="age_group", question=q_age)
v_age_group.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_age.identifier, version="1"),
]

print(f"Code lists: {len(doc.code_lists)}")
print(f"Variables: {len(doc.variables)}")
```

Sortie :

```text
Code lists: 1
Variables: 7
```

**Exercice 3** :

```python
v_emp_code = doc.add_variable(name="employment_status_code", question=q_employed)
v_emp_code.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_employed.identifier, version="1"),
]

v_health_score = doc.add_variable(name="health_score", question=q_health)
v_health_score.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_health.identifier, version="1"),
]

print(f"Variables: {len(doc.variables)}")
```

Sortie : `Variables: 9`

**Exercice 4** :

```python
v_master_ag = doc.add_variable(name="age_group_master", question=q_age)
v_master_ag.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_age_group.identifier, version="1"),
]

v_master_emp = doc.add_variable(name="employment_status_master", question=q_employed)
v_master_emp.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_emp_code.identifier, version="1"),
]

v_master_hs = doc.add_variable(name="health_score_master", question=q_health)
v_master_hs.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_health_score.identifier, version="1"),
]

print(f"Total variables: {len(doc.variables)}")
```

Sortie : `Total variables: 12`

### Réponses au quiz

1. **(b) De quelles autres variables une variable dérivée a été calculée.**
2. **(c) Utiliser `doc.add_variable(name=..., question=q)`.**
3. **(c) Les variables de collecte et les variables dérivées.**
4. **(c) 2 : une pour la taille et une pour le poids.**
5. **(b) Retracer n'importe quelle variable jusqu'à la question et les données originales.**

---

## Module 10 : Couplage de données

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi
from ddi_l.models.base import Reference

doc = ddi.new_study(
    title="Canadian Community Health Survey 2021",
    agency="statcan.gc.ca",
)
q_key = doc.add_question(text="Anonymized linkage key")
q_health = doc.add_question(text="How would you rate your general health?")

survey_key = doc.add_variable(name="anon_id", question=q_key)
survey_health = doc.add_variable(name="health_rating", question=q_health)
survey_key.set_property("linkage_role", "key")

print(f"Survey variables: {len(doc.variables)}")
print(f"anon_id linkage_role: {survey_key.get_property('linkage_role')}")
```

Sortie :

```text
Survey variables: 2
anon_id linkage_role: key
```

**Exercice 2** :

```python
admin = doc.add_study(title="Hospital Admissions Register 2021")
admin_ds = doc.study(admin.identifier)

admin_key = admin_ds.add_variable(name="anon_id")
admin_visits = admin_ds.add_variable(name="hospital_visits")
admin_key.set_property("linkage_role", "key")

cmp = doc.add_comparison(name="Survey-to-Admin Microdata Linkage 2021")
key_match = cmp.correspondence(
    commonality="Anonymized personal identifier common to both sources.",
    weight=1.0,
)
cmp.add_variable_map(
    survey_key.to_reference(),
    admin_key.to_reference(),
    correspondence=key_match,
)

print(f"Comparisons: {len(doc.comparisons)}")
```

Sortie : `Comparisons: 1`

**Exercice 3** :

```python
cmp.set_property("linkage_method", "deterministic")
cmp.set_property("match_rate", "0.94")

print(cmp.get_property("linkage_method"))
```

Sortie : `deterministic`

**Exercice 4** :

```python
linked = doc.add_variable(name="health_by_hospital_use")
linked.source_variable_references = [
    Reference(agency="statcan.gc.ca", identifier=survey_health.identifier, version="1"),
    Reference(agency="statcan.gc.ca", identifier=admin_visits.identifier, version="1"),
]

print(f"Linked variable sources: {len(linked.source_variable_references)}")
```

Sortie : `Linked variable sources: 2`

**Exercice 5** (bonus : couplage probabiliste) :

```python
prob = doc.add_comparison(name="Probabilistic Linkage")

dob = doc.add_variable(name="date_of_birth")
sex = doc.add_variable(name="sex")
postal = doc.add_variable(name="postal_code")
for v in (dob, sex, postal):
    v.set_property("linkage_role", "matching")

weighted = prob.correspondence(
    commonality="Agreement across date of birth, sex, and postal code.",
    weight=0.85,
)

for v in (dob, sex, postal):
    print(f"{v.names[0].text}: {v.get_property('linkage_role')}")
```

Sortie :

```text
date_of_birth: matching
sex: matching
postal_code: matching
```

### Réponses au quiz

1. **(b) Combiner des enregistrements de deux sources ou plus qui se rapportent à la même unité.**
2. **(b) La variable commune aux deux sources qui relie les enregistrements appariés.**
3. **(a) Le déterministe apparie sur une clé exacte ; le probabiliste pondère l'accord sur plusieurs quasi-identifiants.**
4. **(b) Mettre les deux sources dans `source_variable_references`.**
5. **(b) Pour protéger la confidentialité. Les identifiants personnels sont retirés pour que le fichier couplé soit anonymisé.**

---

## Module 11 : Propriétés, recherche et validation

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.new_study(title="Household Survey", agency="research.org")
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="What is your gender?")
q3 = doc.add_question(text="What is your income?")

q3.set_property("sensitivity", "high")
print(q3.properties)
```

Résultat attendu : `{'sensitivity': 'high'}`

**Exercice 2** :

```python
doc.add_variable(name="Age", question=q1)
v = doc.variables[0]
print(v.identifier)
```

**Exercice 3** :

```python
doc.remove(q1.identifier)
print(f"Questions after removal: {len(doc.questions)}")
```

Résultat attendu : `Questions after removal: 2`

**Exercice 4** :

```python
issues = doc.validate()
if not issues:
    print("Document is valid!")
```

### Réponses au quiz

1. **(a) Attache une paire clé-valeur personnalisée à l'élément.** Stocke
   sous forme de UserAttributePair dans le XML.
2. **(a) `item.properties`.** Retourne un dictionnaire de toutes les
   paires clé-valeur.
3. **(a) L'objet élément.** Retourne None s'il n'est pas trouvé.
4. **(a) Vérifie le document par rapport au schéma DDI.** Retourne une
   liste de problèmes (vide si valide).
5. **(a) Supprime l'élément du document.** Retourne True s'il est trouvé.

---

## Module 12 : Champs personnalisés

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.new_study(title="Household Survey", agency="survey.gc.ca")
q_income = doc.add_question(text="What is your household income?")
income = doc.add_variable(name="income", question=q_income)

study = doc.study_unit
study.set_property("myorg:retention_policy", "destroy after 7 years")
study.set_property("myorg:security_class", "Protected B")

print(study.properties)
```

Sortie :

```text
{'myorg:retention_policy': 'destroy after 7 years', 'myorg:security_class': 'Protected B'}
```

**Exercice 2** :

```python
income.set_property("myorg:source_system", "CRM-2024")
q_income.set_property("myorg:steward", "Survey Methods")


def items_with_custom_fields(doc, prefix="myorg:"):
    count = 0
    for collection in (doc.questions, doc.variables):
        for item in collection:
            if any(key.startswith(prefix) for key in item.properties):
                count += 1
    return count


print(f"Items with custom fields: {items_with_custom_fields(doc)}")
```

Sortie : `Items with custom fields: 2`

**Exercice 3** :

```python
from ddi_l.models.base import UserID

income.user_ids.append(UserID(value="CAT-000734", type_of_user_id="InternalCatalogue"))

uid = income.user_ids[0]
print(f"{uid.type_of_user_id}: {uid.value}")
```

Sortie : `InternalCatalogue: CAT-000734`

**Exercice 4** :

```python
doc.save("household-survey.xml")

reopened = ddi.open_ddi("household-survey.xml")
print(reopened.variables[0].get_property("myorg:source_system"))
```

Sortie : `CRM-2024`

**Exercice 5** (bonus : vocabulaire contrôlé) :

```python
from uuid import uuid4

from ddi_l.models.logicalproduct import Category, CodeItem

# Construire le vocabulaire contrôle. Chaque valeur autorisée a besoin d'une
# Category (son sens) ET d'un Code dans la liste qui la référence ; une Category
# seule n'est dans aucune liste. Chaque Code reçoit son propre URN base sur un UUID4.
quality_codes = doc.add_code_list(name="Quality Flag Codes")
for value in ("validated", "provisional", "suppressed"):
    category = doc.add_item(Category, name=value)
    quality_codes.codes.append(
        CodeItem(
            agency=quality_codes.agency,
            identifier=str(uuid4()),
            version=quality_codes.version,
            value=value,
            category=category.to_reference(),
        )
    )

# Un champ dont la valeur vient du vocabulaire, plus un champ qui référence
# la liste de codes définissant les valeurs autorisées
income.set_property("myorg:quality_flag", "validated")
income.set_property("myorg:quality_flag_codes", quality_codes)

print(income.get_property("myorg:quality_flag"))
print(income.get_property("myorg:quality_flag_codes").startswith("urn:ddi:"))
```

Sortie :

```text
validated
True
```

!!! note "Les objets restent attachés"
    Les variables que vous tenez restent les objets que le document
    sérialise, avant comme après `save()`.

### Réponses au quiz

1. **(b) Parce que DDI est une norme ouverte et extensible avec un point d'extension intégré.**
2. **(b) `UserAttributePair`.** `set_property` écrit une paire `AttributeKey`/`AttributeValue`.
3. **(b) Ils survivent : ils sont écrits dans le XML DDI et relus directement.**
4. **(a) Quand la valeur identifie l'élément dans un autre système.** Utilisez une propriété personnalisée quand elle le décrit.
5. **(b) Pour garder vos champs distincts afin qu'ils n'entrent jamais en collision avec ceux d'une autre organisation.**

---

## Module 13 : Mise à jour et versionnage

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.new_study(title="Survey v1", agency="lab.org")
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="What is your gender?")
q3 = doc.add_question(text="How often do you exercise?")
doc.add_variable(name="Age", question=q1)
doc.add_variable(name="Gender", question=q2)
doc.add_variable(name="Exercise", question=q3)
doc.save("survey-v1.xml")
```

**Exercice 2** :

```python
doc = ddi.open_ddi("survey-v1.xml")
q4 = doc.add_question(text="How many hours do you sleep?")
doc.add_variable(name="Sleep", question=q4)
doc.remove(doc.questions[0].identifier)
```

**Exercice 3** :

```python
from ddi_l.models.base import VersionRationale, InternationalString

study = doc.study_unit
study.increment_minor_version()
study.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Added sleep quality question for wave 2")
        ]
    )
)
study.version_responsibility = "Survey Design Team"
```

**Exercice 4** :

```python
issues = doc.validate()
doc.save("survey-v2.xml")
print(f"Version: {study.version}")
for r in study.version_rationales:
    for d in r.descriptions:
        print(f"Rationale: {d.text}")
```

Résultat attendu :

```text
Version: 1.1
Rationale: Added sleep quality question for wave 2
```

### Réponses au quiz

1. **(a) Change la version de 1.0.0 à 1.1.0.** Les incréments de version
   mineure sont pour les ajouts et les petits changements.
2. **(a) Pourquoi un changement a été fait.** Une explication textuelle
   stockée dans le document DDI.
3. **(a) Qui a fait le changement.** Un champ texte identifiant la
   personne ou l'équipe responsable.
4. **(a) Majeure pour les grands changements, mineure pour les ajouts.**
   Utilisez la version majeure quand la structure change de façon
   importante, la mineure quand vous ajoutez ou modifiez.

---

## Module 14 : Ouvrir et modifier des fichiers

### Solutions des exercices

**Exercice 1** :

```python
import ddi_l as ddi

doc = ddi.open_ddi("survey-v1.xml")
print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
```

**Exercice 2** :

```python
q_new1 = doc.add_question(text="What is your education level?")
q_new2 = doc.add_question(text="What is your marital status?")
doc.add_variable(name="Education", question=q_new1)
doc.add_variable(name="MaritalStatus", question=q_new2)
issues = doc.validate()
doc.save("survey-updated.xml")
```

**Exercice 3** :

```python
doc2 = ddi.open_ddi("survey-updated.xml")
print(f"Questions: {len(doc2.questions)}")
print(f"Variables: {len(doc2.variables)}")
```

Les totaux devraient être 2 de plus que dans l'exercice 1.

### Réponses au quiz

1. **(a) Ouvre et analyse un fichier DDI XML en un Document.** Vous
   pouvez ensuite le lire et le modifier.
2. **(a) Vérifie le fichier par rapport au schéma DDI pendant le
   chargement.** Toute erreur est signalée immédiatement.
3. **(a) Non, le contenu existant est préservé.** ddi-l conserve le
   XML inconnu dans `other_elements` pour que rien ne soit perdu.

---

## Module 15 : Validation en ligne de commande

### Solutions des exercices

**Exercice 1** :

```bash
ddi validate survey-v1.xml
```

Résultat attendu : `Document is valid.`

**Exercice 2** :

```bash
ddi to-json survey-v1.xml --indent 2 > survey.json
wc -l survey.json
```

Le nombre de lignes dépend de la taille du document.

**Exercice 3** :

```bash
ddi roundtrip survey-v1.xml --output survey-roundtrip.xml
ls -la survey-v1.xml survey-roundtrip.xml
```

Les tailles de fichiers devraient être similaires.

### Réponses au quiz

1. **(a) Vérifie le fichier par rapport au schéma DDI.** Affiche
   « Document is valid. » ou une liste d'erreurs en JSON.
2. **(a) Le fichier est valide.** Le code de sortie 0 signifie succès
   sous Unix.
3. **(a) Convertit le DDI XML en format JSON.** Utile pour les API web
   et les systèmes d'analyse.

---

## Module 16 : Projets de synthèse

### Exemple de solution : Parcours A (Étudiant)

Utilise le jeu de données d'exemple de la page du projet :
[`thesis-data.csv`](thesis-data.csv){ download="thesis-data.csv" }.

```python
import csv
import ddi_l as ddi
from ddi_l.models.base import VersionRationale, InternationalString

# Read CSV
with open("thesis-data.csv") as f:
    columns = csv.DictReader(f).fieldnames

# Create v1.0
doc = ddi.new_study(title="Thesis Dataset", agency="university.edu")
# Comment chaque colonne a été demandée. StudentID est attribué et AnxietyScore
# est calculé à partir d'un questionnaire : ni l'un ni l'autre n'a de question.
QUESTIONS = {
    "Age": "Quel âge avez-vous ?",
    "Gender": "Quel est votre genre ?",
    "YearOfStudy": "En quelle année de votre programme êtes-vous ?",
    "Program": "Dans quel programme êtes-vous inscrit(e) ?",
    "StudyHours": "Lors d'une journée typique, combien d'heures étudiez-vous ?",
    "SleepHours": "Lors d'une nuit typique, combien d'heures dormez-vous ?",
    "WorkHours": "Combien d'heures par semaine travaillez-vous contre rémunération ?",
    "ExerciseDays": "Combien de jours avez-vous fait de l'exercice la semaine dernière ?",
    "StressLevel": "Sur une échelle de 1 à 10, quel a été votre niveau de stress ce trimestre ?",
    "SoughtSupport": "Avez-vous demandé de l'aide aux services du campus ce trimestre ?",
}
for col in columns:
    libelle = QUESTIONS.get(col)
    q = doc.add_question(text=libelle, lang="fr") if libelle else None
    v = doc.add_variable(name=col, question=q)
    v.set_property("source", "Primary survey data")

doc.add_concept(name="Demographics")
doc.add_concept(name="Academic Performance")
doc.add_concept(name="Well-Being")
doc.add_universe(name="Undergraduate students at University X")

doc.save("thesis-v1.xml")
issues = doc.validate()
print(f"v1 valid: {not issues}")

# Update to v1.1
doc = ddi.open_ddi("thesis-v1.xml")
q_new = doc.add_question(text="What is the student's GPA?")
v_new = doc.add_variable(name="GPA", question=q_new)

study = doc.study_unit
study.increment_minor_version()
study.version_rationales.append(
    VersionRationale(
        descriptions=[InternationalString(text="Added GPA variable for analysis")]
    )
)
study.version_responsibility = "Thesis Author"
doc.save("thesis-v1.1.xml")
print(f"v1.1 valid: {not doc.validate()}")
```

### Questions de réflexion

Ce sont des questions ouvertes. Il n'y a pas de bonne ou mauvaise
réponse. Utilisez-les pour la discussion ou les commentaires écrits.
