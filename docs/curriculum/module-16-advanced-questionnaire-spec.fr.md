---
description: >-
  Module 16 du cours ddi-l : écrire une spécification de questionnaire,
  donner aux filtres et aux contrôles de saisie le sens voulu quand une
  réponse manque, et vérifier un instrument par rapport à la spécification.
---

# Module 16 : Spécification avancée de questionnaires

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Écrire une spécification YAML pour une courte enquête (modules,
      questions avec domaines de réponse, filtres et un contrôle de saisie)
      que `ddi spec validate` accepte sans erreur.
    - **O2.** Prédire si un filtre ou un contrôle de saisie est vrai quand
      une réponse manque, et écrire la condition qui correspond à une
      intention donnée.
    - **O3.** Réécrire en filtres les consignes « aller à » et « sinon »
      d'un document de spécification.
    - **O4.** Remplacer une paire de variables propres à chaque langue par
      une seule variable dont la liste de codes porte des étiquettes dans les
      deux langues.
    - **O5.** Lancer `ddi conform` sur un instrument, décider pour chaque
      constat si c'est la spécification ou l'instrument qui a tort, et
      dresser la liste des éléments qui demandent une nouvelle version.

**Prérequis :** [Module 7](module-07-cli-validation.fr.md),
[Module 10](module-10-questionnaire-flows.fr.md) et
[Module 15](module-15-update-and-version.fr.md). Installez l'extra spec :
`pip install "ddi-l[spec]"`.

**Durée :** 75 min en autonomie / 90 min avec instructeur.

**Nouveau dans ce module :** `ddi spec example`, `ddi spec validate`,
`ddi conform`, `example_spec()`, `load_spec()`, `parse_expression()`,
`normalise()`, `format_expression()`, `equivalent()`, `conform()`.

---

## 1. La spécification est la source

Au Module 10, vous avez traduit une spécification écrite de questionnaire en
**instrument** : le questionnaire en DDI, ses questions et le flux qui les
ordonne. Dans bien des équipes, la spécification tient en deux documents
tenus à la main à côté de l'instrument : un **document de spécification** qui
montre chaque page du questionnaire, et un **tableur** qui liste les
variables. Les documents et l'instrument divergent, et personne ne sait lequel
a raison.

Une **spécification de questionnaire** renverse la situation. C'est un petit
fichier en **YAML**, un format texte où l'indentation montre ce qui appartient
à quoi. Elle dit ce que l'instrument doit contenir, et rien de la mise en
page :

- ses **modules** : les sections du questionnaire, chacune une `Sequence`
  dans l'instrument ;
- ses **questions**, chacune avec un **domaine de réponse** (ou
  **domaine**) : le type de réponse qu'elle accepte, comme un code d'une
  liste, un nombre dans une plage, du texte ou une date ;
- ses **filtres** : des conditions qui décident si un module ou une question
  s'affiche ;
- ses **contrôles de saisie** : des règles qui testent une réponse et
  affichent un message quand elle semble fausse ;
- les variables qui viennent de l'extérieur de l'entrevue (**importées**,
  d'un fichier d'échantillon par exemple) ou qui sont calculées pendant
  celle-ci (**dérivées**).

ddi-l lit la spécification et y compare un instrument : la spécification reste
la référence, et chaque version de l'instrument est vérifiée par rapport à
elle.

ddi-l fournit une petite spécification pour une enquête fictive sur les
animaux de compagnie. En ligne de commande, `ddi spec example` l'écrit, et
`ddi spec validate` la vérifie par rapport au schéma des spécifications et
par rapport à elle-même (chaque identifiant apparaît une fois, chaque filtre
nomme une question ou une variable de la spécification, chaque minimum est
sous son maximum) :

```bash
ddi spec example > pet-survey.spec.yaml
ddi spec validate pet-survey.spec.yaml
```

```text
pet-survey.spec.yaml: the spec 'pet-survey' is valid: 3 module(s), 5 question(s), 1 edit(s).
```

Quand quelque chose ne va pas, chaque problème donne sa place dans le fichier
sous forme de chemin. Les positions comptent à partir de 0 :
`modules[1].questions[2]` est donc la troisième question du deuxième module :

```text
pet-survey.spec.yaml: modules[1].questions[2].gate: 'PetAgee' is not a question or variable of the spec
```

Ouvrez `pet-survey.spec.yaml`. Ses parties principales ressemblent à ceci :

```yaml
spec: pet-survey
version: "1"
languages: [en, fr]

code_lists:
  Species:
    values:
      1: {en: Dog, fr: Chien}
      2: {en: Cat, fr: Chat}
      3: {en: Bird, fr: Oiseau}

modules:
  - id: household
    questions:
      - id: PetCount
        domain: {numeric: {min: 0, max: 20, decimals: 0}}

  - id: pets
    gate: PetCount > 0
    statements: [PetsIntro]
    questions:
      - id: PetKind
        domain: {code: {list: Species}}
      - id: PetName
        domain: {text: {max_length: 50}}
        gate: answered(PetKind)
      - id: PetAge
        domain: {numeric: {min: 0, max: 40, decimals: 0}}

edits:
  - id: age_range
    when: PetAge > 30
    module: pets
    message:
      en: Is the pet really over 30?
      fr: L’animal a-t-il vraiment plus de 30 ans ?
    severity: warning
```

Le fichier complet contient aussi un troisième module, `visits`, et les
variables importées et dérivées. Vous pouvez aussi le lire depuis Python :

```python
from pathlib import Path

from ddi_l.spec import example_spec, load_spec

Path("pet-survey.spec.yaml").write_text(example_spec(), encoding="utf-8")
spec = load_spec("pet-survey.spec.yaml")
modules = [module.id for module in spec.modules]
print(spec.name, modules)  # -> pet-survey ['household', 'pets', 'visits']
```

