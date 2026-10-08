# Module 4 : Ajouter des variables et les associer aux questions

!!! info "Ce que vous apprendrez"
    - Définir ce qu'est une variable dans DDI.
    - Créer des variables avec `doc.add_variable()`.
    - Associer chaque variable à la question dont elle provient.
    - Lister les variables avec `doc.variables`.
    - Expliquer pourquoi associer les questions aux variables est important.

**Prérequis :** [Module 3 : Créer votre première étude DDI](module-03-first-study.md)

**Durée :** 30 min en autonomie / 40 min avec instructeur.

**API enseignée :** `doc.add_variable(name=, question=)`, `doc.variables`

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
l'étude et ajoutez les questions :

```python
import ddi_l as ddi

doc = ddi.new_study(
    title="Student Well-Being Survey",
    agency="university.edu",
)

q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")
```

Maintenant, ajoutez trois variables. Chacune est associée à une question grâce
à l'argument `question=` :

```python
v1 = doc.add_variable(name="Age", question=q1)
v2 = doc.add_variable(name="HealthRating", question=q2)
v3 = doc.add_variable(name="SleepHours", question=q3)
```

Ce que cela fait :

- `doc.add_variable()` crée une nouvelle variable dans l'étude.
- `name=` donne un nom court à la variable, comme un en-tête de colonne.
- `question=` associe la variable à l'objet question qui a collecté les
  données. Notez que vous passez l'**objet question** (comme `q1`), pas la
  chaîne de texte de la question.

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

## 6. Sauvegarder et examiner

Sauvegardez le document complet :

```python
doc.save("well-being.xml")
```

Ouvrez `well-being.xml` dans un éditeur de texte. Cherchez un élément
variable. Vous devriez voir quelque chose comme :

```xml
<l:Variable>
  <l:VariableName>
    <r:String>Age</r:String>
  </l:VariableName>
</l:Variable>
```

Le XML contient aussi la référence qui associe chaque variable à sa question.
`ddi-l` a créé tout cela pour vous.

Voir aussi : [Guide utilisateur : Ajouter des variables](../user-guide.md#ajouter-des-variables)

---

## Exercices

!!! example "Scénario"
    Vous poursuivez votre travail sur l'enquête sur le bien-être étudiant du
    Module 3. Le professeur vous demande maintenant de définir les colonnes de
    données (variables) et de connecter chacune à la question qui l'a
    collectée.

**Exercice 1.** Continuez à partir du Module 3. Créez l'étude, ajoutez trois
questions, puis ajoutez trois variables associées à ces questions :

- `Age` associée à la question sur l'âge.
- `HealthRating` associée à la question sur la santé.
- `SleepHours` associée à la question sur le sommeil.

Affichez le nombre de variables.

```python
import ddi_l as ddi

doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")

q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")

v1 = doc.add_variable(name="Age", question=q1)
v2 = doc.add_variable(name="HealthRating", question=q2)
v3 = doc.add_variable(name="SleepHours", question=q3)

print(f"Variables: {len(doc.variables)}")
```

Résultat attendu :

```text
Variables: 3
```

**Exercice 2.** Affichez l'identifiant de chaque variable à l'aide d'une
boucle for :

```python
for v in doc.variables:
    print(v.identifier)
```

Vous devriez voir trois identifiants uniques affichés, un par ligne.

**Exercice 3.** Sauvegardez le document avec `doc.save("well-being.xml")`.
Ouvrez le fichier XML dans un éditeur de texte. Pouvez-vous trouver un
élément `<l:Variable>` ? Notez le nom de la variable que vous voyez dans le
XML.

---

## Quiz

???+ question "Question 1 : Que fait l'argument question= dans doc.add_variable() ?"
    **A.** Il affiche le texte de la question à l'écran.

    **B.** Il associe la variable à cette question pour que DDI enregistre la
    connexion.

    **C.** Il supprime la question de l'étude.

    **D.** Il renomme la question.

    ??? success "Réponse"
        **B.** L'argument `question=` crée un lien dans le document DDI entre
        la variable et la question qui a collecté les données.

???+ question "Question 2 : Comment lister toutes les variables d'une étude ?"
    **A.** `doc.list_variables()`

    **B.** `doc.get_vars()`

    **C.** `doc.variables`

    **D.** `ddi.variables(doc)`

    ??? success "Réponse"
        **C.** `doc.variables` renvoie la liste de toutes les variables de
        l'étude. Vous pouvez utiliser `len(doc.variables)` pour les compter.

???+ question "Question 3 : Une variable est comme _____ dans un tableur."
    **A.** Une ligne

    **B.** Une cellule

    **C.** Une colonne

    **D.** Un nom de feuille

    ??? success "Réponse"
        **C.** Une variable est comme une colonne. Chaque colonne contient un
        type d'information (comme l'âge ou le revenu) pour chaque personne du
        jeu de données.

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
    - **Vérification pratique :** Après l'exercice 1, demandez aux apprenants
      de partager leur résultat. Tout le monde devrait voir `Variables: 3`.
    - **Activité d'approfondissement :** Demandez aux plus rapides d'ajouter
      une quatrième question et une quatrième variable, puis de sauvegarder
      et d'examiner le XML mis à jour.
    - **Renforcer le concept :** Demandez au groupe : « Si vous n'aviez que
      le fichier de données sans lien avec les questions, comment sauriez-vous
      ce que chaque colonne signifie ? » Cela fait comprendre la valeur de la
      traçabilité.
