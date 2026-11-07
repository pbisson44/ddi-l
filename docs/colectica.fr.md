---
description: >-
  Lire, modifier et écrire les exports FragmentInstance de Colectica Designer
  avec ddi-l : chaque type d'élément comme modèle typé, et des fichiers
  réécrits octet pour octet dans la mise en forme de Colectica.
---

# Travailler avec les exports Colectica

!!! note "Sans lien avec Colectica"
    `ddi-l` est un projet indépendant. Il nomme Colectica pour dire quels
    fichiers il lit et écrit ; les formats propres à Colectica décrits ici
    sont déduits, et non tirés d'une spécification de Colectica.

Colectica Designer et Colectica Repository échangent le DDI 3.3 sous forme de
`FragmentInstance` : un élément par `<Fragment>`, des références entre
éléments par Agency, ID et Version, et une `TopLevelReference` qui nomme
l'élément pour lequel l'export a été fait. `ddi-l` lit ces fichiers, vous
donne chaque élément comme modèle typé et les réécrit comme le fait
Colectica : un fichier ouvert puis enregistré sans modification revient
octet pour octet.

## Ouvrir un export

`ddi.open_fragment()` ouvre une `FragmentInstance`. (`ddi.open_ddi()` sert aux
documents `DDIInstance` et vous renvoie ici si on lui passe un fragment.) Pour
que cette page s'exécute seule, le premier bloc construit un petit export et
l'enregistre ; avec un vrai export, commencez à `open_fragment`.

```python
import ddi_l as ddi

age = ddi.Variable(
    agency="example.org",
    identifier="5f0e3c1a-0b8e-4d3e-9a5e-6a1b2c3d4e5f",
    version="1",
    labels=[
        ddi.InternationalString("Age", lang="en"),
        ddi.InternationalString("Âge", lang="fr"),
    ],
)
ddi.DDIFragment.from_items([age]).save("export.xml")

fragment = ddi.open_fragment("export.xml")
for item in fragment.items():
    print(type(item).__name__, item.identifier, item.version)
```

`items()` analyse chaque élément dans son modèle ; passez une classe de
modèle pour n'en garder qu'un type, comme `fragment.items(ddi.Variable)`.
Chaque type d'élément qu'un fragment DDI 3.3 peut contenir a un modèle (161),
y compris les schémas, groupes, représentations gérées, types géographiques
et dispositions d'enregistrement qui n'ont pas de classe écrite à la main :
ceux-là viennent de `ddi_l.models.items`.

## Retrouver, modifier et remettre

`get()` retrouve un élément par son ID. Un export Colectica peut contenir
plusieurs versions d'un même élément ; sans `version=`, vous obtenez la plus
élevée. Les modèles sont des copies : réécrivez un élément modifié avec
`put()` :

```python
variable = fragment.get("5f0e3c1a-0b8e-4d3e-9a5e-6a1b2c3d4e5f")
variable.labels.append(ddi.InternationalString("Âge (années)", lang="fr-CA"))
variable.increment_major_version()
fragment.put(variable)
fragment.save("export.xml")
```

