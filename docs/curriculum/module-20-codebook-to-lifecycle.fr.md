---
description: >-
  Module 20 facultatif du cours ddi-l : convertir en DDI-Lifecycle les
  fichiers DDI-Codebook de plusieurs cycles d'enquête, en écrivant une seule
  fois chaque question, liste de codes et univers que les livres de codes
  répètent, et reprendre ce qui rend le résultat FAIR.
---

# Module 20 (facultatif) : De DDI-Codebook à DDI-Lifecycle, pensé pour la réutilisation

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Expliquer pourquoi un fichier DDI-Codebook ne peut pas partager
      une question, une liste de codes ou un univers avec une autre étude, et
      comment DDI-Lifecycle permet à chaque cycle d'une enquête de renvoyer au
      même élément.
    - **O2.** Lire des fichiers DDI-Codebook, version 2.5 ou 2.6, avec
      `xml.etree.ElementTree` de Python : la citation et les fichiers de
      données de chaque étude, et le nom, le libellé, la question et les
      catégories de chaque variable.
    - **O3.** Trouver ce que les livres de codes répètent (la même question,
      les mêmes catégories, le même univers) et décider quand une répétition
      est le même élément et quand un changement de formulation en fait un
      autre.
    - **O4.** Écrire les tables de métadonnées pour que chaque élément répété
      y figure une seule fois, avec un renvoi de chaque variable qui l'emploie,
      et charger plusieurs cycles comme une série dans un fichier
      DDI-Lifecycle valide selon le schéma.
    - **O5.** Reprendre ce qui rend le résultat facile à trouver et à
      réutiliser : le DOI de chaque cycle, une licence lisible par un
      programme, une trace de la conversion et un libellé pour chaque
      élément.

