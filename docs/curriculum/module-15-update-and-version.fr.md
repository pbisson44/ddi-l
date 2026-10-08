---
description: >-
  Module 15 du cours ddi-l : mettre à jour des fichiers DDI publiés,
  incrémenter les versions, consigner les justifications et garder les
  références à jour.
---

# Module 15 : Mettre à jour et versionner vos documents

!!! info "Ce que vous apprendrez"
    - Expliquer pourquoi le versionnement est important pour les enquêtes et les études.
    - Ouvrir un document DDI existant et ajouter du nouveau contenu.
    - Utiliser des numéros de version pour suivre les changements au fil du temps.
    - Augmenter les numéros de version majeure, mineure et de sous-version.
    - Enregistrer pourquoi un changement a été fait avec `VersionRationale`.
    - Indiquer qui est responsable d'un changement de version.
    - Modifier le libellé d'une question existante.
    - Faire passer une variable d'une liste de codes à une autre.
    - Garder les références pointées vers la nouvelle version d'un élément modifié.
    - Décrire un nouveau fichier de données et mettre à jour plusieurs variables à partir de celui-ci en une seule boucle.

**Prérequis :** [Module 14 : Champs personnalisés](module-14-custom-fields.md).

**Durée :** 65 min en autonomie / 75 min avec instructeur.

---

## 1. Pourquoi le versionnement est important

Les enquêtes changent au fil du temps. Un recensement peut ajouter une nouvelle question sur l'accès à Internet en 2024. Une enquête sur la population active peut retirer une question dépassée sur les télécopieurs. Quand vous modifiez un document, vous devez répondre à deux questions :

1. **Qu'est-ce qui a changé ?** Quels éléments ont été ajoutés, retirés ou modifiés ?
2. **Pourquoi cela a-t-il changé ?** Quelle était la raison de la mise à jour ?

Le **versionnement** consiste à donner à chaque copie d'un document un numéro (comme « 1.0.0 » ou « 2.1.0 ») pour pouvoir les distinguer. C'est comme enregistrer une rédaction scolaire sous « redaction-v1 », « redaction-v2 » et « redaction-v3 ». Chaque version est une photo à un moment donné.

Sans versionnement, vous ne pouvez pas revenir à une copie précédente. Vous ne pouvez pas comparer ce qui a changé d'une année à l'autre. Et vous ne pouvez pas expliquer vos choix aux autres personnes.

---

## 2. Le processus de mise à jour

Les étapes de base pour mettre à jour un document DDI sont :

1. **Ouvrir** le fichier existant.
2. **Ajouter** du nouveau contenu (questions, variables, concepts).
3. **Retirer** le contenu obsolète.
4. **Enregistrer** le fichier mis à jour avec un nouveau nom.

Voici un court exemple. Les deux premières lignes tiennent lieu du fichier de
l'an dernier ; si vous avez déjà un fichier DDI, ouvrez le vôtre et sautez-les.

```python
import ddi_l as ddi

# Tient lieu du fichier de l'an dernier
ddi.new_study(title="Labour Force Survey 2023", agency="example.org").save(
    "lfs-2023.xml"
)

# Step 1: Open the existing file
doc = ddi.open_ddi("lfs-2023.xml")

# Step 2: Add a new question
doc.add_question(text="Do you work from home?")

# Step 3: Save with a new filename
doc.save("lfs-2024.xml")
```

La fonction `ddi.open_ddi()` lit un fichier DDI XML depuis le disque et vous donne un objet `Document`. Vous pouvez ensuite ajouter ou retirer des éléments comme vous l'avez fait lors de la création du document. La fonction `doc.save()` écrit le document mis à jour dans un nouveau fichier.

---

## 3. Les numéros de version

Chaque élément DDI possède un champ **version**. Une version est une chaîne de chiffres séparés par des points, comme `"1.0.0"`. Les trois parties sont :

| Partie  | Position | Signification            | Exemple       |
| ------- | -------- | ------------------------ | ------------- |
| Majeure | Première | Grands changements       | **2**.0.0     |
| Mineure | Deuxième | Ajouts ou extensions     | 1.**1**.0     |
| Sous    | Troisième| Petites corrections      | 1.0.**1**     |

Vous pouvez lire la version actuelle de n'importe quel élément :

```python
study = doc.study_unit
print(study.version)  # p. ex. "1"
```

