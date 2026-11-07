---
description: >-
  Ce qui a changé dans chaque version de ddi-l, y compris les changements
  incompatibles tant que la version est 0.x.
---

# Notes de version

## 0.2.0 (non publiée)

### Changements de comportement

- **Le noyau XML natif vient avec ddi-l.** `pip install ddi-l` installe aussi
  `ddi-l-native`, et ddi-l lit et écrit le XML avec lui avant lxml : une
  installation avec l'extra `full` utilise désormais le noyau natif. Les
  résultats sont les mêmes ; `DDI_L_XML_BACKEND=lxml` garde lxml. Sur une
  plateforme sans wheel compilée, pip installe un remplaçant en Python pur et
  rien ne change ; voir [quels extras prendre](installation.fr.md#extras-quand-en-prendre-un).
- **Un fichier lu est réécrit tel que lu.** `write_ddi()`, `save()`,
  `to_xml()`, `ddi roundtrip` et `POST /v1/roundtrip` écrivent un document lu
  dans un fichier ou des octets avec chaque élément inchangé tel qu'il a été
  lu, octet pour octet : ses guillemets, références de caractères, sections
  CDATA, commentaires, préfixes et indentation. Seuls les éléments nouveaux
  ou modifiés sont mis en forme, comme le fichier qui les entoure (la mise en
  forme de Colectica dans une `FragmentInstance`, l'indentation du fichier
  sinon). Les éléments sont reconnus par leur contenu : un élément déplacé,
  copié ou reconstruit sans changement à partir de son modèle garde ses
  octets. Avant, seule une `FragmentInstance` déjà dans la mise en forme de
  Colectica revenait inchangée, et une `DDIInstance` revenait dans la mise en
  forme de cette bibliothèque. Une `DDIInstance` dont le fichier lie un
  espace de noms DDI à un autre préfixe (`p0`, `ns1`) est toujours remise en
  forme par `save()` et `to_xml()`, avec les préfixes canoniques (`c`,
  `s`...). Passez `layout="colectica"` ou `layout="default"` (`--layout`,
  `?layout=`) pour remettre en forme tout le fichier comme avant ;
  `DDIFragment.save()` utilise désormais `layout=None` par défaut pour la
  même raison. Un document garde les octets dont il a été lu : il occupe
  donc aussi en mémoire la taille du fichier.
- **`conform` décide les filtres et les contrôles exactement quand l'extra
  `logic` est installé.** Un filtre écrit autrement qui concorde toujours
  avec celui de la spécification (`PetCount > 0` et `PetCount >= 1`, pour
  une question dont le domaine n'a pas de décimales) n'est plus
  `spec.gate.different`, et un filtre de page se trouve de la même façon. Un
  constat `spec.gate.different` ou `spec.edit.different` nomme un répondant
  sur lequel les deux divergent, dans son message (« (they differ when
  PetCount is 1) ») et dans un nouveau champ `example`, que la sortie JSON
  n'a que s'il est rempli. Les domaines de réponse et les types de variables
  de la spécification disent ce qu'est chaque nom.
  `ddi conform --semantics syntactic` (`conform(semantics="syntactic")`)
  compare les formes normales, comme avant ; `--semantics smt` demande
  l'extra.
- **`equivalent()` calcule quand l'extra `logic` est installé.** Des
  filtres écrits différemment qui concordent toujours sont équivalents :
  `x + 1 > 3` et `x > 2`. `equivalent(exact=False)` ne compare que les
  formes normales, comme avant ; sans l'extra, rien ne change.
- **La validation par le schéma signale toutes les erreurs.** `validate()`
  et ce qui s'appuie dessus (`ddi validate`, `Document.validate()`,
  `POST /v1/validate`) signalaient la première erreur et s'arrêtaient. Ils
  les signalent maintenant toutes, puis les avertissements. Une erreur
  trouvée avant la lecture du schéma, comme une identification manquante,
  reste signalée seule. `validate(max_issues=)` s'arrête après ce nombre
  d'erreurs et un avertissement le dit ; l'API HTTP s'arrête à
  `ServerConfig.max_schema_issues` (100 par défaut).
- **La configuration du lint vaut pour un appel.** `run_lint()`,
  `run_profile()`, `document.lint()` et les fonctions `validate_*()`
  acceptent une `configuration` issue du nouveau `lint_configuration()`, pour
  ce seul appel ; `configure_lint()` fixe toujours la valeur par défaut des
  appels qui n'en reçoivent pas. `ddi lint` ne modifie plus cette valeur par
  défaut : appeler `cli.main()` deux fois dans un même processus ne reporte
  plus les options du premier appel sur le second.
- **Un réglage limité à un bloc reste dans son fil d'exécution ou sa
  tâche.** `ddi.configured()` modifiait la valeur par défaut de tout le
  processus pendant son bloc `with`, si bien que les autres fils d'exécution
  la voyaient. Il ne vaut plus que pour son propre fil ou sa propre tâche ;
  `ddi.configure()` fixe toujours la valeur par défaut de tous les fils.
- **ddi-l n'écrit plus dans le registre d'espaces de noms d'ElementTree.**
  Avec le moteur de la bibliothèque standard, les préfixes qu'enregistrait un
  document allaient à `ElementTree.register_namespace`, que tout le processus
  partage : le reste du code utilisant ElementTree les voyait, et les autres
  fils aussi. Ils sont désormais gardés pour le fil ou la tâche courante, et
  l'écrivain nomme les espaces de noms à partir d'eux. La sortie d'un même
  fil ne change pas ; un document construit dans un fil et écrit avec une
  mise en page dans un autre écrit `ns0`, `ns1`... pour les préfixes
  enregistrés seulement dans le premier.
- **Le moteur de validation se choisit à chaque appel.**
  `schema_loader.validate()` accepte `backend="python"` ou `"lxml"`, et le
  nouveau `schema_loader.validation_backend()` en impose un dans un bloc
  `with`, pour son propre fil ou sa propre tâche.
  `set_validation_backend()` fixe toujours la valeur par défaut de
  l'application, que renvoie le nouveau `get_validation_backend()`.
  `VALIDATION_IMPLEMENTATION` désigne désormais le meilleur moteur disponible,
  fixé à l'importation ; il ne suit plus `set_validation_backend()`.
- **`lint.ALLOWED_AGENCIES` et `namespaces.NAMESPACE_PROFILES` sont en
  lecture seule.** `ALLOWED_AGENCIES` était un ensemble qu'une application
  pouvait modifier sur place, et que la règle sur les agences lisait quand la
  configuration par défaut n'avait pas de liste. C'est désormais une vue figée
  de la configuration par défaut : fixez la liste avec
  `configure_lint(allowed_agencies=[...])`.
- **Un fragment est aussi analysé comme un fragment par HTTP.** `POST
  /v1/lint` et `POST /v1/validate` analysaient une `FragmentInstance` à
  l'intérieur d'une `DDIInstance` fabriquée : une référence pendante y était
  une erreur, alors que `ddi lint` en faisait un avertissement, et une liste
  d'agences autorisées vérifiait l'agence de ce conteneur fabriqué. Les deux
  analysent maintenant le fragment lui-même, comme `ddi lint` : un fragment
  dont le seul problème est une référence pendante est désormais `valid`.
- **De deux copies d'une même version, la première compte partout.** Un
  export qui contient un élément deux fois dans la même version (un
  identifiant partagé) nommait la seconde copie dans les explications de
  conditions, les synopsis et `ddi conform`, et la première partout ailleurs ;
  c'est désormais la première partout.
- **Les constats sur les références sont répartis en trois.**
  `ddi.reference.integrity` exigeait une correspondance exacte de
  `(agency, id, version)` ; sur les exports Colectica, il signalait donc
  chaque référence tardive à un paramètre (écrite en version 1 alors que le
  paramètre est, par exemple, en version 4) et chaque lien `BasedOn` vers
  l'élément dont une copie est issue. Sur l'exemple Colectica fourni, il
  signalait 116 références, dont 2 réellement non résolues. Désormais :
  - une référence `lateBound="true"` se résout vers n'importe quelle version
    de son élément ;
  - **`ddi.reference.version`** (avertissement) signale une référence dont
    l'élément est présent, mais pas dans la version nommée, et liste celles
    qui le sont ;
  - **`ddi.reference.provenance-external`** (info) signale une référence
    `BasedOn` ou d'attribut utilisateur vers un élément hors du fichier ;
  - `ddi.reference.integrity` garde le reste, avec la même gravité qu'avant.
- **Une nouvelle gravité, `info`.** Les constats `info` ne font jamais échouer
  `ddi lint`, sauf si vous passez `--fail-severity info`, désormais accepté.
  `ddi lint` traitait comme une erreur toute gravité autre que `warning`. Un
  constat dont la gravité n'est ni `error`, ni `warning`, ni `info` lève
  maintenant `ValueError`.
- **Sans `rules=`, `run_lint()` exécute le profil par défaut** plutôt que
  toutes les règles enregistrées : les règles destinées à un profil nommé
  (comme le nouveau `colectica-questionnaire`) restent hors de `ddi lint`.
  Une règle ajoutée avec `register_rule()` rejoint toujours le profil par
  défaut, sauf si vous passez `default=False`.
- **Une incrémentation mineure ou de sous-version refuse une version
  entière.** `increment_minor_version()` faisait passer `"6"` à `"6.1"`, une
  version que les outils qui numérotent les versions par des entiers, dont
  Colectica, pourraient ne pas lire. Elle lève maintenant `DDIModelError` ;
  `increment_major_version()` donne `"7"`, et `allow_dotted=True` garde
  l'ancien comportement. Les nouveaux éléments commencent à `"1"` :
  incrémenter la version mineure de l'un d'eux demande donc
  `allow_dotted=True`, ou d'abord une version à trois parties.
  `increment_all_versions()` vérifie tous les éléments avant d'en modifier un.
- **Les paramètres et liaisons des constructions de contrôle sont typés.**
  Sur `IfThenElse`, `Loop` et `StatementItem`, `r:InParameter`,
  `r:OutParameter` et `r:Binding` étaient gardés dans `other_elements`, tout
  comme `r:InParameter` sur `Sequence` ; ils sont maintenant dans
  `in_parameters`, `out_parameters` et `bindings`. `Sequence.bindings` contient
  des objets `Binding` plutôt que des éléments, et
  `OutParameter.representation` contient toute représentation (elle ne prenait
  qu'une représentation de codes ou numérique ; les autres étaient dans
  `other_elements`). Les listes sont typées `list[InParameter | Element]` et
  ainsi de suite, `out_parameters` de `Sequence` compris (il était
  `list[OutParameter]`), et acceptent encore des éléments bruts : du code
  vérifié par mypy restreint un élément avec `isinstance()` avant de s'en
  servir comme paramètre.
- **Les paramètres et liaisons des constructions générées sont typés eux
  aussi.** `ComputationItem` et `QuestionConstruct` lisent `r:InParameter`,
  `r:OutParameter` et `r:Binding` comme `InParameter`, `OutParameter` et
  `Binding` plutôt que comme éléments, tout comme les `in_parameters` d'une
  `Instruction` et les modèles d'éléments génériques qui en ont (`Split`,
  `SplitJoin`, `RepeatUntil`, `RepeatWhile`, `MeasurementItem`,
  `MeasurementConstruct`, `DevelopmentStep`, `SampleStep`, `SamplingStage`).
  Le code qui lisait ces valeurs comme éléments appelle leur `to_xml()` ; une
  valeur lue et réécrite sans changement est toujours écrite telle que lue, et
  les listes acceptent encore des éléments bruts. Les annotations des modèles
  génériques indiquent toujours `list[Element]`.
