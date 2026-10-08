# Module 14 : Ouvrir, modifier et ré-enregistrer des fichiers DDI existants

!!! info "Ce que vous apprendrez"
    - Ouvrir un fichier DDI XML existant avec `ddi.open_ddi()`.
    - Explorer le contenu d'un document chargé.
    - Ouvrir un fichier avec la validation activée.
    - Ajouter de nouveaux éléments à un document existant.
    - Enregistrer le document modifié dans un nouveau fichier.
    - Comprendre la garantie aller-retour : le XML inconnu est préservé.

**Prérequis :** [Module 13 : Mettre à jour et versionner vos documents](module-13-update-and-version.md).

**Durée :** 30 min en autonomie / 40 min avec instructeur.

---

## 1. Ouvrir un fichier existant

!!! note "D'abord, obtenez un fichier à ouvrir"
    Ce module travaille sur un fichier nommé `my-study.xml`. Si vous n'en avez
    pas encore, créez-le maintenant, ou réutilisez `household-survey.xml` du
    [module 6](module-06-csv-to-ddi.md) en changeant le nom de fichier dans les
    exemples ci-dessous.

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
- Si le fichier contient des erreurs, `open_ddi()` lève une exception (un message d'erreur) qui vous dit ce qui ne va pas.

C'est utile quand vous recevez un fichier de quelqu'un d'autre et que vous voulez vous assurer qu'il suit le standard DDI avant de commencer à travailler avec.

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

Les éléments retournés, et ceux de `doc.questions`, `doc.variables` et des autres listes, sont des objets vivants. Changez un champ et le changement est enregistré avec le document :

```python
# Reword the question added above
q.question_texts[0].text = "What is the highest level of education you have completed?"

# Code the variable with a code list; calling set_coded() again switches lists
levels = doc.add_code_list(name="Education Levels")
v.set_coded(levels)
```

Dans un fichier publié, une modification comme celle-ci est une nouvelle version de l'élément. Le [Module 13](module-13-update-and-version.md#6-modifier-le-libelle-dune-question) montre tout le processus pour reformuler une question et [faire passer une variable à une autre liste de codes](module-13-update-and-version.md#7-passer-une-variable-a-une-autre-liste-de-codes), y compris l'augmentation de version et les références à mettre à jour.

---

## 5. Enregistrer le document modifié

Après avoir fait des modifications, enregistrez le document dans un fichier. Vous pouvez enregistrer avec le même nom de fichier (pour écraser) ou avec un nouveau nom de fichier (pour garder les deux copies).

```python
# Save to a new file; this keeps the original unchanged
doc.save("my-study-updated.xml")
```

Il est généralement préférable d'enregistrer avec un **nouveau nom de fichier**. De cette façon, vous avez toujours le fichier original comme sauvegarde.

```python
# Overwrite the original (use with care)
doc.save("my-study.xml")
```

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

**Exercice 1.** Créez une étude avec deux questions et deux variables (ou utilisez un fichier d'un module précédent). Enregistrez-la sur le disque. Puis rouvrez-la avec `open_ddi()` et affichez le nombre de questions et de variables.

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
print(f"Questions: {len(doc2.questions)}")
print(f"Variables: {len(doc2.variables)}")
```

Résultat attendu :

```text
Saved.
Questions: 2
Variables: 2
```

**Exercice 2.** Ajoutez deux nouvelles questions et deux nouvelles variables au document rouvert. Validez-le. Enregistrez avec un nouveau nom de fichier.

```python
q3 = doc2.add_question(text="What is your marital status?")
q4 = doc2.add_question(text="How many people live in your household?")
v3 = doc2.add_variable(name="MaritalStatus", question=q3)
v4 = doc2.add_variable(name="HouseholdSize", question=q4)

errors = doc2.validate()
if errors:
    print("Validation errors:", errors)
else:
    print("Document is valid.")
    doc2.save("census-2024-updated.xml")
    print("Saved updated file.")
```

**Exercice 3.** Rouvrez le nouveau fichier. Vérifiez que les nombres ont augmenté.

```python
doc3 = ddi.open_ddi("census-2024-updated.xml")
print(f"Questions: {len(doc3.questions)}")
print(f"Variables: {len(doc3.variables)}")
```

Résultat attendu :

```text
Questions: 4
Variables: 4
```

---

## Quiz

???+ question "Question 1 : Que fait ddi.open_ddi() ?"
    **A.** Elle crée un nouveau document DDI vide.

    **B.** Elle lit un fichier DDI XML existant depuis le disque et retourne un objet Document.

    **C.** Elle supprime un fichier DDI de votre ordinateur.

    **D.** Elle envoie un fichier DDI à un serveur web.

    ??? success "Réponse"
        **B.** `ddi.open_ddi()` lit un fichier DDI XML et retourne un objet
        `Document` que vous pouvez inspecter et modifier.

???+ question "Question 2 : Que fait validate=True quand vous appelez open_ddi() ?"
    **A.** Elle convertit le fichier au format JSON.

    **B.** Elle vérifie le fichier par rapport aux règles du schéma DDI pendant le chargement.

    **C.** Elle retire les éléments invalides du document.

    **D.** Elle affiche le contenu du fichier à l'écran.

    ??? success "Réponse"
        **B.** Quand vous passez `validate=True`, `open_ddi()` exécute la
        vérification du schéma DDI pendant le chargement. Si le fichier
        contient des erreurs, vous recevez un message d'erreur tout de suite.

???+ question "Question 3 : Le contenu existant est-il perdu quand vous ouvrez un fichier, ajoutez des éléments et l'enregistrez ?"
    **A.** Oui, ddi-l supprime tout ce qu'il ne comprend pas.

    **B.** Oui, seuls les nouveaux éléments sont enregistrés.

    **C.** Non, ddi-l préserve les éléments XML inconnus pendant l'aller-retour.

    **D.** Non, mais seulement si vous enregistrez avec le même nom de fichier.

    ??? success "Réponse"
        **C.** `ddi-l` préserve les éléments XML inconnus. C'est ce qu'on
        appelle la garantie aller-retour. Le contenu que `ddi-l` ne
        reconnaît pas passe sans être modifié.

---

**Voir aussi :**

- [Guide utilisateur : Ouvrir un fichier existant](../user-guide.md#ouvrir-un-fichier-existant)
- [Du XML aux objets](../tutorials/xml-to-objects.md)

---

!!! tip "Notes pour l'instructeur"
    - **La pratique d'abord.** Demandez aux apprenants d'apporter un fichier
      DDI d'un module précédent. S'ils n'en ont pas, créez rapidement un
      fichier ensemble en groupe. L'objectif est de pratiquer le processus
      ouvrir-modifier-enregistrer avec un vrai fichier.
    - **Valider au chargement.** Montrez ce qui se passe quand vous ouvrez
      un fichier cassé avec `validate=True`. Vous pouvez créer un fichier
      cassé en modifiant le XML dans un éditeur de texte et en supprimant
      une balise fermante.
    - **Démo aller-retour.** Ouvrez un fichier qui contient des éléments
      XML supplémentaires (par exemple, des blocs `<r:Note>` ou des
      extensions personnalisées). Montrez que ces éléments survivent à
      l'aller-retour. Cela renforce la confiance dans l'outil.
    - **Erreur courante :** Les apprenants oublient parfois d'enregistrer
      après avoir fait des modifications. Rappelez-leur que les changements
      ne vivent qu'en mémoire jusqu'à l'appel de `doc.save()`.
    - **Activité d'extension :** Demandez aux apprenants avancés d'ouvrir
      un fichier, d'ajouter des éléments, de versionner l'étude (Module 13)
      et d'enregistrer, en combinant les deux modules en un seul
      processus.
