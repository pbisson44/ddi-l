---
title: ddi-l
description: >-
  ddi-l est une bibliothèque Python et une CLI pour créer, lire, valider et
  analyser du XML DDI Lifecycle 3.1, 3.2 et 3.3, avec un cours bilingue.
template: home.html
hide:
  - navigation
  - toc
hero:
  eyebrow: DDI Lifecycle 3.1, 3.2 et 3.3
  title: Documenter enquêtes et jeux de données avec le DDI, en Python
  lead: >-
    Manipulez les études, les questions et les variables comme des objets
    Python. ddi-l écrit le XML, le valide selon les schémas DDI et l'analyse
    pour trouver ce que les schémas laissent passer.
  primary:
    text: Commencer le cours
    link: curriculum/
  secondary:
    text: Installer
    link: installation/
  facts:
    - Python 3.11+
    - Licence MIT
    - Français et anglais
  terminal:
    label: Installer ddi-l et valider un fichier
    copy: pip install ddi-l
    lines:
      - cmd: pip install ddi-l
      - cmd: ddi validate enquete-menages.xml
      - out: Document is valid.
---

## Pourquoi ddi-l

Le [DDI](https://ddialliance.org/) (Data Documentation Initiative) est la
norme internationale qu'utilisent les organismes statistiques, les archives de
données et les chercheurs pour décrire les enquêtes et les jeux de données : ce
qui a été demandé, ce que signifie chaque variable et qui a été interrogé.
Écrite en XML, cette documentation est très imbriquée et pleine de renvois.
`ddi-l` vous permet de la rédiger et de la vérifier en Python plutôt que
d'éditer le XML à la main.

<div class="grid cards ddi-features" markdown>

- :material-language-python:{ .lg } **Écrire du DDI en Python**

    ---

    Créez des études, des questions, des variables et des listes de codes
    comme des objets Python. `ddi-l` écrit le XML DDI 3.3 et chaque renvoi
    entre les éléments.

- :material-check-decagram-outline:{ .lg } **Valider toute version 3.x**

    ---

    Vérifiez des fichiers
    [DDI Lifecycle](https://ddialliance.org/Specification/DDI-Lifecycle/)
    3.1, 3.2 et 3.3 selon les schémas officiels, pour contrôler les fonds
    plus anciens avec le même outil.

- :material-format-list-checks:{ .lg } **Analyser ce que les schémas laissent passer**

    ---

    Repérez les éléments sans libellé, les renvois vers des éléments
    inexistants, les traductions manquantes et les conditions qui ne
    peuvent jamais être vraies.

- :material-table-arrow-right:{ .lg } **Partir d'un tableur**

    ---

    Décrivez une étude dans des fichiers CSV ou un classeur Excel, puis
    chargez-la en DDI d'un coup.

- :material-swap-horizontal:{ .lg } **Travailler avec d'autres outils**

    ---

    Exportez du JSON-LD pour les données liées, modifiez des exports
    Colectica, faites entrer des fichiers DDI-Codebook, et faites tout cela
    depuis R ou par HTTP.

- :material-school-outline:{ .lg } **Apprendre en pratiquant**

    ---

    Un cours gratuit en français et en anglais, de « qu'est-ce que les
    métadonnées ? » à un paquet DDI validé et versionné. Aucune expérience
    du DDI ni du XML n'est requise.

</div>

## Démarrage rapide

Installez `ddi-l` depuis PyPI. L'extra `full` ajoute le moteur `lxml`, plus
rapide (voir [Installation](installation.fr.md)).

=== "pip"
    ```bash
    pip install ddi-l
    ```

=== "uv"
    ```bash
    uv add ddi-l
    uv run ddi --help
    ```

=== "Poetry"
    ```bash
    poetry add ddi-l
    poetry run ddi --help
    ```

Créez une étude, ajoutez une question et la variable qui enregistre sa
réponse, puis enregistrez-la :

```python
import ddi_l as ddi

# Créer une nouvelle étude
doc = ddi.new_study(title="Enquête ménages", agency="example.org")

# Ajouter une question et la variable qui enregistre sa réponse. `label=` est
# facultatif, mais `ddi lint` signale chaque élément qui n'en a pas.
q_age = doc.add_question(text="Quel âge avez-vous ?", label="Question sur l'âge")
doc.add_variable(name="Age", question=q_age, label="Âge en années")

# Enregistrer en XML
doc.save("enquete-menages.xml")
```

Rouvrez-la plus tard :

```python
# Ouvrir une étude existante
doc = ddi.open_ddi("enquete-menages.xml")

for v in doc.variables:
    print(v.identifier)
```

Vérifiez le fichier en ligne de commande. Les deux commandes se terminent avec
le code 0 quand le fichier est propre, ce qui permet de les utiliser dans des
scripts et en CI :

```bash
ddi validate enquete-menages.xml
ddi lint enquete-menages.xml
```

Le [guide d'utilisation](user-guide.fr.md#comment-sarticule-une-etude)
montre comment s'articulent les parties d'une étude et fait le tour de
l'API `Document`.

## Trouver votre chemin

<div class="grid cards ddi-paths" markdown>

- :material-school-outline:{ .lg } **Vous découvrez le DDI ?**

    ---

    Suivez le [cours](curriculum/index.fr.md) : 17 modules, puis des
    modules facultatifs sur les filtres de questionnaire, l'API HTTP,
    DDI-Codebook et DDI-CDI.

- :material-compass-outline:{ .lg } **Une tâche à accomplir ?**

    ---

    Les [guides pratiques](guides/index.fr.md) couvrent la validation, les
    tableurs, les autres outils, la ligne de commande, R et HTTP.

- :material-book-open-page-variant-outline:{ .lg } **Une information à vérifier ?**

    ---

    La [référence](reference/index.fr.md) réunit le guide d'utilisation,
    les références de l'API et des modèles, et chaque règle lint.

- :material-source-pull:{ .lg } **Envie de contribuer ?**

    ---

    Commencez par le
    [guide des contributeurs](https://github.com/pbisson44/ddi-l/blob/main/CONTRIBUTING.md),
    puis le [guide de développement](DEVELOPMENT.fr.md).

</div>

## Citer ddi-l

Si vous utilisez `ddi-l` dans une recherche ou dans le flux de travail d'une
archive, merci de le citer :

> Bisson, P. (2026). *ddi-l: a Python toolkit for DDI Lifecycle 3.3 XML
> documents* (Version 0.2.1) [Logiciel].
> <https://github.com/pbisson44/ddi-l>

```bibtex
@software{bisson_ddi_l,
  author  = {Bisson, Philippe},
  title   = {ddi-l: a Python toolkit for DDI Lifecycle 3.3 XML documents},
  year    = {2026},
  version = {0.2.1},
  url     = {https://github.com/pbisson44/ddi-l},
  license = {MIT}
}
```

Le fichier
[`CITATION.cff`](https://github.com/pbisson44/ddi-l/blob/main/CITATION.cff)
du dépôt contient les mêmes métadonnées ; le bouton « Cite this repository »
de GitHub les exporte dans d'autres formats.
