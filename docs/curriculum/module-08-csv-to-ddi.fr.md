---
description: >-
  Module 8 du cours ddi-l : transformer une table CSV, Excel ou SQL en étude
  DDI documentée, en une ou deux langues.
---

# Module 8 : D'un tableau CSV ou Excel vers DDI

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Écrire un script qui lit l'en-tête d'un fichier CSV et crée une variable DDI par colonne, avec le texte des questions tiré d'une table de correspondance.
    - **O2.** Adapter le script pour lire les noms de colonnes d'une feuille Excel avec pandas.
    - **O3.** Ajouter des concepts et un univers au document généré et lier chaque variable mesurée à son concept.
    - **O4.** Ajouter le texte des questions dans une deuxième langue et confirmer que les deux libellés figurent dans le XML enregistré.
    - **O5.** Valider le document généré avec `doc.validate()` et corriger toute erreur signalée avant d'enregistrer.

**Prérequis :** [Module 7](module-07-cli-validation.fr.md).

**Durée :** 45 min en autonomie / 60 min avec instructeur.

**Nouveau dans ce module :** `csv.DictReader`, `reader.fieldnames`, `pd.read_excel()`, `df.columns`, `question_texts.append()`, `issue.message`, `issue.xpath`.

---

## 1. Vue d'ensemble du flux de travail

C'est le module pratique essentiel.
La plupart des chercheurs ont déjà des données dans un fichier CSV ou Excel.
Ils ont besoin de métadonnées DDI qui décrivent ces données.
Ce module enseigne le flux de travail réel :
partir des données que vous avez déjà et produire un document DDI.

!!! tip "Vous documentez déjà dans des tableurs ?"
    Ce module construit le DDI en code, une colonne à la fois. Si les
    concepts, questions, questionnaire, listes de codes, variables et
    fichiers de données de votre étude sont déjà dans des tableurs,
    disposez-les comme dans
    [Charger du DDI depuis des tableurs](../spreadsheet-import.fr.md) et
    chargez-les tous en une étape, dans autant de langues que voulu. Les
    [modèles de tableurs](../spreadsheet-templates.fr.md) sont un point de départ.

Vos données se trouvent dans un fichier CSV ou Excel.
Vous voulez des métadonnées DDI (un fichier XML) qui les décrivent.

Voici le plan :

1. Python lit les **noms de colonnes** de votre fichier de données.
2. Pour chaque colonne, il crée une **variable** dans un document DDI.
3. Vous liez les variables à des concepts, ajoutez une deuxième langue et validez.
4. Vous enregistrez le document DDI en XML.

Le fichier DDI ne contient pas les données elles-mêmes.
Il contient de la **documentation sur les données** : noms de variables, questions, concepts et plus encore.

## 2. Étape 1 : Lire les noms de colonnes d'un CSV

Un **fichier CSV** (Comma-Separated Values) est un fichier texte où chaque ligne est une rangée de données.
La première ligne contient généralement les noms de colonnes.

Python possède un module intégré appelé `csv` qui peut lire ces fichiers.
On utilise `csv.DictReader` pour obtenir les noms de colonnes.

```python
import csv

with open("survey_sample.csv") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames

print(columns)
```

**Résultat attendu :**

```text
['respondent_id', 'age', 'gender', 'income', 'education_level']
```

La variable `columns` est maintenant une liste de chaînes de caractères.
Chaque chaîne est un nom de colonne de votre fichier CSV.

!!! note "Fichier d'exemple"
    Téléchargez le fichier CSV d'exemple et enregistrez-le à côté de votre
    script, ou créez votre propre fichier avec ces colonnes :
    `respondent_id`, `age`, `gender`, `income`, `education_level`.
    Les valeurs sont en français et le fichier est encodé en UTF-8 ; les noms
    de colonnes restent ceux utilisés dans le code.

    [:material-download: Télécharger `survey_sample.csv`](survey_sample.csv){ .md-button download="survey_sample.csv" }

## 3. Étape 2 : Créer une variable par colonne

Maintenant, on utilise `ddi-l` pour construire un document DDI.
On boucle sur les noms de colonnes et on crée une variable pour chacun.

