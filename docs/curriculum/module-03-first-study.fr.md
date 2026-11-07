---
description: >-
  Module 3 du cours ddi-l : créer une étude DDI, ajouter des questions en
  deux langues, l'enregistrer en XML et la vérifier avec validate et lint.
---

# Module 3 : Créer votre première étude DDI

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Écrire un script qui crée une étude avec `ddi.new_study()` et
      y ajoute trois questions avec `doc.add_question()`.
    - **O2.** Compter les questions d'une étude avec `len(doc.questions)` et
      afficher l'identifiant de chaque question.
    - **O3.** Sauvegarder l'étude dans un fichier XML avec `doc.save()` et
      trouver le texte d'une question dans le fichier sauvegardé.
    - **O4.** Ajouter une version française du texte et du libellé d'une
      question existante, pour qu'une seule question contienne les deux
      langues.
    - **O5.** Vérifier une étude avec `doc.validate()` et `doc.lint()`, et
      corriger les avertissements de lint jusqu'à ce que les deux ne
      signalent plus rien.

**Prérequis :** [Module 2](module-02-setup.fr.md)

**Durée :** 30 min en autonomie / 45 min avec instructeur.

**Nouveau dans ce module :** `ddi.new_study()`, `doc.add_question()`,
`doc.questions`, `doc.save()`, `InternationalString`, `doc.validate()`,
`doc.lint()`

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
- `agency=` définit l'organisation responsable de l'étude. Il est
  obligatoire : sans lui, `ddi.new_study()` lève une `TypeError`.

---

## 3. Qu'est-ce qu'une « agency » ?

Une **agency** (agence) est l'organisation responsable de l'étude. Ce peut
être une université, un ministère, un institut de recherche ou tout groupe qui
mène l'enquête. Son **identifiant d'agence** figure dans chaque élément
qu'elle crée, à côté de l'identifiant et de la version de l'élément : ensemble,
ils nomment l'élément.

