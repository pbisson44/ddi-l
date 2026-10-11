---
description: >-
  Lire, modifier et écrire les exports FragmentInstance de Colectica Designer
  avec ddi-l : chaque type d'élément comme modèle typé, et des fichiers
  réécrits octet pour octet dans la mise en forme de Colectica.
---

# Travailler avec les exports Colectica

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
[Charger du DDI depuis des tableurs](spreadsheet-import.md) :
`load_tables(...).to_fragment()` donne le même genre de fragment.

## Mise en forme

`save()` écrit par défaut la mise en forme de Colectica : UTF-8 avec marque
d'ordre des octets, le préfixe `ddi:` sur la racine et la
`TopLevelReference`, chaque `<Fragment>` en marge gauche déclarant l'espace de
noms réutilisable comme `r:`, chaque élément déclarant l'espace de noms de son
module comme espace par défaut, les attributs dans l'ordre du schéma et une
indentation de deux espaces. `save(chemin, layout="default")` écrit plutôt la
mise en forme habituelle de cette bibliothèque.

En ligne de commande :

```bash
ddi validate export.xml
ddi lint export.xml
ddi roundtrip export.xml --layout colectica -o copy.xml
```

`ddi roundtrip --layout colectica` sur un export non modifié écrit un fichier
identique.