- **Une langue ajoutée à un nom ou à un libellé lu dans un fichier s'y
  joint.** Une chaîne construite dans le code ouvrait un conteneur à elle à
  côté de ceux lus : ajouter `fr` à un nom lu en `en` écrivait deux éléments
  `d:ConstructName`. Elle rejoint maintenant le dernier conteneur lu quand
  celui-ci n'a pas de chaîne dans sa langue, en gardant ses attributs ; une
  deuxième chaîne dans la même langue ouvre toujours un nouveau conteneur.
- **`IndividualIdentificationFields.individual_names` contient des
  éléments.** Un `a:IndividualName` est fait de parties (`a:FirstGiven`,
  `a:LastFamily`...), pas de `r:String`, mais le générateur de code le typait
  comme chaînes internationales et perdait les parties. Le générateur vérifie
  maintenant si le type d'un nom dérive de `r:InternationalStringType`.
- **Incrémenter une version met à jour `versionDate`.** Sur un élément qui a
  une `versionDate`, chaque incrémentation la met à l'heure actuelle, au
  format de Colectica ; passez `touch=False` pour garder l'ancienne date. Les
  éléments qui n'en ont pas ne changent pas.
- **Les conditions `Neutral` emploient tous les codes d'opérateurs de
  Colectica.** `Operator(0)` est `NONE`, et non `UNKNOWN_0`, et un code lu
  auparavant comme inconnu (`2`, `4` à `6`, `8` à `10`, `13`, `15` à `17`)
  est maintenant un membre nommé. Un énoncé `ContainsAny` ou `ContainsAll`
  qui a une valeur mais aucun code choisi se relit comme non vérifiable, alors
  qu'il se lisait comme `=`. `compile_condition()` écrit `!=`, `<`, `<=`, `>=`
  et `answered()` en `Neutral` là où il écrivait du Blaise.

- **Un schéma absent ou illisible échoue bruyamment.** Si le XSD livré était
  absent ou illisible, la validation se rabattait sur un substitut qui ne
  vérifiait que l'élément racine et les champs d'identification : une
  installation abîmée laissait passer des fichiers invalides. `get_schema()`
  lève désormais `FileNotFoundError` pour un schéma absent, et laisse passer
  sinon l'erreur de xmlschema.
- **Une erreur dans un rappel `on_register` atteint l'appelant.** Le registre
  l'ignorait. La classe est toujours enregistrée avant l'appel des rappels.
