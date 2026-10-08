# API HTTP

`ddi-l` fournit un service HTTP optionnel qui expose les mêmes opérations de
validation, d'analyse et de conversion que la ligne de commande. Il repose sur
[Litestar](https://litestar.dev/).

Utilisez-le lorsque la validation DDI doit être accessible depuis un
environnement qui n'est pas Python (un formulaire de dépôt, une chaîne Java, un
job d'intégration continue dans un autre langage), sans que chacun d'eux
réimplémente le traitement DDI.

!!! info "C'est le même code"
    Chaque point de terminaison est une fine enveloppe autour de
    `ddi_l.operations`, que la commande `ddi` appelle également : les deux
    donnent la même réponse pour un même document.

## Installation et démarrage

Le serveur est un extra optionnel : une installation standard ne paie jamais le
coût de Litestar.

```bash
pip install 'ddi-l[server]'
ddi serve
```

L'écoute se fait sur `127.0.0.1:8000`, c'est-à-dire cette machine uniquement.
Pour accepter des connexions extérieures :

```bash
ddi serve --host 0.0.0.0 --port 8080
```

## Documentation interactive

Ouvrez le port dans un navigateur et vous arrivez sur **[Swagger UI](https://swagger.io/tools/swagger-ui/)
à l'adresse `/schema`** : <http://localhost:8000/schema>. Un navigateur qui
demande `/` y est redirigé, il n'y a donc rien à retenir.

Elle est générée à partir du code, et non rédigée à la main, et documente les
deux sens de chaque appel :

- **Ce qu'il faut envoyer.** Chaque `POST` déclare son corps de requête, et
  « Try it out » est prérempli avec une instance DDI valide : appuyez sur Execute
  et vous obtenez une vraie réponse de validation sans avoir à composer une
  requête au préalable.
- **Paramètres de requête.** `?version=`, `?lint=` et `?profile=` apparaissent
  comme des champs à remplir, et non comme un texte qu'il faut avoir remarqué.
- **Ce qui revient.** Chaque réponse porte un exemple réel, y compris les cas
  d'échec : à quoi ressemble une erreur de schéma, et l'enveloppe
  `{"status_code", "detail"}` que renvoient un `400`, un `413`, un `503` ou un `504`.

Ces exemples sont des réponses réelles, et la suite de tests les compare à un
service en fonctionnement.

| Chemin | Contenu |
| -------- | --------- |
| `/schema` | Swagger UI ; commencez ici |
| `/schema/redoc` | [ReDoc](https://redocly.com/redoc), référence en lecture seule |
| `/schema/elements`, `/schema/rapidoc` | Autres rendus |
| `/schema/openapi.json`, `/schema/openapi.yaml` | Le document brut, pour les générateurs |
| `/schema/fr` | Swagger UI avec les descriptions en français |
| `/schema/openapi.fr.json` | Le document brut en français |

Un client d'API qui demande `/` sans `Accept: text/html` n'est pas redirigé : il
reçoit un index JSON des points de terminaison.

### Le rendu français

`/schema/fr` sert la même API avec sa prose traduite : résumés des points de
terminaison, descriptions des paramètres et des champs, légendes des exemples.
Ce qui n'est **pas** traduit, c'est tout ce qu'un client analyse : les noms de
champs, les valeurs d'énumération et les documents d'exemple sont identiques
octet pour octet à ceux du schéma anglais, car ils relèvent du contrat et non de
la documentation. `info.title` reste `ddi-l` pour la même raison.

Les boutons propres à Swagger UI (« Try it out », « Execute », « Parameters »)
restent en anglais. swagger-ui ne gère pas l'internationalisation, pas plus que
ReDoc, RapiDoc ou Stoplight : un lecteur francophone obtient donc une prose
française dans une interface à l'habillage anglais.

!!! info "Synchronisée avec l'anglais"
    La suite de tests vérifie que chaque chaîne du schéma vivant a une entrée
    française, et que chaque entrée française correspond encore à sa source
    anglaise.

## Points de terminaison

| Méthode | Chemin | Rôle |
| --------- | -------- | ------ |
| `GET` | `/` | Index du service : version et points de terminaison. |
| `GET` | `/health` | Sonde de disponibilité ; renvoie la version en cours. |
| `GET` | `/v1/versions` | Versions du schéma DDI fournies et version par défaut. |
| `POST` | `/v1/validate` | Validation par schéma et analyse (lint). |
| `POST` | `/v1/lint` | Règles d'analyse uniquement. |
| `POST` | `/v1/convert/json` | XML DDI → JSON (sans perte, réversible). |
| `POST` | `/v1/convert/jsonld` | XML DDI → JSON-LD (données liées, sens unique). |
| `POST` | `/v1/convert/xml` | JSON → XML DDI. |
| `POST` | `/v1/roundtrip` | Re-sérialise un document via la couche de modèles. |

Les points `POST` reçoivent le document dans le corps brut de la requête. Tous
acceptent `?version=3.1|3.2|3.3` pour imposer une version du schéma plutôt que
celle déclarée par le document.

### Valider

```bash
curl --data-binary @mon-etude.xml http://localhost:8000/v1/validate
```

```json
{
  "valid": true,
  "schema_issues": [],
  "lint_findings": [ ... ],
  "messages": [ ... ]
}
```

`valid` répond à la question réellement posée et ne reflète que les **erreurs** :
les avertissements sont signalés mais ne rendent pas un document invalide, ce qui
correspond au code de sortie de `ddi lint`. Ajoutez `?lint=false` pour la
validation par schéma seule.

### Analyser

```bash
curl --data-binary @mon-etude.xml http://localhost:8000/v1/lint
curl --data-binary @mon-etude.xml 'http://localhost:8000/v1/lint?profile=DDI_PROFILE_DEFAULT'
```

### Convertir

```bash
curl --data-binary @mon-etude.xml http://localhost:8000/v1/convert/json > etude.json
curl -H 'Content-Type: application/json' --data-binary @etude.json \
  http://localhost:8000/v1/convert/xml > etude.xml
```

### JSON-LD (données liées)

`/v1/convert/jsonld` restitue le document en JSON-LD à l'aide du vocabulaire
[DDI-RDF Discovery](https://rdf-vocabulary.ddialliance.org/discovery.html)
(« Disco ») de la DDI Alliance, servi en `application/ld+json` :

```bash
curl --data-binary @mon-etude.xml http://localhost:8000/v1/convert/jsonld > etude.jsonld
```

```json
{
  "@context": {"disco": "http://rdf-vocabulary.ddialliance.org/discovery#", "...": "..."},
  "@graph": [
    {
      "@id": "urn:ddi:example.org:8f3a...:1",
      "@type": "disco:Study",
      "dcterms:title": "Enquête auprès des ménages",
      "disco:variable": [{"@id": "urn:ddi:example.org:1c9d...:1"}]
    },
    {
      "@id": "urn:ddi:example.org:1c9d...:1",
      "@type": "disco:Variable",
      "skos:prefLabel": [{"@value": "Âge", "@language": "fr"}],
      "disco:question": [{"@id": "urn:ddi:example.org:44b1...:1"}]
    }
  ]
}
```

Il s'agit d'une correspondance **sémantique**, et non d'une transcription du
XML. Les études, variables, questions et univers deviennent des termes Disco,
avec Dublin Core et SKOS pour les libellés : le résultat se charge directement
dans un triplestore. Les `@id` sont les URN DDI que la bibliothèque produit
déjà, qui sont des IRI valides.

!!! warning "Avec perte et à sens unique, par conception"
    Disco couvre le sous-ensemble **de découverte** de DDI : ce dont un jeu de
    données traite, afin qu'il puisse être trouvé et comparé. Il ne dispose
    d'aucun vocabulaire pour la logique de cheminement des questionnaires, les
    dispositions d'enregistrement, les NCube ou les instructions de traitement,
    qui sont donc abandonnés plutôt qu'approximés. Sa spécification indique
    explicitement que la transformation inverse « n'est pas prévue » : il n'existe
    donc pas de point de terminaison JSON-LD → XML.

    Utilisez `/v1/convert/json` lorsque la charge utile doit redevenir du XML.
    Ce format est une transcription exacte et fait l'aller-retour via
    `/v1/convert/xml`.

## Exploitation en sécurité

Une bibliothèque analyse ce que son appelant a choisi d'ouvrir. Un service
analyse tout ce qui atteint le port : les valeurs par défaut sont donc
délibérément prudentes.

- **Le corps des requêtes est plafonné à 32 Mio.** Modifiable avec
  `--max-body-mb`. Sans plafond, une seule requête peut épuiser la mémoire d'un
  worker.
- **L'analyse XML est durcie, et le serveur n'ajoute aucun analyseur propre.**
  Il passe par le même code que la bibliothèque, qui désactive la résolution des
  entités et l'accès réseau et fait transiter l'analyse par `defusedxml`. Les
  charges d'expansion d'entités (« billion laughs ») et d'entités externes (XXE)
  sont rejetées ; `tests/test_server.py` le vérifie via HTTP.
- **Les requêtes sont limitées à 60 secondes** par défaut. Cela borne l'attente
  du *client*, pas la durée du traitement : la validation s'exécute dans un
  thread de travail et un thread Python en cours ne peut pas être annulé ; au
  dépassement, l'appelant reçoit `504` pendant que ce thread termine. C'est le
  plafond du corps de requête qui borne le travail lui-même.
- **Le travail simultané est borné.** Au plus `--max-jobs` documents sont traités
  à la fois (par défaut : le nombre de processeurs) ; les requêtes suivantes
  reçoivent `503` avec `Retry-After`. Le schéma par défaut est chargé au
  démarrage : la première requête n'a pas à en payer le coût.
- **Rien n'est écrit sur disque.** Les documents sont analysés en mémoire.
- **CORS est désactivé.** Autorisez des origines nommées avec
  `--cors-allow-origin` ; il n'existe volontairement pas d'option joker.
- **`/schema` peut être désactivé** avec `--no-openapi` pour un déploiement
  exposé sur Internet.

!!! warning "La validation est gourmande en CPU"
    Valider une grande instance occupe un worker pendant toute la durée du
    traitement. Placez le service derrière un proxy inverse imposant ses propres
    délais et limites de débit, et dimensionnez le pool de workers pour votre
    document le plus volumineux, pas pour le document médian.

## Intégration

`ddi serve` est un raccourci. Pour un déploiement réel, construisez
l'application vous-même et exécutez-la sous n'importe quel serveur ASGI :

```python
from ddi_l.server import ServerConfig, create_app

app = create_app(
    ServerConfig(
        max_body_bytes=8 * 1024 * 1024,
        cors_allow_origins=("https://metadata.example.org",),
        enable_openapi=False,
    )
)
```

```bash
uvicorn myapp:app --workers 4
```
