# Module 11 : Propriétés personnalisées, recherche, suppression et validation

!!! info "Ce que vous apprendrez"
    - Attacher des propriétés clé-valeur personnalisées à tout élément DDI.
    - Lire et supprimer des propriétés.
    - Trouver des éléments par leur identifiant unique.
    - Supprimer des éléments d'un document.
    - Valider un document par rapport au schéma DDI.
    - Utiliser la boucle valider-corriger-valider avant de publier.

**Prérequis :** [Module 10 : Couplage de données](module-10-data-linkage.md).

**Durée :** 40 min en autonomie / 50 min avec instructeur.

---

## 1. Propriétés personnalisées

Chaque élément DDI peut porter des informations supplémentaires sous forme de **propriétés personnalisées**.
Une propriété est une **paire clé-valeur** : un nom et une valeur, comme une étiquette sur une boîte.

Par exemple, vous pourriez marquer une question avec :

- `"sensitivity"` = `"high"` (cette question demande des informations privées)
- `"data_source"` = `"administrative records"` (ces données proviennent de fichiers gouvernementaux)

Les propriétés permettent à votre équipe d'ajouter des notes et des étiquettes pour lesquelles la norme DDI n'a pas de champs prédéfinis.

## 2. Définir une propriété

Utilisez `item.set_property(key, value)` pour ajouter une propriété à n'importe quel élément.

```python
import ddi_l as ddi

doc = ddi.new_study(title="Household Survey", agency="survey.gc.ca")

q_age = doc.add_question(text="How old are you?")
q_income = doc.add_question(text="What is your household income?")
q_name = doc.add_question(text="What is your full name?")

# Tag the income question as high sensitivity
q_income.set_property("sensitivity", "high")

# Tag the name question too
q_name.set_property("sensitivity", "high")
q_name.set_property("data_source", "self-reported")
```

Vous pouvez définir autant de propriétés que nécessaire sur n'importe quel élément.

## 3. Lire les propriétés

Utilisez `item.get_property(key)` pour lire une propriété.
La méthode retourne la valeur sous forme de chaîne, ou `None` si la clé n'existe pas.

```python
print(q_income.get_property("sensitivity"))  # -> high
print(q_age.get_property("sensitivity"))  # -> None
```

Utilisez `item.properties` pour obtenir toutes les propriétés sous forme de dictionnaire.

```python
print(q_name.properties)
# -> {'sensitivity': 'high', 'data_source': 'self-reported'}
```

Un **dictionnaire** (aussi appelé dict) est une structure de données Python qui associe des clés à des valeurs.

## 4. Supprimer une propriété

Utilisez `item.remove_property(key)` pour supprimer une propriété.
La méthode retourne `True` si la propriété a été trouvée et supprimée, ou `False` si la clé n'existait pas.

```python
removed = q_name.remove_property("data_source")
print(removed)  # -> True
print(q_name.properties)  # -> {'sensitivity': 'high'}
```

## 5. Avancé : Passer une liste de codes comme valeur de propriété

Vous pouvez passer un objet liste de codes (ou tout élément DDI) comme valeur.
La bibliothèque stocke automatiquement l'**URN** (Uniform Resource Name) de l'élément.

Un URN est une adresse unique qui identifie l'élément.

```python
cl = doc.add_code_list(name="Income Brackets")
q_income.set_property("vocabulary", cl)

print(q_income.get_property("vocabulary"))
# Affiche la chaîne URN de la liste de codes
```

C'est utile quand vous voulez lier une question à la liste de codes qui définit ses réponses autorisées.

## 6. Trouver des éléments par identifiant

Chaque élément d'un document DDI reçoit un **identifiant** unique lors de sa création.
Pensez-y comme un numéro de série.

Utilisez `doc.find(identifier)` pour chercher n'importe quel élément par son identifiant.

```python
v1 = doc.add_variable(name="Age", question=q_age)

# Save the identifier
age_id = v1.identifier
print(f"Identifier: {age_id}")

# Find it later
found = doc.find(age_id)
print(found)  # Affiche l'objet Variable
```

Si aucun élément ne correspond, `doc.find()` retourne `None`.

## 7. Supprimer des éléments

Utilisez `doc.remove(identifier)` pour supprimer un élément du document.
La méthode retourne `True` si l'élément a été trouvé et supprimé.

```python
print(f"Questions before: {len(doc.questions)}")  # -> 3

# Remove the name question
doc.remove(q_name.identifier)

print(f"Questions after: {len(doc.questions)}")  # -> 2
```

Attention : la suppression est permanente.
Il n'y a pas de retour en arrière.

## 8. Valider le document

Utilisez `doc.validate()` pour vérifier le document par rapport au **schéma DDI**.
Un schéma est un ensemble de règles qui définit à quoi ressemble un fichier DDI valide.

```python
issues = doc.validate()

if issues:
    for issue in issues:
        print(f"Problem: {issue.message}")
else:
    print("Document is valid!")
```

La méthode retourne une liste de problèmes.
Si la liste est vide, le document est valide.

## 9. La boucle valider-corriger-valider

Avant de publier ou de partager un fichier DDI, suivez cette boucle :

1. **Créez** votre document (ajoutez des questions, variables, concepts, etc.).
2. **Validez-le** avec `doc.validate()`.
3. **Corrigez** les problèmes trouvés.
4. **Validez à nouveau** pour vérifier que les corrections ont fonctionné.
5. **Enregistrez** le fichier final.

```python
# Step 1: Create
doc = ddi.new_study(title="Household Survey", agency="survey.gc.ca")
q = doc.add_question(text="How old are you?")
doc.add_variable(name="Age", question=q)

# Step 2: Validate
issues = doc.validate()
print(f"Issues found: {len(issues) if issues else 0}")

# Step 3: Fix any problems (if needed)
# ... make changes here ...

# Step 4: Validate again
issues = doc.validate()
if not issues:
    print("All clear!")

# Step 5: Save
doc.save("household-survey.xml")
print("Saved!")
```

