---
description: >-
  Échanger des métadonnées DDI entre ddi-l et d'autres outils, libres pour la
  plupart : outils XML et de schéma, données liées et SPARQL, JSON, tableurs,
  R, tout langage par HTTP, fichiers DDI Codebook d'outils comme Dataverse,
  outils DDI 3.2 et générateurs de questionnaires. Chaque section a un exemple
  à exécuter.
---

# Travailler avec d'autres outils

`ddi-l` lit DDI Lifecycle 3.1, 3.2 et 3.3, et écrit du XML DDI Lifecycle 3.3
standard, valide selon les schémas de la DDI Alliance. La plupart des outils
qui traitent le DDI peuvent donc échanger des fichiers avec lui. Cette page
montre comment, outil par outil, avec des exemples à exécuter. Chaque exemple
utilise une petite enquête fictive sur les animaux de compagnie.

## Ce que ddi-l échange

| Format | ddi-l lit | ddi-l écrit | À utiliser avec |
| --- | --- | --- | --- |
| XML DDI Lifecycle 3.3 (`DDIInstance`, `FragmentInstance`) | oui, et le modifie | oui | outils DDI 3.3, tout outil XML |
| XML DDI Lifecycle 3.1 et 3.2 | oui : validation, analyse (lint), accès aux éléments | non | outils DDI 3.1 et 3.2 |
| JSON (`ddi to-json`, `ddi from-json`) | oui | oui | applications web, bases de documents, tout langage |
| JSON-LD (vocabulaire DDI-RDF Discovery) | non | oui, un résumé | triplestores, SPARQL, catalogues de données |
| Fichiers CSV ou classeur Excel | oui | modèles vierges | tableurs, pandas, R |
| HTTP (`ddi serve`) | oui | oui | tout langage capable d'envoyer une requête |
| DDI Codebook 2.x | non | non | le convertir, [comme montré plus bas](#fichiers-ddi-codebook) |

## Tout outil XML

Un fichier écrit par `ddi-l` est du XML DDI ordinaire. Construisez l'enquête
une fois ; les sections suivantes la réutilisent :

```python
import ddi_l as ddi

doc = ddi.new_study(title="Pet survey", agency="example.org")
question = doc.add_question(
    text="How many pets live in your home?", label="Pet count question"
)
doc.add_variable(name="PetCount", question=question, label="Number of pets")
doc.save("pets.xml")
```

Toute bibliothèque XML peut le lire. Ceci n'utilise que la bibliothèque
standard de Python, pas `ddi-l` :

```python
import xml.etree.ElementTree as ET

NS = {"l": "ddi:logicalproduct:3_3", "r": "ddi:reusable:3_3"}
for variable in ET.parse("pets.xml").iter("{ddi:logicalproduct:3_3}Variable"):
    print(variable.findtext("l:VariableName/r:String", namespaces=NS))
# -> PetCount
```

Tout validateur de schéma peut le vérifier. `ddi-l` fournit les schémas de la
DDI Alliance, que `xmllint` (de la bibliothèque libre libxml2) peut utiliser
directement :

```bash
SCHEMA=$(python -c "from importlib.resources import files; print(files('ddi_l.schemas') / 'ddi' / 'v3_3' / 'instance_3_3.xsd')")
xmllint --noout --schema "$SCHEMA" pets.xml
# -> pets.xml validates
```

Il en va de même des processeurs XSLT, des bases XQuery et des éditeurs XML.

## Données liées : RDF et SPARQL

`ddi-l` écrit une étude en JSON-LD avec le
[vocabulaire DDI-RDF Discovery](https://rdf-vocabulary.ddialliance.org/discovery.html)
de la DDI Alliance : études, variables, questions, concepts et univers. Tout
outil RDF peut le charger. Avec la bibliothèque libre
[rdflib](https://github.com/RDFLib/rdflib) (`pip install rdflib`), une requête
SPARQL liste chaque variable et sa question :

```python
import json

from ddi_l.jsonld import to_jsonld
from rdflib import Graph

graph = Graph().parse(data=json.dumps(to_jsonld(doc)), format="json-ld")
rows = graph.query("""
    PREFIX disco: <http://rdf-vocabulary.ddialliance.org/discovery#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?name ?text WHERE {
        ?variable a disco:Variable ;
                  skos:prefLabel ?name ;
                  disco:question ?question .
        ?question disco:questionText ?text .
    }
""")
for name, text in rows:
    print(f"{name}: {text}")
# -> PetCount: How many pets live in your home?
```

En ligne de commande, `ddi to-jsonld pets.xml --output pets.jsonld` écrit le
même fichier, prêt pour un triplestore qui charge le JSON-LD, comme Apache
Jena.

Le vocabulaire décrit une étude pour qu'on la trouve : le JSON-LD est donc un
résumé. Le cheminement du questionnaire, les dispositions d'enregistrement et
le reste en sont absents, et il ne se reconvertit pas en XML DDI. Pour une
copie complète, utilisez JSON.

## JSON, pour les applications web et les autres langages

`ddi to-json` écrit tout le document en JSON, et `ddi from-json` le
retransforme en XML :

```bash
ddi to-json pets.xml --output pets.json
ddi from-json pets.json --output pets-again.xml
```

Le JSON garde la structure du XML, avec des noms qualifiés par leur espace de
noms comme clés : tout langage peut le lire et le modifier. Voir
[Recettes CLI](cli-recipes.fr.md) pour les autres options.

## Tableurs et data frames

Beaucoup d'équipes gardent leurs métadonnées dans des tableurs. `ddi-l`
charge un dossier de fichiers CSV ou un classeur Excel comme DDI : tout ce
qui écrit du CSV peut donc l'alimenter, que ce soit LibreOffice, Excel,
pandas, R ou l'export d'une base de données. Voir
[Charger du DDI depuis des tableurs](spreadsheet-import.fr.md) pour la
disposition et [les modèles](spreadsheet-templates.fr.md) pour commencer.
L'[exemple DDI Codebook](#fichiers-ddi-codebook) plus bas écrit de tels
tableaux à partir de la sortie d'un autre outil.

## R

R peut appeler `ddi-l` par le paquet libre
[reticulate](https://rstudio.github.io/reticulate/) : construire une étude à
partir d'un data frame, relire des variables dans un data frame, valider et
analyser. Voir [Utiliser ddi-l depuis R](r-users.fr.md).

## Tout langage, par HTTP

`ddi serve` lance une API HTTP (installez l'extra `server`) qui valide, analyse
et convertit : un outil écrit dans n'importe quel langage peut s'en servir
sans Python.

```bash
ddi serve --port 8080
curl --data-binary @pets.xml http://localhost:8080/v1/validate
```

L'API se décrit elle-même à `/schema/openapi.json` : des générateurs de
clients comme le logiciel libre OpenAPI Generator peuvent en tirer un client
pour votre langage. Voir [API HTTP](server.fr.md).

## Fichiers DDI Codebook

DDI Codebook (versions 2.x) est la norme DDI que beaucoup d'archives de
données emploient pour documenter les études et leurs variables. Par exemple,
le dépôt de données libre [Dataverse](https://github.com/IQSS/dataverse)
exporte du DDI Codebook 2.5. `ddi-l` ne lit pas le DDI Codebook, mais ses
variables, questions et catégories se reportent dans les
[tableaux](spreadsheet-import.fr.md), que `ddi-l` lit. Ceci convertit un petit
fichier DDI Codebook :

```python
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from ddi_l.tables import load_tables

Path("codebook.xml").write_text(
    """<codeBook xmlns="ddi:codebook:2_5" version="2.5">
  <dataDscr>
    <var name="PetCount">
      <labl>Number of pets</labl>
      <qstn><qstnLit>How many pets live in your home?</qstnLit></qstn>
    </var>
    <var name="PetKind">
      <labl>Kind of pet</labl>
      <qstn><qstnLit>What kind of pet do you have?</qstnLit></qstn>
      <catgry><catValu>1</catValu><labl>Dog</labl></catgry>
      <catgry><catValu>2</catValu><labl>Cat</labl></catgry>
    </var>
  </dataDscr>
</codeBook>
""",
    encoding="utf-8",
)

C = {"c": "ddi:codebook:2_5"}
tables = {"questions": [], "code_lists": [], "codes": [], "variables": []}
for var in ET.parse("codebook.xml").iterfind(".//c:var", C):
    name = var.get("name")
    label = var.findtext("c:labl", namespaces=C)
    categories = var.findall("c:catgry", C)
    code_list = f"{name}_codes" if categories else ""
    # Without categories, this sketch reads a variable as a whole number.
    kind = {"code_list": code_list, "numeric_type": "" if categories else "Integer"}
    tables["questions"].append(
        {
            "id": f"{name}_q",
            "name": name,
            "text@en": var.findtext("c:qstn/c:qstnLit", namespaces=C),
            "response": "code" if categories else "numeric",
            **kind,
        }
    )
    tables["variables"].append(
        {
            "id": name,
            "name": name,
            "label@en": label,
            "question": f"{name}_q",
            "representation": "code" if categories else "numeric",
            **kind,
        }
    )
    if categories:
        tables["code_lists"].append({"id": code_list, "label@en": label})
        for category in categories:
            tables["codes"].append(
                {
                    "code_list": code_list,
                    "value": category.findtext("c:catValu", namespaces=C),
                    "label@en": category.findtext("c:labl", namespaces=C),
                }
            )

folder = Path("from-codebook")
folder.mkdir(exist_ok=True)
(folder / "settings.csv").write_text(
    "setting,value\nagency,example.org\n", encoding="utf-8"
)
for table, rows in tables.items():
    with open(folder / f"{table}.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

study = load_tables(folder).to_study("Pet survey")
print(study.validate())  # -> []
study.save("pets-lifecycle.xml")
```

L'exemple reprend les noms, les libellés, le texte des questions et les
catégories. Les fichiers Codebook varient d'un outil à l'autre : vérifiez ce
que le vôtre écrit (valeurs manquantes, types de valeurs, plusieurs langues)
et ajoutez les colonnes correspondantes, que
[Charger du DDI depuis des tableurs](spreadsheet-import.fr.md) énumère.

## Outils DDI 3.1 et 3.2

Certains outils écrivent du DDI 3.2. Par exemple, l'éditeur de questionnaires
libre de CLOSER, [Archivist](https://github.com/CLOSER-Cohorts/archivist),
documente les questionnaires en DDI Lifecycle 3.2, selon CLOSER. `ddi-l`
valide et analyse ces fichiers : `ddi validate` lit la version dans le fichier.

```bash
ddi validate archivist-export.xml
```

En Python, `read_ddi()` ouvre chacune des trois versions et donne accès aux
éléments du XML. `open_ddi()`, avec ses modèles typés, est pour le DDI 3.3 et
le dit quand on lui donne une version antérieure.

```python
legacy = ddi.read_ddi("archivist-export.xml")
print(legacy.validate())  # -> []
```

## Générateurs de questionnaires

Certains outils libres transforment la description DDI d'un questionnaire en
questionnaires pour les intervieweurs et les répondants. Par exemple,
[Eno](https://github.com/InseeFr/Eno), de l'Insee, produit des questionnaires
web, téléphone, face-à-face et papier à partir du DDI, et son outil de
conception [Pogues](https://github.com/InseeFr/Pogues) travaille avec lui.
Avant de confier un questionnaire à un tel outil, vérifiez-le avec `ddi-l` :
`ddi validate`, `ddi lint`, et `ddi conform` pour le comparer à une
spécification (voir
[Vérifier un questionnaire par rapport à une spécification](spec-conformance.fr.md)).
Vérifiez d'abord quelle version du DDI l'outil attend.

## Colectica

Les outils de Colectica sont commerciaux. `ddi-l` lit et écrit les fichiers
`FragmentInstance` qu'exporte Colectica Designer ; voir
[Travailler avec les exports Colectica](colectica.fr.md). `ddi-l` n'est ni
affilié à Colectica ni approuvé par elle.

## Trouver d'autres outils

La DDI Alliance tient un catalogue des outils DDI, filtrable par licence, à
[ddialliance.org/resources/tools](https://ddialliance.org/resources/tools).
Avant d'échanger des fichiers avec un outil, vérifiez quel DDI il emploie :
Codebook, Lifecycle 3.x, ou le plus récent Cross-Domain Integration
(DDI-CDI), que `ddi-l` ne lit pas.

## Avant d'échanger un fichier

- **Validez-le et analysez-le.** `ddi validate` et `ddi lint` trouvent la
  plupart des problèmes avant l'autre outil. Voir
  [Valider et analyser le contenu DDI](validation.fr.md).
- **Utilisez la même version du DDI des deux côtés.** `ddi-l` écrit du 3.3.
- **Utilisez une agence enregistrée.** Les ID d'agence viennent du
  [registre des agences](https://ddialliance.org/ddi-agency-id-registry) de
  la DDI Alliance : les éléments de deux organisations ne partagent donc pas
  d'URN.
- **Gardez les identifiants et les versions stables.** Incrémentez la version
  d'un élément quand vous le modifiez, plutôt que de lui donner un nouvel ID :
  les autres outils voient ainsi le même élément.
- **Essayez un aller-retour.** Faites passer un fichier par l'autre outil puis
  revenir, et comparez. `ddi-l` garde ce qu'il ne modélise pas (paires
  d'attributs utilisateur, espaces de noms personnalisés) ; un autre outil peut
  le perdre.