`put()` remplace l'élément de même Agency, ID et Version ; à défaut, l'unique
élément de même Agency et ID (la version que vous venez d'incrémenter) ;
sinon il ajoute l'élément dans un nouveau `<Fragment>`. `remove()` supprime
des éléments et `top_level_item()` renvoie l'élément que nomme la
`TopLevelReference`.

Tout ce que vous n'avez pas touché est réécrit tel que lu : `versionDate`,
`r:VersionResponsibility`, la filiation `r:BasedOnObject`, les paires
d'attributs utilisateur (sur les éléments et dans les références), les noms
et libellés multilingues conservés dans un seul élément, `audienceLanguage`
sur le texte des questions, les attributs de vocabulaire contrôlé,
l'orthographe d'origine des valeurs (`"1"` pour vrai, `"01"`) et les
références sans `r:URN`.

## Versions

Colectica numérote les versions par des entiers (`1`, `2`… `78`) et date
chacune d'une `versionDate`. `ddi-l` respecte ces deux conventions quand vous
incrémentez un élément :

- `increment_major_version()` fait passer `"2"` à `"3"`. Sur un élément qui a
  une `versionDate`, elle la met aussi à l'heure actuelle, au format de
  Colectica (`2026-07-16T15:15:11.7905158Z`). Un élément qui n'en a pas n'en
  reçoit pas ; passez `touch=False` pour garder l'ancienne date.
- `increment_minor_version()` et `increment_subversion()` refusent une
  version entière, car Colectica numérote les versions par des entiers et
  pourrait ne pas relire une version pointée comme `"3.1"`. Passez `allow_dotted=True` si c'est bien ce que vous voulez. Une
  version déjà pointée (`"1.0"`) s'incrémente comme avant.
- `responsibility="…"` enregistre l'auteur du changement dans
  `r:VersionResponsibility`. Pour enregistrer le même nom à chaque
  incrémentation, définissez-le une fois avec
  `ddi.configure(version_responsibility="…")` ; `responsibility=None`
  n'en enregistre aucun pour une incrémentation, quel que soit le réglage.
  `ddi-l` n'en invente jamais.

```python
variable = fragment.get("5f0e3c1a-0b8e-4d3e-9a5e-6a1b2c3d4e5f")
variable.increment_major_version(responsibility="Équipe questionnaire")
print(variable.version, variable.version_date, variable.version_responsibility)

try:
    variable.increment_minor_version()
except ddi.DDIModelError as error:
    print(error)

with ddi.configured(version_responsibility="Équipe questionnaire"):
    variable.increment_major_version()
fragment.put(variable)
```

`ddi.configured(...)` applique un réglage dans un bloc `with`, pour le fil
d'exécution ou la tâche en cours seulement, et rétablit le précédent à la
sortie. `ddi.reset_configuration()` rétablit les valeurs par
défaut.

## Vérifier un export avec lint

`ddi lint --profile colectica-questionnaire` exécute les vérifications
écrites pour le contenu Colectica :

```bash
ddi lint export.xml --profile colectica-questionnaire
```

- **`colectica.maintainable.labels`** accepte un `r:Label`, un `r:Name` ou
  l'élément de nom propre à l'élément (`ConstructName`, `QuestionItemName`…),
  pourvu qu'il contienne du texte. Les éléments Colectica portent d'ordinaire
  un nom plutôt qu'un libellé, si bien que la règle `ddi.maintainable.labels`
  du profil par défaut les signale presque tous.
- **Les références se résolvent comme Colectica l'entend.** Une référence
  marquée `lateBound="true"` signifie « la dernière version ». Colectica
  écrit les références tardives aux paramètres en version 1 alors que le
  paramètre lui-même est, par exemple, en version 4 : toute version présente
  la résout donc (`lateBound="1"` compte aussi). Avec un
  `lateBoundRestriction` comme `4`, seules les versions de la version
  majeure 4 la résolvent. Une référence tardive qui nomme une version plus
  récente que toutes celles du fichier, ou dont la restriction ne correspond à
  aucune version présente, est signalée par `ddi.reference.version`.
- **`ddi.reference.version`** (avertissement) signale une référence exacte
  dont l'élément est dans le fichier, mais seulement en d'autres versions, et
  liste celles qui s'y trouvent.
- **`ddi.reference.provenance-external`** (info) signale une
  `r:BasedOnReference`, ou une référence placée dans une
  `r:UserAttributePair`, dont l'élément n'est pas dans le fichier. Ces
  références indiquent d'où un élément a été copié, et la source se trouve
  d'ordinaire ailleurs.
- **`ddi.reference.integrity`** garde tout le reste de ce qui ne se résout
  pas. C'est un avertissement dans un fragment, qui peut être partiel, et une
  erreur dans une `DDIInstance`.

Les constats `info` ne font jamais échouer `ddi lint`. Utilisez
`--fail-severity warning` ou `--fail-severity info` pour un contrôle plus
strict.

Le profil vérifie aussi la conception du questionnaire lui-même, à la
recherche de problèmes courants, chacun nommé d'après l'élément où il se
trouve (type, ID abrégé et nom) :

- **Identifiants et liaisons :** un paramètre ou un code déclaré dans deux
  éléments (une copie qui a gardé les ID de sa source), une liaison vers un
  paramètre que le fichier ne déclare pas.
- **Conditions :** conditions malformées ou vides (avec la description qui
  contient sans doute la logique voulue), groupes qui ne peuvent jamais être
  vrais, code natif qui n'est pas une seule expression, entrées qu'une
  condition n'utilise jamais, synopsis enregistré qui nomme une autre
  variable, et filtre qui n'englobe que la première construction d'une page.
- **Domaines :** domaine de codes sans liste de codes, libellé de domaine
  qui nomme une autre variable, question dont la formulation ne correspond pas
  au type de réponse.
- **Texte :** traductions manquantes, gabarits non remplacés, mots
  d'interface collés depuis des maquettes, insertions `#{nom}` malformées ou
  non déclarées, et énoncés qui sont des notes de conception.
- **Recherches et alias :** champs de recherche de données en double ou
  suspects, et alias de paramètres dont l'échappement s'est accumulé
  (`_x005F_`) ou qui contiennent le texte d'une question.

Plusieurs règles dépendent des conventions de votre organisme : langues
requises, noms fournis par le système d'exécution, schéma de nommage des
variables. Elles ne font rien tant qu'elles ne sont pas configurées :

```bash
ddi lint export.xml --profile colectica-questionnaire --format table \
  --required-language en-CA --required-language fr-CA \
  --known-names noms-execution.txt --lint-config lint.json
```

La [référence des règles lint](lint-rules.fr.md) énumère chaque règle avec un
exemple de constat, ainsi que chaque option.

## Conditions

DDI définit où un `IfThenElse` ou un `ComputationItem` garde sa logique, un
`r:Command`, mais pas ce qu'il contient : `r:ProgramLanguage` nomme le
langage et `r:CommandContent` contient le code sous forme de texte. Colectica y
écrit trois sortes de contenu, que lit `ddi_l.colectica_logic` :

| `r:ProgramLanguage` | Contenu | Lu comme |
| --- | --- | --- |
| `Neutral` | JSON de l'éditeur de conditions de Colectica : des groupes d'énoncés | `Condition` |
| `Blaise5DataLookup` | JSON des champs que lit une recherche de données | `DataLookup` |
| tout autre (`Blaise`…) | code natif | `NativeCondition` (le texte, inchangé) |

Un énoncé `Neutral` compare un **sujet**, l'URN de l'un des `r:InParameter`
de l'élément, à une valeur ou à un ensemble de codes. Une séquence parente
relie ce paramètre à la réponse d'une question.

```python
from ddi_l.colectica_logic import Operator, parse_command, serialize_condition

text = (
    '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{"StatementBooleanType":0,'
    '"Subject":"urn:ddi:example.org:q1-in:1","Operator":3,"Value":{"Value":"2",'
    '"ValueNotNeeded":false,"SelectedCodes":[]}}]}],"Synopsis":"Q1 Greater than 2",'
    '"Version":1}'
)
condition = parse_command("Neutral", text)
statement = condition.logic_groups[0].statements[0]
print(statement.operator is Operator.GREATER_THAN, statement.value)
assert serialize_condition(condition) == text  # inchangée : réécrite telle que lue

statement.value = "3"
print(serialize_condition(condition))
```

`parse_condition(item)` fait de même à partir d'un `IfThenElse` ou d'un
`ComputationItem` (un élément ou un modèle typé), et
`write_condition(item, condition)` y réécrit une condition modifiée. Une
condition inchangée est réécrite octet pour octet. Une condition modifiée est
écrite comme Colectica écrit le JSON : sans espaces, les clés dans l'ordre lu,
et les caractères non ASCII échappés seulement si la source les échappait.

Les boucles gardent leur condition de la même façon : un `Loop` dans
`d:LoopWhile`, un `RepeatUntil` dans `d:UntilCondition` et un `RepeatWhile`
dans `d:WhileCondition`, que `parse_condition()` et `write_condition()` lisent
et écrivent. Les `d:InitialValue` et `d:StepValue` d'un `Loop` contiennent des
affectations plutôt qu'une condition ; `which="InitialValue"` ou
`which="StepValue"` les atteint. Chaque `d:ElseIf` d'un `IfThenElse` a sa
propre condition : passez l'élément `ElseIf`. Les règles de lint vérifient
chaque branche, et une entrée que seul un `ElseIf` teste compte comme
utilisée, là comme dans `ddi explain-condition`.

### Les codes sont ceux de Colectica

Les entiers du JSON sont les codes de Colectica : `Operator` pour l'opérateur
d'un énoncé, `GroupBool` et `StmtBool` pour la façon dont les groupes et les
énoncés se joignent. Une valeur non répertoriée est gardée telle quelle :
une condition qui l'utilise se lit donc et se réécrit telle que lue
(`Operator(99).name == "UNKNOWN_99"`).

| Énumération | Valeurs |
| --- | --- |
| `GroupBool` (comment un groupe se joint aux groupes précédents) | `0` None (`FIRST`, le premier groupe), `1` Et, `2` Ou |
| `StmtBool` (comment un énoncé se joint aux énoncés précédents) | `0` None (`FIRST`, le premier énoncé), `1` Et, `2` Ou |
| `Operator` | `0` None, `1` Equal (`EQUAL_TO`), `2` NotEqual, `3` GreaterThan, `4` GreaterThanOrEqual, `5` LessThan, `6` LessThanOrEqual, `7` Empty, `8` NotEmpty, `9` Contains, `10` DoesNotContain, `11` ContainsAny, `12` ContainsAll, `13` ContainsNone, `14` Refused, `15` NotRefused, `16` DontKnow, `17` NotDontKnow |

Seuls les noms des codes sont connus : ni la façon dont un énoncé traite une
question sans réponse, ni l'ordre dans lequel s'évaluent `And` et `Or` mêlés
dans un groupe ; la page [Vérifier un questionnaire par rapport à une
spécification](spec-conformance.fr.md#ecrire-un-filtre-pour-colectica) dit comment
`ddi-l` les lit.

### Vérifier un synopsis enregistré

Colectica enregistre un `Synopsis` à côté de la logique : le texte que son
éditeur a affiché en dernier. Il peut être périmé, et il numérote les codes
selon leur position dans la liste plutôt que selon leur valeur.
`render_synopsis(condition, fragment)` en écrit un à partir de la logique
elle-même, en nommant chaque sujet d'après la question qui lui est reliée et
chaque code par sa valeur et son libellé. En ligne de commande,
`ddi explain-condition` affiche les deux, la description de la condition et les
entrées de l'élément qu'elle utilise :

```bash
ddi explain-condition export.xml 22222222-2222-4222-8222-000000000030
```

```text
Item              IfThenElse 22222222-2222-4222-8222-000000000030 (version 1)
Language          Neutral
Stored synopsis   (PetName Contains All 2 Cat) And ((PetCount Greater than 2) Or (PetCount Refused))
Rendered          (PetKind contains all of 3 "Cat") and (PetCount > 2 or PetCount is refused)
Synopsis mismatch the stored synopsis does not name PetKind
Description en-CA Show when a cat lives here and there are more than two pets.
Inputs used       PetKind, PetCount
Inputs unused     PetAge
```

`--format json` affiche la même chose en JSON, et
`explain_condition(fragment, id)` la renvoie sous forme de
`ConditionExplanation`.

## Réparer un gabarit

Colectica référence un élément dans une version fixe. Modifiez une séquence,
donnez-lui une nouvelle version, et tous les éléments qui pointent vers
l'ancienne version sont périmés : leur référence doit nommer la nouvelle
version, ce qui modifie ces éléments à leur tour, jusqu'à l'instrument.
`DDIFragment` fait ce parcours, et modifie les séquences d'un fragment sans
laisser ses références en arrière.

- **`revise(*items, cascade=True, dry_run=False, responsibility=None,
  version_date=None, rationale=None)`** donne à chaque élément la version majeure suivante,
  et la donne aussi à chaque identifiable qu'il déclare (ses paramètres, ses
  codes), comme Colectica les numérote. Tous les éléments révisés par un même
  appel reçoivent la même `versionDate` (`version_date`, ou maintenant),
  comme quand Colectica enregistre plusieurs éléments à la fois, et
  `responsibility` (ou celle fixée avec `ddi.configure()`). Avec `cascade`,
  chaque élément qui référence une ancienne version, d'un élément ou de ce
  qu'il déclare, est mis à jour et révisé à son tour, une seule fois,
  jusqu'au sommet ; la
  `TopLevelReference` suit. Les références tardives désignent déjà
  « la dernière version » et ne sont pas touchées. `rationale` (une chaîne,
  ou `{langue: texte}`) est inscrit comme `r:VersionRationale` de chaque
  élément révisé, comme Colectica inscrit le message d'un enregistrement sur
  chaque élément qu'il enregistre ; la justification que portait un élément
  est retirée dans tous les cas, puisqu'elle expliquait la version
  précédente. `dry_run=True` renvoie
  le plan sans rien modifier.
- **`move_construct(construct, from_sequence, to_sequence, index=None)`**
  déplace une construction d'une séquence à une autre.
- **`insert_construct(sequence, construct, index=None, before=None,
  after=None)`** insère une construction dans une séquence : une construction
  déjà dans le fragment, ou un nouvel élément typé, qui est ajouté avec ce que
  Colectica écrit sur chaque élément : la responsabilité configurée, entre
  autres, et un `r:URN` et la version de l'élément sur chaque identifiable
  qu'il déclare.
- **`wrap_in_condition(sequence, constructs, condition)`** place des
  constructions sous un nouvel `IfThenElse`, dans une séquence Then de type
  `ConditionalChildContainer`. Les deux nouveaux éléments partagent une même
  `versionDate` et notent la responsabilité configurée.
- **`duplicate(item)`** copie un élément en donnant un nouvel ID à lui et à
  tout ce qu'il déclare, et note la source dans `r:BasedOnObject`. La copie
  et ce qu'elle déclare commencent à la version 1. Une copie
  faite ainsi ne partage aucun ID de paramètre avec sa source ; placez-la
  avec `insert_construct()`.
- **`repair_shared_identifiables(dry_run=True)`** donne à chaque copie d'un
  identifiable partagé (ce que signale `colectica.identifiable.shared-id`) un
  ID propre, en gardant celui de l'original : la `versionDate` la plus
  ancienne, sinon l'élément sans `r:BasedOnObject`. Les liaisons des
  constructions de question de la copie suivent ; toute autre référence à
  l'ID partagé est signalée comme ambiguë plutôt que devinée.

Les outils de modification ne changent aucune version : ils renvoient les
éléments touchés, à passer à `revise()`. Une page dont le filtre n'englobe
que le premier énoncé, corrigée :

<!-- docs-test: skip -- fragment: les ID sont ceux du gabarit du lecteur -->
```python
fragment = ddi.open_fragment("gabarit.xml")

touched = set()
for statement in statements_after_the_gate:
    result = fragment.move_construct(statement, entry_page, gate_then_sequence)
    touched.update(result.touched)

plan = fragment.revise(*touched, dry_run=True)
for step in plan:
    print(step.item_type, step.identifier, step.old_version, "->", step.new_version)

fragment.revise(*touched, responsibility="Équipe questionnaire")
fragment.save("gabarit.xml")
```

Seuls les éléments sur le chemin entre la modification et l'instrument
reçoivent une nouvelle version : les deux séquences touchées, l'`IfThenElse`
qui fixe la séquence Then, et la section, la racine et l'instrument au-dessus.

Un nouvel énoncé après la dernière question d'une page, de la même façon :

<!-- docs-test: skip -- fragment: les ID sont ceux du gabarit du lecteur -->
```python
from ddi_l.models import InternationalString, StatementItem

thanks = StatementItem(
    agency="example.org",
    identifier=new_statement_id,
    version="1",
    construct_names=[InternationalString("Merci", lang="fr")],
)
result = fragment.insert_construct(page, thanks, after=last_question)
fragment.revise(*result.touched)
```

!!! warning "Réimportation non vérifiée"
    On n'a pas vérifié si Colectica accepte à la réimportation des éléments
    dont les identifiables ont reçu de nouveaux ID par
    `repair_shared_identifiables()`. Essayez d'abord sur une copie du
    référentiel.

## Construire un fragment de zéro

`DDIFragment.from_items()` écrit un élément par `<Fragment>`, nomme le premier
dans la `TopLevelReference` et donne à chaque élément ce que Colectica écrit
sur tous les siens : `isUniversallyUnique="true"`, une `versionDate`
(maintenant, au format UTC à sept décimales de Colectica, sauf si vous en
fournissez une) et un `r:URN`. Les références sont identifiées par Agency, ID
et Version seulement, comme les écrit Colectica.

```python
question = ddi.QuestionItem(
    agency="example.org",
    identifier="c2b1a9e4-7d3f-4b8a-9e21-0f6d5c4b3a29",
    version="1",
    question_texts=[ddi.InternationalString("Quel âge avez-vous?", lang="fr")],
)
package = ddi.DDIFragment.from_items([question, age])
print(package.validate())
package.save("package.xml")
```

Pour construire d'un coup de nombreux éléments à partir de métadonnées tenues
dans des tableurs (une étude, son questionnaire, ses variables, ses fichiers
de données et plus), voir
[Charger du DDI depuis des tableurs](spreadsheet-import.fr.md) :
`load_tables(...).to_fragment()` donne le même genre de fragment.

## Mise en forme

Un fichier lu est réécrit avec ses parties inchangées telles qu'elles ont
été lues, octet pour octet, quel que soit l'outil qui l'a écrit : `save()`,
`to_xml()`, `ddi.write_ddi()`, `ddi roundtrip` et l'API HTTP. Seul ce que vous
ajoutez ou modifiez est mis en forme, dans la mise en forme de Colectica pour
une `FragmentInstance`. Toute autre `FragmentInstance` (construite dans le
code, ou par `ddi from-json`) est écrite entièrement dans la mise en forme de
Colectica. C'est-à-dire UTF-8, le préfixe `ddi:` sur la racine et la
`TopLevelReference`, chaque `<Fragment>` en marge gauche déclarant l'espace
de noms réutilisable comme `r:`, chaque élément déclarant l'espace de noms de
son module comme espace par défaut, les attributs dans l'ordre du schéma et
une indentation de deux espaces. `layout="colectica"` (`--layout colectica`,
`?layout=colectica`) écrit tout le fichier dans la mise en forme de
Colectica, et `layout="default"` dans la mise en forme habituelle de cette
bibliothèque, comme `pretty_print=False`, `xml_declaration=False` ou un
encodage autre qu'UTF-8, que seule cette mise en forme connaît. Une
`DDIInstance` lue dans un fichier garde de même sa propre mise en forme,
quand elle utilise les préfixes canoniques (`r`, `s`, `d`...) ; une
`DDIInstance` construite dans le code est écrite dans la mise en forme de
cette bibliothèque.

En ligne de commande :

```bash
ddi validate export.xml
ddi lint export.xml
ddi roundtrip export.xml -o copy.xml
```

`ddi roundtrip` sur un export non modifié écrit un fichier identique.

Le XHTML en ligne garde ses espaces. Dans
`<r:Content><b>Kind</b> <i>of pet</i></r:Content>`, l'espace entre les deux
éléments est du texte : le libellé se lit « Kind of pet » avec les deux
moteurs, et le fichier est réécrit tel que lu. Les espaces entre des blocs
XHTML (`<p>`, `<ul>`...) sont de la mise en forme. lxml retire le texte vide
à la lecture ; un fichier où du XHTML en ligne n'a pas de texte avant lui
dans son élément est donc analysé une seconde fois, en gardant toutes les
espaces puis en retirant l'indentation : lire un tel fichier prend jusqu'à
deux fois plus de temps, et les autres fichiers sont lus comme avant.

### Marque d'ordre des octets

La plupart des exports Colectica commencent par une marque d'ordre des octets
UTF-8 ; certains exports des outils serveur de Colectica n'en ont pas.
`ddi-l` retient ce qu'il a lu (`fragment.source_bom`) et écrit la même chose,
si bien que les deux sortes d'exports font l'aller-retour octet pour octet.
Passez `bom=True` ou `bom=False` à `save()`, à `to_colectica_bytes()` ou à
`ddi.write_ddi()` pour choisir. Un fragment construit
dans le code reçoit une marque.
