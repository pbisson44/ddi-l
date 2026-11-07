---
description: >-
  Décrire dans une spécification YAML ou JSON ce qu'un questionnaire doit
  contenir, puis y comparer un instrument avec ddi conform : modules,
  questions, codes, domaines, filtres et contrôles.
---

# Vérifier un questionnaire par rapport à une spécification

Une spécification dit ce qu'un questionnaire doit contenir : ses modules, les
questions et les énoncés de chacun, leurs domaines de réponse et listes de
codes, les filtres qui décident qui voit quoi, et les contrôles de saisie.
`ddi conform` y compare un instrument et signale chaque écart, avec un
identifiant de règle, une sévérité, et le module et l'élément en cause.

La spécification est un fichier YAML ou JSON que vous écrivez, ou que vous
produisez à partir de vos propres documents de conception. `ddi-l` ne lit
rien d'autre : passer des documents de votre organisation à une
spécification vous appartient.

Lire une spécification demande l'extra `spec` :

```bash
pip install 'ddi-l[spec]'
```

Sans lui, `ddi spec` et `ddi conform` affichent cette ligne et se terminent
avec le code 1. Le langage d'expressions et ses compilateurs n'ont besoin que
de la bibliothèque standard.

## Écrire une spécification

`ddi spec example` écrit l'exemple, la spécification de l'enquête fictive sur
les animaux de compagnie ; `ddi spec schema` écrit le schéma JSON auquel
une spécification est comparée, pour un éditeur qui complète et vérifie le
YAML.

```bash
ddi spec example > pet-survey.spec.yaml
ddi spec validate pet-survey.spec.yaml
```

L'exemple au complet :

```yaml
spec: pet-survey
version: "1"
description: A small bilingual survey about the pets of a household.
languages: [en, fr]

# The words of your Blaise version, for gates that compile to Blaise.
# ddi-l assumes none of them.
blaise:
  empty: EMPTY
  refused: REFUSAL
  today: SYSDATE

code_lists:
  Species:
    values:
      1: {en: Dog, fr: Chien}
      2: {en: Cat, fr: Chat}
      3: {en: Bird, fr: Oiseau}

imported_variables:
  - {name: OwnerName, type: text, source: register}
derived_variables:
  - {name: HasPets, type: numeric, values: [0, 1]}

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

  - id: visits
    required: false
    questions:
      - id: VisitDate
        domain: {date: {type: Date}}

edits:
  - id: age_range
    when: PetAge > 30
    module: pets
    message:
      en: Is the pet really over 30?
      fr: L’animal a-t-il vraiment plus de 30 ans ?
    severity: warning
```

Les parties :

| Clé | Ce qu'elle contient |
| --- | --- |
| `spec`, `version`, `description` | Le nom de la spécification, et votre propre version et vos notes. |
| `instrument` | L'instrument à vérifier quand le fichier en a plusieurs : son nom, son libellé, son identifiant d'utilisateur ou son ID. |
| `languages` | Les langues de tout texte de question et de tout libellé de code (`en` correspond à `en-CA`). Un libellé écrit sans langue est dans la première. |
| `blaise` | Les mots Blaise pour vide, refus, aujourd'hui et les dates, pour les filtres en code Blaise. |
| `match` | Où trouver chaque identifiant dans l'instrument (plus bas). |
| `severities` | Une sévérité pour une règle, à la place de celle par défaut : `{spec.module.extra: error}`. |
| `code_lists` | Les listes de codes qu'une question nomme avec `list:`. |
| `imported_variables`, `derived_variables` | Les variables qu'une recherche de données fournit, et celles que l'instrument calcule. |
| `modules` | Chaque module : son `id`, s'il est requis (`required`, `true` par défaut), son filtre (`gate`) et sa portée (`gate_scope` : `module` par défaut, ou `page`), ses énoncés (`statements`) et ses questions (`questions`). |
| `edits` | Chaque contrôle de saisie : son `id`, la condition qui le déclenche (`when`), son `module`, son message (`message`) et sa sévérité (`severity`). |