**Prérequis :** [Module 9](module-09-code-lists.fr.md) et
[Module 15](module-15-update-and-version.fr.md). Le
[Module 1](module-01-what-is-metadata.fr.md#4-comment-ddi-rend-les-donnees-fair)
présente les principes FAIR que ce module met en pratique. Ce module est
facultatif : le projet de synthèse n'en a pas besoin.

**Durée :** 60 min en autonomie / 75 min avec instructeur.

**Nouveau dans ce module :** les fichiers DDI-Codebook (`stdyDscr`,
`fileDscr`, `dataDscr`, `var`, `catgry`), `xml.etree.ElementTree`,
`load_tables()`, `to_fragment()`, les tables `groups` et `datasets`, les
colonnes `identifier`, `copyright` et `license` de la table `studies`, et
`run_lint()`.

---

## 1. Un livre de codes par étude, rien de partagé

Beaucoup d'archives de données décrivent leurs fonds en **DDI-Codebook**
(DDI-C), la première norme de la DDI Alliance ; ce cours enseigne
**DDI-Lifecycle** (DDI-L). La différence qui compte ici, c'est ce que
chacune permet de partager :

| | DDI-Codebook | DDI-Lifecycle |
| --- | --- | --- |
| Un fichier contient | Une étude, complète en elle-même | N'importe quels éléments, d'une étude ou de plusieurs |
| Une question, une liste de codes | Écrite dans chaque variable qui l'emploie | Un élément à part entière, auquel les variables renvoient |
| Identifiants | Propres au fichier, comme `ID="V1"` | Un URN, `urn:ddi:agence:id:version`, auquel tout fichier peut renvoyer |
| Une enquête menée chaque année | Un livre de codes par année, qui répète chaque fois les mêmes questions et catégories | Une question et une liste de codes, auxquelles renvoient les variables de chaque année |

Un livre de codes ne peut pas renvoyer hors de lui-même : celui de chaque
cycle recopie donc tout. Rien dans les fichiers ne dit que `PetKind` pose la
même question en 2022 et en 2023 : une personne doit les comparer. Si on
corrige le libellé d'une catégorie, il faut le corriger dans chaque livre de
codes.

Convertir en DDI-Lifecycle un livre de codes à la fois garderait ces copies,
chacune avec son propre identifiant. Ce module convertit en pensant à la
réutilisation : il lit d'abord tous les cycles, trouve ce qu'ils répètent, et
écrit une seule fois chaque élément répété.

`ddi-l` lit et écrit seulement DDI-Lifecycle. Vous lisez les livres de codes
avec la bibliothèque standard de Python et en passez le contenu à `ddi-l`
par les [tables de métadonnées](../spreadsheet-import.fr.md).

## 2. Deux cycles, deux livres de codes

Une enquête inventée a eu lieu en 2022 et en 2023, et son archive a écrit un
livre de codes par cycle, dans la même disposition chaque année. La fonction
ci-dessous les écrit, pour que vous voyiez ce qui change d'une année à
l'autre. Les deux fichiers sont valides selon le schéma DDI-Codebook 2.5 de
la DDI Alliance.

```python
from pathlib import Path

VARIABLES = {
    "PetCount": """
    <var ID="V1" name="PetCount" files="F1" dcml="0">
      <labl>Number of pets</labl>
      <qstn>
        <qstnLit>{count_question}</qstnLit>
      </qstn>
      <varFormat type="numeric"/>
    </var>""",
    "PetKind": """
    <var ID="V2" name="PetKind" files="F1">
      <labl>Kind of pet</labl>
      <qstn>
        <qstnLit>What kind of pet do you have?</qstnLit>
      </qstn>{kinds}
      <varFormat type="numeric"/>
    </var>""",
    "SecondPetKind": """
    <var ID="V3" name="SecondPetKind" files="F1">
      <labl>Kind of second pet</labl>
      <qstn>
        <qstnLit>What kind is your second pet?</qstnLit>
      </qstn>{kinds}
      <varFormat type="numeric"/>
    </var>""",
}
KINDS = "".join(
    f"""
      <catgry{' missing="Y"' if value == "9" else ""}>
        <catValu>{value}</catValu>
        <labl>{label}</labl>
      </catgry>"""
    for value, label in [
        ("1", "Dog"),
        ("2", "Cat"),
        ("3", "Other pet"),
        ("9", "Don't know"),
    ]
)


def write_codebook(year, doi, count_question, names):
    """Le livre de codes d'un cycle, dans la même disposition chaque année."""
    variables = "".join(
        VARIABLES[name].format(count_question=count_question, kinds=KINDS)
        for name in names
    )
    Path(f"pets-{year}.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<codeBook xmlns="ddi:codebook:2_5" version="2.5">
  <stdyDscr>
    <citation>
      <titlStmt>
        <titl>Pet Ownership Survey {year}</titl>
        <IDNo agency="DOI">{doi}</IDNo>
      </titlStmt>
      <rspStmt>
        <AuthEnty>Example Research Institute</AuthEnty>
      </rspStmt>
      <distStmt>
        <distrbtr>Example Data Archive</distrbtr>
        <distDate date="{year}-09-15">15 September {year}</distDate>
      </distStmt>
    </citation>
    <stdyInfo>
      <sumDscr>
        <anlyUnit>Households</anlyUnit>
        <universe>Households with at least one pet</universe>
        <dataKind>Survey data</dataKind>
      </sumDscr>
    </stdyInfo>
    <dataAccs>
      <useStmt>
        <conditions>Free to reuse with attribution (CC BY 4.0).</conditions>
      </useStmt>
    </dataAccs>
  </stdyDscr>
  <fileDscr ID="F1">
    <fileTxt>
      <fileName>pets-{year}.csv</fileName>
    </fileTxt>
  </fileDscr>
  <dataDscr>{variables}
  </dataDscr>
</codeBook>
""",
        encoding="utf-8",
    )


write_codebook(
    2022,
    "10.5072/FK2PETS22",
    "How many pets live in your home?",
    ["PetCount", "PetKind"],
)
write_codebook(
    2023,
    "10.5072/FK2PETS23",
    "How many pets live in your household?",
    ["PetCount", "PetKind", "SecondPetKind"],
)
```

Ouvrez `pets-2022.xml` et `pets-2023.xml` côte à côte. D'une année à
l'autre :

- `PetKind` pose la même question, avec les mêmes quatre catégories ;
- `PetCount` est formulée autrement : « home » est devenu « household » ;
- 2023 ajoute `SecondPetKind`, une nouvelle question avec les mêmes
  catégories que `PetKind`, recopiées une fois de plus.

Les deux livres de codes contiennent cinq questions et trois copies des
quatre catégories. `10.5072` est le préfixe DOI réservé aux essais : ces DOI
ne mènent nulle part ; le livre de codes d'une archive porte le vrai DOI de
l'étude.

## 3. Lire un livre de codes

Chaque élément d'un livre de codes est dans son espace de noms,
`ddi:codebook:2_5` pour la version 2.5 et `ddi:codebook:2_6` pour la 2.6. La
fonction le lit sur l'élément racine, et lit donc les deux versions ; elle
renvoie ce dont la conversion a besoin sous forme de valeurs Python simples :

```python
import xml.etree.ElementTree as ET


def text(element, path, C):
    """Le texte au chemin path sous element, espaces nettoyés, ou une chaîne vide."""
    found = element.findtext(path, namespaces=C) or ""
    return " ".join(found.split())


def read_codebook(path):
    """Ce que dit un livre de codes : son étude, ses fichiers et ses variables."""
    root = ET.parse(path).getroot()
    C = {"c": root.tag[1:].split("}")[0]}
    study = root.find("c:stdyDscr", C)
    id_no = study.find("c:citation/c:titlStmt/c:IDNo", C)
    variables = []
    for var in root.iterfind("c:dataDscr/c:var", C):
        categories = tuple(
            (text(c, "c:catValu", C), text(c, "c:labl", C), c.get("missing") == "Y")
            for c in var.iterfind("c:catgry", C)
        )
        variables.append(
            {
                "name": var.get("name"),
                "label": text(var, "c:labl", C),
                "question": text(var, "c:qstn/c:qstnLit", C),
                "file": var.get("files"),
                "format": var.find("c:varFormat", C).get("type"),
                "decimals": var.get("dcml", "0"),
                "categories": categories,
            }
        )
    return {
        "title": text(study, "c:citation/c:titlStmt/c:titl", C),
        "identifier": id_no.text.strip(),
        "identifier_agency": id_no.get("agency"),
        "creator": text(study, "c:citation/c:rspStmt/c:AuthEnty", C),
        "publisher": text(study, "c:citation/c:distStmt/c:distrbtr", C),
        "published": study.find("c:citation/c:distStmt/c:distDate", C).get("date"),
        "analysis_unit": text(study, "c:stdyInfo/c:sumDscr/c:anlyUnit", C),
        "kind_of_data": text(study, "c:stdyInfo/c:sumDscr/c:dataKind", C),
        "universe": text(study, "c:stdyInfo/c:sumDscr/c:universe", C),
        "files": {
            f.get("ID"): text(f, "c:fileTxt/c:fileName", C)
            for f in root.iterfind("c:fileDscr", C)
        },
        "variables": variables,
    }


waves = {year: read_codebook(f"pets-{year}.xml") for year in (2022, 2023)}
for year, wave in waves.items():
    print(year, wave["identifier"], [var["name"] for var in wave["variables"]])
```

**Résultat attendu :**

```text
2022 10.5072/FK2PETS22 ['PetCount', 'PetKind']
2023 10.5072/FK2PETS23 ['PetCount', 'PetKind', 'SecondPetKind']
```

`find()` renvoie le premier élément qui correspond, ou `None` ;
`findtext()` son texte ; `iterfind()` parcourt chaque correspondance. Les
catégories d'une variable deviennent un tuple de `(valeur, libellé,
manquante)`, que Python peut comparer à celui d'une autre variable en une
seule opération.

## 4. Trouver ce que les livres de codes répètent

Regroupez les variables de tous les cycles selon ce qu'elles partagent : leur
question, leurs catégories, et l'univers de leur étude. Deux variables posent
la même question quand sa formulation et ses réponses concordent toutes deux :

```python
def question_key(var):
    """Une question : sa formulation, et ses catégories ou sinon son format."""
    return var["question"], var["categories"] or (var["format"], var["decimals"])


