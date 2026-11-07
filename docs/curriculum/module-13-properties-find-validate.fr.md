---
description: >-
  Module 13 du cours ddi-l : ajouter des propriétés personnalisées, trouver
  et supprimer des éléments, et valider avant d'enregistrer.
---

# Module 13 : Propriétés personnalisées, recherche, suppression et validation

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Ajouter, lire et supprimer des propriétés personnalisées sur un
      élément DDI avec `set_property()`, `get_property()`, `properties` et
      `remove_property()`.
    - **O2.** Trouver un élément par son identifiant avec `doc.find()`, et
      prédire ce que `doc.find()` retourne quand aucun élément n'a cet
      identifiant.
    - **O3.** Supprimer un élément avec `doc.remove()`, et corriger la
      référence brisée que `doc.lint()` signale quand un autre élément pointe
      encore vers lui.
    - **O4.** Corriger un document qui échoue à la validation : lire le
      message et le contexte de chaque problème, en corriger la cause, et
      relancer `doc.validate()` jusqu'à ce qu'il retourne une liste vide.

**Prérequis :** [Module 12](module-12-data-linkage.fr.md).

**Durée :** 40 min en autonomie / 50 min avec instructeur.

**Nouveau dans ce module :** `set_property()`, `get_property()`, `properties`,
`remove_property()`, `doc.find()`, `doc.remove()`, `issue.message`,
`issue.context`.

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

doc = ddi.new_study(title="Household Survey", agency="survey.example.org")

q_age = doc.add_question(text="How old are you?")
q_income = doc.add_question(text="What is your household income?")
q_name = doc.add_question(text="What is your full name?")

# Tag the income question as high sensitivity
q_income.set_property("sensitivity", "high")

# Tag the name question too
q_name.set_property("sensitivity", "high")
q_name.set_property("data_source", "self-reported")
```

Vous pouvez définir autant de propriétés que nécessaire sur n'importe quel
élément. Définir une clé que l'élément a déjà remplace sa valeur.

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

`properties` vous donne un nouveau dictionnaire chaque fois que vous le lisez.
Modifier ce dictionnaire ne modifie pas l'élément : utilisez les méthodes pour
cela.

## 4. Supprimer une propriété

Utilisez `item.remove_property(key)` pour supprimer une propriété.
La méthode retourne `True` si la propriété a été trouvée et supprimée, ou `False` si la clé n'existait pas.

```python
removed = q_name.remove_property("data_source")
print(removed)  # -> True
print(q_name.properties)  # -> {'sensitivity': 'high'}
```

## 5. Trouver des éléments par identifiant

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
print(found.names[0].text)  # -> Age
```

Si aucun élément ne correspond, `doc.find()` retourne `None`. La méthode ne
lève pas d'erreur : vérifiez donc le résultat avant de l'utiliser.

```python
print(doc.find("not-an-identifier"))  # -> None
```

## 6. Supprimer des éléments

Utilisez `doc.remove(identifier)` pour supprimer un élément du document.
La méthode retourne `True` si l'élément a été trouvé et supprimé, et `False`
si aucun élément n'a cet identifiant.

```python
print(f"Questions before: {len(doc.questions)}")  # -> 3

# Remove the name question
doc.remove(q_name.identifier)

print(f"Questions after: {len(doc.questions)}")  # -> 2
```

Attention : la suppression est permanente.
Il n'y a pas de retour en arrière.

### La suppression laisse des références derrière elle