Quand vous créez une étude avec `ddi.new_study()`, la version par défaut est `"1"`. Vous pouvez la définir à `"1.0.0"` si vous préférez les numéros à trois parties.

---

## 4. Augmenter les versions

`ddi-l` vous offre trois méthodes pour augmenter un numéro de version. Chacune est une méthode sur n'importe quel élément DDI (question, variable, concept, étude, etc.). Un **élément** est tout objet qui étend `MaintainableBase`, la classe de base pour tous les objets DDI.

### Version majeure : grands changements

Utilisez `increment_major_version()` quand vous faites un grand changement qui pourrait causer des problèmes. Par exemple, vous refaites tout le questionnaire.

```python
item.increment_major_version()
# 1.0.0 → 2.0.0
```

### Version mineure : ajouts

Utilisez `increment_minor_version()` quand vous ajoutez quelque chose de nouveau mais gardez tout le reste. Par exemple, vous ajoutez deux nouvelles questions à une enquête.

```python
item.increment_minor_version()
# 1.0.0 → 1.1.0
```

### Sous-version : petites corrections

Utilisez `increment_subversion()` quand vous corrigez une faute de frappe ou une petite erreur. Rien de majeur n'a changé.

```python
item.increment_subversion()
# 1.0.0 → 1.0.1
```

Chaque méthode augmente un nombre et remet les nombres à sa droite à zéro. Par exemple, si la version est `1.2.3` et que vous appelez `increment_minor_version()`, le résultat est `1.3.0`.

---

## 5. Enregistrer pourquoi vous avez changé quelque chose

Une **justification de version** est une courte note qui explique pourquoi un changement a été fait. DDI stocke cette information dans le XML pour que toute personne qui ouvre le fichier plus tard puisse comprendre l'historique.

Vous définissez aussi la **responsabilité de version** : le nom de la personne ou de l'équipe qui a fait le changement.

```python
from ddi_l.models.base import VersionRationale, InternationalString

# Create a rationale with a description
rationale = VersionRationale(
    descriptions=[
        InternationalString(text="Added work-from-home question for 2024 wave")
    ]
)

# Attach it to an item
item.version_rationales.append(rationale)

# Record who made the change
item.version_responsibility = "Survey Design Team"
```

- `VersionRationale` est un petit objet qui contient une liste de descriptions. Chaque description est un `InternationalString` pour que vous puissiez l'écrire dans plusieurs langues.
- `version_rationales` est une liste. Vous pouvez ajouter plus d'une justification si nécessaire.
- `version_responsibility` est une chaîne de texte simple avec le nom de la personne ou de l'équipe.

---

## 6. Modifier le libellé d'une question

Ajouter et retirer des questions n'est qu'une partie du travail. La plupart des mises à jour d'enquête *modifient* quelque chose qui existe déjà : une question reçoit un libellé plus clair, ou ses catégories de réponse changent. Cette section et la suivante montrent les deux cas, sur le même petit fichier.

Le fichier contient une question, « Do you work from home? » (Travaillez-vous à domicile ?). On y répond avec une liste de codes **Oui/Non**, et la réponse est stockée dans la variable `WFH`. Le bloc ci-dessous crée ce fichier, avec le modèle de liste de codes du [Module 14](module-14-custom-fields.md). Sautez-le si vous avez votre propre fichier.

```python
from uuid import uuid4

import ddi_l as ddi
from ddi_l.models.base import InternationalString, VersionRationale
from ddi_l.models.logicalproduct import Category, CodeItem


def add_codes(doc, code_list, answers):
    """Add one Category and one Code per (value, name) pair to code_list."""
    for value, name in answers:
        category = doc.add_item(Category, name=name, label=name)
        code_list.codes.append(
            CodeItem(
                agency=code_list.agency,
                identifier=str(uuid4()),
                version=code_list.version,
                value=value,
                category=category.to_reference(),
            )
        )


# Stand-in for last year's file
last_year = ddi.new_study(title="Labour Force Survey 2023", agency="example.org")
question = last_year.add_question(text="Do you work from home?", label="Work from home")
yes_no = last_year.add_code_list(name="Yes/No", label="Yes/No")
add_codes(last_year, yes_no, [("1", "Yes"), ("2", "No")])
wfh = last_year.add_variable(name="WFH", label="Works from home", question=question)
wfh.set_coded(yes_no)
last_year.save("wfh-2023.xml")
```

### Étape 1 : Trouver la question

Ouvrez le fichier et trouvez la question par son texte actuel :