def repeats(waves):
    """Les questions, listes de codes et univers des cycles, et qui emploie chacun."""
    questions = {}  # (formulation, réponses) -> les variables qui la posent
    code_lists = {}  # catégories -> les variables qui les emploient
    universes = {}  # formulation -> les cycles qu'il couvre
    for year, wave in waves.items():
        universes.setdefault(wave["universe"], []).append(year)
        for var in wave["variables"]:
            where = f"{var['name']} {year}"
            questions.setdefault(question_key(var), []).append(where)
            if var["categories"]:
                code_lists.setdefault(var["categories"], []).append(where)
    return questions, code_lists, universes


questions, code_lists, universes = repeats(waves)
print(len(questions), len(code_lists), len(universes))  # -> 4 1 1
for (wording, _), users in questions.items():
    print(users, wording)
print(list(code_lists.values()))
```

**Résultat attendu :**

```text
4 1 1
['PetCount 2022'] How many pets live in your home?
['PetKind 2022', 'PetKind 2023'] What kind of pet do you have?
['PetCount 2023'] How many pets live in your household?
['SecondPetKind 2023'] What kind is your second pet?
[['PetKind 2022', 'PetKind 2023', 'SecondPetKind 2023']]
```

Les cinq questions des livres de codes en font quatre distinctes ; trois
copies des catégories font une liste de codes ; et les deux cycles couvrent
le même univers.

Les réponses font partie de la question parce que chaque variable tient ses
réponses de sa question (section 5). Si le cycle 2023 avait ajouté une
catégorie à *What kind of pet do you have?*, les deux cycles poseraient deux
questions de même formulation, chacune avec sa liste de codes ; regroupée
selon la seule formulation, `PetKind 2023` aurait reçu les catégories de 2022.

Comparer des formulations est une règle qu'un programme peut appliquer, mais
dire que deux questions sont la même est une décision. Les deux formulations
de `PetCount` diffèrent d'un mot : le convertisseur les garde séparées.
« Home » et « household » comptent-ils les mêmes animaux ? C'est au
responsable de l'enquête de le dire. Si oui, faites correspondre une
formulation à l'autre avant de convertir (exercice 4) ; si le changement
compte un peu, les versions du Module 15 servent à le consigner.

## 5. Écrire chaque élément une seule fois

Chaque question, liste de codes et univers distinct reçoit une ligne, avec un
id (`Q1`, `CL1`, `U1`) que nomme chaque variable qui l'emploie. Le reste suit
les cycles :

- un **groupe** de type `Series` contient les études ;
- chaque cycle est une **étude**, avec sa citation ;
- le fichier de données de chaque cycle est un **jeu de données** de son
  étude ;
- chaque variable reçoit une ligne par cycle, et nomme son jeu de données,
  sa question et son univers.

```python
def response(var, code_list_ids):
    """Les colonnes de questions qui disent quel genre de réponse la variable note."""
    if var["categories"]:
        return {"response": "code", "code_list": code_list_ids[var["categories"]]}
    if var["format"] == "numeric":
        decimal = var["decimals"] != "0"
        return {
            "response": "numeric",
            "numeric_type": "Decimal" if decimal else "Integer",
        }
    return {"response": "text"}


