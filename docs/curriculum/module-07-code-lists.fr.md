# Module 7 : Construire des listes de codes et des vocabulaires contrôlés

!!! info "Ce que vous apprendrez"
    - Comprendre ce qu'est une **liste de codes** et pourquoi elle est importante.
    - Créer des listes de codes avec `doc.add_code_list()`.
    - Ajouter des catégories avec `doc.add_item(Category, name=)`.
    - Interroger toutes les catégories avec `doc.items(Category)`.
    - Importer `Category` depuis `ddi_l.models.logicalproduct`.
    - Importer `Instrument` depuis `ddi_l.models.datacollection`.
    - Construire des listes de codes à partir des valeurs d'une colonne CSV.

**Prérequis :** Module 6.

**Durée :** 40 min en autonomie / 50 min avec instructeur.

---

## 1. Qu'est-ce qu'une liste de codes ?

Une **liste de codes** est un ensemble de réponses autorisées pour une question.
On l'appelle aussi un **vocabulaire contrôlé**.

Par exemple, la question « Quel est votre genre ? » pourrait autoriser ces réponses :

- Male
- Female
- Other

Cet ensemble de trois réponses est une liste de codes.
Chaque réponse dans la liste s'appelle une **catégorie**.

## 2. Pourquoi les listes de codes sont importantes

Les listes de codes gardent vos données cohérentes.
Sans elles, une personne pourrait taper « M » et une autre « Male ».
Les données deviennent désordonnées et difficiles à analyser.

Les listes de codes rendent aussi les enquêtes **comparables**.
Si deux enquêtes utilisent la même liste de codes pour le statut d'emploi, on peut comparer leurs résultats.

Les enquêtes nationales partagent souvent des listes de codes standardisées pour que les données de différents pays puissent être combinées.

## 3. Créer une liste de codes

Utilisez `doc.add_code_list(name=)` pour créer une nouvelle liste de codes.

```python
import ddi_l as ddi

doc = ddi.new_study(title="National Census", agency="census.gc.ca")

cl_gender = doc.add_code_list(name="Gender Codes")
cl_employment = doc.add_code_list(name="Employment Status Codes")
cl_housing = doc.add_code_list(name="Housing Type Codes")

print(f"Code lists: {len(doc.code_lists)}")  # -> Code lists: 3
```

Chaque appel crée une liste de codes et l'ajoute au document.

## 4. Ajouter des catégories

Une **catégorie** est une réponse autorisée dans une liste de codes.
Pour ajouter des catégories, utilisez `doc.add_item()` avec le type `Category`.

D'abord, importez `Category` :

```python
from ddi_l.models.logicalproduct import Category
```

Ensuite, ajoutez les catégories une par une :

```python
# Gender categories
doc.add_item(Category, name="Male")
doc.add_item(Category, name="Female")
doc.add_item(Category, name="Other")

# Employment status categories
doc.add_item(Category, name="Employed")
doc.add_item(Category, name="Unemployed")
doc.add_item(Category, name="Retired")
doc.add_item(Category, name="Student")

# Housing type categories
doc.add_item(Category, name="House")
doc.add_item(Category, name="Apartment")
doc.add_item(Category, name="Other Housing")

print(f"Categories: {len(doc.items(Category))}")  # -> Categories: 10
```

## 5. La méthode add_item()

La méthode `add_item()` est un outil général.
Elle fonctionne pour tout type d'élément DDI, pas seulement les catégories.

Le modèle est toujours le même :

```python
doc.add_item(SomeType, name="Some Name")
```

Vous passez le **type** comme premier argument et le **nom** comme argument nommé.
C'est ainsi que vous ajoutez des éléments qui n'ont pas leur propre méthode pratique comme `add_question()` ou `add_variable()`.

## 6. Interroger les éléments par type

Utilisez `doc.items(Category)` pour obtenir la liste de toutes les catégories du document.

```python
all_categories = doc.items(Category)
print(f"Total categories: {len(all_categories)}")

for cat in all_categories:
    print(f"  - {cat.identifier}")
```

Cela fonctionne pour tout type enregistré.
Passez le type que vous voulez, et vous obtenez la liste de tous les éléments de ce type.

## 7. Construire des listes de codes à partir des valeurs d'une colonne CSV

Dans le module 6, vous avez appris à lire les colonnes d'un fichier CSV.
Vous pouvez aller plus loin : lire les **valeurs uniques** d'une colonne et les transformer en catégories.

C'est utile quand vos données contiennent déjà des réponses codées.
Les exemples utilisent le fichier d'exemple du module 6 :

[:material-download: Télécharger `survey_sample.csv`](survey_sample.csv){ .md-button download="survey_sample.csv" }

```python
import pandas as pd

df = pd.read_csv("survey_sample.csv")

# Get unique values from the "gender" column
unique_genders = df["gender"].dropna().unique()
print(unique_genders)  # -> ['Femme' 'Homme' 'Autre']

# Create a code list and add one category per unique value
cl = doc.add_code_list(name="Gender Codes")
for val in unique_genders:
    doc.add_item(Category, name=str(val))

print(f"Categories: {len(doc.items(Category))}")
```

L'appel `dropna()` supprime les valeurs manquantes.
L'appel `unique()` retourne seulement les valeurs distinctes, sans doublons.