Une question a un `id`, un domaine (`domain`) et un filtre (`gate`) à elle,
qui s'ajoute à celui de son module. Un domaine est l'un de :

| Domaine | Options |
| --- | --- |
| `code` | `values` (chaque valeur et son libellé), ou `list` (une entrée de `code_lists`). |
| `numeric` | `min`, `max`, `min_inclusive` et `max_inclusive` (`true` par défaut), `decimals`. |
| `text` | `min_length`, `max_length`. |
| `date` | `type` : le `DateTypeCode` DDI (`Date`, `DateTime`, `Year`...). |

`ddi spec validate` vérifie une spécification par rapport au schéma, puis par
rapport à elle-même : chaque identifiant n'apparaît qu'une fois, chaque
`list:` nomme une liste de codes, chaque filtre et contrôle s'analyse et ne
nomme que des questions et variables de la spécification, `min` est sous
`max`, les libellés sont dans les langues de la spécification, et
`severities` nomme de vraies règles. Chaque problème dit où il se trouve :

```text
pet-survey.spec.yaml: modules[1].questions[2].gate: 'PetAgee' is not a question or variable of the spec
```

Le YAML est lu strictement, comme du YAML 1.2. Une clé donnée deux fois est
une erreur, tout comme une clé de fusion (`<<`) ; `01` reste la chaîne
`"01"`, un code et non le nombre 1 ; seuls `true` et `false` sont des
booléens, si bien que `no` et `off` restent des chaînes ; les dates et `=`
restent des chaînes ; et un nombre entier écrit `4e1` vaut `40`. Une
spécification doit être en UTF-8, les `NaN` et `Infinity` de JSON sont
refusés, et un filtre peut imbriquer parenthèses, `not` et signe moins sur 50
niveaux au plus.

## Filtres et contrôles : le langage d'expressions

Un filtre ou la condition d'un contrôle est une expression :

```text
PetCount > 0 and answered(PetKind)
not refused(OwnerAge) or OwnerAge >= 18
VisitDate <= today()
```

De la liaison la plus lâche à la plus serrée :

| Opérateurs | Sens |
| --- | --- |
| `or`, `\|\|` | l'un ou l'autre côté |
| `and`, `&&` | les deux côtés |
| `not` | la négation |
| `=` `==` `!=` `<` `<=` `>` `>=` | une seule comparaison ; elles ne s'enchaînent pas : écrivez `1 < x and x < 3`, et non `1 < x < 3` |
| `+` `-` | addition, soustraction |
| `*` `/` | multiplication, division |
| `-` | l'opposé d'un nombre |

