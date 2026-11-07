---
title: Programme de formation
description: >-
  Un cours en 17 modules pour documenter enquêtes et jeux de données avec DDI
  et Python, de la première étude à un paquet validé et versionné.
---

# Programme de formation

Bienvenue dans le programme de formation `ddi-l`. Ce cours vous apprend
à documenter des enquêtes, des recensements et des jeux de données avec
le standard DDI et Python. Aucune expérience avec DDI ou XML n'est requise.

C'est ici que l'on apprend `ddi-l` pas à pas. Le
[guide d'utilisation](../user-guide.fr.md) est une référence d'une page de la
même API, et les [guides pratiques](../validation.fr.md) traitent chacun d'une
tâche, une fois les bases acquises.

!!! info "Ce que ce cours couvre"
    Vous apprendrez à transformer un fichier CSV ou Excel en un package DDI
    complet, avec des questions, des variables, des concepts, des listes
    de codes, des propriétés personnalisées, le versionnage et la validation.

## Organisation du cours

Le programme comprend **17 modules** en trois niveaux. Chaque module
indique ses prérequis en haut de page, et le tableau ci-dessous les reprend :
la plupart des modules ne demandent que le précédent, mais certains en
demandent davantage. Vous vérifiez votre travail dès le module 3 et, à la fin
du niveau 1, vous savez ouvrir, modifier et valider n'importe quel fichier
DDI.

Les durées sont celles que donne chaque module : en autonomie, ou en classe
avec un instructeur.

| # | Module | En autonomie | Avec instructeur | Prérequis |
| --- | -------- | ------- | ------- | ----------- |
| **Niveau 1 : Bases** | | | | |
| 1 | [Qu'est-ce que les métadonnées ?](module-01-what-is-metadata.fr.md) | 30 min | 45 min | Aucun |
| 2 | [Préparez votre environnement](module-02-setup.fr.md) | 20 min | 30 min | Module 1 |
| 3 | [Créez votre première étude](module-03-first-study.fr.md) | 30 min | 45 min | Module 2 |
| 4 | [Variables et questions](module-04-variables.fr.md) | 30 min | 40 min | Module 3 |
| 5 | [Concepts et univers](module-05-concepts-universes.fr.md) | 30 min | 40 min | Module 4 |
| 6 | [Ouvrir et modifier des fichiers](module-06-open-modify.fr.md) | 30 min | 40 min | Module 5 |
| 7 | [Valider depuis la ligne de commande](module-07-cli-validation.fr.md) | 30 min | 40 min | Module 6 |
| **Niveau 2 : Compétences pratiques** | | | | |
| 8 | [Du CSV/Excel au DDI](module-08-csv-to-ddi.fr.md) | 45 min | 60 min | Module 7 |
| 9 | [Listes de codes](module-09-code-lists.fr.md) | 40 min | 50 min | Module 8 |
| 10 | [Flux de questionnaire](module-10-questionnaire-flows.fr.md) | 50 min | 60 min | Module 9 |
| 11 | [Traçabilité des données](module-11-data-lineage.fr.md) | 60 min | 75 min | Module 10 |
| 12 | [Couplage de données](module-12-data-linkage.fr.md) | 60 min | 75 min | Module 11 |
| 13 | [Propriétés, recherche et validation](module-13-properties-find-validate.fr.md) | 40 min | 50 min | Module 12 |
| 14 | [Champs personnalisés](module-14-custom-fields.fr.md) | 45 min | 55 min | Module 13 |
| 15 | [Mise à jour et versionnage](module-15-update-and-version.fr.md) | 65 min | 75 min | Module 14 |
| **Niveau 3 : Pratique appliquée** | | | | |
| 16 | [Spécification avancée de questionnaires](module-16-advanced-questionnaire-spec.fr.md) | 75 min | 90 min | Modules 7, 10 et 15 |
| 17 | [Projets de synthèse](module-17-capstone.fr.md) | 60-90 min | 90 min | Tous (1 à 16) |

Chaque module commence par des **objectifs d'apprentissage** numérotés (O1,
O2, ...) : ce que vous saurez faire à la fin, comme écrire un script ou
valider un fichier. Chaque exercice et chaque question de quiz porte les
objectifs qu'il met en pratique, par exemple **Exercice 2 (O3)**. Chaque
module se termine par une liste **Faites le point**, une ligne par objectif.
Cochez chaque ligne avant de passer à la suite ; pour une ligne que vous ne
pouvez pas cocher, refaites les exercices qui portent cet objectif.

## Par où commencer ?

Choisissez la ligne qui vous correspond le mieux.

| Je suis... | Commencer au | Je peux survoler | Prendre plus de temps sur |
| ------------ | -------------- | ------------------ | ------------------------- |
| Étudiant universitaire (nouveau en données) | Module 1 | Rien | Modules 3-5 |
| Chercheur (connaît Python, pas DDI) | Module 1 | Module 2 | Modules 1, 4 et 5 : le vocabulaire du DDI |
| Archiviste (connaît DDI, pas Python) | Module 1 | Module 1 | Modules 2-7 : le Python dont vous avez besoin |
| Personnel d'un INS (connaît les deux) | Module 2 | Modules 1 et 3 | Modules 8-16 |
| Développeur qui automatise les contrôles DDI | Module 2 | Modules 1, 4 et 5 | Modules 3 et 7, puis le parcours automatisation ci-dessous |

### Parcours automatisation

Pour les équipes qui ajoutent la validation DDI à leurs pipelines ou qui
construisent des services sur `ddi-l`. Suivez les modules 2, 3 et 7, puis ces
guides dans l'ordre :

| Séance | Objectif | Pages |
| ------ | -------- | ----- |
| Bases du pipeline (45 min) | Exécuter et configurer la validation et le lint | [Valider et analyser le contenu DDI](../validation.fr.md), [Recettes CLI](../cli-recipes.fr.md) |
| Automatisation (45 min) | Scripter la CLI, conserver les rapports, faire échouer la CI en cas d'erreur | [Carnet d'automatisation en ligne de commande](../tutorials/automation-playbook.fr.md), [Clinique de dépannage des schémas](../tutorials/schema-troubleshooting-clinic.fr.md) |
| Réutilisation et intégration (45 min) | Partager des fragments, appeler `ddi-l` depuis d'autres systèmes | [Atelier de réutilisation de fragments](../tutorials/fragment-reuse-lab.fr.md), [API HTTP](../server.fr.md), [Construire des outils et applications](../tutorials/building-tools.fr.md) |

