# Module 3 : Créer votre première étude DDI

!!! info "Ce que vous apprendrez"
    - Créer une nouvelle étude DDI avec `ddi.new_study()`.
    - Ajouter des questions d'enquête avec `doc.add_question()`.
    - Lister les questions avec `doc.questions`.
    - Sauvegarder l'étude dans un fichier XML avec `doc.save()`.

**Prérequis :** [Module 2 : Préparer votre environnement Python](module-02-setup.md)

**Durée :** 30 min en autonomie / 45 min avec instructeur.

**API enseignée :** `ddi.new_study()`, `doc.add_question()`, `doc.questions`,
`doc.save()`

---

## 1. Qu'est-ce qu'une « étude » dans DDI ?

Une **étude** est un conteneur qui rassemble toutes les informations sur une
enquête ou un projet de recherche. Pensez-y comme un dossier qui garde tout
ensemble : le titre, l'organisation qui a mené l'enquête, les questions
posées et les données collectées.

Dans `ddi-l`, vous créez d'abord une étude, puis vous y ajoutez des
éléments (comme des questions et des variables).

---

## 2. Créer une étude

Ouvrez une session Python ou créez un nouveau fichier script. Tapez le code
suivant :

```python
import ddi_l as ddi

doc = ddi.new_study(
    title="Student Well-Being Survey",
    agency="university.edu",
)
```

Ce que cela fait :

- `import ddi_l as ddi` charge le paquet `ddi-l` et lui donne le nom
  court `ddi`.
- `ddi.new_study()` crée un nouveau document DDI. Il renvoie un objet
  **Document**, que nous stockons dans la variable appelée `doc`.
- `title=` définit le nom de l'étude.
- `agency=` définit l'organisation responsable de l'étude.

---

## 3. Qu'est-ce qu'une « agency » ?

Une **agency** (agence) est l'organisation responsable de l'étude. Ce peut
être une université, un ministère, un institut de recherche ou tout groupe qui
mène l'enquête. Exemples :

- `"university.edu"` : une université
- `"statistics.gc.ca"` : Statistique Canada
- `"worldbank.org"` : La Banque mondiale

La valeur de l'agence est généralement écrite sous forme de nom de domaine.
Elle aide à identifier qui a créé le document.

---

## 4. Ajouter des questions

Une enquête pose des questions. Dans DDI, chaque question est stockée comme un
élément distinct. Ajoutons trois questions à notre étude :

```python
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")
```

Chaque appel à `doc.add_question()` crée une nouvelle question dans l'étude
et renvoie un **objet question**. Nous sauvegardons chaque objet dans une
variable (`q1`, `q2`, `q3`) pour pouvoir l'utiliser plus tard, par exemple,
pour y associer une variable.

---

## 5. Questions en plusieurs langues

De nombreuses enquêtes sont menées dans plus d'une langue. Par exemple, une
enquête canadienne peut être en anglais et en français. DDI peut stocker la
même question en plusieurs langues dans un seul document.

Chaque appel à `add_question()` accepte un argument `lang=`. La valeur par
défaut est `lang="en"` (anglais). Pour créer une question en français,
passez `lang="fr"` :

```python
q1 = doc.add_question(text="What is your age?", lang="en")
```

Pour ajouter une traduction française de la même question, ajoutez-la à la
liste `question_texts` de la question :

```python
from ddi_l.models.base import InternationalString

q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
```

Maintenant `q1` contient le texte de la question en anglais et en français.
Quand quelqu'un ouvre le fichier DDI, il peut voir les deux versions.

L'argument `lang=` fonctionne sur toutes les méthodes `add_*` :
`add_variable()`, `add_concept()`, `add_universe()` et `add_code_list()`.
Vous pouvez aussi ajouter des traductions à leur liste `names` de la même
façon. Le module 6 montre un flux de travail bilingue complet.

---

## 6. Vérifier vos questions

Vous pouvez voir combien de questions l'étude contient :

```python
print(f"Questions: {len(doc.questions)}")
```

Résultat attendu :

```text
Questions: 3
```

Vous pouvez aussi parcourir toutes les questions et afficher leurs
identifiants :

```python
for q in doc.questions:
    print(q.identifier)
```

Un **identifiant** est une étiquette unique que DDI attribue à chaque élément.
Il vous aide à trouver et à référencer des éléments précis dans le document.

---

## 7. Sauvegarder en XML

Pour sauvegarder votre étude dans un fichier, utilisez la méthode `save()` :

```python
doc.save("well-being.xml")
```

Cela crée un fichier appelé `well-being.xml` dans votre dossier courant. Le
fichier contient votre étude au format DDI XML, un format de texte structuré
qui respecte la norme DDI.

---

## 8. Regarder à l'intérieur du XML

Ouvrez `well-being.xml` dans un éditeur de texte (comme Notepad, VS Code, ou
tout autre éditeur de texte brut). Vous verrez des balises XML : des mots
entourés de chevrons comme `<QuestionItemName>`.

Cherchez le texte de votre première question. Vous devriez trouver quelque
chose comme :

```xml
<d:QuestionText>
  <d:LiteralText>
    <d:Text>What is your age?</d:Text>
  </d:LiteralText>
</d:QuestionText>
```

Vous n'avez pas besoin de comprendre tout le XML. L'important est que
`ddi-l` a transformé vos cinq lignes de Python en un document DDI complet
et conforme à la norme.