```python
import csv
import ddi_l as ddi

# Read columns from CSV
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

# Build the DDI document
doc = ddi.new_study(title="Household Survey", agency="research.org")

for col in columns:
    libelle = QUESTIONS.get(col)
    # Une colonne qu'on n'a demandée à personne, comme respondent_id, n'a pas de question
    q = doc.add_question(text=libelle, lang="fr") if libelle else None
    doc.add_variable(name=col, question=q)

doc.save("household-survey.xml")

print(f"Variables: {len(doc.variables)}")
```

**Résultat attendu :**

```text
Variables: 5
```

Ce qui s'est passé :

- On a lu 5 noms de colonnes du CSV.
- Pour chaque colonne, on a ajouté une variable.
- Les quatre colonnes qui enregistrent une réponse ont aussi reçu une question,
  formulée comme les répondants l'ont lue. `respondent_id` est attribué par
  l'équipe d'enquête, pas demandé : sa variable n'a donc pas de question.
- On a tout enregistré dans un fichier XML.

!!! tip "Pourquoi une table de correspondance ?"
    Un nom de colonne comme `education_level` est une abréviation, pas une
    question. Construire le texte à partir de lui
    (`f"Quel est le {col} du répondant ?"`) donne « Quel est le education_level
    du répondant ? », une question que personne n'a jamais posée. Copiez plutôt
    le libellé de votre questionnaire dans `QUESTIONS`, pour que les
    métadonnées décrivent ce à quoi les répondants ont vraiment répondu.

## 4. Étape 3 : Lire les colonnes depuis Excel

Si vos données sont dans un fichier Excel (`.xlsx`), vous pouvez utiliser la bibliothèque **pandas**.
Pandas est un outil Python populaire pour travailler avec des tableaux de données.

<!-- docs-test: skip -- needs pandas and a reader-supplied survey.xlsx -->
```python
import pandas as pd

df = pd.read_excel("survey.xlsx")
columns = list(df.columns)

print(columns)
```

La variable `df` est un **DataFrame** : un tableau en mémoire.
La propriété `columns` vous donne les noms de colonnes, tout comme `csv.DictReader`.
`pd.read_excel()` lit la première feuille du classeur ; passez
`sheet_name="Data"` pour lire plutôt la feuille appelée « Data ».

Après cette étape, le reste du code est le même que l'étape 2.
Bouclez sur `columns`, créez des variables et enregistrez.

!!! note "Installer pandas"
    Si vous n'avez pas pandas, installez-le avec : `pip install pandas openpyxl`

## 5. Lier les variables à des concepts et à un univers

Importer les noms de colonnes est un bon début, mais les noms bruts ne suffisent pas.
De bonnes métadonnées ont besoin de plus de détails. Après l'importation, ajoutez :

- Des **concepts** pour regrouper les variables liées (voir le [module 5](module-05-concepts-universes.fr.md)).
- Un **univers** pour indiquer qui est étudié.

Pour lier chaque variable à son concept dans la boucle, créez d'abord les
concepts et gardez une deuxième table de correspondance, `CONCEPTS`, qui donne
le concept de chaque colonne mesurée :

```python
doc = ddi.new_study(title="Household Survey", agency="research.org")

# Les concepts et l'univers d'abord, pour que la boucle puisse s'y lier
demo = doc.add_concept(name="Démographie", lang="fr")
econ = doc.add_concept(name="Économie", lang="fr")
doc.add_universe(name="Ménages canadiens, 2024", lang="fr")

# Le concept auquel appartient chaque colonne mesurée
CONCEPTS = {
    "age": demo,
    "gender": demo,
    "income": econ,
    "education_level": demo,
}

for col in columns:
    libelle = QUESTIONS.get(col)
    q = doc.add_question(text=libelle, lang="fr") if libelle else None
    # respondent_id ne mesure rien : CONCEPTS.get() retourne None, donc aucun lien
    doc.add_variable(name=col, question=q, concept=CONCEPTS.get(col))

linked = [v for v in doc.variables if v.concept_references]
print(f"Linked variables: {len(linked)}")  # -> Linked variables: 4
```

