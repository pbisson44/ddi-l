---
description: >-
  L'API Python publique de ddi-l, générée à partir des docstrings :
  new_study, open_ddi, Document et la couche avancée.
---

# Référence de l'API

!!! note "Cette page est en anglais"
    La référence de l'API est générée à partir des docstrings du code source,
    qui sont rédigées en anglais ; elle n'est donc pas traduite.

    Le reste de la documentation (guides, tutoriels et les seize modules du
    programme de formation) est disponible en français.

    [Consulter la référence de l'API (en anglais) →](https://pbisson44.github.io/ddi-l/latest/api/){ .md-button .md-button--primary }

## Par où commencer

`new_study()` et `open_ddi()` renvoient un objet `Document`, qui est le point
d'entrée recommandé. `DDIDocument`, `DDIFragment` et `StudyCursor` constituent la
couche avancée sous-jacente : utilisez-les lorsque vous devez manipuler des
éléments XML bruts, des instances partielles, ou une étude précise dans un
fichier qui en contient plusieurs.

Pour une présentation guidée de la couche de modèles, voir la
[référence des modèles](models.md). Pour savoir ce qui est pris en charge et à
quel niveau, voir la [couverture du schéma](schema-coverage.md).
