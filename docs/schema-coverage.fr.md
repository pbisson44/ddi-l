# Couverture du schéma

Cette page est une carte honnête de la part du schéma DDI Lifecycle 3.3 que
`ddi-l` prend en charge, et à quel niveau. La « prise en charge » signifie
trois choses différentes, alors le tableau les sépare en trois niveaux.

## Les trois niveaux

1. **API de haut niveau** : vous créez et gérez ces éléments avec l'API
   simple de `Document` : `new_study()`, `add_question()`, `add_variable()`,
   `add_item()`, `items()`, `find()`, `remove()`. C'est le chemin facile, en
   une ligne, qui suffit pour la plupart de l'écriture.
2. **Modèle typé** : chaque type du module est une classe Python typée avec
   prise en charge complète de `from_xml()` / `to_xml()` : vous pouvez le
   lire, le construire et le modifier précisément depuis `ddi_l.models.*`,
   même sans raccourci en une ligne.
3. **Conservation lors des aller-retours** : ouvrir un fichier et le ré-
   enregistrer garde le contenu fidèle élément pour élément, même pour les
   parties que la bibliothèque ne modélise pas en détail. Les éléments non
   reconnus sont préservés tels quels.

!!! info "Rien n'est perdu"
    Tout DDI 3.3 est **modélisé et validé** : la couche de modèle est générée
    à partir du XSD officiel (environ 500 types), et `doc.validate()` vérifie
    par rapport au vrai `instance_3_3.xsd`. La fidélité aller-retour est
    complète : un fichier de production de 100 000 éléments se ré-enregistre
    sans perte d'élément. La seule chose qui varie selon le module est
    l'**ergonomie** : la quantité de code à écrire.

## Couverture par module