```python
doc = ddi.open_ddi("wfh-2023.xml")

wfh_question = next(
    q for q in doc.questions if q.question_texts[0].text == "Do you work from home?"
)
```

Si vous connaissez l'identifiant de la question, `doc.find(identifier)` du [Module 13](module-13-properties-find-validate.md) fonctionne aussi.

### Étape 2 : Changer le texte

Le libellé d'une question est conservé dans `question_texts`, une liste avec un `InternationalString` par langue. Changez le `text` de la langue que vous mettez à jour :

```python
for text in wfh_question.question_texts:
    if text.lang == "en":
        text.text = "In a typical week, do you work from home?"

print(wfh_question.question_texts[0].text)
# -> In a typical week, do you work from home?
```

!!! warning "Mettez à jour toutes les langues"
    Si la question a aussi un texte en français (Module 3), changez-le aussi, dans la même boucle (`if text.lang == "fr": ...`). Sinon, les versions anglaise et française ne posent plus la même question.

### Étape 3 : Versionner la question et dire pourquoi

La question a changé, donc sa version doit changer. Un petit changement de clarification comme celui-ci est une **sous-version**. Si le nouveau libellé change ce que la question mesure, et que les réponses ne sont plus comparables avec l'an dernier, utilisez plutôt une version **majeure**.

```python
wfh_question.increment_subversion()
wfh_question.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Added the reference period 'in a typical week'")
        ]
    )
)
wfh_question.version_responsibility = "Survey Design Team"

print(wfh_question.version)  # -> 1.0.1
```

### Étape 4 : Faire pointer les références vers la nouvelle version

Une référence DDI désigne une version précise d'un élément. La variable `WFH` dit encore « question `…`, version `1` ». Cette version n'est plus dans le fichier, donc la référence est maintenant brisée. Faites pointer chaque référence à la question vers sa nouvelle version. Dans ce fichier, seule la variable fait référence à la question :

```python
for variable in doc.variables:
    variable.question_references = [
        wfh_question.to_reference()
        if ref.identifier == wfh_question.identifier
        else ref
        for ref in variable.question_references
    ]
```

`to_reference()` construit une référence à l'élément tel qu'il est *maintenant*, avec sa nouvelle version.

Un fichier qui contient un flux de questionnaire (Module 10) a d'autres références à la question : chaque `QuestionConstruct` qui la pose contient une `question_reference`. Faites-les pointer de la même façon. Ce fichier n'en a pas, donc la boucle ne fait rien :

```python
from ddi_l.models.datacollection import QuestionConstruct

for construct in doc.items(QuestionConstruct):
    ref = construct.question_reference
    if ref is not None and ref.identifier == wfh_question.identifier:
        construct.question_reference = wfh_question.to_reference()
```

Laissez ensuite `doc.lint()` vérifier que plus rien ne pointe vers l'ancienne version. Chaque erreur `ddi.reference.integrity` qu'il signale désigne un élément qu'il vous reste à faire pointer vers la nouvelle version :

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
```

---

## 7. Passer une variable à une autre liste de codes

Pour la vague 2024, une simple réponse Oui/Non ne suffit plus. L'équipe veut savoir *à quelle fréquence* les gens travaillent à domicile. Les catégories de réponse passent de **Oui/Non** à une nouvelle liste de codes **Fréquence**.

### Étape 1 : Créer la nouvelle liste de codes

```python
frequency = doc.add_code_list(name="Frequency", label="Frequency")
add_codes(doc, frequency, [("1", "Every day"), ("2", "Some days"), ("3", "Never")])
```

### Étape 2 : Faire pointer la variable vers elle

`set_coded()` indique à une variable quelle liste de codes contient ses valeurs. L'appeler à nouveau remplace l'ancienne liste de codes par la nouvelle :

```python
wfh = next(v for v in doc.variables if v.names[0].text == "WFH")
wfh.set_coded(frequency)
```

Vous pouvez vérifier quelle liste de codes une variable utilise maintenant. Lisez la référence dans la représentation de la variable, puis cherchez-la avec `doc.find()` :

```python
reference = wfh.variable_representation.code_representation.code_list_reference
current = doc.find(reference.identifier)