def build_tables(waves):
    """Les tables de tous les cycles, où chaque élément répété est écrit une fois."""
    questions, code_lists, universes = repeats(waves)
    question_ids = {key: f"Q{n}" for n, key in enumerate(questions, 1)}
    code_list_ids = {cats: f"CL{n}" for n, cats in enumerate(code_lists, 1)}
    universe_ids = {wording: f"U{n}" for n, wording in enumerate(universes, 1)}
    variables = [
        (year, var) for year, wave in waves.items() for var in wave["variables"]
    ]

    tables = {
        "settings": [{"setting": "agency", "value": "example.org"}],
        "groups": [
            {
                "id": "PETS",
                "title@en": "Pet Ownership Survey",
                "type": "Series",
                "studies": "|".join(f"PETS{year}" for year in waves),
            }
        ],
        "universes": [
            {"id": uid, "label@en": wording} for wording, uid in universe_ids.items()
        ],
        "code_lists": [],
        "codes": [],
        "questions": [],
        "studies": [],
        "datasets": [],
        "variables": [],
    }
    for categories, list_id in code_list_ids.items():
        first = next(var for _, var in variables if var["categories"] == categories)
        tables["code_lists"].append({"id": list_id, "label@en": first["label"]})
        for value, label, missing in categories:
            tables["codes"].append(
                {
                    "code_list": list_id,
                    "value": value,
                    "label@en": label,
                    "missing": "true" if missing else "",
                }
            )
    for key, question_id in question_ids.items():
        first = next(var for _, var in variables if question_key(var) == key)
        tables["questions"].append(
            {"id": question_id, "text@en": key[0], **response(first, code_list_ids)}
        )
    for year, wave in waves.items():
        tables["studies"].append(
            {
                "id": f"PETS{year}",
                "title@en": wave["title"],
                "identifier": wave["identifier"],
                "identifier_agency": wave["identifier_agency"],
                "creator": wave["creator"],
                "publisher": wave["publisher"],
                "publication_date": wave["published"],
                "analysis_unit": wave["analysis_unit"],
                "kind_of_data": wave["kind_of_data"],
                "universe": universe_ids[wave["universe"]],
            }
        )
        for file_id, file_name in wave["files"].items():
            tables["datasets"].append(
                {
                    "id": f"{file_id}_{year}",
                    "name": file_name,
                    "label@en": f"{wave['title']} data",
                    "file": file_name,
                    "study": f"PETS{year}",
                }
            )
    for year, var in variables:
        tables["variables"].append(
            {
                "id": f"{var['name']}_{year}",
                "name": var["name"],
                "label@en": var["label"],
                "question": question_ids[question_key(var)],
                "dataset": f"{var['file']}_{year}",
                "universe": universe_ids[waves[year]["universe"]],
            }
        )
    return tables


