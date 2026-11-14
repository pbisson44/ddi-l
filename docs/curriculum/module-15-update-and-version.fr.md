---
description: >-
  Module 15 du cours ddi-l : mettre à jour des fichiers DDI publiés,
  incrémenter les versions, consigner les justifications et garder les
  références à jour.
---

# Module 15 : Mettre à jour et versionner vos documents

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Ouvrir un fichier DDI existant, ajouter et retirer des
      éléments, et enregistrer le résultat sous un nouveau nom pour que
      l'ancien fichier reste inchangé.
    - **O2.** Donner sa version suivante à un élément modifié (`1` devient
      `2`), prédire le numéro qu'il reçoit, et expliquer pourquoi `ddi-l` ne
      transforme pas `1` en `1.1` à moins que vous ne le demandiez.
    - **O3.** Consigner une justification de version et une responsabilité
      de version sur l'élément que vous avez modifié.
    - **O4.** Modifier le libellé d'une question dans toutes ses langues, lui
      donner une nouvelle version, et faire pointer la variable qui y renvoie
      vers sa nouvelle version pour que `doc.lint()` ne signale aucune erreur.
    - **O5.** Faire passer une variable à une autre liste de codes avec
      `set_coded()`, vérifier quelle liste elle utilise maintenant, et lui
      donner une nouvelle version avec une justification.

**Prérequis :** [Module 14](module-14-custom-fields.fr.md).

**Durée :** 65 min en autonomie / 75 min avec instructeur.

**Nouveau dans ce module :** `increment_version()`, `VersionRationale`,
`version_rationales`, `version_responsibility`, `to_reference()`,
`set_coded()` ; pour les versions pointées seulement,
`increment_major_version()`, `increment_minor_version()`,
`increment_subversion()` et `allow_dotted=True`.

---

## 1. Pourquoi le versionnement est important

Les enquêtes changent au fil du temps. Un recensement peut ajouter une
nouvelle question sur l'accès à Internet en 2024. Une enquête sur la
population active peut retirer une question dépassée sur les télécopieurs.
Quand vous modifiez un document, vous devez répondre à deux questions :

1. **Qu'est-ce qui a changé ?** Quels éléments ont été ajoutés, retirés ou modifiés ?
2. **Pourquoi cela a-t-il changé ?** Quelle était la raison de la mise à jour ?

Le **versionnement** consiste à donner à chaque copie d'un document un numéro
(1, 2, 3...) pour pouvoir les distinguer. C'est comme
enregistrer une rédaction scolaire sous « redaction-v1 », « redaction-v2 » et
« redaction-v3 ». Chaque version est une photo à un moment donné.

Sans versionnement, vous ne pouvez pas revenir à une copie précédente. Vous ne
pouvez pas comparer ce qui a changé d'une année à l'autre. Et vous ne pouvez
pas expliquer vos choix aux autres personnes.

---

## 2. Le processus de mise à jour

Les étapes de base pour mettre à jour un document DDI sont :

1. **Ouvrir** le fichier existant.
2. **Ajouter** du nouveau contenu (questions, variables, concepts).
3. **Retirer** le contenu obsolète.
4. **Vérifier** le résultat, et l'**enregistrer** sous un nouveau nom.

Voici un court exemple. Les trois premières lignes tiennent lieu du fichier de
l'an dernier ; si vous avez déjà un fichier DDI, ouvrez le vôtre et sautez-les.

```python
import ddi_l as ddi

# Stand-in for last year's file
last_year = ddi.new_study(title="Labour Force Survey 2023", agency="ca.statcan")
last_year.add_question(text="Do you use a fax machine at work?")
last_year.save("lfs-2023.xml")

# Step 1: Open the existing file
doc = ddi.open_ddi("lfs-2023.xml")

# Step 2: Add a new question
doc.add_question(text="Do you work from home?")

# Step 3: Remove the outdated question, by its identifier
fax = next(
    q
    for q in doc.questions
    if q.question_texts[0].text == "Do you use a fax machine at work?"
)
doc.remove(fax.identifier)

# Step 4: Check, then save with a new filename
print(doc.validate())  # -> []
doc.save("lfs-2024.xml")
```

La fonction `ddi.open_ddi()` lit un fichier DDI XML depuis le disque et vous
donne un objet `Document`. Vous pouvez ensuite ajouter ou retirer des éléments
comme vous l'avez fait lors de la création du document. La fonction
`doc.save()` écrit le document mis à jour dans un nouveau fichier : ainsi
`lfs-2023.xml` reste exactement tel quel, et vous pouvez encore comparer les
deux années, ou revenir en arrière.

---

## 3. Les numéros de version

Chaque élément DDI possède une **version**. La plupart des outils numérotent
les versions avec des nombres entiers : un élément commence à la version `1`,
et chaque changement enregistré lui donne la suivante, `2`, puis `3`. `ddi-l`
fonctionne aussi ainsi : chaque élément que vous créez commence à `"1"`.

Vous pouvez lire la version actuelle de n'importe quel élément :

```python
study = doc.study_unit
print(study.version)  # e.g. "1"
```

Le numéro indique *que* l'élément a changé, pas à quel point. L'ampleur du
changement, et le fait que les réponses restent ou non comparables avec la
version précédente, se notent dans la justification de l'élément (section 5).