print(current.names[0].text)  # -> Frequency
print([code.value for code in current.codes])  # -> ['1', '2', '3']
```

### Étape 3 : Versionner la variable et dire pourquoi

De nouvelles catégories de réponse changent ce que la variable peut contenir. Des réponses codées 1 ou 2 l'an dernier et 1, 2 ou 3 cette année ne peuvent pas être comparées directement. C'est donc au moins un changement **mineur**, et souvent un changement **majeur** :

```python
wfh.increment_major_version()
wfh.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(
                text="Answer categories changed from Yes/No to Frequency"
            )
        ]
    )
)
wfh.version_responsibility = "Survey Design Team"

print(wfh.version)  # -> 2
```

La variable commençait à la version `"1"`, donc une augmentation majeure donne `"2"`. L'augmentation de sous-version de la question a donné `"1.0.1"` parce qu'une sous-version a besoin des trois parties.

Comme pour la question, tout ce qui fait référence à la variable pointe maintenant vers son ancienne version. Dans ce fichier, rien ne le fait. Dans un fichier plus grand, vérifiez les variables dérivées de celle-ci (leurs `source_variable_references`, Module 11) et tout schéma d'enregistrement (section 8). Faites-les pointer de la même façon, ou construisez-les après l'augmentation.

### Étape 4 : Garder ou retirer l'ancienne liste de codes

La liste de codes Oui/Non est encore dans le fichier. Gardez-la si d'autres variables l'utilisent encore, ou si vous voulez que le fichier montre ce que signifiaient les réponses de l'an dernier. Si plus rien ne l'utilise, retirez-la :

```python
old_list = next(cl for cl in doc.code_lists if cl.names[0].text == "Yes/No")
doc.remove(old_list.identifier)

print([cl.names[0].text for cl in doc.code_lists])  # -> ['Frequency']
```

Les catégories « Yes » et « No » restent dans le fichier. C'est sans danger, et d'autres listes de codes peuvent encore les réutiliser.

Enfin, vérifiez le fichier et enregistrez-le sous un nouveau nom, pour que le fichier de l'an dernier reste tel quel. `doc.validate()` vérifie le fichier par rapport au schéma DDI seulement. Il ne remarque pas une référence à une version qui n'existe plus ; exécutez donc aussi `doc.lint()` :

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
print(doc.validate())  # -> []

doc.save("wfh-2024.xml")
```

!!! note "Le domaine de réponse de la question"
    Dans ce programme, une liste de codes est rattachée à la **variable**. Les fichiers d'autres outils, comme Colectica, la rattachent souvent aussi à la **question**, dans un élément `d:CodeDomain` à l'intérieur de la question. `ddi-l` conserve cet élément exactement tel qu'il a été lu : `set_coded()` ne change que la variable, et `ddi-l` n'a pas encore d'aide pour changer le domaine de réponse d'une question. Si votre fichier en a un, ouvrez-le dans un éditeur de texte après le changement et vérifiez quelle liste de codes désigne le `r:CodeListReference` de la question.

---

## 8. Mettre à jour plusieurs variables à partir d'un nouveau fichier de données

Une nouvelle vague arrive généralement sous forme de **fichier de données**. Les métadonnées doivent suivre : il faut décrire le nouveau fichier, et de nombreuses variables ont besoin du même type de changement. En DDI, un fichier de données est décrit par une **instance physique** (`PhysicalInstance`) : où se trouve le fichier et combien d'enregistrements il contient.

Cette section rassemble les morceaux. Vous décrivez le nouveau fichier, puis vous parcourez les variables une seule fois pour mettre chacune à jour à partir des données, en versionnant chaque changement au fur et à mesure.

L'exemple utilise le fichier du Module 8 :

[:material-download: Télécharger `survey_sample.csv`](survey_sample.csv){ .md-button download="survey_sample.csv" }

Le document de l'an dernier décrit déjà les cinq mêmes colonnes, ainsi que le fichier de données 2023. Le bloc ci-dessous le crée. Sautez-le si vous avez votre propre fichier.

```python
import csv

from ddi_l.models.physical import PhysicalInstance

# Stand-in for last year's file
last_year = ddi.new_study(title="Income Survey 2023", agency="example.org")
for column in ("respondent_id", "age", "gender", "income", "education_level"):
    last_year.add_variable(name=column, label=column)
data_2023 = last_year.add_item(PhysicalInstance, name="Income Survey 2023 data")
data_2023.set_data_file("https://example.org/data/income-2023.csv")
data_2023.set_record_count(4800)
last_year.save("income-2023.xml")
```

### Étape 1 : Ouvrir le document et lire le nouveau fichier de données

