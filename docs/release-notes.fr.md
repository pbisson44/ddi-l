---
description: >-
  Ce qui a changé dans chaque version de ddi-l, y compris les changements
  incompatibles tant que la version est 0.x.
---

# Notes de version

## Non publié

### Documentation

- **Les liens sans version ne renvoient plus d'erreur 404.** Le README et le
  modèle de ticket passent par `/latest/`, et la racine du site sert désormais
  un `404.html` qui redirige tout chemin sans version (`/ddi-l/server/`) vers
  la même page sous `/latest/` et renvoie les pages renommées du programme
  vers leur nouveau nom.
- **Installation depuis PyPI partout.** Les pages qui indiquaient
  `pip install .` ou `pip install -e .` indiquent maintenant
  `pip install ddi-l`, et les onglets d'installation ajoutent `uv add ddi-l`.
- **Un seul endroit pour apprendre.** Le site s'organise en Apprendre (le
  programme), Guides pratiques, Référence et À propos. Le tutoriel de
  rédaction, les laboratoires et les parcours par profil sont intégrés au
  programme, qui a désormais un seul ensemble de profils d'apprenants et un
  parcours automatisation.
- **Ordre du programme.** L'ouverture de fichiers et la validation en ligne de
  commande passent aux modules 6 et 7, et le module 3 vérifie désormais le
  travail avec `doc.validate()` et `doc.lint()`, pour que les apprenants
  valident dès le départ. Les modules 6 à 13 deviennent 8 à 15.
- **Réponses sous chaque exercice.** Chaque exercice a une réponse
  repliable. La page des corrigés pour les instructeurs est générée à partir
  des modules et ne peut donc plus s'en écarter.
- **Page d'accueil.** Un premier exemple sans avertissement de lint, ce
  qu'est le DDI, la prise en charge de DDI 3.1, 3.2 et 3.3, un schéma d'une
  étude, une tuile Apprendre, une tuile R / API HTTP et une section « Citer
  ddi-l ». Chaque page a désormais sa propre description pour les moteurs de
  recherche.

## 0.1.0

