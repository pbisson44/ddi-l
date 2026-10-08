# Workflows de rédaction

Ces tutoriels pratiques montrent comment construire des documents DDI étape par
étape avec l'API CRUD de `ddi-l`. Chaque leçon démarre d'un espace de
travail vierge et construit une étude avec des questions, des variables, des
concepts et de la validation.

!!! note
    Installez d'abord le paquet :

    ```bash
    pip install -e .
    ```

## Tutoriel 1 : Créer une étude de base

!!! info "Objectifs"
    - Créer une étude avec `ddi.new_study()`.
    - Ajouter des questions et des variables.
    - Sauvegarder en XML.

1. Créer l'étude :

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Etude tutoriel", agency="tutorial.org")
    ```

2. Ajouter des questions :

    ```python
    q1 = doc.add_question(text="Quel est votre age ?")
    q2 = doc.add_question(text="Quel est votre genre ?")
    ```

3. Ajouter des variables liées aux questions :

    ```python
    doc.add_variable(name="Age", question=q1)
    doc.add_variable(name="Genre", question=q2)
    ```

4. Sauvegarder :

    ```python
    doc.save("etude-tutoriel.xml")
    ```

## Tutoriel 2 : Ajouter des concepts et des univers

1. Ajouter du contenu conceptuel :

    ```python
    concept_age = doc.add_concept(name="Age")
    doc.add_universe(name="Adultes de 18 ans et plus")
    ```

2. Créer des variables avec des liens conceptuels :

    ```python
    doc.add_variable(name="Age du repondant", question=q1, concept=concept_age)
    ```

## Tutoriel 3 : Utiliser n'importe quel type d'élément

1. Ajouter des catégories et des instruments :

    ```python
    from ddi_l.models.logicalproduct import Category
    from ddi_l.models.datacollection import Instrument

    doc.add_item(Category, name="Homme")
    doc.add_item(Category, name="Femme")
    doc.add_item(Instrument, name="Questionnaire en ligne")
    ```

2. Interroger par type :

    ```python
    print(f"Categories : {len(doc.items(Category))}")
    ```

## Tutoriel 4 : Ouvrir, valider et modifier

!!! info "Objectifs"
    - Ouvrir un fichier DDI existant.
    - Valider le document.
    - Ajouter du contenu et sauvegarder.

1. Ouvrir et valider :

    ```python
    doc = ddi.open_ddi("tutorial-study.xml", validate=True)
    ```

2. Ajouter du contenu :

    ```python
    doc.add_question(text="Quel est votre niveau d'etudes ?")
    doc.add_code_list(name="Niveaux d'etudes")
    ```

3. Valider et sauvegarder :

    ```python
    issues = doc.validate()
    if not issues:
        doc.save("tutorial-study-updated.xml")
    ```

## Prochaines étapes

- Consultez le [guide de validation](../validation.md).
- Consultez la [référence des modèles](../models.md).
- Essayez les [ateliers de formation](training-labs.md).