Cela transforme une simple liste de noms de colonnes en métadonnées utiles et partageables.
Les listes de codes, qui enregistrent les réponses autorisées à chaque
question, sont le sujet du [module 9](module-09-code-lists.fr.md).

## 6. Documenter en plusieurs langues

De nombreuses enquêtes servent des populations bilingues ou multilingues. Par
exemple, une enquête canadienne peut avoir besoin de métadonnées en anglais et
en français. DDI stocke plusieurs versions linguistiques dans le même document.

Au Module 3, vous avez appris que chaque méthode `add_*` accepte un argument
`lang=`. Voici comment créer un document DDI entièrement bilingue à partir
d'un fichier CSV :

```python
import csv
import ddi_l as ddi
from ddi_l.models.base import InternationalString

with open("survey_sample.csv") as f:
    columns = csv.DictReader(f).fieldnames

doc = ddi.new_study(title="Household Survey", agency="research.org")

# English and French wording for each question
QUESTIONS = {
    "age": ("How old are you?", "Quel âge avez-vous ?"),
    "gender": ("What is your gender?", "Quel est votre genre ?"),
    "income": (
        "What was your total income last year, before taxes?",
        "Quel a été votre revenu total l'an dernier, avant impôts ?",
    ),
    "education_level": (
        "What is the highest level of education you have completed?",
        "Quel est le plus haut niveau de scolarité que vous avez atteint ?",
    ),
}

for col in columns:
    q = None
    if col in QUESTIONS:
        english, french = QUESTIONS[col]
        # Create the question in English (default)...
        q = doc.add_question(text=english)
        # ...and append the French wording to the same question
        q.question_texts.append(InternationalString(text=french, lang="fr"))

    # Create the variable with an English name
    v = doc.add_variable(name=col, question=q)

    # Append the French variable name
    v.names.append(InternationalString(text=col, lang="fr", child_tag="String"))

# Bilingual concepts
demo = doc.add_concept(name="Demographics")
demo.names.append(
    InternationalString(text="Démographie", lang="fr", child_tag="String")
)

econ = doc.add_concept(name="Economics")
econ.names.append(InternationalString(text="Économie", lang="fr", child_tag="String"))

# Bilingual universe
u = doc.add_universe(name="Canadian households, 2024")
u.names.append(
    InternationalString(text="Ménages canadiens, 2024", lang="fr", child_tag="String")
)

doc.save("household-survey-bilingual.xml")
print(f"Variables: {len(doc.variables)}")
```

**Résultat attendu :**

```text
Variables: 5
```

Le processus est le même pour chaque type d'élément :

1. Créez l'élément avec `add_*()` (utilise `lang="en"` par défaut).
2. Ajoutez un `InternationalString` avec `lang="fr"` à la liste de textes
   de l'élément (`question_texts` pour les questions, `names` pour tout le
   reste).

Vous pouvez ajouter autant de langues que nécessaire. Ajoutez simplement un
`InternationalString` par langue.

Pour confirmer que les deux langues ont été enregistrées, ouvrez le fichier
XML dans un éditeur de texte : vous verrez à la fois des entrées
`xml:lang="en"` et `xml:lang="fr"` pour chaque question, variable, concept et
univers. Ou laissez Python vérifier : lisez le fichier enregistré comme du
texte et cherchez les deux libellés d'une question.

```python
from pathlib import Path

saved = Path("household-survey-bilingual.xml").read_text(encoding="utf-8")
print("How old are you?" in saved, "Quel âge avez-vous ?" in saved)  # -> True True
```

## 7. Valider avant d'enregistrer

Un script qui construit des métadonnées à partir d'un fichier peut construire
quelque chose d'invalide sans s'en apercevoir : une coquille dans une table de
correspondance suffit. Vérifiez le document avec `doc.validate()` avant de
l'enregistrer. La méthode retourne une liste de **problèmes**, vide quand le
document suit le schéma DDI. Chaque problème a :

- `issue.message` : la règle enfreinte.
- `issue.xpath` : l'endroit, sous forme de chemin depuis la racine du
  document, comme le chemin après `at` au module 7.