Chaque module liste ses questions, chacune avec un domaine et, s'il y en a un,
un filtre :

```python
pets = spec.module("pets")
print(f"Gate: {pets.gate_text}")  # -> Gate: PetCount > 0
for question in pets.questions:
    kind, gate = question.domain.kind, question.gate_text or "-"
    print(question.id, kind, gate)  # -> PetName text answered(PetKind)
```

Où va chaque partie d'un document de spécification ou d'un tableur :

| Document de spécification ou tableur | Spécification |
| --- | --- |
| Une section, un groupe de pages | un module (`modules`) |
| Une question et ses cases de réponse | une question avec un `domain` |
| Une liste de catégories de réponse | `code_lists`, utilisée par un domaine `code` |
| « Poser si ... », une condition d'affichage | un `gate` sur le module ou la question |
| Une règle de vérification et son message | une entrée de `edits`, avec `when`, `message` et `severity` |
| Une valeur lue dans un fichier d'échantillon | `imported_variables` |
| Une valeur calculée pendant l'entrevue | `derived_variables` |
| Un texte inséré avec une copie de variable par langue | une seule variable, souvent un code (section 5) |

!!! tip "Deux choses à retenir"
    - La spécification dit ce que contient l'instrument, pas de quoi il a l'air.
    - Un filtre nomme les questions et les variables par leur identifiant, jamais par leur numéro. Les numéros changent quand une question bouge ; les identifiants, non.

## 2. Filtres, contrôles et réponses manquantes