Les opérandes sont des nombres (`3`, `2.5`), des chaînes (`"texte"` ou
`'texte'`, un guillemet doublé à l'intérieur), des dates ISO (`2024-05-31` :
entourez un moins d'espaces pour soustraire), les identifiants de questions et
de variables, des parenthèses, et cinq fonctions :

| Fonction | Vraie quand |
| --- | --- |
| `answered(x)` | `x` a une réponse : ni vide ni refusée |
| `missing(x)` | `x` n'a pas de réponse : vide ou refusée |
| `empty(x)` | `x` est restée sans réponse |
| `refused(x)` | `x` a été refusée |
| `today()` | (une valeur) la date de l'entrevue |

Les mots-clés et les noms de fonctions ne tiennent pas compte de la casse ;
les identifiants, si. Un nombre est comparé comme nombre, donc `01` vaut `1` :
écrivez entre guillemets un code dont le zéro initial compte, `"01"`.
`identifiers()` liste les identifiants qu'une expression utilise, dans
l'ordre de leur première apparition, et `walk()` donne chacun de ses nœuds.

Deux filtres sont comparés une fois normalisés : `missing(x)` devient
`empty(x) or refused(x)` et `answered(x)` sa négation, une valeur comparée à
une question passe à droite, `not` se déplace vers l'intérieur de `and` et de
`or`, et les parties d'un `and` ou d'un `or` sont triées. Dans un `and`, un
test de réponse à côté d'une comparaison de la même question disparaît,
puisqu'une comparaison est fausse sans réponse : `answered(x) and x > 3` est
`x > 3`. Dans un filtre
enregistré sous la forme `Neutral` de Colectica, qui enregistre `"2"` et `2`
de la même façon, un nombre simple entre guillemets est comparé comme ce
nombre (`x = "2"` correspond à `x = 2`) ; `"02"`, `"+2"` ou `" 2"` restent
du texte, et dans du code Blaise un nombre entre guillemets est toujours du
texte.

```python
from ddi_l.spec import equivalent, format_expression, normalise, parse_expression

gate = parse_expression("not (answered(PetKind) and 3 < PetCount)")
print(format_expression(normalise(gate)))
print(equivalent("answered(x)", "not missing(x)"))
print(equivalent("x > 3", "x >= 4"))
```

La dernière ligne affiche `False`. La normalisation ne calcule rien : `x > 3`
et `x >= 4` ont des formes normales différentes. Sans l'extra `logic`, c'est
tout ce que sait `equivalent()` : un filtre signalé comme différent peut donc
être juste, et le rapport montre les deux formes normales pour en juger. Avec
l'extra, `equivalent()` décide le reste : ces deux filtres diffèrent encore,
pour un `x` entre 3 et 4, et concordent quand `x` est un nombre entier. De
même, `not (x > 3)` n'est pas `x <= 3` : un `x` sans réponse rend le premier
vrai et le second faux.

### Décider si deux filtres concordent

Avec l'extra `logic` (`pip install 'ddi-l[logic]'`, qui ajoute le solveur
Z3), `decide()` dit si deux filtres valent pour les mêmes répondants. Quand ce
n'est pas le cas, il donne un répondant sur lequel ils divergent :

```python
from ddi_l.spec import decide

verdict = decide("answered(x)", "x > 3 or x <= 3")
print(verdict.outcome)  # -> different
print(verdict.example.describe())  # -> x is answered with no value
print(decide("x > 3", "x >= 4", types={"x": "integer"}).outcome)  # -> equivalent
print(decide('Owner = "Ana"', 'Owner < "B"').reason)  # -> compares text by order
```

Un répondant laisse chaque question vide, la refuse ou y répond, et une
réponse peut n'avoir aucune valeur à comparer, comme un « ne sait pas ». Une
comparaison n'est vraie que si chaque question qu'elle lit a une valeur et
que rien n'y divise par zéro. Comment chaque nom est lu :

- une question comparée seulement par `=` et `!=` peut avoir plusieurs
  réponses : `x = 1` est vrai quand 1 est parmi elles, `x != 1` quand elle a
  des réponses et que 1 n'en est pas une ;
- une question ordonnée (`<`...), calculée, ou comparée à une date ou à
  `today()` a une seule valeur ;
- les nombres peuvent être des fractions sauf si `types` dit `integer`, et
  les dates sont des jours entiers. `types` donne à chaque nom l'un de
  `numeric`, `integer`, `date`, `text` ou `code`.

Le verdict est `equivalent`, `different` avec son `example`, ou `unknown` avec
une `reason` : du texte comparé par ordre, une condition comparée comme une
valeur, un nom comparé à des nombres et à du texte, ou deux noms comparés
quand l'un ou l'autre peut avoir plusieurs réponses. Deux filtres qui ne
diffèrent que pour une question à plusieurs codes répondus sont aussi
`unknown`, puisque cela dépend de la question. `evaluate()` dit si une
expression vaut pour un répondant, et chaque verdict `different` est vérifié
avec elle. Une limite de travail, et non une horloge, borne le solveur : un
verdict est le même à chaque exécution.

## Écrire un filtre pour Colectica