---

## 4. Donner à un élément sa version suivante

`increment_version()` donne à un élément sa version suivante. C'est une
méthode sur n'importe quel élément DDI (question, variable, concept, étude,
etc.). Un **élément** est tout objet qui étend `MaintainableBase`, la classe de
base pour tous les objets DDI.

Prédisez chaque version affichée avant de lancer le bloc :

```python
item = doc.add_question(text="How many hours do you work per week?")
print(item.version)  # -> 1

item.increment_version()
print(item.version)  # -> 2

item.increment_version()
print(item.version)  # -> 3
```

Chaque élément compte ses propres changements : une question à la version `3`
peut côtoyer une variable à la version `1`.

### Si votre organisation utilise des versions pointées

DDI permet aussi des versions avec des points, comme `1.0.0`. Certaines
organisations donnent un sens à chaque partie, la taille du changement :
majeure, mineure et sous-version (un correctif). `ddi-l` a une méthode pour chaque partie, qui
augmente cette partie de un et remet à zéro les parties à sa droite :

| Méthode | À partir de `1.2.3` |
| --- | --- |
| `increment_major_version()` | `2.0.0` |
| `increment_minor_version()` | `1.3.0` |
| `increment_subversion()` | `1.2.4` |

Un élément garde sa numérotation. Sur une version entière,
`increment_minor_version()` et `increment_subversion()` lèvent une erreur au
lieu de rendre `"3"` pointée (`"3.1"`, `"3.0.1"`), car les outils qui numérotent les
versions 1, 2, 3 risquent de ne pas relire une version pointée. Ne passez
`allow_dotted=True` que si votre organisation utilise vraiment des versions
pointées :

```python
try:
    item.increment_minor_version()
except ddi.DDIModelError:
    print("Refused: a whole-number version stays whole")
# -> Refused: a whole-number version stays whole

item.version = "1.2.3"
item.increment_minor_version()
print(item.version)  # -> 1.3.0
```

La suite de ce module utilise des nombres entiers.

---

## 5. Enregistrer pourquoi vous avez changé quelque chose

Une **justification de version** est une courte note qui explique pourquoi un
changement a été fait. DDI stocke cette information dans le XML pour que toute
personne qui ouvre le fichier plus tard puisse comprendre l'historique.

Vous définissez aussi la **responsabilité de version** : le nom de la personne
ou de l'équipe qui a fait le changement.

<!-- docs-test: skip -- fragment: `item` is whichever item the reader is versioning -->
```python
from ddi_l.models.base import VersionRationale, InternationalString

# Create a rationale with a description
rationale = VersionRationale(
    descriptions=[
        InternationalString(text="Added work-from-home question for 2024 wave")
    ]
)

# Attach it to an item
item.version_rationales.append(rationale)

# Record who made the change
item.version_responsibility = "Survey Design Team"
```

- `VersionRationale` est un petit objet qui contient une liste de
  descriptions. Chaque description est un `InternationalString` pour que vous
  puissiez l'écrire dans plusieurs langues.
- `version_rationales` est une liste, mais le schéma n'autorise qu'une
  justification par élément : la raison de sa version actuelle. Si l'élément
  en a déjà une, issue d'un changement précédent, remplacez-la
  (`item.version_rationales = [rationale]`) au lieu d'en ajouter une
  seconde ; avec deux, `doc.validate()` signale une erreur.
- `version_responsibility` est une chaîne de texte simple avec le nom de la
  personne ou de l'équipe.

Placez la justification et la responsabilité sur l'élément que vous avez
modifié. Une question reformulée reçoit les siennes ; l'étude n'en reçoit que
pour un changement de l'étude.

---

## 6. Modifier le libellé d'une question

Ajouter et retirer des questions n'est qu'une partie du travail. La plupart des
mises à jour d'enquête *modifient* quelque chose qui existe déjà : une question
reçoit un libellé plus clair, ou ses catégories de réponse changent. Cette
section et la suivante montrent les deux cas, sur le même petit fichier.

Le fichier contient une question, « Do you work from home? » (Travaillez-vous
à domicile ?). On y répond avec une liste de codes **Oui/Non**, et la réponse
est stockée dans la variable `WFH`. Le bloc ci-dessous crée ce fichier, avec
le modèle de liste de codes du [Module 14](module-14-custom-fields.fr.md).
Sautez-le si vous avez votre propre fichier.

```python
from uuid import uuid4

import ddi_l as ddi
from ddi_l.models.base import InternationalString, VersionRationale
from ddi_l.models.logicalproduct import Category, CodeItem


def add_codes(doc, code_list, answers):
    """Add one Category and one Code per (value, name) pair to code_list."""
    for value, name in answers:
        category = doc.add_item(Category, name=name, label=name)
        code_list.codes.append(
            CodeItem(
                agency=code_list.agency,
                identifier=str(uuid4()),
                version=code_list.version,
                value=value,
                category=category.to_reference(),
            )
        )


# Stand-in for last year's file
last_year = ddi.new_study(title="Labour Force Survey 2023", agency="ca.statcan")
question = last_year.add_question(text="Do you work from home?", label="Work from home")
yes_no = last_year.add_code_list(name="Yes/No", label="Yes/No")
add_codes(last_year, yes_no, [("1", "Yes"), ("2", "No")])
wfh = last_year.add_variable(name="WFH", label="Works from home", question=question)
wfh.set_coded(yes_no)
last_year.save("wfh-2023.xml")
```