```python
doc = ddi.open_ddi("income-2023.xml")

with open("survey_sample.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"{len(rows)} records")  # -> 5 records
```

### Étape 2 : Décrire le nouveau fichier

Ajoutez une instance physique pour le fichier 2024. Gardez celle de 2023 : elle décrit toujours correctement le fichier de l'an dernier.

```python
data_2024 = doc.add_item(PhysicalInstance, name="Income Survey 2024 data")
data_2024.set_data_file("https://example.org/data/income-2024.csv")
data_2024.set_record_count(len(rows))
```

### Étape 3 : Noter les changements

Rassemblez les changements au même endroit avant de toucher à une variable. Ici, chaque variable reçoit un libellé plus clair, deux reçoivent une plage numérique et deux reçoivent une liste de codes :

```python
new_labels = {
    "respondent_id": "Respondent identifier",
    "age": "Age in years",
    "gender": "Gender",
    "income": "Annual income (CAD)",
    "education_level": "Highest level of education",
}
numeric_columns = {"age", "income"}
coded_columns = {"gender", "education_level"}
```

### Étape 4 : Mettre à jour toutes les variables en une seule boucle

Pour chaque variable, trouvez sa colonne dans le fichier de données, appliquez les changements, puis versionnez-la. Les listes de codes utilisent la fonction `add_codes()` de la section 6.

```python
for variable in doc.variables:
    column = variable.names[0].text
    values = [row[column] for row in rows if row[column] != ""]

    # A clearer label
    variable.labels = [InternationalString(text=new_labels[column], lang="en")]

    # What the variable holds, taken from the new file
    if column in numeric_columns:
        numbers = [int(value) for value in values]
        variable.set_numeric("Integer", low=min(numbers), high=max(numbers))
    elif column in coded_columns:
        code_list = doc.add_code_list(name=new_labels[column], label=new_labels[column])
        answers = sorted(set(values))
        add_codes(doc, code_list, [(str(n), a) for n, a in enumerate(answers, 1)])
        variable.set_coded(code_list)
    else:
        variable.set_text()

    # Version the change and say why
    variable.increment_minor_version()
    variable.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Label and representation updated for 2024")
            ]
        )
    )
    variable.version_responsibility = "Data Processing Unit"

for variable in doc.variables:
    print(variable.names[0].text, variable.version)
```

```text
respondent_id 1.1
age 1.1
gender 1.1
income 1.1
education_level 1.1
```

Vous pouvez en vérifier une. La plage de `age` correspond maintenant aux âges du nouveau fichier :

```python
age = next(v for v in doc.variables if v.names[0].text == "age")
age_range = age.variable_representation.numeric_representation.number_range
print(age_range.low, age_range.high)  # -> 22 51
```

### Étape 5 : Indiquer où se trouve chaque variable dans le nouveau fichier

Un **schéma d'enregistrement** (`RecordLayout`) liste les variables du fichier de données. Construisez-le *après* les augmentations de version, pour qu'il pointe vers les nouvelles versions. Un schéma construit avant la boucle pointerait vers les anciennes. Liez ensuite le schéma au fichier 2024 :

```python
layout = doc.add_record_layout()
for variable in doc.variables:
    layout.add_data_item(variable.to_reference(), delimiter="comma")
data_2024.record_layout_references.append(layout.to_reference())
```

### Étape 6 : Vérifier et enregistrer

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
print(doc.validate())  # -> []

doc.save("income-2024.xml")
```

!!! tip "Une boucle, une justification par élément"
    Le modèle s'adapte à toutes les tailles. Que vous changiez cinq variables ou cinq cents, notez d'abord les changements (étape 3). Appliquez-les ensuite en une seule boucle qui modifie, versionne et explique chaque élément. Chaque variable modifiée reçoit sa propre version et sa propre justification, et l'historique reste lisible élément par élément.

---

## 9. Le cycle complet de mise à jour

Voici le processus complet du début à la fin :

```python
import ddi_l as ddi
from ddi_l.models.base import VersionRationale, InternationalString

# Tient lieu du fichier de l'an dernier (sautez si vous avez le votre)
first = ddi.new_study(title="Survey v1", agency="example.org")
first.add_question(text="Do you own a fax machine?")
first.save("survey-v1.xml")

# 1. Open the existing document
doc = ddi.open_ddi("survey-v1.xml")

# 2. Add new content
doc.add_question(text="How many hours do you sleep per night?")

