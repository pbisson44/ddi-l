---
description: >-
  Module 5 du cours ddi-l : regrouper les variables sous des concepts et
  décrire la population couverte avec des univers.
---

# Module 5 : Organiser avec les concepts et les univers

!!! info "Ce que vous apprendrez"
    - Comprendre ce qu'est un **concept** et pourquoi il est important.
    - Comprendre ce qu'est un **univers** et pourquoi il est important.
    - Ajouter des concepts et des univers à un document DDI.
    - Lier une variable à un concept.
    - Lister tous les concepts et univers d'un document.

**Prérequis :** Module 4.

**Durée :** 30 min en autonomie / 40 min avec instructeur.

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

## 6. Lister les concepts et les univers

Utilisez `doc.concepts` et `doc.universes` pour voir tous les éléments du document.

```python
print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
```

Ces propriétés retournent des listes.
Vous pouvez les parcourir pour afficher les noms ou faire d'autres opérations.

---

!!! example "Scénario"
    Une autorité nationale de santé interroge des adultes sur leur alimentation et leur activité physique.
    Elle a besoin de trois concepts : **Nutrition**, **Physical Activity** et **Demographics**.
    L'univers est **Adultes de 18 ans et plus au Canada**.
    Votre travail est de construire cette structure en code.

---

## Exercices

**Exercice 1.** Documentez une enquête nationale sur la santé.

1. Créez un document d'enquête de santé avec le titre « National Health Survey » et l'agence « health.gc.ca ».

2. Ajoutez quatre questions :
    - « How old are you? »
    - « What is your weight in kg? »
    - « How many days per week do you exercise? »
    - « How many servings of fruit do you eat per day? »

3. Ajoutez trois concepts : Demographics, Physical Activity, Nutrition.

4. Ajoutez un univers : Adults aged 18+ in Canada.

5. Ajoutez quatre variables. Liez chacune à son concept correspondant :
    - Age -> Demographics
    - Weight -> Demographics
    - Exercise Frequency -> Physical Activity
    - Fruit Servings -> Nutrition

6. Affichez les compteurs :

```python
print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
print(f"Concepts: {len(doc.concepts)}")
print(f"Universes: {len(doc.universes)}")
```

**Résultat attendu :**

```text
Questions: 4
Variables: 4
Concepts: 3
Universes: 1
```

Vérifiez ensuite votre travail : `doc.validate()` doit renvoyer une liste vide.

??? success "Réponse"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")

    q1 = doc.add_question(text="How old are you?")
    q2 = doc.add_question(text="What is your weight in kg?")
    q3 = doc.add_question(text="How many days per week do you exercise?")
    q4 = doc.add_question(text="How many servings of fruit do you eat per day?")

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
    print(f"Schema problems: {len(doc.validate())}")
    ```

---

## Quiz

???+ question "Question 1 : Qu'est-ce qu'un concept ?"
    **A.** Un format de fichier pour les enquêtes.

    **B.** Une idée abstraite que mesure une variable.

    **C.** Une liste de réponses autorisées.

    **D.** Le groupe de personnes étudiées.

    ??? success "Réponse"
        **B.** Un concept est une idée abstraite, comme « Demographics »
        ou « Nutrition ». Les variables mesurent des concepts.

???+ question "Question 2 : Qu'est-ce qu'un univers ?"
    **A.** Le logiciel qui exécute l'enquête.

    **B.** Un type de variable.

    **C.** Le groupe de personnes ou de choses étudiées.

    **D.** Une liste de questions.

    ??? success "Réponse"
        **C.** L'univers indique qui l'enquête couvre, par exemple,
        « Adultes de 18 ans et plus au Canada ».

???+ question "Question 3 : Comment liez-vous une variable à un concept ?"
    **A.** `doc.add_concept(variable=v)`

    **B.** `doc.add_variable(name="Age", concept=age_concept)`

    **C.** `doc.link(variable, concept)`

    **D.** `variable.set_concept(concept)`

    ??? success "Réponse"
        **B.** Passez l'argument `concept=` quand vous appelez
        `doc.add_variable()`.

---

!!! tip "Notes pour l'instructeur"
    - Dessinez un diagramme au tableau : le concept en haut, avec des flèches pointant vers ses variables. Cela aide les apprenants visuels.
    - Demandez à la classe : « Si vous aviez une enquête sur les écoles, quel serait votre univers ? » (par ex., « Toutes les écoles publiques de l'Ontario ».)
    - Erreur fréquente : les étudiants oublient de garder l'objet concept dans une variable. Rappelez-leur que `doc.add_concept()` retourne quelque chose qu'ils doivent conserver.
    - Insistez sur le fait que les concepts et les univers servent à **décrire** les données ; ils ne changent pas les données elles-mêmes.

---

**Voir aussi :** [Guide utilisateur : Concepts et univers](../user-guide.md#ajouter-des-concepts-et-des-univers)
