---
description: >-
  Module 5 du cours ddi-l : regrouper les variables sous des concepts et
  décrire la population couverte avec des univers.
---

# Module 5 : Organiser avec les concepts et les univers

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Expliquer, en une phrase chacun, ce que décrivent un **concept** et un **univers**, et classer des exemples de phrases en concepts et en univers.
    - **O2.** Ajouter des concepts et un univers à un document avec `doc.add_concept()` et `doc.add_universe()`.
    - **O3.** Lier chaque variable au concept qu'elle mesure en passant `concept=` à `doc.add_variable()`, et vérifier le lien.
    - **O4.** Afficher les noms de tous les concepts et univers d'un document, avec `doc.concepts` et `doc.universes`.

**Prérequis :** [Module 4](module-04-variables.fr.md).

**Durée :** 30 min en autonomie / 40 min avec instructeur.

**Nouveau dans ce module :** `doc.add_concept()`, `doc.add_universe()`, l'argument `concept=` de `doc.add_variable()`, `doc.concepts`, `doc.universes`, `concept_references`, `names[0].text`.

---

## 1. Qu'est-ce qu'un concept ?

Un **concept** est une idée abstraite que mesure une variable.
Pensez-y comme une étiquette pour un groupe de variables liées.

Par exemple, la variable « Age » mesure le concept « Démographie ».
La variable « Portions de fruits par jour » mesure le concept « Nutrition ».

Les concepts vous aident à organiser votre enquête.
Quand quelqu'un lit vos métadonnées, il peut rapidement voir quelles variables vont ensemble.

## 2. Qu'est-ce qu'un univers ?

Un **univers** est le groupe de personnes ou de choses étudiées.
Il répond à la question : « Qui cette enquête couvre-t-elle ? »

Par exemple : « Adultes de 18 ans et plus au Canada. »

Une enquête a généralement un seul univers, mais certaines enquêtes étudient plus d'un groupe.

!!! tip "Concept ou univers ? Un test rapide"
    Posez deux questions sur une phrase :

    - Dit-elle **ce qui** est mesuré ? C'est alors un concept (« Nutrition », « Qualité du sommeil »).
    - Dit-elle **qui ou quoi** est mesuré ? C'est alors un univers (« Adultes de 18 ans et plus au Canada », « Écoles publiques de l'Ontario »).

## 3. Ajouter des concepts

Utilisez `doc.add_concept(name=)` pour ajouter un concept à votre document.
La méthode retourne un objet concept que vous pouvez utiliser plus tard.

```python
import ddi_l as ddi

doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")

demo = doc.add_concept(name="Demographics")
activity = doc.add_concept(name="Physical Activity")
nutrition = doc.add_concept(name="Nutrition")

print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
```

Chaque appel crée un concept et l'ajoute au document.
On garde la valeur de retour dans une variable pour pouvoir la lier plus tard.

## 4. Ajouter des univers

Utilisez `doc.add_universe(name=)` pour ajouter un univers.

```python
doc.add_universe(name="Adults aged 18+ in Canada")

print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
```

Le nom doit décrire clairement qui est étudié.

## 5. Lier une variable à un concept

Quand vous ajoutez une variable, vous pouvez passer un argument `concept=`.
Cela lie la variable à ce concept dans les métadonnées DDI.

```python
q1 = doc.add_question(text="How old are you?")
q2 = doc.add_question(text="How many days per week do you exercise?")
q3 = doc.add_question(text="How many servings of fruit do you eat per day?")

doc.add_variable(name="Age", question=q1, concept=demo)
doc.add_variable(name="Exercise Frequency", question=q2, concept=activity)
doc.add_variable(name="Fruit Servings", question=q3, concept=nutrition)

print(f"Variables: {len(doc.variables)}")  # -> Variables: 3
```

Maintenant, chaque variable est connectée à son concept.
Toute personne qui lit le fichier DDI peut voir que « Age » appartient à « Demographics ».

Pour vérifier un lien, regardez la liste `concept_references` de la variable.
Chaque entrée est une **référence** : un pointeur qui contient l'identifiant
du concept. Si l'identifiant correspond à celui du concept, le lien est bon :

```python
age = doc.variables[0]
print(age.concept_references[0].identifier == demo.identifier)  # -> True
```

Une variable ajoutée sans `concept=` a une liste `concept_references` vide.

## 6. Lister les concepts et les univers

Utilisez `doc.concepts` et `doc.universes` pour voir tous les éléments du document.

```python
print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
```

Ces propriétés retournent des listes : vous pouvez donc les parcourir.
Chaque élément garde son nom dans une liste appelée `names`, avec une entrée par langue.
`names[0].text` est le texte du premier nom :

