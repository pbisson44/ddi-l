---
description: >-
  Module 4 du cours ddi-l : ajouter des variables et lier chacune à la
  question qui l'a collectée.
---

# Module 4 : Ajouter des variables et les associer aux questions

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Expliquer en une phrase ce qu'est une variable, en prenant une
      colonne de tableur comme exemple.
    - **O2.** Écrire un script qui ajoute une variable avec libellé pour
      chaque question avec `doc.add_variable()` et l'associe à sa question
      avec `question=`, de sorte que `doc.validate()` et `doc.lint()` ne
      signalent rien.
    - **O3.** Compter les variables avec `len(doc.variables)` et afficher
      l'identifiant de chaque variable.
    - **O4.** Expliquer en deux phrases pourquoi il est important d'associer
      une variable à sa question, en prenant une colonne de données comme
      exemple.
    - **O5.** Trouver le nom d'une variable et son lien vers sa question
      (`<r:QuestionReference>`) dans le XML sauvegardé.

**Prérequis :** [Module 3](module-03-first-study.fr.md)

**Durée :** 30 min en autonomie / 40 min avec instructeur.

**Nouveau dans ce module :** `doc.add_variable()` (avec `name=`, `label=` et
`question=`), `doc.variables`

---

## 1. Qu'est-ce qu'une variable ?

Une **variable** est comme une colonne dans un tableur. Si vous avez un
tableur de résultats d'enquête, chaque colonne contient un type d'information
pour chaque personne qui a répondu à l'enquête. Par exemple :

| Age | HealthRating | SleepHours |
| --: | -----------: | ---------: |
|  19 |            4 |          7 |
|  21 |            3 |          6 |
|  20 |            5 |          8 |

Dans ce tableau, `Age`, `HealthRating` et `SleepHours` sont les trois
variables. Chacune stocke les réponses à une question de l'enquête.

---

## 2. Le lien entre les questions et les variables

Chaque variable provient d'une question. La question demande une information,
et la variable stocke les réponses.

```text
Question: "What is your age?"   --->   Variable: Age
Question: "Rate your health?"   --->   Variable: HealthRating
Question: "Hours of sleep?"     --->   Variable: SleepHours
```

Dans DDI, vous pouvez **associer** une variable à la question qui l'a
produite. Ce lien est stocké dans le document DDI pour que toute personne
lisant les métadonnées puisse remonter d'une colonne de données jusqu'à la
question exacte qui a collecté les données.

---

## 3. Ajouter des variables associées aux questions

Reprenons l'enquête sur le bien-être étudiant du Module 3. D'abord, créez
l'étude et ajoutez les questions, chacune avec un libellé comme vous l'avez
appris au module 3 :

```python
import ddi_l as ddi

doc = ddi.new_study(
    title="Student Well-Being Survey",
    agency="university.edu",
)

q1 = doc.add_question(text="What is your age?", label="Age")
q2 = doc.add_question(text="How would you rate your health?", label="Self-rated health")
q3 = doc.add_question(
    text="How many hours do you sleep per night?", label="Hours of sleep"
)
```

Maintenant, ajoutez trois variables. Chacune est associée à une question grâce
à l'argument `question=` :

```python
v1 = doc.add_variable(name="Age", label="Age in years", question=q1)
v2 = doc.add_variable(
    name="HealthRating", label="Self-rated health, 1 to 5", question=q2
)
v3 = doc.add_variable(name="SleepHours", label="Hours of sleep per night", question=q3)
```

Ce que cela fait :

- `doc.add_variable()` crée une nouvelle variable dans l'étude.
- `name=` donne un nom court à la variable, comme un en-tête de colonne.
- `label=` lui donne un libellé lisible, comme vous l'avez fait pour les
  questions au module 3. Sans libellé, `doc.lint()` signale un
  avertissement.
- `question=` associe la variable à l'objet question qui a collecté les
  données. Notez que vous passez l'**objet question** (comme `q1`), pas la
  chaîne de texte de la question. Passer le texte, comme dans
  `question="What is your age?"`, provoque une erreur.

---

## 4. Lister toutes les variables

Vous pouvez compter les variables et les parcourir, comme vous l'avez fait
avec les questions :

```python
print(f"Variables: {len(doc.variables)}")
```

Résultat attendu :

```text
Variables: 3
```

Pour afficher l'identifiant de chaque variable :

```python
for v in doc.variables:
    print(v.identifier)
```