# 3. Remove outdated content (use the identifier of the old item)
old_question = doc.questions[0]
doc.remove(old_question.identifier)

# 4. Increment the version on the study
study = doc.study_unit
study.increment_minor_version()

# 5. Add a rationale
study.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Added sleep question; removed outdated item")
        ]
    )
)
study.version_responsibility = "Research Methods Unit"

# 6. Validate
errors = doc.validate()
if errors:
    print("Errors:", errors)
else:
    print("Document is valid.")  # -> Document is valid.

# 7. Save
doc.save("survey-v2.xml")
```

---

## 10. Bonnes pratiques

Suivez ces règles pour garder votre versionnement propre et utile :

- **Toujours valider avant de publier.** Exécutez `doc.validate()` et corrigez toutes les erreurs avant de partager le fichier.
- **Gardez les anciennes versions.** Enregistrez chaque version dans un fichier différent (comme `survey-v1.xml`, `survey-v2.xml`). N'écrasez pas les anciens fichiers.
- **Écrivez des justifications claires.** Les futurs utilisateurs vous remercieront. Une bonne justification dit *ce qui* a changé et *pourquoi*.
- **Utilisez le bon type d'augmentation.** N'utilisez pas une version majeure pour une petite correction. Faites correspondre l'augmentation à la taille du changement.
- **Définissez la responsabilité de version.** Notez qui a approuvé ou fait le changement pour qu'il y ait un contact pour les questions.
- **Versionnez l'élément modifié, pas seulement l'étude.** Une question reformulée ou une variable avec de nouvelles catégories de réponse reçoit sa propre augmentation de version et sa propre justification.
- **Mettez à jour les références.** Après une augmentation de version, faites pointer chaque référence à l'élément vers sa nouvelle version, puis exécutez `doc.lint()` pour confirmer que rien n'est brisé.

---

## Exercices

!!! example "Scénario"
    Une enquête nationale sur la population active est menée chaque année. La version 2024 a ajouté deux nouvelles questions et retiré une ancienne question. L'agence doit mettre à jour le document DDI et enregistrer pourquoi.

**Exercice 1.** Créez une étude avec trois questions (« Survey v1 »). Enregistrez-la sous `survey-v1.xml`.

??? success "Réponse"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Labour Force Survey v1", agency="stats.example.org")
    q1 = doc.add_question(text="What is your current employment status?")
    q2 = doc.add_question(text="How many hours do you work per week?")
    q3 = doc.add_question(text="Do you use a fax machine at work?")
    doc.save("survey-v1.xml")
    print(f"Saved with {len(doc.questions)} questions.")
    ```

**Exercice 2.** Rouvrez `survey-v1.xml`. Ajoutez une nouvelle question. Retirez une ancienne question.

??? success "Réponse"
    ```python
    doc = ddi.open_ddi("survey-v1.xml")
    print(f"Before: {len(doc.questions)} questions")

    # Add a new question
    doc.add_question(text="How many hours do you sleep per night?")

    # Remove the outdated fax question (the third one)
    fax_q = doc.questions[2]
    doc.remove(fax_q.identifier)
    print(f"After: {len(doc.questions)} questions")
    ```

**Exercice 3.** Récupérez l'étude du document. Appelez `increment_minor_version()` dessus. Ajoutez un `VersionRationale`. Définissez `version_responsibility`.

??? success "Réponse"
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

**Exercice 4.** Validez et enregistrez sous `survey-v2.xml`. Affichez la version et la justification.

Résultat attendu :

```text
Version: 1.1
Rationale: Added sleep quality question for wave 2
```

??? success "Réponse"
    ```python
    errors = doc.validate()
    if errors:
        print("Errors:", errors)
    else:
        doc.save("survey-v2.xml")
        print(f"Version: {study.version}")
        for r in study.version_rationales:
            for d in r.descriptions:
                print(f"Rationale: {d.text}")
    ```

**Exercice 5.** Rouvrez `survey-v2.xml`. Changez le libellé de la question sur la situation d'emploi pour « What was your main activity last week? » (Quelle était votre activité principale la semaine dernière ?). Donnez à la question une augmentation de sous-version et une justification. Enregistrez ensuite le fichier sous `survey-v3.xml`.