La première version de `ddi-l` : une boîte à outils Python pour créer, lire,
mettre à jour et valider des documents XML
[DDI Lifecycle 3.3](https://ddialliance.org/Specification/DDI-Lifecycle/3.3/),
avec une API CRUD simple posée sur une couche de modèles générée depuis les XSD.

### Rédaction

- **API CRUD simple** : `ddi.new_study()`, `ddi.open_ddi()` et la classe
  `Document` avec `add_question()`, `add_variable()`, `add_concept()`,
  `add_universe()`, `add_code_list()`, `add_item()`, `find()`, `remove()`,
  `save()` et `validate()`. Chaque méthode `add_*` accepte un `label=`
  optionnel (et `label_lang=`), de sorte qu'un objet peut être libellé là où il
  est créé plutôt qu'en seconde passe. C'est la différence entre une sortie
  qui passe le lint sans rien signaler et une sortie qui se signale elle-même.
- **`add_item()` / `items()` génériques** : 30 types d'éléments DDI
  (QuestionItem, Variable, Category, Instrument, Concept, Universe, et
  d'autres) via un registre de types unique.
- **Représentations de variables** : `Variable.set_numeric()`, `set_coded()`,
  `set_text()` et `set_datetime()` déclarent le type de valeurs que porte une
  variable, avec des plages numériques optionnelles (`low_inclusive` /
  `high_inclusive`), `missing_values`, `blank_is_missing_value`, ou une
  référence vers une liste de codes. Ces setters s'enchaînent sur
  `add_variable()`.
- **Propriétés personnalisées** : `set_property()`, `get_property()`,
  `properties` et `remove_property()` sur tout élément DDI.
- **Versionnement** : `increment_major_version()`, `increment_minor_version()`,
  `increment_subversion()`, justifications de version et responsabilité de
  version.
- **Support multilingue** : un paramètre `lang=` sur toutes les méthodes
  `add_*`, et `InternationalString` pour les traductions supplémentaires.

### Structure d'étude

- **Séries multi-études** : `doc.add_study()` ajoute d'autres études au
  groupe. `doc.study(identifier)` renvoie un `StudyCursor` dont
  `add_variable()`, `add_question()` et les autres helpers `add_*` ciblent
  cette étude précise : les études non primaires sont donc éditables via l'API
  de haut niveau. `doc.study()` sans argument cible l'étude primaire.
- **Groupes d'études** : `doc.add_group()` organise une étude dans un
  `<g:Group>` (une série d'études ou un lot de publication). Le document reste
  pleinement éditable, et les fichiers organisés en groupe s'ouvrent et font
  l'aller-retour.
- **Paquets au niveau instance** : `doc.add_resource_package()` et
  `doc.add_local_holding_package()` attachent un `ResourcePackage` (métadonnées
  réutilisables) ou un `LocalHoldingPackage` (une détention locale d'une étude
  déposée, référençant l'étude primaire par défaut) directement sur la
  `DDIInstance` ; `doc.resource_packages` / `doc.local_holding_packages` les
  relisent.
- **Archive** : `doc.add_archive()` attache un module `Archive` (métadonnées
  de cycle de vie d'archive) à l'étude primaire ; `doc.archives` les relit.
- **Informations de traduction** :
  `doc.add_translation_information(languages=..., description=...)` définit la
  `TranslationInformation` de l'instance ; `doc.translation_information` la
  relit.
- **Comparaisons** : `doc.add_comparison()` enregistre des cartes
  d'harmonisation entre éléments, d'une étude ou d'une version à l'autre :
  `add_variable_map()`, `add_concept_map()`, `add_managed_item_map()`,
  `add_representation_map()`, un constructeur `correspondence()`, et les
  arguments `source_scheme` / `target_scheme` / `correspondence` sur les
  helpers de carte.
- **Profils DDI** : `doc.add_ddi_profile()` attache un `DDIProfile` déclarant
  quels éléments DDI un système utilise, via des énoncés XPath `add_used()` /
  `add_not_used()`.

### Description des données

- **Relations de données** : `doc.add_data_relationship()` construit une
  `DataRelationship` dont `add_logical_record()` déclare quelles variables
  composent un cas (le défaut rectangulaire).
- **NCubes** : `doc.add_ncube()` construit un cube multidimensionnel ;
  `add_dimension(variable_ref)` ajoute un axe, `add_measure(variable_ref)`
  ajoute une valeur mesurée et `add_attribute()` ajoute une variable
  qualifiante. `add_coordinate_region()` et `add_dimension_value()` décrivent
  une région du cube, et `add_attribute(..., attachment_region=)` s'y attache.
- **Instances physiques** : `PhysicalInstance` est un type `add_item` de
  premier ordre au niveau de l'étude, décrivant un fichier de données concret
  avec `set_data_file()`, `set_record_count()` et `set_citation_title()`.
- **Dispositions d'enregistrement** : `doc.add_record_layout()` associe les
  variables à des positions dans un fichier de données via
  `add_data_item(variable_ref, start_position=, width=)`, qui accepte aussi
  `storage_format`, `delimiter` et `decimal_positions`. Passez
  `logical_record=` pour lier la structure sous-jacente à un enregistrement
  logique modélisé. `PhysicalStructure.link_logical_record(..., key_variable=)`
  déclare une clé de segment.
- **Jeux de données en ligne** : `doc.add_dataset()` stocke les valeurs
  directement dans le document, sous forme `ItemSet` (`add_item_value()`),
  `RecordSet` (`set_variable_order()` / `add_record()`) ou `VariableSet`
  (`add_variable_item()`).

### Questionnaires

- **Constructions de flux** : `QuestionConstruct`, `Sequence`, `IfThenElse`,
  `StatementItem`, `ComputationItem` et `Loop` sont des types `add_item()` de
  premier ordre, stockés dans un `ControlConstructScheme` construit, sérialisé
  et rejoue automatiquement, et reliés entre eux par `.to_reference()`.

### Validation et qualité

- **Validation de schéma hors ligne** : les XSD DDI 3.1, 3.2 et 3.3 sont
  livres dans le paquet : `doc.validate()` et `ddi validate` fonctionnent sans
  accès réseau ni téléchargement séparé.
- **Lecture de DDI 3.1, 3.2 et 3.3** : `read_ddi()`, `ddi validate`,
  `ddi lint`, `ddi to-json` et `ddi roundtrip` détectent la version déclarée
  par le document. L'API de rédaction `Document` et les modèles types ciblent
  DDI 3.3 ; les documents 3.1 et 3.2 se manipulent en XML via
  `DDIDocument.root`.
- **Moteur de lint** : `ddi lint` et `Document.lint()` vérifient l'intégrité
  des références, les libellés manquants et la complétude des citations. La
  règle des libellés suit le schéma : elle n'exige un libellé que là où le
  modèle de contenu prévoit un emplacement `r:Label` (174 des 1247 éléments de
  DDI 3.3). La règle sur les langues de citation compare des plages de langue
  selon le RFC 4647 : un `en` requis est satisfait par `en`, `en-CA` ou
  `en-Latn-CA`, mais pas par `eng`.
- **Une sortie propre au lint par défaut** : l'API `Document` libellé les
  modules, schemes et conteneurs physiques qu'elle crée, et chaque méthode
  `add_*` accepte `label=`. `set_scheme_label()` libellé n'importe quel
  conteneur de scheme généré. Un document *lu* n'est jamais modifié.
- **Des valeurs par défaut adaptées à une bibliothèque publiée** : la liste
  blanche d'agences est optionnelle (`configure_lint(allowed_agencies=[...])`
  ou `--allowed-agency`) ; une agence *absente* est toujours une erreur.
  `ddi lint` ne renvoie un code non nul que pour les erreurs ; utilisez
  `--fail-severity warning` pour un contrôle strict.
- **Des libellés seulement là où le schéma les autorise** : la prise en
  charge des libellés est dérivée des XSD. Poser un libellé sur un type sans
  emplacement `r:Label` émet un avertissement au lieu de produire un document
  invalide.
- **Vérification des références** : `Document.save()` signale en un seul
  `DDIReferenceWarning` les références vers des éléments absents de l'étude.
- **Des erreurs claires** : un XML mal forme lève `DDIParseError` avec la
  ligne et la colonne de l'analyseur ; une référence introuvable lève
  `DDIReferenceError` (un `LookupError`) ; un identifiant en double lève
  `DuplicateIdentifierError`, et un nom vide ou non textuel est refusé des
  l'ajout. Les échecs de schéma lèvent `SchemaValidationError`, un
  `DDIValidationError` dont `.issues` porte le détail des problèmes.
- **Des exemples qui passent nos propres contrôles** : les fichiers livres
  `example_instance.xml` et `Quality_of_Life.xml` sont valides selon le schéma
  et exempts d'erreurs de lint ; `example_instance.xml` n'a aucun signalement,
  quelle que soit la sévérité.
- **`Methodology` utilise l'espace de noms de DDI** : `<Methodology>` est
  écrit dans `ddi:datacollection:3_3`, comme le déclare DDI 3.3.
- **Les types d'extension sont visiblement les nôtres** : les quelques types
  `Process` et `Methodology` qu'aucune version de DDI Lifecycle ne définit sont
  sérialisés dans `urn:ddi-l:extension:*` : rien ne peut être confondu avec un
  espace de noms DDI officiel.
- **Fidélité de l'aller-retour** : les éléments et attributs XML inconnus sont
  préservés à l'ouverture et à la re-sauvegarde.
- **Le backend `lxml` est un choix de performance, pas un dialecte** : les
  documents produits par `ddi-l` sont sérialisés en octets identiques avec et
  sans `ddi-l[full]`. Un fichier tiers dont les espaces de noms sont disposés
  autrement (racine préfixée et redéclarations `xmlns=` par élément, comme dans
  `Quality_of_Life.xml`) peut différer par l'écriture des préfixes entre les
  backends ; son contenu est identique.

### Performance

- `import ddi_l` charge les noms à la première utilisation : importer le paquet
  et lancer la commande `ddi` prennent quelques centièmes de seconde.
- `read_ddi()` construit son index de résolution à la demande.
- Avec `ddi-l[full]`, la validation vérifie d'abord le document avec libxml2 et
  ne lance le validateur détaillé xmlschema qu'en cas d'échec : un document
  valide est valide en quelques millisecondes, et les anomalies signalées sont
  identiques sur les deux moteurs.
- `iter_variables()`, `iter_questions()` et `iterparse_ddi()` parcourent les
  gros documents en flux et fournissent des objets complets.
- Voir [Performance](performance.md) pour les temps mesures.

### API HTTP

- **Service Litestar optionnel** : `pip install 'ddi-l[server]'` puis
  `ddi serve` expose la validation, l'analyse et la conversion via HTTP, avec la
  documentation OpenAPI sur `/schema`. Chaque point de terminaison est une fine
  enveloppe autour de `ddi_l.operations`, que la ligne de commande appelle
  également : les deux ne peuvent pas diverger sur la validité d'un document.
- **OpenAPI qui se décrit lui-même** : `/schema` sert Swagger UI, et un
  navigateur qui ouvre la racine y est redirigé. Chaque point de terminaison
  déclare son corps de requête, ses paramètres de requête et un schéma de
  réponse type avec un exemple réel ; « Try it out » est prérempli avec une
  instance DDI valide.
- **Des valeurs par défaut adaptées à un service** : corps de requête plafonné
  à 32 Mio, nombre de traitements simultanés borne (`--max-jobs`, `503`
  au-delà), schéma par défaut chargé au démarrage, aucune écriture disque, CORS
  désactivé sauf origines nommées, et le même durcissement XML que la
  bibliothèque.
- **Sortie JSON-LD** : `POST /v1/convert/jsonld` et `ddi to-jsonld` restituent
  une étude en données liées à l'aide du vocabulaire DDI-RDF Discovery
  (« Disco ») de la DDI Alliance, avec Dublin Core et SKOS pour les libellés et
  les URN DDI comme IRI. Couvre le sous-ensemble de découverte de DDI et
  fonctionne à sens unique, conformément à la spécification Disco ; `to-json`
  reste le format sans perte et réversible (XML vers JSON puis retour rend
  exactement les octets fournis, tout comme `/v1/roundtrip`).
- **`ddi_l.operations`** : le coeur indépendant du transport, utilisable
  directement pour intégrer ddi-l dans une autre application.

### Couche de modèles

- **Génération des modèles depuis les XSD** : chaque classe de modèle est
  générée depuis le XSD officiel DDI 3.3, source unique de vérité pour les
  champs, l'ordre des éléments, les espaces de noms et la documentation. Les
  508 types complexes du XSD sont couverts.
- **Moteur XML générique** : `from_xml()` / `to_xml()` pilote par les tables
  générées `_FIELD_XML_MAP`, `_ATTR_XML_MAP` et `_ELEMENT_ORDER`, émettant les
  enfants dans l'ordre déclaré par le XSD.
- **Préfixes d'espaces de noms DDI stables** : la sortie utilise les préfixes
  canoniques `r:`, `s:`, `d:`, `l:`, `c:`, `a:`, `p:`, `pr:` (ddiprofile) et
  `prc:` (process) plutôt que des noms générés `ns0`/`p0`, et la sérialisation
  préfère le préfixe enregistré d'un espace de noms à un préfixe auto-généré.
- **Constantes d'espaces de noms** : exportées pour chaque module DDI, y
  compris `DDI_PROFILE_NS` et `DATASET_NS`.
- **Type** : livre `py.typed` ; l'API publique est entièrement annotée.

### Outils et distribution

- **CLI** : `ddi validate`, `ddi lint`, `ddi to-json`, `ddi to-jsonld`,
  `ddi from-json`, `ddi roundtrip`, `ddi versions` et `ddi serve`. Les
  commandes acceptent `-o/--output` et `--ddi-version` ; `ddi validate --format
  json` produit un tableau JSON (vide si le document est valide) pour les
  scripts.
- **Backend lxml optionnel** : `pip install ddi-l[full]` active une analyse
  plus rapide des gros documents.
- **Référence d'API générée** à partir des docstrings du code source, en plus
  des guides.
- **Chaque exemple de code documenté est exécuté en CI**, y compris les
  exemples R.
- **Python 3.11, 3.12, 3.13 et 3.14** pris en charge et testés en CI.
- **Publication PyPI** via la publication de confiance OIDC de GitHub.
- **Documentation bilingue** en anglais et en français, dont un guide pour
  [utiliser ddi-l depuis R](r-users.md) avec reticulate.
- **Cursus de formation** : un cours progressif de 16 modules avec exercices,
  quiz, guide de l'instructeur, corrigés et aide-mémoire bilingue.
