---
title: Programme de formation
description: >-
  Un cours en 16 modules pour documenter enquêtes et jeux de données avec DDI
  et Python, de la première étude à un paquet validé et versionné.
---

# Programme de formation

Bienvenue dans le programme de formation `ddi-l`. Ce cours vous apprend
à documenter des enquêtes, des recensements et des jeux de données avec
le standard DDI et Python. Aucune expérience avec DDI ou XML n'est requise.

C'est ici que l'on apprend `ddi-l` pas à pas. Le
[guide d'utilisation](../user-guide.md) est une référence d'une page de la
même API, et les [guides pratiques](../validation.md) traitent chacun d'une
tâche, une fois les bases acquises.

!!! info "Ce que ce cours couvre"
    Vous apprendrez à transformer un fichier CSV ou Excel en un package DDI
    complet, avec des questions, des variables, des concepts, des listes
    de codes, des propriétés personnalisées, le versionnage et la validation.

## Organisation du cours

Le programme comprend **16 modules** en trois niveaux. Chaque module
s'appuie sur le précédent. Vous vérifiez votre travail dès le module 3 et, à
la fin du niveau 1, vous savez ouvrir, modifier et valider n'importe quel
fichier DDI.

| # | Module | Durée | Prérequis |
| --- | -------- | ------- | ----------- |
| **Niveau 1 : Bases** | | | |
| 1 | [Qu'est-ce que les métadonnées ?](module-01-what-is-metadata.md) | 30 min | Aucun |
| 2 | [Préparez votre environnement](module-02-setup.md) | 20 min | Module 1 |
| 3 | [Créez votre première étude](module-03-first-study.md) | 30 min | Module 2 |
| 4 | [Variables et questions](module-04-variables.md) | 30 min | Module 3 |
| 5 | [Concepts et univers](module-05-concepts-universes.md) | 30 min | Module 4 |
| 6 | [Ouvrir et modifier des fichiers](module-06-open-modify.md) | 30 min | Module 5 |
| 7 | [Valider depuis la ligne de commande](module-07-cli-validation.md) | 30 min | Module 6 |
| **Niveau 2 : Compétences pratiques** | | | |
| 8 | [Du CSV/Excel au DDI](module-08-csv-to-ddi.md) | 45 min | Module 7 |
| 9 | [Listes de codes](module-09-code-lists.md) | 40 min | Module 8 |
| 10 | [Flux de questionnaire](module-10-questionnaire-flows.md) | 50 min | Module 9 |
| 11 | [Traçabilité des données](module-11-data-lineage.md) | 60 min | Module 10 |
| 12 | [Couplage de données](module-12-data-linkage.md) | 60 min | Module 11 |
| 13 | [Propriétés, recherche et validation](module-13-properties-find-validate.md) | 40 min | Module 12 |
| 14 | [Champs personnalisés](module-14-custom-fields.md) | 45 min | Module 13 |
| 15 | [Mise à jour et versionnage](module-15-update-and-version.md) | 40 min | Module 14 |
| **Niveau 3 : Pratique appliquée** | | | |
| 16 | [Projets de synthèse](module-16-capstone.md) | 60-90 min | Tous |

## Par où commencer ?

Choisissez la ligne qui vous correspond le mieux.

| Je suis... | Commencer au | Je peux survoler | Prendre plus de temps sur |
| ------------ | -------------- | ------------------ | ------------------------- |
| Étudiant universitaire (nouveau en données) | Module 1 | Rien | Modules 3-5 |
| Chercheur (connaît Python, pas DDI) | Module 1 | Module 2 | Modules 1, 4 et 5 : le vocabulaire du DDI |
| Archiviste (connaît DDI, pas Python) | Module 1 | Module 1 | Modules 2-7 : le Python dont vous avez besoin |
| Personnel d'un INS (connaît les deux) | Module 2 | Modules 1 et 3 | Modules 8-15 |
| Développeur qui automatise les contrôles DDI | Module 2 | Modules 1, 4 et 5 | Modules 3 et 7, puis le parcours automatisation ci-dessous |

### Parcours automatisation

Pour les équipes qui ajoutent la validation DDI à leurs pipelines ou qui
construisent des services sur `ddi-l`. Suivez les modules 2, 3 et 7, puis ces
guides dans l'ordre :

| Séance | Objectif | Pages |
| ------ | -------- | ----- |
| Bases du pipeline (45 min) | Exécuter et configurer la validation et le lint | [Valider et analyser le contenu DDI](../validation.md), [Recettes CLI](../cli-recipes.md) |
| Automatisation (45 min) | Scripter la CLI, conserver les rapports, faire échouer la CI en cas d'erreur | [Carnet d'automatisation en ligne de commande](../tutorials/automation-playbook.md), [Clinique de dépannage des schémas](../tutorials/schema-troubleshooting-clinic.md) |
| Réutilisation et intégration (45 min) | Partager des fragments, appeler `ddi-l` depuis d'autres systèmes | [Atelier de réutilisation de fragments](../tutorials/fragment-reuse-lab.md), [API HTTP](../server.md), [Construire des outils et applications](../tutorials/building-tools.md) |

Consultez le [playbook de performance](../performance.md) avant de planifier
de gros traitements par lots.

## Vue d'ensemble

Voici le processus que vous allez apprendre :

```text
CSV / Excel / SQL table
        ↓
  Python script (ddi-l)
        ↓
  DDI XML document
        ↓
  Validate & version
        ↓
  Archive or publish
```

## Calendriers suggérés

| Format | Modules | Durée totale |
| -------- | --------- | -------------- |
| Atelier d'une demi-journée | 1-7 | ~3,5 heures |
| Atelier d'une journée | 1-10 | ~6 heures |
| Formation intensive de deux jours | 1-16 | ~11 heures |
| Auto-formation | 1 par séance | 3 semaines |

## Ressources complémentaires

- [Guide de l'instructeur](instructor-guide.md) : Conseils d'animation
- [Aide-mémoire](cheat-sheet.md) : Référence rapide de toutes les APIs et imports
- [Corrigés](answer-keys.md) : Toutes les solutions sur une page, pour les
  instructeurs. Les apprenants peuvent plutôt ouvrir la réponse sous chaque
  exercice.
- [Guide d'utilisation](../user-guide.md) : L'API `Document` sur une page
- [Guide de validation](../validation.md) : Détails sur le schéma et le linting
- [Recettes CLI](../cli-recipes.md) : Toutes les commandes CLI
- [Référence des modèles](../models.md) : Couche de modèles avancée
