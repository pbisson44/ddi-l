# Benchmark de conversion de schémas

Cette page décrit un benchmark de référence pour convertir des définitions de schémas en objets ddi-l. Utilisez-le pour valider les changements de performance et pour éviter les régressions.

## Objectif du benchmark

- Mesurer le temps et la mémoire nécessaires pour analyser, valider et convertir les sources de schéma.
- Observer l'impact du cache, du streaming et des options de traitement en lot.

## Jeu de données

- Inclure un paquet de schémas DDI représentatif et un grand fichier XML d'exemple.
- Noter la taille des fichiers et toute simplification utilisée pour le run.

## Procédure

1. Préparer l'environnement avec une commande à vide pour charger les dépendances.
2. Exécuter la commande de conversion sur le jeu de données de référence.
3. Répéter au moins trois fois et retenir la médiane.
4. Comparer les résultats en activant ou désactivant les options clés (cache, parallélisme, réutilisation des schémas).

## Métriques à collecter

- Durée totale du pipeline de conversion.
- Pic de mémoire et empreinte stabilisée.
- Nombre d'avertissements ou d'erreurs de validation rencontrés.

## Modèle de compte rendu

Utilisez le canevas suivant pour enregistrer les résultats :

```markdown
### Environnement
- Matériel :
- Python :
- Dépendances :

### Jeu de données
- Paquet de schémas :
- Fichier d'instance :

### Résultats
- Durée médiane :
- Pic mémoire :
- Notes :
```

## Prochaines étapes

- Partager les conclusions dans le playbook de performance et mettre à jour les recommandations.
- Étendre le benchmark pour couvrir les nouvelles fonctionnalités de schéma au fur et à mesure.