```python
for concept in doc.concepts:
    print(concept.names[0].text)
```

Résultat attendu :

```text
Demographics
Physical Activity
Nutrition
```

---

## Exercices

!!! example "Scénario"
    Une autorité nationale de santé interroge des adultes sur leur alimentation et leur activité physique.
    Elle a besoin de trois concepts : **Nutrition**, **Physical Activity** et **Demographics**.
    L'univers est **Adultes de 18 ans et plus au Canada**.
    Votre travail est de construire cette structure en code.

**Exercice 1 (O1).** Pour chaque phrase ci-dessous, écrivez « concept » ou
« univers ». Écrivez ensuite une phrase qui explique ce que décrit un concept
et une phrase qui explique ce que décrit un univers.

- Nutrition
- Adultes de 18 ans et plus au Canada
- Qualité du sommeil
- Écoles publiques de l'Ontario
- Emploi
- Enfants de 6 à 11 ans vivant dans des ménages privés

??? success "Réponse"
    - Nutrition : concept.
    - Adultes de 18 ans et plus au Canada : univers.
    - Qualité du sommeil : concept.
    - Écoles publiques de l'Ontario : univers.
    - Emploi : concept.
    - Enfants de 6 à 11 ans vivant dans des ménages privés : univers.

    Un concept est l'idée que mesure une variable, comme « Nutrition ».
    Un univers est le groupe de personnes ou de choses que couvre une étude,
    comme « Adultes de 18 ans et plus au Canada ».

**Exercice 2 (O2).** Créez un document avec le titre « National Health
Survey » et l'agence « health.gc.ca ». Ajoutez trois concepts (Demographics,
Physical Activity, Nutrition) et un univers (Adults aged 18+ in Canada).
Gardez chaque concept dans une variable Python : vous les lierez à
l'exercice 3. Affichez les compteurs.

**Résultat attendu :**

```text
Concepts: 3
Universes: 1
```

??? success "Réponse"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")

    demo = doc.add_concept(name="Demographics")
    activity = doc.add_concept(name="Physical Activity")
    nutrition = doc.add_concept(name="Nutrition")

    doc.add_universe(name="Adults aged 18+ in Canada")

    print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
    print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
    ```

**Exercice 3 (O3).** Continuez avec le même document.

1. Ajoutez quatre questions :
    - « How old are you? »
    - « What is your weight in kg? »
    - « How many days per week do you exercise? »
    - « How many servings of fruit do you eat per day? »

2. Ajoutez quatre variables. Liez chacune à son concept correspondant :
    - Age -> Demographics
    - Weight -> Demographics
    - ExerciseFrequency -> Physical Activity
    - FruitServings -> Nutrition

3. Vérifiez que Weight est liée à Demographics, puis vérifiez le document
   par rapport au schéma avec `doc.validate()`.

**Résultat attendu :**

```text
Questions: 4
Variables: 4
Weight is linked to Demographics: True
Schema problems: 0
```

??? success "Réponse"
    ```python
    q1 = doc.add_question(text="How old are you?")
    q2 = doc.add_question(text="What is your weight in kg?")
    q3 = doc.add_question(text="How many days per week do you exercise?")
    q4 = doc.add_question(text="How many servings of fruit do you eat per day?")

    doc.add_variable(name="Age", question=q1, concept=demo)
    weight = doc.add_variable(name="Weight", question=q2, concept=demo)
    doc.add_variable(name="ExerciseFrequency", question=q3, concept=activity)
    doc.add_variable(name="FruitServings", question=q4, concept=nutrition)

    linked = weight.concept_references[0].identifier == demo.identifier

    print(f"Questions: {len(doc.questions)}")  # -> Questions: 4
    print(f"Variables: {len(doc.variables)}")  # -> Variables: 4
    print(f"Weight is linked to Demographics: {linked}")
    print(f"Schema problems: {len(doc.validate())}")  # -> Schema problems: 0
    ```

**Exercice 4 (O4).** Affichez le nom de chaque concept et de chaque univers
du document, sous un titre pour chaque type.

**Résultat attendu :**

```text
Concepts:
  Demographics
  Physical Activity
  Nutrition
Universes:
  Adults aged 18+ in Canada
