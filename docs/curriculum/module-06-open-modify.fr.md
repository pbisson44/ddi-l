---
description: >-
  Module 6 du cours ddi-l : ouvrir un fichier DDI existant, l'inspecter et
  le modifier, le valider au chargement et en enregistrer une copie.
---

# Module 6 : Ouvrir, modifier et ré-enregistrer des fichiers DDI existants

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Ouvrir un fichier DDI existant avec `ddi.open_ddi()` et afficher combien de questions et de variables il contient.
    - **O2.** Ouvrir un fichier avec `validate=True`, intercepter la `ddi.DDIValidationError` que lève un fichier cassé, et nommer l'élément que désigne son message.
    - **O3.** Ajouter de nouveaux éléments à un document ouvert, reformuler une question existante et coder une variable avec une liste de codes.
    - **O4.** Enregistrer le document modifié sous un nouveau nom de fichier et le rouvrir pour confirmer que vos modifications ont été conservées et que le fichier original n'a pas changé.
    - **O5.** Prédire ce qu'il advient du XML que `ddi-l` ne modélise pas quand vous ouvrez et enregistrez un fichier, et vérifier votre prédiction.

**Prérequis :** [Module 5](module-05-concepts-universes.fr.md).

**Durée :** 30 min en autonomie / 40 min avec instructeur.

**Nouveau dans ce module :** `ddi.open_ddi()`, `open_ddi(..., validate=True)`, `ddi.DDIValidationError`, `question_texts`, `doc.add_code_list()`, `variable.set_coded()`.

---

## 1. Ouvrir un fichier existant

!!! note "D'abord, obtenez un fichier à ouvrir"
    Ce module travaille sur un fichier nommé `my-study.xml`. Si vous n'en avez
    pas encore, créez-le maintenant, ou réutilisez `well-being.xml` du
    [module 3](module-03-first-study.fr.md) en changeant le nom de fichier dans
    les exemples ci-dessous.

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="My Study", agency="example.org")
    doc.add_question(text="What is your age?")
    doc.add_variable(name="Age")
    doc.save("my-study.xml")
    ```

La fonction `ddi.open_ddi()` lit un fichier DDI XML depuis votre ordinateur et vous donne un objet `Document`. Un **Document** est l'objet principal que vous utilisez pour voir et modifier le contenu DDI.

```python
import ddi_l as ddi

doc = ddi.open_ddi("my-study.xml")
```

L'argument est le **chemin** : l'emplacement du fichier sur votre ordinateur. Ce peut être un simple nom de fichier (comme `"my-study.xml"`) si le fichier est dans le même dossier que votre script, ou un chemin complet (comme `"/home/user/data/my-study.xml"`).

Après l'exécution de cette ligne, la variable `doc` contient tout le document DDI en mémoire. Vous pouvez maintenant lire son contenu ou faire des modifications.

---

## 2. Explorer ce qu'il contient

Une fois que vous ouvrez un document, vous pouvez compter et lister ce qu'il contient. L'objet `Document` possède des propriétés (raccourcis) pour les types d'éléments les plus courants :

- `doc.questions` : une liste de toutes les questions.
- `doc.variables` : une liste de toutes les variables.
- `doc.concepts` : une liste de tous les concepts.
- `doc.universes` : une liste de tous les univers.
- `doc.code_lists` : une liste de toutes les listes de codes.

Voici comment compter les éléments et afficher leurs identifiants :

```python
doc = ddi.open_ddi("my-study.xml")

print(f"Questions:  {len(doc.questions)}")
print(f"Variables:  {len(doc.variables)}")
print(f"Concepts:   {len(doc.concepts)}")

# Print each question's identifier
for q in doc.questions:
    print(f"  Question: {q.identifier}")

# Print each variable's identifier
for v in doc.variables:
    print(f"  Variable: {v.identifier}")