## 8. Exemple concret

Les instituts nationaux de statistique utilisent des listes de codes standardisées pour la classification des emplois.
Par exemple, la Classification internationale type des professions (CITP) définit des centaines de catégories d'emploi.

Quand plusieurs pays utilisent la même liste de codes, leurs données d'emploi peuvent être comparées.
C'est la force des vocabulaires contrôlés : ils rendent les données interopérables.

Avec `ddi-l`, vous construisez ces listes de codes de la même manière : une catégorie à la fois, ou en les important depuis un fichier de données.

---

!!! example "Scénario"
    Vous construisez des métadonnées pour un recensement national.
    Vous avez besoin de listes de codes pour **Gender** (Male, Female, Other),
    **Employment Status** (Employed, Unemployed, Retired, Student)
    et **Housing Type** (House, Apartment, Other).
    Vous devez aussi ajouter un élément Instrument pour représenter le questionnaire.

---

## Exercices

1. Créez une étude de recensement avec le titre « National Census » et l'agence « census.gc.ca ». Ajoutez 3 listes de codes (Gender Codes, Employment Status Codes, Housing Type Codes) et leurs catégories (10 au total). Affichez les compteurs.

    **Résultat attendu :**

    ```text
    Code lists: 3
    Categories: 10
    ```

2. Listez tous les noms de catégories. Bouclez sur `doc.items(Category)` et affichez l'identifiant de chacune.

    ```python
    from ddi_l.models.logicalproduct import Category

    for cat in doc.items(Category):
        print(cat.identifier)
    ```

3. Ajoutez un élément Instrument pour représenter le questionnaire du recensement.

    ```python
    from ddi_l.models.datacollection import Instrument

    doc.add_item(Instrument, name="Census Questionnaire")
    print(f"Instruments: {len(doc.items(Instrument))}")
    ```

    **Résultat attendu :**

    ```text
    Instruments: 1
    ```

4. (Bonus) Générez automatiquement des catégories à partir des valeurs uniques d'une colonne CSV. Lisez [`survey_sample.csv`](survey_sample.csv){ download="survey_sample.csv" }, obtenez les valeurs uniques de la colonne `education_level`, et créez une catégorie pour chacune.

---

## Quiz

???+ question "Question 1 : Qu'est-ce qu'une liste de codes ?"
    **A.** Un script Python.

    **B.** Un ensemble de réponses autorisées pour une question.

    **C.** Une liste de noms de colonnes.

    **D.** Un type de fichier CSV.

    ??? success "Réponse"
        **B.** Une liste de codes définit les réponses autorisées pour
        une question. Par exemple, « Male / Female / Other » pour le
        genre.

???+ question "Question 2 : Comment ajouter une catégorie à un document ?"
    **A.** `doc.add_category(name="Male")`

    **B.** `doc.add_item(Category, name="Male")`

    **C.** `doc.add_code_list(category="Male")`

    **D.** `Category.add("Male")`

    ??? success "Réponse"
        **B.** Utilisez `doc.add_item(Category, name="Male")`. Vous
        devez d'abord importer `Category` depuis
        `ddi_l.models.logicalproduct`.

???+ question "Question 3 : Comment obtenir toutes les catégories d'un document ?"
    **A.** `doc.categories`

    **B.** `doc.get_categories()`

    **C.** `doc.items(Category)`

    **D.** `doc.code_lists`

    ??? success "Réponse"
        **C.** Utilisez `doc.items(Category)` pour obtenir la liste de
        tous les éléments Category. Cela fonctionne pour tout type DDI
        enregistré.

???+ question "Question 4 : Pourquoi les listes de codes sont-elles importantes ?"
    **A.** Elles réduisent la taille du fichier.

    **B.** Elles sont requises par Python.

    **C.** Elles gardent les données cohérentes et rendent les enquêtes
    comparables.

    **D.** Elles accélèrent l'ordinateur.

    ??? success "Réponse"
        **C.** Les listes de codes empêchent les réponses désordonnées
        et incohérentes. Elles permettent aussi à différentes enquêtes
        de partager le même ensemble de valeurs autorisées, rendant les
        données comparables.

---

!!! tip "Notes pour l'instructeur"
    - Commencez en demandant : « Avez-vous déjà vu un menu déroulant dans une enquête ? Ce menu déroulant est une liste de codes. »
    - Montrez un exemple réel : le menu déroulant du genre sur un formulaire gouvernemental. Faites remarquer que les choix sont fixes. C'est un vocabulaire contrôlé.
    - Le modèle `add_item()` peut sembler abstrait. Rappelez aux apprenants : « Vous dites à Python quel type créer et comment le nommer. »
    - L'exercice 4 (bonus) relie le module 6 (CSV) au module 7 (listes de codes). C'est un excellent objectif supplémentaire pour les apprenants plus rapides.
    - Si les apprenants demandent comment lier les catégories aux listes de codes au niveau du XML DDI : c'est un sujet avancé. Pour l'instant, ils doivent juste savoir comment créer les deux.

---

**Voir aussi :** [Guide utilisateur : Listes de codes](../user-guide.md#ajouter-des-listes-de-codes) | [Guide utilisateur : Tout type d'élément](../user-guide.md#travailler-avec-nimporte-quel-type-delement)
