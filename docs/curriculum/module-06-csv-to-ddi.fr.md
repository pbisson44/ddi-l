# Module 6 : D'un tableau CSV ou Excel vers DDI

!!! info "Ce que vous apprendrez"
    - Lire les noms de colonnes d'un fichier CSV avec Python.
    - Créer automatiquement une variable DDI pour chaque colonne.
    - Faire la même chose à partir d'un fichier Excel avec pandas.
    - (Optionnel) Lire les noms de colonnes d'une base de données SQL.
    - Enrichir les métadonnées avec des concepts, des univers et des listes de codes.
    - Écrire un script complet CSV vers DDI.

**Prérequis :** Module 5.

**Durée :** 45 min en autonomie / 60 min avec instructeur.

---

## Pourquoi ce module est important

C'est le module pratique essentiel.
La plupart des chercheurs ont déjà des données dans un fichier CSV ou Excel.
Ils ont besoin de métadonnées DDI qui décrivent ces données.

Ce module enseigne le flux de travail réel :
partir des données que vous avez déjà et produire un document DDI.

---

## 1. Vue d'ensemble du flux de travail

Vos données se trouvent dans un fichier CSV ou Excel.
Vous voulez des métadonnées DDI (un fichier XML) qui les décrivent.

Voici le plan :

1. Python lit les **noms de colonnes** de votre fichier de données.
2. Pour chaque colonne, il crée une **variable** dans un document DDI.
3. Vous enregistrez le document DDI en XML.

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

## 4. Étape 3 : Faire la même chose depuis Excel

Si vos données sont dans un fichier Excel (`.xlsx`), vous pouvez utiliser la bibliothèque **pandas**.
Pandas est un outil Python populaire pour travailler avec des tableaux de données.

```python
import pandas as pd

df = pd.read_excel("survey.xlsx")
columns = list(df.columns)

print(columns)
```

La variable `df` est un **DataFrame** : un tableau en mémoire.
La propriété `columns` vous donne les noms de colonnes, tout comme `csv.DictReader`.

Après cette étape, le reste du code est le même que l'étape 2.
Bouclez sur `columns`, créez des variables et enregistrez.

!!! note "Installer pandas"
    Si vous n'avez pas pandas, installez-le avec : `pip install pandas openpyxl`

## 5. Étape 4 (optionnel) : Lire depuis une base de données SQL

Cette section est pour les utilisateurs avancés qui stockent leurs données dans une base de données SQL.
Vous pouvez la sauter si vous utilisez seulement des fichiers CSV ou Excel.

**SQL** (Structured Query Language) est un langage pour travailler avec des bases de données.
On utilise le module intégré `sqlite3` de Python pour se connecter à une base SQLite.

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

## 6. Enrichir les métadonnées

Importer les noms de colonnes est un bon début, mais les noms bruts ne suffisent pas.
De bonnes métadonnées ont besoin de plus de détails.

Après l'importation, vous devriez ajouter :

- Des **concepts** pour regrouper les variables liées (voir Module 5).
- Des **univers** pour indiquer qui est étudié.
- Des **listes de codes** pour définir les réponses autorisées (voir Module 7).

```python
# Add concepts
demo = doc.add_concept(name="Demographics")
econ = doc.add_concept(name="Economics")

# Add a universe
doc.add_universe(name="Canadian households, 2024")

# Link variables to concepts (you would do this for each variable)
```

Cet enrichissement transforme une simple liste de noms de colonnes en métadonnées utiles et partageables.

## 7. Documenter en plusieurs langues

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

doc = ddi.new_study(title="Household Survey", agency="statcan.gc.ca")

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

Ouvrez le fichier XML sauvegardé. Vous verrez à la fois des entrées
`xml:lang="en"` et `xml:lang="fr"` pour chaque question, variable, concept
et univers.

Le processus est le même pour chaque type d'élément :

1. Créez l'élément avec `add_*()` (utilise `lang="en"` par défaut).
2. Ajoutez un `InternationalString` avec `lang="fr"` à la liste de textes
   de l'élément (`question_texts` pour les questions, `names` pour tout le
   reste).

Vous pouvez ajouter autant de langues que nécessaire. Ajoutez simplement un
`InternationalString` par langue.

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

# Step 2: Build the DDI document
doc = ddi.new_study(title="Household Survey", agency="research.org")

for col in columns:
    libelle = QUESTIONS.get(col)
    # Une colonne qu'on n'a demandée à personne, comme respondent_id, n'a pas de question
    q = doc.add_question(text=libelle, lang="fr") if libelle else None
    doc.add_variable(name=col, question=q)

# Step 3: Enrich
doc.add_concept(name="Demographics")
doc.add_concept(name="Economics")
doc.add_universe(name="Canadian households, 2024")

# Step 4: Save
doc.save("household-survey.xml")

