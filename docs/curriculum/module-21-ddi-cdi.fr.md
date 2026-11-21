---
description: >-
  Module 21 facultatif du cours ddi-l : décrire les données d'une étude avec
  DDI-CDI, la norme de la DDI Alliance pour intégrer des données de domaines
  différents, et valider le résultat selon son schéma.
---

# Module 21 (facultatif) : Décrire vos données avec DDI-CDI

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Dire ce que décrit DDI-CDI, en quoi il diffère de
      DDI-Lifecycle et de DDI-Codebook, et quand un projet l'emploierait.
    - **O2.** Faire correspondre une variable d'une étude `ddi-l` à DDI-CDI :
      une variable d'instance dont les valeurs viennent d'un domaine de valeurs
      substantives, et les valeurs manquantes d'un domaine de valeurs
      sentinelles, chacun appuyé sur une liste de codes.
    - **O3.** Décrire un fichier de données comme une structure de données
      large DDI-CDI, avec une composante d'identification et des composantes
      de mesure, et dire en quoi une structure longue diffère.
    - **O4.** Écrire du XML DDI-CDI 1.0 à partir d'une étude `ddi-l` avec
      `xml.etree.ElementTree` de Python, et le valider selon le schéma de la
      DDI Alliance.
    - **O5.** Expliquer comment DDI-CDI identifie les objets et les relie,
      et comparer avec un URN DDI-Lifecycle.

**Prérequis :** [Module 9](module-09-code-lists.fr.md).
Le [Module 20](module-20-codebook-to-lifecycle.fr.md) aide, mais n'est pas
nécessaire. Ce module est facultatif : le projet de synthèse n'en a pas
besoin.

**Durée :** 60 min en autonomie / 75 min avec instructeur.

**Nouveau dans ce module :** DDI-CDI 1.0, `InstanceVariable`,
`SubstantiveValueDomain`, `SentinelValueDomain`, `CodeList`, `Code`,
`Notation`, `Category`, `WideDataStructure`, `IdentifierComponent`,
`MeasureComponent`, `WideDataSet`, `xmlschema.XMLSchema11`.

---

## 1. Trois normes DDI

La DDI Alliance a publié **DDI Cross-Domain Integration** (DDI-CDI) 1.0 en
janvier 2025. La norme ne remplace pas les deux autres ; elle décrit ce
qu'elles ne décrivent pas :

| | DDI-Codebook | DDI-Lifecycle | DDI-CDI |
| --- | --- | --- | --- |
| Décrit | Une étude et ses fichiers de données | Des études tout au long de leur vie : concepts, questions, questionnaires, variables, fichiers de données | Les données elles-mêmes : chaque valeur, quelle que soit la structure qui la contient, et les traitements qui l'ont produite |
| Domaines | Sciences sociales | Statistiques sociales, économiques et de santé | Tout domaine, pour combiner des données de champs différents |
| Structures de données | Un fichier de lignes et de colonnes | Dispositions d'enregistrement et tableaux multidimensionnels | Large, longue, multidimensionnelle et clé-valeur |
| Encodages | XML | XML | Un modèle UML, encodé en XML Schema et en ontologie RDF avec JSON-LD |

Un projet emploie DDI-CDI quand il combine des données de plusieurs sources,
comme une enquête, un registre et des relevés de capteurs, et doit dire
exactement comment chaque valeur se rapporte aux autres, quelle que soit la
forme de chaque source. Les questions et le questionnaire de l'enquête
restent en DDI-Lifecycle.

`ddi-l` lit et écrit seulement DDI-Lifecycle. Ce module lit une étude
`ddi-l` et écrit la description DDI-CDI de ses données avec la bibliothèque
standard de Python, puis la vérifie selon le schéma de la DDI Alliance.

## 2. L'étude à décrire

L'étude est un fichier de données à une ligne par ménage, comme dans les
modules précédents : un identifiant, le type d'animal, qui peut être « Don't
know », et le nombre d'animaux. Les
[tables de métadonnées](../spreadsheet-import.fr.md) la construisent en
quelques lignes :

