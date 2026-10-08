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
ci-dessus. `schema_loader.set_validation_backend("python")` désactive la
vérification libxml2.

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
```

- [Benchmark de conversion de schémas](performance/schema_conversion.md)
