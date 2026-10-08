# Recettes CLI

Le point d’entrée `ddi` regroupe les commandes de validation et de
transformation des documents d’instance. Cette page rassemble les tâches les
plus courantes sous forme de commandes à copier et à adapter.

!!! note "Chemins des exemples embarqués"
    Lorsque ``ddi-l`` est installé depuis une roue, les échantillons XML
    résident à côté du paquet. Exportez une variable d’aide avant d’exécuter les
    commandes pour que les chemins soient valides sur toutes les plates-formes :

    ```bash
    export DDI_L_FIXTURES=$(python -c "from pathlib import Path; import ddi_l; print(Path(ddi_l.__file__).resolve().parent / 'examples' / 'tests' / 'fixtures')")
    ```

    Remplacez ``src/ddi_l/examples/tests/fixtures/...`` dans les exemples par ``$DDI_L_FIXTURES/...``
    si vous ne travaillez pas depuis un dépôt cloné.

## Valider des instances avec `ddi validate`

Utilisez l’outil de validation comme contrôle préalable avant de committer des
modifications XML ou de diffuser un nouvel extrait. La commande renvoie le code
de sortie `0` pour les charges utiles valides et `1` lorsqu’elle détecte des
problèmes de schéma ou de lint.

=== "Commande"
    ```bash
    ddi validate src/ddi_l/examples/tests/fixtures/minimal_instance.xml
    ```

=== "Résultat attendu"
    ```text
    Document is valid.
    ```

Passez `-` pour lire depuis l’entrée standard lorsque vous enchaînez des outils.
Les exécutions réussies affichent exactement `Document is valid.` (sans emoji
ni préfixe), tandis que les échecs produisent du JSON structuré pour que les
pipelines d’automatisation puissent réagir de manière programmatique.

