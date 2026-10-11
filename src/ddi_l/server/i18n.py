"""Localized renderings of the OpenAPI description.

The spec's own prose (summaries, descriptions, example captions) is
translated. Swagger UI's chrome ("Try it out", "Execute") is not; the
renderers have no i18n support.

The catalog is keyed by the English string, so rewording an English
description invalidates its translation and :func:`missing_translations`
reports it.

Never translated: ``info.title``, JSON field names and example values, which
are part of the wire contract.
"""

from __future__ import annotations

import copy
from typing import Any, Final

__all__ = [
    "DEFAULT_LOCALE",
    "LOCALES",
    "TRANSLATABLE_KEYS",
    "missing_translations",
    "translate_schema",
    "unused_translations",
]

#: The locale the handlers are written in; :func:`translate_schema` returns the
#: schema untouched for it.
DEFAULT_LOCALE: Final = "en"

#: OpenAPI fields holding prose. Deliberately narrow: `title` is excluded so a
#: schema component's name is never translated, and neither is any field whose
#: value a client parses.
TRANSLATABLE_KEYS: Final = frozenset({"summary", "description"})

#: Subtrees never descended into. `value` and `example` hold the sample DDI
#: documents, which are payloads rather than prose -- and a DDI document is
#: perfectly entitled to contain a key called `description`.
_OPAQUE_KEYS: Final = frozenset({"value", "example"})