tables = build_tables(waves)
print(len(tables["questions"]), len(tables["codes"]), len(tables["variables"]))
# -> 4 4 5
```

Une variable prend la réponse de sa question : `PetKind` reçoit ainsi la
liste de codes sans la nommer deux fois. Un livre de codes dit seulement
`numeric` ou `character` ; c'est `dcml="0"`, aucune décimale, qui fait de
`PetCount` un nombre entier. L'`IDNo` du livre de codes et son `agency` vont
dans les colonnes `identifier` et `identifier_agency`, qui écrivent le DOI
dans la citation de l'étude.

## 6. Charger et vérifier la réutilisation

Écrivez chaque table dans un fichier CSV, chargez le dossier et écrivez un
seul fichier DDI-Lifecycle pour les deux cycles :

```python
import csv

from ddi_l.tables import load_tables


def write_tables(folder, tables):
    """Un fichier CSV par table, avec chaque colonne qu'une de ses lignes utilise."""
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    for name, rows in tables.items():
        headers = list(dict.fromkeys(key for row in rows for key in row))
        with open(folder / f"{name}.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)


write_tables("pets-tables", tables)
loaded = load_tables("pets-tables")
fragment = loaded.to_fragment()
print(fragment.validate())  # -> []
fragment.save("pets-lifecycle.xml")

asked_2022 = loaded.get("variables", "PetKind_2022").question_references[0]
asked_2023 = loaded.get("variables", "PetKind_2023").question_references[0]
print(asked_2022.urn == asked_2023.urn)  # -> True
print(fragment.get_top_level_reference().type_of_object)  # -> Group
```

`to_fragment()` écrit une `FragmentInstance` DDI-Lifecycle, un fragment par
élément, avec la série comme élément de premier niveau. `to_study()`, qui
écrit une étude comme les documents des modules précédents, n'a pas de place
pour une série ni pour plusieurs études.

`PetKind` en 2022 et `PetKind` en 2023 renvoient maintenant à la même
question par son URN, et trois variables renvoient à la même liste de codes.
Un troisième cycle ajouterait son étude, son fichier de données et ses
variables, et renverrait de nouveau aux mêmes éléments. Corriger le libellé
d'une catégorie se fait désormais une fois, à un seul endroit.

## 7. Facile à trouver et à réutiliser

Le
[Module 1](module-01-what-is-metadata.fr.md#4-comment-ddi-rend-les-donnees-fair)
a montré comment DDI soutient les principes FAIR. Une conversion est le
moment de reprendre, ou d'ajouter, ce que les livres de codes contiennent de
façon lâche :

- **Un identifiant pérenne.** Le DOI de chaque cycle, tiré de son `IDNo`, est
  maintenant dans la citation de son étude comme `r:InternationalIdentifier`,
  et chaque élément a un URN. Les URN portent `example.org`, l'agence
  inventée de ce cours ; une vraie agence est enregistrée auprès de la DDI
  Alliance, comme l'explique le [Module 3](module-03-first-study.fr.md).
- **Une licence lisible par un programme.** DDI-Codebook 2.5 n'a pas
  d'élément de licence : les conditions d'utilisation sont du texte libre
  dans `useStmt`. La version 2.6 ajoute un élément `license`, dont l'attribut
  `URI` contient l'adresse web de la licence. En DDI-Lifecycle, la colonne
  `license` l'écrit comme `dcterms:license` dans la citation de l'étude.
  Donnez-lui l'adresse, pas le nom.
- **Un libellé pour chaque élément.** Les livres de codes donnaient un
  libellé aux variables, mais pas aux questions, et un libellé est ce
  qu'affichent un catalogue ou une banque de questions. `run_lint()` exécute
  sur un fragment les vérifications de `ddi lint`, et les trouve.

La licence et les libellés vont dans les tables, pour que chaque conversion
suivante les garde :

```python
from ddi_l.lint import run_lint

print(len(run_lint(fragment)))  # -> 4
for row in tables["studies"]:
    row["license"] = "https://creativecommons.org/licenses/by/4.0/"
for question in tables["questions"]:
    asker = next(v for v in tables["variables"] if v["question"] == question["id"])
    question["label@en"] = asker["label@en"]
write_tables("pets-tables", tables)
```

Les quatre constats étaient des `ddi.maintainable.labels`, un par question.

- **Une trace de la conversion.** Consignez la provenance des métadonnées
  comme justification de version de chaque étude, comme au Module 15. Les
  tables vous donnent chaque élément avant de l'écrire : vous pouvez l'y
  ajouter. Vérifiez ensuite le résultat et enregistrez-le :

```python
from ddi_l.models.base import InternationalString, VersionRationale

loaded = load_tables("pets-tables")
for year in waves:
    loaded.get("studies", f"PETS{year}").version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text=f"Converti du fichier DDI-Codebook 2.5 pets-{year}.xml."
                )
            ]
        )
    )