```

Un **identifiant** est un nom unique que DDI attribue à chaque élément. C'est comme un numéro d'étudiant : aucun élément ne partage le même.

---

## 3. Ouvrir avec validation

Vous pouvez demander à `ddi-l` de vérifier le fichier par rapport aux règles DDI pendant le chargement. C'est ce qu'on appelle la **validation**. Si le fichier contient des erreurs, vous les verrez tout de suite au lieu de les découvrir plus tard.

```python
doc = ddi.open_ddi("my-study.xml", validate=True)
```

L'option `validate=True` dit à `open_ddi()` d'exécuter la vérification du schéma DDI pendant le chargement. Un **schéma** est un ensemble de règles qui dit quels éléments sont permis et comment ils doivent être organisés.

- Si le fichier est valide, `open_ddi()` retourne le document comme d'habitude.
- Si le fichier enfreint une règle du schéma, `open_ddi()` lève une **exception** : une erreur Python qui arrête le script, sauf si vous l'interceptez. Pour un problème de schéma, l'exception est `ddi.DDIValidationError`.

Pour signaler le problème au lieu de vous arrêter, interceptez l'exception avec `try`/`except` :

```python
try:
    doc = ddi.open_ddi("my-study.xml", validate=True)
except ddi.DDIValidationError as error:
    print(f"Not valid: {error}")
```

Le message a deux parties. La première nomme la règle enfreinte. La partie entre parenthèses, après `at`, est le **chemin** vers l'élément qui pose problème, de la racine du fichier vers le bas. Par exemple, `(at /{ddi:instance:3_3}DDIInstance/{ddi:reusable:3_3}Version)` désigne l'élément `Version` situé directement sous `DDIInstance`. Vous pouvez ignorer les parties entre accolades : elles nomment l'espace de noms DDI auquel appartient chaque élément.

Si le fichier n'est même pas du XML bien formé (par exemple, il manque une balise fermante), `open_ddi()` lève plutôt `ddi.DDIParseError`, avec ou sans `validate=True`.

Valider au chargement est utile quand vous recevez un fichier de quelqu'un d'autre et que vous voulez vous assurer qu'il suit le standard DDI avant de commencer à travailler avec.

---

## 4. Ajouter de nouveaux éléments à un document existant

Vous pouvez ajouter des questions, des variables, des concepts, des univers et des listes de codes à un document existant. Les méthodes sont les mêmes que celles que vous avez utilisées quand vous avez créé un nouveau document :

```python
doc = ddi.open_ddi("my-study.xml")

# Add a new question
q = doc.add_question(text="What is your highest level of education?")

# Add a new variable linked to the question
v = doc.add_variable(name="Education", question=q)

# Add a concept
c = doc.add_concept(name="Educational Attainment")

# Add a universe
u = doc.add_universe(name="Adults aged 18 and over")
```

Chaque méthode `add_*` retourne le nouvel élément. Vous pouvez utiliser cet élément plus tard, par exemple, pour lier une variable à une question ou pour définir une propriété personnalisée.

### Modifier les éléments déjà présents

Les éléments retournés, et ceux de `doc.questions`, `doc.variables` et des autres listes, sont des objets vivants. Changez un champ et le changement est enregistré avec le document. Une question garde son libellé dans `question_texts`, une liste avec une entrée par langue : `question_texts[0].text` est donc le premier libellé.

Une variable peut aussi être **codée** : ses valeurs viennent d'une **liste de codes**, l'ensemble des réponses autorisées à une question (par exemple « Secondaire », « Collégial », « Universitaire »). Deux appels suffisent pour l'instant :

- `doc.add_code_list(name=...)` crée une nouvelle liste de codes, vide, dans le document et la retourne.
- `v.set_coded(code_list)` indique que les valeurs de la variable `v` viennent de cette liste de codes. Un nouvel appel avec une autre liste fait passer la variable à cette liste.

Le [module 9](module-09-code-lists.fr.md) traite les listes de codes en profondeur, y compris la façon de remplir une liste avec ses réponses.

```python
# Reword the question added above
q.question_texts[0].text = "What is the highest level of education you have completed?"