### Étape 1 : Trouver la question

Ouvrez le fichier et trouvez la question par son texte actuel :

```python
doc = ddi.open_ddi("wfh-2023.xml")

wfh_question = next(
    q for q in doc.questions if q.question_texts[0].text == "Do you work from home?"
)
```

Si vous connaissez l'identifiant de la question, `doc.find(identifier)` du
[Module 13](module-13-properties-find-validate.fr.md) fonctionne aussi.

### Étape 2 : Changer le texte

Le libellé d'une question est conservé dans `question_texts`, une liste avec
un `InternationalString` par langue. Changez le `text` de la langue que vous
mettez à jour :

```python
for text in wfh_question.question_texts:
    if text.lang == "en":
        text.text = "In a typical week, do you work from home?"

print(wfh_question.question_texts[0].text)
# -> In a typical week, do you work from home?
```

!!! warning "Mettez à jour toutes les langues"
    Si la question a aussi un texte en français (Module 3), changez-le aussi,
    dans la même boucle (`if text.lang == "fr": ...`). Sinon, les versions
    anglaise et française ne posent plus la même question.

### Étape 3 : Versionner la question et dire pourquoi

La question a changé, donc elle reçoit sa version suivante. Que le changement
soit petit, comme celui-ci, ou qu'il change ce que la question mesure, le
numéro augmente de un ; la justification dit de quel cas il s'agit.

```python
wfh_question.increment_version()
wfh_question.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Added the reference period 'in a typical week'")
        ]
    )
)
wfh_question.version_responsibility = "Survey Design Team"

print(wfh_question.version)  # -> 2
```

### Étape 4 : Faire pointer la variable vers la nouvelle version

Une référence DDI désigne une version précise d'un élément. La variable `WFH`
dit encore « question `…`, version `1` ». Cette version n'est plus dans le
fichier, donc la référence est maintenant brisée. Faites-la pointer vers la
nouvelle version de la question :

```python
for variable in doc.variables:
    variable.question_references = [
        wfh_question.to_reference()
        if ref.identifier == wfh_question.identifier
        else ref
        for ref in variable.question_references
    ]
```

`to_reference()` construit une référence à l'élément tel qu'il est
*maintenant*, avec sa nouvelle version.

Laissez ensuite `doc.lint()` vérifier que plus rien ne pointe vers l'ancienne
version. Chaque erreur `ddi.reference.integrity` qu'il signale désigne un
élément qu'il vous reste à faire pointer vers la nouvelle version :

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
```

Dans ce fichier, seule la variable fait référence à la question. Un fichier
plus grand peut avoir d'autres références vers elle : voyez
[Pour aller plus loin](#pour-aller-plus-loin-facultatif).

---

## 7. Passer une variable à une autre liste de codes

Pour la vague 2024, une simple réponse Oui/Non ne suffit plus. L'équipe veut
savoir *à quelle fréquence* les gens travaillent à domicile. Les catégories de
réponse passent de **Oui/Non** à une nouvelle liste de codes **Fréquence**.

### Étape 1 : Créer la nouvelle liste de codes

```python
frequency = doc.add_code_list(name="Frequency", label="Frequency")
add_codes(doc, frequency, [("1", "Every day"), ("2", "Some days"), ("3", "Never")])
```

### Étape 2 : Faire pointer la variable vers elle

`set_coded()` indique à une variable quelle liste de codes contient ses
valeurs. L'appeler à nouveau remplace l'ancienne liste de codes par la
nouvelle :

```python
wfh = next(v for v in doc.variables if v.names[0].text == "WFH")
wfh.set_coded(frequency)
```

Vous pouvez vérifier quelle liste de codes une variable utilise maintenant.
Lisez la référence dans la représentation de la variable, puis cherchez-la
avec `doc.find()` :

```python
reference = wfh.variable_representation.code_representation.code_list_reference
current = doc.find(reference.identifier)

print(current.names[0].text)  # -> Frequency
print([code.value for code in current.codes])  # -> ['1', '2', '3']
```

### Étape 3 : Versionner la variable et dire pourquoi

De nouvelles catégories de réponse changent ce que la variable peut contenir.
Des réponses codées 1 ou 2 l'an dernier et 1, 2 ou 3 cette année ne peuvent
pas être comparées directement : la variable reçoit sa version suivante, et la
justification le dit :

```python
wfh.increment_version()
wfh.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(
                text="Answer categories changed from Yes/No to Frequency; "
                "not comparable with 2023"
            )
        ]
    )
)
wfh.version_responsibility = "Survey Design Team"

print(wfh.version)  # -> 2
```

La question et la variable sont toutes deux passées de `1` à `2` : chaque
élément compte ses propres changements.

Dans ce fichier, rien ne fait référence à la variable. Si quelque chose le
faisait (une variable dérivée, un schéma d'enregistrement), cela pointerait
maintenant vers l'ancienne version : [Pour aller plus
loin](#pour-aller-plus-loin-facultatif) montre comment s'en occuper.

### Étape 4 : Garder ou retirer l'ancienne liste de codes

La liste de codes Oui/Non est encore dans le fichier. Gardez-la si d'autres
variables l'utilisent encore, ou si vous voulez que le fichier montre ce que
signifiaient les réponses de l'an dernier. Si plus rien ne l'utilise,
retirez-la :

```python
old_list = next(cl for cl in doc.code_lists if cl.names[0].text == "Yes/No")
doc.remove(old_list.identifier)