Validez toujours avant de partager votre fichier.
Il est beaucoup plus facile de corriger les problèmes avant que d'autres dépendent de vos métadonnées.

---

!!! example "Scénario"
    Une équipe d'enquête prépare une enquête auprès des ménages pour publication.
    Elle doit marquer certaines questions avec des niveaux de sensibilité et des sources de données.
    Avant de publier, elle doit valider le document, corriger les problèmes et enregistrer un fichier propre.
    Votre travail est d'utiliser les propriétés, la recherche, la suppression et la validation pour préparer le document.

---

## Exercices

1. Créez une étude avec 3 questions : « How old are you? », « What is your household income? » et « What is your full name? ». Définissez `"sensitivity"` = `"high"` sur la question du revenu. Affichez ses propriétés.

    **Résultat attendu :**

    ```text
    {'sensitivity': 'high'}
    ```

2. Ajoutez une variable pour la question sur l'âge. Trouvez-la par son identifiant. Affichez l'identifiant.

    ```python
    v = doc.add_variable(name="Age", question=q_age)
    found = doc.find(v.identifier)
    print(f"Found: {found.identifier}")
    ```

3. Supprimez une question du document. Affichez le nouveau compteur pour vérifier la diminution.

    ```python
    doc.remove(q_name.identifier)
    print(f"Questions: {len(doc.questions)}")
    ```

    **Résultat attendu :**

    ```text
    Questions: 2
    ```

4. Validez le document. Affichez s'il est valide.

    ```python
    issues = doc.validate()
    if issues:
        for issue in issues:
            print(f"Problem: {issue.message}")
    else:
        print("Document is valid!")
    ```

---

## Quiz

???+ question "Question 1 : Que fait set_property ?"
    **A.** Crée une nouvelle variable.

    **B.** Attache une paire clé-valeur à un élément DDI.

    **C.** Enregistre le document dans un fichier.

    **D.** Supprime une propriété d'un élément.

    ??? success "Réponse"
        **B.** `set_property(key, value)` attache une paire clé-valeur
        personnalisée à tout élément DDI. Par exemple,
        `q.set_property("sensitivity", "high")`.

???+ question "Question 2 : Comment lire toutes les propriétés d'un élément ?"
    **A.** `item.get_property()`

    **B.** `item.all_properties()`

    **C.** `item.properties`

    **D.** `doc.properties(item)`

    ??? success "Réponse"
        **C.** Utilisez `item.properties` (sans parenthèses ; c'est
        une propriété, pas une méthode). Cela retourne un dictionnaire
        de toutes les paires clé-valeur.

???+ question "Question 3 : Que retourne doc.find(identifier) ?"
    **A.** Une liste de tous les éléments.

    **B.** L'élément avec cet identifiant, ou None s'il n'est pas
    trouvé.

    **C.** Une valeur True/False.

    **D.** La chaîne de l'identifiant elle-même.

    ??? success "Réponse"
        **B.** `doc.find(identifier)` cherche dans tous les types
        d'éléments et retourne celui qui correspond. Si rien ne
        correspond, il retourne `None`.

???+ question "Question 4 : Que fait doc.validate() ?"
    **A.** Enregistre le document.

    **B.** Supprime les éléments invalides.

    **C.** Vérifie le document par rapport au schéma DDI et retourne
    une liste de problèmes.

    **D.** Ajoute automatiquement les champs manquants.

    ??? success "Réponse"
        **C.** `validate()` vérifie si le document respecte les règles
        DDI. La méthode retourne une liste de problèmes. Une liste vide
        signifie que le document est valide.

???+ question "Question 5 : Que fait doc.remove(identifier) ?"
    **A.** Supprime une propriété d'un élément.

    **B.** Supprime le fichier XML du disque.

    **C.** Supprime l'élément avec cet identifiant et retourne True, ou
    retourne False s'il n'est pas trouvé.

    **D.** Supprime tous les éléments du document.

    ??? success "Réponse"
        **C.** `doc.remove(identifier)` trouve l'élément avec cet
        identifiant, le supprime du document et retourne `True`. Si
        aucun élément n'a cet identifiant, il retourne `False`.

---

!!! tip "Notes pour l'instructeur"
    - Les propriétés sont la partie la plus flexible de l'API. Insistez sur le fait qu'elles servent aux métadonnées propres à l'équipe pour lesquelles la norme DDI n'a pas de champ prédéfini.
    - Les méthodes `find()` et `remove()` fonctionnent avec des identifiants, pas des noms. Rappelez aux apprenants de sauvegarder l'identifiant quand ils créent un élément.
    - La boucle valider-corriger-valider est une habitude professionnelle. Comparez-la à la vérification orthographique d'un document avant de l'envoyer.
    - Erreur fréquente : les apprenants oublient que `properties` est une propriété (sans parenthèses), tandis que `get_property()` et `set_property()` sont des méthodes (avec parenthèses).
    - Si les apprenants posent des questions sur l'URN dans la section avancée des propriétés : expliquez qu'un URN est comme une adresse web pour un élément DDI. Il permet à d'autres systèmes de trouver l'élément. Ils n'ont pas besoin de mémoriser le format.
    - Ce module rassemble tout ce qui a été vu dans les modules 5 à 9. Pensez à terminer par un mini-projet : construire un document complet avec des questions, des variables, des concepts, des listes de codes et des propriétés, puis valider et enregistrer.

---

**Voir aussi :** [Guide de validation](../validation.md)
