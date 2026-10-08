# Parcours d'apprentissage par persona

Deux plans d'atelier proposés : l'un pour les personnes qui découvrent DDI,
l'autre pour les équipes qui automatisent la validation. Chaque plan indique
les séances, les pages à utiliser et des extensions facultatives.

## Nouveaux intégrateurs

!!! info "Public"
    Ingénieurs ou analystes adoptant DDI pour la première fois qui ont besoin de
    créer des études, ajouter du contenu et valider des documents.

### Objectifs d'apprentissage

- Installer la boîte à outils et créer une étude avec `ddi.new_study()`.
- Ajouter des questions, variables, concepts et univers avec l'API CRUD.
- Valider des documents et naviguer dans la CLI.

### Séquence recommandée

| Session | Focus | Ressources | Points de contrôle |
| ------- | ----- | ---------- | ------------------ |
| Lancement (30 min) | Installation et première étude | [Installation](../installation.md), [Guide d'utilisation](../user-guide.md) | Les apprenants peuvent créer une étude et la sauvegarder en XML. |
| Rédaction guidée (45 min) | Construire une étude complète | [Workflows d'auteur](authoring.md), Atelier 1 des [exercices](training-labs.md) | Les équipes peuvent créer une étude avec des questions et variables liées. |
| Pratique CLI (30 min) | Valider et convertir depuis le terminal | [Recettes CLI](../cli-recipes.md), Atelier 3 des [exercices](training-labs.md) | Les participants peuvent exécuter `ddi validate` et interpréter la sortie. |

## Équipes d'automatisation avancées

!!! info "Public"
    Équipes de plateforme intégrant la validation DDI dans des pipelines CI/CD.

### Objectifs d'apprentissage

- Personnaliser les profils lint.
- Automatiser la validation dans l'intégration continue.
- Collecter des résultats structures pour d'autres systèmes.

### Séquence recommandée

| Session | Focus | Ressources | Points de contrôle |
| ------- | ----- | ---------- | ------------------ |
| Fondations pipeline (45 min) | Validation personnalisée | [Validation](../validation.md), Atelier 2 des [exercices](training-labs.md) | Les équipes peuvent valider des documents par programme et via la CLI. |
| Automatisation (30 min) | Fragments réutilisables | [Workflows d'auteur](authoring.md), [Lab fragments](fragment-reuse-lab.md) | Les apprenants peuvent créer et valider des documents DDI. |
| Intégration service (45 min) | Résultats pour outils en aval | [Playbook automation](automation-playbook.md), [Outils](building-tools.md) | Les participants peuvent valider en lot et capturer les résultats structures. |

## Conseils d'animation

- Commencez chaque séance en rappelant ce que le groupe doit savoir faire à la fin.
- Capturez les artefacts (transcriptions, sortie JSON) pour les réutiliser
  comme références d'intégration.
- Demandez un retour après la dernière séance ; les apprenants peuvent utiliser le
  modèle de ticket « Learner feedback ».
