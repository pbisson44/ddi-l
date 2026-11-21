---
description: >-
  Module 19 facultatif du cours ddi-l : avec l'extra server, faire tourner
  ddi-l comme service HTTP, valider, analyser et convertir des documents par
  HTTP, lire ses codes d'état et choisir des réglages sûrs pour un service
  partagé.
---

# Module 19 (facultatif) : Servir ddi-l par HTTP

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Démarrer le service avec `ddi serve`, vérifier qu'il tourne
      avec `/health`, et trouver les paramètres de requête d'un point de
      terminaison dans la documentation interactive, à `/schema`.
    - **O2.** Valider et analyser (lint) un document par HTTP, depuis le
      terminal et depuis Python, et lire `valid`, `schema_issues` et
      `lint_findings` dans la réponse.
    - **O3.** Convertir un document en JSON et inversement par HTTP, et
      vérifier que l'aller-retour a gardé chaque octet.
    - **O4.** Dire, d'après un code d'état et son `detail`, ce qui n'allait
      pas dans une requête (400, 405, 413, 503 ou 504), et corriger la
      requête.
    - **O5.** Choisir les réglages d'un service partagé (adresse, plus gros
      document, origines permises, documentation interactive) et construire
      le service avec `create_app(ServerConfig(...))`.

**Prérequis :** [Module 7](module-07-cli-validation.fr.md). Ce module est
facultatif : le projet de synthèse n'en a pas besoin.

!!! warning "Installez d'abord l'extra server"
    Le service demande l'extra `server`, qui ajoute Litestar (le cadriciel
    web) et uvicorn (le programme qui le sert). `pip install ddi-l` seul
    n'installe ni l'un ni l'autre :

    ```bash
    pip install -U "ddi-l[server]"
    ```

**Durée :** 45 min en autonomie / 60 min avec instructeur.

**Nouveau dans ce module :** `ddi serve`, `/health`, `/schema`, `POST
/v1/validate`, `POST /v1/lint`, `POST /v1/convert/json`, `POST
/v1/convert/xml`, `create_app()`, `ServerConfig`, le `TestClient` de
Litestar.

---

## 1. Pourquoi un service ?

Au module 7, vous avez lancé `ddi validate` et `ddi lint` sur votre propre
machine. D'autres personnes et d'autres programmes peuvent avoir besoin des
mêmes vérifications : un formulaire de dépôt sur un site web, une chaîne de
traitement écrite en Java ou en R, une tâche d'intégration continue dans un
autre langage. Ils ne peuvent pas tous installer Python et `ddi-l`.

Un **service** répond à des requêtes envoyées par HTTP, le protocole du web.
Vous faites tourner `ddi-l` une fois, comme service, et tout programme
capable d'envoyer une requête HTTP peut valider un document. Le service
appelle le même code que la commande `ddi` : les deux donnent la même
réponse pour le même document.

Chaque requête va à un **point de terminaison** : un chemin comme
`/v1/validate`, avec une méthode. `GET` demande quelque chose ; `POST` envoie
quelque chose, ici un document, dans le **corps** de la requête. Le service
répond par un **code d'état** (200 veut dire que tout a fonctionné) et, ici,
par un corps en JSON.

## 2. Démarrer le service

Dans un terminal :

```bash
ddi serve
```

```text
Interactive API docs: http://localhost:8000/schema
OpenAPI document:     http://localhost:8000/schema/openapi.json
INFO:     Started server process [1550]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Le service écoute maintenant sur le port 8000 de **cette machine
seulement** (`127.0.0.1`), jusqu'à ce que vous appuyiez sur Ctrl+C. Laissez
ce terminal ouvert et ouvrez-en un second pour les commandes qui suivent.

!!! tip "Le port 8000 est déjà pris ?"
    Si `ddi serve` s'arrête avec « address already in use » (sous Windows :
    « only one usage of each socket address ... is normally permitted »), un
    autre programme écoute déjà sur le port 8000 : c'est le cas de
    `mkdocs serve` par défaut, par exemple. Démarrez le service sur un autre
    port avec `ddi serve --port 8001`, et utilisez 8001 au lieu de 8000 dans
    les adresses de ce module. Une réponse qui est une page web disant
    « 404 - Not found » veut dire qu'une commande est encore allée au port
    8000, vers l'autre programme.

Vérifiez qu'il répond, depuis le second terminal :

=== "Windows PowerShell"

    ```powershell
    Invoke-RestMethod http://localhost:8000/health
    ```

=== "macOS et Linux"

    ```bash
    curl http://localhost:8000/health
    ```

```text
{"status":"ok","version":"X.Y.Z"}
```

PowerShell affiche les deux mêmes champs sous forme de petit tableau. À la
place de `X.Y.Z`, vous voyez la version de `ddi-l` que vous avez installée.

!!! warning "Windows PowerShell a son propre curl"
    Dans Windows PowerShell, `curl` est une autre commande, et `@` y veut
    dire autre chose : les commandes pour macOS et Linux y échouent donc
    (`The splatting operator '@' cannot be used...`). Utilisez l'onglet
    Windows PowerShell, ou tapez `curl.exe` et mettez le nom du fichier
    entre guillemets :
    `curl.exe --data-binary "@pets.xml" http://localhost:8000/v1/validate`.