# Code the variable with a code list; calling set_coded() again switches lists
levels = doc.add_code_list(name="Education Levels")
v.set_coded(levels)
```

Dans un fichier publié, une modification comme celle-ci est une nouvelle version de l'élément. Plus loin dans le cours, le [Module 15](module-15-update-and-version.fr.md#6-modifier-le-libelle-dune-question) montre tout le processus pour reformuler une question et [faire passer une variable à une autre liste de codes](module-15-update-and-version.fr.md#7-passer-une-variable-a-une-autre-liste-de-codes), y compris l'augmentation de version et les références à mettre à jour.

---

## 5. Enregistrer le document modifié

Après avoir fait des modifications, enregistrez le document dans un fichier. Vous pouvez enregistrer avec le même nom de fichier (pour écraser) ou avec un nouveau nom de fichier (pour garder les deux copies). Vos modifications n'existent qu'en mémoire jusqu'à ce que vous appeliez `doc.save()`.

```python
# Save to a new file; this keeps the original unchanged
doc.save("my-study-updated.xml")
```

Il est généralement préférable d'enregistrer avec un **nouveau nom de fichier**. De cette façon, vous avez toujours le fichier original comme sauvegarde.

```python
# Overwrite the original (use with care)
doc.save("my-study.xml")
```

Pour confirmer qu'un enregistrement a fonctionné, rouvrez le nouveau fichier et comptez ce qu'il contient, comme à la section 2.

---

## 6. La garantie aller-retour

`ddi-l` fait une promesse : **il ne supprimera pas le contenu qu'il ne comprend pas.** C'est ce qu'on appelle la **garantie aller-retour**.

Les fichiers DDI XML peuvent contenir de nombreux éléments. `ddi-l` sait lire et écrire les plus courants (questions, variables, concepts, listes de codes, et plus). Mais si le fichier contient des éléments supplémentaires que `ddi-l` ne reconnaît pas, ces éléments sont conservés exactement tels quels. Ils passent à travers le cycle lecture-écriture sans être touchés.

Cela signifie que vous pouvez ouvrir en toute sécurité un fichier créé par un autre outil, ajouter vos métadonnées et l'enregistrer. Les parties que vous n'avez pas touchées resteront les mêmes.

```text
Original file           ddi-l                  Saved file
┌──────────────┐        ┌────────────┐            ┌──────────────┐
│ Known items  │──────▶ │ Parsed     │──────────▶ │ Known items  │
│ Unknown XML  │──────▶ │ Preserved  │──────────▶ │ Unknown XML  │
└──────────────┘        └────────────┘            └──────────────┘
```

---

## Exercices

!!! example "Scénario"
    Un archiviste reçoit un fichier DDI d'une équipe de recherche. Il doit
    vérifier son contenu, ajouter les métadonnées manquantes, valider le
    fichier et enregistrer une copie mise à jour.

**Exercice 1 (O1).** Créez une étude avec deux questions et deux variables (ou utilisez un fichier d'un module précédent). Enregistrez-la sur le disque. Puis rouvrez-la avec `open_ddi()` et affichez le nombre de questions et de variables.

Résultat attendu :

```text
Saved.
Questions: 2
Variables: 2
```

??? success "Réponse"
    ```python
    import ddi_l as ddi

    # Create and save
    doc = ddi.new_study(title="Census 2024", agency="stats.example.org")
    q1 = doc.add_question(text="What is your age?")
    q2 = doc.add_question(text="What is your gender?")
    v1 = doc.add_variable(name="Age", question=q1)
    v2 = doc.add_variable(name="Gender", question=q2)
    doc.save("census-2024.xml")
    print("Saved.")

    # Re-open and inspect
    doc2 = ddi.open_ddi("census-2024.xml")
    print(f"Questions: {len(doc2.questions)}")  # -> Questions: 2
    print(f"Variables: {len(doc2.variables)}")  # -> Variables: 2
    ```

**Exercice 2 (O2).** Les fichiers des autres ne sont pas toujours valides. Exécutez ce code pour créer une copie cassée de `census-2024.xml` : le premier numéro de version devient le mot `one`.

```python
from pathlib import Path

