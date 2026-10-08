# ddi-l

`ddi-l` est une bibliothèque Python pour créer, lire, modifier et valider des
documents XML
[DDI Lifecycle 3.3](https://ddialliance.org/Specification/DDI-Lifecycle/3.3/).
Vous manipulez les études, les questions et les variables comme des objets
Python, et `ddi-l` écrit et vérifie le XML.

<div class="ddi-cta-group">

<a class="md-button md-button--primary" href="installation.md#installer-depuis-pypi">Installer ddi-l</a>
<a class="md-button md-button--secondary md-button--outlined" href="cli-recipes.md">Parcourir les recettes CLI</a>

</div>

## Démarrage rapide

```python
import ddi_l as ddi

# Créer une nouvelle étude
doc = ddi.new_study(title="Enquête ménages", agency="example.org")

# Ajouter des questions
q = doc.add_question(text="Quel âge avez-vous ?")

# Ajouter des variables liées aux questions
doc.add_variable(name="Age", question=q)

# Enregistrer en XML
doc.save("enquete-menages.xml")
```

```python
# Ouvrir une étude existante
doc = ddi.open_ddi("enquete-menages.xml")

for v in doc.variables:
    print(v.identifier)
```

## Installer

Installez `ddi-l` avec pip ou Poetry. L'extra `full` ajoute le moteur `lxml`,
plus rapide (voir [Installation](installation.md)).

=== "pip"
    ```bash
    pip install ddi-l
    ```

=== "Poetry"
    ```bash
    poetry add ddi-l
    poetry run ddi --help
    ```

## Pour continuer

<div class="grid cards landing-tiles" markdown>

- **Installer**

    Installez le paquet avec `pip` ou `poetry` et vérifiez qu'il fonctionne.

    [Guide d'installation →](installation.md#installer-depuis-pypi){ .md-button .md-button--primary }

- **Valider**

    Validez les documents par rapport aux schémas DDI, exécutez les règles de
    lint et ajoutez ces contrôles à la CI.

    [Guide de validation →](validation.md){ .md-button .md-button--secondary .md-button--outlined }

- **Rédiger**

    Construisez des documents DDI étape par étape avec l'API CRUD.

    [Tutoriels de rédaction →](tutorials/authoring.md){ .md-button .md-button--secondary .md-button--outlined }

- **Utiliser la CLI**

    Validez, faites l'aller-retour et convertissez des fichiers avec la
    commande `ddi`.

    [Recettes CLI →](cli-recipes.md){ .md-button .md-button--secondary .md-button--outlined }

</div>

Le site contient aussi un [programme de formation](curriculum/index.md) en
16 modules, une [référence de l'API](api.md) et une
[référence des modèles](models.md). Pour contribuer, consultez le
[guide de développement](DEVELOPMENT.md) et le
[guide des contributeurs](https://github.com/pbisson44/ddi-l/blob/main/CONTRIBUTING.md).