`compile_condition()` traduit un filtre en ce que Colectica enregistre dans un
`r:Command`. Le JSON de son éditeur de conditions (`Neutral`) contient ce que
les codes d'opérateurs de Colectica (énumérés dans
[Travailler avec les exports Colectica](colectica.fr.md#les-codes-sont-ceux-de-colectica))
peuvent exprimer :

| Expression | Énoncé |
| --- | --- |
| `x = 3`, `x != 3` (`x` sans codes) | `Equal`, `NotEqual` 3 |
| `x > 3`, `x >= 3`, `x < 3`, `x <= 3` | `GreaterThan`, `GreaterThanOrEqual`, `LessThan`, `LessThanOrEqual` 3 |
| `empty(x)`, `not empty(x)` | `Empty`, `NotEmpty` |
| `refused(x)`, `not refused(x)` | `Refused`, `NotRefused` |
| `x = 2`, `x = 2 or x = 3` (`x` codée) | `ContainsAny` ces codes |
| `x = 2 and x = 3` (`x` codée) | `ContainsAll` ces codes |
| `x != 2`, `x != 2 and x != 3` (`x` codée) | `ContainsNone` ces codes |

`answered(x)`, qui est `not empty(x) and not refused(x)`, fait donc deux
énoncés, et `missing(x)` est `Empty` ou `Refused`. Les énoncés sont joints en
un groupe par `and` ou `or`, ou en groupes joints par un seul `and` ou `or`
(`(a or b) and c`). Un choix parmi les codes d'une question codée est un seul
énoncé, où qu'il se trouve : `a and (x = 2 or x = 3) or b` convient donc
aussi.

`ddi-l` lit chaque énoncé de comparaison comme le langage d'expressions lit une
comparaison : faux quand la question n'a pas de réponse. On ne sait pas si
Colectica fait de même. Cela compte surtout pour `NotEqual` et
`ContainsNone`, qu'on pourrait aussi lire comme vrais quand rien n'a été
répondu ; vérifiez un tel filtre dans un aperçu.

```python
from ddi_l.colectica_logic import serialize_condition
from ddi_l.spec import BlaiseDialect, compile_condition

subjects = {
    "PetCount": "urn:ddi:example.org:in-count:1",
    "PetKind": "urn:ddi:example.org:in-kind:1",
}
codes = {"PetKind": {"2": "urn:ddi:example.org:code-cat:1"}}
compiled = compile_condition(
    "PetCount > 0 and PetKind = 2", subjects=subjects, codes=codes
)
print(compiled.condition.language, compiled.inputs)
print(serialize_condition(compiled.condition))
```

`subjects` donne l'`r:InParameter` de l'élément auquel chaque identifiant est
lié, et `codes` le `l:Code` de chaque valeur codée.

Tout le reste est écrit en code Blaise, et `fallback_reason` dit pourquoi :
- un `not` devant une comparaison : `not (x = 3)` est vrai quand `x` n'a pas
  de réponse, et on ne sait pas si `NotEqual` l'est ;
- de l'arithmétique, des dates ou `today()` ;
- une question comparée à une autre, ou du texte comparé par `<`, `<=`, `>`
  ou `>=` ;
- `and` et `or` mêlés dans un groupe (hors un choix parmi les codes d'une
  question codée), puisque l'ordre dans lequel Colectica les évalue n'est pas
  documenté.

Blaise nomme les entrées `{{name}}` et met chaque comparaison entre
parenthèses. Les mots qu'il emploie pour vide, refus, aujourd'hui et les
dates viennent d'un `BlaiseDialect`, qui n'a aucune valeur par défaut. Sans
le mot nécessaire, rien n'est compilé, et la raison nomme le réglage. Un
modèle de date doit se relire sans ambiguïté : `{year}`, `{month}` et `{day}`
une fois chacun, un texte avant le premier champ qui ne finit pas par un
chiffre, autre chose que des chiffres entre deux champs, aucun chiffre juste
après un champ, et des formats de la seule forme `0Nd` (`{month:02d}` ; une
largeur complète par des zéros, donc une valeur plus large se relit
aussi) ; `TODATE({year}, {month}, {day})`
convient, `{year}{month:02d}{day:02d}` est refusé :

```python
dialect = BlaiseDialect(empty="EMPTY", refused="REFUSAL")
gate = "answered(PetKind) and not (PetCount = 0)"
compiled = compile_condition(gate, subjects=subjects, dialect=dialect)
print(compiled.condition.text)
print(compiled.fallback_reason)

unset = compile_condition(gate, subjects=subjects)
print(unset.condition, unset.missing_settings)
```

`parse_blaise()` et `condition_to_expression()` relisent les deux formes en
expressions ; `ddi conform` s'en sert pour comparer les filtres d'un
instrument à ceux de la spécification. `compile_condition()` s'en sert aussi :
il relit ce qu'il a compilé et le compare au filtre, par forme normale puis
avec l'extra `logic` s'il est installé. `compiled.verified` vaut `True` quand
ils concordent, `False` quand ils diffèrent et `None` quand il n'a pas pu
trancher ; `compile_condition(..., validate=True)` lève une exception au lieu
de rendre une condition qui diffère, et nomme un répondant sur lequel elle
diffère.

```python
print(compiled.verified)  # -> True
```

## Vérifier un instrument

```text
pet-survey: Instrument 55555555 (Pet survey instrument)
module     severity  rule                             item       message
---------  --------  -------------------------------  ---------  --------------------------------------------------------------------------------------------------
household  info      spec.item.id-sources-differ      PetCount   The question PetCount is found by its construct_alias; its item_name is 'HouseholdPets'.
pets       error     spec.code.missing                PetKind    The question PetKind does not offer the code(s) 3.
pets       error     spec.code.extra                  PetKind    The question PetKind offers the code(s) 4, which the spec does not list.
pets       warning   spec.code.label                  PetKind    Code 2 of PetKind is labelled 'Chats' in fr; the spec says 'Chat'.
pets       error     spec.domain.length               PetName    The maximum length of PetName is 40; the spec says 50.
pets       warning   spec.language.missing            PetAge     The question text of PetAge has no fr.
pets       error     spec.domain.range                PetAge     The range of PetAge is [0, 30]; the spec says [0, 40].
pets       warning   spec.domain.decimals             PetAge     PetAge allows 1 decimal(s); the spec says 0.
pets       warning   spec.gate.extra                  PetAge     Question PetAge is gated by PetCount > 1; the spec gates it with nothing.
pets       warning   spec.item.extra                  PetColour  Module pets has the question QuestionConstruct 55555555 (PetColour), which the spec does not list.
visits     warning   spec.item.misplaced              VisitDate  The question VisitDate belongs in module visits, but is in module pets.
-          warning   spec.module.extra                feedback   The instrument has the module Sequence 55555555 (feedback), which the spec does not list.
-          error     spec.variable.derived-is-lookup  HasPets    The derived variable HasPets is a data lookup field: it is imported, not computed.
pets       info      spec.edit.unverifiable           age_range  The edit age_range: not verifiable (edit storage unknown).
5 error(s), 7 warning(s), 2 info.
```

| Option | Effet |
| --- | --- |
| `--spec SPEC` | La spécification (obligatoire). |
| `--module ID` | Ne comparer qu'un module ; les modules que la spécification ne liste pas et les variables ne sont alors pas vérifiés, et un élément du module que la spécification liste dans un autre module est signalé en trop. |
| `--instrument NAME` | L'instrument à comparer quand le fichier en a plusieurs. |
| `--edits off\|info\|strict` | Comment vérifier les contrôles (plus bas). Par défaut : `info`. |
| `--format json\|table` | JSON (par défaut) : la spécification, l'instrument, un résumé, le résultat de chaque module et les constats ; ou un tableau. |
| `-o PATH`, `--indent N` | Où écrire, et l'indentation du JSON. |
| `--fail-severity info\|warning\|error` | Le constat le moins sévère qui fait échouer l'exécution. Par défaut : `error`. |

`ddi conform` se termine avec :

- **0** : aucun constat n'atteint `--fail-severity` ;
- **1** : un constat l'atteint, ou l'extra `spec` n'est pas installé ;
- **2** : la comparaison ne peut pas s'exécuter : la spécification ne se lit
  pas ou ne passe pas ses vérifications, `--module` ne nomme aucun module de
  la spécification, `--edits strict` est demandé sans `match.edits` dans la
  spécification, ou le fichier de l'instrument ne se lit pas.

Depuis Python :

<!-- docs-test: skip -->
```python
import ddi_l as ddi
from ddi_l.spec import conform, load_spec

report = conform(ddi.read_ddi("instrument.xml"), load_spec("pet-survey.spec.yaml"))
print(report.summary)
for finding in report.findings:
    print(
        finding.severity, finding.rule_id, finding.module, finding.item, finding.message
    )
```

### Où les identifiants sont trouvés

Chaque identifiant est cherché aux endroits que `match` énumère, dans
l'ordre. Le premier endroit qui contient un identifiant, n'importe où dans
l'instrument, est celui qui sert. Un identifiant trouvé là sur plusieurs
constructions est signalé comme ambigu, jamais deviné.

| Clé | Par défaut | Endroits |
| --- | --- | --- |
| `question_id` | `[construct_alias, item_name, item_alias, construct_name]` | l'alias de l'`r:OutParameter` de la construction de question, le nom de la question, son alias de sortie, le nom de la construction |
| `statement_id` | `[construct_name, label, user_id]` | le `ConstructName`, l'`r:Label` et l'`r:UserID` de l'énoncé |
| `module_id` | `[construct_name, label, user_id]` | les mêmes, sur une séquence |
| `module_depth` | toute profondeur | la profondeur des séquences de modules : la séquence de l'instrument est 1, ses enfants 2 |
| `edits` | aucun | comment les contrôles sont enregistrés, pour `--edits strict` |
| `lookup_types` | aucun | un type de champ de recherche de données et le type de la spécification qu'il représente : `{Text: text, Integer: numeric}` |

Un module est une séquence. Une séquence de type `ConditionalChildContainer`
est le corps d'une branche d'un `IfThenElse`, jamais un module ni une page ;
une page est toute autre séquence à l'intérieur d'un module. Quand plusieurs
endroits donnent des identifiants différents pour une même question (l'alias
de sa construction et le nom de la question, par exemple), la question est
trouvée par le premier, et `spec.item.id-sources-differ` dit ce que
contiennent les autres.

Un module trouvé sur plusieurs séquences est `spec.module.ambiguous` ; aucun
de ses candidats n'est signalé comme module en trop, et les éléments qu'ils
contiennent ne sont ni mal placés ni comparés pour leurs filtres. Un élément
référencé à plusieurs endroits est comparé là où la spécification le place :
il n'est mal placé que si aucun de ses endroits n'est dans son module, et
chaque autre module qui le contient le signale comme `spec.item.extra`. Un
domaine référencé (une `ManagedNumericRepresentation`, par exemple) est
comparé comme un domaine en ligne ; d'un `StructuredMixedResponseDomain`,
c'est le seul domaine du type de la spécification qui est comparé.

### Filtres

Le filtre d'un module est l'ensemble des conditions sur le chemin de
l'instrument au module ; le filtre propre d'une question est l'ensemble des
conditions entre son module et la question. La branche Then d'un
`IfThenElse` ajoute sa condition ; une branche `ElseIf` ajoute sa condition
et la négation des précédentes ; la branche Else ajoute la négation de
toutes. Avec `gate_scope: page`, le filtre du module est attendu sur chaque
page plutôt que sur le module. Une spécification ne donne pas de filtre propre
à un énoncé : avec `gate_scope: page`, le filtre de sa page doit être l'un des
filtres entre son module et lui (sinon `spec.gate.missing` ou
`spec.gate.different`), et un autre filtre qui lui est propre n'est pas
comparé.

Quand les chemins vers un élément, dans son module, portent des filtres qui
ne sont pas équivalents, son filtre est `spec.gate.unverifiable`.

Avec l'extra `logic`, les filtres et les contrôles sont décidés comme le fait
`decide()` après comparaison de leurs formes normales : un filtre écrit
autrement qui concorde toujours avec celui de la spécification n'est pas
signalé. Les domaines de réponse et les types de variables de la
spécification disent ce qu'est chaque nom : un domaine numérique sans
décimales est un nombre entier, si bien que `PetCount > 0` et `PetCount >= 1`
concordent. Un filtre ou un contrôle qui diffère nomme un répondant sur lequel
les deux divergent, dans le message et dans le champ `example` du constat :

```text
Module pets is gated by PetCount > 0; the spec says PetCount > 1 (they differ when PetCount is 1).
```

`--semantics syntactic` (`conform(semantics="syntactic")`) ne compare que les
formes normales, comme sans l'extra ; `--semantics smt` échoue sans lui.

Les sujets d'une condition `Neutral` sont suivis à travers leurs liaisons,
celles de la dernière version de chaque élément, jusqu'à la question dont ils
viennent. Une question que la spécification ne liste pas est nommée par son
premier identifiant : un filtre lié à la mauvaise question se lit donc comme
cette question ; une sortie d'une question qui en a plusieurs (la cellule
d'une grille) est nommée par son alias ou, quand la spécification ne connaît
pas cet alias, par la variable de la spécification qu'un alias du chemin
nomme. Un sujet lié à aucune question est nommé par la sortie où ses liaisons
aboutissent (le champ d'une recherche de données) : un alias ne cache jamais
à quelle question, sortie ou champ un filtre est lié. Le code Blaise est lu avec les mots `blaise` de la
spécification, ses entrées `{{name}}` nommées de la même façon.

### Contrôles de saisie

L'endroit où un instrument enregistre ses contrôles n'est pas connu en
général : par défaut, chaque contrôle est donc signalé comme **info : not
verifiable (edit storage unknown)**. `--edits off` laisse les contrôles de
côté.

`--edits strict` les cherche, dès que la spécification dit comment ils sont
enregistrés. Un contrôle est un `ComputationItem` marqué par un attribut
d'utilisateur ; son identifiant est dans son `construct_name`, son `label`
ou son `user_id` :

```yaml
match:
  edits: {attribute: kind, value: EditCheck, id: construct_name}
```

Colectica, par exemple, marque ses calculs d'un `r:UserAttributePair` dont
l'`r:AttributeKey` est `x:TypeOfComputation` : donnez à `attribute` et à
`value` ce que contiennent vos exports. Un contrôle sans tel calcul est
`spec.edit.missing` ; un calcul dont la condition diffère de `when` est
`spec.edit.different`.

## Règles

| Règle | Par défaut | Signalée quand |
| --- | --- | --- |
| `spec.instrument.missing` | error | Aucun instrument du fichier ne correspond à l'`instrument` de la spécification, ou le fichier n'en a aucun. |
| `spec.instrument.ambiguous` | error | Plusieurs instruments correspondent ; nommez-en un avec `instrument` ou `--instrument`. |
| `spec.module.missing` | error | Un module requis n'est pas dans l'instrument. |
| `spec.module.ambiguous` | error | Plusieurs séquences portent l'identifiant d'un module. |
| `spec.module.extra` | warning | Une séquence à la profondeur des modules que la spécification ne liste pas. |
| `spec.item.missing` | error | Une question ou un énoncé est introuvable. |
| `spec.item.ambiguous` | error | Plusieurs constructions portent l'identifiant d'une question ou d'un énoncé. |
| `spec.item.extra` | warning | Une question ou un énoncé d'un module que la spécification n'y liste pas, ou qu'elle liste dans un autre module. |
| `spec.item.misplaced` | warning | Une question ou un énoncé trouvé seulement dans d'autres modules que celui de la spécification. |
| `spec.item.id-sources-differ` | info | Les sources d'identifiant d'une question ne concordent pas (le nom de sa construction et celui de la question, par exemple). |
| `spec.code.missing` | error | Un code que la spécification liste n'est pas offert. |
| `spec.code.extra` | error | Un code est offert que la spécification ne liste pas. |
| `spec.code.label` | warning | Le libellé de catégorie d'un code diffère de celui de la spécification, dans une langue. |
| `spec.language.missing` | warning | Le texte d'une question ou d'un énoncé, ou le libellé d'un code, n'est pas dans l'une des langues de la spécification. |
| `spec.domain.type` | error | Le domaine de réponse est d'un autre genre (code, numérique, texte, date), ou un domaine mixte n'en contient aucun du type de la spécification. |
| `spec.domain.length` | error | La longueur minimale ou maximale d'un domaine texte diffère. |
| `spec.domain.range` | error | Les bornes d'un domaine numérique, ou leur inclusion, diffèrent. |
| `spec.domain.decimals` | warning | Les décimales d'un domaine numérique diffèrent. |
| `spec.domain.unverifiable` | info | Le domaine de la question ne peut pas être lu (plusieurs domaines, un domaine mixte qui en contient plusieurs du type de la spécification, une référence absente du fichier, une liste de codes introuvable). |
| `spec.gate.missing` | error | La spécification filtre un module ou une question, et rien ne le filtre. |
| `spec.gate.different` | error | Le filtre diffère de celui de la spécification ; les deux formes normales sont montrées. |
| `spec.gate.extra` | warning | Un module ou une question est filtré, et la spécification ne le filtre pas. |
| `spec.gate.scope` | error | Le filtre entoure chaque page là où la spécification dit le module, ou l'inverse. |
| `spec.gate.unverifiable` | warning | Le filtre enregistré ne peut pas être relu en expression (un code d'opérateur non énuméré, un test de « ne sait pas », and et or mêlés, du JSON `Neutral` mal formé, du code natif que ce lecteur ne connaît pas), ou les chemins vers l'élément portent des filtres différents. |
| `spec.edit.unverifiable` | info | Non vérifiable (enregistrement des contrôles inconnu) : signalé pour chaque contrôle, sauf avec `--edits strict` ou `off`. |
| `spec.edit.missing` | error | Avec `--edits strict`, aucun calcul ne porte l'identifiant du contrôle. |
| `spec.edit.different` | error | Avec `--edits strict`, la condition du calcul diffère de `when`. |
| `spec.variable.import-undeclared` | error | Une variable importée n'est un champ d'aucune recherche de données que l'instrument atteint. |
| `spec.variable.import-type` | warning | Le type du champ de recherche d'une variable importée diffère (avec `match.lookup_types`). |
| `spec.variable.derived-is-lookup` | error | Une variable dérivée est un champ de recherche de données : elle est importée, non calculée. |

## Limites

- **Seuls les noms des codes d'opérateurs sont connus.** Un code non
  énuméré, et `DontKnow` et `NotDontKnow` (le langage d'expressions n'a pas
  de « ne sait pas »), sont signalés comme non vérifiables.
- **La façon dont un énoncé traite une question sans réponse n'est pas
  connue.** `ddi-l` lit chaque comparaison comme fausse sans réponse,
  comme le fait le langage d'expressions.
- **L'ordre de `and` et de `or` dans un groupe n'est pas connu.** Les
  filtres qui les mêlent dans un groupe sont signalés comme non vérifiables, et
  aucun n'est compilé ainsi.
- **Sans l'extra `logic`, rien n'est calculé.** La normalisation ne prouve
  pas l'équivalence arithmétique : `x > 3` et `x >= 4` sont signalés comme
  différents, même pour une question à nombre entier. Avec lui, ce que
  `decide()` ne sait pas modéliser, comme du texte comparé par ordre, est
  encore comparé par forme normale.
- **Une question comparée seulement par `=` et `!=` peut avoir plusieurs
  réponses**, sauf si son domaine dit autre chose. Deux filtres qui ne
  diffèrent que pour plusieurs réponses (`x = 1 and x = 2` et
  `x = 1 and x = 3`) sont signalés comme différents, sans répondant.
- **L'endroit où les contrôles sont enregistrés n'est pas connu en général**,
  d'où `--edits info` par défaut.
- **Une comparaison sous `not` reste telle qu'écrite**, puisqu'elle diffère de
  son contraire quand la question n'a pas de réponse.