Consultez le [playbook de performance](../performance.fr.md) avant de planifier
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

Chaque total additionne les durées des modules eux-mêmes, sans pauses ni
installation.

| Format | Modules | Avec instructeur | En autonomie |
| -------- | --------- | -------------- | -------------- |
| Atelier d'une demi-journée | 1-5 | 3 h 20 min | 2 h 20 min |
| Atelier d'une journée | 1-9 | 6 h 30 min | 4 h 45 min |
| Formation intensive de trois jours | 1-17 | 16 h (environ 5 h 20 min par jour) | 12 h 20 min à 12 h 50 min |
| Auto-formation | Un module par séance | Sans objet | 12 h 20 min à 12 h 50 min en 17 séances : 3 à 4 semaines à raison d'une séance par jour ouvrable |

Pour terminer le niveau 1 en atelier, ajoutez les modules 6 et 7 à la
demi-journée (1 h 20 min de plus, 4 h 40 min au total) : c'est alors une
courte journée plutôt qu'une demi-journée.

## Ressources complémentaires

- [Guide de l'instructeur](instructor-guide.fr.md) : Conseils d'animation
- [Aide-mémoire](cheat-sheet.fr.md) : Référence rapide de toutes les APIs et imports
- [Corrigés](answer-keys.fr.md) : Toutes les solutions sur une page, pour les
  instructeurs. Les apprenants peuvent plutôt ouvrir la réponse sous chaque
  exercice.
- [Guide d'utilisation](../user-guide.fr.md) : L'API `Document` sur une page
- [Guide de validation](../validation.fr.md) : Détails sur le schéma et le linting
- [Recettes CLI](../cli-recipes.fr.md) : Toutes les commandes CLI
- [Référence des modèles](../models.fr.md) : Couche de modèles avancée