```python
from pathlib import Path

from ddi_l.tables import load_tables

folder = Path("pets-tables")
folder.mkdir(exist_ok=True)
files = {
    "settings": "setting,value\nagency,example.org\n",
    "code_lists": "id,label@en\nPET_KINDS,Kinds of pet\n",
    "codes": (
        "code_list,value,label@en,missing\n"
        "PET_KINDS,1,Dog,\n"
        "PET_KINDS,2,Cat,\n"
        "PET_KINDS,3,Other pet,\n"
        "PET_KINDS,9,Don't know,true\n"
    ),
    "variables": (
        "id,label@en,representation,code_list,numeric_type,max_length\n"
        "HouseholdId,Household identifier,text,,,10\n"
        "PetKind,Kind of pet,code,PET_KINDS,,\n"
        "PetCount,Number of pets,numeric,,Integer,\n"
    ),
}
for name, text in files.items():
    (folder / f"{name}.csv").write_text(text, encoding="utf-8")

tables = load_tables(folder)
items = {item.identifier: item for item in tables.items}
print(len(tables.variables))  # -> 3
```

`items` trouve tout élément par son identifiant : c'est ainsi que le code
plus bas suit un renvoi, d'une variable à sa liste de codes et d'un code à sa
catégorie.

## 3. Les variables en DDI-CDI

Les deux normes décrivent une variable à trois niveaux, du plus général au
plus précis :

| Niveau | Ce que c'est | DDI-Lifecycle | DDI-CDI |
| --- | --- | --- | --- |
| Conceptuel | Ce qui est mesuré, quelles que soient les réponses | `ConceptualVariable` | `ConceptualVariable` |
| Représenté | Ce qui est mesuré et la façon d'en noter les valeurs | `RepresentedVariable` | `RepresentedVariable` |
| Instance | Une colonne d'un fichier de données | `Variable` | `InstanceVariable` |

En DDI-CDI, chaque niveau prolonge celui du dessus : une variable d'instance
est une variable représentée, qui est une variable conceptuelle. Ce module
écrit seulement le niveau de l'instance.

L'autre différence est la façon de décrire les valeurs. En DDI-Lifecycle, une
variable a une liste de codes, et une catégorie est marquée `isMissing`.
DDI-CDI partage les valeurs d'une variable entre deux **domaines de
valeurs** :

- un **domaine de valeurs substantives** : les réponses à la question, ici
  Dog, Cat et Other pet ;
- un **domaine de valeurs sentinelles** : les valeurs qui tiennent lieu
  d'autre chose, comme « ne sait pas », « refus » ou « sans objet ».

Chaque domaine de valeurs prend ses valeurs dans une **liste de codes**. Dans
une liste de codes, un **code** relie une **notation**, la valeur inscrite
dans les données comme `9`, à la **catégorie** qu'elle représente, comme
« Don't know ».

## 4. Identifier et relier les objets

DDI-CDI identifie un objet comme DDI-Lifecycle, par une agence, un
identifiant et une version, écrits comme trois éléments d'`identifier`. Un
renvoi vers un autre objet en donne les trois mêmes parties et la classe de
l'objet. Quatre petites fonctions les écrivent :

```python
import xml.etree.ElementTree as ET

CDI = "http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/"
ET.register_namespace("cdi", CDI)


def cdi(tag, *children, text=None):
    """Un élément cdi: qui contient des enfants, ou du texte."""
    element = ET.Element(f"{{{CDI}}}{tag}")
    element.text = text
    element.extend(children)
    return element


def identifier(object_id, agency="example.org", version="1"):
    """Ce que DDI-Lifecycle écrit en Agency, ID et Version."""
    return cdi(
        "identifier",
        cdi(
            "ddiIdentifier",
            cdi("dataIdentifier", text=object_id),
            cdi("registrationAuthorityIdentifier", text=agency),
            cdi("versionIdentifier", text=version),
        ),
    )


def link(association, object_id, valid_type, agency="example.org", version="1"):
    """Un renvoi vers un autre objet : son identifiant et sa classe."""
    return cdi(
        association,
        cdi(
            "ddiReference",
            cdi("dataIdentifier", text=object_id),
            cdi("registrationAuthorityIdentifier", text=agency),
            cdi("versionIdentifier", text=version),
        ),
        cdi("validType", text=valid_type),
    )


def label(text, language="en"):
    """Un libellé dans une langue."""
    return cdi(
        "displayLabel",
        cdi(
            "languageSpecificString",
            cdi("content", text=text),
            cdi("language", text=language),
        ),
    )
```