text = Path("census-2024.xml").read_text(encoding="utf-8")
broken = text.replace("<r:Version>1</r:Version>", "<r:Version>one</r:Version>", 1)
Path("census-2024-broken.xml").write_text(broken, encoding="utf-8")
```

Ensuite :

1. Ouvrez `census-2024-broken.xml` avec `validate=True`. Interceptez la `ddi.DDIValidationError` et affichez son message.
2. À partir du message, nommez l'élément fautif et dites ce qui ne va pas.
3. Ouvrez le même fichier sans `validate=True` et affichez son nombre de questions. Qu'est-ce que cela vous apprend ?

Résultat attendu :

```text
Not valid: value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*'] (at /{ddi:instance:3_3}DDIInstance/{ddi:reusable:3_3}Version)
Opened without checking: 2 questions
```

??? success "Réponse"
    ```python
    try:
        ddi.open_ddi("census-2024-broken.xml", validate=True)
    except ddi.DDIValidationError as error:
        print(f"Not valid: {error}")

    unchecked = ddi.open_ddi("census-2024-broken.xml")
    print(f"Opened without checking: {len(unchecked.questions)} questions")
    ```

    Le chemin après `at` désigne l'élément `Version` situé directement sous
    `DDIInstance`. Sa valeur, `one`, ne correspond pas au motif des
    versions : `[0-9]+(\.[0-9]+)*` signifie des chiffres, suivis
    éventuellement d'autres groupes formés d'un point et de chiffres, comme
    `1` ou `1.0.0`.

    Sans `validate=True`, le fichier cassé s'ouvre sans aucune plainte. Seule
    la validation vous dit que le fichier enfreint les règles DDI.

**Exercice 3 (O3).** Travaillez sur le document rouvert à l'exercice 1 (`doc2`) :

1. Ajoutez deux nouvelles questions et deux nouvelles variables liées à ces questions (MaritalStatus et HouseholdSize).
2. Reformulez la première question en « What was your age at your last birthday? ».
3. Créez une liste de codes appelée « Marital Status Codes » et codez la variable MaritalStatus avec elle.
4. Validez le document. S'il est valide, enregistrez-le sous `census-2024-updated.xml`.

Résultat attendu :

```text
Document is valid.
Saved updated file.
```

??? success "Réponse"
    ```python
    q3 = doc2.add_question(text="What is your marital status?")
    q4 = doc2.add_question(text="How many people live in your household?")
    v3 = doc2.add_variable(name="MaritalStatus", question=q3)
    v4 = doc2.add_variable(name="HouseholdSize", question=q4)

    doc2.questions[0].question_texts[0].text = "What was your age at your last birthday?"

    statuses = doc2.add_code_list(name="Marital Status Codes")
    v3.set_coded(statuses)

    errors = doc2.validate()
    if errors:
        print("Validation errors:", errors)
    else:
        print("Document is valid.")
        doc2.save("census-2024-updated.xml")
        print("Saved updated file.")
    ```

**Exercice 4 (O4).** Rouvrez `census-2024-updated.xml`. Affichez son nombre de questions, de variables et de listes de codes, et le libellé de sa première question. Rouvrez ensuite le fichier original `census-2024.xml` et confirmez qu'il a toujours deux questions.

Résultat attendu :

```text
Questions: 4
Variables: 4
Code lists: 1
First question: What was your age at your last birthday?
Original questions: 2
```

??? success "Réponse"
    ```python
    doc3 = ddi.open_ddi("census-2024-updated.xml")
    print(f"Questions: {len(doc3.questions)}")  # -> Questions: 4
    print(f"Variables: {len(doc3.variables)}")
    print(f"Code lists: {len(doc3.code_lists)}")
    print(f"First question: {doc3.questions[0].question_texts[0].text}")

    original = ddi.open_ddi("census-2024.xml")
    print(f"Original questions: {len(original.questions)}")
    ```

    Les nombres ont augmenté dans le nouveau fichier, et l'original a gardé
    ses deux questions : l'enregistrer sous un nouveau nom de fichier l'a
    laissé intact.

**Exercice 5 (O5).** La copie de votre fichier qu'a un partenaire contient un élément que `ddi-l` ne modélise pas : une description des unités que couvre l'étude. Exécutez ce code pour créer cette copie :

```python
from pathlib import Path

