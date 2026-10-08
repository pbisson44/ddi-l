# Installation

`ddi-l` nécessite **Python 3.11 ou plus récent** et est disponible sur PyPI.

## Installer depuis PyPI

Utilisez cette méthode, sauf si vous voulez modifier `ddi-l` lui-même.

=== "pip"
    ```bash
    pip install ddi-l
    ddi --help
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

### Dépendances optionnelles

| Besoin | Commande | Ce que cela apporte |
| --- | --- | --- |
| Analyse XML accélérée | `pip install 'ddi-l[full]'` | Active le moteur `lxml` : analyse plus rapide et validation quasi instantanée des documents valides. |
| API HTTP | `pip install 'ddi-l[server]'` | Ajoute le service Litestar de `ddi serve` ; voir [API HTTP](server.md). |

!!! info "Les schémas sont déjà inclus"
    Les schémas XML DDI 3.1, 3.2 et 3.3 sont livres dans le paquet :
    `doc.validate()` et `ddi validate` fonctionnent hors ligne, sans
    téléchargement supplémentaire ni accès réseau.

## Installer depuis les sources

Les développeurs contribuant à `ddi-l` devraient installer depuis un clone local :

```bash
git clone https://github.com/pbisson44/ddi-l.git
cd ddi-l
pip install -e .
```

Installer les outils de développement. Le projet est géré avec
[uv](https://docs.astral.sh/uv/), et `uv.lock` épingle chaque version de
dépendance :

```bash
uv sync --group dev              # Dépendances d'exécution et de développement
uv sync --group dev --extra full # ...plus le backend lxml optionnel
```

Notez que `full` est un **extra**, pas un groupe de dépendances :
`--group full` échoue.

Avec pip à la place (pip 25.1 ou plus récent lit les groupes de dépendances) :

```bash
pip install -e '.[full]' --group dev
```

Pour le travail sur la documentation (`docs` est un groupe de dépendances, pas
un extra) :

```bash
uv sync --group docs
# ou
pip install -e . --group docs
```

## Vérifier avec un test rapide

```python
import ddi_l as ddi

doc = ddi.new_study(title="Test", agency="example.org")
doc.add_question(text="Est-ce que ca marche ?")
print(f"Questions : {len(doc.questions)}")  # -> 1
```

Pour plus de détails, consultez le [guide d'utilisation](user-guide.md) ou le
[guide du contributeur](DEVELOPMENT.md).
