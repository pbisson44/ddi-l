---
description: >-
  Module 9 du cours ddi-l : construire des listes de codes et des
  catégories, et les générer à partir des valeurs d'une colonne.
---

# Module 9 : Construire des listes de codes et des vocabulaires contrôlés

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Expliquer en deux phrases ce que sont une liste de codes et une catégorie, et pourquoi deux enquêtes qui partagent une liste de codes peuvent être comparées.
    - **O2.** Écrire un script qui crée des listes de codes avec `doc.add_code_list()` et ajoute leurs catégories avec `doc.add_item(Category, name=...)`.
    - **O3.** Écrire une boucle sur `doc.items(Category)` qui affiche le nom de chaque catégorie, et prédire les compteurs que renvoient `len(doc.code_lists)` et `len(doc.items(Category))`.
    - **O4.** Écrire un script qui lit les valeurs distinctes d'une colonne CSV et crée une catégorie pour chaque valeur.

**Prérequis :** [Module 8](module-08-csv-to-ddi.fr.md).

**Durée :** 40 min en autonomie / 50 min avec instructeur.

**Nouveau dans ce module :** `doc.add_code_list()`, `doc.code_lists`, `Category`, `doc.add_item()`, `doc.items()`, `item.names[0].text`.

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

!!! note "Catégories et codes"
    `doc.add_item(Category, ...)` ajoute la catégorie à l'étude. Elle ne la
    place pas encore dans une liste de codes précise. Dans ce module, vous
    construisez les listes de codes et leurs catégories côte à côte.
    Le [module 14](module-14-custom-fields.fr.md) montre comment placer chaque
    catégorie dans sa liste sous forme de **code** (une valeur comme `1` qui
    pointe vers la catégorie).

## 5. La méthode add_item()

La méthode `add_item()` est un outil général.
Elle fonctionne pour tout type d'élément DDI, pas seulement les catégories.

Le modèle est toujours le même :

<!-- docs-test: skip -- SomeType is a placeholder for any registered item type -->
```python
doc.add_item(SomeType, name="Some Name")
```

Vous passez le **type** comme premier argument et le **nom** comme argument nommé.
C'est ainsi que vous ajoutez des éléments qui n'ont pas leur propre méthode pratique comme `add_question()` ou `add_variable()`.

## 6. Interroger les éléments par type

Utilisez `doc.items(Category)` pour obtenir la liste de toutes les catégories du document.

```python
all_categories = doc.items(Category)
print(f"Total categories: {len(all_categories)}")  # -> Total categories: 10

for cat in all_categories:
    print(f"  - {cat.names[0].text}")
```

Chaque élément garde ses noms dans une liste appelée `names`, car un élément
peut avoir un nom dans plusieurs langues. `names[0]` est le premier nom, et
`.text` est son texte. La boucle affiche `Male`, `Female`, `Other`, et ainsi de
suite, dans l'ordre où vous les avez ajoutées.

Cela fonctionne pour tout type enregistré.
Passez le type que vous voulez, et vous obtenez la liste de tous les éléments de ce type.

## 7. Construire des listes de codes à partir des valeurs d'une colonne CSV

Dans le module 8, vous avez appris à lire les colonnes d'un fichier CSV.
Vous pouvez aller plus loin : lire les **valeurs uniques** d'une colonne et les transformer en catégories.

C'est utile quand vos données contiennent déjà des réponses codées.
Les exemples utilisent le fichier d'exemple du module 8 :

[:material-download: Télécharger `survey_sample.csv`](survey_sample.csv){ .md-button download="survey_sample.csv" }

<!-- docs-test: skip -- needs pandas, which ddi-l does not depend on -->
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

Sans pandas, le module `csv` intégré à Python et un `set` font le même travail :
un `set` ne garde qu'une copie de chaque valeur. L'exercice 5 utilise cette
approche.

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

---

## Exercices

1. **(O1)** Un collègue demande pourquoi le recensement devrait réutiliser la liste de codes du statut d'emploi de l'enquête sur la population active de l'an dernier, au lieu de laisser les intervieweurs taper chaque réponse. Écrivez votre réponse en deux phrases.

    ??? success "Réponse"
        Une réponse possible : « Une liste de codes est l'ensemble fixe des
        réponses autorisées à une question, et chaque réponse autorisée (comme
        Employed ou Retired) est une catégorie. Si le recensement utilise la
        même liste de codes que l'enquête sur la population active, chaque
        réponse tombe dans les mêmes catégories dans les deux enquêtes ; on peut
        donc les compter et les comparer directement, au lieu de nettoyer du
        texte libre comme « M », « empl. » ou « travaille ». »