Chaque variable reçoit un **identifiant** unique (une étiquette attribuée par
DDI) pour qu'elle puisse être trouvée et référencée dans le document.

---

## 5. Pourquoi l'association est importante

Associer les variables aux questions crée de la **traçabilité**. La
traçabilité signifie que vous pouvez suivre le chemin de n'importe quelle
donnée jusqu'à son origine.

Imaginez que vous regardez une colonne appelée `SleepHours` dans un jeu de
données. Vous vous demandez : « Qu'est-ce que l'enquête a demandé
exactement ? » Comme la variable est associée à la question, vous pouvez
consulter la question et voir : « How many hours do you sleep per night? »

C'est important pour :

- Les **chercheurs** qui ont besoin de comprendre comment les données ont été
  collectées.
- Les **archivistes** qui préservent les données pour un usage futur.
- Les **auditeurs** qui vérifient que les données ont été collectées
  correctement.

Sans le lien, vous devriez deviner quelle question a produit quelle colonne.
Avec DDI, la connexion est claire et automatique.

---

## 6. Vérifier, sauvegarder et examiner

Vérifiez votre travail, comme vous l'avez appris au module 3, puis
sauvegardez le document complet :

```python
print(f"Problèmes de schéma : {len(doc.validate())}")
print(f"Constats de lint : {len(doc.lint())}")
doc.save("well-being.xml")
```

Résultat attendu :

```text
Problèmes de schéma : 0
Constats de lint : 0
```

Ouvrez `well-being.xml` dans un éditeur de texte. Cherchez un élément
variable. Vous devriez voir quelque chose comme :

```xml
<l:Variable>
  <r:ID>c4eefbc3-...</r:ID>
  <l:VariableName>
    <r:String xml:lang="en">Age</r:String>
  </l:VariableName>
  <r:Label>
    <r:Content xml:lang="en">Age in years</r:Content>
  </r:Label>
  <r:QuestionReference>
    <r:ID>86aed7cf-...</r:ID>
    <r:TypeOfObject>QuestionItem</r:TypeOfObject>
  </r:QuestionReference>
</l:Variable>
```

`<l:VariableName>` contient le nom. `<r:QuestionReference>` est le lien :
le `<r:ID>` qu'il contient est l'identifiant de la question `q1`, ce qui
permet au lecteur de retrouver la question exacte. `ddi-l` a créé tout cela
pour vous.