- **Le générateur d'exemples écrit dans le dossier courant.** `python -m
  ddi_l.examples.build_and_validate` écrivait par défaut dans le paquet
  installé, et ajoutait le dossier du paquet lui-même à `sys.path`, où
  `ddi_l/io.py` pouvait masquer le module standard `io`. `make example` passe
  les chemins du paquet : il rafraîchit toujours les fichiers livrés.
- **Une `FragmentInstance` est écrite par défaut dans la mise en forme de
  Colectica.** `write_ddi()`, `DDIFragment.to_xml()`, `ddi roundtrip`,
  `ddi from-json`, `POST /v1/roundtrip` et `POST /v1/convert/xml` écrivaient
  la mise en forme de cette bibliothèque : un export Colectica réécrit par eux
  changeait (déclaration, préfixes, marque d'ordre des octets) sans que rien
  ne soit perdu. Seul `save()` écrivait celle de Colectica. Désormais la
  racine décide : une `FragmentInstance` reçoit la mise en forme de Colectica
  et une `DDIInstance` celle de cette bibliothèque. `layout="default"`
  (`--layout default`, `?layout=default`) donne l'ancienne sortie, comme
  `pretty_print=False`, `xml_declaration=False` ou un encodage autre qu'UTF-8,
  que seule cette mise en forme connaît.

### Exports Colectica

- **Lire, modifier et écrire les exports `FragmentInstance` de Colectica.**
  `ddi.open_fragment()` en ouvre un ; `DDIFragment.items()`, `get()`,
  `top_level_item()`, `put()` et `remove()` en manipulent les éléments comme
  modèles typés ; `DDIFragment.save()` écrit exactement la mise en forme de
  Colectica Designer (UTF-8 avec marque d'ordre des octets, un élément par
  `<Fragment>`, chaque élément déclarant son module comme espace de noms par
  défaut, attributs dans l'ordre du schéma) : un export ouvert puis enregistré
  revient octet pour octet. `DDIFragment.from_items()` construit un nouvel
  export avec ce que Colectica écrit sur chaque élément. Toutes les autres
  façons d'écrire une `FragmentInstance` utilisent par défaut la même mise en
  forme (voir *Changements de comportement*), comme le module
  `ddi_l.colectica`. Voir *Travailler avec les exports Colectica*.
- **Un modèle typé pour chaque type d'élément de fragment.** Les 161 types
  d'éléments qu'un fragment DDI 3.3 peut contenir s'analysent maintenant avec
  `MaintainableBase.from_xml` ; les 91 sans classe écrite à la main en
  reçoivent une de `ddi_l.models.items`. Un test construit à partir des XSD un
  échantillon valide de chacun et vérifie qu'il fait l'aller-retour à
  l'identique.
- **`version_date`** lit et modifie `versionDate` sur tout élément.
- **Les exports sans marque d'ordre des octets font l'aller-retour octet pour
  octet.** La mise en forme Colectica écrivait toujours une marque. Désormais,
  `DDIFragment.source_bom` retient si le fichier en avait une, et `save()`,
  `to_colectica_bytes()`, `write_ddi(..., layout="colectica")` et
  `ddi roundtrip --layout colectica` écrivent la même chose ; passez `bom=`
  pour choisir.
- **Le XHTML en ligne garde ses espaces.** Dans `<b>Kind</b> <i>of</i> pet`,
  l'espace entre les éléments est du texte. Il était lu comme de
  l'indentation : lxml lisait « Kindof pet », et le moteur stdlib
  réécrivait un tel fichier autrement. Les deux moteurs la gardent
  maintenant et la réécrivent telle que lue, dans la mise en forme par
  défaut comme dans celle de Colectica ; les espaces entre des blocs XHTML
  sont de la mise en forme. Un tel fichier est analysé deux fois avec
  lxml : le lire prend jusqu'à deux fois plus de temps. `iterparse_ddi()` lit
  les éléments comme `read_ddi()`. Voir *Mise en forme* dans la page Colectica.
  Un `<br>` sépare les mots, et le texte sous `xml:space="preserve"` est
  réécrit tel que lu.
- **`ddi lint --profile colectica-questionnaire`** pour les exports Colectica.
  Sa règle `colectica.maintainable.labels` accepte le nom d'un élément
  (`ConstructName`, `QuestionItemName`, `r:Name`) aussi bien qu'un `r:Label`,
  pourvu qu'il contienne du texte.
- **Lire, modifier et expliquer les conditions Colectica.**
  `ddi_l.colectica_logic` lit la logique que Colectica enregistre dans un
  `r:Command` : le JSON `Neutral` de son éditeur de conditions (`Condition`,
  avec groupes et énoncés), les champs d'une `Blaise5DataLookup`
  (`DataLookup`) et le code natif, gardé tel quel (`NativeCondition`). Il lit
  la condition d'un `IfThenElse` et de chacune de ses branches `ElseIf`, d'un
  `ComputationItem`, et d'un `Loop`, `RepeatUntil` ou `RepeatWhile`
  (`which=` atteint les `InitialValue` et `StepValue` d'un `Loop`). Une
  condition inchangée est réécrite octet pour octet, et une condition modifiée
  comme Colectica écrit le JSON. Les codes d'opérateurs (les 18) et de
  jonction sont ceux de Colectica ; un code non énuméré est gardé tel que lu.
  `render_synopsis()` décrit une condition à partir de sa logique, en nommant
  les sujets d'après leurs questions et les codes par leur valeur, alors que le
  synopsis enregistré par Colectica peut être périmé et numérote les codes par
  position. `ddi explain-condition FICHIER ID` affiche les deux, la description
  de la condition et ses entrées utilisées et inutilisées.
- **25 règles lint pour les questionnaires Colectica**, dans le profil
  `colectica-questionnaire` : identifiants partagés, liaisons orphelines,
  conditions malformées, vides, impossibles ou en code natif invalide (de
  chaque branche `ElseIf` et de chaque boucle aussi ; un `ComputationItem`
  qui a des sorties contient un programme, qui peut tenir sur plusieurs
  lignes et les affecter), entrées inutilisées, synopsis périmés, filtres qui n'englobent qu'une partie
  d'une page, domaines de codes sans liste de codes, libellés de domaine et
  formulations qui ne correspondent pas à l'élément, traductions manquantes,
  gabarits non remplacés, texte d'interface collé, insertions malformées ou
  non déclarées, champs de recherche en double ou suspects, sorties d'une
  recherche absentes de sa liste de champs, alias à
  l'échappement accumulé ou malformés, notes de conception affichées comme
  énoncés, valeurs lues avant que le déroulement ne les demande ou ne les
  calcule (sur chaque chemin vers une page réutilisée), et filtres sur une
  réponse d'une question qui en a plusieurs, que la vue d'acheminement de
  Designer signale comme brisés. Les règles heuristiques signalent au plus un avertissement ; les
  règles qui dépendent des conventions d'un organisme sont inactives tant
  qu'elles ne sont pas configurées avec les nouvelles options de
  `LintConfiguration` (`required_languages`, `known_names`,
  `ui_chrome_tokens`…).
- **`colectica.flow.unreachable` : les constructions qu'aucun répondant
  n'atteint.** Avec l'extra `logic`, le solveur établit la condition d'accès
  de chaque construction, la disjonction, sur les chemins qui y mènent, de la
  conjonction de leurs filtres, en encodant une seule fois les parties du
  flux que de nombreux chemins partagent, et signale une construction
  qu'aucune réponse ne satisfait (`PetAge > 10 and PetAge < 1`, ou un filtre
  dans une branche qu'il contredit). Seule la première construction d'un
  chemin est signalée. Une condition qu'il ne sait pas lire peut être vraie
  ou fausse. Sans l'extra, un flux qui a un filtre reçoit un constat `info`
  indiquant qu'il n'a pas été vérifié.
- **`colectica.flow.read-before-computed` donne un répondant.** Avec l'extra
  `logic`, un constat ajoute un répondant qui atteint l'élément avant la
  question ou le calcul (« For example, when PetCount is 0. »). S'il n'y en a
  aucun, parce que chaque chemin qui y mène d'abord est exclu, le constat est
  `info` : seule la vue de routage de Designer est touchée. Chaque répondant
  donné est vérifié en parcourant le flux avec `evaluate`.
- **`ddi lint --format table`**, `--required-language`, `--known-names FICHIER`
  et `--lint-config FICHIER`. `configure_lint()` accepte tout champ de
  `LintConfiguration` par son nom.
- **Une référence des règles lint générée.** La page *Référence des règles
  lint* énumère chaque règle enregistrée avec sa gravité, ses profils et un
  exemple de constat ; `register_rule()` accepte `severity=` et `example=`,
  et `iter_rule_metadata()` les renvoie.
- **Modifier un questionnaire sans laisser ses références en arrière.**
  `DDIFragment.revise()` donne une nouvelle version à des éléments et, avec
  `cascade`, à chaque élément qui les fixe, jusqu'à l'instrument, sans toucher
  aux références tardives ; `dry_run=True` renvoie seulement le plan. Il
  gère les versions comme Colectica : ce qu'un élément déclare (ses
  paramètres, ses codes) prend sa nouvelle version, une référence qui fixe
  l'un d'eux est mise à jour aussi, et les éléments d'un même appel partagent
  une même `versionDate` (`version_date=` la fixe). `rationale=` inscrit la
  raison comme `r:VersionRationale` de chaque élément révisé, comme Colectica
  inscrit le message d'un enregistrement ; la justification que portait un
  élément, qui expliquait sa version précédente, est retirée. Les nouveaux
  éléments notent la responsabilité configurée.
  `move_construct()`, `insert_construct()` et `wrap_in_condition()` modifient
  des séquences et renvoient les éléments à réviser. `duplicate()` copie un élément en donnant
  un nouvel ID à tout ce qu'il déclare, et `repair_shared_identifiables()`
  (un essai à blanc par défaut) donne un ID propre aux copies d'un paramètre
  partagé, en signalant les références qu'il ne peut pas attribuer.
- **Des paramètres et des liaisons typés.** `InParameter` et `Binding`
  rejoignent `OutParameter` dans `ddi_l.models`. `IfThenElse`, `Loop`,
  `StatementItem` et `Sequence` gardent les leurs dans `in_parameters`,
  `out_parameters` et `bindings` : un nouveau filtre peut donc déclarer les
  entrées que teste sa condition. `Binding.between(source, target,
  late_bound=False)` relie deux paramètres, et `to_reference()` désigne l'un
  d'eux sans `r:URN`, comme l'écrit Colectica. Un paramètre lit son
  `r:ParameterName`, sa `r:Description`, sa `r:DefaultValue`, `isArray` et
  toute représentation.
- **Enregistrer l'auteur d'une version.** Les méthodes `increment_*` acceptent
  `responsibility=`, et `ddi.configure(version_responsibility=...)` en fixe la
  valeur par défaut. `ddi.configured()` limite un réglage à un bloc `with`, et
  `ddi.reset_configuration()` rétablit les valeurs par défaut.

### Charger du DDI depuis des tableurs

- **Charger en lot les métadonnées d'une étude depuis des fichiers CSV, un zip
  de ces fichiers, ou un classeur Excel.** Un tableau par type d'élément, des lignes liées par `id`,
  couvrant ce que la plupart des organisations documentent :
  - l'étude, ses groupes, organisations et personnes (`studies`, `groups`,
    `organizations`, `individuals`) ;
  - concepts, univers, types d'unités et la cascade des variables
    (`conceptual_variables`, `represented_variables`, `variables`) ;
  - listes de codes, y compris les classifications hiérarchiques
    (`codes.parent`) ;
  - questions avec instructions, grilles, blocs et groupes de questions,
    formulées par langue et par public (`question_texts`) ;
  - questionnaires et leur cheminement (`instruments`, `flow`) : séquences,
    énoncés, conditions et boucles ;
  - groupes de variables, fichiers de données (`datasets`) et n-cubes ;
  - méthodologie, traitements, énoncés de qualité et tables de
    correspondance.

  Le texte va dans une colonne par langue (`label@en`, `label@fr`) et les
  colonnes `custom:<nom>` sont enregistrées comme `r:UserAttributePair`.
  `ddi_l.tables.load_tables()` renvoie des modèles typés ; `to_fragment()`
  écrit une `FragmentInstance` Colectica qui contient tous les éléments,
  valide selon le schéma DDI 3.3, et `to_study()` une étude DDI pour les tableaux qu'un
  document d'étude peut contenir. Les éléments qu'impliquent les lignes sont
  écrits aussi : une collecte de données par étude, des séquences pour le
  cheminement, une relation de données par fichier. Les identifiants sont
  dérivés de l'agence et de vos id : recharger donne les mêmes éléments. Tous
  les problèmes sont signalés d'un coup, avec leur fichier, leur ligne et leur
  colonne. Aussi `ddi tables template` et `ddi tables import`, et
  `Document.attach()` pour placer dans une étude un élément construit
  ailleurs. Les classeurs Excel sont lus et écrits avec la bibliothèque
  standard : aucune nouvelle dépendance. Voir *Charger du DDI depuis des
  tableurs* et *Modèles de tableurs*, qui offre des modèles vides et
  d'exemple à télécharger.

### Conformité à une spécification

- **Vérifier un questionnaire par rapport à une spécification.** Une
  spécification liste, en YAML ou en JSON, les modules d'une enquête, les
  questions et les énoncés de chacun, leurs domaines de réponse et listes de
  codes, les filtres des modules et des questions, les contrôles de saisie,
  et les variables qu'une recherche de données fournit ou que l'instrument
  calcule. `ddi conform INSTRUMENT --spec SPEC` (et `ddi_l.spec.conform()`)
  y compare un instrument et signale, avec un identifiant de règle et une
  sévérité, les modules et éléments manquants, en trop, mal placés ou
  ambigus, et les codes et libellés, langues, domaines, filtres et contrôles
  qui diffèrent. La sortie est en JSON ou en tableau ; `--fail-severity`
  fixe ce qui fait échouer l'exécution, et le code de sortie 2 signale
  qu'elle n'a pas pu s'exécuter. Les identifiants sont cherchés là où le bloc
  `match` de la spécification l'indique, et un identifiant trouvé sur
  plusieurs constructions est signalé, jamais deviné. Un élément atteint par
  plusieurs chemins est comparé là où la spécification le place, un filtre
  est lu à partir des liaisons de la dernière version de chaque élément, et
  les domaines référencés et mixtes sont comparés. Avec `gate_scope: page`,
  chaque énoncé du module doit aussi se trouver sous le filtre de sa page.
  Voir *Vérifier un questionnaire par rapport à une spécification*.
- **`ddi spec validate|schema|example`** vérifie une spécification par
  rapport à son schéma JSON et à elle-même (chaque problème avec son
  chemin, dans l'ordre du document), écrit le schéma, ou écrit l'exemple (une
  enquête fictive sur les animaux de compagnie). Le YAML est lu comme du
  YAML 1.2 : les clés répétées et les clés de fusion sont des erreurs.
- **Un langage d'expressions pour les filtres et les contrôles**
  (`ddi_l.spec.expression`) : comparaisons, `and`, `or`, `not`,
  arithmétique, dates et les prédicats `answered()`, `missing()`, `empty()`,
  `refused()` et `today()`. `normalise()` compare deux filtres sans
  calculer : `x > 3` et `x >= 4` restent différents. `equivalent()` aussi,
  sans l'extra `logic` (plus bas). Un test de réponse à côté d'une
  comparaison de la même question
  disparaît (`answered(x) and x > 3` est `x > 3`), si bien qu'un tel filtre
  se compile en `Neutral`.
- **Compiler un filtre pour Colectica** (`compile_condition()`) : une
  condition `Neutral` quand les codes d'opérateurs de Colectica peuvent
  l'exprimer, sinon du code Blaise, avec `fallback_reason` qui dit pourquoi.
  `!=`, `<`, `<=` et `>=` ont leur propre code, `answered(x)` est `NotEmpty`
  et `NotRefused`, et `x != 2` sur une question codée est `ContainsNone` ; un
  `not` devant une comparaison, les dates, l'arithmétique, deux questions
  comparées et `and` et `or` mêlés dans un groupe restent en Blaise. La
  relecture d'une condition a une branche pour chaque code, et un test de
  « ne sait pas » (`DontKnow`) est signalé comme non vérifiable. Les mots Blaise pour vide, refus, aujourd'hui et les dates n'ont
  pas de valeur par défaut : un `BlaiseDialect` ou le bloc `blaise` de la
  spécification les fixe, et un modèle de date doit se relire sans
  ambiguïté. `parse_blaise()` et `condition_to_expression()` relisent l'une
  et l'autre forme ; `comparable()` fait d'un nombre simple entre guillemets
  ce nombre, puisque `Neutral` enregistre `"2"` et `2` de la même façon. Les
  nombres gardent tous leurs chiffres, si longs soient-ils. Un choix parmi
  les codes d'une question codée est un seul énoncé `ContainsAny`, où qu'il
  se trouve, si bien que `a and (x = 2 or x = 3) or b` se compile en
  `Neutral`. Chaque condition compilée est relue et comparée au filtre, par
  forme normale puis avec l'extra `logic` s'il est installé :
  `CompiledCondition.verified` en garde le résultat, et
  `compile_condition(validate=True)` lève une exception quand ils
  diffèrent, en nommant un répondant sur lequel ils divergent.
- **Les contrôles de saisie sont signalés comme non vérifiables par
  défaut**, puisque l'endroit où un instrument les enregistre n'est pas connu
  en général ; `--edits strict` les compare dès que le `match.edits` de la
  spécification dit comment ils sont marqués.
- **Décider si deux filtres valent pour les mêmes répondants** (`decide()`,
  avec le nouvel extra `logic`, `pip install 'ddi-l[logic]'`, qui ajoute le
  solveur Z3). Quand ce n'est pas le cas, le verdict donne un répondant sur
  lequel ils divergent : `x > 3` et `x >= 4` diffèrent quand `x` vaut 3,25,
  et concordent avec `types={"x": "integer"}`. Un répondant laisse chaque
  question vide, la refuse ou y répond, et une réponse peut n'avoir aucune
  valeur à comparer (un « ne sait pas ») ; une comparaison n'est vraie
  que si les questions qu'elle lit ont une valeur. Ce qui ne peut pas être
  modélisé, comme du texte comparé par ordre, est `unknown`, avec la raison.
  `evaluate()` dit si une expression vaut pour un répondant, et chaque
  verdict `different` est vérifié avec elle. Une limite de travail, et non
  une horloge, borne le solveur : un verdict est le même à chaque
  exécution, et `import ddi_l.spec` ne le charge pas.
- **Un nouvel extra `spec`**, `pip install 'ddi-l[spec]'`, ajoute PyYAML et
  jsonschema pour lire les spécifications. Le langage d'expressions et ses
  compilateurs n'ont besoin que de la bibliothèque standard, et
  `import ddi_l` n'en charge rien.

### API HTTP

- **Des options de lint par requête.** `POST /v1/lint` accepte `?rule=`,
  `?skip_rule=` et `?lint_config=` (l'objet JSON que lit `--lint-config`), et
  `POST /v1/validate` accepte `?lint_config=`. Elles ne valent que pour cette
  requête : des requêtes simultanées ne partagent plus un réglage commun au
  processus.
- **Les exports Colectica font l'aller-retour octet pour octet.** `POST
  /v1/roundtrip` écrit une `FragmentInstance` comme Colectica Designer : un
  export inchangé revient identique, et une comparaison ne montre que ce que
  l'analyse a perdu. Avant, chaque fichier Colectica semblait modifié ;
  `?layout=default` donne la mise en forme de cette bibliothèque.
- **Charger des tableaux de métadonnées par HTTP.** `POST /v1/tables/import`
  reçoit un classeur `.xlsx` ou un `.zip` de fichiers CSV et répond par une
  `FragmentInstance` Colectica (ou, avec `?study=`, une étude). Des tableaux
  qui ont des problèmes donnent un `422` dont `extra` énumère chaque problème
  avec son fichier, sa ligne et sa colonne. `GET /v1/tables/template`
  télécharge les tableaux vides ou d'exemple, et `GET /v1/tables` décrit
  chaque tableau et chaque colonne en JSON. Les envois sont lus en mémoire,
  dans des limites de taille, de nombre de fichiers, de lignes et de colonnes.
- **`load_tables()` lit aussi un zip de fichiers CSV, ou les octets d'un
  classeur ou d'un zip.** Tout comme `ddi tables import`.

### Noyau XML natif

- **`pip install ddi-l` apporte un noyau XML compilé**, le paquet
  `ddi-l-native` (Rust, construit avec PyO3), que ddi-l utilise avant lxml.
  Il a des wheels pour Linux (x86_64, aarch64), macOS et Windows (x64), avec
  CPython 3.11 et plus ; ailleurs, pip installe un remplaçant en Python pur de
  même nom et de même version, dont ddi-l se passe : installer ddi-l ne
  compile jamais rien. Son analyseur construit l'arbre que construit celui
  de la bibliothèque standard, et ses éléments se comportent comme les siens ;
  l'arbre garde les octets lus et met en cache l'empreinte de chaque élément,
  effacée seulement sur le chemin d'une modification jusqu'à la racine.
  `DDI_L_XML_BACKEND=native|lxml|stdlib` choisit un moteur ; voir
  [Installation](installation.fr.md#moteurs-xml).
- **Les mêmes résultats avec chaque moteur.** Toute la suite de tests
  s'exécute avec le moteur natif. L'analyseur est comparé à celui de la
  bibliothèque standard sur chaque fixture, sur des entrées construites et sur
  du XML aléatoire ou abîmé : il lit les mêmes documents en les mêmes arbres
  et refuse les mêmes, et il refuse en plus toute déclaration de type de
  document. Ses empreintes et son index de la source sont comparés à ceux en
  Python pur après des modifications aléatoires, et l'écrivain écrit les mêmes
  octets avec l'un ou l'autre.
- **Plus rapide là où cela compte.** Sur un export de 9 Mo : `read_ddi`
  0,13 s (lxml 0,33 s) ; la réécriture sans changement 0,01 s (0,28 s), ou
  après une modification 0,04 s (0,31 s) ; le profil
  `colectica-questionnaire` 0,67 s (1,74 s). L'analyse atteint 185 Mo/s (lxml
  124 Mo/s, bibliothèque standard 41 Mo/s), loin de la bande passante
  mémoire : créer les nœuds de l'arbre en coûte l'essentiel. Écrire un
  document avec une mise en page neuve est plus lent qu'avec lxml (0,80 s
  contre 0,26 s) ; voir [Performance](performance.fr.md).
- **Validation par schéma en une passe, avec les lignes, sur le moteur
  natif.** Un nouveau moteur de validation `native`, celui par défaut avec le
  moteur natif, vérifie un document en une passe contre une forme compilée du
  schéma (`ddi_l/schemas/ir/`, produite par `codegen/schema_ir.py` à partir
  des XSD fournis). Un document valide ne charge jamais xmlschema. Chaque
  élément qui peut être fautif est vérifié seul par xmlschema : les messages
  et les chemins sont ceux d'xmlschema, et les problèmes portent la ligne où
  chaque élément commence, comme avec le moteur lxml. Sur un export de 9 Mo :
  0,09 s s'il est valide ; 0,13 s avec une erreur (2,6 s au premier appel),
  là où libxml2 puis xmlschema prennent 6,5 s. Comparé à xmlschema sur
  chaque fixture et sur 300 documents abîmés au hasard à chaque exécution :
  les mêmes erreurs, dans le même ordre.
- **Relancer le lint coûte ce qui a changé, sur le moteur natif.** Une passe
  de lint garde ce qu'elle a lu de chaque élément sous l'empreinte de son
  contenu, et une passe suivante sur le même document ne relit que les
  éléments dont l'empreinte a changé. Sur un export de 9 Mo, le profil
  `colectica-questionnaire` prend 0,13 s après une modification, contre
  0,8 s pour une première passe, avec les mêmes constats. Les règles
  qui suivent tout le flux (`colectica.flow.read-before-computed`,
  `colectica.ifthenelse.partial-gate`) le parcourent encore à chaque fois.
  Une première passe coûte environ 0,04 s de plus : elle calcule les
  empreintes, qu'une écriture suivante réutilise. Comparé, après des
  modifications au hasard, à une passe qui relit tout.

### Performances

- **`revise` ne parcourt plus tous les éléments pour chaque élément révisé.**
  Il trouve qui renvoie à un élément révisé dans un index construit une fois
  par appel (gardé élément par élément sur le moteur natif), et une
  simulation fait ses changements puis les reprend au lieu de copier le
  fragment ; `repair_shared_identifiables` fait de même. Sur un export de
  9 Mo, réviser une question et ses six ancêtres prend 0,02 s
  sur le moteur natif (0,20 s avant ; 0,38 s en simulation) et
  0,14 s avec lxml (0,41 s ; 0,49 s en simulation). Comparé,
  après des modifications au hasard, à la cascade d'avant : le même plan et
  le même document.
- **Une passe de lint construit chaque index une fois.** Les règles d'une
  passe partagent ce qu'elles tirent du document : ses éléments et leur
  dernière version, la résolution des références, les liaisons et les
  conditions analysées ; `conform` fait de même. Chaque règle qui en avait
  besoin les reconstruisait, et les éléments les plus internes d'une
  `DDIInstance` étaient trouvés en parcourant le sous-arbre de chaque élément.
  Le profil `colectica-questionnaire` sur un export de 9 Mo (4 478 éléments)
  est passé de 6,1 s à 2,0 s, avec les mêmes constats.
- **`colectica.flow.read-before-computed` ne parcourt plus chaque chemin.**
  Une page atteinte par plusieurs chemins était reparcourue pour chacun :
  un flux de filtres enchaînés prenait un temps qui doublait à chaque
  filtre. Une construction atteinte de nouveau rejoue maintenant ce qu'elle
  a trouvé la première fois, pour les mêmes liaisons au-dessus d'elle ; les
  constats sont les mêmes. Un flux de 20 filtres enchaînés (un million de
  chemins) prend quelques millisecondes. Un flux qui boucle sur lui-même est
  encore parcouru chemin par chemin.
- **`conform` ne parcourt plus chaque chemin vers une construction.** Une
  construction est un nœud pour chaque suite de séquences au-dessus d'elle ;
  ce nœud compte les chemins qui y mènent et garde les filtres du premier.
  On sait si les chemins s'accordent sur un filtre sans les parcourir un à
  un. Les rapports sont les mêmes. Une question sous 16 filtres enchaînés
  (65 536 chemins) prenait 9,1 s et prend maintenant 13 ms ; sous 20
  filtres, 17 ms. Un instrument qui boucle sur lui-même est encore parcouru
  chemin par chemin.

### Corrections

- **`DDIReferenceWarning` peut être recréé à partir de ses arguments**, comme
  le font `pickle`, `copy` et pytest-xdist : son argument est la liste des
  références, et son texte ne change pas.
- **Un attribut posé dans le code sur un nouveau `<Fragment>` est écrit.** La
  mise en forme de Colectica écrivait chaque balise ouvrante `<Fragment>` à
  partir d'un modèle : un attribut sur un fragment copié ou ajouté était
  perdu, celui d'un fragment lu dans un fichier était gardé.
- **Une simulation de `revise` à qui l'on passe un élément choisit l'élément
  que choisit la vraie révision.** Elle le cherchait par son ID seul : avec
  deux éléments de cet ID sous des agences différentes, elle pouvait
  planifier pour l'autre.
- **Une déclaration de type de document est refusée sur les deux
  backends.** Le backend stdlib acceptait `<!DOCTYPE root><root/>`, que lxml
  refusait ; les deux le refusent maintenant avec le même message.
  `iterparse_ddi` la refuse aussi, et l'appelant ne peut plus assouplir son
  analyseur : `resolve_entities=True`, `load_dtd=True`, `no_network=False`,
  un `forbid_*=False` ou un `parser` lèvent `ValueError`.
- **Les questions ajoutées à un fichier ouvert sont enregistrées.** Une
  collecte de données ou un schéma de questions lu dans un fichier n'écrivait
  que les questions lues : une question ajoutée après `open_ddi()` disparaissait
  à l'enregistrement sans avertissement, et une question supprimée revenait.
- `validate_document(doc)` sur un `Document` ne détache plus les modèles que
  l'appelant détient ; les modifications faites ensuite étaient perdues à
  l'enregistrement.
- `--debug` fonctionne avec toutes les commandes ; `tables`, `spec`,
  `conform`, `explain-condition`, `versions` et `serve` le refusaient.
- `ddi.citation.title.languages` est enregistrée, listée et documentée comme
  le `warning` qu'elle signale, et non comme une `error`.
- `DDIDocument.validate(raise_error=True)` est documentée comme levant
  `DDIValidationError`, ce qu'elle fait.
- **`colectica.statement.logic-note` ignore les notes.** Un énoncé que
  Colectica type comme note (`extension:TypeOfStatement` = `Note`) n'est pas
  affiché : une condition de cheminement qui y est écrite est à sa place, et
  n'est plus signalée comme montrée aux répondants.
- **Une `str` est lue comme le texte qu'elle est.** `read_ddi()` lit le XML
  donné en chaîne quel que soit l'encodage que nomme sa déclaration ; il
  était décodé de nouveau selon cet encodage, ou refusé.
- **Les noms construits dans le code sont valides.** Un nom défini dans le
  code (`construct_names`, `names` et tout autre champ `…Name` d'un modèle
  généré) était écrit avec `r:Content`, que le schéma interdit dans un nom :
  `validate()` rejetait donc des éléments comme `ComputationItem`,
  `QuestionConstruct`, `Category`, `Universe` et tous les schemes et
  groupes. Les noms sont écrits avec `r:String`. Un nom lu dans un fichier
  garde sa balise, sauf s'il s'agissait du `r:Content` invalide.
- **`ConceptualComponent` garde ses noms de module.** Un
  `c:ConceptualComponentModuleName` défini dans le code n'était jamais écrit,
  et celui lu dans un fichier n'était gardé que comme contenu non relié ; les
  deux passent maintenant par `conceptual_component_module_names`.
- **Deux types d'éléments ne peuvent plus partager en silence un même ID
  généré.** Un `DataCollection` donne à chaque élément construit avec un
  identifiant qui n'est pas un UUID l'ID `uuid5(agence:identifiant)` : un
  `DataCollection` et un `CollectionEvent` tous deux nommés `main` sortaient
  donc avec le même `r:ID`, tout comme un `CollectionEvent` nommé `main`
  ajouté à ce `DataCollection` après l'avoir relu. La sérialisation lève
  maintenant `ModelValidationError` en nommant les deux types. Les versions
  d'un même élément partagent toujours leur ID, et les identifiants qu'un
  élément a déjà sont écrits tels quels.
- **Une étude dans un fragment ne signale plus ses références.**
  `DDIFragment.from_items()` et `put()` signalaient chaque référence d'un
  `StudyUnit` comme non résolue, alors que dans un fragment les éléments
  qu'elle désigne sont chacun dans leur propre fragment.
- **Les modèles typés ne perdent plus de contenu.** Lire un élément puis le
  réécrire supprimait `versionDate`, `r:VersionResponsibility` et la filiation
  `r:BasedOnObject` dans les modèles écrits à la main (Variable, CodeList,
  RepresentedVariable, DataRelationship, StudyUnit et d'autres) ; scindait un
  `r:Label` ou un nom bilingue en un élément par langue ; supprimait
  `audienceLanguage` et `d:ConditionalText` du texte des questions, les paires
  d'attributs utilisateur et les attributs dans les références, les
  attributs de `r:URN`/`r:ID`, les attributs de vocabulaire contrôlé et les
  métadonnées des schémas en ligne ; et écrivait certains contenus hors de
  l'ordre du schéma (QuestionItem, Sequence), ce que le schéma refuse.
- **Le texte balisé est conservé.** Un libellé, une description ou un autre
  texte multilingue dont le `r:Content` contient du XHTML
  (`<b>Kind</b> of pet`) était coupé au texte précédant son premier élément
  chaque fois que son élément était écrit depuis son modèle (`put()`,
  `to_xml()`), et ses blocs pouvaient être réordonnés (un `<ul>` déplacé
  avant le `<p>` qu'il suivait). Une telle chaîne contient maintenant tout son
  texte (`"Kind of pet"`, avec une espace entre les blocs) et est réécrite telle que lue tant qu'elle ne change
  pas ; une chaîne modifiée est écrite comme son texte, et les autres langues
  gardent leur balisage. Les paramètres gardent les attributs de leur
  `r:URN` quand ils sont modifiés.
- **`DDIFragment.from_items()` retire chaque URN de référence redondant.** Il
  sautait la référence suivant chaque URN retiré : un élément à plusieurs
  références gardait des `r:URN` que Colectica n'écrit pas.
- **Les références sont écrites telles que lues.** Une référence lue sans
  `r:URN` n'en reçoit plus ; une référence construite dans le code en reçoit
  toujours une.
- **Le `xs:boolean` `"1"` est vrai.** Plusieurs enveloppes le lisaient comme
  faux et écrivaient `"false"`. Les valeurs gardent leur orthographe d'origine
  tant qu'elles ne changent pas.
- **Les identifiants lus dans un fichier sont conservés.** `DataCollection`
  réécrivait les `r:ID` non UUID (le sien et ceux de tout ce qu'elle contient)
  en UUID générés, ce qui brisait les références d'autres éléments ; elle ne
  le fait plus que pour les objets construits dans le code.
- **La validation des fragments ne pardonne plus de vraies erreurs.** Une
  erreur dans le `StudyUnit` d'un fragment (et quelques autres vrais éléments
  DDI) était ignorée, et la validation s'arrêtait là, masquant toute erreur
  suivante. Seuls les types d'extension de la bibliothèque sont exemptés, et
  toutes les erreurs sont vérifiées.
- `ConceptualComponent` écrit toujours les concepts, univers, variables
  conceptuelles et types d'unités dans leurs schémas ; écrits seuls, ils
  étaient invalides.
- `d:Methodology` écrit `d:MethodologyName` dans l'espace de noms DDI 3.3.
- `r:ExternalURLReference`, `r:ExternalURNReference` et quelques autres
  éléments nommés `*Reference` ne sont plus lus comme des références DDI (ce
  qui les vidait).
- Une valeur valide selon le schéma qui ne s'analyse pas comme le type
  numérique déclaré n'empêche plus le chargement d'un élément.
- Construire un fragment est linéaire en sa taille (c'était quadratique :
  53 s pour un export de 4 478 éléments, moins de 3 s maintenant).

### Documentation

- **Une page sur le travail avec d'autres outils.** « Travailler avec d'autres
  outils » montre, avec des exemples qui s'exécutent, comment ddi-l échange
  des métadonnées avec les outils XML et de schéma (`xmllint`), les outils de
  données liées (`rdflib` et SPARQL), JSON, les tableurs, R, tout langage par
  HTTP, les fichiers DDI Codebook (par exemple l'export de Dataverse, converti
  par l'import de tableaux), les outils DDI 3.2 et les générateurs de
  questionnaires libres, et ce qu'il faut vérifier avant d'échanger un fichier.
- **Des objectifs d'apprentissage mesurables dans chaque module.** Chacun des
  17 modules s'ouvre sur trois à six objectifs qui disent ce que l'apprenant
  peut faire (« écrire un script qui… », « lancer `ddi lint` et nommer un
  constat »), étiquette chaque exercice et chaque question du quiz avec
  l'objectif qu'il exerce, donne la sortie attendue de chaque exercice et se
  termine par une liste « Faites le point ». Chaque objectif a désormais un
  exercice et une question de quiz ; les bonnes réponses se répartissent de A
  à D (B était la réponse de 42 questions sur 72). Les modules 12, 14, 15 et
  16 gardent six objectifs au plus et déplacent le reste dans « Pour aller
  plus loin ». La grille du projet de synthèse note les techniques de chaque
  parcours, et les quatre parcours ont une solution type. Dix copies périmées
  de modules renumérotés, dans les deux langues, sont supprimées.
- **Les renvois s'affichent sur la page de l'API.** Les docstrings les
  écrivaient en rôles Sphinx (`:func:`...``), affichés tels quels ; ce sont
  désormais des extraits de code.
- **Un module sur la spécification avancée de questionnaires.** Le module 16
  apprend aux rédacteurs à écrire une spécification de questionnaire, à
  donner aux filtres et aux contrôles de saisie le sens voulu quand une
  réponse manque, à remplacer « aller à » et « sinon » par des filtres, à
  adapter les filtres à l'éditeur de conditions d'un outil sans en changer le
  sens, à garder une seule variable par idée dans les deux langues et à vérifier un instrument avec `ddi conform`. Les
  projets de synthèse deviennent le module 17 ; leur ancienne adresse
  redirige vers eux.
- **Un seul jeu de couleurs, lisible dans chaque mode.** Le site emploie un
  seul bleu de marque pour l'en-tête, les liens et les boutons, l'orange ne
  marquant que l'anneau de focus du clavier, et chaque couleur de texte
  respecte le niveau AA des WCAG en mode clair, sombre et contraste élevé. Le
  mode sombre utilise désormais les couleurs du site plutôt que celles de
  Material par défaut, et ses boutons sont lisibles : les boutons à contour
  étaient à 2,3:1, et un bouton de téléchargement dans une page à 1,1:1, bleu
  marine sur noir. Le contraste élevé a un en-tête noir, des onglets de
  navigation visibles et du code lisible, et ses notes et astuces sont sombres
  comme la page au lieu d'être des encadrés blancs dont les tableaux étaient
  blanc sur blanc. Le logo suit la couleur de l'en-tête au lieu de
  s'afficher en noir, et le menu des palettes se trouve dans l'en-tête, à côté
  du bouton clair/sombre, au lieu de recouvrir l'icône de recherche sur
  téléphone. Les trois palettes adaptées à la vision des couleurs sont
  retirées : le bleu et l'orange conviennent déjà à ces lecteurs.
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

### Outils et paquets

- **Les tests tournent sur tous les cœurs.** `pytest` tourne avec
  pytest-xdist (`-n auto`, une nouvelle dépendance de développement) ;
  `-n 0` le fait tourner dans un seul processus. Sur quatre cœurs, la suite
  avec lxml prend 58 s au lieu de 3 min 20 s (sans la couverture) ; avec la
  couverture, lxml prend 1 min 43 s, la bibliothèque standard 2 min 49 s et
  le moteur natif 3 min 45 s.
- **La suite de tests tourne sans avertissement.** Un test dont les éléments
  renvoient à des éléments hors de son document le déclare désormais, et tout
  autre `DDIReferenceWarning` le fait échouer ; les deux pages du cursus
  qui avertissent exprès doivent toujours avertir. Cinq tests ne sont plus
  ignorés : deux bogues du générateur (une valeur d'élément fixe, un modèle
  de contenu qui doit apparaître deux fois) laissaient trois types d'éléments
  sans test, et un fichier volontairement tronqué n'est plus donné aux tests
  qui exigent du XML bien formé. Les tests encore ignorés dépendent de
  l'environnement (pas de R, pas de cœur natif, l'autre moteur XML) ou du
  moteur générique, qui ne lit pas les membres d'un groupe de substitution.
- **Python 3.15.** ddi-l est aussi testé sur Python 3.15 : une demande de
  fusion teste 3.11 et 3.15, un envoi sur `main` teste 3.11 à 3.15, avec les
  deux moteurs XML chaque fois. L'intégration continue fixe uv 0.13.7, la
  première série d'uv qui installe 3.15.
- **Une commande fixe la version.** `scripts/set_version.py 0.3.0` (ou
  `patch`, `minor`, `major`) écrit la version dans les 11 fichiers qui
  l'indiquent, avec la date de publication et l'année des citations, puis
  lance `uv lock` ; il n'écrit rien tant que chaque fichier ne correspond
  pas. Un test échoue quand un autre fichier se met à indiquer la version.
- **Un lien vers un titre absent fait échouer la documentation.**
  `mkdocs build --strict` vérifie désormais les ancres
  (`validation: anchors: warn`). Il a trouvé deux liens de l'aide-mémoire
  vers une section du module 15 qui avait changé de place, corrigés.
- **Les exécutions de mutation tirent moins d'exemples, les mêmes à chaque
  fois.** Sous mutmut, un test de propriété tire au plus 30 exemples, sans
  hasard, au lieu de 300 (ou des 100 de Hypothesis), puisqu'il tourne une fois
  par mutant qu'il couvre ; un mutant est attrapé à chaque exécution ou
  jamais. La suite en tire toujours 300.
- **Le noyau natif dans l'intégration continue et les versions.** Une tâche
  de l'intégration continue vérifie le code Rust (`cargo fmt`,
  `cargo clippy`) et exécute toute la suite avec le moteur natif. Une version
  construit les wheels de `ddi-l-native` (une wheel à ABI stable par
  plateforme : Linux x86_64 et aarch64, macOS universal2, Windows x64) et sa
  sdist, plus la wheel du remplaçant en Python pur (`native/fallback/`), et
  les publie avec ddi-l ; PyPI doit aussi connaître ce dépôt comme éditeur de
  confiance du projet `ddi-l-native`. La tâche mensuelle teste l'analyseur au
  hasard contre celui de la bibliothèque standard, 300 000 entrées par test.
  Dans le dépôt, `uv.lock` installe le remplaçant : aucun contributeur n'a
  besoin de Rust ; la sdist de ddi-l le contient, avec les sources du crate.
- **Les fixtures de test ne sont livrées que dans la sdist.** La wheel
  contenait 250 fichiers de test sous `ddi_l/examples/tests/`. Elle garde les
  deux exemples qu'exécutent les recettes en ligne de commande ; le reste est
  dans `tests/fixtures/`, et `scripts/check_distributions.py` échoue s'ils
  reviennent dans la wheel.
- **Une barrière de tests de mutation.** `mutmut` couvre désormais quinze
  modules, et la tâche mensuelle échoue quand survit un mutant que
  `tests/mutation_baseline.txt` ne liste pas, ou quand un mutant listé ne
  survit plus (`scripts/check_mutation.py`, `make mutation`). La dernière
  exécution complète a attrapé 12 290 mutants sur 14 542 (84,5 %). La liste
  contient les 2 252 survivants : 239 avec la raison pour laquelle aucun
  test ne peut les attraper, et 2 013 pas encore examinés. De nouveaux
  tests ont attrapé environ 500 survivants, surtout dans la validation, les
  opérations, le compilateur de conditions, les entrées-sorties et la
  conformité. Dans les quatre modules nouveaux de cette version (la base de
  faits, l'index du questionnaire, l'évaluateur et l'encodage pour le
  solveur), 1 237 mutants sur 1 282 sont attrapés, et chacun des 45
  survivants a sa raison.
- Ruff et l'audit des dépendances tournent une fois dans la CI au lieu de
  sur chacune des huit variantes de test.
- Une pull request teste Python 3.11 et 3.14 avec les deux moteurs ; un push
  sur `main` teste toujours les quatre versions.
- Suppression du code que rien n'utilisait, fusion des cinq copies de la clé
  de tri des versions, et une fonction à la place des classes de stratégie du
  sérialiseur.

### Problèmes connus

- `ddi validate` renvoie 1 dès qu'il signale un problème, même de gravité
  `warning`.
- Une étude déplacée dans un `Group` (`Document.add_group()`) manque à
  `iter_study_units()`, et donc à l'index construit à partir de cette méthode.
- Sans lxml, une sortie écrite avec `pretty_print=False` écrit les éléments
  vides `<tag />`, là où lxml écrit `<tag/>`.
- Une `DDIInstance` DDI 3.2 est réécrite avec des préfixes générés (`ns0:`
  avec lxml, `p0:` sans) et avec `r:` lié à l'espace de noms 3.3. Le XML a le
  même sens, mais ne se lit plus comme la source. Une `FragmentInstance` 3.2
  est écrite dans la mise en forme de Colectica, avec `r:` et `ddi:` liés aux
  espaces de noms 3.2.

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
- Voir [Performance](performance.fr.md) pour les temps mesures.

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
  [utiliser ddi-l depuis R](r-users.fr.md) avec reticulate.
- **Cursus de formation** : un cours progressif de 16 modules avec exercices,
  quiz, guide de l'instructeur, corrigés et aide-mémoire bilingue.
