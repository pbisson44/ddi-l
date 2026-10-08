# Carnet d'automatisation en ligne de commande

Ce carnet enchaîne les commandes ``ddi`` en tâches automatisées reproductibles à intégrer dans vos pipelines CI/CD. Les exercices portent sur les codes de sortie, la journalisation et la conservation des fichiers produits, pour qu'une exécution en échec indique ce qu'il faut corriger.

!!! note
    Les extraits supposent que la CLI est disponible sur votre ``PATH`` (`pip install -e .`) et que vous travaillez depuis la racine du dépôt.

!!! note "Utiliser les exemples du paquet"
    La roue publiée inclut le répertoire ``examples/``. Retrouvez son chemin
    installé via ``importlib.resources`` (voir le
    [guide d'installation](../installation.md))
    plutôt que de cloner le dépôt uniquement pour accéder aux charges XML.

## 1. Valider et capturer les rapports JSON

   Le dépôt fournit un échantillon prêt à l'emploi : ``examples/Quality_of_Life.xml``. Utilisez-le ou remplacez-le par votre propre fichier avant de lancer les commandes suivantes.

1. Créez le répertoire des rapports avec ``mkdir -p reports`` afin que la redirection fonctionne même dans un espace de travail vierge.
2. Exécutez ``ddi validate --format json examples/Quality_of_Life.xml > reports/validation.json``.
3. Vérifiez le code de sortie : zéro indique la réussite, tandis que ``1`` signale un échec de validation. Le flux redirigé est un tableau JSON d'anomalies, vide lorsque le document est valide.
4. Capturez la sortie dans votre pipeline CI pour que les exécutions réussies enregistrent un tableau vide et que les échecs conservent la charge JSON pour analyse ultérieure.

## 2. Convertir du XML en JSON pour les systèmes aval

1. Créez un répertoire de sortie (par exemple ``build/artifacts``).
2. Exécutez ``ddi to-json examples/Quality_of_Life.xml --indent 2 > build/artifacts/Quality_of_Life.json``.
3. Stockez ``build/artifacts/Quality_of_Life.json`` parmi vos artefacts de build afin que les systèmes analytiques consomment des données structurées sans parser l'XML.

## 3. Vérifier les conversions aller-retour

1. Créez le répertoire de sortie aller-retour avec ``mkdir -p build/roundtrip`` avant d'exécuter les conversions ; vous n'avez à le créer qu'une fois par espace de travail.
2. Lancez ``ddi roundtrip examples/Quality_of_Life.xml build/roundtrip/Quality_of_Life.xml`` pour resérialiser le document après analyse par le modèle.
3. Ajoutez des indicateurs comme ``--validate``, ``--no-pretty-print`` ou ``--no-declaration`` si vous avez besoin de contrôles de schéma ou d'ajuster le XML émis.
4. Comparez le XML régénéré à l'original pour vérifier la stabilité du convertisseur. Intégrez cette comparaison à vos contrôles de pull request.

## 4. Regrouper le workflow dans un script

1. Créez ``scripts/validate.sh`` avec le contenu suivant :

    ```bash
    #!/usr/bin/env bash
    set -euo pipefail

    INPUT=${1:-examples/Quality_of_Life.xml}
    REPORT_DIR=${2:-reports}

    mkdir -p "$REPORT_DIR" build/artifacts build/roundtrip

    ddi validate "$INPUT" > "$REPORT_DIR"/validation.json
    ddi to-json "$INPUT" --indent 2 \
      > build/artifacts/$(basename "$INPUT" .xml).json
    ROUNDTRIP_OUTPUT="build/roundtrip/$(basename "$INPUT")"
    ddi roundtrip "$INPUT" "$ROUNDTRIP_OUTPUT"
    ```

2. Rendez le script exécutable (``chmod +x scripts/validate.sh``).
3. Appelez le script dans votre configuration CI et comptez sur le code de sortie non nul pour échouer le pipeline si la validation ou la conversion rencontre une erreur.

## 5. Mettre en évidence les constats dans les tableaux de bord CI

- Relisez et expurgez ``reports/validation.json`` avant de le téléverser, puis
  partagez-le ainsi que ``build/artifacts`` comme artefacts de build pour que
  les parties prenantes puissent les consulter sans fouiller les logs.
- Analysez le rapport JSON (après avoir confirmé que tout contenu sensible a
  été retiré) pour commenter les pull requests ou annoter les commits en cas de
  violation.
- Planifiez l'exécution nocturne du script sur les instances de référence afin
  de détecter les dérives même en l'absence de changements de code, en veillant
  à diffuser des sorties dûment expurgées.

!!! caution "Données confidentielles"
    Anonymisez les identifiants ou restreignez l'accès aux artefacts générés
    lorsqu'ils contiennent des données confidentielles avant de les partager sur
    des tableaux de bord ou d'autres plateformes collaboratives.
