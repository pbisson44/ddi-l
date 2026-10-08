---
description: >-
  Paquets Python utiles à côté de ddi-l pour analyser, valider, transformer
  et publier du contenu DDI Lifecycle.
---

# Paquets Python associés

Des paquets utiles à côté de `ddi-l` pour lire, valider ou transformer du
contenu DDI Lifecycle (DDI-L). À part les dépendances que `ddi-l` installe
déjà, aucun n'est requis.

## Analyse et validation XML

- **`xmlschema`** : valide les documents par rapport aux schémas DDI fournis.
  C'est une dépendance de `ddi-l` ; il est donc toujours installé.
- **`lxml`** : un analyseur et sérialiseur XML plus rapide. Installez-le avec
  `pip install 'ddi-l[full]'` ; `ddi-l` l'utilise automatiquement lorsqu'il
  est présent, et utilise la bibliothèque standard sinon.

## Traitement des données

- **`pandas`** : transformer des variables, des questions ou des listes de
  codes en tableaux pour des rapports et des contrôles.
- **`polars`** : une solution plus rapide que pandas pour les gros documents
  ou les nombreux fichiers.
- **`pyarrow`** : écrire des fichiers Parquet ou Feather, ou passer des data
  frames entre pandas et polars.

## Fichiers, HTTP et outils en ligne de commande

- **`requests` ou `httpx`** : télécharger des instances DDI, des schémas ou
  des vocabulaires contrôlés avant de les valider.
- **`typer` ou `click`** : construire vos propres outils en ligne de commande
  au-dessus de `ddi-l`.
- **`fsspec`** : lire et écrire des fichiers sur disque local, sur un stockage
  compatible S3 ou sur d'autres systèmes de fichiers distants avec le même
  code.

## Tests

- **`pytest`** : l'outil de test utilisé par ce dépôt.
- **`hypothesis`** : des tests basés sur les propriétés pour les règles de
  validation ou le code de conversion.
- **`ruff`** : lint et formatage.

## Gestion des dépendances

- **`uv`** : ce dépôt utilise uv et son fichier `uv.lock`. Exécutez
  `uv sync --group dev` pour obtenir les mêmes outils de développement que la
  CI.

## Choisir des paquets

- Épinglez les dépendances optionnelles dans un fichier de verrouillage, et
  utilisez le même fichier en déploiement, pour qu'un pipeline se comporte de
  la même façon partout.
- Validez aux frontières de chaque étape du pipeline (`doc.validate()`, ou
  `ddi validate` en ligne de commande) pour qu'un fichier mal formé soit
  détecté là où il entre, et non plusieurs étapes plus loin.
