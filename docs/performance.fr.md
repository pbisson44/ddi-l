---
description: >-
  Temps et mémoire mesurés pour ddi-l, et les réglages qui les modifient :
  moteur lxml, cache de validation et lecture en flux.
---

# Performance

Ce qui coûte du temps et de la mémoire dans ddi-l, avec des mesures et les
réglages qui les modifient.

## Temps indicatifs

Une étude de 5 000 variables (1,4 Mio de XML), Python 3.11 sur un seul cœur,
médiane de plusieurs exécutions. Lisez ces chiffres comme des proportions, pas
comme des garanties.

| Opération | Moteur lxml | Moteur stdlib |
| --- | --- | --- |
| `read_ddi(data)` | 0,02 s | 0,18 s |
| `write_ddi(document)` | 0,06 s | 0,35 s |
| `Document.to_xml()` | 0,6 s | 0,3 s |
| `lint_source(data)` | 0,4 s | 0,2 s |
| `validate_source(data)` (schéma seul) | 0,05 s | 1,4 s |
| `Document.validate()` | 0,6 s | 3,5 s |
| `import ddi_l` | 0,03 s | 0,03 s |
| `ddi --help` | 0,08 s | 0,08 s |

Lorsque lxml est installé, un document est d'abord vérifié par le validateur C
de libxml2, qui confirme un document valide en quelques millisecondes.
[xmlschema](https://pypi.org/project/xmlschema/) ne s'exécute que si cette
vérification échoue, pour produire le détail des anomalies : les erreurs
signalées sont donc les mêmes sur les deux moteurs. Sans lxml, toute
validation passe par xmlschema, écrit en Python pur, qui domine les temps
ci-dessus. `schema_loader.validate(..., backend="python")` désactive la
vérification libxml2 pour un appel, et
`schema_loader.set_validation_backend("python")` pour toute l'application.

## Les moteurs XML sur un gros export

Un export Colectica de 9 Mo (112 000 éléments), Python 3.13, meilleur de cinq
essais sur une même machine. `benchmarks/backends_bench.py` mesure les mêmes
étapes sur n'importe quel fichier, avec le moteur que nomme
`DDI_L_XML_BACKEND`.

| Étape | native | lxml | stdlib |
| --- | --- | --- | --- |
| Analyse syntaxique | 0,05 s (185 Mo/s) | 0,07 s (124 Mo/s) | 0,22 s (41 Mo/s) |
| `read_ddi` | 0,13 s | 0,33 s | 0,29 s |
| Premier `write_ddi` (construit l'index de la source) | 0,23 s | 1,4 s | 1,7 s |
| `write_ddi` de nouveau, sans changement | 0,01 s | 0,28 s | 0,23 s |
| `write_ddi` après la modification d'un attribut | 0,04 s | 0,31 s | 0,28 s |
| `write_ddi(layout="default")` | 0,80 s | 0,26 s | 0,76 s |
| Profil `colectica-questionnaire` | 0,67 s | 1,74 s | 0,62 s |

- **L'analyse n'est pas limitée par la bande passante mémoire.** Copier les
  mêmes octets prend 1 ms (6,5 Go/s) ; l'essentiel de l'analyse native est la
  création des 112 000 nœuds de l'arbre. Un texte qui n'avait pas besoin
  d'être décodé reste une plage des octets source.
- **La réécriture coûte ce qui a changé.** L'arbre natif garde l'empreinte de
  chaque élément et ne l'efface que sur le chemin d'une modification jusqu'à
  la racine : un document inchangé est écrit tel quel, et un document modifié
  ne recalcule que ce chemin.
- **Une mise en page complète est du code Python** avec les moteurs natif et
  bibliothèque standard (l'indentation, le nettoyage des espaces de noms et
  l'écrivain d'ElementTree) : un nouveau document, ou un document écrit avec
  un `layout` explicite, s'écrit environ trois fois plus vite avec lxml.

## À quoi s'attendre

- **Les schémas sont chargés une fois par version.** libxml2 compile les XSD
  d'une version en 0,1 s environ. xmlschema demande environ 2 s et 20 à 25 Mio,
  et n'est chargé qu'en cas de besoin ; les validations suivantes dans le même
  processus réutilisent les deux. `ddi serve` charge la version par défaut au
  démarrage.
- **La lecture est légère ; l'index des modèles est paresseux.** `read_ddi`
  analyse le XML et s'arrête là. L'index de résolution est construit au premier
  usage de `DDIDocument.resolver`, ou d'emblée avec `build_index=True`.
- **`Document` sérialise à la demande.** `to_xml()`, `save()` et `validate()`
  réécrivent le modèle en XML à chaque appel. Regroupez vos modifications et
  sérialisez une seule fois.
- **Les références sont vérifiées par `save()` seulement.** Les références
  orphelines sont signalées par un unique `DDIReferenceWarning` à
  l'enregistrement.

## Documents volumineux

Parcourez le document en flux plutôt que de charger tout l'arbre :

```python
import ddi_l as ddi

for variable in ddi.iter_variables("large-study.xml"):
    print(variable.identifier)
```

`iter_variables` et `iter_questions` libèrent chaque élément dès qu'il est
converti en objet ; la mémoire reste de l'ordre d'un seul élément (environ
190 Kio au maximum pour l'étude de 5 000 variables ci-dessus). `iterparse_ddi`
diffuse n'importe quel type maintenable ; ne demandez que les types utiles, car
un élément est conservé jusqu'à ce que l'élément demandé le plus englobant soit
construit.

## Lint et conformité

- **Une exécution construit chaque index une fois.** Les règles d'un appel à
  `run_lint` ou à `run_profile`, et les vérifications d'un appel à `conform`,
  partagent ce qu'elles construisent à partir du document : ses éléments et
  leurs versions, la résolution des références, les liaisons et les
  conditions lues. Le profil `colectica-questionnaire` sur un export
  Colectica de 9 Mo (4 478 éléments) prend 2,0 s ; il prenait 6,1 s quand
  chaque règle construisait les siens.
- **Une passe suivante ne lit que ce qui a changé** (moteur natif). Les faits
  et les constats propres à chaque élément sont gardés sous l'empreinte de son
  contenu : relancer le lint sur le même document après une modification ne
  relit que les éléments modifiés. Sur cet export, le profil prend 0,8 s à la
  première passe et 0,13 s après une modification. Les règles qui suivent
  tout le flux le parcourent encore : c'est l'essentiel de ce qui reste.
- **Les chemins sont comptés, pas parcourus.** Un flux dont les pages se
  rejoignent après chacun de n filtres a 2^n chemins depuis l'instrument.
  `colectica.flow.read-before-computed` et `conform` atteignent chaque
  construction une fois par état qui peut changer ce qu'ils signalent : 20
  filtres enchaînés (un million de chemins) prennent quelques millisecondes,
  là où 16 prenaient 9,1 s dans `conform`. Un flux qui boucle sur lui-même
  est encore parcouru chemin par chemin.
- **Ce qu'un répondant atteint est résolu une fois par flux.**
  `colectica.flow.unreachable` donne au solveur une variable par
  construction, quel que soit le nombre de chemins qui y mènent, établit sans
  lui ce qu'il peut, et marque chaque construction qu'atteint chaque
  répondant qu'il trouve. 40 filtres enchaînés (2^40 chemins) prennent
  0,16 s ; un flux aléatoire de 300 constructions, 0,17 s.
- **La comparaison exacte des filtres coûte environ 5 ms par paire.** Avec
  l'extra `logic`, `conform` ne décide une paire de filtres que si leurs
  formes normales diffèrent, et chaque paire une fois : le fichier Pet se
  compare en environ 8 ms avec le solveur ou sans lui. Vingt filtres
  enchaînés prennent 33 ms avec lui et 16 ms sans.

## API HTTP

`ddi serve` traite au plus `--max-jobs` documents à la fois (par défaut : le
nombre de processeurs) et répond `503` avec `Retry-After` au-delà. La
validation détient le GIL : plus de tâches simultanées que de cœurs ajoute de
la mémoire, pas du débit. Pour monter en charge, lancez plusieurs processus
derrière un répartiteur de charge.

## Mesurer

Le dossier `benchmarks/` du dépôt contient des scripts reproductibles :

```bash
uv run python -m benchmarks.iterparse_bench
uv run python -m benchmarks.validation_report_bench
uv run python benchmarks/colectica_profile_bench.py EXPORT.xml
DDI_L_XML_BACKEND=native uv run python benchmarks/backends_bench.py EXPORT.xml
```

- [Benchmark de conversion de schémas](performance/schema_conversion.fr.md)