| Module DDI | API de haut niveau | Modèle typé | Aller-retour |
| ------------ | :------------------: | :-----------: | :------------: |
| Study Unit | Oui | Oui | Oui |
| Conceptual Component (concepts, univers, types d'unité) | Oui | Oui | Oui |
| Data Collection (questions, instruments, **flux de questionnaire**) | Oui | Oui | Oui |
| Logical Product (variables, listes de codes, relations de données, NCubes) | Oui | Oui | Oui |
| Reusable (types partagés : références, noms, dates…) | s.o. | Oui | Oui |
| Archive (citations, couverture, provenance) | Oui | Oui | Oui |
| Methodology (méthodologie de collecte) | Oui | Oui | Oui |
| Types Process (`urn:ddi-l:extension:process:1`) | Non | Oui | Oui |
| Comparative (cartes d'harmonisation) | Oui | Oui | Oui |
| Physical Data Product : dispositions d'enregistrements | Oui | Oui | Oui |
| Physical Data Product : structures, NCube | Oui | Oui | Oui |
| Physical Instance (fichiers de données) | Oui | Oui | Oui |
| Group (série d'études) | Oui | Oui | Oui |
| Resource / Local Holding Packages | Oui | Oui | Oui |
| Information de traduction | Oui | Oui | Oui |
| DDI Profile (déclaration d'usage) | Oui | Oui | Oui |
| Dataset (données en ligne) | Oui | Oui | Oui |

« Non » dans la colonne de l'API de haut niveau signifie qu'il n'existe pas de
raccourci en une ligne ; utilisez plutôt le modèle typé. s.o. signifie sans
objet.

!!! note "À propos du module Process"
    Le module **Process** autonome (`urn:ddi-l:extension:process:1`) est modélisé et fait
    l'aller-retour, mais il **ne fait pas partie du schéma d'instance DDI 3.3** :
    `instance_3_3.xsd` ne l'importe pas, il n'a donc aucun point d'attache au
    niveau de l'instance et par conséquent aucun raccourci en une ligne ;
    construisez-le depuis `ddi_l.models.process` au besoin. Le **flux** de
    questionnaire et de capture de données en DDI 3.3 réside plutôt dans Data
    Collection sous forme de control constructs (`QuestionConstruct`, `Sequence`,
    `IfThenElse`, `StatementItem`, `ComputationItem`, `Loop`), qui *sont* des
    types `add_item` de première classe.

## Ce que couvre « add_item »

`add_item()` / `items()` reconnaissent actuellement 30 types d'éléments, y
compris l'ensemble complet du flux de questionnaire (`QuestionConstruct`,
`Sequence`, `IfThenElse`, `StatementItem`, `ComputationItem`, `Loop` ; voir le
[Module 8](curriculum/module-08-questionnaire-flows.md)), `PhysicalInstance`,
`RecordLayout`, `DataRelationship` et `NCube`. Une instance physique décrit un
fichier de données ; une disposition d'enregistrements associe les variables
à des positions dans ce fichier :

```python
from ddi_l.models.physical import PhysicalInstance

pi = doc.add_item(PhysicalInstance, name="2021 Microdata File")
pi.set_data_file("https://example.org/health-2021.csv")
pi.set_record_count(15000)

# Associer les variables à des colonnes de largeur fixe
rl = doc.add_record_layout()
rl.add_data_item(age.to_reference(), start_position=1, width=2)
rl.add_data_item(income.to_reference(), start_position=3, width=8)

# Enregistrements logiques (quelles variables composent un cas)
dr = doc.add_data_relationship()
dr.add_logical_record()  # toutes les variables, un enregistrement rectangulaire

# Données multidimensionnelles (cube) (avec une région de coordonnées pour un attribut)
cube = doc.add_ncube(name="Population par année et région")
cube.add_dimension(year.to_reference())
cube.add_dimension(region.to_reference())
cube.add_measure(population.to_reference())
region = cube.add_coordinate_region()
cube.add_attribute(footnote.to_reference(), attachment_region=region)

# Types de variables : numérique / codé / texte / date
# (les plages numériques acceptent des bornes inclusives et des valeurs manquantes)
doc.add_variable(name="age").set_numeric(
    "Integer", low=0, high=120, low_inclusive=True, missing_values=["-9"]
)
doc.add_variable(name="sex").set_coded(sex_codes)
```

## Atteindre la couche de modèle

Quand un module n'a pas de raccourci en une ligne, vous gardez un accès typé
complet. Construisez l'objet depuis `ddi_l.models.*` et attachez-le, ou
relisez-le après `open_ddi()`. Par exemple, la couche de données physiques se
trouve dans `ddi_l.models.physical`, la couche d'archive dans
`ddi_l.models.archive`, et ainsi de suite. Comme chaque type fait l'aller-
retour, vous pouvez aussi ouvrir un fichier existant, atteindre la partie qui
vous intéresse, la modifier et enregistrer ; rien d'autre dans le document ne
change.

## Groupes

Un document peut être organisé en **Group** (une série d'études / un paquet de
publication). `doc.add_group()` déplace l'étude sous un `<g:Group>`, et le
document reste entièrement modifiable. Les fichiers organisés en groupe
s'ouvrent et font l'aller-retour :

```python
doc = ddi.new_study(title="Vague 1", agency="exemple.org")
doc.add_variable(name="age")
doc.add_group()  # organiser l'étude dans un groupe
doc.add_variable(name="income")  # modifie toujours l'étude (maintenant groupée)
```

Ajoutez **d'autres** études avec `doc.add_study(title=...)`, et reliez les
items entre elles avec une **Comparison** :

```python
vague2 = doc.add_study(title="Vague 2")  # une seconde étude dans la série
cmp = doc.add_comparison(name="2020 vers 2021")
cmp.add_variable_map(age_2020.to_reference(), age_2021.to_reference())
```

Par défaut, les aides de haut niveau `add_*` modifient l'étude *primaire*. Pour
modifier une autre étude de la série, utilisez son curseur : `doc.study(id)`
renvoie un `StudyCursor` dont les aides `add_*` ciblent cette étude :

```python
vague2 = doc.add_study(title="Vague 2")
doc.study(vague2.identifier).add_variable(name="revenu")  # modifie la vague 2
doc.study().add_variable(name="age")  # modifie l'étude primaire
```

## Paquets au niveau de l'instance, archive et traduction

Au-delà de l'étude, un `DDIInstance` peut porter des paquets réutilisables et de
conservation, une archive et des informations de traduction, chacun avec une
aide en une ligne :

```python
doc.add_archive()  # métadonnées d'archivage de l'étude
doc.add_resource_package()  # métadonnées réutilisables partagées entre études
doc.add_local_holding_package()  # une conservation locale d'une étude déposée
doc.add_translation_information(  # langues entre lesquelles l'instance a été traduite
    languages=["en", "fr"], description="Traduit du français."
)
```

Relisez-les avec `doc.archives`, `doc.resource_packages`,
`doc.local_holding_packages` et `doc.translation_information`. Les paquets et
l'information de traduction sont sérialisés à leur position correcte dans le
modèle de contenu du `DDIInstance` lors de l'enregistrement.

## Résumé de la couverture

L'API de haut niveau couvre **tous** les modules d'instance DDI
Lifecycle 3.3 : études, concepts, collecte de données et flux de questionnaire,
produits logiques (variables avec représentations typées incluant bornes
inclusives et valeurs manquantes, listes de codes, relations de données, NCubes
avec dimensions/mesures/attributs et régions de coordonnées), instances
physiques, structures et dispositions d'enregistrements (y compris clés de
segment et détails de stockage/décimales), données en ligne (ensembles d'items,
d'enregistrements et de variables), groupes d'études avec séries multi-études
(`doc.study(id)`) et l'ensemble complet des cartes de comparaison, paquets au
niveau de l'instance et profils DDI. Le seul module qui reste au niveau du
modèle uniquement est **Process** (`urn:ddi-l:extension:process:1`), qui se situe hors du
schéma d'instance 3.3. Tout ce qu'il contient, comme tout autre module, reste
modélisé, validé et conservé lors des aller-retours.