print([cl.names[0].text for cl in doc.code_lists])  # -> ['Frequency']
```

Les catégories « Yes » et « No » restent dans le fichier. C'est sans danger,
et d'autres listes de codes peuvent encore les réutiliser.

Enfin, vérifiez le fichier et enregistrez-le sous un nouveau nom, pour que le
fichier de l'an dernier reste tel quel. `doc.validate()` vérifie le fichier
par rapport au schéma DDI seulement. Il ne remarque pas une référence à une
version qui n'existe plus ; exécutez donc aussi `doc.lint()` :

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
print(doc.validate())  # -> []

doc.save("wfh-2024.xml")
```

!!! note "Le domaine de réponse de la question"
    Dans ce programme, une liste de codes est rattachée à la **variable**. Les
    fichiers d'autres outils la rattachent souvent aussi à la **question**,
    dans un élément `d:CodeDomain` à l'intérieur de la question. `ddi-l`
    conserve cet élément exactement tel qu'il a été lu : `set_coded()` ne
    change que la variable, et `ddi-l` n'a pas encore d'aide pour changer le
    domaine de réponse d'une question. Si votre fichier en a un, ouvrez-le
    dans un éditeur de texte après le changement et vérifiez quelle liste de
    codes désigne le `r:CodeListReference` de la question.

---

## 8. Bonnes pratiques

- **Gardez les anciennes versions.** Enregistrez chaque version dans un
  fichier différent (comme `survey-v1.xml`, `survey-v2.xml`). N'écrasez pas
  les anciens fichiers.
- **Laissez la justification dire l'ampleur du changement.** Chaque
  changement enregistré donne à l'élément sa version suivante. La
  justification dit ce qui a changé, et si les réponses restent comparables
  avec la version précédente.
- **Versionnez l'élément modifié, pas seulement l'étude.** Une question
  reformulée ou une variable avec de nouvelles catégories de réponse reçoit
  sa propre augmentation de version, sa justification et sa responsabilité.
- **Écrivez des justifications claires.** Une bonne justification dit *ce
  qui* a changé et *pourquoi*.
- **Mettez à jour les références, puis vérifiez.** Après une augmentation de
  version, faites pointer chaque référence à l'élément vers sa nouvelle
  version. Exécutez `doc.validate()` et `doc.lint()`, et corrigez chaque
  erreur avant de partager le fichier.

---

## Exercices

!!! example "Scénario"
    Une enquête nationale sur la population active est menée chaque année. La
    version 2024 a ajouté une nouvelle question, retiré une ancienne, et
    reformulé et recodé la question sur l'emploi. L'agence doit mettre à jour
    le document DDI et enregistrer pourquoi.