- **Enregistré.** Pour que deux organisations n'aient jamais le même
  identifiant, chacune enregistre le sien dans le
  [registre des identifiants d'agence DDI](https://ddialliance.org/ddi-agency-id-registry).
  Elle peut ensuite ajouter des sous-agences après un point, par exemple une
  par division.
- **Format.** Des lettres, des chiffres et des traits d'union, en parties
  reliées par des points, chaque partie d'au plus 63 caractères.
  `doc.validate()` vérifie le format, pas l'enregistrement.
- **Dans ce cours.** Les identifiants comme `"university.edu"` et
  `"stats.example.org"` sont inventés. Dans un vrai document, utilisez
  l'identifiant que votre organisation a enregistré.

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
défaut est `lang="en"` (anglais) : les questions ajoutées ci-dessus sont donc
en anglais. Pour créer une question en français, passez `lang="fr"`, comme dans
`doc.add_question(text="Quel est votre âge ?", lang="fr")`.

Pour ajouter une traduction française de la même question, ajoutez-la à la
liste `question_texts` de la question :

```python
from ddi_l.models.base import InternationalString

q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
```

Un `InternationalString` est un texte accompagné de son code de langue
(`"en"`, `"fr"`, etc.). Maintenant `q1` contient le texte de la question en
anglais et en français. Quand quelqu'un ouvre le fichier DDI, il peut voir
les deux versions.

L'argument `lang=` fonctionne sur toutes les méthodes `add_*` :
`add_variable()`, `add_concept()`, `add_universe()` et `add_code_list()`.
Vous pouvez aussi ajouter des traductions à leur liste `names` de la même
façon. Le module 8 montre un flux de travail bilingue complet.

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

Voir aussi : [Guide utilisateur : Créer une étude](../user-guide.fr.md#creer-une-etude)

---

## 9. Vérifier votre travail

Prenez l'habitude de vérifier une étude avant de la partager. `ddi-l` effectue
deux types de vérification :

- La **validation** compare le document au **schéma** DDI : les règles
  officielles qui indiquent quels éléments sont permis, où ils se placent et
  lesquels sont obligatoires. Un document qui échoue à la validation n'est pas
  du DDI valide.
- L'**analyse (lint)** repère des problèmes que le schéma autorise mais qui
  sont le plus souvent des erreurs, comme un élément sans libellé.

```python
issues = doc.validate()
print(f"Problèmes de schéma : {len(issues)}")

findings = doc.lint()
print(f"Constats de lint : {len(findings)}")
for finding in findings:
    print(f"  [{finding.severity}] {finding.message}")
```

Résultat attendu :

```text
Problèmes de schéma : 0
Constats de lint : 3
  [warning] Maintainable element is missing a label.
  [warning] Maintainable element is missing a label.
  [warning] Maintainable element is missing a label.
```

L'étude est du DDI valide. Les trois avertissements indiquent que vos
questions n'ont pas de **libellé** : un nom court que les catalogues et les
autres outils affichent à la place du texte complet de la question. Ajoutez un
libellé à chaque question, puis vérifiez de nouveau :

```python
q1.labels.append(InternationalString(text="Age", lang="en"))
q2.labels.append(InternationalString(text="Self-rated health", lang="en"))
q3.labels.append(InternationalString(text="Hours of sleep", lang="en"))

print(f"Constats de lint : {len(doc.lint())}")
doc.save("well-being.xml")
```

Résultat attendu :

```text
Constats de lint : 0
```

Un libellé peut avoir plus d'une langue, comme le texte de la question.
Ajoutez un libellé français à la même liste `labels` :

```python
q1.labels.append(InternationalString(text="Âge", lang="fr"))
```

Quand vous ajoutez un nouvel élément, vous pouvez lui donner un libellé tout
de suite. Chaque méthode `add_*` accepte `label=` :

```python
q4 = doc.add_question(text="Do you exercise every week?", label="Weekly exercise")
```

Les avertissements ne rendent pas un document invalide ; les erreurs de schéma,
si. Vérifiez votre travail de cette façon à la fin de chaque module. Le
[module 7](module-07-cli-validation.fr.md) effectue les mêmes vérifications en
ligne de commande.

---

## Exercices

!!! example "Scénario"
    Vous êtes assistant de recherche. Votre professeur vous demande de
    documenter une enquête sur le bien-être étudiant avec trois questions
    sur l'âge, la santé et le sommeil. Vous allez utiliser `ddi-l` pour
    créer la documentation.

**Exercice 1 (O1, O2).** Créez une étude intitulée
`"Student Well-Being Survey"` avec l'agence `"university.edu"`. Ajoutez trois
questions :

1. `"What is your age?"`
2. `"How would you rate your health?"`
3. `"How many hours do you sleep per night?"`

Affichez le nombre de questions, puis l'identifiant de chaque question.
Sauvegardez l'étude sous `well-being.xml`.

Résultat attendu : `Questions: 3`, puis trois identifiants, un par ligne (les
vôtres seront différents).

```text
Questions: 3
4f0c9a5e-...
9b1d2e7c-...
c3a8f610-...
```

??? success "Réponse"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")

    q1 = doc.add_question(text="What is your age?")
    q2 = doc.add_question(text="How would you rate your health?")
    q3 = doc.add_question(text="How many hours do you sleep per night?")

    print(f"Questions: {len(doc.questions)}")  # -> Questions: 3
    for q in doc.questions:
        print(q.identifier)

    doc.save("well-being.xml")
    ```

**Exercice 2 (O3).** Ouvrez `well-being.xml`, le fichier sauvegardé à
l'exercice 1, dans un éditeur de texte. Trouvez le texte de votre première
question dans le XML. Notez la balise XML qui entoure le texte de la
question.

Résultat attendu : le nom d'une balise XML.

??? success "Réponse"
    Le texte de la question se trouve dans un élément `<d:Text>`, à l'intérieur de
    `<d:LiteralText>`, lui-même dans `<d:QuestionText>` :

    ```xml
    <d:Text xml:lang="en" isPlainText="true">What is your age?</d:Text>
    ```

**Exercice 3 (O5).** Continuez à partir de l'exercice 1. Vérifiez l'étude
avec `doc.validate()` et `doc.lint()`, et affichez le nombre de problèmes que
chacune signale. Donnez ensuite un libellé anglais à chaque question
(`"Age"`, `"Self-rated health"`, `"Hours of sleep"`), vérifiez de nouveau et
sauvegardez.

Résultat attendu :

```text
Problèmes de schéma : 0
Constats de lint : 3
Constats de lint : 0
```

??? success "Réponse"
    ```python
    from ddi_l.models.base import InternationalString

    print(f"Problèmes de schéma : {len(doc.validate())}")  # -> Problèmes de schéma : 0
    print(f"Constats de lint : {len(doc.lint())}")  # -> Constats de lint : 3

    q1.labels.append(InternationalString(text="Age", lang="en"))
    q2.labels.append(InternationalString(text="Self-rated health", lang="en"))
    q3.labels.append(InternationalString(text="Hours of sleep", lang="en"))

    print(f"Constats de lint : {len(doc.lint())}")  # -> Constats de lint : 0
    doc.save("well-being.xml")
    ```

    Les trois avertissements étaient « Maintainable element is missing a
    label. », un par question. Un libellé corrige chacun d'eux.

**Exercice 4 (O4).** Ajoutez le français à la première question : le texte
`"Quel est votre âge ?"` et le libellé `"Âge"`. Ne créez pas de nouvelle
question. Affichez le nombre de questions et le nombre de constats de lint,
sauvegardez de nouveau le fichier et vérifiez dans le XML que les deux
langues apparaissent.

Résultat attendu :

```text
Questions: 3
Constats de lint : 0
```

Dans le XML, la première question a des entrées `xml:lang="en"` et
`xml:lang="fr"` pour son libellé comme pour son texte.

??? success "Réponse"
    ```python
    q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
    q1.labels.append(InternationalString(text="Âge", lang="fr"))

    print(f"Questions: {len(doc.questions)}")  # -> Questions: 3
    print(f"Constats de lint : {len(doc.lint())}")  # -> Constats de lint : 0
    doc.save("well-being.xml")
    ```

    Le nombre reste à 3, car les deux traductions appartiennent à `q1`. Dans
    le XML, la première question se lit maintenant ainsi :

    ```xml
    <r:Label>
      <r:Content xml:lang="en">Age</r:Content>
      <r:Content xml:lang="fr">Âge</r:Content>
    </r:Label>
    <d:QuestionText>
      <d:LiteralText>
        <d:Text xml:lang="en" isPlainText="true">What is your age?</d:Text>
      </d:LiteralText>
      <d:LiteralText>
        <d:Text xml:lang="fr">Quel est votre âge ?</d:Text>
      </d:LiteralText>
    </d:QuestionText>
    ```

---

## Quiz

???+ question "Question 1 (O1) : Vous exécutez `doc = ddi.new_study(title='Sleep Survey')` et obtenez une TypeError. Pourquoi ?"
    **A.** Le titre est trop court.

    **B.** `agency=` manque. Chaque étude a besoin de l'organisation qui en
    est responsable.

    **C.** Vous devez d'abord importer `InternationalString`.

    **D.** `new_study()` ne prend aucun argument.

    ??? success "Réponse"
        **B.** `ddi.new_study()` exige à la fois `title=` et `agency=`. Le
        message d'erreur le dit : « missing 1 required keyword-only argument:
        'agency' ».

???+ question "Question 2 (O1) : Après `q1 = doc.add_question(text='What is your age?')`, qu'est-ce que `q1` ?"
    **A.** La chaîne `"What is your age?"`.

    **B.** Le nombre de questions de l'étude.

    **C.** Un objet question stocké dans l'étude, que vous pouvez utiliser
    plus tard, par exemple pour le traduire ou pour y associer une variable.

    **D.** Le texte XML de la question.

    ??? success "Réponse"
        **C.** `doc.add_question()` ajoute un élément question à l'étude et
        renvoie cet objet question. Le garder dans une variable vous permet
        de l'utiliser plus tard.

???+ question "Question 3 (O2) : Une étude a trois questions. Vous en ajoutez une quatrième avec `doc.add_question()`, puis exécutez `print(len(doc.questions))`. Qu'est-ce qui s'affiche ?"
    **A.** `4`

    **B.** `3`

    **C.** `1`

    **D.** Une erreur, car `doc.questions` n'est pas une liste.

    ??? success "Réponse"
        **A.** `doc.questions` est la liste de toutes les questions de
        l'étude, et `len()` les compte : trois plus la nouvelle.

???+ question "Question 4 (O3) : Vous ouvrez le fichier écrit par `doc.save('well-being.xml')`. Où trouvez-vous le texte de votre première question ?"
    **A.** Dans un élément `<d:Text>` à l'intérieur de `<d:QuestionText>`.

    **B.** Seulement dans le nom du fichier.

    **C.** Dans l'élément `<r:Agency>`.

    **D.** Nulle part : `save()` n'écrit que le titre de l'étude.

    ??? success "Réponse"
        **A.** `doc.save()` écrit toute l'étude, et le texte de chaque
        question se trouve dans `<d:Text>`, à l'intérieur de
        `<d:LiteralText>`, lui-même dans `<d:QuestionText>`.

???+ question "Question 5 (O4) : Vous voulez la première question, `q1`, en anglais et en français. Quelle ligne le fait ?"
    **A.** `doc.add_question(text="Quel est votre âge ?", lang="fr")`

    **B.** `q1.lang = "fr"`

    **C.** `q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))`

    **D.** Aucune : DDI ne peut pas stocker plus d'une langue dans une
    question.

    ??? success "Réponse"
        **C.** Ajouter un `InternationalString` avec la nouvelle langue
        stocke les deux versions dans le même élément question. L'option A
        crée une toute nouvelle question séparée, pas une traduction de
        `q1`.

???+ question "Question 6 (O5) : `doc.validate()` renvoie une liste vide, mais `doc.lint()` signale des avertissements. Le document est-il du DDI valide ?"
    **A.** Non. Tout constat rend un document invalide.

    **B.** Seulement après l'avoir enregistré.

    **C.** Cela dépend de la langue des questions.

    **D.** Oui. La validation vérifie le schéma ; les avertissements de lint
    signalent des problèmes de qualité, comme un libellé manquant, que le
    schéma autorise.

    ??? success "Réponse"
        **D.** Une liste vide renvoyée par `doc.validate()` signifie que le
        document respecte le schéma DDI. Les avertissements de lint méritent
        d'être corrigés, mais ils ne rendent pas le document invalide.

???+ question "Question 7 (O5) : `doc.lint()` signale 'Maintainable element is missing a label.' une fois pour chacune de vos trois questions. Quelle modification fait disparaître les avertissements ?"
    **A.** Sauvegarder de nouveau le document avec `doc.save()`.

    **B.** Donner un libellé à chaque question, par exemple
    `q1.labels.append(InternationalString(text="Age", lang="en"))`, ou
    passer `label=` à l'appel de `doc.add_question()`.

    **C.** Supprimer les questions et les ajouter de nouveau avec le même
    code.

    **D.** Appeler `doc.validate()` avant `doc.lint()`.

    ??? success "Réponse"
        **B.** L'avertissement nomme le problème : les questions n'ont pas
        de libellé. Sauvegarder ou valider ne modifie pas le document, et
        ajouter de nouveau les questions avec le même code ramène les mêmes
        avertissements.

---

## Faites le point

- [ ] Je peux écrire un script qui crée une étude avec `ddi.new_study()` et
  y ajoute trois questions avec `doc.add_question()`. (O1)
- [ ] Je peux compter les questions avec `len(doc.questions)` et afficher
  l'identifiant de chaque question. (O2)
- [ ] Je peux sauvegarder l'étude avec `doc.save()` et trouver le texte
  d'une question dans le fichier XML. (O3)
- [ ] Je peux ajouter une version française du texte et du libellé d'une
  question existante sans créer de nouvelle question. (O4)
- [ ] Je peux vérifier une étude avec `doc.validate()` et `doc.lint()` et
  corriger les avertissements de lint jusqu'à ce que les deux ne signalent
  plus rien. (O5)

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
    - **Erreur courante :** À l'exercice 4, certains apprenants appellent
      `doc.add_question(..., lang="fr")`. Demandez-leur d'afficher
      `len(doc.questions)` : un total de 4 montre qu'ils ont créé une
      deuxième question au lieu de traduire la première.
    - **Explorez le XML ensemble :** Ouvrez le fichier sauvegardé à l'écran
      et faites défiler. Montrez le texte de la question à l'intérieur des
      balises. Insistez sur le fait que les apprenants n'ont pas eu besoin
      d'écrire ce XML à la main.
    - **Activité d'approfondissement :** Demandez aux plus rapides d'ajouter
      deux questions supplémentaires de leur choix, chacune avec un
      `label=`, puis de vérifier avec `doc.lint()` et de sauvegarder à
      nouveau le fichier.