Un filtre, ou le `when` d'un contrôle de saisie, est une expression : des
comparaisons jointes par `and`, `or` et `not`, avec cinq fonctions pour les
réponses absentes : `answered(x)`, `missing(x)`, `empty(x)` (sans réponse),
`refused(x)` et `today()`. La grammaire complète est dans
[Vérifier un questionnaire par rapport à une spécification](../spec-conformance.fr.md#filtres-et-controles-le-langage-dexpressions).

La règle qui compte le plus : **une comparaison est fausse quand la question n'a pas de réponse.** Les trois expressions ci-dessous ne sont donc pas pareilles :

| `PetAge` | `PetAge > 30` | `not PetAge > 30` | `PetAge <= 30` |
| --- | --- | --- | --- |
| 35 | vrai | faux | faux |
| 12 | faux | vrai | vrai |
| sans réponse | faux | **vrai** | faux |

`not PetAge > 30` montre une question à qui n'a jamais donné l'âge ;
`PetAge <= 30`, non. Aucune des deux n'est fausse. Choisissez celle que vous
voulez dire, et écrivez-la pour qu'un lecteur voie le choix :
`PetAge <= 30 or missing(PetAge)` dit à voix haute ce que `not PetAge > 30`
dit tout bas.

Il en va de même pour « différent de » : `PetKind != 1` est faux quand
`PetKind` n'a pas de réponse, et `not PetKind = 1` est vrai.

`missing(x)` vaut `empty(x) or refused(x)`, et `answered(x)` en est la
négation. À côté d'une comparaison de la même question, `answered(x)`
n'ajoute rien, puisque la comparaison exige déjà une réponse.

Pour comparer deux filtres, ddi-l réécrit d'abord chacun sous une forme
standard, sa **forme normale** : `missing(x)` est développé, `not` est
déplacé vers l'intérieur, les parties d'un `and` ou d'un `or` sont triées, et
un test de réponse qu'une comparaison implique déjà est retiré :

```python
from ddi_l.spec import equivalent, format_expression, normalise, parse_expression


def normal(text):
    return format_expression(normalise(parse_expression(text)))


print(normal("answered(PetAge) and PetAge > 30"))  # -> PetAge > 30
print(normal("missing(PetAge)"))  # -> empty(PetAge) or refused(PetAge)
print(equivalent("PetKind = 1 or PetKind = 2", "PetKind = 2 or PetKind = 1"))  # -> True
print(equivalent("PetAge > 30", "PetAge >= 31"))  # -> False
```

`equivalent()` compare d'abord des formes normales, et la normalisation ne
calcule rien. Sans l'extra `logic`, il ne fait rien de plus : `PetAge > 30` et
`PetAge >= 31` sont des filtres différents, même pour des nombres entiers.
Avec l'extra, il décide le reste : ils diffèrent encore quand `PetAge` peut
être une fraction, et concordent avec `types={"PetAge": "integer"}` ;
`ddi conform` le lit dans le domaine de la spécification.
`not PetAge > 30` et `PetAge <= 30 or missing(PetAge)` se ressemblent mais
diffèrent pour une réponse sans valeur à comparer, un « ne sait pas » : le
premier est vrai et le second faux. Choisissez une forme et utilisez-la à la
fois dans la spécification et dans l'instrument. Quand une vérification
signale deux filtres différents, lisez les deux avant de changer l'un ou
l'autre.

**Le `when` d'un contrôle de saisie est la condition d'erreur** : le contrôle
se déclenche quand il est vrai. Dans l'enquête sur les animaux, `age_range`
se déclenche quand `PetAge > 30`. Puisqu'une comparaison est fausse sans
réponse, un contrôle ne se déclenche jamais sur une question restée sans
réponse. Si la réponse manquante est elle-même l'erreur, dites-le avec
`missing(x)`.

## 3. De « aller à » et « sinon » aux filtres

Les documents de spécification acheminent par des sauts : « Si aucun animal,
aller à la section 3 ». Un instrument achemine par sa structure : un module ou
une question s'exécute quand son filtre est vrai. Pour traduire un saut,
demandez-vous ce qu'il saute, et filtrez cela :

| Document de spécification | Spécification |
| --- | --- |
| Q1 PetCount. Si 0, aller à la section 3. | module `pets`, `gate: PetCount > 0` |
| Q3 PetName. Poser si Q2 a une réponse. | question `PetName`, `gate: answered(PetKind)` |
| Si Q4 > 10, poser Q5, sinon Q6. | `Q5` : `gate: PetAge > 10` ; `Q6` : un filtre à choisir (ci-dessous) |

« Sinon » cache une décision. Q6 peut être `not PetAge > 10` (il s'affiche
aussi quand l'âge manque) ou `PetAge <= 10` (non). Écrivez celui dont
l'enquête a besoin, et vérifiez qu'ensemble les deux filtres couvrent chaque
cas voulu, sans qu'un cas soit dans les deux.

Écrivez le complément comme un second filtre plutôt que comme une branche
« sinon », à moins de savoir que votre outil exécute ces branches. Deux
filtres se lisent de la même façon dans tous les outils et dans la
spécification.

## 4. Contrôles de saisie

Un contrôle de saisie a besoin de quatre choses : un identifiant, la
condition d'erreur, un message dans chaque langue et une sévérité.

```yaml
edits:
  - id: age_range
    when: PetAge > 30
    module: pets
    message:
      en: Is the pet really over 30?
      fr: L’animal a-t-il vraiment plus de 30 ans ?
    severity: warning
```

```python
edit = spec.edits[0]
print(edit.id, edit.when_text, edit.severity)  # -> age_range PetAge > 30 warning
```

- Un **avertissement** (`warning`, contrôle souple) laisse le répondant
  confirmer et continuer ; une **erreur** (`error`, contrôle strict), non.
- N'écrivez pas de contrôle pour ce que le domaine impose déjà. `PetAge` a un
  maximum de 40 : un contrôle sur `PetAge > 40` ne se déclencherait jamais.
- Écrivez le message comme une question à laquelle le répondant peut
  répondre, dans les deux langues.

## 5. Bilingue dès la conception

Le DDI enregistre chaque texte une fois par langue (`xml:lang`). Une question
a son texte anglais et son texte français côte à côte ; un code a une
étiquette anglaise et une étiquette française.

Un **texte inséré** (aussi appelé insertion ou *fill*) est une valeur placée
dans le texte d'une question au moment où elle s'affiche, comme le genre
d'animal dans « Quel est le nom de votre chien ? ». Certaines équipes gardent
une copie de chaque variable insérée par langue, comme `RefMonth_en` et
`RefMonth_fr`. Les variables n'ont besoin d'aucun suffixe de langue :

- **Une valeur d'une liste fermée** (un mois, une espèce) est un code. Sa
  liste de codes porte les étiquettes dans les deux langues, et insérer
  `RefMonth` dans le texte d'une question affiche l'étiquette de la langue en
  cours. Une seule variable remplace `RefMonth_en` et `RefMonth_fr`. Vérifiez
  une fois que le texte inséré de votre outil affiche l'étiquette et non le
  code.
- **Une valeur sans mots** (une année, un montant, un nom) demande une seule
  variable et aucune étiquette.
- **Une forme qu'exige la grammaire d'une langue** (en français, *de janvier*
  mais *d'avril*) est une seconde liste de codes aux étiquettes dans cette
  langue, utilisée par le seul texte de cette langue.
- **Seul un texte libre qui diffère selon la langue** demande deux variables.

```yaml
code_lists:
  Month:
    values:
      1: {en: January, fr: janvier}
      2: {en: February, fr: février}
      # ... jusqu'à 12
derived_variables:
  - {name: RefMonth, type: code, values: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
```

Dans l'instrument, déclarez chaque variable insérée comme entrée de l'élément
dont le texte l'affiche, pour que le texte et sa valeur voyagent ensemble.
`ddi conform` signale un texte de question ou une étiquette de code qui manque
dans l'une des langues de la spécification (`spec.language.missing`).

## 6. Vérifier l'instrument par rapport à la spécification

`ddi conform` trouve dans un instrument chaque module, question et filtre de
la spécification et signale ce qui diffère. Pour le voir à l'œuvre, il vous
faut un instrument. Le bloc ci-dessous construit une ébauche de l'instrument
de l'enquête sur les animaux avec les constructions du Module 10, comme une
équipe de développement pourrait livrer une première version. Il contient
quelques problèmes, exprès.

`ddi conform` trouve une question par le nom de sa `QuestionConstruct`, et un
module par le nom de sa `Sequence` (parmi d'autres endroits que le bloc
`match` de la spécification peut changer) : chacun est donc nommé d'après son
identifiant dans la spécification.

```python
import ddi_l as ddi
from ddi_l.models.base import InternationalString
from ddi_l.models.datacollection import (
    IfThenElse,
    Instrument,
    QuestionConstruct,
    Sequence,
    StatementItem,
)

draft = ddi.new_study(title="Pet Survey", agency="example.org")


def ask(name, en, fr=None):
    """Add a question in English (and French) and the construct that asks it."""
    question = draft.add_question(text=en, label=name)
    if fr:
        question.question_texts.append(InternationalString(text=fr, lang="fr"))
    return draft.add_item(
        QuestionConstruct, name=name, question_reference=question.to_reference()
    )


count = ask("PetCount", "How many pets live here?", "Combien d'animaux vivent ici ?")
intro = draft.add_item(StatementItem, name="PetsIntro")
kind = ask("PetKind", "What kind of pet is it?", "Quelle sorte d'animal est-ce ?")
name = ask("PetName", "What is its name?", "Quel est son nom ?")
age = ask("PetAge", "How old is it?")
colour = ask("PetColour", "What colour is it?", "De quelle couleur est-il ?")

ask_name = draft.add_item(IfThenElse, name="Ask PetName")
ask_name.set_condition("answered(PetKind)")
ask_name.then_construct_reference = name.to_reference()

household = draft.add_item(
    Sequence, name="household", control_construct_references=[count.to_reference()]
)
pets = draft.add_item(
    Sequence,
    name="pets",
    control_construct_references=[
        intro.to_reference(),
        kind.to_reference(),
        ask_name.to_reference(),
        age.to_reference(),
        colour.to_reference(),
    ],
)
main = draft.add_item(
    Sequence,
    name="Pet survey",
    control_construct_references=[household.to_reference(), pets.to_reference()],
)
instrument = draft.add_item(Instrument, name="Pet survey instrument")
instrument.control_construct_reference = main.to_reference()

print(draft.validate())  # -> []
draft.save("pet-instrument.xml")
```

L'ébauche est du DDI valide. Comparez-la maintenant à la spécification.
`--module pets` ne compare que le module `pets`, ce qui garde la sortie
courte :

```bash
ddi conform pet-instrument.xml --spec pet-survey.spec.yaml --module pets --format table
```

```text
pet-survey: Instrument 0e8d208b (Pet survey instrument)
module  severity  rule                    item       message
------  --------  ----------------------  ---------  --------------------------------------------------------------------------------------------------
pets    error     spec.gate.missing       -          Module pets is not gated; the spec says PetCount > 0.
pets    error     spec.domain.type        PetKind    The question PetKind has no response domain; the spec says code.
pets    error     spec.domain.type        PetName    The question PetName has no response domain; the spec says text.
pets    warning   spec.gate.unverifiable  PetName    The gate of question PetName cannot be compared: it is python code.
pets    warning   spec.language.missing   PetAge     The question text of PetAge has no fr.
pets    error     spec.domain.type        PetAge     The question PetAge has no response domain; the spec says numeric.
pets    warning   spec.item.extra         PetColour  Module pets has the question QuestionConstruct 92df660e (PetColour), which the spec does not list.
pets    info      spec.edit.unverifiable  age_range  The edit age_range: not verifiable (edit storage unknown).
4 error(s), 3 warning(s), 1 info.
```

Les identifiants courts (`0e8d208b`, `92df660e`) sont le début
d'identifiants générés : les vôtres diffèrent. Chaque ligne est un
**constat** : le module, sa sévérité, la règle qui l'a trouvé, l'élément de
la spécification qu'il concerne, et un message. La dernière ligne les compte.
`ddi conform` se termine avec le code 1 quand il y a au moins une erreur, pour
qu'un script ou une tâche d'intégration continue puisse s'arrêter. La même
vérification depuis Python :

```python
from ddi_l.spec import conform

report = conform(ddi.read_ddi("pet-instrument.xml"), spec, module="pets")
print(report.summary)  # -> {'error': 4, 'warning': 3, 'info': 1}
```

Ce que veulent dire les règles de ce module (la liste complète est dans
[Vérifier un questionnaire par rapport à une spécification](../spec-conformance.fr.md#regles)) :

| Règle | Sévérité | Ce qu'elle veut dire |
| --- | --- | --- |
| `spec.gate.missing` | erreur | La spécification filtre ce que l'instrument montre à tous. |
| `spec.gate.different` | erreur | Les filtres diffèrent ; les deux formes normales sont affichées. |
| `spec.domain.type` | erreur | Le domaine de réponse est d'un autre type, ou manque. |
| `spec.language.missing` | avertissement | Un texte ou une étiquette manque dans l'une des langues de la spécification. |
| `spec.item.extra` | avertissement | L'instrument a une question que la spécification ne liste pas à cet endroit. |
| `spec.gate.unverifiable` | avertissement | Le filtre enregistré ne peut pas être relu. Vérifiez-le à la main. |
| `spec.edit.unverifiable` | information | On ne sait pas où l'instrument enregistre ses contrôles. Vérifiez-les à la main. |

Les erreurs sont des différences à résoudre ; les avertissements et les
informations disent ce qui est en trop ou ce qui n'a pas été comparé. Une
vérification propre, c'est 0 erreur, pas 0 constat.

L'ébauche enregistre son filtre en texte simple, défini avec
`set_condition()` au Module 10. `ddi conform` lit les filtres sous les formes
qu'enregistrent les outils de questionnaire ; il ne peut pas relire celui-ci,
et le dit par un avertissement plutôt que de deviner.

**La spécification ou l'instrument ?** Pour chaque erreur, demandez-vous
lequel des deux dit ce dont l'enquête a besoin. La spécification est la
référence : c'est donc d'habitude l'instrument qu'il faut corriger. Mais une
spécification peut aussi se tromper : une question ajoutée exprès que
personne n'a écrite dans la spécification, ou une borne mal saisie. Corrigez
alors la spécification, donnez-lui une nouvelle `version`, et relancez la
vérification.

## 7. Versionner la modification

Une référence DDI désigne une version précise d'un élément (Module 15). Quand
vous corrigez un élément, il reçoit une nouvelle version : chaque élément qui
y renvoie doit donc être révisé pour pointer vers la nouvelle version, et
ainsi de suite jusqu'à l'instrument. Les éléments qui ne renvoient à rien de
ce que vous avez changé gardent leur version. Un nouvel élément, comme un
nouveau filtre, commence à sa première version, et l'élément qui y renvoie
désormais est révisé.

Par exemple, corriger la condition de `Ask PetName` modifie ce
`IfThenElse`. La séquence `pets` y renvoie : elle est révisée ; la séquence
principale renvoie à `pets`, et l'instrument à la séquence principale : les
deux sont révisés aussi. La séquence `household` et les questions gardent
leur version.

Faites de toute la correction une seule diffusion : une date (`versionDate`)
et une responsabilité (la personne qui l'a faite) pour chaque élément nouveau
ou révisé, comme au [Module 15](module-15-update-and-version.fr.md). Relancez
ensuite `ddi conform` sur la nouvelle version, et gardez sa sortie avec la
diffusion.

## 8. Liste de vérification de la spécification

- [ ] Chaque module et chaque question a un identifiant qui ne dépend pas de son numéro.
- [ ] Chaque question a un domaine, avec des bornes là où la réponse en a.
- [ ] Chaque « aller à » est un filtre sur ce qu'il saute ; chaque « sinon » est un second filtre.
- [ ] Pour chaque filtre, vous avez décidé ce qui arrive quand une réponse manque.
- [ ] Le `when` de chaque contrôle est l'erreur, son message est dans chaque langue, sa sévérité est fixée.
- [ ] Aucune variable n'a de suffixe de langue.
- [ ] `ddi spec validate` passe, et `ddi conform` signale 0 erreur.
- [ ] Une copie de la spécification avec un filtre ou une borne changé donne exactement une nouvelle erreur.

---

!!! example "Scénario"
    L'équipe de l'enquête sur les animaux vous envoie un document de
    spécification et un tableur de variables. La section 1 dit : « Q1
    Combien d'animaux vivent ici ? (0 à 20). Si 0, aller à la section 3. » La
    section 2 dit : « Q2 Quelle sorte d'animal est-ce ? (Chien, Chat,
    Oiseau). Q3 Quel est son nom ? (texte, jusqu'à 50 caractères ; poser si
    Q2 a une réponse). Q4 Quel âge a-t-il ? (0 à 40 ans). Si Q4 > 10, poser
    Q5 (visites chez le vétérinaire l'an dernier, 0 à 50), sinon poser Q6
    (nombre de jouets, 0 à 99). » La section 3 dit : « Q7 Quand êtes-vous
    allé chez le vétérinaire pour la dernière fois ? (une date). » Le tableur
    liste `KindText_en` et `KindText_fr` pour la sorte d'animal insérée dans
    le texte de Q3, et un contrôle : « Q4 plus de 30 : veuillez confirmer. »

    Votre tâche : décider ce que chaque filtre fait d'une réponse manquante,
    écrire la spécification, et y comparer un instrument.

---

## Exercices

1. **(O2)** Écrivez les filtres de Q5 et de Q6 du scénario. Q6 doit s'afficher quand l'âge manque. Vérifiez leurs formes normales. Prédisez ensuite si le contrôle du scénario, `when: PetAge > 30`, se déclenche pour un animal de 35 ans, un animal de 12 ans, et un animal sans âge.

    **Résultat attendu :**

    ```text
    PetAge > 10
    not PetAge > 10
    ```

    ??? success "Réponse"
        Q5 est `PetAge > 10`. Q6 s'affiche quand Q5 ne s'affiche pas, y compris quand l'âge manque : c'est donc `not PetAge > 10` (ou, pour le dire à voix haute, `PetAge <= 10 or missing(PetAge)` ; choisissez une forme et gardez-la).

        ```python
        print(normal("PetAge > 10"))  # -> PetAge > 10
        print(normal("not PetAge > 10"))  # -> not PetAge > 10
        ```

        Si Q6 avait été `PetAge <= 10`, un répondant sans âge n'aurait vu ni Q5 ni Q6.

        Le contrôle ne se déclenche que pour 35. Pour 12, la comparaison est fausse, et pour un âge manquant, une comparaison est toujours fausse. Pour signaler un âge manquant, il faudrait un second contrôle avec `when: missing(PetAge)`.

2. **(O3)** Le document de spécification d'une enquête sur le logement dit : « H1 Êtes-vous propriétaire de votre logement ? (1 Oui, 2 Non). Si Non, aller à H4. H2 Il y a combien d'années l'avez-vous acheté ? H3 Avez-vous un prêt hypothécaire ? H4 Combien de pièces y a-t-il ? » Les identifiants des questions sont `Own`, `YearsOwned`, `Mortgage` et `Rooms`. (a) Écrivez le filtre de H2 et H3 qui fait exactement ce que dit le saut, y compris quand H1 n'a pas de réponse. (b) Le responsable de l'enquête dit que H2 et H3 ne sont que pour les propriétaires. Écrivez ce filtre. Vérifiez les deux avec `normal()`.

    **Résultat attendu :**

    ```text
    not Own = 2
    Own = 1
    ```

    ??? success "Réponse"
        (a) Le saut ne se fait que sur « Non ». Un répondant qui n'a pas répondu à H1 ne saute pas : il voit H2 et H3. Le filtre est `not Own = 2`. (b) Propriétaires seulement : `Own = 1`. Les deux ne diffèrent que quand H1 n'a pas de réponse : écrivez celui que l'enquête veut dire. H4 n'a pas de filtre : tout le monde la voit.

        ```python
        print(normal("not Own = 2"))  # -> not Own = 2
        print(normal("Own = 1"))  # -> Own = 1
        ```

3. **(O4)** Remplacez `KindText_en` et `KindText_fr` par une seule variable, et écrivez le YAML de la liste de codes qu'elle utilise.

    ??? success "Réponse"
        La sorte d'animal vient d'une liste fermée : c'est un code, la question `PetKind` elle-même, avec la liste de codes `Species`, dont les étiquettes sont en anglais et en français. Le texte anglais de Q3 insère `PetKind`, son texte français aussi ; chacun affiche l'étiquette de sa langue (vérifiez une fois que le texte inséré de votre outil affiche les étiquettes). Aucune variable dérivée n'est nécessaire, puisque la réponse est déjà la valeur.

        ```yaml
        code_lists:
          Species:
            values:
              1: {en: Dog, fr: Chien}
              2: {en: Cat, fr: Chat}
              3: {en: Bird, fr: Oiseau}
        ```

4. **(O1)** Écrivez `my-pets.spec.yaml` pour le scénario : trois modules (`household`, `pets`, `visits`), les sept questions avec leurs domaines, les filtres du module `pets`, de Q3 et de l'exercice 1, et le contrôle comme contrôle souple. Nommez les questions `PetCount`, `PetKind`, `PetName`, `PetAge`, `VetVisits`, `Toys` et `LastVisit`. Lancez `ddi spec validate my-pets.spec.yaml`.

    **Résultat attendu :**

    ```text
    my-pets.spec.yaml: the spec 'my-pets' is valid: 3 module(s), 7 question(s), 1 edit(s).
    ```

    ??? success "Réponse"
        ```yaml
        spec: my-pets
        version: "1"
        languages: [en, fr]

        code_lists:
          Species:
            values:
              1: {en: Dog, fr: Chien}
              2: {en: Cat, fr: Chat}
              3: {en: Bird, fr: Oiseau}

        modules:
          - id: household
            questions:
              - id: PetCount
                domain: {numeric: {min: 0, max: 20, decimals: 0}}

          - id: pets
            gate: PetCount > 0
            questions:
              - id: PetKind
                domain: {code: {list: Species}}
              - id: PetName
                domain: {text: {max_length: 50}}
                gate: answered(PetKind)
              - id: PetAge
                domain: {numeric: {min: 0, max: 40, decimals: 0}}
              - id: VetVisits
                domain: {numeric: {min: 0, max: 50, decimals: 0}}
                gate: PetAge > 10
              - id: Toys
                domain: {numeric: {min: 0, max: 99, decimals: 0}}
                gate: not PetAge > 10

          - id: visits
            questions:
              - id: LastVisit
                domain: {date: {type: Date}}

        edits:
          - id: age_over_30
            when: PetAge > 30
            module: pets
            message:
              en: Is the pet really over 30?
              fr: L’animal a-t-il vraiment plus de 30 ans ?
            severity: warning
        ```

        « Si 0, aller à la section 3 » devient le filtre du module qu'il saute, `pets`. Si `ddi spec validate` signale un problème, son chemin dit où : `modules[1].questions[2]` est la troisième question du deuxième module.

5. **(O5)** Construisez l'ébauche d'instrument de la section 6 si ce n'est pas fait, et lancez `ddi conform pet-instrument.xml --spec pet-survey.spec.yaml --module pets --format table`. Pour chaque constat, dites si c'est la spécification ou l'instrument qui a tort, et ce qu'il faut changer. Le responsable de l'enquête vous dit que `PetColour` a été ajoutée exprès cette vague. Dressez ensuite la liste des éléments qui reçoivent une nouvelle version quand vous ajoutez le texte français de PetAge et le filtre du module.

    **Résultat attendu :** le tableau de la section 6, qui se termine par :

    ```text
    4 error(s), 3 warning(s), 1 info.
    ```

    ??? success "Réponse"
        | Constat | Qui a tort | Que changer |
        | --- | --- | --- |
        | `spec.gate.missing` (module `pets`) | l'instrument | N'afficher `pets` que si `PetCount > 0` : l'envelopper dans un `IfThenElse` avec cette condition. |
        | `spec.domain.type` (PetKind, PetName, PetAge) | l'instrument | Les questions de l'ébauche n'ont pas de domaine de réponse. Donner à PetKind les codes `Species`, à PetName un texte de 50 caractères au plus, à PetAge un nombre de 0 à 40. |
        | `spec.gate.unverifiable` (PetName) | aucun | Vérifier à la main : la condition de l'ébauche est `answered(PetKind)`, le filtre de la spécification. Rien à changer. |
        | `spec.language.missing` (PetAge) | l'instrument | Ajouter le texte français de la question. |
        | `spec.item.extra` (PetColour) | la spécification | Elle a été ajoutée exprès : ajouter `PetColour` et son domaine au module `pets` de la spécification, et donner à la spécification une nouvelle `version`. |
        | `spec.edit.unverifiable` (age_range) | aucun | Non comparé. Vérifier le contrôle dans l'instrument à la main. |

        Éléments qui reçoivent une nouvelle version après les deux corrections : la question de PetAge (nouveau texte) ; la construction de PetAge, qui y renvoie ; la séquence `pets`, qui renvoie à la construction ; le nouvel `IfThenElse` du filtre du module, à sa première version ; la séquence principale, qui renvoie maintenant à cet `IfThenElse` au lieu de `pets` ; et l'instrument. La séquence `household`, les autres questions et constructions, et `Ask PetName` gardent leur version. Tous les éléments nouveaux et révisés partagent un seul `versionDate` et une seule responsabilité.

6. **(O2, O5)** Pour un instrument dont il sait lire les filtres, `ddi conform` signale : `spec.gate.different  Toys  Question Toys is gated by PetAge <= 10; the spec says not PetAge > 10.` Lequel a raison, et que changez-vous ?

    ??? success "Réponse"
        Le scénario dit que Q6 s'affiche quand Q5 ne s'affiche pas : un âge manquant doit donc afficher Q6, et la spécification (`not PetAge > 10`) a raison. Changez le filtre de l'instrument. Les deux filtres ne diffèrent que pour un âge manquant, et c'est pourquoi `equivalent()` et `ddi conform` les traitent comme différents.

---

## Quiz

???+ question "Question 1 (O2) : PetAge n'a pas de réponse. Quel filtre est vrai ?"
    **A.** `PetAge > 30`

    **B.** `PetAge <= 30`

    **C.** `not PetAge > 30`

    **D.** `PetAge != 30`

    ??? success "Réponse"
        **C.** Une comparaison est fausse sans réponse : A, B et D sont
        fausses, et `not` fait du faux de A un vrai.

???+ question "Question 2 (O2) : Un contrôle a when: PetAge > 30. Un répondant saute PetAge. Le contrôle se déclenche-t-il ?"
    **A.** Oui : une réponse manquante est une erreur.

    **B.** Non : une comparaison est fausse sans réponse. Pour signaler un
    âge manquant, écrivez un contrôle avec `when: missing(PetAge)`.

    **C.** Seulement si sa sévérité est `error`.

    **D.** Seulement dans la version française.

    ??? success "Réponse"
        **B.** Le contrôle se déclenche quand `when` est vrai, et
        `PetAge > 30` est faux quand il n'y a pas de réponse.

???+ question "Question 3 (O3) : Le document dit : si Q4 > 10, poser Q5, sinon Q6. Un répondant sans âge doit voir Q6. Quel filtre écrivez-vous pour Q6 ?"
    **A.** `PetAge <= 10`

    **B.** Aucun : une branche « sinon » suffit.

    **C.** `PetAge < 10`

    **D.** `not PetAge > 10`

    ??? success "Réponse"
        **D.** `not PetAge > 10` est vrai quand `PetAge > 10` est faux, y
        compris quand l'âge manque. A et C sont faux pour un âge manquant (et
        C cache aussi Q6 à un animal d'exactement 10 ans). Un second filtre
        se lit de la même façon dans tous les outils, ce qui n'est pas le cas
        d'une branche « sinon ».

???+ question "Question 4 (O4) : Pourquoi un mois n'a-t-il pas besoin de copies de sa variable propres à chaque langue ?"
    **A.** L'étiquette d'un code est enregistrée dans chaque langue, et le
    texte inséré affiche l'étiquette de la langue en cours.

    **B.** Les mois sont des nombres.

    **C.** Le français n'a pas de noms de mois.

    **D.** Le fichier de données contient les deux.

    ??? success "Réponse"
        **A.** Un code, deux étiquettes, une variable.

???+ question "Question 5 (O1) : ddi spec validate affiche ceci. Que corrigez-vous ?"
    ```text
    my.spec.yaml: modules[0].questions[1].domain.numeric: min is greater than max
    ```

    **A.** Le nom du premier module.

    **B.** Les bornes de la deuxième question du premier module.

    **C.** Le filtre de la première question.

    **D.** Rien : c'est un avertissement.

    ??? success "Réponse"
        **B.** Les positions comptent à partir de 0 : `modules[0].questions[1]`
        est la deuxième question du premier module, et son `min` numérique
        dépasse son `max`. `ddi spec validate` signale des problèmes, pas des
        avertissements : la spécification ne se charge pas tant que vous ne
        l'avez pas corrigée.

???+ question "Question 6 (O5) : ddi conform signale 0 erreur et 12 avertissements. L'instrument est-il juste ?"
    **A.** Non : les avertissements sont des erreurs.

    **B.** Seulement si les avertissements tombent à 0.

    **C.** Impossible à dire.

    **D.** Oui, pour autant que la spécification le dise ; les
    avertissements disent ce qui est en trop ou n'a pas été comparé.

    ??? success "Réponse"
        **D.** Lisez les avertissements : un module commun couvert par une
        autre spécification en est un cas typique, et un filtre non
        vérifiable demande une vérification à la main. Pour être sûr que la
        vérification fonctionne, changez un filtre dans une copie de la
        spécification et attendez-vous à exactement une nouvelle erreur.

???+ question "Question 7 (O5) : ddi conform signale spec.item.extra pour PetColour, que le responsable de l'enquête a ajoutée exprès. Que changez-vous ?"
    **A.** Retirer `PetColour` de l'instrument.

    **B.** Rien : on peut ignorer les avertissements.

    **C.** Ajouter `PetColour` à la spécification et donner une nouvelle
    version à la spécification.

    **D.** Renommer `PetColour` pour qu'elle ne soit pas trouvée.

    ??? success "Réponse"
        **C.** Ici, c'est la spécification qui a tort : elle ne liste pas une
        question dont l'enquête a besoin. Corrigez la référence, versionnez-la,
        et relancez la vérification.

???+ question "Question 8 (O5) : Vous corrigez la condition de l'IfThenElse qui filtre PetName, dans la séquence pets. Quels éléments reçoivent une nouvelle version ?"
    **A.** L'`IfThenElse`, la séquence `pets`, la séquence principale et
    l'instrument.

    **B.** Seulement l'`IfThenElse`.

    **C.** Tous les éléments de l'instrument.

    **D.** Seulement l'instrument.

    ??? success "Réponse"
        **A.** L'élément modifié et chaque élément qui y renvoie, jusqu'à
        l'instrument. Les éléments qui ne renvoient à rien de ce que vous
        avez changé, comme la séquence `household`, gardent leur version.

---

## Pour aller plus loin (facultatif)

### Quand votre outil ne sait pas le dire

Un outil de questionnaire enregistre chaque filtre sous une forme qu'il sait
exécuter. Beaucoup ont un éditeur de conditions doté d'un jeu fixe
d'opérateurs, et se rabattent sur du code dans un langage de script pour tout
le reste. Un filtre que l'éditeur contient reste modifiable par les
rédacteurs ; un filtre en code demande un programmeur pour le changer.
Écrivez donc des filtres que l'éditeur peut contenir, tant que le sens reste
exactement le même.

Partez des opérateurs qu'énumère la documentation de l'outil. Un opérateur
qu'elle énumère s'emploie comme elle le décrit ; un opérateur que vous n'avez
vu que dans un fichier exporté est une supposition. La documentation peut
aussi être incomplète : elle peut nommer un opérateur sans dire ce qu'il fait
d'une réponse manquante, et un filtre qui en dépend se vérifie alors dans un
aperçu.

Supposons que l'éditeur de votre outil offre `=`, `>`, « est vide », « est
refusé » et « l'un de » pour une question codée, joints par `and` ou `or`, et
rien d'autre. Trois réécritures gardent exactement le sens et permettent à
plus de filtres d'y tenir :

1. **Retirer un test de réponse qu'une comparaison implique déjà.**
   `answered(PetAge) and PetAge > 30` demande « n'est pas vide », que
   l'éditeur n'a pas. Sa forme normale (section 2) est `PetAge > 30`, qui y
   tient.
2. **Lire un choix parmi les codes d'une question comme un seul « l'un
   de ».** Dans `PetCount > 1 and (PetKind = 1 or PetKind = 2)`, la partie
   entre parenthèses est « PetKind est l'un de 1, 2 » : une seule condition,
   jointe à l'autre par `and`.
3. **Utiliser un ensemble de valeurs que la spécification déclare.**
   `HasPets` est déclarée avec les valeurs 0 et 1, donc `HasPets != 1` vaut
   `HasPets = 0`. Les expressions seules ne permettent pas de le savoir :

    ```python
    print(equivalent("HasPets != 1", "HasPets = 0"))  # -> False
    print(spec.derived_variables[0].values)  # -> ('0', '1')
    ```

    Les valeurs viennent de la spécification : la réécriture vous revient.
    Notez à côté du filtre d'où viennent les valeurs, pour que la personne
    qui les changera sache qu'il faut changer le filtre aussi.

Tout le reste reste dans le code de l'outil, et c'est très bien : c'est
exact. Ce qu'il ne faut jamais faire, c'est deviner une partie non documentée
du format d'un outil, un numéro d'opérateur par exemple, pour forcer un
filtre dans l'éditeur. Une supposition fausse donne un mauvais filtre qui a
l'air juste. Si une lacune compte, signalez-la au fabricant de l'outil avec
un exemple fictif, et gardez le code jusqu'à la réponse.

**Exercice facultatif.** L'éditeur de votre outil offre ce que suppose le
paragraphe ci-dessus. Lesquelles de ces conditions peut-il contenir, après une
réécriture exacte quand il en existe une ? `PetCount > 2`,
`PetKind = 1 or PetKind = 3`, `answered(PetName)`, `PetCount < 2`,
`answered(PetCount) and PetCount > 2`.

??? note "Réponse"
    - `PetCount > 2` : oui, telle quelle.
    - `PetKind = 1 or PetKind = 3` : oui, comme « PetKind est l'un de 1, 3 ».
    - `answered(PetName)` : non. C'est « ni vide ni refusé », et l'éditeur
      n'a pas de « non ». Elle reste en code.
    - `PetCount < 2` : oui, après réécriture. La spécification déclare
      PetCount comme un nombre entier à partir de 0 : `PetCount < 2` vaut
      `PetCount = 0 or PetCount = 1`.
    - `answered(PetCount) and PetCount > 2` : oui. Sa forme normale retire le
      test de réponse.

    ```python
    domain = spec.module("household").questions[0].domain
    print(domain.minimum, domain.maximum, domain.decimals)  # -> 0 20 0
    print(normal("answered(PetCount) and PetCount > 2"))  # -> PetCount > 2
    ```

---

## Faites le point

- [ ] Je peux écrire une spécification YAML pour une courte enquête que `ddi spec validate` accepte sans erreur. (O1)
- [ ] Je peux prédire si un filtre ou un contrôle de saisie est vrai quand une réponse manque, et écrire la condition que je veux dire. (O2)
- [ ] Je peux réécrire en filtres les consignes « aller à » et « sinon ». (O3)
- [ ] Je peux remplacer les copies d'une variable propres à chaque langue par une seule variable dont la liste de codes a des étiquettes dans les deux langues. (O4)
- [ ] Je peux lancer `ddi conform`, décider pour chaque constat si c'est la spécification ou l'instrument qui a tort, et dresser la liste des éléments qui demandent une nouvelle version. (O5)

---

!!! tip "Notes pour l'instructeur"
    - Commencez par la table des réponses manquantes de la section 2 au tableau. Demandez au groupe de remplir la dernière ligne avant de la montrer ; la plupart se trompent sur `not PetAge > 30`.
    - Apportez une vraie page de document de spécification si vous en avez une, avec ses sauts et ses « sinon ». La traduire ensemble en filtres est le meilleur exercice du module.
    - Avant que les apprenants lancent `ddi conform` à la section 6, demandez-leur de prédire les constats à partir du code de l'ébauche. Les problèmes y sont exprès : pas de filtre de module, pas de domaines de réponse, pas de texte français pour PetAge, une question en trop.
    - Les personnes habituées aux tableurs demandent une variable par langue par habitude. Montrez la liste de codes à deux étiquettes et le texte inséré dans les deux langues.
    - La section 7 applique le Module 15 ; si les apprenants sortent de ce module, allez vite.
    - La section Pour aller plus loin est le point où la connaissance de l'outil rejoint la rédaction de la spécification. Insistez : un filtre gardé dans le code propre à l'outil est une bonne réponse, et deviner un format non documenté est la seule chose à ne jamais faire.

---

**Voir aussi :** [Module 10 : Flux de questionnaire](module-10-questionnaire-flows.fr.md) | [Vérifier un questionnaire par rapport à une spécification](../spec-conformance.fr.md)
