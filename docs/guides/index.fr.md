---
description: >-
  Guides pratiques de ddi-l : valider et analyser du DDI, charger des
  métadonnées depuis des tableurs, échanger des fichiers avec d'autres outils,
  et utiliser ddi-l en ligne de commande, par HTTP ou depuis R.
icon: material/compass-outline
---

# Guides pratiques

Chaque guide montre comment accomplir une tâche, pour qui connaît déjà les
bases. Vous découvrez `ddi-l` ? Commencez par le
[cours](../curriculum/index.fr.md) ; vous cherchez une fonction ? Voyez la
[référence](../reference/index.fr.md).

## Vérifier vos métadonnées

<div class="grid cards" markdown>

- :material-check-decagram-outline:{ .lg } **[Valider et analyser](../validation.fr.md)**

    ---

    Vérifier des documents selon les schémas DDI 3.1, 3.2 et 3.3, exécuter
    les règles lint et lire les résultats en Python ou en ligne de commande.

- :material-bug-outline:{ .lg } **[Dépanner les erreurs de schéma](../tutorials/schema-troubleshooting-clinic.fr.md)**

    ---

    Lire une erreur de schéma, trouver l'élément qu'elle nomme et le
    corriger, à partir de fichiers volontairement erronés.

- :material-clipboard-check-outline:{ .lg } **[Vérifier un questionnaire par rapport à une spécification](../spec-conformance.fr.md)**

    ---

    Écrire ce qu'un questionnaire doit contenir dans une spécification, puis
    vérifier un instrument avec `ddi conform`.

- :material-robot-outline:{ .lg } **[Automatiser la validation en CI](../tutorials/automation-playbook.fr.md)**

    ---

    Faire échouer un pipeline sur du DDI invalide, garder des rapports JSON
    et regrouper les vérifications dans un script.

</div>

## Faire entrer et sortir les métadonnées

<div class="grid cards" markdown>

- :material-table-arrow-right:{ .lg } **[Charger du DDI depuis des tableurs](../spreadsheet-import.fr.md)**

    ---

    Documenter une étude dans des fichiers CSV ou un classeur Excel, puis la
    charger en DDI d'un coup.

- :material-file-download-outline:{ .lg } **[Modèles de tableurs](../spreadsheet-templates.fr.md)**

    ---

    Des modèles vierges et d'exemple, bilingues, prêts à remplir.

- :material-swap-horizontal:{ .lg } **[Travailler avec d'autres outils](../interoperability.fr.md)**

    ---

    Échanger des métadonnées avec des outils XML, des données liées, du
    JSON, R, des fichiers DDI-Codebook et des outils DDI 3.2.

- :material-file-replace-outline:{ .lg } **[Travailler avec les exports Colectica](../colectica.fr.md)**

    ---

    Lire, modifier et écrire des exports `FragmentInstance`, réécrits octet
    pour octet dans leur propre disposition.

- :material-code-tags:{ .lg } **[Passer du XML aux objets](../tutorials/xml-to-objects.fr.md)**

    ---

    Ouvrir du XML DDI brut, l'explorer et travailler avec la couche de
    modèles typés.

- :material-puzzle-outline:{ .lg } **[Réutiliser des fragments](../tutorials/fragment-reuse-lab.fr.md)**

    ---

    Emballer des fragments réutilisables, les partager et les rattacher à
    de nouveaux documents.

</div>

## Utiliser ddi-l ailleurs

<div class="grid cards" markdown>

- :material-console:{ .lg } **[Utiliser la ligne de commande](../cli-recipes.fr.md)**

    ---

    Des recettes pour la commande `ddi` : valider, analyser, convertir en
    JSON et en JSON-LD, et faire l'aller-retour du XML DDI.

- :material-web:{ .lg } **[Servir l'API HTTP](../server.fr.md)**

    ---

    Valider, analyser et convertir des documents par HTTP avec `ddi serve`,
    depuis n'importe quel langage.

- :material-language-r:{ .lg } **[Utiliser ddi-l depuis R](../r-users.fr.md)**

    ---

    Créer, ouvrir, valider et analyser des documents DDI sans quitter R.

- :material-hammer-wrench:{ .lg } **[Construire des outils et applications](../tutorials/building-tools.fr.md)**

    ---

    Bâtir sur `ddi-l` des tableaux de bord, des services web, des outils en
    ligne de commande et des pipelines de données.

</div>