L'élément d'un renvoi est nommé d'après l'association qu'il représente : sa
classe, le sens du lien et la classe visée. `Code_denotes_Category`, par
exemple, relie un code à la catégorie qu'il désigne. Le schéma fixe l'ordre
des éléments dans chaque classe, que ces fonctions suivent.

## 5. Listes de codes et domaines de valeurs

Une liste de codes donne trois objets par code : la catégorie, la notation et
le code qui les relie. Chacun reçoit un identifiant formé de celui de la
liste et de la valeur, pour que les renvois entre eux soient simples à
écrire :

```python
def code_list(list_id, codes):
    """Une liste de codes, avec une Category, une Notation et un Code par code."""
    objects = []
    code_links = []
    for code in codes:
        category = items[code.category.identifier]
        key = f"{list_id}-{code.value}"
        objects.append(
            cdi(
                "Category",
                label(category.labels[0].text),
                identifier(f"category-{key}"),
            )
        )
        objects.append(
            cdi(
                "Notation",
                cdi("content", cdi("content", text=code.value)),
                identifier(f"notation-{key}"),
            )
        )
        objects.append(
            cdi(
                "Code",
                identifier(f"code-{key}"),
                link("Code_denotes_Category", f"category-{key}", "Category"),
                link("Code_uses_Notation", f"notation-{key}", "Notation"),
            )
        )
        code_links.append(link("CodeList_has_Code", f"code-{key}", "Code"))
    listing = cdi(
        "CodeList",
        identifier(list_id),
        cdi("allowsDuplicates", text="false"),
        *code_links,
    )
    return [*objects, listing]
```

Une variable avec une liste de codes reçoit deux listes de codes et deux
domaines de valeurs : les codes substantifs, et les codes dont la catégorie
est manquante. Vient ensuite la variable d'instance, avec ses renvois vers
ses domaines :

```python
def describe(variable):
    """Les objets DDI-CDI d'une variable ddi-l : ses domaines et elle-même."""
    name = variable.names[0].text
    objects = []
    domains = []
    coded = variable.variable_representation.code_representation
    if coded is not None:
        codes = items[coded.code_list_reference.identifier].codes
        missing = [c for c in codes if items[c.category.identifier].isMissing]
        answers = [c for c in codes if c not in missing]
        objects += code_list(f"codes-{name}", answers)
        objects.append(
            cdi(
                "SubstantiveValueDomain",
                identifier(f"values-{name}"),
                link(
                    "SubstantiveValueDomain_takesValuesFrom_EnumerationDomain",
                    f"codes-{name}",
                    "CodeList",
                ),
            )
        )
        if missing:
            objects += code_list(f"missing-{name}", missing)
            objects.append(
                cdi(
                    "SentinelValueDomain",
                    identifier(f"missing-values-{name}"),
                    link(
                        "SentinelValueDomain_takesValuesFrom_EnumerationDomain",
                        f"missing-{name}",
                        "CodeList",
                    ),
                )
            )
            domains.append(
                link(
                    "RepresentedVariable_takesSentinelValuesFrom_SentinelValueDomain",
                    f"missing-values-{name}",
                    "SentinelValueDomain",
                )
            )
        domains.append(
            link(
                "RepresentedVariable_takesSubstantiveValuesFrom_SubstantiveValueDomain",
                f"values-{name}",
                "SubstantiveValueDomain",
            )
        )
    objects.append(
        cdi(
            "InstanceVariable",
            label(variable.labels[0].text),
            identifier(f"variable-{name}"),
            cdi("name", cdi("name", text=name)),
            *domains,
        )
    )
    return objects


model = cdi("DDICDIModels")
for variable in tables.variables:
    model.extend(describe(variable))
print(len(model))  # -> 19
```