2. **(O2)** Créez une étude de recensement avec le titre « National Census » et l'agence « census.gc.ca ». Ajoutez 3 listes de codes (Gender Codes, Employment Status Codes, Housing Type Codes) et leurs catégories (10 au total). Affichez les compteurs.

    **Résultat attendu :**

    ```text
    Code lists: 3
    Categories: 10
    ```

    ??? success "Réponse"
        ```python
        import ddi_l as ddi
        from ddi_l.models.logicalproduct import Category

        doc = ddi.new_study(title="National Census", agency="census.gc.ca")

        doc.add_code_list(name="Gender Codes")
        doc.add_item(Category, name="Male")
        doc.add_item(Category, name="Female")
        doc.add_item(Category, name="Other")

        doc.add_code_list(name="Employment Status Codes")
        doc.add_item(Category, name="Employed")
        doc.add_item(Category, name="Unemployed")
        doc.add_item(Category, name="Retired")
        doc.add_item(Category, name="Student")

        doc.add_code_list(name="Housing Type Codes")
        doc.add_item(Category, name="House")
        doc.add_item(Category, name="Apartment")
        doc.add_item(Category, name="Other Housing")

        print(f"Code lists: {len(doc.code_lists)}")
        print(f"Categories: {len(doc.items(Category))}")
        ```

3. **(O3)** Listez tous les noms de catégories. Bouclez sur `doc.items(Category)` et affichez le nom de chaque catégorie.

    **Résultat attendu :**

    ```text
    Male
    Female
    Other
    Employed
    Unemployed
    Retired
    Student
    House
    Apartment
    Other Housing
    ```

    ??? success "Réponse"
        ```python
        for cat in doc.items(Category):
            print(cat.names[0].text)
        ```

        Les catégories reviennent dans l'ordre où vous les avez ajoutées.

4. **(O2, O3)** Le recensement pose aussi une question sur l'état matrimonial. Ajoutez une liste de codes « Marital Status Codes » avec quatre catégories : Single, Married, Separated, Widowed. **Avant d'exécuter votre script**, notez les deux compteurs qu'il affichera. Puis exécutez-le et vérifiez votre prédiction.

    **Résultat attendu :**

    ```text
    Code lists: 4
    Categories: 14
    ```

    ??? success "Réponse"
        ```python
        doc.add_code_list(name="Marital Status Codes")
        for status in ("Single", "Married", "Separated", "Widowed"):
            doc.add_item(Category, name=status)

        print(f"Code lists: {len(doc.code_lists)}")
        print(f"Categories: {len(doc.items(Category))}")
        ```

        Une nouvelle liste de codes donne 3 + 1 = 4. Quatre nouvelles
        catégories donnent 10 + 4 = 14. Les compteurs couvrent tout le
        document, pas seulement la dernière liste ajoutée.

5. **(O4)** Générez des catégories à partir des valeurs uniques d'une colonne CSV. Lisez [`survey_sample.csv`](survey_sample.csv){ download="survey_sample.csv" }, obtenez les valeurs uniques de la colonne `education_level`, et créez une catégorie pour chacune.

    **Résultat attendu :**

    ```text
    Education levels: 4
    ```

    ??? success "Réponse"
        Le module `csv` intégré à Python suffit ; un `set` ne garde qu'une copie de
        chaque valeur :

        ```python
        import csv

        with open("survey_sample.csv") as f:
            levels = sorted({row["education_level"] for row in csv.DictReader(f)})

        doc.add_code_list(name="Education Level Codes")
        for level in levels:
            doc.add_item(Category, name=level)

        print(f"Education levels: {len(levels)}")
        ```

        Le fichier a cinq lignes mais seulement quatre niveaux distincts, car
        « Baccalauréat » apparaît deux fois. Avec pandas,
        `df["education_level"].dropna().unique()` donne les mêmes valeurs,
        comme à la section 7.

---

## Quiz

???+ question "Question 1 (O1) : Pourquoi l'enquête 2 est-elle plus facile à comparer ?"
    L'enquête 1 laisse les intervieweurs taper le statut d'emploi en texte
    libre. L'enquête 2 utilise la liste de codes Employed / Unemployed /
    Retired / Student. Pourquoi l'enquête 2 est-elle plus facile à comparer
    avec d'autres enquêtes ?

    **A.** Son fichier de données est plus petit.

    **B.** Python a besoin d'une liste de codes avant d'enregistrer une variable.

    **C.** DDI ne peut pas stocker de réponses en texte libre.

    **D.** Chaque réponse fait partie d'un ensemble fixe de catégories, donc une autre enquête qui utilise la même liste de codes compte exactement les mêmes réponses.

    ??? success "Réponse"
        **D.** Une liste de codes fixe les réponses autorisées. Deux enquêtes
        qui la partagent placent chaque réponse dans les mêmes catégories, donc
        leurs comptes concordent. Du texte libre comme « M », « empl. » ou
        « travaille » doit d'abord être nettoyé.