!!! warning "Protéger les artéfacts de validation"
    Épurez les données personnelles ou confidentielles du JSON (ou limitez-en la
    diffusion) avant de le partager en dehors de l’équipe immédiate. Passez
    `--redact-context` pour supprimer l’extrait contextuel de la sortie CLI et
    combinez l’option avec `--validate` pour `to-json` et `roundtrip` lorsque vos
    pipelines reproduisent les diagnostics. Lors de l’utilisation des assistants
    Python, `validation.validate_document(..., include_context=False)` offre la
    même protection. Pour les démarches de rédaction, consultez les
    [recommandations du carnet d'automatisation](tutorials/automation-playbook.md#5-mettre-en-evidence-les-constats-dans-les-tableaux-de-bord-ci).

=== "Exécution en échec"
    ```bash
    cat src/ddi_l/examples/tests/fixtures/invalid_instance_missing_id.xml | ddi validate
    ```

    ```text
    error: Missing required identification element(s): ID (line 3)
        at /DDIInstance
        context: <DDIInstance>
    1 issue found.
    ```

=== "JSON des anomalies"
    ```bash
    ddi validate --format json src/ddi_l/examples/tests/fixtures/invalid_instance_missing_id.xml
    ```

    ```json
    [
      {
        "message": "Missing required identification element(s): ID",
        "xpath": "/DDIInstance",
        "severity": "error",
        "line": 3,
        "column": null,
        "context": "<DDIInstance>"
      }
    ]
    ```

=== "JSON caviardé"
    ```bash
    ddi validate --format json --redact-context src/ddi_l/examples/tests/fixtures/invalid_instance_missing_id.xml
    ```

    ```json
    [
      {
        "message": "Missing required identification element(s): ID",
        "xpath": "/DDIInstance",
        "severity": "error",
        "line": 3,
        "column": null
      }
    ]
    ```

Poursuivez avec la page [Valider et lint les contenus DDI](validation.fr.md)
pour une présentation détaillée des règles disponibles, des profils
personnalisés et des options de configuration avancées.

## Ajuster les contrôles d'analyse avec `ddi lint`

Exécutez les règles d'analyse directement et personnalisez les contrôles
intégrés sans écrire de code Python. Combinez les réglages d'agence, les
bascules de citation et les exigences linguistiques pour refléter la politique
de votre organisation.

Utilisez `ddi lint --list-rules` ou `ddi lint --list-profiles` pour inspecter
les contrôles disponibles avant de les exécuter. Associez `--list-format table`
à l'une de ces options pour un affichage en colonnes compact plutôt qu'un JSON
délimité par des sauts de ligne.

=== "Commande"
    ```bash
    ddi lint src/ddi_l/examples/tests/fixtures/minimal_instance.xml \
      --allowed-agency org.example --required-citation-language en \
      --no-require-citation-title --skip-rule ddi.agency.allowed
    ```

=== "Effet"
    - Active le contrôle d'agence et le restreint à ``org.example``. Ce contrôle
      est désactivé par défaut : `ddi-l` n'a aucune base pour décider quels
      identifiants d'organisation sont légitimes, il ne s'applique donc qu'une
      fois que vous fournissez l'ensemble accepté par votre organisation.
    - Impose des titres de citation en anglais tout en rendant la règle du titre
      de citation optionnelle.
    - Ignore le constat de la liste blanche d'agences dans le calcul du code de
      sortie et dans la charge utile produite.
    - Renvoie le code de sortie ``0`` sauf si un constat de gravité supérieure ou
      égale à la valeur par défaut ``error`` est émis. Passez
      ``--fail-severity warning`` pour échouer aussi sur les avertissements, ce
      qui est souhaitable une fois qu'un corpus est propre.

Associez ces options à ``--profile`` pour exécuter un profil personnalisé, ou à
``--validate`` pour inclure les problèmes de schéma aux côtés des constats
d'analyse dans le JSON produit.

## Tester les modifications avec `ddi roundtrip`

`ddi roundtrip` re-sérialise un document après l’avoir analysé avec le modèle
interne. Utilisez-le pour détecter les problèmes de formatage, les espaces de
noms manquants ou les contenus invalides introduits lors d’éditions manuelles.

=== "Commande"
    ```bash
    ddi roundtrip src/ddi_l/examples/tests/fixtures/minimal_instance.xml --validate
    ```

=== "Résultat attendu"
    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <DDIInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <r:Agency>example.agency</r:Agency>
      <r:ID>minimal-instance</r:ID>
      <r:Version>1.0</r:Version>
      <r:Citation>
        <r:Title>
          <r:String xml:lang="en">Minimal Instance</r:String>
        </r:Title>
      </r:Citation>
    </DDIInstance>
    ```

Ajoutez `--no-pretty-print` ou `--no-declaration` lorsque vous comparez des
fichiers qui doivent conserver leur mise en forme d’origine. Pour écrire sur le
disque, indiquez un chemin de destination plutôt que `-`. Avec l’option
`--validate`, la commande se comporte comme `ddi validate` en renvoyant le code
`1` et en produisant les anomalies JSON si la source est invalide.

Le [Playbook d’automatisation en ligne de commande](tutorials/automation-playbook.fr.md)
montre comment intégrer cette étape avec les conversions et la préparation de
paquets dans un pipeline de publication plus large.

## Exporter des instantanés avec `ddi to-json`

Transformez le XML en structure JSON normalisée pour les tests d’intégration,
les miroirs de contenu ou les API aval. Le convertisseur réutilise
`DDIDocument.to_dict()` de sorte que la structure reflète le modèle Python.

=== "Commande"
    ```bash
    ddi to-json src/ddi_l/examples/tests/fixtures/minimal_instance.xml --validate --indent 2
    ```

=== "Résultat attendu"
    ```json
    {
      "@isMaintainable": true,
      "{ddi:reusable:3_3}Agency": "example.agency",
      "{ddi:reusable:3_3}ID": {
        "@type": "ID",
        "#text": "minimal-instance"
      },
      "{ddi:reusable:3_3}Version": "1.0",
      "{ddi:reusable:3_3}Citation": {
        "{ddi:reusable:3_3}Title": {
          "{ddi:reusable:3_3}String": {
            "@{http://www.w3.org/XML/1998/namespace}lang": "en",
            "#text": "Minimal Instance"
          }
        }
      }
    }
    ```

Le convertisseur écrit uniquement le JSON sur la sortie standard : redirigez-le
vers un fichier (`> build/artifacts/minimal.json`) ou chaînez-le avec d’autres
programmes selon vos besoins. Associez-le à `jq` ou à des outils similaires pour
extraire des sections spécifiques lors de la préparation de paquets de
relecture.

## Intégrer le CLI dans une chaîne CI

Considérez la validation et la conversion comme des tests de non-régression en
les exécutant dans vos workflows d’intégration continue. L’exemple ci-dessous
montre un job GitHub Actions qui valide tous les fichiers XML et maintient les
résultats de round-trip à jour.

```yaml
name: Validate DDI payloads

on:
  push:
    paths:
      - "**/*.xml"
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install ddi-l
        run: |
          pip install . lxml
      - name: Validate XML fixtures
        run: |
          set -euo pipefail
          find src/ddi_l/examples/tests/fixtures -name "*.xml" -print0 \
            | xargs -0 -n1 -P4 ddi validate
      - name: Rebuild round-trip artefacts
        run: |
          mkdir -p build/roundtrip
          for input in src/ddi_l/examples/tests/fixtures/*.xml; do
            output="build/roundtrip/$(basename "$input")"
            ddi roundtrip "$input" --output "$output" --validate
          done
```

Complétez le workflow avec `ddi to-json` pour publier des instantanés lisibles
par machine aux côtés des sorties XML ou déléguez à un script sur mesure comme
proposé dans le [Playbook d’automatisation en ligne de commande](tutorials/automation-playbook.fr.md).