text = Path("census-2024.xml").read_text(encoding="utf-8")
extra = (
    '<r:AnalysisUnitsCovered><r:String xml:lang="en">'
    "Persons living in private households"
    "</r:String></r:AnalysisUnitsCovered>"
)
Path("census-2024-partner.xml").write_text(
    text.replace("<d:DataCollection>", extra + "<d:DataCollection>", 1),
    encoding="utf-8",
)
```

Avant d'aller plus loin, écrivez votre prédiction en une phrase : si vous ouvrez `census-2024-partner.xml`, ajoutez une variable appelée Region et l'enregistrez sous `census-2024-partner-updated.xml`, le fichier enregistré contiendra-t-il encore « Persons living in private households » ? Faites-le ensuite, et vérifiez en cherchant cette phrase dans le fichier enregistré.

Résultat attendu :

```text
True
```

??? success "Réponse"
    ```python
    partner = ddi.open_ddi("census-2024-partner.xml", validate=True)
    partner.add_variable(name="Region")
    partner.save("census-2024-partner-updated.xml")

    saved = Path("census-2024-partner-updated.xml").read_text(encoding="utf-8")
    print("Persons living in private households" in saved)  # -> True
    ```

    L'élément survit : `ddi-l` conserve le XML qu'il ne modélise pas
    exactement tel quel, de sorte qu'ouvrir et enregistrer un fichier ne
    supprime jamais le contenu que vous n'avez pas touché. C'est la garantie
    aller-retour.

---

## Quiz

???+ question "Question 1 (O1) : Qu'affiche ce code pour un fichier de 3 questions et 5 variables ?"
    `doc = ddi.open_ddi("survey.xml")`, puis
    `print(len(doc.questions), len(doc.variables))`

    **A.** `5 3`

    **B.** `0 0`, parce qu'un fichier doit être validé avant qu'on puisse
    compter ses éléments.

    **C.** `8`

    **D.** `3 5`

    ??? success "Réponse"
        **D.** `ddi.open_ddi()` lit le fichier entier. `doc.questions` et
        `doc.variables` listent ses questions et ses variables, dans cet
        ordre dans l'appel à `print()`.

???+ question "Question 2 (O2) : Qu'est-ce qui ne va pas dans ce fichier ?"
    `ddi.open_ddi("partner.xml", validate=True)` lève une
    `ddi.DDIValidationError` avec ce message :

    `value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*'] (at /{ddi:instance:3_3}DDIInstance/{ddi:reusable:3_3}Version)`

    **A.** Le fichier `partner.xml` n'existe pas.

    **B.** L'élément `Version` situé directement sous `DDIInstance` contient
    une valeur qui n'est pas un numéro de version comme `1` ou `1.0.0`.

    **C.** Le fichier contient trop de questions.

    **D.** `ddi-l` ne sait pas lire les fichiers DDI 3.3.

    ??? success "Réponse"
        **B.** Le chemin après `at` nomme l'élément : `Version`, sous
        `DDIInstance`. La première partie du message dit que sa valeur ne
        correspond pas au motif des numéros de version.

???+ question "Question 3 (O3) : Quelle ligne code la variable v avec la liste de codes levels ?"
    **A.** `levels.set_coded(v)`

    **B.** `doc.add_code_list(v)`

    **C.** `v.set_coded(levels)`

    **D.** `v.code_list = "levels"`

    ??? success "Réponse"
        **C.** `set_coded()` est une méthode de la variable, et elle prend la
        liste de codes en argument. `doc.add_code_list()` crée une nouvelle
        liste ; elle ne code pas une variable.