Voir aussi : [Guide utilisateur : Créer une étude](../user-guide.md#creer-une-etude)

---

## Exercices

!!! example "Scénario"
    Vous êtes assistant de recherche. Votre professeur vous demande de
    documenter une enquête sur le bien-être étudiant avec trois questions
    sur l'âge, la santé et le sommeil. Vous allez utiliser `ddi-l` pour
    créer la documentation.

**Exercice 1.** Créez une étude intitulée `"Student Well-Being Survey"` avec
l'agence `"university.edu"`. Ajoutez trois questions :

1. `"What is your age?"`
2. `"How would you rate your health?"`
3. `"How many hours do you sleep per night?"`

Sauvegardez l'étude sous `well-being.xml`. Affichez le nombre de questions.

```python
import ddi_l as ddi

doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")

q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")

print(f"Questions: {len(doc.questions)}")
doc.save("well-being.xml")
```

Résultat attendu :

```text
Questions: 3
```

**Exercice 2.** Ouvrez `well-being.xml` dans un éditeur de texte. Pouvez-vous
trouver le texte de votre première question dans le XML ? Notez la balise XML
qui entoure le texte de la question.

**Exercice 3.** Ajoutez une traduction française à la première question. Puis
sauvegardez à nouveau le fichier et vérifiez dans le XML que les deux langues
apparaissent.

```python
from ddi_l.models.base import InternationalString

q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
doc.save("well-being.xml")
```

Ouvrez le XML. Vous devriez voir à la fois `xml:lang="en"` et `xml:lang="fr"`
pour la première question.

---

## Quiz

???+ question "Question 1 : Que renvoie ddi.new_study() ?"
    **A.** Une chaîne de texte XML.

    **B.** Un objet Document qui représente l'étude.

    **C.** Une liste de questions.

    **D.** Un fichier CSV.

    ??? success "Réponse"
        **B.** `ddi.new_study()` renvoie un objet Document. Vous utilisez cet
        objet pour ajouter des questions, des variables et d'autres éléments
        à l'étude.

???+ question "Question 2 : Que fait doc.add_question() ?"
    **A.** Elle envoie une question aux répondants de l'enquête.

    **B.** Elle ajoute une question à l'étude et renvoie un objet question.

    **C.** Elle affiche une question à l'écran.

    **D.** Elle supprime une question de l'étude.

    ??? success "Réponse"
        **B.** `doc.add_question()` ajoute un nouvel élément question à
        l'étude DDI. Elle renvoie l'objet question pour que vous puissiez
        l'utiliser plus tard.

???+ question "Question 3 : Que fait doc.save() ?"
    **A.** Elle envoie le fichier sur Internet.

    **B.** Elle imprime le document sur papier.

    **C.** Elle écrit l'étude dans un fichier XML sur votre ordinateur.

    **D.** Elle valide le document.

    ??? success "Réponse"
        **C.** `doc.save("filename.xml")` écrit le document DDI dans un
        fichier XML dans votre dossier courant.

???+ question "Question 4 : Comment ajouter une traduction française à une question ?"
    **A.** `doc.add_question(text="...", lang="fr")`. Cela crée une
    nouvelle question séparée en français.

    **B.** Ajouter un `InternationalString` avec `lang="fr"` à la liste
    `question_texts` de la question.

    **C.** Changer la langue de la question avec `q.lang = "fr"`.

    **D.** On ne peut pas stocker plus d'une langue dans DDI.

    ??? success "Réponse"
        **B.** Pour ajouter une traduction, ajoutez un `InternationalString`
        avec la nouvelle langue à la liste `question_texts` de la question.
        Les deux versions linguistiques sont stockées dans le même élément
        question. L'option A créerait une toute nouvelle question, pas une
        traduction d'une question existante.

???+ question "Question 5 : Comment compter les questions dans une étude ?"
    **A.** `doc.count_questions()`

    **B.** `len(doc.questions)`

    **C.** `doc.questions.size()`

    **D.** `print(doc)`

    ??? success "Réponse"
        **B.** `doc.questions` vous donne la liste des questions, et `len()`
        compte combien d'éléments se trouvent dans cette liste.

---

!!! tip "Notes pour l'instructeur"
    - **C'est le module du « déclic ».** Cinq lignes de Python créent un vrai
      document XML conforme à la norme. Faites-en la démonstration en direct
      pour que l'impact soit clair.
    - **Codage en direct :** Tapez le code à l'écran, ligne par ligne. Laissez
      les apprenants suivre. Faites une pause après chaque étape pour
      permettre à chacun de rattraper.
    - **Erreur courante :** Les apprenants oublient souvent les guillemets
      autour des chaînes de caractères. Par exemple, ils tapent
      `text=What is your age?` au lieu de `text="What is your age?"`.
      Surveillez cela pendant les exercices.
    - **Explorez le XML ensemble :** Ouvrez le fichier sauvegardé à l'écran
      et faites défiler. Montrez le texte de la question à l'intérieur des
      balises. Insistez sur le fait que les apprenants n'ont pas eu besoin
      d'écrire ce XML à la main.
    - **Activité d'approfondissement :** Demandez aux plus rapides d'ajouter
      deux questions supplémentaires de leur choix et de sauvegarder à
      nouveau le fichier.