_FR: Final[dict[str, str]] = {
    "Validate, lint and convert DDI Lifecycle XML. Every endpoint is a thin "
    "wrapper over the same functions the `ddi` CLI calls.": (
        "Validez, analysez et convertissez du XML DDI Lifecycle. Chaque point "
        "de terminaison est une fine enveloppe autour des fonctions qu'appelle "
        "aussi la commande `ddi`."
    ),
    "Service index": "Index du service",
    "The available endpoints.": "Les points de terminaison disponibles.",
    "Liveness probe": "Sonde de vivacité",
    "The service is up.": "Le service est en ligne.",
    "Service is up": "Service en ligne",
    "Supported DDI schema versions": "Versions de schéma DDI prises en charge",
    "The bundled DDI Lifecycle releases.": (
        "Les versions DDI Lifecycle fournies avec le paquet."
    ),
    "Bundled schema releases": "Versions de schéma fournies",
    "Validate a DDI document": "Valider un document DDI",
    "DDI Lifecycle release to work against. Omit to use the version the "
    "document declares. See `GET /v1/versions` for what is bundled.": (
        "Version DDI Lifecycle à utiliser. Omettez ce paramètre pour reprendre "
        "la version que le document déclare. Voir `GET /v1/versions` pour la "
        "liste fournie."
    ),
    "Run lint rules alongside schema validation. Pass `false` to skip them.": (
        "Exécuter les règles de lint en plus de la validation de schéma. "
        "Passez `false` pour les ignorer."
    ),
    "A DDI Lifecycle XML document, sent as the raw request body -- not "
    "multipart, not JSON-wrapped. `curl --data-binary @study.xml` is the "
    "shape.": (
        "Un document XML DDI Lifecycle, envoyé tel quel dans le corps de la "
        "requête -- ni multipart, ni encapsulé en JSON. "
        "`curl --data-binary @study.xml` en donne la forme."
    ),
    "A minimal valid DDI Lifecycle 3.3 instance": (
        "Une instance DDI Lifecycle 3.3 valide et minimale"
    ),
    "Passes schema validation and lint with nothing to report. Paste it into "
    "any endpoint that takes XML.": (
        "Passe la validation de schéma et le lint sans rien à signaler. "
        "Collez-la dans n'importe quel point de terminaison qui accepte du XML."
    ),
    "The verdict. Note that an *invalid document* is still a 200 -- read "
    "`valid`, not the status code.": (
        "Le verdict. Notez qu'un *document invalide* renvoie tout de même un "
        "200 -- lisez `valid`, pas le code de statut."
    ),
    "A valid document, with warnings": "Un document valide, avec des avertissements",
    "The common case for freshly authored DDI: the document satisfies the "
    "schema, so `valid` is `true`, while lint reports the items authored "
    "without a label. Pass `label=` to `add_question()` and friends and "
    "these go away. Warnings never flip `valid` to `false`.": (
        "Le cas courant pour du DDI fraîchement rédigé : le document satisfait "
        "le schéma, donc `valid` vaut `true`, tandis que le lint signale les "
        "objets créés sans libellé. Passez `label=` à `add_question()` et à ses "
        "semblables et ces avertissements disparaissent. Les avertissements ne "
        "font jamais basculer `valid` à `false`."
    ),
    "A document that fails the schema": (
        "Un document qui échoue à la validation de schéma"
    ),
    "Note the status code is still 200 -- the service answered the question it "
    "was asked. `valid` is the field that reports the verdict; a non-2xx "
    "status means the request itself was unusable, not that the document "
    "was.": (
        "Notez que le code de statut reste 200 -- le service a répondu à la "
        "question posée. `valid` est le champ qui porte le verdict ; un statut "
        "non-2xx signifie que la requête elle-même était inexploitable, pas "
        "que le document l'était."
    ),
    "The body was empty, not XML, or not a DDI document.": (
        "Le corps était vide, n'était pas du XML, ou n'était pas un document DDI."
    ),
    "Not a DDI document": "Pas un document DDI",
    "Body exceeded the configured limit (32 MiB by default).": (
        "Le corps dépasse la limite configurée (32 Mio par défaut)."
    ),
    "Body over the configured cap": "Corps au-delà de la limite configurée",
    "Processing exceeded the configured request timeout.": (
        "Le traitement a dépassé le délai de requête configuré."
    ),
    "Processing exceeded the timeout": "Traitement au-delà du délai",
    "Lint a DDI document": "Analyser un document DDI",
    "Run a named lint profile instead of the default rule set. A profile "
    "validates as well as lints, changing the response shape.": (
        "Exécuter un profil de lint nommé au lieu du jeu de règles par défaut. "
        "Un profil valide en plus d'analyser, ce qui change la forme de la "
        "réponse."
    ),
    "Rule findings. With `?profile=` the response instead carries "
    "`schema_issues` and `lint_findings`, since a profile validates as well as "
    "lints -- see the second example.": (
        "Constats des règles. Avec `?profile=`, la réponse porte à la place "
        "`schema_issues` et `lint_findings`, puisqu'un profil valide en plus "
        "d'analyser -- voir le second exemple."
    ),
    "Rule findings": "Constats des règles",
    "A named profile (?profile=...)": "Un profil nommé (?profile=...)",
    "A profile validates as well as lints, so the response carries both lists.": (
        "Un profil valide en plus d'analyser : la réponse porte donc les deux listes."
    ),
    "Convert DDI XML to JSON": "Convertir du XML DDI en JSON",
    "A lossless transcription of the XML. Keys are Clark-notation tag names "
    "(`{namespace}Local`); `@`-prefixed keys are attributes and `#text` is "
    "element content. Round-trips through `POST /v1/convert/xml`.": (
        "Une transcription sans perte du XML. Les clés sont des noms de "
        "balises en notation Clark (`{namespace}Local`) ; les clés préfixées "
        "par `@` sont des attributs et `#text` est le contenu de l'élément. "
        "Fait l'aller-retour via `POST /v1/convert/xml`."
    ),
    "The same document as JSON": "Le même document en JSON",
    "Lossless. `POST /v1/convert/xml` turns it back into the XML above.": (
        "Sans perte. `POST /v1/convert/xml` le retransforme en le XML ci-dessus."
    ),
    "Convert DDI XML to JSON-LD (Disco)": "Convertir du XML DDI en JSON-LD (Disco)",
    "A Disco graph: `@context` binds the vocabulary prefixes and `@graph` is a "
    "flat list of nodes keyed by DDI URN, ready to load into a triple store.": (
        "Un graphe Disco : `@context` lie les préfixes du vocabulaire et "
        "`@graph` est une liste plate de nœuds indexés par URN DDI, prête à "
        "charger dans un triplestore."
    ),
    "The same document as a Disco graph": (
        "Le même document sous forme de graphe Disco"
    ),
    "A discovery subset, not a transcription -- and one-way by design.": (
        "Un sous-ensemble de découverte, non une transcription -- et à sens "
        "unique par conception."
    ),
    "Convert JSON back to DDI XML": "Reconvertir du JSON en XML DDI",
    "A JSON document in the form `POST /v1/convert/json` produces: "
    "Clark-notation keys, `@` for attributes, `#text` for content.": (
        "Un document JSON de la forme que produit `POST /v1/convert/json` : "
        "clés en notation Clark, `@` pour les attributs, `#text` pour le "
        "contenu."
    ),
    "The reconstructed document.": "Le document reconstruit.",
    "Re-serialize a DDI document": "Re-sérialiser un document DDI",
    "The document as this library re-serializes it. Diff it against what you "
    "sent -- anything that changed did not survive a parse.": (
        "Le document tel que cette bibliothèque le re-sérialise. Comparez-le à "
        "ce que vous avez envoyé -- tout ce qui a changé n'a pas survécu à "
        "l'analyse syntaxique."
    ),
    "Repeats the HTTP status, for clients that log the body only.": (
        "Répète le statut HTTP, pour les clients qui ne journalisent que le corps."
    ),
    "What went wrong. For a 400 from a document endpoint this is the parser's "
    "or validator's own message, including position where it has one.": (
        "Ce qui n'a pas fonctionné. Pour un 400 renvoyé par un point de "
        "terminaison de document, c'est le message propre à l'analyseur ou au "
        "validateur, position comprise lorsqu'il en fournit une."
    ),
    "Itemized detail: the query parameters that failed validation (a 400, for "
    "example `?lint=maybe`), or every problem in the tables sent to `POST "
    "/v1/tables/import` (a 422), each with `where` and `message`. Absent "
    "otherwise.": (
        "Détail par élément : les paramètres de requête qui ont échoué à la "
        "validation (un 400, par exemple `?lint=maybe`), ou chaque problème des "
        "tableaux envoyés à `POST /v1/tables/import` (un 422), chacun avec "
        "`where` et `message`. Absent sinon."
    ),
    "Always `ok`; a failing service does not answer.": (
        "Toujours `ok` ; un service en panne ne répond pas."
    ),
    "The installed `ddi-l` version.": "La version de `ddi-l` installée.",
    "Distribution name.": "Nom de la distribution.",
    "Every route this service exposes, keyed by short name.": (
        "Toutes les routes exposées par ce service, indexées par nom court."
    ),
    "Path to the interactive docs. `null` when started with `--no-openapi`.": (
        "Chemin vers la documentation interactive. `null` lorsque le service "
        "est démarré avec `--no-openapi`."
    ),
    "Dotted identifier of the rule. Stable -- suppress or filter on this.": (
        "Identifiant pointé de la règle. Stable -- c'est sur lui qu'il faut "
        "filtrer ou appliquer une suppression."
    ),
    "What the rule found.": "Ce que la règle a trouvé.",
    "`error` or `warning`. Only `error` makes a document invalid, matching "
    "`ddi lint`'s default exit status.": (
        "`error` ou `warning`. Seul `error` rend un document invalide, ce qui "
        "correspond au statut de sortie par défaut de `ddi lint`."
    ),
    "Prefixed path to the element that triggered the rule.": (
        "Chemin préfixé vers l'élément qui a déclenché la règle."
    ),
    "Every rule result, in document order.": (
        "Tous les résultats de règles, dans l'ordre du document."
    ),
    "XSD failures, because a profile validates as well as lints.": (
        "Échecs XSD, puisqu'un profil valide en plus d'analyser."
    ),
    "Results from the rules the profile selects.": (
        "Résultats des règles que le profil sélectionne."
    ),
    "What the schema objected to.": "Ce que le schéma a rejeté.",
    "Always `error` -- a document either satisfies the XSD or does not.": (
        "Toujours `error` -- un document satisfait le XSD ou non."
    ),
    "Path to the offending element, when the validator reports one.": (
        "Chemin vers l'élément fautif, lorsque le validateur en indique un."
    ),
    "1-based line in the submitted document.": (
        "Ligne dans le document soumis, indexée à partir de 1."
    ),
    "1-based column, when the validator reports one.": (
        "Colonne indexée à partir de 1, lorsque le validateur en indique une."
    ),
    "The element's start tag, to orient a reader.": (
        "La balise ouvrante de l'élément, pour situer le lecteur."
    ),
    "The finding, from whichever check produced it.": (
        "Le constat, quelle que soit la vérification qui l'a produit."
    ),
    "`error` or `warning`.": "`error` ou `warning`.",
    "Which check produced it: `schema` or `lint`.": (
        "Quelle vérification l'a produit : `schema` ou `lint`."
    ),
    "Set on schema issues.": "Renseigné sur les problèmes de schéma.",
    "Human-readable position. Schema issues render as `line N, xpath ...`; "
    "lint findings carry the element path.": (
        "Position lisible. Les problèmes de schéma s'affichent comme "
        "`line N, xpath ...` ; les constats de lint portent le chemin de "
        "l'élément."
    ),
    "Set on lint findings.": "Renseigné sur les constats de lint.",
    "`true` when nothing at *error* severity was found. Warnings are reported "
    "but do not make a document invalid -- the same rule `ddi lint` applies to "
    "its exit status. This is the field to branch on.": (
        "`true` lorsque rien n'a été trouvé au niveau de sévérité *error*. Les "
        "avertissements sont signalés mais ne rendent pas un document invalide "
        "-- la même règle que `ddi lint` applique à son statut de sortie. "
        "C'est le champ sur lequel brancher."
    ),
    "XSD failures. Empty when the document validates.": (
        "Échecs XSD. Vide lorsque le document est valide."
    ),
    "Style and convention findings. Empty when `?lint=false` was passed.": (
        "Constats de style et de convention. Vide lorsque `?lint=false` a été passé."
    ),
    "Both lists again, flattened and normalized -- read this one to render a report.": (
        "Les deux listes à nouveau, aplaties et normalisées -- lisez celle-ci "
        "pour produire un rapport."
    ),
    "Used when a document declares no version and none is requested.": (
        "Utilisée lorsqu'un document ne déclare aucune version et qu'aucune "
        "n'est demandée."
    ),
    "Every release accepted in `?version=`.": (
        "Toutes les versions acceptées dans `?version=`."
    ),
    # --- Metadata tables and the Colectica layout ---------------------------
    "`colectica` writes a FragmentInstance as Colectica Designer does (UTF-8 "
    "with a byte-order mark, one item per fragment), so an unchanged Colectica "
    "export comes back byte for byte. Only for a FragmentInstance.": (
        "`colectica` écrit une FragmentInstance comme Colectica Designer (UTF-8 "
        "avec indicateur d'ordre des octets, un élément par fragment) : un "
        "export Colectica inchangé revient octet pour octet. Seulement pour une "
        "FragmentInstance."
    ),
    "The metadata tables and their columns": (
        "Les tableaux de métadonnées et leurs colonnes"
    ),
    "Every table `POST /v1/tables/import` reads, and every column, with what "
    "goes in it: enough to build a form or check a file before sending it.": (
        "Chaque tableau que lit `POST /v1/tables/import`, et chaque colonne, "
        "avec son contenu : de quoi construire un formulaire ou vérifier un "
        "fichier avant de l'envoyer."
    ),
    "The settings and one of the tables": "Les paramètres et l'un des tableaux",
    "The response lists every table; this example shows `concepts` only.": (
        "La réponse énumère tous les tableaux ; cet exemple ne montre que `concepts`."
    ),
    "Every table `POST /v1/tables/import` reads, in display order.": (
        "Chaque tableau que lit `POST /v1/tables/import`, dans l'ordre d'affichage."
    ),
    "The rows the `settings` table takes.": (
        "Les lignes que prend le tableau `settings`."
    ),
    "What separates several ids in one cell.": (
        "Ce qui sépare plusieurs id dans une cellule."
    ),
    "What starts the name of a column of your own.": (
        "Ce par quoi commence le nom d'une colonne à vous."
    ),
    "The file name without `.csv`, or the sheet name.": (
        "Le nom du fichier sans `.csv`, ou le nom de la feuille."
    ),
    "What one row is.": "Ce qu'est une ligne.",
    "Whether it takes `custom:<name>` columns, stored as `r:UserAttributePair`.": (
        "S'il accepte des colonnes `custom:<nom>`, enregistrées comme "
        "`r:UserAttributePair`."
    ),
    "Its columns, in order.": "Ses colonnes, dans l'ordre.",
    "The column's name in the header row.": (
        "Le nom de la colonne dans la ligne d'en-tête."
    ),
    "What goes in it.": "Ce qu'elle contient.",
    "Whether every row must fill it.": "Si chaque ligne doit la remplir.",
    "Whether it takes one column per language: `label@en`, `label@fr`.": (
        "Si elle se répète en une colonne par langue : `label@en`, `label@fr`."
    ),
    "The table whose `id`s it holds, if it points at one.": (
        "Le tableau dont elle contient des `id`, si elle en désigne un."
    ),
    "Whether it takes several values separated by `|`.": (
        "Si elle accepte plusieurs valeurs séparées par `|`."
    ),
    "The setting, in the `setting` column.": "Le paramètre, dans la colonne `setting`.",
    "Whether it must be given.": "S'il doit être fourni.",
    "Its value when not given; `null` if required.": (
        "Sa valeur s'il n'est pas fourni ; `null` s'il est requis."
    ),
    "What it sets.": "Ce qu'il fixe.",
    "Download the metadata tables to fill in": (
        "Télécharger les tableaux de métadonnées à remplir"
    ),
    "The tables, as a workbook or (with `?format=zip`) a zip of CSV files, "
    "sent as an attachment.": (
        "Les tableaux, en classeur ou (avec `?format=zip`) en zip de fichiers "
        "CSV, envoyés en pièce jointe."
    ),
    "The blank workbook": "Le classeur vide",
    "One sheet per table and a README sheet listing every column.": (
        "Une feuille par tableau et une feuille README qui décrit chaque colonne."
    ),
    "The blank CSV files": "Les fichiers CSV vides",
    "One CSV file per table, and a README.txt listing every column.": (
        "Un fichier CSV par tableau, et un README.txt qui décrit chaque colonne."
    ),
    "An .xlsx workbook, one sheet per table.": (
        "Un classeur .xlsx, une feuille par tableau."
    ),
    "A zip of CSV files, one per table.": "Un zip de fichiers CSV, un par tableau.",
    "A language that is not a language tag, or the example asked for in "
    "languages other than English and French.": (
        "Une langue qui n'est pas une étiquette de langue, ou l'exemple demandé "
        "dans d'autres langues que l'anglais et le français."
    ),
    "A malformed language tag": "Une étiquette de langue mal formée",
    "`xlsx` for one workbook, `zip` for one CSV file per table.": (
        "`xlsx` pour un classeur, `zip` pour un fichier CSV par tableau."
    ),
    "The bilingual example that fills every table, instead of empty tables. In "
    "English and French only.": (
        "L'exemple bilingue qui remplit chaque tableau, au lieu de tableaux "
        "vides. En anglais et en français seulement."
    ),
    "The languages to give columns such as `label@en` for. Repeat it for "
    "each: `?lang=en&lang=fr`. Defaults to English and French.": (
        "Les langues pour lesquelles créer des colonnes comme `label@en`. "
        "Répétez-le pour chacune : `?lang=en&lang=fr`. Par défaut, l'anglais "
        "et le français."
    ),
    "Load metadata tables as DDI": "Charger des tableaux de métadonnées en DDI",
    "The metadata tables: an .xlsx workbook with one sheet per table, or a "
    ".zip of CSV files, one per table, sent as the raw request body. `curl "
    "--data-binary @my-survey.xlsx` is the shape.": (
        "Les tableaux de métadonnées : un classeur .xlsx avec une feuille par "
        "tableau, ou un .zip de fichiers CSV, un par tableau, envoyé tel quel "
        "dans le corps de la requête. `curl --data-binary @my-survey.xlsx` en "
        "donne la forme."
    ),
    "The example workbook": "Le classeur d'exemple",
    "A bilingual labour survey that fills every table. Download it, then "
    "choose it as the file to send.": (
        "Une enquête bilingue sur le travail qui remplit chaque tableau. "
        "Téléchargez-le, puis choisissez-le comme fichier à envoyer."
    ),
    "The example as CSV files": "L'exemple en fichiers CSV",
    "The same tables as a zip of CSV files, one file per table.": (
        "Les mêmes tableaux en zip de fichiers CSV, un fichier par tableau."
    ),
    "The agency of every item; overrides `settings`.": (
        "L'agence de chaque élément ; remplace `settings`."
    ),
    "The version of items without their own; overrides `settings`.": (
        "La version des éléments qui n'en ont pas ; remplace `settings`."
    ),
    "The language of names; overrides `settings`.": (
        "La langue des noms ; remplace `settings`."
    ),
    "Write a DDIInstance with the items inside a study of this title, instead "
    "of a Colectica FragmentInstance. The tables that describe studies, "
    "groups, people, variable groups, processing, quality or comparisons do "
    "not fit in a study document.": (
        "Écrire une DDIInstance avec les éléments dans une étude de ce titre, "
        "au lieu d'une FragmentInstance Colectica. Les tableaux qui décrivent "
        "des études, des groupes, des personnes, des groupes de variables, des "
        "traitements, la qualité ou des comparaisons n'ont pas leur place dans "
        "un document d'étude."
    ),
    "A Colectica FragmentInstance holding every item, or with `?study=` a "
    "DDIInstance study.": (
        "Une FragmentInstance Colectica qui contient tous les éléments, ou, avec "
        "`?study=`, une étude DDIInstance."
    ),
    "One concept and its variable": "Un concept et sa variable",
    "From a zip of three CSV files: `settings.csv` (the agency), "
    "`concepts.csv` (AGE) and `variables.csv` (AGE, a numeric variable "
    "measuring that concept). Written as Colectica Designer writes an export, "
    "so it imports into a Colectica repository.": (
        "À partir d'un zip de trois fichiers CSV : `settings.csv` (l'agence), "
        "`concepts.csv` (AGE) et `variables.csv` (AGE, une variable numérique "
        "qui mesure ce concept). Écrite comme Colectica Designer écrit un "
        "export : elle s'importe dans un dépôt Colectica."
    ),
    "The body was empty, or not an .xlsx workbook or a .zip of CSV files.": (
        "Le corps était vide, ou n'était ni un classeur .xlsx ni un .zip de "
        "fichiers CSV."
    ),
    "Not a workbook or a zip": "Ni un classeur ni un zip",
    "The tables were read but have problems: `extra` lists every one, with "
    "its file (or sheet), row and column.": (
        "Les tableaux ont été lus mais ont des problèmes : `extra` les énumère "
        "tous, avec leur fichier (ou feuille), leur ligne et leur colonne."
    ),
    "Tables with a problem": "Des tableaux avec un problème",
    "Every problem found, at once, each with its file (or sheet), row and "
    "column, so one request lists everything to fix.": (
        "Tous les problèmes trouvés, d'un coup, chacun avec son fichier (ou sa "
        "feuille), sa ligne et sa colonne : une seule requête énumère tout ce "
        "qu'il faut corriger."
    ),
}