```python
issues = doc.validate()
if issues:
    for issue in issues:
        print(issue.message)
        print(f"  at {issue.xpath}")
else:
    doc.save("household-survey-bilingual.xml")
    print("Document is valid. Saved.")  # -> Document is valid. Saved.
```

N'enregistrez que lorsque la liste est vide ; sinon, lisez chaque message,
corrigez le script et exécutez-le à nouveau.

!!! warning "Une erreur fréquente : le code de langue"
    Les codes de langue suivent la norme BCP 47 : une langue, puis
    éventuellement une région, reliées par un **trait d'union** : `fr`,
    `fr-CA`, `en-GB`. Certains logiciels écrivent `fr_CA`, avec un trait de
    soulignement. Le schéma DDI le rejette, et `doc.validate()` signale un
    problème dont le message contient `lang='fr_CA'`.

## 8. Un script complet

Voici le pipeline complet CSV vers DDI dans un seul fichier.
Copiez-le et modifiez-le pour correspondre à vos propres données.

```python
import csv
import ddi_l as ddi

# Step 1: Read column names
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

# Step 2: Build the DDI document, with its concepts and universe
doc = ddi.new_study(title="Household Survey", agency="research.org")
demo = doc.add_concept(name="Démographie", lang="fr")
econ = doc.add_concept(name="Économie", lang="fr")
doc.add_universe(name="Ménages canadiens, 2024", lang="fr")

# Le concept auquel appartient chaque colonne mesurée
CONCEPTS = {
    "age": demo,
    "gender": demo,
    "income": econ,
    "education_level": demo,
}

# Step 3: One variable per column, linked to its question and concept
for col in columns:
    libelle = QUESTIONS.get(col)
    # Une colonne qu'on n'a demandée à personne, comme respondent_id, n'a pas de question
    q = doc.add_question(text=libelle, lang="fr") if libelle else None
    doc.add_variable(name=col, question=q, concept=CONCEPTS.get(col))

# Step 4: Validate, and save only a valid document
issues = doc.validate()
for issue in issues:
    print(issue.message)
if not issues:
    doc.save("household-survey.xml")

# Step 5: Verify
print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
print(f"Concepts: {len(doc.concepts)}")
print(f"Universes: {len(doc.universes)}")
print(f"Schema problems: {len(issues)}")
```

**Résultat attendu :**

```text
Questions: 4
Variables: 5
Concepts: 2
Universes: 1
Schema problems: 0
```

---

## Exercices

!!! example "Scénario"
    Un chercheur a un fichier CSV appelé `survey_sample.csv` provenant d'une enquête auprès des ménages.
    Il contient cinq colonnes : `respondent_id`, `age`, `gender`, `income`, `education_level`.
    Il doit créer des métadonnées DDI pour ce jeu de données.
    Votre travail est d'écrire un script Python qui lit le CSV, construit le document DDI,
    le lie à des concepts et à un univers, ajoute un libellé anglais, le valide et l'enregistre en XML.