`doc.remove()` supprime l'élément et rien d'autre. Si un autre élément y
renvoie, cette **référence** (le lien d'un élément vers un autre, Module 4)
reste, et ne pointe plus vers rien. La variable `Age` renvoie à la question
sur l'âge. Supprimez la question et demandez à `doc.lint()` (Module 3) ce
qu'il trouve :

```python
doc.remove(q_age.identifier)

for finding in doc.lint():
    if finding.severity == "error":
        print(finding.rule_id)  # -> ddi.reference.integrity
```

La règle `ddi.reference.integrity` veut dire « cette référence ne mène à
aucun élément du document ». `doc.validate()` ne la signale pas : le schéma
vérifie la forme du fichier, pas si chaque référence trouve sa cible.
`doc.save()` émet aussi un avertissement.

Vous avez deux façons de corriger. Retirer la référence, pour que la variable
ne nomme plus de question. Ou supprimer aussi la variable, si elle n'a pas de
sens sans la question. Ici, la variable reste et la référence part :

```python
v1.question_references = [
    ref for ref in v1.question_references if ref.identifier != q_age.identifier
]

errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
```

## 7. Lire un problème de validation

Au Module 3, vous avez lancé `doc.validate()` sur une étude correcte et
obtenu une liste vide. Voici à quoi ressemble un problème.

Une erreur fréquente est une balise de langue écrite avec un trait de
soulignement, `fr_CA`. La norme l'écrit avec un trait d'union : `fr-CA`.
Ajoutez un texte français avec la mauvaise balise et validez :

```python
from ddi_l.models.base import InternationalString

q_income.question_texts.append(
    InternationalString(text="Quel est le revenu de votre ménage ?", lang="fr_CA")
)

issues = doc.validate()
print(f"Issues: {len(issues)}")  # -> Issues: 1
for issue in issues:
    print(issue.message)
    print(issue.context)
```

Résultat attendu :

```text
Issues: 1
attribute {http://www.w3.org/XML/1998/namespace}lang='fr_CA': value doesn't match any pattern of ['[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*']
<d:Text> Quel est le revenu de votre ménage ?
```

Chaque problème a deux parties à lire :

- **`message`** dit quelle règle le fichier enfreint. Ici, un attribut,
  `{http://www.w3.org/XML/1998/namespace}lang` (le nom long de `xml:lang`),
  contient `fr_CA`. Cette valeur ne correspond pas au **motif** que le schéma
  autorise : des lettres, puis des parties facultatives qui commencent
  chacune par un trait d'union.
- **`context`** montre l'élément et le début de son texte : un `<d:Text>`
  qui contient le texte français que vous venez d'ajouter. Cela vous dit
  quel élément corriger.

Si le contexte ne suffit pas, `issue.xpath` donne le chemin complet de
l'élément dans le fichier.

## 8. La boucle valider-corriger-valider

Avant de publier ou de partager un fichier DDI, suivez cette boucle :

1. **Validez** avec `doc.validate()`.
2. **Lisez** le message et le contexte de chaque problème.
3. **Corrigez** la cause dans votre document.
4. **Validez à nouveau**, et revenez à l'étape 2 jusqu'à ce que la liste soit vide.
5. **Enregistrez** le fichier.

Corrigez la balise de langue de la section 7, validez à nouveau et
enregistrez :

```python
q_income.question_texts[-1].lang = "fr-CA"

issues = doc.validate()
print(f"Issues: {len(issues)}")  # -> Issues: 0

doc.save("household-survey.xml")
```

L'étape 4 n'est pas une formalité. Une correction peut être fausse, et le
validateur ne signale pas toujours tous les problèmes d'un coup : quand une
erreur l'empêche de vérifier le reste d'un élément, le problème suivant
n'apparaît qu'une fois le premier corrigé. Lancez aussi `doc.lint()`, car la
validation ne voit pas les références brisées (section 6).

---

!!! example "Scénario"
    Une équipe d'enquête prépare une enquête auprès des ménages pour publication.
    Elle doit marquer certaines questions avec des niveaux de sensibilité et des sources de données.
    Avant de publier, elle doit supprimer une question abandonnée, valider le
    document, corriger les problèmes et enregistrer un fichier propre.

---

## Exercices

1. **(O1)** Créez une étude avec 3 questions : « How old are you? », « What is your household income? » et « What is your full name? ». Définissez `"sensitivity"` = `"high"` sur la question du revenu. Sur la question du nom, définissez `"sensitivity"` = `"high"` et `"data_source"` = `"self-reported"`, et affichez ses propriétés. Supprimez ensuite `"data_source"`, affichez ce que retourne `remove_property()`, et affichez de nouveau les propriétés.

    **Résultat attendu :**

    ```text
    {'sensitivity': 'high', 'data_source': 'self-reported'}
    True
    {'sensitivity': 'high'}
    ```

    ??? success "Réponse"
        ```python
        import ddi_l as ddi

        doc = ddi.new_study(title="Household Survey", agency="research.org")
        q_age = doc.add_question(text="How old are you?")
        q_income = doc.add_question(text="What is your household income?")
        q_name = doc.add_question(text="What is your full name?")

        q_income.set_property("sensitivity", "high")
        q_name.set_property("sensitivity", "high")
        q_name.set_property("data_source", "self-reported")
        print(q_name.properties)
        # -> {'sensitivity': 'high', 'data_source': 'self-reported'}

        print(q_name.remove_property("data_source"))  # -> True
        print(q_name.properties)  # -> {'sensitivity': 'high'}
        ```

2. **(O2)** Ajoutez une variable nommée `Age` pour la question sur l'âge. Trouvez-la par son identifiant et affichez son nom. Prédisez ensuite ce que retourne `doc.find("not-an-identifier")`, et affichez-le pour vérifier.

    **Résultat attendu :**

    ```text
    Found: Age
    None
    ```

    ??? success "Réponse"
        ```python
        v_age = doc.add_variable(name="Age", question=q_age)

        found = doc.find(v_age.identifier)
        print(f"Found: {found.names[0].text}")  # -> Found: Age
        print(doc.find("not-an-identifier"))  # -> None
        ```

        `doc.find()` retourne `None` quand rien ne correspond ; la méthode ne lève pas d'erreur.

3. **(O3)** Supprimez la question du nom et affichez le nouveau nombre de questions. Appelez ensuite `doc.remove()` de nouveau avec le même identifiant et affichez ce qu'il retourne.

    **Résultat attendu :**

    ```text
    Questions: 2
    False
    ```

    ??? success "Réponse"
        ```python
        doc.remove(q_name.identifier)
        print(f"Questions: {len(doc.questions)}")  # -> Questions: 2
        print(doc.remove(q_name.identifier))  # -> False
        ```

        Le second appel ne trouve rien à supprimer : il retourne donc `False`.

4. **(O3)** Supprimez la question sur l'âge, à laquelle renvoie la variable `Age`. Lancez `doc.lint()` et affichez la règle de chaque erreur. Corrigez la référence brisée en la retirant de la variable, puis affichez le nombre d'erreurs de lint.

    **Résultat attendu :**

    ```text
    ddi.reference.integrity
    Lint errors: 0
    ```

    ??? success "Réponse"
        ```python
        doc.remove(q_age.identifier)

        for finding in doc.lint():
            if finding.severity == "error":
                print(finding.rule_id)  # -> ddi.reference.integrity

        v_age.question_references = [
            ref for ref in v_age.question_references if ref.identifier != q_age.identifier
        ]
        errors = [finding for finding in doc.lint() if finding.severity == "error"]
        print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
        ```

        Supprimer aussi la variable `Age` (`doc.remove(v_age.identifier)`) est une autre bonne correction, si la variable n'a pas de sens sans sa question.

5. **(O4)** Le bloc ci-dessous met deux erreurs dans la question du revenu. Lancez `doc.validate()` et affichez le nombre de problèmes et le contexte du premier. Corrigez cette cause, et validez à nouveau. Recommencez jusqu'à ce qu'il n'y ait plus de problème, puis enregistrez le document sous `household-clean.xml`.

    ```python
    from ddi_l.models.base import InternationalString

    q_income.question_texts.append(
        InternationalString(text="Revenu du ménage ?", lang="fr_CA")
    )
    q_income.version = "1.a"
    ```

    **Résultat attendu :**

    ```text
    Issues: 1
    <r:Version> 1.a
    Issues: 1
    <d:Text> Revenu du ménage ?
    Issues: 0
    ```

    ??? success "Réponse"
        ```python
        issues = doc.validate()
        print(f"Issues: {len(issues)}")  # -> Issues: 1
        print(issues[0].context)  # -> <r:Version> 1.a

        # A version is numbers separated by dots
        q_income.version = "1.1"
        issues = doc.validate()
        print(f"Issues: {len(issues)}")
        print(issues[0].context)  # -> <d:Text> Revenu du ménage ?

        # A language tag uses a hyphen, not an underscore
        q_income.question_texts[-1].lang = "fr-CA"
        issues = doc.validate()
        print(f"Issues: {len(issues)}")  # -> Issues: 0

        doc.save("household-clean.xml")
        ```

        La première validation ne signale que la version. La balise de langue apparaît une fois la version corrigée : c'est pourquoi on valide à nouveau après chaque correction.

---

## Quiz

???+ question "Question 1 (O1) : Qu'affiche print(q.properties) après ces deux appels ?"
    `q.set_property("sensitivity", "high")`, puis
    `q.set_property("sensitivity", "low")`.

    **A.** `{'sensitivity': 'high'}`

    **B.** `{'sensitivity': ['high', 'low']}`

    **C.** `{'sensitivity': 'low'}`

    **D.** Une erreur, parce que la clé existe déjà.

    ??? success "Réponse"
        **C.** Définir une clé que l'élément a déjà remplace sa valeur. Un
        élément a au plus une valeur par clé.

???+ question "Question 2 (O1) : Quelle ligne supprime la propriété data_source de l'élément q ?"
    **A.** `q.remove_property("data_source")`

    **B.** `del q.properties["data_source"]`

    **C.** `doc.remove("data_source")`

    **D.** `q.get_property("data_source")`

    ??? success "Réponse"
        **A.** `remove_property()` supprime la clé et retourne `True`. B
        supprime la clé d'un nouveau dictionnaire construit par
        `properties`, et l'élément la garde. C supprime des éléments par
        identifiant, pas des propriétés. D ne fait que lire la valeur.

???+ question "Question 3 (O2) : doc.remove(v.identifier) vient de retourner True. Que retourne maintenant doc.find(v.identifier) ?"
    **A.** La variable `v`.

    **B.** `True`

    **C.** Une erreur, parce que l'identifiant est inconnu.

    **D.** `None`

    ??? success "Réponse"
        **D.** La variable n'est plus dans le document : rien ne
        correspond, et `doc.find()` retourne `None` au lieu de lever une
        erreur.

???+ question "Question 4 (O3) : Vous supprimez une question à laquelle une variable renvoie. doc.validate() retourne une liste vide. Le document est-il prêt à être partagé ?"
    **A.** Oui. Une liste vide veut dire qu'il n'y a rien à corriger.

    **B.** Non. `doc.lint()` signale `ddi.reference.integrity` : la variable
    pointe encore vers la question supprimée, alors corrigez d'abord cette
    référence.

    **C.** Non. Le schéma aurait dû l'attraper : le schéma est donc brisé.

    **D.** Oui. `doc.save()` retire les références brisées pour vous.

    ??? success "Réponse"
        **B.** La validation vérifie la forme du fichier par rapport au
        schéma, pas si chaque référence trouve sa cible. Le lint, oui.
        `doc.save()` avertit de la référence brisée, mais la garde.

???+ question "Question 5 (O4) : La validation signale ce problème. Quelle correction est la bonne ?"
    ```text
    attribute {http://www.w3.org/XML/1998/namespace}lang='en_US': value doesn't match any pattern of ['[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*']
    <d:Text> How old are you?
    ```

    **A.** Changer la balise de langue de ce texte de question en `en-US`.

    **B.** Supprimer la question « How old are you? ».

    **C.** Ajouter une étiquette à la question.

    **D.** Enregistrer le fichier, puis valider le fichier enregistré.

    ??? success "Réponse"
        **A.** Le message dit que la valeur `en_US` de `xml:lang` ne
        correspond pas au motif autorisé, qui utilise des traits d'union. Le
        contexte montre quel texte la contient. Supprimer la question (B)
        perd des données pour cacher le problème ; C et D ne changent pas la
        balise.

???+ question "Question 6 (O4) : La validation signale ce problème sur la version d'une question. Quelle valeur passe ?"
    ```text
    value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*']
    <r:Version> 1.a
    ```

    **A.** `"1.a"`

    **B.** `"v1.1"`

    **C.** `"1.1"`

    **D.** `"1-1"`

    ??? success "Réponse"
        **C.** Le motif autorise des nombres séparés par des points, et rien
        d'autre. Validez à nouveau après la correction pour la confirmer, et
        pour voir un problème que le premier aurait caché.

---

## Pour aller plus loin (facultatif)

### Stocker un lien vers une liste de codes dans une propriété

Vous pouvez passer un objet liste de codes (ou tout élément DDI) comme valeur
d'une propriété. La bibliothèque stocke l'**URN** (Uniform Resource Name) de
l'élément, une adresse unique qui l'identifie.

```python
cl = doc.add_code_list(name="Income Brackets")
q_income.set_property("vocabulary", cl)

print(q_income.get_property("vocabulary").startswith("urn:ddi:"))  # -> True
```

Cela lie une question à la liste de codes qui définit ses réponses
autorisées. Le [Module 14](module-14-custom-fields.fr.md) s'en sert pour adosser
un champ personnalisé à un vocabulaire contrôlé.

---

## Faites le point

- [ ] Je peux ajouter, lire et supprimer des propriétés personnalisées sur un élément DDI. (O1)
- [ ] Je peux trouver un élément par son identifiant et dire ce que `doc.find()` retourne quand rien ne correspond. (O2)
- [ ] Je peux supprimer un élément et corriger la référence brisée que `doc.lint()` signale. (O3)
- [ ] Je peux lire un problème de validation, en corriger la cause, et valider à nouveau jusqu'à ce que la liste soit vide. (O4)

---

!!! tip "Notes pour l'instructeur"
    - Les propriétés sont la partie la plus flexible de l'API. Insistez sur le fait qu'elles servent aux métadonnées propres à l'équipe pour lesquelles la norme DDI n'a pas de champ prédéfini.
    - Les méthodes `find()` et `remove()` fonctionnent avec des identifiants, pas des noms. Rappelez aux apprenants de sauvegarder l'identifiant quand ils créent un élément.
    - La boucle valider-corriger-valider est une habitude professionnelle. Comparez-la à la vérification orthographique d'un document avant de l'envoyer. L'exercice 5 montre pourquoi l'étape 4 compte : la seconde erreur n'apparaît qu'une fois la première corrigée.
    - Erreur fréquente : les apprenants oublient que `properties` est une propriété (sans parenthèses), tandis que `get_property()` et `set_property()` sont des méthodes (avec parenthèses).
    - Faites sauter une fois aux apprenants la correction de référence de l'exercice 4, puis enregistrer : le `DDIReferenceWarning` montre que supprimer un élément peut en briser un autre.
    - Ce module s'appuie sur les précédents. Le Module 12 utilisait déjà `set_property()` pour marquer les clés de couplage ; le Module 3 a présenté `doc.validate()` et `doc.lint()`, et le Module 7 les lance depuis la ligne de commande. Pour un mini-projet de clôture, faites construire un document avec des questions et des variables (Modules 3 et 4), des concepts (Module 5), des listes de codes (Module 9) et des propriétés, puis le valider, le corriger et l'enregistrer.

---

**Voir aussi :** [Guide de validation](../validation.fr.md)