#: Available translations, by locale code. `en` is absent on purpose: it is the
#: source language, not a translation of anything.
LOCALES: Final[dict[str, dict[str, str]]] = {"fr": _FR}


def _walk(node: Any, visit: Any) -> None:
    """Apply ``visit(container, key, text)`` to every translatable string.

    Skips :data:`_OPAQUE_KEYS` entirely rather than merely declining to
    translate them, so a sample document containing a ``description`` key is
    never even inspected.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key in _OPAQUE_KEYS:
                continue
            if key in TRANSLATABLE_KEYS and isinstance(value, str):
                visit(node, key, value)
            else:
                _walk(value, visit)
    elif isinstance(node, list):
        for item in node:
            _walk(item, visit)


def translate_schema(schema: dict[str, Any], locale: str) -> dict[str, Any]:
    """Return ``schema`` rendered in ``locale``.

    The input is never mutated: Litestar reuses one schema object for every
    request. A string with no catalog entry is left in English;
    :func:`missing_translations` reports such gaps.

    Args:
        schema: The serialized OpenAPI document, as ``OpenAPI.to_schema()``
            returns it.
        locale: A key of :data:`LOCALES`, or :data:`DEFAULT_LOCALE`.

    Returns:
        A deep copy with every known string replaced, or ``schema`` itself when
        ``locale`` is the default or unknown.
    """
    catalog = LOCALES.get(locale)
    if catalog is None:
        return schema

    translated = copy.deepcopy(schema)

    def visit(container: dict[str, Any], key: str, text: str) -> None:
        replacement = catalog.get(text)
        if replacement is not None:
            container[key] = replacement

    _walk(translated, visit)
    return translated


def _strings(schema: dict[str, Any]) -> set[str]:
    """Every translatable string reachable in ``schema``."""
    collected: set[str] = set()
    _walk(schema, lambda _container, _key, text: collected.add(text))
    return collected


def missing_translations(schema: dict[str, Any], locale: str) -> list[str]:
    """Strings in ``schema`` that ``locale`` has no entry for.

    Non-empty means an endpoint description has no translation yet.
    """
    catalog = LOCALES.get(locale, {})
    return sorted(text for text in _strings(schema) if text not in catalog)


def unused_translations(schema: dict[str, Any], locale: str) -> list[str]:
    """Catalog entries for ``locale`` that no longer appear in ``schema``.

    Non-empty means a translation whose English source text has changed.
    """
    catalog = LOCALES.get(locale, {})
    present = _strings(schema)
    return sorted(text for text in catalog if text not in present)
