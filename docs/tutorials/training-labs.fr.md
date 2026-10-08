# Exercices de formation interactifs

Ces ateliers guident les apprenants à travers l'API CRUD de `ddi-l`. Chaque
atelier est conçu pour une animation en direct ou un apprentissage autonome.

## Atelier 1 : Construire une enquête de zéro

!!! info "Objectifs"
    - Créer une étude, ajouter des questions et des variables, sauvegarder en XML.

### Étapes

1. Installer `ddi-l` et ouvrir une session Python :

    ```bash
    pip install -e .
    python
    ```

2. Créer une étude :

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Enquete Atelier 1", agency="lab.org")
    ```

3. Ajouter au moins trois questions et trois variables.

4. Ajouter un concept et un univers.

5. Sauvegarder et valider :

    ```python
    doc.save("atelier1.xml")
    issues = doc.validate()
    ```

## Atelier 2 : Ouvrir, modifier et revalider

1. Ouvrir le fichier de l'atelier 1 :

    ```python
    doc = ddi.open_ddi("atelier1.xml")
    ```

2. Ajouter une liste de codes et des catégories.

3. Supprimer une variable.

4. Valider et sauvegarder.

## Atelier 3 : Validation par CLI

1. Valider un fichier :

    ```bash
    ddi validate atelier1.xml
    ```

2. Convertir en JSON :

    ```bash
    ddi to-json atelier1.xml --indent 2
    ```

3. Vérifier avec le lint :

    ```bash
    ddi lint atelier1.xml
    ```