```

??? success "Réponse"
    ```python
    print("Concepts:")
    for concept in doc.concepts:
        print(f"  {concept.names[0].text}")

    print("Universes:")
    for universe in doc.universes:
        print(f"  {universe.names[0].text}")
    ```

---

## Quiz

???+ question "Question 1 (O1) : Quelle phrase est l'univers de cette étude ?"
    Un rapport dit : « Nous avons interrogé des adultes de 18 ans et plus au
    Canada sur la qualité de leur sommeil et leur stress. »

    **A.** Adultes de 18 ans et plus au Canada

    **B.** Qualité du sommeil

    **C.** Stress

    **D.** La question « Combien d'heures dormez-vous ? »

    ??? success "Réponse"
        **A.** L'univers dit qui est étudié. « Qualité du sommeil » et
        « Stress » disent ce qui est mesuré : ce sont des concepts. Une
        question n'est ni l'un ni l'autre.

???+ question "Question 2 (O1) : Quelle phrase explique correctement un concept ?"
    **A.** Un concept est le groupe de personnes que couvre une étude.

    **B.** Un concept est une liste de réponses autorisées.

    **C.** Un concept est l'idée que mesure une variable, comme
    « Nutrition » ; plusieurs variables peuvent partager un même concept.

    **D.** Un concept est un format de fichier pour les enquêtes.

    ??? success "Réponse"
        **C.** Un concept est une idée abstraite que mesurent des variables.
        L'option A décrit un univers et l'option B, une liste de codes.

???+ question "Question 3 (O2) : Qu'affiche ce code ?"
    ```python
    doc = ddi.new_study(title="Sleep Study", agency="example.org")
    doc.add_concept(name="Sleep quality")
    doc.add_concept(name="Stress")
    doc.add_universe(name="Adults aged 18+ in Canada")
    print(len(doc.concepts), len(doc.universes))
    ```

    **A.** `3 0`

    **B.** `1 2`

    **C.** `0 0`

    **D.** `2 1`

    ??? success "Réponse"
        **D.** Deux appels à `doc.add_concept()` ajoutent deux concepts, et
        un appel à `doc.add_universe()` ajoute un univers.

???+ question "Question 4 (O3) : La variable Age n'est pas liée à son concept. Quel appel corrige le problème ?"
    Après `age = doc.add_variable(name="Age", question=q1)`,
    `age.concept_references` est une liste vide.

    **A.** `doc.add_variable(name="Age", question=q1, universe=demo)`

    **B.** `doc.add_variable(name="Age", question=q1, concept=demo)`

    **C.** `doc.add_concept(name="Age", variable=q1)`

    **D.** `doc.link(q1, demo)`

    ??? success "Réponse"
        **B.** Passez le concept avec `concept=` quand vous appelez
        `doc.add_variable()`. Les autres appels n'existent pas.

???+ question "Question 5 (O4) : Quelle boucle affiche le nom de chaque univers ?"
    **A.** `for u in doc.universes: print(u)`

    **B.** `print(doc.universes.names)`

    **C.** `for u in doc.universes: print(u.names[0].text)`

    **D.** `for u in doc.concepts: print(u.names[0].text)`

    ??? success "Réponse"
        **C.** Chaque univers garde son nom dans `names` ; `names[0].text`
        en est le texte. L'option A affiche l'objet entier, l'option B échoue
        parce qu'une liste n'a pas de `names`, et l'option D parcourt les
        concepts.

---

## Faites le point

- [ ] Je peux expliquer, en une phrase chacun, ce que décrivent un concept et un univers, et classer des phrases dans l'un ou l'autre. (O1)
- [ ] Je peux ajouter des concepts et un univers avec `doc.add_concept()` et `doc.add_universe()`. (O2)
- [ ] Je peux lier une variable à son concept avec `concept=` et vérifier le lien. (O3)
- [ ] Je peux afficher les noms de tous les concepts et univers d'un document. (O4)

---

!!! tip "Notes pour l'instructeur"
    - Dessinez un diagramme au tableau : le concept en haut, avec des flèches pointant vers ses variables. Cela aide les apprenants visuels.
    - Demandez à la classe : « Si vous aviez une enquête sur les écoles, quel serait votre univers ? » (par ex., « Toutes les écoles publiques de l'Ontario ».)
    - Faites de l'exercice 1 un sondage rapide en classe avant que quiconque écrive du code. Le test « quoi ou qui » de la section 2 règle la plupart des désaccords.
    - Erreur fréquente : les étudiants oublient de garder l'objet concept dans une variable. Rappelez-leur que `doc.add_concept()` retourne quelque chose qu'ils doivent conserver.
    - Insistez sur le fait que les concepts et les univers servent à **décrire** les données ; ils ne changent pas les données elles-mêmes.

---

**Voir aussi :** [Guide utilisateur : Concepts et univers](../user-guide.fr.md#ajouter-des-concepts-et-des-univers)