??? success "Réponse"
    ```python
    doc = ddi.open_ddi("survey-v2.xml")

    status_q = next(
        q
        for q in doc.questions
        if q.question_texts[0].text == "What is your current employment status?"
    )
    for text in status_q.question_texts:
        if text.lang == "en":
            text.text = "What was your main activity last week?"

    status_q.increment_subversion()
    status_q.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Aligned wording with the ILO definition")
            ]
        )
    )

    # Repoint any variable that references the question
    for variable in doc.variables:
        variable.question_references = [
            status_q.to_reference() if ref.identifier == status_q.identifier else ref
            for ref in variable.question_references
        ]

    doc.save("survey-v3.xml")
    print(f"{status_q.question_texts[0].text} (version {status_q.version})")
    # -> What was your main activity last week? (version 1.0.1)
    ```

**Exercice 6.** Dans le même document, ajoutez une variable `EMPSTAT` pour la question. Codez-la avec une liste à trois valeurs (Employed, Unemployed, Not in labour force). Faites-la ensuite passer à une liste à quatre valeurs qui sépare « Not in labour force » en « Student » et « Retired ». Augmentez la version majeure de la variable et notez pourquoi.

??? success "Réponse"
    ```python
    three_way = doc.add_code_list(name="Status (3)", label="Status (3)")
    add_codes(
        doc,
        three_way,
        [("1", "Employed"), ("2", "Unemployed"), ("3", "Not in labour force")],
    )
    four_way = doc.add_code_list(name="Status (4)", label="Status (4)")
    add_codes(
        doc,
        four_way,
        [("1", "Employed"), ("2", "Unemployed"), ("3", "Student"), ("4", "Retired")],
    )

    empstat = doc.add_variable(name="EMPSTAT", label="Employment status", question=status_q)
    empstat.set_coded(three_way)

    # The switch
    empstat.set_coded(four_way)
    empstat.increment_major_version()
    empstat.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Split 'Not in labour force' into Student and Retired"
                )
            ]
        )
    )

    reference = empstat.variable_representation.code_representation.code_list_reference
    print(doc.find(reference.identifier).names[0].text)  # -> Status (4)
    ```

---

## Quiz

???+ question "Question 1 : Que fait increment_minor_version() ?"
    **A.** Elle change la version de 1.0.0 à 2.0.0.

    **B.** Elle change la version de 1.0.0 à 1.1.0.

    **C.** Elle change la version de 1.0.0 à 1.0.1.

    **D.** Elle supprime le numéro de version.

    ??? success "Réponse"
        **B.** `increment_minor_version()` augmente le deuxième nombre et
        remet le troisième nombre à zéro. Donc 1.0.0 devient 1.1.0.

???+ question "Question 2 : Qu'enregistre une justification de version ?"
    **A.** La taille du fichier du document.

    **B.** Le nombre de questions dans l'enquête.

    **C.** Une explication de pourquoi le document a changé.

    **D.** Le nom du fichier Python utilisé pour créer le document.

    ??? success "Réponse"
        **C.** Une justification de version est une courte note qui explique
        pourquoi un changement a été fait. Elle aide les futurs utilisateurs
        à comprendre l'historique du document.

???+ question "Question 3 : Que suit version_responsibility ?"
    **A.** L'ordinateur où le fichier est stocké.

    **B.** La personne ou l'équipe qui a fait le changement de version.

    **C.** La date de la prochaine vague d'enquête.

    **D.** Le nombre total de versions.

    ??? success "Réponse"
        **B.** `version_responsibility` est un champ texte qui enregistre
        qui a fait ou approuvé le changement. Ce peut être le nom d'une
        personne ou le nom d'une équipe.

???+ question "Question 4 : Quand devez-vous utiliser une augmentation de version majeure ?"
    **A.** Quand vous corrigez une faute de frappe dans une question.

    **B.** Quand vous ajoutez une nouvelle variable.

    **C.** Quand vous faites un grand changement, comme refaire tout le questionnaire.

    **D.** Quand vous enregistrez le fichier dans un nouveau dossier.

    ??? success "Réponse"
        **C.** Une augmentation de version majeure (1.0.0 à 2.0.0) signale
        un grand changement qui peut causer des problèmes. Les petits ajouts
        utilisent une augmentation mineure. Les corrections de fautes utilisent
        une augmentation de sous-version.