fragment = loaded.to_fragment()
print(fragment.validate())  # -> []
print(run_lint(fragment))  # -> []
fragment.save("pets-lifecycle.xml")
```

## 8. Ce que cette conversion laisse de côté

- **Une réutilisation au-delà des questions et des listes de codes.** Les
  deux variables `PetKind` pourraient aussi partager une variable
  représentée, qui dit qu'elles notent la même chose de la même façon : voyez
  la table `represented_variables` du
  [guide des tables de métadonnées](../spreadsheet-import.fr.md).
- **Plusieurs langues.** Un livre de codes peut répéter `titl` ou `labl` avec
  `xml:lang` ; donnez à chaque langue sa colonne, comme `label@fr`.
- **Statistiques et méthodologie.** Le `sumStat` d'une variable (fréquences,
  moyennes) décrit les données plutôt que l'étude et reste à l'archive ;
  `method/dataColl` correspond à la table `methodologies`.

Avant de convertir de vrais livres de codes, dressez la liste des éléments
qu'ils emploient, et comparez les cycles avant de décider de ce qui est
pareil : chaque outil et chaque équipe écrit le DDI-Codebook à sa façon.

---

## Exercices

1. **(O1)** Une collègue convertit chaque livre de codes dans son propre
   fichier DDI-Lifecycle, un à la fois. Les deux fichiers sont valides. Que
   perdent-ils par rapport à la conversion de ce module ?

    ??? success "Réponse"

        Chaque fichier reçoit sa propre question `PetKind` et sa propre liste
        de codes, avec des URN différents : rien ne dit que 2022 et 2023 ont
        posé la même question avec les mêmes catégories, ce dont la
        comparaison des cycles a justement besoin. Un libellé de catégorie
        corrigé doit l'être de nouveau dans chaque fichier. Convertir tous
        les cycles ensemble, en écrivant une seule fois chaque élément
        répété, garde ce savoir dans les métadonnées.

2. **(O2)** Faites une copie DDI-Codebook 2.6 de `pets-2023.xml` : changez
   l'espace de noms et la version, et ajoutez un élément `license` comme
   premier enfant de `dataAccs`. Lisez son espace de noms sur la racine, et
   affichez-le avec l'`URI` de la licence.

    **Résultat attendu :**

    ```text
    ddi:codebook:2_6 https://creativecommons.org/licenses/by/4.0/
    ```

    ??? success "Réponse"

        ```python
        source = Path("pets-2023.xml").read_text(encoding="utf-8")
        source = source.replace(
            'xmlns="ddi:codebook:2_5" version="2.5"',
            'xmlns="ddi:codebook:2_6" version="2.6"',
        )
        source = source.replace(
            "    <dataAccs>\n",
            "    <dataAccs>\n"
            '      <license URI="https://creativecommons.org/licenses/by/4.0/">'
            "CC BY 4.0</license>\n",
        )
        Path("pets-2023-2.6.xml").write_text(source, encoding="utf-8")

        root_26 = ET.parse("pets-2023-2.6.xml").getroot()
        C_26 = {"c": root_26.tag[1:].split("}")[0]}
        licence = root_26.find("c:stdyDscr/c:dataAccs/c:license", C_26)
        print(C_26["c"], licence.get("URI"))
        # -> ddi:codebook:2_6 https://creativecommons.org/licenses/by/4.0/
        ```

        `read_codebook()` lit ce fichier tel quel, parce qu'elle prend
        l'espace de noms sur la racine. Un convertisseur peut prendre la
        licence dans `license/@URI` quand un livre de codes en a une, et la
        demander à une personne quand il n'a que le texte de `useStmt`.

3. **(O3, O4)** L'enquête a de nouveau lieu en 2024, avec le questionnaire
   de 2023. Écrivez son livre de codes avec `write_codebook()`, ajoutez-le à
   `waves`, et affichez le nombre de questions et de listes de codes
   distinctes, puis le nombre de lignes de `questions` et de `variables` dans
   les tables reconstruites.

    **Résultat attendu :**

    ```text
    4 1
    4 8
    ```

    ??? success "Réponse"

        ```python
        write_codebook(
            2024,
            "10.5072/FK2PETS24",
            "How many pets live in your household?",
            ["PetCount", "PetKind", "SecondPetKind"],
        )
        waves[2024] = read_codebook("pets-2024.xml")
        questions, code_lists, universes = repeats(waves)
        print(len(questions), len(code_lists))  # -> 4 1
        tables = build_tables(waves)
        print(len(tables["questions"]), len(tables["variables"]))  # -> 4 8
        ```

        Le troisième cycle ajoute une étude, un fichier de données et trois
        variables, et pas une seule question ni liste de codes : ses
        variables renvoient aux éléments que les deux premiers cycles ont
        déjà.

4. **(O3)** Le responsable de l'enquête décide que « How many pets live in
   your home? » et « How many pets live in your household? » demandent la
   même chose. Faites correspondre la formulation de 2023 à celle de 2022
   dans chaque cycle, reconstruisez et chargez les tables, et vérifiez que
   `PetCount` en 2022 et en 2024 posent maintenant la même question.

    **Résultat attendu :**

    ```text
    3
    True
    ```

    ??? success "Réponse"

        ```python
        same = {"How many pets live in your household?": "How many pets live in your home?"}
        for wave in waves.values():
            for var in wave["variables"]:
                var["question"] = same.get(var["question"], var["question"])
        tables = build_tables(waves)
        print(len(tables["questions"]))  # -> 3
        write_tables("pets-tables", tables)
        loaded = load_tables("pets-tables")
        first = loaded.get("variables", "PetCount_2022").question_references[0]
        last = loaded.get("variables", "PetCount_2024").question_references[0]
        print(first.urn == last.urn)  # -> True
        ```

        La décision est consignée à un seul endroit, le dictionnaire `same`,
        que le responsable peut relire. La question garde la formulation de
        2022 ; si celle de 2023 doit aussi être gardée, une nouvelle version
        de la question (Module 15) consigne plutôt le changement.

5. **(O5)** Donnez à chaque variable et à chaque question un libellé
   français (`label@fr`), avec *Nombre d'animaux*, *Type d'animal* et *Type
   du deuxième animal*. Chargez les tables, et affichez le libellé français de
   `PetKind_2023` et le nombre de constats du linter.

    **Résultat attendu :**

    ```text
    Type d'animal
    0
    ```

    ??? success "Réponse"

        ```python
        french = {
            "PetCount": "Nombre d'animaux",
            "PetKind": "Type d'animal",
            "SecondPetKind": "Type du deuxième animal",
        }
        for variable in tables["variables"]:
            variable["label@fr"] = french[variable["name"]]
        for question in tables["questions"]:
            asker = next(v for v in tables["variables"] if v["question"] == question["id"])
            question["label@en"] = asker["label@en"]
            question["label@fr"] = french[asker["name"]]
        write_tables("pets-tables", tables)

        loaded = load_tables("pets-tables")
        labels = loaded.get("variables", "PetKind_2023").labels
        print(next(label.text for label in labels if label.lang == "fr"))
        # -> Type d'animal
        print(len(run_lint(loaded.to_fragment())))  # -> 0
        ```

        L'en-tête de colonne porte la langue : `label@en` et `label@fr`
        deviennent un seul libellé à deux chaînes. Comme chaque question est
        écrite une seule fois, elle est traduite une seule fois, pour tous
        les cycles.

---

## Quiz

???+ question "Question 1 (O1) : Pourquoi deux fichiers DDI-Codebook ne peuvent-ils pas partager les catégories de PetKind ?"
    **A.** DDI-Codebook n'a pas de catégories.

    **B.** Un livre de codes est complet en lui-même : ses identifiants sont propres au fichier, et rien en lui ne peut renvoyer à un élément d'un autre fichier.

    **C.** Les catégories sont dans des langues différentes.

    **D.** Ils le peuvent, avec `catgry`.

    ??? success "Réponse"
        **B.** Le livre de codes de chaque cycle réécrit les catégories. En
        DDI-Lifecycle, la liste de codes est un élément avec un URN, auquel
        renvoient les variables de chaque cycle.

???+ question "Question 2 (O3) : Les livres de codes de 2022 et de 2023 formulent une question autrement. Que fait le convertisseur de ce module ?"
    **A.** Il les fusionne, puisque la variable a le même nom.

    **B.** Il garde deux questions, et laisse la décision de les fusionner au responsable de l'enquête, qui peut faire correspondre une formulation à l'autre.

    **C.** Il s'arrête sur une erreur.

    **D.** Il ne garde que la formulation la plus récente.

    ??? success "Réponse"
        **B.** Un nom de variable n'est pas une question. Un programme peut
        comparer des formulations, mais dire que deux formulations demandent
        la même chose est une décision.

???+ question "Question 3 (O4) : Dans les tables, qu'est-ce qui rattache PetKind_2023 à l'étude de 2023 ?"
    **A.** Son nom.

    **B.** Sa colonne `dataset` : le fichier de données de 2023, dont la `study` est `PETS2023`.

    **C.** Sa question.

    **D.** L'ordre des lignes.

    ??? success "Réponse"
        **B.** La question est partagée par les deux cycles ; le fichier de
        données appartient à une étude, et la variable est une colonne de ce
        fichier.

???+ question "Question 4 (O4) : Deux cycles, trois variables avec les mêmes quatre catégories. Combien de listes de codes le fichier DDI-Lifecycle contient-il ?"
    **A.** Trois.

    **B.** Une, à laquelle renvoient les trois variables.

    **C.** Deux, une par cycle.

    **D.** Aucune : les catégories restent dans les variables.

    ??? success "Réponse"
        **B.** Les catégories sont comparées comme un tout, et le même
        ensemble devient une seule liste de codes.

???+ question "Question 5 (O5) : Les conditions d'utilisation d'un livre de codes disent « Free to reuse with attribution (CC BY 4.0). » Que doit contenir le fichier converti ?"
    **A.** La même phrase, dans une propriété personnalisée.

    **B.** L'adresse web de la licence dans le `dcterms:license` de la citation, par la colonne `license`.

    **C.** Rien : les licences sont l'affaire de l'archive.

    **D.** Les mots « CC BY 4.0 » dans le titre.

    ??? success "Réponse"
        **B.** Une adresse web nomme une licence sans ambiguïté, et un
        programme peut la reconnaître. La phrase n'est claire que pour une
        personne.

---

## Faites le point

- [ ] Je peux expliquer pourquoi les livres de codes répètent questions et catégories, et comment DDI-Lifecycle permet à chaque cycle de renvoyer à un seul élément. (O1)
- [ ] Je peux lire la citation, les fichiers et les variables de fichiers DDI-Codebook 2.5 ou 2.6 avec ElementTree. (O2)
- [ ] Je peux trouver les questions, listes de codes et univers que répètent plusieurs livres de codes, et dire quand une répétition est le même élément. (O3)
- [ ] Je peux écrire les tables avec chaque élément répété une seule fois, et charger plusieurs cycles comme une série. (O4)
- [ ] Je peux reprendre le DOI, ajouter une adresse de licence, une trace de la conversion et des libellés, et les vérifier avec le linter. (O5)

---

!!! tip "Notes pour l'instructeur"
    - Commencez par deux livres de codes de la même enquête tirés de l'archive
      du groupe, s'il y en a. Demandez aux participants de trouver ce qui a
      changé d'une année à l'autre avant d'exécuter du code.
    - La décision de la section 4 est le cœur du module : qui dit que deux
      formulations sont la même question ? Laissez le groupe débattre de
      « home » et de « household ».
    - L'exercice 3 montre le bénéfice : un troisième cycle n'ajoute aucune
      question. Faites-le au projecteur.
    - Les participants s'attendent souvent à ce que `ddi-l` lise lui-même les
      livres de codes. Ce n'est pas le cas, à dessein : les tables sont
      l'entrée documentée, et elles signalent chaque problème avec sa ligne
      et sa colonne.

---

**Voir aussi :** [Charger du DDI depuis des tableurs](../spreadsheet-import.fr.md) | [Travailler avec d'autres outils](../interoperability.fr.md#fichiers-ddi-codebook) | [Module 21 : Décrire vos données avec DDI-CDI](module-21-ddi-cdi.fr.md)