???+ question "Question 4 (O4) : Que contient my-study.xml ensuite ?"
    Vous ouvrez `my-study.xml`, ajoutez une variable et fermez Python sans
    appeler `doc.save()`.

    **A.** Le contenu original, sans la nouvelle variable.

    **B.** Le contenu original et la nouvelle variable.

    **C.** Rien : le fichier est vidé.

    **D.** Une copie de sauvegarde de l'original.

    ??? success "Réponse"
        **A.** Les modifications n'existent qu'en mémoire jusqu'à l'appel de
        `doc.save()`. Le fichier sur le disque est inchangé.

???+ question "Question 5 (O5) : Qu'advient-il d'un élément que ddi-l ne modélise pas ?"
    Le fichier d'un partenaire contient un élément que `ddi-l` ne modélise
    pas. Vous ouvrez le fichier, ajoutez une variable et l'enregistrez sous un
    nouveau nom.

    **A.** Il est supprimé, parce que `ddi-l` n'écrit que ce qu'il comprend.

    **B.** Il est déplacé à la fin du fichier.

    **C.** Il est transformé en note.

    **D.** Il est conservé tel quel dans le fichier enregistré.

    ??? success "Réponse"
        **D.** C'est la garantie aller-retour : le contenu que `ddi-l` ne
        reconnaît pas passe à travers le cycle lecture-écriture sans être
        touché.

---

## Faites le point

- [ ] Je peux ouvrir un fichier DDI existant avec `ddi.open_ddi()` et afficher combien de questions et de variables il contient. (O1)
- [ ] Je peux ouvrir un fichier avec `validate=True`, intercepter `ddi.DDIValidationError` et nommer l'élément que désigne son message. (O2)
- [ ] Je peux ajouter des éléments à un document ouvert, reformuler une question et coder une variable avec une liste de codes. (O3)
- [ ] Je peux enregistrer le document modifié sous un nouveau nom de fichier et le rouvrir pour confirmer mes modifications et l'original intact. (O4)
- [ ] Je peux prédire ce qu'il advient du XML que `ddi-l` ne modélise pas quand j'ouvre et enregistre un fichier, et le vérifier. (O5)

---

**Voir aussi :**

- [Guide utilisateur : Ouvrir un fichier existant](../user-guide.fr.md#ouvrir-un-fichier-existant)
- [Du XML aux objets](../tutorials/xml-to-objects.fr.md)

---

!!! tip "Notes pour l'instructeur"
    - **La pratique d'abord.** Demandez aux apprenants d'apporter un fichier
      DDI d'un module précédent. S'ils n'en ont pas, créez rapidement un
      fichier ensemble en groupe. L'objectif est de pratiquer le processus
      ouvrir-modifier-enregistrer avec un vrai fichier.
    - **Valider au chargement.** Montrez ce qui se passe quand vous ouvrez
      un fichier cassé avec `validate=True`. Changez un numéro de version en
      mot, comme à l'exercice 2, pour montrer une erreur de schéma
      (`ddi.DDIValidationError`). Supprimez une balise fermante dans un
      éditeur de texte pour montrer une erreur d'analyse
      (`ddi.DDIParseError`), qui apparaît même sans `validate=True`.
    - **Démo aller-retour.** L'exercice 5 ajoute un élément que `ddi-l` ne
      modélise pas. Ouvrez le fichier enregistré dans un éditeur de texte et
      montrez l'élément à sa place. Cela renforce la confiance dans l'outil.
    - **Erreur courante :** Les apprenants oublient parfois d'enregistrer
      après avoir fait des modifications. Rappelez-leur que les changements
      ne vivent qu'en mémoire jusqu'à l'appel de `doc.save()`.
    - **Les listes de codes viennent plus tard.** Ce module utilise
      `add_code_list()` et `set_coded()` avec une liste vide. Si les
      apprenants demandent comment ajouter les réponses, renvoyez-les au
      module 9.
    - **Activité d'extension :** Demandez aux apprenants avancés d'ouvrir
      un fichier, d'ajouter des éléments, de versionner l'étude (Module 15, plus loin dans le cours)
      et d'enregistrer, en combinant les deux modules en un seul
      processus.
