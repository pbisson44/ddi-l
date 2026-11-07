---
description: >-
  Installer ddi-l depuis PyPI avec pip, uv ou Poetry, choisir les extras
  utiles, ou préparer un environnement de développement.
---

# Installation

`ddi-l` nécessite **Python 3.11 ou plus récent** et est disponible sur PyPI.

## Installer depuis PyPI

Utilisez cette méthode, sauf si vous voulez modifier `ddi-l` lui-même.

=== "pip"
    ```bash
    pip install ddi-l
    ddi --help
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

!!! tip "Vérifier l'installation"
    - `ddi --help` confirme que le point d'entrée CLI est disponible.
    - `python -c "import ddi_l; print(ddi_l.__version__)"` affiche la
      version installée.

### Ce que donne `pip install ddi-l`

`pip install ddi-l` lit, écrit, valide et analyse les documents DDI sans rien
d'autre. Il apporte le noyau XML natif, le paquet `ddi-l-native` de même
version, partout où une wheel compilée existe : Linux (x86_64 et aarch64),
macOS et Windows (x64), avec CPython 3.11 et plus. Ailleurs, pip installe un
remplaçant en Python pur du même nom, et `ddi-l` fonctionne de la même façon,
plus lentement. pip ne compile jamais rien.

### Extras : quand en prendre un

Un extra ajoute une fonction ou un moteur dont la plupart des gens n'ont pas
besoin. Installez-en un quand votre travail correspond à sa colonne « À
installer quand » ; combinez-les ainsi : `pip install 'ddi-l[spec,logic]'`.

| Extra | À installer quand | Ce qu'il ajoute |
| --- | --- | --- |
| `spec` | Vous vérifiez des questionnaires par rapport à une spécification : `ddi spec`, `ddi conform`, ou une spécification YAML ou JSON lue en Python. | PyYAML et jsonschema ; voir [Vérifier un questionnaire par rapport à une spécification](spec-conformance.fr.md). Sans lui, `ddi spec` et `ddi conform` disent quoi installer. |
| `logic` | Vous voulez comparer les filtres exactement : `equivalent()` et `ddi conform` décident alors si deux filtres valent pour les mêmes répondants et nomment un répondant qui les distingue, et l'analyse signale les éléments qu'aucun répondant n'atteint. | Le solveur Z3 (MIT, environ 57 Mo installé) ; voir [Vérifier un questionnaire par rapport à une spécification](spec-conformance.fr.md). Sans lui, les filtres sont comparés tels qu'écrits. |
| `server` | Vous lancez l'API HTTP, `ddi serve`. | Litestar et uvicorn ; voir [API HTTP](server.fr.md). Sans lui, `ddi serve` dit quoi installer. |
| `full` | Votre plateforme n'a pas de noyau natif compilé (Alpine Linux, Windows sur ARM, PyPy, Python sans GIL), ou vous écrivez surtout de nouveaux documents mis en page à neuf (`layout="default"`), que lxml écrit plus vite. | lxml, utilisé quand le noyau natif n'est pas là ; `DDI_L_XML_BACKEND=lxml` le choisit quand même. |

### Moteurs XML

`ddi-l` lit et écrit le XML avec le premier de ces moteurs qui est installé :

1. `native`, de `ddi-l-native` là où une wheel compilée existe ;
2. `lxml`, de l'extra `full` ;
3. la bibliothèque standard, toujours présente.

Tous donnent les mêmes documents, les mêmes problèmes de validation et les
mêmes constats d'analyse. La variable d'environnement `DDI_L_XML_BACKEND`
(`native`, `lxml` ou `stdlib`) en choisit un ; elle est lue une fois, à
l'import de `ddi_l`. `ddi_l._etree.BACKEND` nomme le moteur utilisé.

Le moteur `native` valide aussi contre le schéma en une passe ; voir
[le déroulement de la validation](validation.fr.md#deroulement-de-la-validation-par-schema).
Un document mis en page à neuf (un nouveau document, ou `layout="default"`)
est écrit par du code Python avec les moteurs `native` et bibliothèque
standard, plus lentement qu'avec lxml.

!!! info "Les schémas sont déjà inclus"
    Les schémas XML DDI 3.1, 3.2 et 3.3 sont livres dans le paquet :
    `doc.validate()` et `ddi validate` fonctionnent hors ligne, sans
    téléchargement supplémentaire ni accès réseau.

## Installer depuis les sources

Les développeurs contribuant à `ddi-l` devraient installer depuis un clone local :

```bash
git clone https://github.com/pbisson44/ddi-l.git
cd ddi-l
pip install -e . ./native/fallback
```

`./native/fallback` est le remplaçant en Python pur de `ddi-l-native`. pip ne
lit pas `uv.lock`, et une version de `ddi-l` pas encore publiée n'a pas de
`ddi-l-native` à installer depuis PyPI.

Installer les outils de développement. Le projet est géré avec
[uv](https://docs.astral.sh/uv/), et `uv.lock` épingle chaque version de
dépendance :

```bash
uv sync --group dev              # Dépendances d'exécution et de développement
uv sync --group dev --extra full # ...plus le backend lxml optionnel
```

Notez que `full` est un **extra**, pas un groupe de dépendances :
`--group full` échoue. Dans un clone, `ddi-l-native` est son remplaçant en
Python pur (`native/fallback/`) : personne n'a besoin de Rust. Pour utiliser le
noyau natif, construisez-le par-dessus le remplaçant ; il faut une chaîne
d'outils Rust ([rustup](https://rustup.rs/)) et, sous Windows, les Build Tools
de Visual Studio avec la charge de travail C++. `uv sync` et `uv run` remettent
le remplaçant : lancez les commandes avec `uv run --no-sync` :

```bash
uv pip install --reinstall-package ddi-l-native ./native
uv run --no-sync python -c "import ddi_l._etree as e; print(e.BACKEND)"  # native
```

Avec pip à la place (pip 25.1 ou plus récent lit les groupes de dépendances) :

```bash
pip install -e '.[full]' ./native/fallback --group dev
```

Pour le travail sur la documentation (`docs` est un groupe de dépendances, pas
un extra) :

```bash
uv sync --group docs
# ou
pip install -e . ./native/fallback --group docs
```

## Vérifier avec un test rapide

```python
import ddi_l as ddi

doc = ddi.new_study(title="Test", agency="example.org")
doc.add_question(text="Est-ce que ca marche ?")
print(f"Questions : {len(doc.questions)}")  # -> 1
```

Pour plus de détails, consultez le [guide d'utilisation](user-guide.fr.md) ou le
[guide de développement](DEVELOPMENT.fr.md).