Ouvrez maintenant <http://localhost:8000/schema> dans un navigateur. C'est la
**documentation interactive** : chaque point de terminaison, ce qu'il faut
envoyer, ses paramètres de requête (la partie `?nom=valeur` d'une adresse)
et ce qui revient, avec des exemples. Ouvrez `POST /v1/validate`, cliquez
sur **Try it out**, puis sur **Execute** : le corps est rempli avec un
document valide, et vous obtenez une vraie réponse. `/schema/fr` montre la
même page avec les descriptions en français.

## 3. Valider et analyser

Enregistrez un petit document à envoyer :

```python
import ddi_l as ddi

doc = ddi.new_study(title="Pet Survey", agency="example.org")
doc.add_question(text="How many pets live here?")
doc.add_variable(name="PetCount")
doc.save("pets.xml")
```

Envoyez-le à `/v1/validate` depuis le second terminal :

=== "Windows PowerShell"

    ```powershell
    Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/validate `
      -InFile pets.xml -ContentType application/xml | ConvertTo-Json -Depth 5
    ```

=== "macOS et Linux"

    ```bash
    curl --data-binary @pets.xml http://localhost:8000/v1/validate
    ```

`--data-binary @pets.xml` et `-InFile pets.xml` envoient tous deux le
fichier comme corps, octet pour octet. La réponse a quatre champs :

| Champ | Ce qu'il contient |
| --- | --- |
| `valid` | `true` quand le document n'a aucune erreur, du schéma ou de l'analyse |
| `schema_issues` | Chaque erreur de schéma : `message`, `line`, `xpath`, `context` |
| `lint_findings` | Chaque constat de l'analyse : `rule_id`, `severity`, `message`, `location` |
| `messages` | Tous ensemble dans une liste, chacun marqué de sa `source` |

Les avertissements ne rendent pas un document invalide, tout comme
`ddi lint` retourne 0 quand il ne signale que des avertissements.

### La même requête depuis Python

Pour essayer le service depuis Python, vous n'avez pas besoin de le
démarrer. Litestar, qu'installe l'extra `server`, offre un **client de
test** qui envoie des requêtes au service à l'intérieur de votre propre
programme. C'est aussi ainsi que vous testeriez les réglages d'un service :

```python
import logging
from pathlib import Path

from ddi_l.server import create_app
from litestar.testing import TestClient

# Le client de test journalise chaque requête ; ne gardez que ce que vous affichez.
logging.getLogger("httpx").setLevel(logging.WARNING)

client = TestClient(app=create_app())
xml = Path("pets.xml").read_bytes()

response = client.post("/v1/validate", content=xml)
print(response.status_code)  # -> 200
report = response.json()
print(report["valid"], len(report["schema_issues"]))  # -> True 0
for finding in report["lint_findings"]:
    print(finding["severity"], finding["rule_id"])
# -> warning ddi.maintainable.labels
```

La question et la variable n'ont pas de libellé, d'où deux avertissements.
Le document reste valide.

`client.post()` et `client.get()` prennent les mêmes chemins, paramètres de
requête et corps que `curl` : tout ce qui suit fonctionne aussi avec un
service en marche.

### Paramètres de requête

Les options de `ddi lint` voyagent comme paramètres de requête :

| Paramètre | Sur | Effet |
| --- | --- | --- |
| `lint=false` | `/v1/validate` | Validation du schéma seulement |
| `version=3.2` | chaque point de terminaison qui reçoit un document | Valider selon cette version de DDI, pas celle que déclare le document |
| `rule=...` | `/v1/lint` | N'exécuter que cette règle (répétez-le pour plusieurs) |
| `skip_rule=...` | `/v1/lint` | Écarter les constats de cette règle |
| `profile=...` | `/v1/lint` | Exécuter un profil d'analyse |
| `lint_config=...` | `/v1/lint`, `/v1/validate` | Le JSON que lit `ddi lint --lint-config` |

```python
quiet = client.post(
    "/v1/lint", params={"skip_rule": "ddi.maintainable.labels"}, content=xml
)
print(quiet.json())  # -> {'lint_findings': []}
```

Depuis le terminal, mettez-les dans l'adresse, entre guillemets, car `&` et
`?` ont un sens pour le terminal :

=== "Windows PowerShell"

    ```powershell
    Invoke-RestMethod -Method Post -InFile pets.xml -ContentType application/xml `
      -Uri "http://localhost:8000/v1/lint?skip_rule=ddi.maintainable.labels"
    ```

=== "macOS et Linux"

    ```bash
    curl --data-binary @pets.xml 'http://localhost:8000/v1/lint?skip_rule=ddi.maintainable.labels'
    ```

## 4. Convertir en JSON et inversement

`/v1/convert/json` transforme un document en JSON, comme `ddi to-json`, et
`/v1/convert/xml` retransforme ce JSON en XML :

```python
as_json = client.post("/v1/convert/json", content=xml)
print(as_json.headers["content-type"])  # -> application/json
back = client.post(
    "/v1/convert/xml",
    content=as_json.content,
    headers={"Content-Type": "application/json"},
)
print(back.content == xml)  # -> True
```

L'aller-retour a redonné les mêmes octets. Envoyez du JSON avec l'en-tête
`Content-Type: application/json`, pour que le service lise le corps comme du
JSON :

=== "Windows PowerShell"

    ```powershell
    Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/convert/json `
      -InFile pets.xml -ContentType application/xml -OutFile pets.json
    Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/convert/xml `
      -InFile pets.json -ContentType application/json -OutFile pets-back.xml
    ```

=== "macOS et Linux"

    ```bash
    curl --data-binary @pets.xml http://localhost:8000/v1/convert/json -o pets.json
    curl -H 'Content-Type: application/json' --data-binary @pets.json \
      http://localhost:8000/v1/convert/xml -o pets-back.xml
    ```

`-o` et `-OutFile` enregistrent la réponse dans un fichier, avec ses octets
tels quels.

## 5. Quand une requête échoue

Un code d'état de 400 ou plus veut dire que la requête n'a pas abouti. Le
corps dit pourquoi, dans `detail` :

```python
answer = client.post("/v1/validate", params={"version": "4.0"}, content=xml)
print(answer.status_code, answer.json()["detail"])
# -> 400 Unsupported DDI schema version: '4.0'
```

| Code | Signifie | Correction |
| --- | --- | --- |
| 400 Bad Request | Le corps ou un paramètre est illisible : pas du XML, pas du JSON, une `version` inconnue | Envoyez le fichier lui-même, avec `--data-binary`, et vérifiez le paramètre |
| 405 Method Not Allowed | La mauvaise méthode, comme `GET` sur `/v1/validate` | Utilisez `POST` pour les points de terminaison qui reçoivent un document |
| 413 Request Entity Too Large | Le corps dépasse ce que le service accepte (32 Mo par défaut) | Envoyez un fichier plus petit, ou relevez la limite au démarrage du service |
| 422 Unprocessable Content | Des tableaux de métadonnées ont été lus mais ont des problèmes (`/v1/tables/import`) | Corrigez les lignes listées dans `extra` |
| 503 Service Unavailable | Le service traite déjà autant de documents qu'il le peut | Attendez les secondes indiquées dans l'en-tête `Retry-After` et renvoyez |
| 504 Gateway Timeout | La réponse a pris plus de 60 secondes | Envoyez un document plus petit, ou parlez-en à qui fait tourner le service |

Un document qui n'est pas du DDI valide n'est **pas** une erreur : la
réponse est 200, avec `valid` à faux et les erreurs de schéma listées. 400
veut dire que le service n'a pas du tout pu lire ce que vous avez envoyé.

## 6. Le faire tourner pour d'autres

`ddi serve` seul écoute sur cette machine seulement, ce qui convient tant
que vous apprenez. Pour servir d'autres machines, la personne qui fait
tourner le service choisit ses réglages :

| Réglage | Option de `ddi serve` | Champ de `ServerConfig` | Par défaut |
| --- | --- | --- | --- |
| Adresse d'écoute | `--host 0.0.0.0` (tous les réseaux de cette machine) | (fixée par le programme serveur) | `127.0.0.1` |
| Plus gros corps | `--max-body-mb` | `max_body_bytes` | 32 Mio |
| Documents à la fois | `--max-jobs` | `max_concurrent_jobs` | le nombre de processeurs |
| Sites dont les pages peuvent l'appeler | `--cors-allow-origin` (à répéter) | `cors_allow_origins` | aucun |
| Documentation interactive | `--no-openapi` la désactive | `enable_openapi` | activée |

**CORS** (partage de ressources entre origines) est la façon dont un
navigateur décide si une page web d'un site peut appeler un service sur un
autre. Nommez chaque site qui en a besoin ; il n'y a pas d'option « tous les
sites », et c'est voulu.

Pour un vrai service, construisez-le dans un fichier Python, ici
`myapp.py`, et faites-le tourner avec uvicorn, qui peut démarrer plusieurs
processus de travail :

```python
from ddi_l.server import ServerConfig, create_app

app = create_app(
    ServerConfig(
        max_body_bytes=8 * 1024 * 1024,
        cors_allow_origins=("https://deposit.example.org",),
        enable_openapi=False,
    )
)
```

Lancez ceci depuis le dossier qui contient `myapp.py`. `myapp:app` nomme le
fichier (sans `.py`) et la variable qu'il contient : utilisez le nom de
votre propre fichier s'il diffère.

```bash
uvicorn myapp:app --host 0.0.0.0 --port 8000 --workers 4
```

Le service lit le XML avec les mêmes protections que la bibliothèque : pas
d'entités, pas d'accès au réseau, rien d'écrit sur le disque. La validation
occupe un processeur : placez le service derrière un mandataire (proxy) qui
limite le nombre de requêtes de chaque appelant, et dimensionnez-le pour
votre plus gros document. Le [guide de l'API HTTP](../server.fr.md), section
« Exploitation en sécurité », donne les détails.

---

!!! example "Scénario"
    Votre archive de données construit un formulaire de dépôt sur son site
    web. Quand un chercheur téléverse un fichier DDI, le formulaire doit
    dire tout de suite s'il est valide et en lister les problèmes. L'équipe
    web écrit du JavaScript, pas du Python. Vous faites tourner `ddi-l`
    comme service pour elle, vous lui montrez quelles requêtes envoyer et ce
    que signifient les réponses, et vous choisissez ses réglages.

---

## Exercices

1. **(O1)** Démarrez `ddi serve` et vérifiez `/health`. Puis, dans la documentation interactive, trouvez les paramètres de requête que prend `POST /v1/lint`. Vérifiez votre liste depuis Python en demandant au client de test `/v1/versions`, puis le document OpenAPI à `/schema/openapi.json`.

    **Résultat attendu :**

    ```text
    {'default': '3.3', 'supported': ['3.1', '3.2', '3.3']}
    ['version', 'profile', 'rule', 'skip_rule', 'lint_config']
    ```

    ??? success "Réponse"

        ```python
        print(client.get("/v1/versions").json())
        openapi = client.get("/schema/openapi.json").json()
        lint = openapi["paths"]["/v1/lint"]["post"]
        print([parameter["name"] for parameter in lint["parameters"]])
        ```

        `/v1/versions` liste les versions de DDI selon lesquelles le service valide, et celle qu'il utilise quand un document ne le dit pas. Le document OpenAPI est la source de la documentation interactive : sa liste correspond à ce que vous avez trouvé dans le navigateur.

2. **(O2)** Analysez `pets.xml` par HTTP avec une liste d'agences permises qui ne contient pas `example.org`, à l'aide de `lint_config`. Affichez la règle de chaque constat. Envoyez ensuite le même `lint_config` à `/v1/validate` et affichez `valid`.

    **Résultat attendu :**

    ```text
    ['ddi.agency.allowed', 'ddi.maintainable.labels', 'ddi.maintainable.labels']
    True
    ```

    ??? success "Réponse"

        ```python
        config = '{"allowed_agencies": ["ca.statcan"]}'
        found = client.post("/v1/lint", params={"lint_config": config}, content=xml)
        print([finding["rule_id"] for finding in found.json()["lint_findings"]])
        checked = client.post("/v1/validate", params={"lint_config": config}, content=xml)
        print(checked.json()["valid"])
        ```

        `ddi.agency.allowed` signale l'agence `example.org`, que la liste ne permet pas. C'est un avertissement, comme les deux libellés manquants : le document reste donc valide. La configuration ne vaut que pour cette requête : la requête suivante, sans elle, reçoit les vérifications par défaut.

3. **(O2)** Abîmez `pets.xml` comme au module 7 : remplacez `<r:Version>1</r:Version>` par `<r:Version>one</r:Version>`. Envoyez-le à `/v1/validate` et affichez le code d'état, `valid`, puis la ligne et le message de l'erreur de schéma.

    **Résultat attendu :**

    ```text
    200 False
    5 value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*']
    ```

    ??? success "Réponse"

        ```python
        broken = xml.replace(b"<r:Version>1</r:Version>", b"<r:Version>one</r:Version>", 1)
        answer = client.post("/v1/validate", content=broken)
        report = answer.json()
        print(answer.status_code, report["valid"])
        issue = report["schema_issues"][0]
        print(issue["line"], issue["message"])
        ```

        Le code d'état est 200 : le service a lu le document et fait son travail. C'est le document qui a un problème : `valid` est donc faux, et l'erreur dit où.

4. **(O3)** Convertissez `pets.xml` en JSON par HTTP, puis de nouveau en XML. Le XML qui revient est-il identique au fichier, octet pour octet ?

    **Résultat attendu :**

    ```text
    True
    ```

    ??? success "Réponse"

        ```python
        as_json = client.post("/v1/convert/json", content=xml)
        back = client.post(
            "/v1/convert/xml",
            content=as_json.content,
            headers={"Content-Type": "application/json"},
        )
        print(back.content == xml)
        ```

        Le JSON garde tout ce que contient le XML : l'aller-retour est donc exact. Ses clés portent l'espace de noms de chaque élément entre accolades, comme dans `ddi to-json` : regardez `as_json.json()` pour les voir.

5. **(O4)** Pour chaque requête qui a échoué, dites ce qui ne va pas et comment le corriger. (a) `GET /v1/validate` donne 405. (b) `POST /v1/validate?version=3.4` donne 400. (c) Un fichier de 50 Mo donne 413 avec un service démarré par `ddi serve`. (d) Une requête donne 503 à une heure chargée.

    ??? success "Réponse"

        (a) `/v1/validate` reçoit un document : il faut `POST`, avec le document comme corps. (b) Le service connaît DDI 3.1, 3.2 et 3.3 (voir `/v1/versions`) : retirez `version` ou choisissez l'une d'elles. (c) La limite par défaut est de 32 Mo : la personne qui fait tourner le service la relève, par exemple `ddi serve --max-body-mb 64`. (d) Le service traite déjà autant de documents qu'il le peut : attendez les secondes indiquées dans `Retry-After` et renvoyez. Un client écrit pour un service devrait le faire de lui-même.

6. **(O5)** Le formulaire de dépôt du scénario se trouve à `https://deposit.example.org`. Les dépôts peuvent atteindre 100 Mo. L'archive ne veut pas de la documentation interactive sur Internet. Construisez le service avec `create_app(ServerConfig(...))`, puis vérifiez avec un client de test que `/schema` a disparu et qu'une page du formulaire de dépôt peut appeler `/v1/validate`. Écrivez la commande `ddi serve` avec les mêmes réglages.

    **Résultat attendu :**

    ```text
    404
    https://deposit.example.org
    ```

    ??? success "Réponse"

        ```python
        from ddi_l.server import ServerConfig

        deposit = create_app(
            ServerConfig(
                max_body_bytes=100 * 1024 * 1024,
                cors_allow_origins=("https://deposit.example.org",),
                enable_openapi=False,
            )
        )
        checker = TestClient(app=deposit)
        print(checker.get("/schema").status_code)
        preflight = checker.options(
            "/v1/validate",
            headers={
                "Origin": "https://deposit.example.org",
                "Access-Control-Request-Method": "POST",
            },
        )
        print(preflight.headers["access-control-allow-origin"])
        ```

        Un navigateur interroge d'abord le service (cette requête `OPTIONS` est la « vérification préalable ») et n'envoie le dépôt que si la réponse nomme le site du formulaire. La commande avec les mêmes réglages :

        ```bash
        ddi serve --host 0.0.0.0 --max-body-mb 100 --cors-allow-origin https://deposit.example.org --no-openapi
        ```

---

## Quiz

???+ question "Question 1 (O1) : Vous démarrez ddi serve sur votre portable. Un collègue sur une autre machine ne l'atteint pas. Pourquoi ?"
    **A.** Le service demande un mot de passe.

    **B.** Par défaut, il écoute sur `127.0.0.1`, cette machine seulement. Démarrez-le avec `--host 0.0.0.0` pour accepter d'autres machines.

    **C.** Le port 8000 est réservé aux navigateurs.

    **D.** Le collègue doit d'abord installer `ddi-l`.

    ??? success "Réponse"
        **B.** Le réglage par défaut garde privé, sur votre machine, un
        service que vous essayez.

???+ question "Question 2 (O2) : /v1/validate répond 200 avec valid à faux. Qu'est-ce que cela veut dire ?"
    **A.** Le service a échoué.

    **B.** La requête était fausse.

    **C.** Le service a lu le document, et le document a au moins une erreur, listée dans `schema_issues` ou `lint_findings`.

    **D.** Le document a des avertissements.

    ??? success "Réponse"
        **C.** 200 dit que la requête a fonctionné. `valid` porte sur le
        document, et seules les erreurs le rendent faux.

???+ question "Question 3 (O4) : Quel code d'état dit que le service n'a pas du tout pu lire le corps ?"
    **A.** 200

    **B.** 400

    **C.** 413

    **D.** 503

    ??? success "Réponse"
        **B.** 400 Bad Request : pas du XML, pas du JSON, ou un paramètre
        qu'il ne connaît pas. 413 veut dire que le corps était trop gros
        pour être lu.

???+ question "Question 4 (O3) : Quel en-tête envoyez-vous avec un corps JSON à /v1/convert/xml ?"
    **A.** `Accept: application/xml`

    **B.** `Content-Type: application/json`

    **C.** `Content-Length: json`

    **D.** Aucun : le service devine.

    ??? success "Réponse"
        **B.** `Content-Type` dit ce qu'est le corps. Sans lui, le service
        ne peut pas distinguer le JSON d'autre chose.

???+ question "Question 5 (O5) : Une page web du site forms.example.org doit appeler le service depuis le navigateur. Que réglez-vous ?"
    **A.** `--cors-allow-origin https://forms.example.org`

    **B.** `--cors-allow-origin '*'`

    **C.** `--no-openapi`

    **D.** `--max-jobs 1`

    ??? success "Réponse"
        **A.** Nommez chaque site qui peut appeler le service. Il n'y a pas
        de joker, pour qu'un service ne s'ouvre jamais à tous les sites par
        erreur.

---

## Faites le point

- [ ] Je sais démarrer `ddi serve`, vérifier `/health` et trouver les paramètres de requête d'un point de terminaison à `/schema`. (O1)
- [ ] Je sais valider et analyser un document par HTTP et lire `valid`, `schema_issues` et `lint_findings`. (O2)
- [ ] Je sais convertir un document en JSON et inversement par HTTP, et vérifier que rien n'a été perdu. (O3)
- [ ] Je sais dire, d'après un code d'état et son `detail`, ce qui n'allait pas dans une requête, et la corriger. (O4)
- [ ] Je sais choisir les réglages d'un service partagé et le construire avec `create_app(ServerConfig(...))`. (O5)

---

!!! tip "Notes pour l'instructeur"
    - Démarrez le service au projecteur et faites la section 2 en direct :
      `/health`, puis **Try it out** dans `/schema`. Voir une vraie réponse
      dans le navigateur rend la suite concrète.
    - Apprenants sous Windows : `curl` dans Windows PowerShell 5.1 est une
      autre commande qui porte le même nom. Utilisez `Invoke-RestMethod`
      comme montré, ou tapez `curl.exe`.
    - La confusion la plus fréquente est entre « la requête a échoué » (400
      et plus) et « le document n'est pas valide » (200 avec `valid` à
      faux). Demandez à la salle laquelle un formulaire de dépôt devrait
      montrer au chercheur.
    - L'exercice 6 est celui à discuter avec qui fera tourner le service :
      qui peut l'appeler, quelle taille peut avoir un document, et si les
      pages de documentation doivent être publiques.

---

**Voir aussi :** [Module 7 : Valider depuis la ligne de commande](module-07-cli-validation.fr.md) | [API HTTP](../server.fr.md)