???+ question "Question 5 : Vous reformulez une question et augmentez sa version. Que devez-vous faire d'autre ?"
    **A.** Rien ; la variable suit la question automatiquement.

    **B.** Supprimer la variable et en créer une nouvelle.

    **C.** Faire pointer chaque référence à la question vers sa nouvelle version.

    **D.** Renommer le fichier en `.ddi`.

    ??? success "Réponse"
        **C.** Une référence DDI désigne une version précise. Après
        l'augmentation, les `question_references` de la variable (et tout
        `QuestionConstruct` qui pose la question) désignent encore l'ancienne
        version ; remplacez-les par `question.to_reference()`. `doc.lint()`
        signale une erreur `ddi.reference.integrity` pour chacune que vous
        oubliez.

???+ question "Question 6 : Comment faire passer une variable d'une liste de codes à une autre ?"
    **A.** Appeler `variable.set_coded(new_code_list)`.

    **B.** Renommer l'ancienne liste de codes.

    **C.** Ajouter les nouveaux codes à l'ancienne liste de codes.

    **D.** Appeler `doc.add_code_list()` avec le nom de la variable.

    ??? success "Réponse"
        **A.** `set_coded()` remplace la représentation de la variable par une
        représentation qui désigne la nouvelle liste de codes. Augmentez
        ensuite la version de la variable, notez une justification, et
        retirez l'ancienne liste de codes si plus rien ne l'utilise.

???+ question "Question 7 : Vous mettez à jour 30 variables à partir d'un nouveau fichier de données. Quand devez-vous construire le nouveau schéma d'enregistrement ?"
    **A.** Avant la boucle, pour qu'il soit prêt.

    **B.** Après les augmentations de version, pour qu'il pointe vers les nouvelles versions.

    **C.** Jamais ; l'instance physique trouve les variables par leur nom.

    **D.** Seulement si le fichier est à largeur fixe.

    ??? success "Réponse"
        **B.** Un schéma d'enregistrement contient des références aux
        variables, et chaque référence désigne une version. Construit avant
        les augmentations, il pointerait vers les anciennes versions.
        Construit après, `variable.to_reference()` donne les nouvelles.

---

!!! tip "Notes pour l'instructeur"
    - **Module clé pour les archivistes et le personnel des INS.** Le
      versionnement est intégré dans le standard DDI lui-même ; ce n'est
      pas quelque chose ajouté par-dessus. Chaque objet maintenable porte
      ses propres champs de version, justification et responsabilité.
    - **Montrez le XML avant/après.** Ouvrez `survey-v1.xml` et
      `survey-v2.xml` dans un éditeur de texte côte à côte. Montrez les
      éléments `<r:Version>` et `<r:VersionRationale>` pour que les
      apprenants voient ce que le code Python produit.
    - **Les méthodes de version sont sur `MaintainableBase`.** Tous les
      objets DDI (questions, variables, concepts, études, listes de codes)
      héritent de ces méthodes. Vous pouvez versionner n'importe quel
      élément, pas seulement l'étude de niveau supérieur.
    - **Erreur courante :** Les apprenants peuvent oublier de définir la
      version comme une chaîne à trois parties comme `"1.0.0"` avant
      d'appeler `increment_subversion()`. Si la version est juste `"1"`,
      la méthode la complétera automatiquement, mais il est plus clair de
      commencer avec trois parties.
    - **Des modifications, pas seulement des ajouts (sections 6 et 7).** La
      plupart des vraies mises à jour reformulent une question ou changent
      ses catégories de réponse. Insistez sur les quatre étapes : trouver
      l'élément, le modifier, le versionner avec une justification, faire
      pointer les références. Faites sauter la dernière étape une fois aux
      apprenants et exécuter `doc.lint()` pour qu'ils voient eux-mêmes
      l'erreur `ddi.reference.integrity`.
    - **Libellé ou sens.** Demandez si un changement de libellé garde les
      réponses comparables avec l'an dernier. Si oui, utilisez une
      sous-version ; sinon, une version majeure. La même question s'applique
      à une nouvelle liste de codes.
    - **Mises à jour en bloc (section 8).** C'est le cas réaliste pour le
      personnel des INS : le fichier de données d'une nouvelle vague arrive
      et des dizaines de variables ont besoin du même type de changement.
      Faites remarquer que l'étape 3 est un simple dictionnaire. Les
      apprenants peuvent le garder dans un tableur et le charger, pour que
      les spécialistes du domaine révisent les changements avant que
      quiconque exécute la boucle.
    - **Question de discussion :** Demandez aux apprenants comment leur
      organisation suit actuellement les changements aux instruments
      d'enquête. Comparez ce processus au versionnement DDI.