1. **(O1)** [Téléchargez](survey_sample.csv){ download="survey_sample.csv" } ou créez `survey_sample.csv` avec ces 5 colonnes : `respondent_id`, `age`, `gender`, `income`, `education_level`. Écrivez un script qui lit le CSV, crée un document DDI avec une variable par colonne (avec le texte des questions tiré d'une table de correspondance), et l'enregistre. Affichez le compteur.

    **Résultat attendu :**

    ```text
    Variables: 5
    ```

    ??? success "Réponse"
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
        print(f"Variables: {len(doc.variables)}")  # -> Variables: 5
        ```

2. **(O2)** (Si pandas est installé) Adaptez votre script de l'exercice 1 pour lire les noms de colonnes d'une feuille Excel. Pour obtenir un classeur, convertissez une fois le CSV d'exemple avec `pd.read_csv("survey_sample.csv").to_excel("survey_sample.xlsx", index=False)`, ou enregistrez-le sous `survey_sample.xlsx` depuis votre tableur. Utilisez ensuite `pd.read_excel()` pour obtenir les colonnes, puis créez les variables de la même façon.

    **Résultat attendu :**

    ```text
    Variables: 5
    ```

    ??? success "Réponse"
        Seules les lignes qui lisent les noms de colonnes changent.
        `QUESTIONS` est la table de correspondance de l'exercice 1.

        <!-- docs-test: skip -- needs pandas, openpyxl and an Excel workbook -->
        ```python
        import pandas as pd
        import ddi_l as ddi

        # Make a workbook from the sample CSV (once)
        pd.read_csv("survey_sample.csv").to_excel("survey_sample.xlsx", index=False)

        df = pd.read_excel("survey_sample.xlsx")
        columns = list(df.columns)

        doc = ddi.new_study(title="Household Survey", agency="research.org")
        for col in columns:
            libelle = QUESTIONS.get(col)
            q = doc.add_question(text=libelle, lang="fr") if libelle else None
            doc.add_variable(name=col, question=q)
        doc.save("household-survey-excel.xml")
        print(f"Variables: {len(doc.variables)}")
        ```

3. **(O3)** Reconstruisez le document de l'exercice 1 avec trois concepts et un univers : Démographie (pour `age` et `gender`), Économie (pour `income`), Scolarité (pour `education_level`), et l'univers « Ménages canadiens, 2024 ». Liez chaque variable mesurée à son concept ; `respondent_id` n'a pas de concept. Affichez les compteurs et le nombre de variables liées.

    **Résultat attendu :**

    ```text
    Concepts: 3
    Universes: 1
    Linked variables: 4
    ```

    ??? success "Réponse"
        En reprenant l'exercice 1 (`columns` et `QUESTIONS`) :

        ```python
        doc = ddi.new_study(title="Household Survey", agency="research.org")

        demo = doc.add_concept(name="Démographie", lang="fr")
        econ = doc.add_concept(name="Économie", lang="fr")
        educ = doc.add_concept(name="Scolarité", lang="fr")
        doc.add_universe(name="Ménages canadiens, 2024", lang="fr")

        CONCEPTS = {
            "age": demo,
            "gender": demo,
            "income": econ,
            "education_level": educ,
        }

        for col in columns:
            libelle = QUESTIONS.get(col)
            q = doc.add_question(text=libelle, lang="fr") if libelle else None
            doc.add_variable(name=col, question=q, concept=CONCEPTS.get(col))

        linked = [v for v in doc.variables if v.concept_references]
        print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
        print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
        print(f"Linked variables: {len(linked)}")  # -> Linked variables: 4
        ```

4. **(O4)** Ajoutez un libellé anglais aux questions `age` et `gender` et un nom anglais au concept Démographie. Enregistrez le fichier sous `household-survey-bilingual.xml`. Lisez ensuite le fichier enregistré et confirmez que les deux libellés de la question sur l'âge s'y trouvent.

    **Résultat attendu :**

    ```text
    True True
    ```

    ??? success "Réponse"
        ```python
        from pathlib import Path

        from ddi_l.models.base import InternationalString

        # La première question porte sur l'âge du répondant, la deuxième sur son genre
        doc.questions[0].question_texts.append(
            InternationalString(text="How old are you?", lang="en")
        )
        doc.questions[1].question_texts.append(
            InternationalString(text="What is your gender?", lang="en")
        )
        doc.concepts[0].names.append(
            InternationalString(text="Demographics", lang="en", child_tag="String")
        )
        doc.save("household-survey-bilingual.xml")

        saved = Path("household-survey-bilingual.xml").read_text(encoding="utf-8")
        print("Quel âge avez-vous ?" in saved, "How old are you?" in saved)  # -> True True
        ```

        Vous pouvez aussi ouvrir le XML dans un éditeur de texte et chercher
        `xml:lang="en"` à côté du texte français.

5. **(O5)** Ce code ajoute un libellé anglais à la question sur le revenu, mais il contient une erreur. Exécutez-le et lisez le problème que signale `doc.validate()`. Corrigez ensuite l'erreur, validez à nouveau et enregistrez le document une fois qu'il est valide.

    ```python
    doc.questions[2].question_texts.append(
        InternationalString(
            text="What was your total income last year, before taxes?",
            lang="en_CA",
        )
    )
    for issue in doc.validate():
        print(issue.message)
    ```

    **Résultat attendu** (avant la correction, puis après) :

    ```text
    attribute {http://www.w3.org/XML/1998/namespace}lang='en_CA': value doesn't match any pattern of ['[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*']
    Document is valid.
    ```

    ??? success "Réponse"
        Le message nomme l'attribut `lang` et sa valeur, `en_CA`. Le motif
        `[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*` signifie des lettres, suivies
        éventuellement de groupes formés d'un **trait d'union** et de lettres
        ou de chiffres. Le trait de soulignement n'est pas permis : écrivez
        `en-CA` (ou simplement `en`) :

        ```python
        doc.questions[2].question_texts[-1].lang = "en-CA"

        issues = doc.validate()
        if issues:
            for issue in issues:
                print(issue.message)
        else:
            print("Document is valid.")  # -> Document is valid.
            doc.save("household-survey-bilingual.xml")
        ```

---

## Quiz

???+ question "Question 1 (O1) : Combien de variables le document contient-il ?"
    L'en-tête d'un CSV est `id,age,income`. Le script boucle sur
    `reader.fieldnames` et appelle `doc.add_variable(name=col, question=q)`
    une fois par colonne.

    **A.** 1

    **B.** 2, parce que `id` n'a été demandé à personne.

    **C.** 0, jusqu'à ce que vous enregistriez le document.

    **D.** 3

    ??? success "Réponse"
        **D.** La boucle ajoute une variable par colonne, et il y a trois
        colonnes. Une colonne sans question, comme `id`, reçoit quand même
        une variable.

???+ question "Question 2 (O1) : Pourquoi le script prend-il le texte des questions dans la table de correspondance QUESTIONS ?"
    L'autre façon de faire est de le construire à partir du nom de colonne,
    avec `f"Quel est le {col} du répondant ?"`.

    **A.** Python ne sait pas formater une chaîne qui contient un nom de
    colonne.

    **B.** Pour que les métadonnées enregistrent le libellé que les
    répondants ont vraiment lu, pas une phrase fabriquée à partir d'un nom de
    colonne.

    **C.** Une table de correspondance rend le script plus rapide.

    **D.** DDI ne permet pas de points d'interrogation dans un texte généré.

    ??? success "Réponse"
        **B.** Un nom de colonne comme `education_level` est une
        abréviation. Le texte de la question dans DDI doit être le libellé du
        questionnaire.

???+ question "Question 3 (O2) : Comment obtenir les noms de colonnes d'un DataFrame pandas ?"
    **A.** `df.rows`

    **B.** `df.fieldnames`

    **C.** `df.columns`

    **D.** `df.headers`

    ??? success "Réponse"
        **C.** Utilisez `df.columns` pour obtenir les noms de colonnes
        d'un DataFrame pandas. Entourez-le de `list()` pour obtenir une
        liste simple. `fieldnames` appartient à `csv.DictReader`, pas à
        pandas.

???+ question "Question 4 (O3) : Quel appel ajoute la variable income et la lie au concept Économie econ ?"
    **A.** `doc.add_variable(name="income", question=q, concept=econ)`

    **B.** `doc.add_concept(name="income", concept=econ)`

    **C.** `econ.add_variable("income")`

    **D.** `doc.add_universe(name="income")`

    ??? success "Réponse"
        **A.** Passez le concept avec `concept=` quand vous ajoutez la
        variable. Dans une boucle, `concept=CONCEPTS.get(col)` fait la même
        chose pour chaque colonne.

???+ question "Question 5 (O4) : Comment confirmer que le libellé français a été enregistré ?"
    Vous avez ajouté un libellé français à une question avec
    `q.question_texts.append(InternationalString(text=french, lang="fr"))`
    et enregistré le document.

    **A.** Comptez les variables du document.

    **B.** Exécutez `doc.validate()` : la méthode liste les langues du
    document.

    **C.** Ouvrez le fichier CSV et cherchez le texte français.

    **D.** Lisez le fichier XML enregistré et vérifiez qu'il contient le
    libellé français, à côté de `xml:lang="fr"`.

    ??? success "Réponse"
        **D.** Le XML enregistré est ce que les autres reçoivent : vérifiez-le
        donc. Ouvrez-le dans un éditeur de texte, ou lisez-le avec
        `Path(...).read_text()` et testez `"Quel âge avez-vous ?" in saved`.
        Le CSV contient des données, pas des métadonnées.

???+ question "Question 6 (O5) : doc.validate() signale ce problème. Quelle est la correction ?"
    `attribute {http://www.w3.org/XML/1998/namespace}lang='fr_CA': value doesn't match any pattern of ['[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*']`

    **A.** Écrire le code de langue avec un trait d'union, `fr-CA`, ou
    simplement `fr`.

    **B.** Retirer le texte français du document.

    **C.** Enregistrer le fichier quand même : le problème n'est qu'un
    avertissement.

    **D.** Renommer la variable qui contient la question.

    ??? success "Réponse"
        **A.** Le motif permet des lettres reliées par des traits d'union,
        pas par des traits de soulignement. Un problème de schéma rend le
        document invalide : corrigez-le avant d'enregistrer.

---

## Pour aller plus loin (facultatif)

Cette section s'adresse aux personnes qui stockent leurs données dans une
base de données SQL. Elle n'a pas d'objectif, et vous pouvez la sauter si
vous utilisez seulement des fichiers CSV ou Excel.

### Lire les noms de colonnes d'une base de données SQL

**SQL** (Structured Query Language) est un langage pour travailler avec des bases de données.
On utilise le module intégré `sqlite3` de Python pour se connecter à une base SQLite.

<!-- docs-test: skip -- needs a reader-supplied survey.db -->
```python
import sqlite3

conn = sqlite3.connect("survey.db")
cursor = conn.execute("SELECT * FROM survey LIMIT 0")
columns = [desc[0] for desc in cursor.description]

print(columns)
```

L'astuce est `LIMIT 0`.
Cela lit zéro ligne mais nous donne quand même les noms de colonnes via `cursor.description`.

Après cela, le reste est le même : bouclez sur `columns` et créez des variables.

---

## Faites le point

- [ ] Je peux écrire un script qui lit l'en-tête d'un CSV et crée une variable par colonne, avec le texte des questions tiré d'une table de correspondance. (O1)
- [ ] Je peux adapter le script pour lire les noms de colonnes d'une feuille Excel avec pandas. (O2)
- [ ] Je peux ajouter des concepts et un univers et lier chaque variable mesurée à son concept. (O3)
- [ ] Je peux ajouter le texte des questions dans une deuxième langue et confirmer que les deux libellés sont dans le XML enregistré. (O4)
- [ ] Je peux valider le document généré et corriger toute erreur signalée avant d'enregistrer. (O5)

---

!!! tip "Notes pour l'instructeur"
    - C'est le module « eurêka » pour les chercheurs et le personnel des INS. Beaucoup d'apprenants reconnaîtront leur propre flux de travail ici.
    - **Message clé :** Le CSV contient les **données**. Le XML DDI est la **documentation sur les données**. Ce sont deux fichiers distincts avec deux objectifs distincts.
    - Parcourez le script complet ligne par ligne. Laissez les apprenants taper en même temps.
    - L'exemple SQL de « Pour aller plus loin » est facultatif. Sautez-le pour les publics non techniques. Il est là pour les participants familiers avec les bases de données qui demandent « et pour SQL ? »
    - L'exercice 5 glisse un code de langue avec un trait de soulignement (`en_CA`). Beaucoup d'apprenants ont déjà vu ce style dans d'autres logiciels ; laissez-les trouver la correction à partir du message avant de l'expliquer.
    - Si le temps le permet, laissez les apprenants essayer avec leurs propres fichiers CSV. Les données réelles rendent l'exercice plus significatif.
    - Erreur fréquente : les apprenants confondent le fichier CSV avec la sortie XML. Rappelez-leur que `doc.save()` écrit des métadonnées, pas des données.

---

**Voir aussi :** [Téléchargez le fichier CSV d'exemple](survey_sample.csv){ download="survey_sample.csv" } (`survey_sample.csv`).
