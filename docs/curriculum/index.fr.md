# Programme de formation

Bienvenue dans le programme de formation `ddi-l`. Ce cours vous apprend
à documenter des enquêtes, des recensements et des jeux de données avec
le standard DDI et Python. Aucune expérience avec DDI ou XML n'est requise.

!!! info "Ce que ce cours couvre"
    Vous apprendrez à transformer un fichier CSV ou Excel en un package DDI
    complet, avec des questions, des variables, des concepts, des listes
    de codes, des propriétés personnalisées, le versionnage et la validation.

## Organisation du cours

Le programme comprend **16 modules** en trois niveaux. Chaque module
s'appuie sur le précédent.

| # | Module | Durée | Prérequis |
| --- | -------- | ------- | ----------- |
| **Niveau 1 : Bases** | | | |
| 1 | [Qu'est-ce que les métadonnées ?](module-01-what-is-metadata.md) | 30 min | Aucun |
| 2 | [Préparez votre environnement](module-02-setup.md) | 20 min | Module 1 |
| 3 | [Créez votre première étude](module-03-first-study.md) | 30 min | Module 2 |
| 4 | [Variables et questions](module-04-variables.md) | 30 min | Module 3 |
| 5 | [Concepts et univers](module-05-concepts-universes.md) | 30 min | Module 4 |
| **Niveau 2 : Compétences pratiques** | | | |
| 6 | [Du CSV/Excel au DDI](module-06-csv-to-ddi.md) | 45 min | Module 5 |
| 7 | [Listes de codes](module-07-code-lists.md) | 40 min | Module 6 |
| 8 | [Flux de questionnaire](module-08-questionnaire-flows.md) | 50 min | Module 7 |
| 9 | [Traçabilité des données](module-09-data-lineage.md) | 60 min | Module 8 |
| 10 | [Couplage de données](module-10-data-linkage.md) | 60 min | Module 9 |
| 11 | [Propriétés, recherche et validation](module-11-properties-find-validate.md) | 40 min | Module 10 |
| 12 | [Champs personnalisés](module-12-custom-fields.md) | 45 min | Module 11 |
| 13 | [Mise à jour et versionnage](module-13-update-and-version.md) | 40 min | Module 12 |
| **Niveau 3 : Pratique appliquée** | | | |
| 14 | [Ouvrir et modifier des fichiers](module-14-open-modify.md) | 30 min | Module 13 |
| 15 | [Validation en ligne de commande](module-15-cli-validation.md) | 30 min | Module 14 |
| 16 | [Projets de synthèse](module-16-capstone.md) | 60-90 min | Tous |

## Par où commencer ?

Choisissez la ligne qui vous correspond le mieux.

| Je suis... | Commencer au | Je peux survoler |
| ------------ | -------------- | ------------------ |
| Étudiant universitaire (nouveau en données) | Module 1 | Rien |
| Chercheur (connaît Python, pas DDI) | Module 1 | Module 1 |
| Archiviste (connaît DDI, pas Python) | Module 1 | Modules 3-5 |
| Personnel d'un INS (connaît les deux) | Module 2 | Module 1 |

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
| Atelier d'une demi-journée | 1-6 | ~3 heures |
| Atelier d'une journée | 1-14 | ~6 heures |
| Formation intensive de deux jours | 1-16 | ~8 heures |
| Auto-formation | 1 par séance | 3 semaines |

## Ressources complémentaires

Ces guides existants approfondissent des sujets spécifiques :

- [Guide de l'utilisateur](../user-guide.md) : Référence complète de l'API CRUD
- [Guide de validation](../validation.md) : Détails sur le schéma et le linting
- [Recettes CLI](../cli-recipes.md) : Toutes les commandes CLI
- [Référence des modèles](../models.md) : Couche de modèles avancée
- [Tutoriels de création](../tutorials/authoring.md) : Tutoriels pas à pas
- [Guide de l'instructeur](instructor-guide.md) : Conseils d'animation
- [Aide-mémoire](cheat-sheet.md) : Référence rapide de toutes les APIs et imports
- [Corrigés](answer-keys.md) : Solutions et réponses aux quiz