Voir aussi : [Guide utilisateur : Ajouter des variables](../user-guide.fr.md#ajouter-des-variables)

---

## Exercices

!!! example "Scénario"
    Vous poursuivez votre travail sur l'enquête sur le bien-être étudiant du
    Module 3. Le professeur vous demande maintenant de définir les colonnes de
    données (variables) et de connecter chacune à la question qui l'a
    collectée.

**Exercice 1 (O1).** Une étudiante de première année vous montre cet extrait
de son fichier de données :

| StudentID | SleepHours | ExerciseDays |
| --------- | ---------: | -----------: |
| S001      |        6.9 |            7 |
| S002      |        7.6 |            7 |
| S003      |        6.6 |            2 |

Écrivez **une phrase** qui explique ce qu'est une variable, en prenant
`SleepHours` comme exemple.

Résultat attendu : une phrase.

??? success "Réponse"
    Par exemple : « Une variable est une colonne d'un fichier de données,
    comme `SleepHours`, qui contient la réponse de chaque étudiant à la même
    question : combien d'heures il dort par nuit. »

**Exercice 2 (O2).** Continuez à partir du Module 3. Créez l'étude et
ajoutez trois questions, chacune avec un libellé. Ajoutez ensuite trois
variables, chacune avec un libellé et associée à sa question :

- `Age` associée à la question sur l'âge.
- `HealthRating` associée à la question sur la santé.
- `SleepHours` associée à la question sur le sommeil.

Vérifiez votre travail avec `doc.validate()` et `doc.lint()`.

Résultat attendu :

```text
Problèmes de schéma : 0
Constats de lint : 0
```

??? success "Réponse"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")

    q1 = doc.add_question(text="What is your age?", label="Age")
    q2 = doc.add_question(text="How would you rate your health?", label="Self-rated health")
    q3 = doc.add_question(
        text="How many hours do you sleep per night?", label="Hours of sleep"
    )

    v1 = doc.add_variable(name="Age", label="Age in years", question=q1)
    v2 = doc.add_variable(
        name="HealthRating", label="Self-rated health, 1 to 5", question=q2
    )
    v3 = doc.add_variable(name="SleepHours", label="Hours of sleep per night", question=q3)

    print(f"Problèmes de schéma : {len(doc.validate())}")  # -> Problèmes de schéma : 0
    print(f"Constats de lint : {len(doc.lint())}")  # -> Constats de lint : 0
    ```

    Si `doc.lint()` signale « Maintainable element is missing a label. »,
    l'une de vos questions ou variables n'a pas de `label=`.

**Exercice 3 (O3).** Affichez le nombre de variables, puis l'identifiant de
chaque variable à l'aide d'une boucle `for`.

Résultat attendu : `Variables: 3`, puis trois identifiants uniques, un par
ligne (les vôtres seront différents).

??? success "Réponse"
    ```python
    print(f"Variables: {len(doc.variables)}")  # -> Variables: 3
    for v in doc.variables:
        print(v.identifier)
    ```

    Chaque identifiant est un UUID, par exemple `a1b2c3d4-...`.

**Exercice 4 (O4).** Un collègue trouve la colonne `HealthRating`, avec des
valeurs de 1 à 5, dans votre fichier de données. Écrivez **deux phrases** :
ce que le lien entre `HealthRating` et sa question apprend à votre collègue,
et ce qui pourrait mal tourner si ce lien manquait.

Résultat attendu : deux phrases.

??? success "Réponse"
    Par exemple : « Le lien mène à la question "How would you rate your
    health?", donc mon collègue sait que les valeurs sont l'évaluation que
    chaque étudiant fait de sa propre santé. Sans ce lien, il pourrait se
    tromper, par exemple en croyant que les valeurs ont été mesurées par un
    médecin, ou que 1 correspond à la meilleure santé. »

**Exercice 5 (O5).** Sauvegardez le document avec
`doc.save("well-being.xml")`. Ouvrez le fichier XML dans un éditeur de texte
et trouvez l'élément `<l:Variable>` de `Age`. Notez :

1. Le nom de la variable dans `<l:VariableName>`.
2. Le `<r:ID>` dans son `<r:QuestionReference>`.

Exécutez ensuite `print(q1.identifier)` et comparez.

Résultat attendu : le nom `Age`, et un identifiant identique à celui
qu'affiche `print(q1.identifier)`.

??? success "Réponse"
    ```python
    doc.save("well-being.xml")
    print(q1.identifier)
    ```

    Le nom de la variable se trouve dans `<l:VariableName>` :

    ```xml
    <l:VariableName>
      <r:String xml:lang="en">Age</r:String>
    </l:VariableName>
    ```

    Le `<r:ID>` dans le `<r:QuestionReference>`, quelques lignes plus bas, est
    le même identifiant que celui qu'affiche `print(q1.identifier)`. Cet
    identifiant commun est le lien entre la variable et la question.

---

## Quiz

???+ question "Question 1 (O1) : Dans un tableau avec les colonnes Age, HealthRating et SleepHours, lequel de ces éléments est une variable ?"
    **A.** La ligne du premier répondant.

    **B.** La valeur 4 dans la deuxième colonne.

    **C.** La colonne `HealthRating`, qui contient la réponse de chaque
    répondant à une même question.

    **D.** Le nom de l'onglet du tableur.

    ??? success "Réponse"
        **C.** Une variable est comme une colonne. Chaque colonne contient un
        type d'information, comme une évaluation de la santé, pour chaque
        personne du jeu de données. Une ligne est une personne ; une valeur
        est une réponse.

???+ question "Question 2 (O2) : Que se passe-t-il quand vous exécutez `doc.add_variable(name='Age', question='What is your age?')` ?"
    **A.** `ddi-l` trouve la question par son texte et l'associe.

    **B.** Une erreur est levée, car `question=` attend l'objet question
    (comme `q1`), pas le texte de la question.

    **C.** La variable est créée sans lien vers une question.

    **D.** Une nouvelle question avec ce texte est créée.

    ??? success "Réponse"
        **B.** `question=` a besoin de l'objet renvoyé par
        `doc.add_question()`. Une simple chaîne n'est pas une question :
        l'appel échoue avec une `AttributeError`. Passez plutôt `q1`.

???+ question "Question 3 (O2) : Que fait `question=q2` dans `doc.add_variable(name='HealthRating', question=q2)` ?"
    **A.** Il enregistre, dans le document DDI, une référence de la variable
    vers la question `q2`.

    **B.** Il affiche le texte de la question à l'écran.

    **C.** Il supprime `q2` de l'étude.

    **D.** Il renomme la question en `HealthRating`.

    ??? success "Réponse"
        **A.** L'argument `question=` enregistre un lien entre la variable et
        la question qui a collecté les données. Vous le voyez dans le XML
        sous la forme de `<r:QuestionReference>`.

???+ question "Question 4 (O3) : Quel code affiche l'identifiant de chaque variable de l'étude ?"
    **A.** `print(doc.variables.identifier)`

    **B.** `doc.list_variables()`

    **C.** `for v in doc.questions: print(v.identifier)`

    **D.** `for v in doc.variables: print(v.identifier)`

    ??? success "Réponse"
        **D.** `doc.variables` est une liste : vous la parcourez et affichez
        l'`identifier` de chaque variable. L'option A échoue, car une liste
        n'a pas d'`identifier`, et l'option C parcourt les questions, pas
        les variables.

???+ question "Question 5 (O4) : Un utilisateur des données voit la colonne SleepHours et veut savoir exactement ce qui a été demandé. En quoi le lien entre la variable et sa question l'aide-t-il ?"
    **A.** Il convertit les heures en minutes.

    **B.** L'utilisateur peut suivre le lien jusqu'à la question « How many
    hours do you sleep per night? » au lieu de deviner.

    **C.** Il cache la colonne aux utilisateurs qui n'en ont pas besoin.

    **D.** Il réduit la taille du fichier de données.

    ??? success "Réponse"
        **B.** C'est la traçabilité : le lien mène l'utilisateur de la
        colonne de données jusqu'à la question exacte qui a collecté les
        données.

???+ question "Question 6 (O5) : Dans le XML sauvegardé, quel élément associe une variable à la question qui l'a collectée ?"
    **A.** `<l:VariableName>`

    **B.** `<r:Agency>`

    **C.** `<r:QuestionReference>`

    **D.** `<d:QuestionText>`

    ??? success "Réponse"
        **C.** `<r:QuestionReference>` se trouve dans l'élément
        `<l:Variable>` et contient l'identifiant de la question.
        `<l:VariableName>` contient le nom de la variable, et
        `<d:QuestionText>` appartient à la question elle-même.

---

## Faites le point

- [ ] Je peux expliquer en une phrase ce qu'est une variable, en prenant une
  colonne de tableur comme exemple. (O1)
- [ ] Je peux écrire un script qui ajoute une variable avec libellé pour
  chaque question et l'associe avec `question=`, de sorte que
  `doc.validate()` et `doc.lint()` ne signalent rien. (O2)
- [ ] Je peux compter les variables avec `len(doc.variables)` et afficher
  l'identifiant de chaque variable. (O3)
- [ ] Je peux expliquer en deux phrases pourquoi il est important d'associer
  une variable à sa question. (O4)
- [ ] Je peux trouver le nom d'une variable et son `<r:QuestionReference>`
  dans le XML sauvegardé. (O5)

---

!!! tip "Notes pour l'instructeur"
    - **Aide visuelle :** Dessinez ce schéma au tableau ou à l'écran :
      `Question --> Variable --> Colonne de données`. Parcourez un exemple :
      « What is your age? » mène à la variable `Age`, qui devient la colonne
      `Age` dans le tableur.
    - **Erreur courante :** Les apprenants passent parfois le texte de la
      question (une chaîne comme `"What is your age?"`) au lieu de l'objet
      question (`q1`). Rappelez-leur que `question=` attend l'objet renvoyé
      par `doc.add_question()`, pas le texte.
    - **Vérification pratique :** Après les exercices 2 et 3, demandez aux
      apprenants de partager leur résultat. Tout le monde devrait voir
      `Constats de lint : 0` et `Variables: 3`.
    - **Activité d'approfondissement :** Demandez aux plus rapides d'ajouter
      une quatrième question et une quatrième variable, puis de vérifier, de
      sauvegarder et d'examiner le XML mis à jour.
    - **Renforcer le concept :** Demandez au groupe : « Si vous n'aviez que
      le fichier de données sans lien avec les questions, comment sauriez-vous
      ce que chaque colonne signifie ? » Cela fait comprendre la valeur de la
      traçabilité (exercice 4).