???+ question "Question 2 (O2) : Quelle correction permet à ce script de s'exécuter ?"
    Un script appelle `doc.add_item(Category, name="Male")` et s'arrête avec
    `NameError: name 'Category' is not defined`. Quelle correction lui permet
    de s'exécuter ?

    **A.** Ajouter `from ddi_l.models.logicalproduct import Category` au début du script.

    **B.** Remplacer l'appel par `doc.add_category(name="Male")`.

    **C.** Appeler plutôt `doc.add_code_list(name="Male")`.

    **D.** Mettre le type entre guillemets : `doc.add_item("Category", name="Male")`.

    ??? success "Réponse"
        **A.** `Category` est une classe qu'il faut importer avant de l'utiliser.
        `doc.add_category()` n'existe pas, `add_code_list()` créerait une liste
        de codes nommée « Male », et `add_item()` a besoin de la classe
        elle-même, pas de son nom sous forme de chaîne.

???+ question "Question 3 (O3) : Qu'affiche ce script ?"
    ```python
    import ddi_l as ddi
    from ddi_l.models.logicalproduct import Category

    census = ddi.new_study(title="Census", agency="example.org")
    census.add_code_list(name="Yes/No")
    census.add_item(Category, name="Yes")
    census.add_item(Category, name="No")
    census.add_code_list(name="Tenure")
    census.add_item(Category, name="Owner")
    census.add_item(Category, name="Renter")
    census.add_item(Category, name="Other")
    print(len(census.code_lists), len(census.items(Category)))
    ```

    **A.** `2 2`

    **B.** `5 5`

    **C.** `2 5`

    **D.** `7 0`

    ??? success "Réponse"
        **C.** Le script crée deux listes de codes et cinq catégories.
        `items(Category)` compte toutes les catégories du document, quelle que
        soit la liste à laquelle vous les destiniez.

???+ question "Question 4 (O3) : Quelle boucle affiche le nom de chaque catégorie de `doc` ?"
    **A.** `for cat in doc.code_lists: print(cat.names[0].text)`

    **B.** `for cat in doc.items(Category): print(cat.names[0].text)`

    **C.** `for cat in doc.categories: print(cat)`

    **D.** `for cat in doc.items("Category"): print(cat.identifier)`

    ??? success "Réponse"
        **B.** `doc.items(Category)` renvoie toutes les catégories, et
        `names[0].text` est le premier nom de chacune. L'option A affiche les
        noms des listes de codes, `doc.categories` n'existe pas, et `items()`
        prend la classe, pas une chaîne.

???+ question "Question 5 (O4) : Combien de catégories une colonne CSV donne-t-elle ?"
    Une colonne CSV `gender` contient Femme, Homme, Femme, (vide), Autre,
    Homme. Vous gardez une copie de chaque valeur, ignorez la valeur vide et
    ajoutez une catégorie par valeur. Combien de catégories ajoutez-vous ?

    **A.** 3

    **B.** 4

    **C.** 5

    **D.** 6

    ??? success "Réponse"
        **A.** Les valeurs distinctes non vides sont Femme, Homme et Autre.
        Avec pandas, `df["gender"].dropna().unique()` renvoie exactement ces
        trois valeurs.

---

## Faites le point

- [ ] Je peux expliquer en deux phrases ce que sont une liste de codes et une catégorie, et pourquoi une liste de codes partagée rend des enquêtes comparables. (O1)
- [ ] Je peux écrire un script qui crée des listes de codes avec `doc.add_code_list()` et ajoute des catégories avec `doc.add_item(Category, name=...)`. (O2)
- [ ] Je peux écrire une boucle sur `doc.items(Category)` qui affiche le nom de chaque catégorie, et prédire ce que renvoient `len(doc.code_lists)` et `len(doc.items(Category))`. (O3)
- [ ] Je peux écrire un script qui transforme les valeurs distinctes d'une colonne CSV en catégories. (O4)

---

!!! tip "Notes pour l'instructeur"
    - Commencez en demandant : « Avez-vous déjà vu un menu déroulant dans une enquête ? Ce menu déroulant est une liste de codes. »
    - Montrez un exemple réel : le menu déroulant du genre sur un formulaire gouvernemental. Faites remarquer que les choix sont fixes. C'est un vocabulaire contrôlé.
    - Le modèle `add_item()` peut sembler abstrait. Rappelez aux apprenants : « Vous dites à Python quel type créer et comment le nommer. »
    - L'exercice 4 demande de prédire avant d'exécuter. Recueillez d'abord quelques prédictions. Une erreur courante est `Categories: 4`, chez les apprenants qui pensent que le compteur ne couvre que la nouvelle liste.
    - L'exercice 5 relie le module 8 (CSV) au module 9 (listes de codes). Les apprenants plus rapides peuvent le refaire pour la colonne `gender`.
    - Si les apprenants demandent comment une catégorie entre dans une liste de codes précise dans le XML DDI : chaque liste contient des **codes**, et chaque code pointe vers une catégorie. Le [module 14](module-14-custom-fields.fr.md) les construit. Pour l'instant, les apprenants créent les listes et les catégories côte à côte.

---

**Voir aussi :** [Guide utilisateur : Listes de codes](../user-guide.fr.md#ajouter-des-listes-de-codes) | [Guide utilisateur : Tout type d'élément](../user-guide.fr.md#travailler-avec-nimporte-quel-type-delement)