# Step 5: Verify
print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
print(f"Concepts: {len(doc.concepts)}")
print(f"Universes: {len(doc.universes)}")
```

**Résultat attendu :**

```text
Questions: 4
Variables: 5
Concepts: 2
Universes: 1
```

---

!!! example "Scénario"
    Un chercheur a un fichier CSV appelé `survey_sample.csv` provenant d'une enquête auprès des ménages.
    Il contient cinq colonnes : `respondent_id`, `age`, `gender`, `income`, `education_level`.
    Il doit créer des métadonnées DDI pour ce jeu de données.
    Votre travail est d'écrire un script Python qui lit le CSV, construit le document DDI,
    l'enrichit avec des concepts et un univers, et l'enregistre en XML.

---

## Exercices

1. [Téléchargez](survey_sample.csv){ download="survey_sample.csv" } ou créez `survey_sample.csv` avec ces 5 colonnes : `respondent_id`, `age`, `gender`, `income`, `education_level`. Écrivez un script qui lit le CSV, crée un document DDI avec une variable par colonne, et l'enregistre. Affichez le compteur.

    **Résultat attendu :**

    ```text
    Variables: 5
    ```

2. (Si pandas est installé) Faites la même chose à partir d'un fichier Excel. Utilisez `pd.read_excel()` pour obtenir les colonnes, puis créez les variables de la même façon.

3. Enrichissez votre document : ajoutez un concept pour chaque variable et un univers. Validez le document et enregistrez-le.

    ```python
    issues = doc.validate()
    if issues:
        for issue in issues:
            print(issue.message)
    else:
        print("Document is valid!")
    doc.save("household-survey-enriched.xml")
    ```

4. (Bilingue) Ajoutez des traductions françaises à au moins 2 questions et 1 concept de votre document. Enregistrez le fichier et ouvrez le XML pour vérifier que les deux langues apparaissent.

    ```python
    from ddi_l.models.base import InternationalString

    # Add French text to the first question
    q = doc.questions[0]
    q.question_texts.append(
        InternationalString(text="Quel est l'identifiant du répondant ?", lang="fr")
    )
    doc.save("household-survey-bilingual.xml")
    ```

---

## Quiz

???+ question "Question 1 : Que vous donne csv.DictReader ?"
    **A.** Le fichier CSV entier sous forme d'une grande chaîne de
    caractères.

    **B.** Un objet lecteur dont la propriété `fieldnames` liste les
    noms de colonnes.

    **C.** Une liste de nombres.

    **D.** Un document XML.

    ??? success "Réponse"
        **B.** `csv.DictReader` lit un fichier CSV. Sa propriété
        `fieldnames` retourne les noms de colonnes de la première ligne.

???+ question "Question 2 : Comment obtenir les noms de colonnes d'un DataFrame pandas ?"
    **A.** `df.rows`

    **B.** `df.fieldnames`

    **C.** `df.columns`

    **D.** `df.headers`

    ??? success "Réponse"
        **C.** Utilisez `df.columns` pour obtenir les noms de colonnes
        d'un DataFrame pandas. Entourez-le de `list()` pour obtenir une
        liste simple.

???+ question "Question 3 : Que produit le script ?"
    **A.** Un fichier CSV avec de nouvelles données.

    **B.** Un fichier DDI XML avec des métadonnées sur les données.

    **C.** Une copie du CSV original.

    **D.** Une base de données SQL.

    ??? success "Réponse"
        **B.** Le script produit un fichier DDI XML. Ce fichier décrit
        les données (noms de variables, questions, concepts) mais ne
        contient pas les données elles-mêmes.

???+ question "Question 4 : Pourquoi devriez-vous ajouter des concepts après avoir importé les colonnes ?"
    **A.** Les concepts suppriment les colonnes.

    **B.** Python l'exige.

    **C.** Les concepts regroupent les variables et rendent les
    métadonnées plus utiles et organisées.

    **D.** Le fichier ne s'enregistrera pas sans concepts.

    ??? success "Réponse"
        **C.** Les concepts regroupent les variables liées entre elles.
        Sans eux, vous n'avez qu'une liste plate de noms. Les concepts
        ajoutent du sens et de la structure.

---

!!! tip "Notes pour l'instructeur"
    - C'est le module « eurêka » pour les chercheurs et le personnel des INS. Beaucoup d'apprenants reconnaîtront leur propre flux de travail ici.
    - **Message clé :** Le CSV contient les **données**. Le XML DDI est la **documentation sur les données**. Ce sont deux fichiers distincts avec deux objectifs distincts.
    - Parcourez le script complet ligne par ligne. Laissez les apprenants taper en même temps.
    - La section SQL (étape 4) est optionnelle. Sautez-la pour les publics non techniques. Elle est là pour les participants familiers avec les bases de données qui demandent « et pour SQL ? »
    - Si le temps le permet, laissez les apprenants essayer avec leurs propres fichiers CSV. Les données réelles rendent l'exercice plus significatif.
    - Erreur fréquente : les apprenants confondent le fichier CSV avec la sortie XML. Rappelez-leur que `doc.save()` écrit des métadonnées, pas des données.

---

**Voir aussi :** [Téléchargez le fichier CSV d'exemple](survey_sample.csv){ download="survey_sample.csv" } (`survey_sample.csv`).