`PetKind` donne 17 objets : 3 codes de réponses et 1 code pour « Don't
know », avec leurs catégories, notations et codes, 2 listes de codes, 2
domaines de valeurs et la variable. `HouseholdId` et `PetCount` donnent
chacune une variable d'instance. Tous sont côte à côte dans `DDICDIModels`,
l'élément racine, et renvoient les uns aux autres par identifiant.

## 6. La structure de données

Un fichier de données à une ligne par unité et une colonne par variable est
**large**. DDI-CDI en décrit la structure par une **composante** par colonne,
chacune définie par sa variable :

- une **composante d'identification** pour les colonnes qui distinguent les
  lignes, ici `HouseholdId` ;
- une **composante de mesure** pour chaque colonne de valeurs observées, ici
  `PetKind` et `PetCount`.

```python
components = []
structure_links = []
for variable in tables.variables:
    name = variable.names[0].text
    kind = "IdentifierComponent" if name == "HouseholdId" else "MeasureComponent"
    components.append(
        cdi(
            kind,
            identifier(f"component-{name}"),
            link(
                "DataStructureComponent_isDefinedBy_RepresentedVariable",
                f"variable-{name}",
                "InstanceVariable",
            ),
        )
    )
    structure_links.append(
        link("DataStructure_has_DataStructureComponent", f"component-{name}", kind)
    )

model.extend(components)
model.append(cdi("WideDataStructure", identifier("pets-structure"), *structure_links))
model.append(
    cdi(
        "WideDataSet",
        identifier("pets-data"),
        link(
            "DataSet_isStructuredBy_DataStructure",
            "pets-structure",
            "WideDataStructure",
        ),
    )
)
ET.indent(model)
ET.ElementTree(model).write("pets-cdi.xml", encoding="utf-8", xml_declaration=True)
print(len(model))  # -> 24
```

Les mêmes valeurs pourraient être rangées en format **long** : une ligne par
ménage et par variable, avec une colonne qui nomme la variable et une colonne
qui en contient la valeur. DDI-CDI décrit ce fichier par une structure de
données longue, dans laquelle ces deux colonnes sont une composante de
descripteur de variable et une composante de valeur de variable. Les
variables, les domaines de valeurs et les listes de codes restent les mêmes :
c'est ce qui permet à DDI-CDI de dire que deux fichiers contiennent les mêmes
données sous des formes différentes.

## 7. Valider selon le schéma