**Exercice 1 (O1).** Créez une étude, « Labour Force Survey v1 », avec trois
questions : « What is your current employment status? » (avec le texte
français « Quelle est votre situation d'emploi actuelle ? »), « How many hours
do you work per week? » et « Do you use a fax machine at work? ». Ajoutez une
variable `EMPSTAT` pour la première question. Enregistrez l'étude sous
`survey-v1.xml`.

Résultat attendu :

```text
Saved with 3 questions and 1 variable.
```

??? success "Réponse"
    ```python
    import ddi_l as ddi
    from ddi_l.models.base import InternationalString

    doc = ddi.new_study(title="Labour Force Survey v1", agency="ca.statcan")
    q1 = doc.add_question(text="What is your current employment status?")
    q1.question_texts.append(
        InternationalString(
            text="Quelle est votre situation d'emploi actuelle ?", lang="fr"
        )
    )
    q2 = doc.add_question(text="How many hours do you work per week?")
    q3 = doc.add_question(text="Do you use a fax machine at work?")
    doc.add_variable(name="EMPSTAT", label="Employment status", question=q1)

    doc.save("survey-v1.xml")
    print(f"Saved with {len(doc.questions)} questions and {len(doc.variables)} variable.")
    ```

**Exercice 2 (O1).** Rouvrez `survey-v1.xml`. Ajoutez la question « How many
hours do you sleep per night? ». Retirez la question sur le télécopieur,
trouvée par son texte. Affichez le nombre de questions avant et après, et
vérifiez le document avec `doc.validate()`.

Résultat attendu :

```text
Before: 3 questions
After: 3 questions
[]
```

??? success "Réponse"
    ```python
    doc = ddi.open_ddi("survey-v1.xml")
    print(f"Before: {len(doc.questions)} questions")

    # Add a new question
    doc.add_question(text="How many hours do you sleep per night?")

    # Remove the outdated fax question
    fax_q = next(
        q
        for q in doc.questions
        if q.question_texts[0].text == "Do you use a fax machine at work?"
    )
    doc.remove(fax_q.identifier)
    print(f"After: {len(doc.questions)} questions")
    print(doc.validate())  # -> []
    ```

    Le compte est le même, mais pas le contenu : une question entre, une sort.
    `survey-v1.xml` sur le disque reste inchangé tant que vous ne
    l'écrasez pas, ce que vous ne ferez pas.

**Exercice 3 (O2).** Une question est à la version `3`. (a) Vous y corrigez
une faute de frappe et lui donnez sa version suivante. (b) Vous remplacez
ensuite ses catégories de réponse, et les réponses ne sont plus comparables
avec l'an dernier ; vous lui donnez encore sa version suivante. Prédisez les
deux versions, puis vérifiez-les en Python. (c) Que se passe-t-il si vous
appelez ensuite `increment_minor_version()` dessus ?

Résultat attendu :

```text
4
5
Refused
```

??? success "Réponse"
    (a) `4`. (b) `5` : la taille du changement ne change pas le numéro ;
    c'est donc dans la justification de la version 5 que vous dites que les
    réponses ne sont plus comparables. (c) L'appel lève une erreur : `5` est
    une version entière, et `ddi-l` n'en fait pas une version pointée, sauf si
    vous passez `allow_dotted=True`.

    ```python
    check = ddi.new_study(title="Version check", agency="example.org")
    question = check.add_question(text="Do you work from home?")
    question.version = "3"

    question.increment_version()
    print(question.version)  # -> 4

    question.increment_version()
    print(question.version)  # -> 5

    try:
        question.increment_minor_version()
    except ddi.DDIModelError:
        print("Refused")  # -> Refused
    ```

**Exercice 4 (O3).** De retour dans le document de l'exercice 2, récupérez
l'étude, donnez-lui sa version suivante avec `increment_version()`, ajoutez un
`VersionRationale` et définissez `version_responsibility`. Validez,
enregistrez sous `survey-v2.xml`, et affichez la version, la justification et
la responsabilité.

Résultat attendu :

```text
Version: 2
Rationale: Added sleep question; retired fax question
Responsibility: Survey Design Team
```

??? success "Réponse"
    ```python
    from ddi_l.models.base import VersionRationale

    study = doc.study_unit
    study.increment_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Added sleep question; retired fax question")
            ]
        )
    )
    study.version_responsibility = "Survey Design Team"

    errors = doc.validate()
    if errors:
        print("Errors:", errors)
    else:
        doc.save("survey-v2.xml")
        print(f"Version: {study.version}")  # -> Version: 2
        for r in study.version_rationales:
            for d in r.descriptions:
                print(f"Rationale: {d.text}")
        print(f"Responsibility: {study.version_responsibility}")
    ```

**Exercice 5 (O4).** Rouvrez `survey-v2.xml`. Changez le libellé de la
question sur la situation d'emploi, dans les deux langues, pour « What was
your main activity last week? » et « Quelle était votre activité principale
la semaine dernière ? ». Donnez à la question sa version suivante et une
justification. Faites pointer `EMPSTAT` vers la nouvelle version de la
question, vérifiez avec `doc.lint()`, et enregistrez le fichier sous
`survey-v3.xml`.

Résultat attendu :

```text
What was your main activity last week? (version 2)
Quelle était votre activité principale la semaine dernière ?
Lint errors: 0
```

??? success "Réponse"
    ```python
    doc = ddi.open_ddi("survey-v2.xml")

    status_q = next(
        q
        for q in doc.questions
        if q.question_texts[0].text == "What is your current employment status?"
    )
    for text in status_q.question_texts:
        if text.lang == "en":
            text.text = "What was your main activity last week?"
        if text.lang == "fr":
            text.text = "Quelle était votre activité principale la semaine dernière ?"

    status_q.increment_version()
    status_q.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Aligned wording with the ILO definition")
            ]
        )
    )

    # Repoint the variable that references the question
    for variable in doc.variables:
        variable.question_references = [
            status_q.to_reference() if ref.identifier == status_q.identifier else ref
            for ref in variable.question_references
        ]

    print(f"{status_q.question_texts[0].text} (version {status_q.version})")
    # -> What was your main activity last week? (version 2)
    print(status_q.question_texts[1].text)

    errors = [finding for finding in doc.lint() if finding.severity == "error"]
    print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
    doc.save("survey-v3.xml")
    ```

    Sautez une fois la boucle qui refait pointer la variable et lancez
    `doc.lint()` : il signale une erreur `ddi.reference.integrity` pour
    `EMPSTAT`.

**Exercice 6 (O5).** Dans le même document, codez `EMPSTAT` avec une liste à
trois valeurs (Employed, Unemployed, Not in labour force), comme dans le
fichier de l'an dernier. Faites-la ensuite passer à une liste à quatre
valeurs qui sépare « Not in labour force » en « Student » et « Retired ».
Donnez à la variable sa version suivante, notez pourquoi, et affichez le nom
de la liste de codes qu'elle utilise maintenant et sa version.

Résultat attendu :

```text
Status (4)
2
```

??? success "Réponse"
    ```python
    three_way = doc.add_code_list(name="Status (3)", label="Status (3)")
    add_codes(
        doc,
        three_way,
        [("1", "Employed"), ("2", "Unemployed"), ("3", "Not in labour force")],
    )
    four_way = doc.add_code_list(name="Status (4)", label="Status (4)")
    add_codes(
        doc,
        four_way,
        [("1", "Employed"), ("2", "Unemployed"), ("3", "Student"), ("4", "Retired")],
    )

    empstat = next(v for v in doc.variables if v.names[0].text == "EMPSTAT")
    empstat.set_coded(three_way)

    # The switch
    empstat.set_coded(four_way)
    empstat.increment_version()
    empstat.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Split 'Not in labour force' into Student and Retired"
                )
            ]
        )
    )

    reference = empstat.variable_representation.code_representation.code_list_reference
    print(doc.find(reference.identifier).names[0].text)  # -> Status (4)
    print(empstat.version)  # -> 2
    ```

    C'est la justification qui dit au lecteur que le code 3 de l'an dernier
    ne veut plus dire la même chose : la version dit seulement que la
    variable a changé.

---

## Quiz

???+ question "Question 1 (O1) : Vous avez ouvert survey-2023.xml et ajouté deux questions. Quelle ligne garde le fichier de l'an dernier inchangé ?"
    **A.** `doc.save("survey-2023.xml")`

    **B.** `doc.validate()`

    **C.** `doc.save("survey-2024.xml")`

    **D.** `ddi.open_ddi("survey-2024.xml")`

    ??? success "Réponse"
        **C.** Enregistrer sous un nouveau nom écrit la mise à jour dans un
        nouveau fichier et laisse `survey-2023.xml` tel quel. A écrase le
        fichier de l'an dernier. B vérifie mais n'enregistre rien ; D lit un
        fichier qui n'existe pas encore.

???+ question "Question 2 (O2) : Une question est à la version 3. Vous appelez increment_version(). Quelle est sa version maintenant ?"
    **A.** `3.1`

    **B.** `4`

    **C.** `3.0.1`

    **D.** `4.0`

    ??? success "Réponse"
        **B.** `increment_version()` donne le nombre entier suivant. A, C et D
        sont des versions pointées, que `ddi-l` ne crée jamais à partir d'un
        nombre entier, sauf si vous en demandez une.

???+ question "Question 3 (O2) : Une variable est à la version 1. Vous appelez increment_subversion() sans argument. Que se passe-t-il ?"
    **A.** Elle lève une erreur : utilisez `increment_version()` pour obtenir
    `2`, ou passez `allow_dotted=True` si votre organisation utilise des
    versions pointées.

    **B.** La version devient `1.0.1`.

    **C.** La version devient `2`.

    **D.** Rien : la version reste `1` et aucune erreur n'est levée.

    ??? success "Réponse"
        **A.** Un élément garde sa numérotation. Une version entière le reste,
        à moins de passer `allow_dotted=True`, car les outils qui numérotent
        les versions 1, 2, 3 risquent de ne pas lire une version pointée.

???+ question "Question 4 (O3) : Quel code consigne pourquoi la question q a changé et qui l'a changée ?"
    **A.** `q.labels.append(InternationalString(text="Reworded for 2024"))`

    **B.** `q.version_rationales.append(VersionRationale(descriptions=[InternationalString(text="Reworded for 2024")]))`,
    puis `q.version_responsibility = "Survey Design Team"`

    **C.** `q.set_property("why", "Reworded for 2024")`

    **D.** `doc.save("survey-2024.xml")`

    ??? success "Réponse"
        **B.** Un `VersionRationale` contient la raison, et
        `version_responsibility` nomme qui a fait le changement. A change
        l'étiquette ; C stocke un champ personnalisé qu'aucun outil DDI ne lit
        comme une justification.

???+ question "Question 5 (O4) : Vous avez reformulé une question et augmenté sa version. doc.lint() signale maintenant ddi.reference.integrity. Que corrigez-vous ?"
    **A.** Supprimer la variable et en créer une nouvelle.

    **B.** Annuler l'augmentation de version.

    **C.** Remplacer la référence de la variable par `question.to_reference()`,
    qui désigne la nouvelle version.

    **D.** Rien : `doc.validate()` passe, donc le fichier est correct.

    ??? success "Réponse"
        **C.** Une référence DDI désigne une version précise. Après
        l'augmentation, les `question_references` de la variable désignent
        encore l'ancienne ; remplacez-les par `question.to_reference()`.
        `doc.validate()` ne vérifie pas les références : c'est pourquoi D est
        faux.

???+ question "Question 6 (O5) : Comment faire passer une variable d'une liste de codes à une autre ?"
    **A.** Appeler `variable.set_coded(new_code_list)`.

    **B.** Renommer l'ancienne liste de codes.

    **C.** Ajouter les nouveaux codes à l'ancienne liste de codes.

    **D.** Appeler `doc.add_code_list()` avec le nom de la variable.

    ??? success "Réponse"
        **A.** `set_coded()` remplace la représentation de la variable par une
        représentation qui désigne la nouvelle liste de codes. Donnez ensuite
        à la variable sa version suivante, notez une justification, et
        retirez l'ancienne liste de codes si plus rien ne l'utilise.

???+ question "Question 7 (O5) : Les réponses d'une variable à la version 2 passent de Oui/Non à Tous les jours, Certains jours, Jamais. Que faites-vous ?"
    **A.** Rien : seules les étiquettes ont changé.

    **B.** La mettre à la version 2.1 : une catégorie a été ajoutée.

    **C.** Garder la version 2 et ajouter une justification.

    **D.** Lui donner la version 3, avec une justification qui dit que les
    réponses de l'an dernier ne se comparent pas directement à celles de cette
    année.

    ??? success "Réponse"
        **D.** De nouvelles catégories de réponse changent ce que la variable
        contient : elle reçoit donc sa version suivante. La version dit
        seulement qu'elle a changé ; la justification dit comment, et que les
        réponses ne sont plus comparables. B rend pointée une version entière ;
        C donne la même version à deux états différents de la variable.

---

## Pour aller plus loin (facultatif)

### Garder chaque référence à jour

La section 6 a refait pointer la seule variable qui renvoyait à la question.
Un fichier plus grand peut contenir d'autres références à un élément que vous
versionnez :

- **Un flux de questionnaire** (Module 10) : chaque `QuestionConstruct` qui
  pose une question contient une `question_reference`. Faites-la pointer de
  la même façon :

    ```python
    from ddi_l.models.datacollection import QuestionConstruct


    def repoint_constructs(doc, question):
        """Point every QuestionConstruct that asks `question` at its new version."""
        for construct in doc.items(QuestionConstruct):
            ref = construct.question_reference
            if ref is not None and ref.identifier == question.identifier:
                construct.question_reference = question.to_reference()
    ```

- **Les variables dérivées** (Module 11) renvoient à leurs sources dans
  `source_variable_references`.
- **Un schéma d'enregistrement** renvoie à chaque variable d'un fichier de
  données (ci-dessous).

Faites pointer chacune vers la nouvelle version avec `to_reference()`, ou
construisez-la après l'augmentation pour qu'elle pointe dès le départ vers la
nouvelle version. Lancez ensuite `doc.lint()` : chaque erreur
`ddi.reference.integrity` en désigne une que vous avez oubliée.

### Mettre à jour plusieurs variables à partir d'un nouveau fichier de données

Une nouvelle vague arrive généralement sous forme de **fichier de données**.
Les métadonnées doivent suivre : il faut décrire le nouveau fichier, et de
nombreuses variables ont besoin du même type de changement. En DDI, un fichier
de données est décrit par une **instance physique** (`PhysicalInstance`) : où
se trouve le fichier et combien d'enregistrements il contient.

Vous décrivez le nouveau fichier, puis vous parcourez les variables une seule
fois pour mettre chacune à jour à partir des données, en versionnant chaque
changement au fur et à mesure.

L'exemple utilise le fichier du Module 8 :

[:material-download: Télécharger `survey_sample.csv`](survey_sample.csv){ .md-button download="survey_sample.csv" }

Le document de l'an dernier décrit déjà les cinq mêmes colonnes, ainsi que le
fichier de données 2023. Le bloc ci-dessous le crée. Sautez-le si vous avez
votre propre fichier.

```python
import csv

from ddi_l.models.physical import PhysicalInstance

# Stand-in for last year's file
last_year = ddi.new_study(title="Income Survey 2023", agency="example.org")
for column in ("respondent_id", "age", "gender", "income", "education_level"):
    last_year.add_variable(name=column, label=column)
data_2023 = last_year.add_item(PhysicalInstance, name="Income Survey 2023 data")
data_2023.set_data_file("https://example.org/data/income-2023.csv")
data_2023.set_record_count(4800)
last_year.save("income-2023.xml")
```

**Étape 1 : Ouvrir le document et lire le nouveau fichier de données.**

```python
doc = ddi.open_ddi("income-2023.xml")

with open("survey_sample.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"{len(rows)} records")  # -> 5 records
```

**Étape 2 : Décrire le nouveau fichier.** Ajoutez une instance physique pour
le fichier 2024. Gardez celle de 2023 : elle décrit toujours correctement le
fichier de l'an dernier.

```python
data_2024 = doc.add_item(PhysicalInstance, name="Income Survey 2024 data")
data_2024.set_data_file("https://example.org/data/income-2024.csv")
data_2024.set_record_count(len(rows))
```

**Étape 3 : Noter les changements.** Rassemblez les changements au même
endroit avant de toucher à une variable. Ici, chaque variable reçoit un
libellé plus clair, deux reçoivent une plage numérique et deux reçoivent une
liste de codes :

```python
new_labels = {
    "respondent_id": "Respondent identifier",
    "age": "Age in years",
    "gender": "Gender",
    "income": "Annual income (CAD)",
    "education_level": "Highest level of education",
}
numeric_columns = {"age", "income"}
coded_columns = {"gender", "education_level"}
```

**Étape 4 : Mettre à jour toutes les variables en une seule boucle.** Pour
chaque variable, trouvez sa colonne dans le fichier de données, appliquez les
changements, puis versionnez-la. Les listes de codes utilisent la fonction
`add_codes()` de la section 6.

```python
for variable in doc.variables:
    column = variable.names[0].text
    values = [row[column] for row in rows if row[column] != ""]

    # A clearer label
    variable.labels = [InternationalString(text=new_labels[column], lang="en")]

    # What the variable holds, taken from the new file
    if column in numeric_columns:
        numbers = [int(value) for value in values]
        variable.set_numeric("Integer", low=min(numbers), high=max(numbers))
    elif column in coded_columns:
        code_list = doc.add_code_list(name=new_labels[column], label=new_labels[column])
        answers = sorted(set(values))
        add_codes(doc, code_list, [(str(n), a) for n, a in enumerate(answers, 1)])
        variable.set_coded(code_list)
    else:
        variable.set_text()

    # Version the change and say why
    variable.increment_version()
    variable.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Label and representation updated for 2024")
            ]
        )
    )
    variable.version_responsibility = "Data Processing Unit"

for variable in doc.variables:
    print(variable.names[0].text, variable.version)
```

```text
respondent_id 2
age 2
gender 2
income 2
education_level 2
```

Vous pouvez en vérifier une. La plage de `age` correspond maintenant aux âges
du nouveau fichier :

```python
age = next(v for v in doc.variables if v.names[0].text == "age")
age_range = age.variable_representation.numeric_representation.number_range
print(age_range.low, age_range.high)  # -> 22 51
```

**Étape 5 : Indiquer où se trouve chaque variable dans le nouveau fichier.**
Un **schéma d'enregistrement** (`RecordLayout`) liste les variables du fichier
de données. Construisez-le *après* les augmentations de version, pour qu'il
pointe vers les nouvelles versions. Un schéma construit avant la boucle
pointerait vers les anciennes. Liez ensuite le schéma au fichier 2024 :

```python
layout = doc.add_record_layout()
for variable in doc.variables:
    layout.add_data_item(variable.to_reference(), delimiter="comma")
data_2024.record_layout_references.append(layout.to_reference())
```

**Étape 6 : Vérifier et enregistrer.**

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
print(doc.validate())  # -> []

doc.save("income-2024.xml")
```

!!! tip "Une boucle, une justification par élément"
    Le modèle s'adapte à toutes les tailles. Que vous changiez cinq variables
    ou cinq cents, notez d'abord les changements (étape 3). Appliquez-les
    ensuite en une seule boucle qui modifie, versionne et explique chaque
    élément. Chaque variable modifiée reçoit sa propre version et sa propre
    justification, et l'historique reste lisible élément par élément.

---

## Faites le point

- [ ] Je peux ouvrir un fichier DDI, ajouter et retirer des éléments, et enregistrer le résultat sous un nouveau nom. (O1)
- [ ] Je peux donner sa version suivante à un élément modifié et prédire le numéro qu'il reçoit. (O2)
- [ ] Je peux consigner une justification et une responsabilité de version sur l'élément que j'ai modifié. (O3)
- [ ] Je peux reformuler une question dans toutes ses langues, la versionner, et faire pointer vers elle la variable qui y renvoie. (O4)
- [ ] Je peux faire passer une variable à une autre liste de codes, vérifier quelle liste elle utilise, et la versionner. (O5)

---

!!! tip "Notes pour l'instructeur"
    - **Module clé pour les archivistes et le personnel des instituts de
      statistique.** Le versionnement est intégré dans le standard DDI
      lui-même ; ce n'est pas quelque chose ajouté par-dessus. Chaque objet
      maintenable porte ses propres champs de version, justification et
      responsabilité.
    - **Montrez le XML avant/après.** Ouvrez `survey-v1.xml` et
      `survey-v2.xml` dans un éditeur de texte côte à côte. Montrez les
      éléments `<r:Version>` et `<r:VersionRationale>` pour que les
      apprenants voient ce que le code Python produit.
    - **Les méthodes de version sont sur `MaintainableBase`.** Tous les
      objets DDI (questions, variables, concepts, études, listes de codes)
      héritent de ces méthodes. Vous pouvez versionner n'importe quel
      élément, pas seulement l'étude de niveau supérieur.
    - **Des nombres entiers par défaut.** Les nouveaux éléments commencent à
      `1`, et `increment_version()` donne `2`. Les apprenants qui connaissent
      les versions de logiciels se tournent vers `increment_minor_version()` ;
      sur `"1"`, elle lève une erreur au lieu de produire `"1.1"`, car les
      outils qui numérotent les versions 1, 2, 3 risquent de ne pas lire une
      version pointée. La section 4 leur montre l'erreur.
    - **Des modifications, pas seulement des ajouts (sections 6 et 7).** La
      plupart des vraies mises à jour reformulent une question ou changent
      ses catégories de réponse. Insistez sur les quatre étapes : trouver
      l'élément, le modifier, le versionner avec une justification, faire
      pointer les références. Faites sauter la dernière étape une fois aux
      apprenants et exécuter `doc.lint()` pour qu'ils voient eux-mêmes
      l'erreur `ddi.reference.integrity`.
    - **Libellé ou sens.** Demandez si un changement de libellé garde les
      réponses comparables avec l'an dernier. La version augmente de un dans
      les deux cas ; la réponse va dans la justification. La même question
      s'applique à une nouvelle liste de codes.
    - **Mises à jour en bloc (Pour aller plus loin).** C'est le cas réaliste
      pour le personnel des instituts de statistique : le fichier de données
      d'une nouvelle vague arrive et des dizaines de variables ont besoin du
      même type de changement. Faites remarquer que l'étape 3 est un simple
      dictionnaire. Les apprenants peuvent le garder dans un tableur et le
      charger, pour que les spécialistes du domaine révisent les changements
      avant que quiconque exécute la boucle.
    - **Question de discussion :** Demandez aux apprenants comment leur
      organisation suit actuellement les changements aux instruments
      d'enquête. Comparez ce processus au versionnement DDI.
