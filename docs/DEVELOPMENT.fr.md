---
description: >-
  Le guide de développement de ddi-l : environnement, contrôles qualité,
  générateur de code XSD, architecture, documentation et publication.
---

# Guide de développement

Merci de contribuer à améliorer `ddi-l` ! Deux documents couvrent la
contribution :

- [`CONTRIBUTING.md`](https://github.com/pbisson44/ddi-l/blob/main/CONTRIBUTING.md),
  sur GitHub, est la version courte : préparer l'environnement, lancer les
  contrôles, ouvrir une pull request. Commencez par là.
- Ce guide est la référence détaillée qui le complète : l'architecture, le
  générateur de code à partir des XSD, l'ajout d'une version de DDI, les deux
  moteurs XML, la chaîne de documentation et le processus de publication.

## Préparer votre environnement

**Python 3.11 ou plus récent** est requis. Le projet est géré avec
[uv](https://docs.astral.sh/uv/), et `uv.lock` est la source unique de vérité
pour les versions des dépendances ; la CI installe à partir de ce fichier
avec `--locked`.

```bash
uv sync --group dev              # Dépendances d'exécution et de développement
uv sync --group dev --extra full # ...plus le backend optionnel lxml
uv sync --group docs             # Chaîne de production de la documentation
```

Préfixez les commandes avec `uv run` (`uv run pytest`), ou activez
l'environnement avec `source .venv/bin/activate`.

!!! note "`full` est un extra, pas un groupe de dépendances"
    Le backend optionnel `lxml` est déclaré sous
    `[project.optional-dependencies]` : il s'installe donc avec
    `--extra full`. Le demander comme groupe (`--group full`) échoue.

Si vous préférez pip :

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[full]' --group dev   # pip 25.1+ reads dependency groups
```

## Contrôles qualité

Exécutez-les avant d'ouvrir une pull request :

```bash
uv run ruff format --check .   # Formatage
uv run ruff check .            # Linting (inclut les docstrings Google)
uv run mypy src tests          # Vérification de types (bloquante en CI)
uv run pytest                  # Tests (cible : 90 % de couverture)
uvx pip-audit --strict         # Scan de vulnérabilités
git diff --exit-code           # Un run de tests ne doit modifier aucun fichier suivi
```

`ruff` et `mypy` sont épinglés à des versions exactes dans le groupe `dev`.
Une nouvelle version de l'un ou l'autre peut changer ce qui constitue une
violation : l'épinglage est ce qui rend la CI reproductible. Mettez-le à jour
délibérément, dans un commit dédié.

Le Makefile fournit également :

```bash
make release-check             # Construit les distributions et vérifie l'empaquetage
make docs-build                # Construit la documentation en mode strict
make docs-serve                # Serveur de prévisualisation
```

`make release-check` est le contrôle déterminant avant une publication. Il
construit les deux distributions, vérifie la présence des XSD intégrés et des
fichiers d'exemple, vérifie que `ddi_l` est le *seul* paquet de premier niveau
dans la roue, puis installe la roue dans un environnement virtuel vierge et y
valide un document.

### Tests de mutation

La couverture indique qu'une ligne a été exécutée. Elle ne dit pas si un test
s'apercevrait que cette ligne est fausse, et l'écart compte surtout dans les
petits prédicats qui décident si une étiquette de langue correspond ou si un
espace de noms est utilisé. `mutmut` répond à la seconde question : il modifie
le code et vérifie si la suite proteste.

```bash
uv run mutmut run                       # tout ce qui est dans le périmètre
uv run mutmut results                   # ce qui a survécu
uv run mutmut show <nom-du-mutant>      # le diff d'un survivant
uv run mutmut run <nom-du-mutant>       # recontrôler après avoir ajoute un test
```

Le périmètre est défini dans `[tool.mutmut]` du `pyproject.toml` et reste
volontairement étroit : quatre modules de logique de décision écrite à la main,
ni les dataclasses générées ni la plomberie XML, dont les mutants sont pour
l'essentiel équivalents. Élargissez-le quand vous ajoutez un module comportant
de vraies ramifications.

**Ce n'est pas un contrôle bloquant sur les pull requests**, et
`.github/workflows/mutation.yml` explique longuement pourquoi : un passage
cible représente environ 2 200 mutants et des dizaines de minutes, les
survivants demandent un jugement qu'un seuil ne peut pas fournir, et les
résultats différent entre les deux moteurs XML. Le travail s'exécute chaque
semaine et à la demande ; le rapport se lit, il ne se satisfait pas.

Lire les survivants est le savoir-faire. Certains sont réels :
`test_tree_uses_namespace_looks_at_tags_and_attributes` existe parce que forcer
cet utilitaire à toujours répondre « non » laissait toute la suite au vert,
donc rien ne vérifiait qu'un document *utilisant* `xsi:schemaLocation` conserve
sa déclaration. D'autres ne peuvent pas être tus et ne doivent pas l'être :
`getattr(node, "nsmap", )` se comporte exactement comme `getattr(node, "nsmap",
None)` quand tous les noeuds possèdent l'attribut. Corrigez les premiers en
écrivant le test manquant ; laissez les seconds tranquilles.

## Normes de codage

- **Longueur de ligne** : 88 caractères.
- **Linting** : `ruff` avec les jeux de règles `E`, `F`, `W`, `I`, `N`,
  `UP`, `B`, `SIM`, `RUF` et `D` (docstrings Google).
- **Types** : `mypy` sur `src/` et `tests/`, bloquant en CI.
- **Docstrings** : Style Google avec sections `Args:`, `Returns:`, `Raises:`.
- **Tests** : `pytest` avec `pytest-cov`. Cible de couverture : 90 %.
- **Imports** : L'intégration isort de Ruff gère l'ordre.

## Pipeline de génération de code à partir des XSD

Toutes les classes de modèles sont générées à partir des fichiers XSD DDI 3.3.
Le XSD est la source unique de vérité pour les champs, l'ordre des éléments,
les espaces de noms et la documentation.

### Fonctionnement

1. `codegen/xsd_introspect.py` extrait le modèle de contenu complet du XSD :
   l'arbre ordonné des particules, la cardinalité, les espaces de noms, les
   attributs, l'indicateur mixte et le texte `xs:documentation`.
2. `codegen/generate_model_bases.py` émet des dataclasses de base (champs
   uniquement) sous `src/ddi_l/models/_generated/`. Chacune porte ses champs
   dérivés du XSD ainsi que trois tables de classe : `_FIELD_XML_MAP` (nom de
   champ vers balise et type), `_ATTR_XML_MAP` (nom de champ vers attribut XML)
   et `_ELEMENT_ORDER` (l'ordre des enfants déclaré par le XSD). Il émet aussi
   `_generated/label_slots.py`, une table couvrant tout le schéma indiquant
   quels éléments peuvent porter un `r:Label` ; la règle de lint
   `ddi.maintainable.labels` s'en sert pour ne jamais exiger un libellé que le
   schéma n'autorise pas, et `ALLOW_LABELS` en est dérivé à la création de la
   classe plutôt que tenu à la main. Une seconde table couvrant tout le schéma,
   `_generated/fixed_attributes.py`, recense les attributs que le XSD fixe à
   une valeur donnée ; la conversion JSON vers XML les supprime, puisqu'un
   attribut fixé par le schéma ne porte aucune information et que le réécrire
   ferait rendre au aller-retour plus que ce qu'on lui a fourni.
3. Le moteur XML générique de `MaintainableBase.from_xml()` / `.to_xml()`
   (`src/ddi_l/models/base.py`) pilote la sérialisation à partir de ces tables
   et émet les enfants dans l'ordre déclaré par le XSD. Tout ce que les tables
   ne nomment pas est préservé tel quel via le passthrough `other_elements` /
   `other_attributes` : un aller-retour ne perd jamais de contenu.
4. Les classes écrites à la main dans `src/ddi_l/models/*.py` héritent des
   bases générées et n'ajoutent que des helpers, de la validation et des
   constructeurs de commodité.

### Régénérer les modèles

```bash
uv run python -m codegen.generate_model_bases
```

La CI inclut un contrôle de dérive qui échoue si le code généré diffère de ce
que le XSD produirait :

```bash
uv run python -m codegen.generate_model_bases
git diff --exit-code src/ddi_l/models/_generated/
```

Ne modifiez jamais les fichiers sous `_generated/` manuellement.

### Audit de couverture

`uv run python -m codegen.coverage_audit` régénère
`codegen/COVERAGE_AUDIT.md`, qui mesure la part du XSD exposée par la couche
générée sous forme de champs nommés par rapport à celle préservée via le
passthrough.

## Prendre en charge une nouvelle version de DDI

Cette section existe pour que la prochaine personne n'ait pas à rétro-concevoir
ce qui est lié à une version de DDI. C'est délibérément un cadre de décision et
non un script de migration : DDI 4.0 n'est pas entièrement publié, et un plan
détaillé écrit contre une spécification qui n'a pas atterri serait de la
fiction.

### Ce qui est réellement couplé à la version

Le point le plus souvent mal compris à propos de ce paquet :

!!! warning "La validation est multi-version. La couche de modèles ne couvre que 3.3."
    `doc.validate(version="3.1")` fonctionne vraiment. `ddi_l.models.*` est un
    **modèle DDI 3.3** qui se trouve aussi valider des documents 3.1 et 3.2.
    Ajouter `"3.4"` à `SUPPORTED_SCHEMA_VERSIONS` vous apporterait la
    validation, et rien d'autre.

| Point de couplage | Où | Notes |
| --- | --- | --- |
| XSD intégrés | `src/ddi_l/schemas/ddi/v3_1/`, `v3_2/`, `v3_3/` | Livres dans la roue ; résolus via `importlib.resources` |
| Versions prises en charge | `_schema_versions.SUPPORTED_SCHEMA_VERSIONS` | Pilote `normalize_version()` et le `--version` de la CLI |
| Modèles d'espaces de noms | `_schema_versions._SCHEMA_NAMESPACE_TEMPLATES` | Suppose que chaque espace de noms est `ddi:{module}:{suffix}` |
| Sommes de contrôle | `_schema_versions.SCHEMA_ARCHIVE_CHECKSUMS` | SHA-256 par version ; vérifiée au téléchargement |
| Rafraîchissement | `schema_sync.update_schema_package()` | Télécharge et réécrit une arborescence `v3_x/` |
| Détection de version | `schema_loader/_versions.py` | Déduit la version depuis l'espace de noms ou `schemaLocation` |
| **Point d'entrée de la génération** | `codegen/xsd_introspect.py` | **Figé sur 3.3** : `SCHEMA_DIR = .../v3_3`, `ENTRY_SCHEMA = instance_3_3.xsd`, et une table d'espaces de noms littérale |

### Voie A : une nouvelle version mineure DDI 3.x

Cette voie est balisée ; 3.1 et 3.2 ont toutes deux été ajoutées ainsi.

1. Enregistrez le SHA-256 de l'archive dans `SCHEMA_ARCHIVE_CHECKSUMS`.
2. Lancez `update_schema_package("3.x")` pour peupler
   `src/ddi_l/schemas/ddi/v3_x/`.
3. Ajoutez la version à `SUPPORTED_SCHEMA_VERSIONS`.
4. Vérifiez que la convention `ddi:{module}:{suffix}` tient toujours. Si la
   version ajoute un espace de noms, `tests/test_schema_versions.py` échouera :
   il dérive l'ensemble attendu des XSD livres plutôt que de faire confiance à
   la liste écrite à la main.
5. Décidez **explicitement** si la couche de modèles générée passe à la nouvelle
   version. Ce n'est ni automatique ni gratuit : régénérer contre un nouveau XSD
   modifie `_FIELD_XML_MAP`, `_ATTR_XML_MAP` et `_ELEMENT_ORDER`, donc la sortie
   sérialisée, donc l'ensemble des fixtures de référence sous
   `src/ddi_l/examples/tests/fixtures/`. Traitez cela comme un changement
   cassant.

### Voie B : DDI 4.0

Ne supposez pas qu'il s'agit de la voie A avec un numéro plus grand. Cette
section consigne ce que dit le modèle **DDI Lifecycle 4.0 bêta 4**, lu dans
l'étiquette `v4.0-beta.4` (janvier 2026) de
[ddialliance/ddimodel](https://github.com/ddialliance/ddimodel), la version que
la DDI Alliance a présentée comme la
[dernière bêta avant l'examen public](https://ddialliance.org/news/ddi-lifecycle-v4.0-beta-4-review).
Ce sont des faits sur une bêta : revérifiez chacun contre la version finale
avant de construire dessus.

**Générer à partir du modèle, pas du XSD.** 4.0 part du modèle. Sa source est
un ensemble de fichiers CSV gérés avec COGS (le Convention-based Ontology
Génération System de la DDI Alliance), et le XML Schéma n'est qu'un des quelque
douze formats que COGS en génère, avec JSON Schéma, OWL, SHACL, ShEx, UML XMI,
LinkML et une bibliothèque C#. `codegen/xsd_introspect.py` pourrait introspecter
le XSD publié, mais les CSV en disent davantage :

| Source | Contenu |
| --- | --- |
| `ItemTypes/<Nom>/<Nom>.csv` | 172 types d'items (les objets identifiables), une ligne par propriété avec son type et sa cardinalité |
| `CompositeTypes/<Nom>/<Nom>.csv` | 320 types de valeurs structurées |
| `ItemTypes/<Nom>/Extends.<Base>` | Héritage : 72 types d'items étendent `Versionable`, 42 `Maintainable`, les autres l'une de neuf autres bases abstraites |
| Colonnes `DeprecatedNamespace`, `DeprecatedElementOrAttribute` | Pour 2 325 des 2 631 propriétés, l'espace de noms 3.3 d'origine et s'il s'agissait d'un élément ou d'un attribut ; les 306 autres sont nouvelles en 4.0 |
| `Topics/` | Huit regroupements : Agent, Classification, Data Capture, Data Description, Foundational et Study, plus les fourre-tout « All Content Items » et « Non-Packaging Items » |

Les colonnes `Deprecated*` sont les plus utiles pour ce paquet : la
correspondance 3.3 vers 4.0 fait partie du modèle, elle n'est pas à
rétro-concevoir.

**La convention d'espaces de noms ne survit pas.** La construction officielle
publie le XSD dans un seul espace de noms, `ddi:instance:4_0`
(`cogs publish-xsd ... --namespace "ddi:instance:4_0"` dans
`build/build-windows.bat`), là où 3.3 en compte dix-sept. `_build_release()`
formate chaque espace de noms depuis un modèle unique `ddi:{module}:{suffix}`,
et le générateur écrit un module Python par espace de noms : ni l'un ni l'autre
ne se transpose. 4.0 a besoin de sa propre description de version, et les
modules générés d'une autre clé de regroupement : les thèmes du modèle, ou
l'espace de noms 3.3 majoritaire de chaque type d'après les colonnes
`Deprecated*`, ce qui garderait les noms de modules actuels.

**L'inclusion devient référence.** Une propriété dont le type est un type
d'item est une référence, et 635 propriétés le sont. Un `VariableScheme` 4.0
liste des `VariableReference` au lieu de contenir des éléments `Variable` : les
items sont autonomes et les schémas pointent vers eux. Les modèles écrits à la
main supposent l'imbrication 3.3 (un `Document` parcourt `StudyUnit` →
`LogicalProduct` → `VariableScheme` → `Variable`) ; c'est donc le changement de
plus grande portée, bien au-delà d'un renommage.

**Identification.** Chaque item 4.0 a une `URN` obligatoire en plus de
`Agency`, `ID` et `Version` (`Settings/Identification.csv` et
`Identification.Mixin.csv`). La mécanique de référence 3.3 s'y transpose, mais
l'URN n'est plus facultative.

**Un successeur, avec un long chevauchement.** La DDI Alliance présente 4.0
comme le contenu de 3.3 dans une structure qui prend en charge plusieurs
syntaxes : il succède à 3.3 au lieu de coexister avec lui comme DDI-CDI. Les
fichiers 3.3 resteront en usage des années, donc la conclusion ne change pas :
ajouter un second paquet de modèles à côté de l'existant plutôt que migrer
`ddi_l.models`, ce qui casserait tous les consommateurs sans rien apporter à
ceux qui ont encore des données 3.3.

**La fidélité de l'aller-retour reste ouverte.** Le passthrough
`other_elements` / `other_attributes` et les fixtures de référence sont les
garanties sur lesquelles ce paquet est bâti. Le modèle ne dit rien de leur
transposition ; tranchez avant de prototyper.

#### Ordre de travail suggéré

1. **Attendre la version finale.** Les propriétés et types de la bêta peuvent
   encore changer.
2. **Validation seule.** Intégrer le XSD 4.0, ajouter une description de
   version qui contourne le modèle d'espaces de noms 3.x, apprendre à
   `schema_loader/_versions.py` l'espace de noms `ddi:instance:4_0`, et ajouter
   `"4.0"` à `SUPPORTED_SCHEMA_VERSIONS`. C'est la voie A plus cette seule
   exception, et cela donne `validate(version="4.0")` sans toucher aux modèles.
   Prenez les noms de fichiers et le schéma d'entrée dans le paquet publié ;
   ils ne figurent pas dans le dépôt du modèle.
3. **Modèles.** Ajouter à `codegen/` une seconde entrée qui lit les CSV COGS à
   une étiquette `ddimodel` figée et écrit les bases générées dans un paquet
   distinct (par exemple `ddi_l.models_v4`), en réutilisant la table de types
   de `generate_model_bases.py`. Laisser le pipeline 3.3 intact.
4. **Conversion.** Construire une table de correspondance 3.3 ↔ 4.0 à partir
   des colonnes `Deprecated*` et fonder la conversion dessus. Les 306 nouvelles
   propriétés demandent des décisions à la main.

### Invariants à défendre, quelle que soit la voie

Ce sont eux qui font qu'une migration future reste circonscrite au lieu de
devenir une réécriture :

- **Tout ce qui est généré reste derrière `src/ddi_l/models/_generated/`** et
  n'est consommé que comme classes de base. Le code écrit à la main ne doit
  jamais importer les rouages du générateur. Cette couture est ce qui rend le
  remplacement du générateur circonscrit.
- **Le contrôle de dérive reste vert.** Régénérer sur un arbre propre doit être
  sans effet, afin qu'un rafraîchissement de schéma et une modification du
  générateur restent distinguables en revue.
- **`SCHEMA_ARCHIVE_CHECKSUMS` reste renseigné**, pour la même raison.
- **Une seule liste d'espaces de noms.** `codegen/xsd_introspect.py` et
  `_schema_versions.py` énumèrent tous deux les espaces de noms DDI ;
  `tests/test_schema_versions.py` les compare aux schémas livres. Lancez-le si
  vous touchez l'un des deux.

### Espaces de noms synthétiques, et la règle qui les encadré

`_schema_versions._SYNTHETIC_NAMESPACE_TEMPLATES` déclare
`urn:ddi-l:extension:process:1` et `urn:ddi-l:extension:methodology:1`.
**Aucune version de DDI Lifecycle ne déclare l'un ou l'autre.** Ils accueillent
des types de modèles que DDI 3.3 ne définit pas : `Process`, `ProcessStep`,
`ProcessControl`, `ProcessMethod`, leurs schemes, ainsi que `MethodologyItem`,
`MethodologyScheme` et `ReviewEvent`. Le vocabulaire de processus propre à DDI
(`ProcessingEvent`, `ProcessingInstruction`, `ControlConstruct`) se trouve dans
`ddi:datacollection:3_3` et est modélisé séparément.

**La règle : un type qui a une place dans le schéma doit l'utiliser.** Les
espaces de noms synthétiques ne servent qu'au contenu que DDI ne définit pas.
`Methodology`, par exemple, est un élément DDI 3.3 et s'écrit dans
`ddi:datacollection:3_3`.

`tests/test_namespace_provenance.py` vérifie les deux volets : aucun modèle ne
peut émettre un espace de noms en forme de `ddi:` qui ne soit ni déclaré par le
schéma ni enregistré comme synthétique, et aucun type dans un espace de noms
synthétique ne peut porter le nom d'un élément réel des XSD. Ajouter un nouveau
type synthétique impose de l'inscrire explicitement : c'est donc une décision,
pas un accident.

Les espaces de noms synthétiques ne sont délibérément **pas** de la forme
`ddi:`, afin que personne ne les prenne pour des espaces de noms de la DDI
Alliance, et ils ne portent aucune version DDI : toutes les versions pointent
vers le même URI. La détection de version n'utilise que l'espace de noms
`instance` et le nom du fichier de schéma.

## Vue d'ensemble de l'architecture

```text
src/ddi_l/
  __init__.py                # API publique : new_study, open_ddi, Document
  document.py                # Document, DDIDocument, DDIFragment, StudyCursor
  _document_mixins.py        # Comportement de Document decoupe par sujet
  _document_maintainables.py # Helpers de recherche / rattachement
  _document_namespaces.py    # Gestion des espaces de noms pour Document
  models/
    base.py                  # InternationalString, Reference, MaintainableBase
                             # et le moteur generique from_xml / to_xml
    _generated/              # Bases generees (champs uniquement, ne pas editer)
    datacollection/          # Types DataCollection (seul sous-paquet de modeles)
    logicalproduct.py        # Variables, listes de codes, categories, NCubes
    conceptualcomponent.py   # Concepts, univers, variables conceptuelles
    reusable.py, study.py, archive.py, group.py, physical.py, process.py,
    quality.py, comparison.py, methodology.py, classification.py, ...
  schema_loader/             # Resolution des schemas, validation, conversion JSON
  schemas/                   # XSD DDI 3.1 / 3.2 / 3.3 integres (CC-BY-4.0)
  examples/                  # Instances et fixtures d'exemple empaquetees
  validation.py              # Validation de haut niveau
  lint.py                    # Moteur lint et regles
  cli.py                     # Point d'entree CLI (`ddi`)
  io.py                      # Lecture/ecriture bas niveau et streaming
  index.py                   # Index d'identifiants pour find() / references
  registry/                  # Registre des types maintainable
  schema_sync.py             # Rafraichit le lot de schemas integre
```

Répertoires de support hors du paquet : `codegen/` (générateurs à la
construction), `tests/`, `benchmarks/`, `demo/` et `docs/`. Aucun n'est
empaqueté : rien de ce qu'ils contiennent ne peut servir de point d'entrée
console ni être importe à l'exécution.

## Les deux backends XML

`lxml` est un accélérateur optionnel installé avec `ddi-l[full]`. Sa présence
ne doit pas changer ce que `ddi-l` entend par un document, et la différence de
résolution des préfixes entre les deux mérite d'être comprise avant de toucher
à la sérialisation :

- **`ElementTree` (bibliothèque standard)** résout les préfixes au moment de la
  *sérialisation*, depuis un registre global au processus. Un préfixe
  enregistré en écrivant un document affecte tous les suivants dans le même
  processus.
- **`lxml`** résout depuis le `nsmap` de chaque élément, **figé à la création
  de l'élément**. Il ne peut pas être redéfini sur place, d'où le fait que
  `apply_namespace_map()` renvoie une racine au lieu d'en muter une.

Cette asymétrie est la source la plus fréquente de comportements propres à un
backend : lancez la suite sur les deux backends quand vous touchez à la
sérialisation.

### Ce qui est garanti

- **Les documents produits par `ddi-l` sont sérialisés en octets identiques sur
  les deux backends.** Chaque espace de noms DDI reçoit son préfixe canonique,
  et les déclarations sont hissées sur la racine. `tests/test_backend_parity.py`
  le vérifie.
- **Un aller-retour ne modifie jamais le contenu**, sur l'un ou l'autre
  backend : mêmes éléments, mêmes noms qualifiés, mêmes attributs, même texte.

### Ce qui n'est pas garanti

L'aller-retour d'un fichier tiers dont les espaces de noms sont disposés
autrement que les nôtres (racine préfixée et redéclarations `xmlns=` par
élément, comme dans le `Quality_of_Life.xml` livré) peut différer par
l'*écriture des préfixes* entre les backends. lxml reproduit la disposition
source ; la bibliothèque standard la canonise sur la racine. Les documents sont
sémantiquement identiques.

Obtenir l'égalité octet par octet imposerait de reconstruire, dans `write()`,
chaque sous-arbre qui porte son propre `nsmap` : un coût réel sur le chemin le
plus chaud pour une question de préfixes. Toute modification doit garder la
bibliothèque standard sur les préfixes canoniques `c:`/`d:`/`l:` ; mesurez les
deux backends sur `Quality_of_Life.xml` et `example_instance.xml`.

## Schémas intégrés

Les XSD DDI sont livres dans le paquet, sous `src/ddi_l/schemas/`, afin que la
validation fonctionne hors ligne depuis un simple `pip install ddi-l`.
Résolvez-les toujours via `importlib.resources`
(`resources.files("ddi_l.schemas")`), jamais via un chemin relatif à la racine
du dépôt : un tel chemin fonctionne dans un clone et casse dans une roue
installée.

Les schémas sont sous licence CC-BY-4.0 de la DDI Alliance. `license.txt` et
`readme.txt` sont redistribués avec eux pour satisfaire l'attribution et
doivent rester dans la distribution.

## Documentation

Le site utilise MkDocs avec le thème Material et un support bilingue (EN/FR).
Les pages vont par paires `.en.md` / `.fr.md` : **mettez à jour les deux**
lorsque vous modifiez du contenu destiné aux utilisateurs.

```bash
make docs-serve    # Prévisualisation en direct
make docs-build    # Construction et validation
```

Le logo, le favicon et leurs règles d'usage sont décrits dans les
[ressources de marque](assets/README.md).

La page des [corrigés](curriculum/answer-keys.md) du programme est générée par
`hooks/answer_keys.py` à partir des réponses `??? success` de chaque module.
Ajoutez ou modifiez une réponse dans le module, jamais sur la page des
corrigés.

Préférez les cibles `make` à un appel direct de `mkdocs` : elles définissent
`NO_MKDOCS_2_WARNING`, sans quoi chaque invocation affiche un avertissement de
plusieurs lignes des auteurs de Material for MkDocs au sujet de MkDocs 2.0.

### Versions de la chaîne de documentation

`uv.lock` fige les versions exactes ; l'intégration continue et le déploiement
installent avec `uv sync --locked --group docs`. `mkdocs` et `mkdocs-material`
sont plafonnés sous leur prochaine version majeure dans `pyproject.toml`, afin
qu'une nouvelle majeure soit adoptée délibérément ; Dependabot propose cette
mise à jour sous forme de pull request testée. `tests/test_docs_site_config.py`
vérifie que chaque plugin activé dans `mkdocs.yml` est fourni par le groupe
`docs`.

### Le sélecteur de version n'apparaît que sous `mike`

`extra.version.provider: mike` fait récupérer `versions.json` par le thème, en
le résolvant comme `../versions.json` relativement à la base du site, car
`mike` publie chaque version sous `<site_url>/<version>/` et place le manifeste
à côté.

C'est correct en production et faux en local. Un simple `mkdocs serve` ne
construit aucune version : la base reste `/ddi-l/` et `../versions.json` dépasse
vers `/versions.json`, que rien ne sert : une 404 à chaque chargement de page,
pour un sélecteur qui ne pourrait de toute façon pas fonctionner en local.

`hooks/version_selector.py` retire `extra.version` sauf si `MIKE_DOCS_VERSION`
est définie (la variable que `mike` exporte quand il pilote la construction.
Pour prévisualiser le sélecteur lui-même, lancez `uv run mike serve`, ou
définissez la variable à la main.

### Pourquoi le journal de construction est court

`mkdocs-static-i18n` journalise, en INFO, la valeur entière par laquelle il
remplace chaque clé de configuration, une fois par langue, à chaque
reconstruction. Pour `nav`, c'est tout l'arbre de navigation : une construction
affichait donc plusieurs milliers de caractères de configuration recopiée autour
des cinq lignes utiles.

`hooks/quiet_i18n_logs.py` filtre exactement ces enregistrements
`Overriding`/`Updating … config …`. La ligne `Building '<lang>' documentation to
directory: …` est conservée, et rien au niveau WARNING ou au-dessus n'est
touché ; un véritable `Unknown '<lang>' config override` remonte toujours.
Lancez `mkdocs serve --verbose` pour tout revoir.

Le filtre est attaché au *handler* du logger `mkdocs`, et non au logger du
plugin. Python consulte les handlers d'un logger ancêtre lorsqu'un
enregistrement se propage, mais pas ses filtres, et le plugin journalise depuis
ses sous-modules : un filtre sur `mkdocs.plugins.mkdocs_static_i18n` ne ferait
donc silencieusement rien.

### `VIRTUAL_ENV does not match the project environment path`

Un avertissement de uv, pas un réglage du projet : rien dans ce dépôt ne choisit
un chemin d'environnement. Il signifie que votre shell a un virtualenv actif
tandis que uv résout celui du projet ailleurs, généralement parce que
`UV_PROJECT_ENVIRONMENT` est définie dans votre profil. Annulez-la, pointez-la
vers le `.venv` de ce dépôt, ou passez `--active` pour que uv utilise
l'environnement actuellement activé.

## Publier une version

Les versions sont publiées sur PyPI par `.github/workflows/publish.yml` au moyen
de la [publication de confiance](https://docs.pypi.org/trusted-publishers/)
(OIDC, sans jeton d'API), avec des attestations PEP 740.

### Configuration initiale

1. Sur [PyPI](https://pypi.org/manage/account/publishing/) et
   [TestPyPI](https://test.pypi.org/manage/account/publishing/), ajoutez un
   éditeur de confiance en attente pour le projet `ddi-l` : propriétaire
   `pbisson44`, dépôt `ddi`, workflow `publish.yml`, environnement `pypi`
   (TestPyPI : `testpypi`).
2. Dans les paramètres du dépôt GitHub, créez les environnements `pypi` et
   `testpypi`. Protégez `pypi` par des relecteurs obligatoires.

### À chaque version

1. Fixez la version dans `pyproject.toml` et `CITATION.cff`, et réglez
   `date-released` dans `CITATION.cff` sur la date de publication.
   `tests/test_release_metadata.py` vérifie leur concordance.
2. Datez le titre dans `docs/release-notes.en.md` et `docs/release-notes.fr.md`.
3. Lancez les contrôles locaux : `uv run make release-check` et la suite de
   tests complète.
4. Essai à blanc : déclenchez **Publish to PyPI** depuis l'onglet Actions avec
   la cible `testpypi`, puis installez depuis TestPyPI dans un environnement
   propre :

    ```bash
    pip install --index-url https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple/ ddi-l
    ```

5. Publiez une GitHub Release avec l'étiquette `vX.Y.Z`. Le workflow construit
   les distributions, vérifie que l'étiquette correspond à la version du
   paquet et publie sur PyPI ; le workflow de documentation publie la
   documentation versionnée.

## Soumettre des modifications

1. Forkez le dépôt et créez une branche.
2. Écrivez ou mettez à jour les tests.
3. Mettez à jour les pages anglaise et française pour tout changement visible.
4. Exécutez les contrôles qualité ci-dessus.
5. Commitez avec des messages clairs.
6. Ouvrez une pull request avec un résumé et les références d'issues.