La DDI Alliance publie le schéma XML de DDI-CDI 1.0 sur sa
[page DDI-CDI](https://ddialliance.org/ddi-cdi_v1.0), et dans la version
publiée sur GitHub. Téléchargez-le une fois :

<!-- docs-test: skip -- télécharge le schéma -->
```python
from urllib.request import urlretrieve

urlretrieve(
    "https://raw.githubusercontent.com/ddi-cdi/ddi-cdi/v1.0/"
    "build/encoding/xml-schema/ddi-cdi.xsd",
    "ddi-cdi.xsd",
)
```

Validez ensuite avec `xmlschema`, que `pip install ddi-l` installe :

<!-- docs-test: skip -- demande le schéma téléchargé -->
```python
import xmlschema

schema = xmlschema.XMLSchema11("ddi-cdi.xsd")
print(schema.is_valid("pets-cdi.xml"))  # -> True
for error in schema.iter_errors("pets-cdi.xml"):
    print(error.path, error.reason)
```

!!! warning "Employez XMLSchema11"
    Le schéma DDI-CDI indique qu'il demande un processeur XML Schema 1.1.
    `xmlschema.XMLSchema`, le validateur XML Schema 1.0, le respecte et
    ignore tout le schéma : il signale alors que `DDICDIModels` « is not an
    element of the schema ». `xmlschema.XMLSchema11` le lit.

Une erreur nomme l'élément où le fichier s'écarte du schéma. La plus
fréquente vient des éléments d'une classe écrits dans un autre ordre que
celui du schéma.

## 8. Ce que cette esquisse laisse de côté

DDI-CDI peut en dire bien plus que ce fichier :

- **Les autres niveaux de chaque variable.** Une variable représentée
  partagée par plusieurs fichiers de données, et une variable conceptuelle
  avec son concept et son type d'unité (ici, les ménages), permettraient aux
  variables d'un autre fichier de renvoyer aux mêmes.
- **Les valeurs elles-mêmes.** Un point de données est une cellule du
  fichier, et une donnée la valeur qui s'y trouve. Les décrire permet à
  DDI-CDI de suivre une seule valeur d'un fichier à un autre.
- **Le fichier physique.** La disposition des colonnes dans un fichier CSV ou
  à largeur fixe, et les formats des logiciels statistiques.
- **Le traitement.** Des activités et des étapes consignent comment les
  données ont été produites ou transformées, de la collecte au fichier
  publié.

La DDI Alliance publie aussi DDI-CDI sous forme d'ontologie RDF, avec un
encodage JSON-LD : les mêmes classes et associations, pour les systèmes de
données liées.

---

## Exercices

1. **(O1)** Pour chaque projet, quelle norme DDI convient le mieux ? (a) Une
   archive documente un fichier d'enquête déposé, pour son catalogue. (b) Un
   organisme statistique garde ses questions et ses listes de codes dans une
   banque, réutilisée à chaque cycle. (c) Une équipe de recherche combine une
   enquête, des dossiers hospitaliers et des relevés de qualité de l'air, et
   doit montrer comment chaque valeur a été obtenue.

    ??? success "Réponse"

        (a) DDI-Codebook, ou DDI-Lifecycle si l'archive veut réutiliser
        chaque élément : une étude et son fichier. (b) DDI-Lifecycle : chaque
        question et chaque liste de codes est un élément avec son
        identifiant et sa version, auquel chaque cycle renvoie. (c) DDI-CDI :
        des données de domaines et de formes différents, et les traitements
        qui les relient. Le questionnaire de l'enquête serait toujours décrit
        en DDI-Lifecycle.

2. **(O2, O5)** Relisez `pets-cdi.xml` avec ElementTree. Pour chaque
   variable d'instance, affichez son nom et les classes des domaines de
   valeurs dont elle prend ses valeurs.

    **Résultat attendu :**

    ```text
    HouseholdId []
    PetKind ['SentinelValueDomain', 'SubstantiveValueDomain']
    PetCount []
    ```

    ??? success "Réponse"

        ```python
        written = ET.parse("pets-cdi.xml").getroot()
        N = {"cdi": CDI}
        for variable in written.iterfind("cdi:InstanceVariable", N):
            name = variable.findtext("cdi:name/cdi:name", namespaces=N)
            domains = [
                valid_type.text for valid_type in variable.iterfind("*/cdi:validType", N)
            ]
            print(name, domains)
        ```

        Un renvoi contient dans `validType` la classe de l'objet visé : un
        programme sait ce qu'il trouvera sans suivre le renvoi.
        `HouseholdId` et `PetCount` n'ont pas de liste de codes : cette
        esquisse ne leur donne donc pas de domaine de valeurs.

3. **(O3)** Les mêmes données sur les animaux sont rangées en format long,
   avec les colonnes `HouseholdId`, `Variable` et `Value` : `Variable`
   contient `PetKind` ou `PetCount`, et `Value` la réponse. Nommez le type de
   structure de données et la composante que reçoit chaque colonne.

    ??? success "Réponse"

        Une structure de données longue (`LongDataStructure`). `HouseholdId`
        est une composante d'identification, comme dans le fichier large.
        `Variable` est une composante de descripteur de variable : ses
        valeurs nomment les variables, et elle est définie par une variable
        descriptive dont les valeurs sont `PetKind` et `PetCount`. `Value`
        est une composante de valeur de variable : elle contient les valeurs
        de plusieurs variables dans une seule colonne. `PetKind` et
        `PetCount` gardent leurs variables d'instance et leurs domaines de
        valeurs.

4. **(O4)** Donnez à chaque catégorie un libellé français en plus de
   l'anglais. Modifiez `label()` pour qu'elle prenne plusieurs paires
   `(texte, langue)`, donnez aux catégories les libellés *Chien*, *Chat*,
   *Autre animal* et *Ne sait pas*, écrivez de nouveau le fichier et
   affichez combien de chaînes françaises il contient.

    **Résultat attendu :**

    ```text
    4
    ```

    ??? success "Réponse"

        ```python
        def label(*strings):
            """Un libellé dans chaque langue donnée, en paires (texte, langue)."""
            return cdi(
                "displayLabel",
                *(
                    cdi(
                        "languageSpecificString",
                        cdi("content", text=text),
                        cdi("language", text=language),
                    )
                    for text, language in strings
                ),
            )


        french = {"Dog": "Chien", "Cat": "Chat", "Other pet": "Autre animal"}
        french["Don't know"] = "Ne sait pas"
        written = ET.parse("pets-cdi.xml").getroot()
        N = {"cdi": CDI}
        for category in written.iterfind("cdi:Category", N):
            english = category.findtext(
                "cdi:displayLabel/cdi:languageSpecificString/cdi:content", namespaces=N
            )
            category.remove(category.find("cdi:displayLabel", N))
            category.insert(0, label((english, "en"), (french[english], "fr")))
        ET.indent(written)
        ET.ElementTree(written).write("pets-cdi.xml", encoding="utf-8", xml_declaration=True)
        print(
            sum(1 for language in written.iter(f"{{{CDI}}}language") if language.text == "fr")
        )  # -> 4
        ```

        Le nouveau libellé vient en premier dans chaque catégorie, là où le
        schéma place `displayLabel`, avant `identifier`. Validez de nouveau
        le fichier pour le vérifier.

5. **(O5)** Affichez l'URN DDI-Lifecycle de la variable `PetKind` des
   tables, puis les trois parties que DDI-CDI écrit pour la même variable
   dans `pets-cdi.xml`. Que faudrait-il pour que les deux désignent la même
   chose ?

    ??? success "Réponse"

        ```python
        pet_kind = tables.get("variables", "PetKind")
        print(pet_kind.to_reference().urn)
        # -> urn:ddi:example.org:e96e0842-d74e-5893-a7ba-b3c3fabda24d:1
        written = ET.parse("pets-cdi.xml").getroot()
        N = {"cdi": CDI}
        for variable in written.iterfind("cdi:InstanceVariable", N):
            if variable.findtext("cdi:name/cdi:name", namespaces=N) == "PetKind":
                parts = variable.find("cdi:identifier/cdi:ddiIdentifier", N)
                print([part.text for part in parts])
        # -> ['variable-PetKind', 'example.org', '1']
        ```

        Les deux ont une agence, un identifiant et une version. Le fichier
        DDI-CDI emploie ses propres identifiants, comme `variable-PetKind`.
        Pour que les deux descriptions de la variable soient le même objet,
        donnez à DDI-CDI l'identifiant DDI-Lifecycle : passez plutôt
        `pet_kind.identifier` et `pet_kind.version` à `identifier()`.

---

## Quiz

???+ question "Question 1 (O1) : Que décrit DDI-CDI que DDI-Lifecycle ne décrit pas ?"
    **A.** Les questionnaires et leur cheminement.

    **B.** Les données elles-mêmes, en structures large, longue, multidimensionnelle ou clé-valeur, et les traitements qui les ont produites, à travers les domaines.

    **C.** Les listes de codes.

    **D.** Les titres des études.

    ??? success "Réponse"
        **B.** Les questionnaires sont la force de DDI-Lifecycle ; les deux
        ont des listes de codes. DDI-CDI décrit des données de toute forme
        et de tout domaine, jusqu'à une seule valeur.

???+ question "Question 2 (O2) : Une variable a les codes 1 Dog, 2 Cat et 9 Don't know. Comment DDI-CDI les contient-il ?"
    **A.** Une liste de codes, avec 9 marqué comme manquant.

    **B.** Un domaine de valeurs substantives avec une liste de codes de 1 et 2, et un domaine de valeurs sentinelles avec une liste de codes de 9.

    **C.** Trois variables d'instance.

    **D.** Dans la structure de données.

    ??? success "Réponse"
        **B.** DDI-CDI sépare les réponses des valeurs qui tiennent lieu
        d'autre chose. DDI-Lifecycle le fait avec une liste de codes et
        l'indicateur `isMissing` d'une catégorie.

???+ question "Question 3 (O3) : Dans une structure de données large, que reçoit la colonne de l'identifiant du ménage ?"
    **A.** Une composante de mesure.

    **B.** Une composante d'identification, définie par la variable de l'identifiant.

    **C.** Une composante de valeur de variable.

    **D.** Rien : les identifiants ne sont pas décrits.

    ??? success "Réponse"
        **B.** Les composantes d'identification distinguent les lignes ; les
        composantes de mesure contiennent ce qui a été observé.

???+ question "Question 4 (O4) : xmlschema.XMLSchema dit que DDICDIModels n'est pas un élément du schéma. Pourquoi ?"
    **A.** Le fichier a le mauvais espace de noms.

    **B.** Le schéma DDI-CDI demande un processeur XML Schema 1.1 ; le validateur 1.0 l'ignore. Employez `xmlschema.XMLSchema11`.

    **C.** Le fichier du schéma est corrompu.

    **D.** `DDICDIModels` doit être le dernier élément.

    ??? success "Réponse"
        **B.** Le schéma déclare `vc:minVersion="1.1"`. Un processeur XML
        Schema 1.0 le respecte en ignorant le contenu du schéma.

???+ question "Question 5 (O5) : Que contient un renvoi DDI-CDI ?"
    **A.** L'autre objet, copié en entier.

    **B.** L'identifiant de l'autre objet (identifiant de données, autorité d'enregistrement et version) et sa classe dans `validType`.

    **C.** Un chemin de fichier.

    **D.** Un URN seulement.

    ??? success "Réponse"
        **B.** `ddiReference` donne les trois mêmes parties qu'un URN
        DDI-Lifecycle, et `validType` dit quelle classe attendre.

---

## Faites le point

- [ ] Je peux dire ce que décrit DDI-CDI, et quand l'employer à côté de DDI-Lifecycle et de DDI-Codebook. (O1)
- [ ] Je peux faire correspondre une variable codée avec des valeurs manquantes à une variable d'instance, deux domaines de valeurs et leurs listes de codes. (O2)
- [ ] Je peux décrire un fichier de données comme une structure de données large, et nommer les composantes qu'emploierait une structure longue. (O3)
- [ ] Je peux écrire du XML DDI-CDI à partir d'une étude `ddi-l` et le valider avec `xmlschema.XMLSchema11`. (O4)
- [ ] Je peux expliquer un identifiant et un renvoi DDI-CDI, et les comparer à un URN DDI-Lifecycle. (O5)

---

!!! tip "Notes pour l'instructeur"
    - Commencez par le tableau de la section 1 et un vrai cas du groupe : un
      projet qui combine des fichiers de formes différentes. DDI-CDI prend
      son sens quand les participants ont vécu ce problème.
    - Le partage entre valeurs substantives et sentinelles (section 3) est
      l'idée que les participants retiennent. Demandez quelles valeurs d'une
      variable connue sont des sentinelles avant de montrer le code.
    - Téléchargez le schéma avant la séance si le réseau de la salle est
      lent : il fait environ 1 Mo.
    - Le fichier est long pour trois variables. C'est l'objet de l'exercice
      sur les identifiants : en pratique, un programme écrit le DDI-CDI,
      comme ici, et personne ne le tape.

---

**Voir aussi :** [Module 20 : De DDI-Codebook à DDI-Lifecycle, pensé pour la réutilisation](module-20-codebook-to-lifecycle.fr.md) | [Travailler avec d'autres outils](../interoperability.fr.md) | [DDI-CDI à la DDI Alliance](https://ddialliance.org/ddi-cdi_v1.0)
