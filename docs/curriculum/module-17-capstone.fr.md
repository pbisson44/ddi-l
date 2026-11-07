---
description: >-
  Module 17 du cours ddi-l : quatre projets de synthèse, pour étudiants,
  chercheurs, archivistes et personnel d'organismes statistiques.
---

# Module 17 : Projets de synthèse

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Rédiger un plan de projet pour le jeu de données de votre piste : une ligne par colonne avec sa question (ou la raison pour laquelle elle n'en a pas), son type et sa liste de codes, ainsi que les techniques dont votre piste a besoin.
    - **O2.** Construire le document DDI à partir des données avec `ddi-l`, de sorte que chaque colonne demandée soit une variable liée à sa question, que les colonnes codées utilisent des listes de codes avec catégories, et que l'étude ait des concepts et un univers.
    - **O3.** Valider et analyser (lint) votre document, de sorte que `doc.validate()` ne renvoie aucune erreur, que `doc.lint()` ne signale aucune erreur et que `ddi validate` réussisse sur chaque fichier que vous enregistrez.
    - **O4.** Consigner le flux de questionnaire, la traçabilité, le couplage, les champs personnalisés ou la spécification que demande votre piste, de sorte qu'un lecteur du XML puisse les suivre sans votre script.
    - **O5.** Versionner un changement : augmenter la version, consigner une justification et le responsable, et enregistrer chaque version dans son propre fichier.
    - **O6.** Présenter votre projet en 5 minutes et justifier deux choix de conception, en nommant pour chacun l'option écartée et pourquoi.

**Prérequis :** Tous les modules précédents, du [Module 1](module-01-what-is-metadata.fr.md) au [Module 16](module-16-advanced-questionnaire-spec.fr.md). Le tableau sous « Choisissez votre piste » indique les modules sur lesquels chaque piste s'appuie le plus.

**Durée :** 60 à 90 min en autonomie / 90 min avec instructeur.

**Nouveau dans ce module :** rien de nouveau. Vous combinez ce que les modules précédents ont enseigné, comme `ddi.new_study()`, `doc.add_variable()`, `set_coded()`, `source_variable_references`, `doc.add_comparison()`, `set_property()`, `doc.lint()`, `load_spec()`, `ddi validate` et `ddi spec validate`.

---

## Introduction

Vous avez maintenant appris tous les outils. Vous savez comment créer des documents DDI, ajouter des métadonnées, valider des fichiers, gérer les versions et utiliser la ligne de commande. Il est maintenant temps de tout rassembler dans un vrai projet.

Choisissez la **piste** qui correspond à votre rôle. Chaque piste vous guide à travers un processus complet : planifier les métadonnées, les construire à partir d'un fichier de données, consigner ce dont votre piste a besoin, les valider, les versionner et présenter vos choix.

Si vous ne savez pas quelle piste choisir, essayez la **Piste A** (Étudiant universitaire). C'est le point de départ le plus simple.

### Choisissez votre piste

Chaque piste met en pratique les six objectifs. Elles diffèrent par les données et par les techniques que vous consignez pour l'objectif O4 :

| Piste | Pour | Données | Techniques pour O4 | Modules à revoir |
| --- | --- | --- | --- | --- |
| A | Étudiants universitaires | `thesis-data.csv` : 40 étudiants, 12 colonnes | Traçabilité : un indice de stress dérivé | 11 |
| B | Chercheurs | `health-survey.csv` : 40 répondants, 15 colonnes | Traçabilité (indice de masse corporelle) et couplage avec un registre hospitalier | 11, 12 |
| C | Archivistes | Trois petits fichiers DDI de trois équipes de recherche | Champs personnalisés tirés d'un catalogue, avec un audit | 6, 13, 14 |
| D | Personnel d'un institut national de statistique | `census-data.csv` : 55 personnes dans 20 ménages, 22 colonnes | Flux de questionnaire et spécification | 10, 16 |

---

## Planifiez votre projet

**(O1)** De bonnes métadonnées commencent sur papier. Avant d'écrire du code, rédigez un **plan** : un court tableau avec une ligne par colonne de votre fichier de données, et quelques lignes en dessous. Le plan est votre premier livrable. Il fait aussi gagner du temps, car la plupart des erreurs d'un projet de synthèse viennent de décisions prises au milieu du code.

Pour chaque colonne, décidez :

- **Question :** le libellé exact vu par le répondant, ou la raison pour laquelle il n'y en a pas. Un identifiant, comme un numéro d'étudiant, est *attribué*, et un score peut être *calculé*. Ni l'un ni l'autre n'a de question.
- **Type :** numérique, codé (une réponse dans une liste fixe), texte ou date.
- **Liste de codes :** pour une colonne codée, la liste des réponses permises.
- **Concept :** l'idée que la colonne mesure, comme « Bien-être ».

Voici quatre lignes d'un plan pour la Piste A :

| Colonne | Question, ou raison de son absence | Type | Liste de codes | Concept |
| --- | --- | --- | --- | --- |
| StudentID | Aucune : attribué par le chercheur | Texte | Aucune | Aucun |
| Gender | « Quel est votre genre ? » | Codé | Femme, Homme, Non binaire | Démographie |
| StressLevel | « Sur une échelle de 1 à 10, quel a été votre niveau de stress ce trimestre ? » | Numérique, 1 à 10 | Aucune | Bien-être |
| AnxietyScore | Aucune : calculé à partir d'une échelle d'anxiété standard | Numérique | Aucune | Bien-être |

Sous le tableau, rédigez trois courtes notes :

- **Techniques :** les techniques dont votre piste a besoin (voir le tableau ci-dessus), et où chacune s'applique. Pour la Piste A : « StressIndex est dérivé de StressLevel et AnxietyScore. »
- **Versions :** ce qui change dans la version suivante, et pourquoi.
- **Deux choix de conception** que vous présenterez à la fin (voir « Présentez votre projet » plus bas). Par exemple : pourquoi Program est codé plutôt qu'en texte libre.

---

## Piste A : Étudiant universitaire : Documenter le jeu de données de votre mémoire

!!! example "Scénario"
    Vous venez de terminer votre mémoire sur le stress étudiant. Votre jeu
    de données comporte 12 colonnes. Vous devez créer un document DDI pour
    que le dépôt de recherche de votre université puisse cataloguer vos
    données.

### Étapes

1. **(O1)** **Planifiez le projet.** Téléchargez le jeu de données de mémoire d'exemple (40 étudiants, 12 colonnes) ou utilisez votre propre fichier CSV d'au moins 10 colonnes. Remplissez le tableau du plan pour chaque colonne.

    [:material-download: Télécharger `thesis-data.csv`](thesis-data.csv){ .md-button download="thesis-data.csv" }

2. **(O2)** **Créez une étude DDI :**

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(
        title="Student Stress Survey 2024",
        agency="university.example.org",
    )
    ```

3. **(O2)** **Ajoutez des variables** à partir de vos colonnes CSV. Créez une variable pour chaque colonne. Liez chaque variable à la question dont elle provient. Un identifiant comme StudentID est attribué, et AnxietyScore est calculé : ni l'un ni l'autre n'a besoin de question.

    ```python
    q1 = doc.add_question(text="Combien d'heures étudiez-vous par jour ?", lang="fr")
    v1 = doc.add_variable(name="StudyHours", question=q1)
    q2 = doc.add_question(
        text="Sur une échelle de 1 à 10, quel a été votre niveau de stress ce trimestre ?",
        lang="fr",
    )
    stress = doc.add_variable(name="StressLevel", question=q2)
    # AnxietyScore est calculé à partir d'une échelle standard : pas de question.
    anxiety = doc.add_variable(name="AnxietyScore")
    # Répétez pour chaque colonne...
    ```

4. **(O2)** **Ajoutez 3 concepts et 1 univers :**

    ```python
    c1 = doc.add_concept(name="Academic Workload")
    c2 = doc.add_concept(name="Mental Health")
    c3 = doc.add_concept(name="Demographics")
    u1 = doc.add_universe(name="Undergraduate students aged 18-25")
    ```

5. **(O2)** **Ajoutez une liste de codes avec catégories** pour chaque colonne codée. Une **liste de codes** est l'ensemble des réponses permises. Chaque réponse est une **catégorie** (son sens) et un **code** (la valeur enregistrée dans les données) qui pointe vers la catégorie. `set_coded()` indique à la variable quelle liste de codes contient ses valeurs.

    ```python
    from uuid import uuid4

    from ddi_l.models.logicalproduct import Category, CodeItem

    gender_codes = doc.add_code_list(name="Gender Codes")
    for number, label in enumerate(["Femme", "Homme", "Non binaire"], start=1):
        category = doc.add_item(Category, name=label, label=label)
        gender_codes.codes.append(
            CodeItem(
                agency=gender_codes.agency,
                identifier=str(uuid4()),
                version=gender_codes.version,
                value=str(number),
                category=category.to_reference(),
            )
        )

    q3 = doc.add_question(text="Quel est votre genre ?", lang="fr")
    gender = doc.add_variable(name="Gender", question=q3)
    gender.set_coded(gender_codes)
    print(f"Gender codes: {len(gender_codes.codes)}")  # -> Gender codes: 3
    ```

6. **(O2)** **Définissez des propriétés personnalisées** sur au moins 2 éléments. Une propriété personnalisée est une métadonnée supplémentaire que vous définissez vous-même, comme une source de données ou une date de collecte.

    ```python
    v1.set_property("dataSource", "Outil d'enquête en ligne")
    v1.set_property("collectionDate", "2024-03-15")
    anxiety.set_property("scoring", "Somme d'une échelle d'anxiété standard à 10 items")
    ```

7. **(O3)** **Validez, analysez et enregistrez en version 1.0 :**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"Validation errors: {len(errors)}, lint errors: {len(lint_errors)}")
    # -> Validation errors: 0, lint errors: 0
    doc.save("thesis-v1.xml")
    ```

    L'analyse peut aussi signaler des avertissements, comme un élément sans libellé. Lisez-les, mais seules les erreurs vous empêchent d'enregistrer.

8. **(O4)** **Consignez la traçabilité d'une variable dérivée.** Ajoutez StressIndex, qui combine StressLevel et AnxietyScore. Elle est calculée, pas demandée : elle n'a donc pas de question. À la place, `source_variable_references` liste les variables à partir desquelles elle a été calculée.

    ```python
    stress_index = doc.add_variable(name="StressIndex")
    stress_index.source_variable_references = [
        stress.to_reference(),
        anxiety.to_reference(),
    ]
    print(f"StressIndex sources: {len(stress_index.source_variable_references)}")
    # -> StressIndex sources: 2
    ```

9. **(O5)** **Versionnez le changement.** Augmentez la version à 1.1, et consignez pourquoi et par qui.

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Added the derived StressIndex variable")
            ]
        )
    )
    study.version_responsibility = "Thesis Author"
    print(study.version)  # -> 1.1
    ```

10. **(O3)** **Validez, analysez et enregistrez en version 1.1 :**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    if not errors and not lint_errors:
        doc.save("thesis-v1.1.xml")
        print("Saved thesis-v1.1.xml")  # -> Saved thesis-v1.1.xml
    else:
        print("Errors:", errors, lint_errors)
    ```

### Livrables

- Votre plan : une ligne par colonne, et les trois notes.
- `thesis-v1.xml` : document DDI valide avec une variable pour chaque colonne.
- `thesis-v1.1.xml` : version 1.1, avec StressIndex, ses deux sources et une justification.

??? success "Exemple de solution"
    Un script complet pour toutes les étapes ci-dessus, avec
    [`thesis-data.csv`](thesis-data.csv){ download="thesis-data.csv" }.

    ```python
    import csv
    from uuid import uuid4

    import ddi_l as ddi
    from ddi_l.models.base import InternationalString, VersionRationale
    from ddi_l.models.logicalproduct import Category, CodeItem


    def add_codes(doc, code_list, labels):
        """Ajoute une Category et un Code par libellé, numérotés à partir de 1."""
        for number, label in enumerate(labels, start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )


    with open("thesis-data.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    columns = list(rows[0])

    # Version 1.0
    doc = ddi.new_study(title="Student Stress Survey 2024", agency="university.example.org")
    # Comment chaque colonne a été demandée. StudentID est attribué et AnxietyScore
    # est calculé à partir d'un questionnaire : ni l'un ni l'autre n'a de question.
    QUESTIONS = {
        "Age": "Quel âge avez-vous ?",
        "Gender": "Quel est votre genre ?",
        "YearOfStudy": "En quelle année de votre programme êtes-vous ?",
        "Program": "Dans quel programme êtes-vous inscrit(e) ?",
        "StudyHours": "Lors d'une journée typique, combien d'heures étudiez-vous ?",
        "SleepHours": "Lors d'une nuit typique, combien d'heures dormez-vous ?",
        "WorkHours": "Combien d'heures par semaine travaillez-vous contre rémunération ?",
        "ExerciseDays": "Combien de jours avez-vous fait de l'exercice la semaine dernière ?",
        "StressLevel": "Sur une échelle de 1 à 10, quel a été votre niveau de stress ce trimestre ?",
        "SoughtSupport": "Avez-vous demandé de l'aide aux services du campus ce trimestre ?",
    }
    questions = {
        col: doc.add_question(text=text, lang="fr") for col, text in QUESTIONS.items()
    }
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }

    # Une liste de codes par colonne codée, à partir des valeurs du fichier
    for col in ("Gender", "Program", "SoughtSupport"):
        code_list = doc.add_code_list(name=f"{col} Codes")
        add_codes(doc, code_list, sorted({row[col] for row in rows}))
        variables[col].set_coded(code_list)

    doc.add_concept(name="Demographics")
    doc.add_concept(name="Academic Workload")
    doc.add_concept(name="Well-Being")
    doc.add_universe(name="Undergraduate students aged 18-25")
    variables["StudyHours"].set_property("dataSource", "Outil d'enquête en ligne")
    variables["AnxietyScore"].set_property(
        "scoring", "Somme d'une échelle d'anxiété standard à 10 items"
    )

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v1: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    doc.save("thesis-v1.xml")

    # Version 1.1 : une variable dérivée et sa traçabilité
    doc = ddi.open_ddi("thesis-v1.xml")
    by_name = {v.names[0].text: v for v in doc.variables}
    stress_index = doc.add_variable(name="StressIndex")
    stress_index.source_variable_references = [
        by_name["StressLevel"].to_reference(),
        by_name["AnxietyScore"].to_reference(),
    ]

    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Added the derived StressIndex variable")
            ]
        )
    )
    study.version_responsibility = "Thesis Author"

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v1.1: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    # -> v1.1: 0 validation errors, 0 lint errors
    doc.save("thesis-v1.1.xml")
    ```

---

## Piste B : Chercheur : Préparer une enquête de santé pour publication

!!! example "Scénario"
    Vous dirigez une étude de santé multi-pays. Votre fichier de données
    comporte 15 colonnes de données d'enquête. Votre équipe a aussi couplé
    chaque répondant à un registre des hospitalisations. Vous devez préparer
    les métadonnées pour un dépôt de données ouvertes.

### Étapes

1. **(O1)** **Planifiez le projet et lisez les données.** Partez d'un fichier de données avec au moins 15 colonnes. Téléchargez l'enquête de santé d'exemple (40 répondants, 15 colonnes) ou utilisez la vôtre. Remplissez le tableau du plan, puis lisez le nom des colonnes :

    [:material-download: Télécharger `health-survey.csv`](health-survey.csv){ .md-button download="health-survey.csv" }

    ```python
    import csv

    import ddi_l as ddi

    with open("health-survey.csv", newline="", encoding="utf-8") as f:
        columns = csv.DictReader(f).fieldnames

    doc = ddi.new_study(
        title="International Health Survey 2024",
        agency="health-research.example.org",
    )
    print(f"{len(columns)} columns")  # -> 15 columns
    ```

    Si vos données sont dans un classeur Excel, lisez plutôt le nom des colonnes avec pandas (voir le [Module 8](module-08-csv-to-ddi.fr.md)) :

    <!-- docs-test: skip -- needs pandas and a workbook the reader supplies -->
    ```python
    import pandas as pd

    columns = list(pd.read_excel("health-survey.xlsx").columns)
    ```

2. **(O2)** **Créez les questions et les variables** à partir des colonnes. La première ligne ci-dessous crée une question par entrée de `QUESTIONS`. La seconde crée une variable par colonne et la lie à sa question. `questions.get(col)` donne `None` pour une colonne sans question, comme RespondentID.

    ```python
    # Copiez les libellés de votre questionnaire. Les colonnes absentes, comme
    # RespondentID, deviennent des variables sans question.
    QUESTIONS = {
        "Age": "Quel âge avez-vous ?",
        "SmokingStatus": "Laquelle de ces options décrit le mieux votre consommation de tabac ?",
        "ExerciseFrequency": "À quelle fréquence faites-vous au moins 30 minutes d'exercice ?",
        "SelfRatedHealth": "En général, comment évaluez-vous votre santé ?",
        # ...une entrée pour chaque colonne demandée
    }
    questions = {
        col: doc.add_question(text=text, lang="fr") for col, text in QUESTIONS.items()
    }
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }
    print(f"Variables: {len(doc.variables)}")  # -> Variables: 15
    ```

3. **(O2)** **Ajoutez 4 concepts et un univers :**

    ```python
    doc.add_concept(name="Physical Health")
    doc.add_concept(name="Mental Health")
    doc.add_concept(name="Access to Healthcare")
    doc.add_concept(name="Demographics")
    doc.add_universe(name="Adults aged 18 and over in the participating countries")
    ```

4. **(O2)** **Ajoutez 2 listes de codes** construites à partir des valeurs du fichier. Une **liste de codes** est un ensemble de réponses permises (comme « Oui », « Non », « Incertain »). `{row[col] for row in rows}` recueille les valeurs distinctes d'une colonne ; chacune devient une catégorie et un code, et `set_coded()` fait pointer la variable vers la liste.

    ```python
    from uuid import uuid4

    from ddi_l.models.logicalproduct import Category, CodeItem

    with open("health-survey.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for col in ["SmokingStatus", "ExerciseFrequency"]:
        code_list = doc.add_code_list(name=f"{col} Codes")
        for number, label in enumerate(sorted({row[col] for row in rows}), start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )
        variables[col].set_coded(code_list)

    print(f"Code lists: {len(doc.code_lists)}")  # -> Code lists: 2
    ```

5. **(O4)** **Consignez la traçabilité.** L'indice de masse corporelle (IMC) est calculé à partir de la taille et du poids. Il n'a pas de question ; il liste plutôt ses deux sources (voir le [Module 11](module-11-data-lineage.fr.md)) :

    ```python
    bmi = doc.add_variable(name="BMI", label="Body mass index")
    bmi.source_variable_references = [
        variables["HeightCm"].to_reference(),
        variables["WeightKg"].to_reference(),
    ]
    ```

6. **(O4)** **Consignez le couplage.** Votre équipe a joint l'enquête à un registre des hospitalisations sur RespondentID. Consignez-le comme au [Module 12](module-12-data-linkage.fr.md) : le registre est une seconde étude, la clé est marquée des deux côtés, une `Comparison` met les clés en correspondance, et la variable couplée nomme ses sources dans les deux études.

    ```python
    register = doc.add_study(title="Hospital Admissions Register 2024")
    register_ds = doc.study(register.identifier)
    register_key = register_ds.add_variable(name="RespondentID")
    admissions = register_ds.add_variable(name="HospitalAdmissions")

    variables["RespondentID"].set_property("linkage_role", "key")
    register_key.set_property("linkage_role", "key")

    link = doc.add_comparison(name="Survey-to-register linkage 2024")
    exact = link.correspondence(
        commonality="The same respondent identifier in both sources.",
        weight=1.0,
    )
    link.add_variable_map(
        variables["RespondentID"].to_reference(),
        register_key.to_reference(),
        correspondence=exact,
    )
    link.set_property("linkage_method", "deterministic")

    linked = doc.add_variable(name="HealthByHospitalUse")
    linked.source_variable_references = [
        variables["SelfRatedHealth"].to_reference(),
        admissions.to_reference(),
    ]
    print(f"Comparisons: {len(doc.comparisons)}")  # -> Comparisons: 1
    ```

    À l'enregistrement, `ddi-l` avertit qu'une variable source n'est pas dans le document courant. C'est attendu : elle est dans l'étude du registre.

7. **(O3)** **Validez et analysez le document :**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"Validation errors: {len(errors)}, lint errors: {len(lint_errors)}")
    # -> Validation errors: 0, lint errors: 0
    ```

8. **(O3)** **Enregistrez en version 1.0 :**

    ```python
    doc.save("health-survey-v1.xml")
    ```

    Puis **exportez-le en JSON** depuis la ligne de commande :

    ```bash
    ddi to-json health-survey-v1.xml --indent 2 > health-survey-v1.json
    ```

9. **(O5)** **Mettez à jour en version 1.1** avec une justification. Ajoutez une nouvelle variable ou corrigez un libellé.

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    q_dentist = doc.add_question(
        text="Combien de fois avez-vous consulté un dentiste au cours des 12 derniers mois ?",
        lang="fr",
    )
    doc.add_variable(name="DentistVisitsLastYear", question=q_dentist)
    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added dental visit frequency question")]
        )
    )
    study.version_responsibility = "Principal Investigator"
    doc.save("health-survey-v1.1.xml")
    ```

    Vérifiez le nouveau fichier depuis la ligne de commande avec `ddi validate health-survey-v1.1.xml`.

### Livrables

- Votre plan : une ligne par colonne, et les trois notes.
- `health-survey-v1.xml` : document DDI valide, avec la traçabilité de l'IMC et le couplage avec le registre.
- `health-survey-v1.json` : export JSON du document.
- `health-survey-v1.1.xml` : version mise à jour avec justification.

??? success "Exemple de solution"
    Un script complet, avec
    [`health-survey.csv`](health-survey.csv){ download="health-survey.csv" }.
    Exécutez ensuite `ddi to-json health-survey-v1.xml --indent 2 > health-survey-v1.json`.

    ```python
    import csv
    from uuid import uuid4

    import ddi_l as ddi
    from ddi_l.models.base import InternationalString, VersionRationale
    from ddi_l.models.logicalproduct import Category, CodeItem


    def add_codes(doc, code_list, labels):
        """Ajoute une Category et un Code par libellé, numérotés à partir de 1."""
        for number, label in enumerate(labels, start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )


    with open("health-survey.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    columns = list(rows[0])

    doc = ddi.new_study(
        title="International Health Survey 2024", agency="health-research.example.org"
    )
    # RespondentID est attribué, pas demandé : il n'a pas de question.
    QUESTIONS = {
        "Country": "Dans quel pays habitez-vous ?",
        "Age": "Quel âge avez-vous ?",
        "Sex": "Quel est votre sexe ?",
        "HeightCm": "Quelle est votre taille, en centimètres ?",
        "WeightKg": "Quel est votre poids, en kilogrammes ?",
        "SmokingStatus": "Laquelle de ces options décrit le mieux votre consommation de tabac ?",
        "ExerciseFrequency": "À quelle fréquence faites-vous au moins 30 minutes d'exercice ?",
        "AlcoholDrinksPerWeek": "Combien de boissons alcoolisées prenez-vous lors d'une semaine typique ?",
        "SelfRatedHealth": "En général, comment évaluez-vous votre santé ?",
        "ChronicCondition": "Avez-vous un problème de santé de longue durée ?",
        "DoctorVisitsLastYear": "Combien de fois avez-vous consulté un médecin au cours des 12 derniers mois ?",
        "HasHealthInsurance": "Avez-vous une assurance maladie ?",
        "SleepHours": "Lors d'une nuit typique, combien d'heures dormez-vous ?",
        "Wellbeing": "Sur une échelle de 0 à 10, dans quelle mesure êtes-vous satisfait(e) de votre vie ?",
    }
    questions = {
        col: doc.add_question(text=text, lang="fr") for col, text in QUESTIONS.items()
    }
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }

    for col in ("SmokingStatus", "ExerciseFrequency"):
        code_list = doc.add_code_list(name=f"{col} Codes")
        add_codes(doc, code_list, sorted({row[col] for row in rows}))
        variables[col].set_coded(code_list)

    for name in (
        "Physical Health",
        "Mental Health",
        "Access to Healthcare",
        "Demographics",
    ):
        doc.add_concept(name=name)
    doc.add_universe(name="Adults aged 18 and over in the participating countries")

    # Traçabilité : l'IMC est calculé à partir de la taille et du poids
    bmi = doc.add_variable(name="BMI", label="Body mass index")
    bmi.source_variable_references = [
        variables["HeightCm"].to_reference(),
        variables["WeightKg"].to_reference(),
    ]

    # Couplage : le registre est une seconde étude, jointe sur RespondentID
    register = doc.add_study(title="Hospital Admissions Register 2024")
    register_ds = doc.study(register.identifier)
    register_key = register_ds.add_variable(name="RespondentID")
    admissions = register_ds.add_variable(name="HospitalAdmissions")
    variables["RespondentID"].set_property("linkage_role", "key")
    register_key.set_property("linkage_role", "key")

    link = doc.add_comparison(name="Survey-to-register linkage 2024")
    exact = link.correspondence(
        commonality="The same respondent identifier in both sources.", weight=1.0
    )
    link.add_variable_map(
        variables["RespondentID"].to_reference(),
        register_key.to_reference(),
        correspondence=exact,
    )
    link.set_property("linkage_method", "deterministic")
    linked = doc.add_variable(name="HealthByHospitalUse")
    linked.source_variable_references = [
        variables["SelfRatedHealth"].to_reference(),
        admissions.to_reference(),
    ]

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v1: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    # -> v1: 0 validation errors, 0 lint errors
    doc.save("health-survey-v1.xml")

    # Version 1.1
    dentist = doc.add_question(
        text="Combien de fois avez-vous consulté un dentiste au cours des 12 derniers mois ?",
        lang="fr",
    )
    doc.add_variable(name="DentistVisitsLastYear", question=dentist)
    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added dental visit frequency question")]
        )
    )
    study.version_responsibility = "Principal Investigator"
    print(f"v1.1: {len(doc.validate())} validation errors")
    # -> v1.1: 0 validation errors
    doc.save("health-survey-v1.1.xml")
    ```

---

## Piste C : Archiviste : Enrichir et versionner des fichiers DDI existants

!!! example "Scénario"
    Vous gérez une collection de données dans une bibliothèque nationale.
    Vous recevez 3 fichiers DDI de différentes équipes de recherche. Certains
    fichiers manquent de métadonnées. Vous devez vérifier chaque fichier,
    ajouter ce qui manque, consigner les renseignements propres aux archives
    et créer de nouvelles versions.

### Étapes

1. **(O1)** **Préparez 3 fichiers DDI et planifiez.** Utilisez des fichiers des modules précédents, ou créez 3 petites études maintenant. Votre plan a une ligne par fichier : ce qu'il contient, ce qui manque et ce que vous ajouterez.

    ```python
    import ddi_l as ddi

    questions = [
        "Quel âge avez-vous ?",
        "Combien de personnes vivent dans votre ménage ?",
        "Avez-vous voté à la dernière élection fédérale ?",
    ]
    for i, texte in enumerate(questions, start=1):
        doc = ddi.new_study(
            title=f"Research Study {i}",
            agency="library.example.org",
        )
        doc.add_question(text=texte, lang="fr")
        doc.add_variable(name=f"Var{i}")
        doc.save(f"study-{i}.xml")
    ```

2. **(O3)** **Pour chaque fichier, vérifiez la complétude.** Ouvrez le fichier et listez ce qu'il contient. La dernière ligne compte les variables liées à une question :

    ```python
    doc = ddi.open_ddi("study-1.xml")
    print(f"Questions:  {len(doc.questions)}")
    print(f"Variables:  {len(doc.variables)}")
    print(f"Concepts:   {len(doc.concepts)}")
    print(f"Universes:  {len(doc.universes)}")
    print(f"Code lists: {len(doc.code_lists)}")
    linked = sum(1 for v in doc.variables if v.question_references)
    print(f"Variables linked to a question: {linked}")
    # -> Variables linked to a question: 0
    ```

3. **(O2)** **Ajoutez les métadonnées manquantes.** Si un fichier n'a pas de concepts, ajoutez-en un. S'il n'a pas d'univers, ajoutez-en un. Si une variable n'est pas liée à sa question, liez-la. Si une question a un ensemble fixe de réponses, comme la question sur le vote de l'étude 3, ajoutez une liste de codes avec catégories et faites pointer la variable vers elle (l'exemple de solution montre comment).

    ```python
    doc.add_concept(name="Social Sciences")
    doc.add_universe(name="General population")

    # Liez la variable à la question qu'elle enregistre
    variable, question = doc.variables[0], doc.questions[0]
    variable.question_references = [question.to_reference()]
    ```

4. **(O4)** **Ajoutez des champs personnalisés tirés d'un catalogue.** Vos archives consignent les mêmes renseignements pour chaque fichier accepté. Écrivez-les une fois sous forme de **catalogue** : un espace de noms (`archive:`) et le sens de chaque clé (voir le [Module 14](module-14-custom-fields.fr.md)). Ne définissez les champs qu'au moyen d'une fonction qui vérifie le catalogue, pour qu'une faute de frappe ne puisse pas créer une nouvelle clé. Puis faites l'audit du fichier : comptez les éléments qui portent vos champs.

    ```python
    ARCHIVE_FIELDS = {
        "archive:accession_date": "Date à laquelle les archives ont reçu le fichier.",
        "archive:depositor": "Équipe qui a déposé le fichier.",
        "archive:retention": "Durée de conservation du fichier par les archives.",
        "archive:access": "Qui peut utiliser les données : ouvert, inscrit ou restreint.",
    }


    def set_archive_field(item, key, value):
        if key not in ARCHIVE_FIELDS:
            raise KeyError(f"{key!r} is not in the archive catalog")
        item.set_property(key, value)


    def count_archive_fields(doc):
        items = [doc.study_unit, *doc.questions, *doc.variables]
        return sum(
            any(key.startswith("archive:") for key in item.properties) for item in items
        )


    study = doc.study_unit
    set_archive_field(study, "archive:accession_date", "2024-11-04")
    set_archive_field(study, "archive:depositor", "Research team 1")
    set_archive_field(study, "archive:retention", "permanent")
    set_archive_field(variable, "archive:access", "open")
    print(f"Items with archive fields: {count_archive_fields(doc)}")
    # -> Items with archive fields: 2
    ```

5. **(O5)** **Augmentez la version avec une justification :**

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Enriched metadata: added concept, universe, question link and archive fields"
                )
            ]
        )
    )
    study.version_responsibility = "Archive Metadata Team"
    ```

6. **(O3)** **Validez, analysez et enregistrez :**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    if not errors and not lint_errors:
        doc.save("study-1-enriched.xml")
        print("Saved study-1-enriched.xml")  # -> Saved study-1-enriched.xml
    ```

7. **Répétez les étapes 2 à 6 pour les 3 fichiers.**

### Livrables

- Votre plan : une ligne par fichier.
- 3 fichiers XML mis à jour (`study-1-enriched.xml`, `study-2-enriched.xml`, `study-3-enriched.xml`), tous valides, chacun avec une justification de version.
- Votre catalogue de champs personnalisés, et le compte de l'audit pour chaque fichier.

??? success "Exemple de solution"
    Une boucle sur les trois fichiers de l'étape 1.

    ```python
    from uuid import uuid4

    import ddi_l as ddi
    from ddi_l.models.base import InternationalString, VersionRationale
    from ddi_l.models.logicalproduct import Category, CodeItem

    ARCHIVE_FIELDS = {
        "archive:accession_date": "Date à laquelle les archives ont reçu le fichier.",
        "archive:depositor": "Équipe qui a déposé le fichier.",
        "archive:retention": "Durée de conservation du fichier par les archives.",
        "archive:access": "Qui peut utiliser les données : ouvert, inscrit ou restreint.",
    }
    YES_NO_FILES = {3}  # d'après le plan : l'étude 3 pose une question oui/non


    def set_archive_field(item, key, value):
        if key not in ARCHIVE_FIELDS:
            raise KeyError(f"{key!r} is not in the archive catalog")
        item.set_property(key, value)


    def count_archive_fields(doc):
        items = [doc.study_unit, *doc.questions, *doc.variables]
        return sum(
            any(key.startswith("archive:") for key in item.properties) for item in items
        )


    for i in (1, 2, 3):
        doc = ddi.open_ddi(f"study-{i}.xml")
        if not doc.concepts:
            doc.add_concept(name="Social Sciences")
        if not doc.universes:
            doc.add_universe(name="General population")
        variable, question = doc.variables[0], doc.questions[0]
        if not variable.question_references:
            variable.question_references = [question.to_reference()]
        if i in YES_NO_FILES:
            yes_no = doc.add_code_list(name="Oui/Non")
            for value, label in (("1", "Oui"), ("2", "Non")):
                category = doc.add_item(Category, name=label, label=label)
                yes_no.codes.append(
                    CodeItem(
                        agency=yes_no.agency,
                        identifier=str(uuid4()),
                        version=yes_no.version,
                        value=value,
                        category=category.to_reference(),
                    )
                )
            variable.set_coded(yes_no)

        study = doc.study_unit
        set_archive_field(study, "archive:accession_date", "2024-11-04")
        set_archive_field(study, "archive:depositor", f"Research team {i}")
        set_archive_field(study, "archive:retention", "permanent")
        set_archive_field(variable, "archive:access", "open")

        study.increment_minor_version(allow_dotted=True)
        study.version_rationales.append(
            VersionRationale(
                descriptions=[
                    InternationalString(
                        text="Enriched metadata: added concept, universe, question link and archive fields"
                    )
                ]
            )
        )
        study.version_responsibility = "Archive Metadata Team"

        lint_errors = [f for f in doc.lint() if f.severity == "error"]
        print(
            f"study-{i}: {len(doc.validate())} validation errors, "
            f"{len(lint_errors)} lint errors, "
            f"{count_archive_fields(doc)} items with archive fields"
        )
        doc.save(f"study-{i}-enriched.xml")
    # -> study-3: 0 validation errors, 0 lint errors, 2 items with archive fields
    ```

---

## Piste D : Personnel des INS : Construire un instrument de recensement

!!! example "Scénario"
    Vous travaillez dans un bureau national de statistique. Votre équipe de
    recensement possède un grand fichier CSV avec 20+ colonnes. Vous devez
    construire un document DDI complet, créer des listes de codes à partir
    des données, décrire le flux du questionnaire et rédiger sa
    spécification, gérer plusieurs versions et automatiser la validation
    avec un script bash.

### Étapes

1. **(O1)** **Planifiez le projet et lisez les données.** Partez d'un grand CSV avec 20+ colonnes. Téléchargez l'extrait de recensement d'exemple (55 personnes dans 20 ménages, 22 colonnes, dont les cinq colonnes codées utilisées à l'étape 3) ou utilisez le vôtre. Remplissez le tableau du plan. Notez que EmploymentType vaut « Sans objet » pour les enfants : c'est un filtre, que l'étape 5 consigne.

    [:material-download: Télécharger `census-data.csv`](census-data.csv){ .md-button download="census-data.csv" }

    ```python
    import csv

    import ddi_l as ddi

    with open("census-data.csv", newline="", encoding="utf-8") as f:
        columns = csv.DictReader(f).fieldnames

    doc = ddi.new_study(
        title="National Census 2024",
        agency="census.example.gov",
    )
    print(f"{len(columns)} columns")  # -> 22 columns
    ```

2. **(O2)** **Créez 20+ variables** à partir des colonnes du CSV, chacune liée à sa question :

    ```python
    # Libellés du questionnaire du recensement. HouseholdID et PersonNumber sont
    # attribués, pas demandés : ils sont omis et n'ont pas de question.
    QUESTIONS = {
        "Province": "Dans quelle province ou quel territoire habitez-vous ?",
        "Age": "Quel âge aviez-vous à votre dernier anniversaire ?",
        "Gender": "Quel est votre genre ?",
        "MaritalStatus": "Quel est votre état matrimonial ?",
        "EmploymentType": "La semaine dernière, étiez-vous salarié(e), travailleur autonome ou sans travail ?",
        "HousingType": "Dans quel type de logement habitez-vous ?",
        # ...une entrée pour chaque colonne restante
    }
    questions = {
        col: doc.add_question(text=text, lang="fr") for col, text in QUESTIONS.items()
    }
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }
    print(f"Variables: {len(doc.variables)}")  # -> Variables: 22
    ```

3. **(O2)** **Construisez 5 listes de codes** à partir des valeurs du fichier, chacune avec une catégorie et un code par valeur :

    ```python
    from uuid import uuid4

    from ddi_l.models.logicalproduct import Category, CodeItem

    with open("census-data.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    categorical_cols = [
        "Province",
        "Gender",
        "MaritalStatus",
        "EmploymentType",
        "HousingType",
    ]
    for col in categorical_cols:
        code_list = doc.add_code_list(name=f"{col}Codes")
        for number, label in enumerate(sorted({row[col] for row in rows}), start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )
        variables[col].set_coded(code_list)

    print(f"Code lists: {len(doc.code_lists)}")  # -> Code lists: 5
    ```

4. **(O2)** **Ajoutez des concepts, un univers et des propriétés personnalisées.** Définissez des propriétés personnalisées, comme une classification, sur au moins 2 éléments :

    ```python
    doc.add_concept(name="Population")
    doc.add_concept(name="Labour")
    doc.add_universe(name="All persons usually resident in private dwellings")

    variables["Occupation"].set_property("classification", "ISCO-08")
    variables["AnnualIncome"].set_property("referencePeriod", "Calendar year 2023")
    ```

5. **(O4)** **Construisez le flux du questionnaire.** Tout le monde répond aux questions sur la personne. Seules les personnes de 15 ans et plus répondent aux questions sur le travail. Construisez le flux comme au [Module 10](module-10-questionnaire-flows.fr.md) : un `QuestionConstruct` pour chaque question, une `Sequence` pour chaque section, un `IfThenElse` pour le filtre, et un `Instrument` qui pointe vers la séquence principale.

    ```python
    from ddi_l.models.datacollection import (
        IfThenElse,
        Instrument,
        QuestionConstruct,
        Sequence,
    )

    AGE_GATE = "Age >= 15"


    def ask(col):
        """Un QuestionConstruct qui pose la question de la colonne col."""
        return doc.add_item(
            QuestionConstruct, name=col, question_reference=questions[col].to_reference()
        )


    person = doc.add_item(
        Sequence,
        name="person",
        control_construct_references=[
            ask("Age").to_reference(),
            ask("Gender").to_reference(),
        ],
    )
    labour = doc.add_item(
        Sequence,
        name="labour",
        control_construct_references=[ask("EmploymentType").to_reference()],
    )
    gate = doc.add_item(IfThenElse, name="Working-age gate")
    gate.set_condition(AGE_GATE, description="Persons aged 15 and over")
    gate.then_construct_reference = labour.to_reference()

    main = doc.add_item(
        Sequence,
        name="Census flow",
        control_construct_references=[person.to_reference(), gate.to_reference()],
    )
    instrument = doc.add_item(Instrument, name="Census 2024 questionnaire")
    instrument.control_construct_reference = main.to_reference()
    print(f"Instruments: {len(doc.items(Instrument))}")  # -> Instruments: 1
    ```

6. **(O4)** **Rédigez la spécification.** Une spécification dit ce que l'instrument doit contenir : ses modules, leurs questions et les filtres (voir le [Module 16](module-16-advanced-questionnaire-spec.fr.md)). Écrivez-la dans un fichier, chargez-la et vérifiez que son filtre dit la même chose que celui de l'instrument.

    ```python
    from pathlib import Path

    from ddi_l.spec import equivalent, load_spec

    SPEC = """\
    spec: census-2024
    version: "1"
    code_lists:
      Employment:
        values: {1: Employé(e), 2: Travailleur autonome, 3: Sans emploi, 4: Inactif}
    modules:
      - id: person
        questions:
          - id: Age
            domain: {numeric: {min: 0, max: 120, decimals: 0}}
      - id: labour
        gate: Age >= 15
        questions:
          - id: EmploymentType
            domain: {code: {list: Employment}}
    """
    Path("census.spec.yaml").write_text(SPEC, encoding="utf-8")

    spec = load_spec("census.spec.yaml")
    labour_gate = spec.module("labour").gate_text
    print(labour_gate, equivalent(labour_gate, AGE_GATE))  # -> Age >= 15 True
    print(equivalent(AGE_GATE, "not Age < 15"))  # -> False
    ```

    Décidez ce que fait le filtre quand Age n'a pas de réponse, et écrivez-le dans votre plan. `Age >= 15` est faux quand Age manque : une personne sans âge saute donc les questions sur le travail. `not Age < 15` les lui poserait, et c'est pourquoi `equivalent()` dit que les deux diffèrent. « Sans objet » n'est pas dans la liste de codes de la spécification : c'est ce que les données contiennent pour les personnes que le filtre a fait sauter.

    Vérifiez aussi le fichier de spécification depuis la ligne de commande :

    ```bash
    ddi spec validate census.spec.yaml
    ```

7. **(O3)** **Validez, analysez et enregistrez en version 1.0 :**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"Validation errors: {len(errors)}, lint errors: {len(lint_errors)}")
    # -> Validation errors: 0, lint errors: 0
    doc.save("census-v1.xml")
    ```

8. **(O5)** **Mettez à jour en version 1.1** : ajoutez une nouvelle question et une variable :

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    q_internet = doc.add_question(
        text="Avez-vous accès à Internet haute vitesse ?", lang="fr"
    )
    doc.add_variable(name="HighSpeedInternet", question=q_internet)
    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added internet access question")]
        )
    )
    study.version_responsibility = "Census Content Team"
    doc.save("census-v1.1.xml")
    ```

9. **(O5)** **Mettez à jour en version 2.0** : refonte majeure (ajoutez 5 nouvelles questions, retirez-en 3 anciennes). Retirer une question retire aussi la variable qui enregistrait ses réponses ; sinon, elle continuerait de pointer vers une question qui n'est plus dans le fichier (voir le [Module 15](module-15-update-and-version.fr.md)). Ne retirez que des questions que le flux n'utilise pas. Une version contient une seule justification : remplacez donc celle de la version 1.1 ; `census-v1.1.xml` la conserve.

    ```python
    # Ajoutez les nouvelles questions
    for texte in [
        "Quelle langue parlez-vous le plus souvent à la maison ?",
        "Vous identifiez-vous comme Autochtone ?",
        "Quel est votre plus haut diplôme ?",
        "Avez-vous une incapacité ?",
        "Quel est le revenu annuel de votre ménage ?",
    ]:
        doc.add_question(text=texte, lang="fr")

    # Retirez 3 anciennes questions, et les variables qui enregistraient leurs réponses
    for col in ["Province", "MaritalStatus", "HousingType"]:
        doc.remove(variables[col].identifier)
        doc.remove(questions[col].identifier)

    study.increment_major_version()
    study.version_rationales = [
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Major redesign: added equity and income questions"
                )
            ]
        )
    ]
    errors = [finding for finding in doc.lint() if finding.severity == "error"]
    print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
    print(f"Validation errors: {len(doc.validate())}")  # -> Validation errors: 0
    doc.save("census-v2.xml")
    ```

10. **(O3)** **Validation par lots** des trois fichiers depuis la ligne de commande :

    ```bash
    ddi validate census-v1.xml
    ddi validate census-v1.1.xml
    ddi validate census-v2.xml
    ```

11. **(O3)** **Écrivez un script bash** qui exécute le pipeline complet :

    ```bash
    #!/bin/bash
    # validate.sh: check the spec, then validate all census DDI files.

    echo "=== Checking the spec ==="
    ddi spec validate census.spec.yaml

    echo "=== Validating census files ==="
    for f in census-v*.xml; do
        echo "--- $f ---"
        ddi validate "$f"
        if [ $? -eq 0 ]; then
            echo "PASS"
        else
            echo "FAIL"
        fi
        echo ""
    done
    echo "=== Done ==="
    ```

    Rendez le script exécutable et lancez-le :

    ```bash
    chmod +x validate.sh
    ./validate.sh
    ```

### Livrables

- Votre plan : une ligne par colonne, les trois notes, et ce que fait le filtre quand l'âge manque.
- `census-v1.xml` : version 1.0, valide, avec l'instrument et son filtre.
- `census.spec.yaml` : la spécification, qui passe `ddi spec validate`.
- `census-v1.1.xml` : version 1.1, valide, avec justification.
- `census-v2.xml` : version 2.0, valide, avec justification.
- `validate.sh` : script bash qui vérifie la spécification et valide tous les fichiers.

??? success "Exemple de solution"
    Un script complet, avec
    [`census-data.csv`](census-data.csv){ download="census-data.csv" }.
    Exécutez ensuite `validate.sh` de l'étape 11.

    ```python
    import csv
    from pathlib import Path
    from uuid import uuid4

    import ddi_l as ddi
    from ddi_l.models.base import InternationalString, VersionRationale
    from ddi_l.models.datacollection import (
        IfThenElse,
        Instrument,
        QuestionConstruct,
        Sequence,
    )
    from ddi_l.models.logicalproduct import Category, CodeItem
    from ddi_l.spec import equivalent, load_spec


    def add_codes(doc, code_list, labels):
        """Ajoute une Category et un Code par libellé, numérotés à partir de 1."""
        for number, label in enumerate(labels, start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )


    def rationale(text):
        return VersionRationale(descriptions=[InternationalString(text=text)])


    with open("census-data.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    columns = list(rows[0])

    doc = ddi.new_study(title="National Census 2024", agency="census.example.gov")
    # HouseholdID et PersonNumber sont attribués, pas demandés.
    QUESTIONS = {
        "Province": "Dans quelle province ou quel territoire habitez-vous ?",
        "Age": "Quel âge aviez-vous à votre dernier anniversaire ?",
        "Gender": "Quel est votre genre ?",
        "MaritalStatus": "Quel est votre état matrimonial ?",
        "RelationshipToHead": "Quel est votre lien avec la personne 1 ?",
        "CountryOfBirth": "Dans quel pays êtes-vous né(e) ?",
        "Citizenship": "De quel pays êtes-vous citoyen(ne) ?",
        "MotherTongue": "Quelle langue avez-vous apprise en premier à la maison dans votre enfance ?",
        "HighestEducation": "Quel est le plus haut niveau de scolarité que vous avez terminé ?",
        "EmploymentType": "La semaine dernière, étiez-vous salarié(e), travailleur autonome ou sans travail ?",
        "Occupation": "Quel était votre principal genre de travail la semaine dernière ?",
        "WeeklyHoursWorked": "Combien d'heures avez-vous travaillé la semaine dernière ?",
        "AnnualIncome": "Quel était votre revenu total l'an dernier ?",
        "CommuteMode": "Comment vous rendiez-vous habituellement au travail la semaine dernière ?",
        "HousingType": "Dans quel type de logement habitez-vous ?",
        "Tenure": "Ce logement appartient-il à un membre du ménage ou est-il loué ?",
        "Rooms": "Combien de pièces compte ce logement ?",
        "YearBuilt": "En quelle année ce logement a-t-il été construit ?",
        "HouseholdSize": "Combien de personnes habitent ici habituellement ?",
        "InternetAccess": "Ce ménage a-t-il accès à Internet à la maison ?",
    }
    questions = {
        col: doc.add_question(text=text, lang="fr") for col, text in QUESTIONS.items()
    }
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }

    for col in ("Province", "Gender", "MaritalStatus", "EmploymentType", "HousingType"):
        code_list = doc.add_code_list(name=f"{col}Codes")
        add_codes(doc, code_list, sorted({row[col] for row in rows}))
        variables[col].set_coded(code_list)

    doc.add_concept(name="Population")
    doc.add_concept(name="Labour")
    doc.add_universe(name="All persons usually resident in private dwellings")
    variables["Occupation"].set_property("classification", "ISCO-08")
    variables["AnnualIncome"].set_property("referencePeriod", "Calendar year 2023")

    # Le flux : tout le monde répond à la section personne ; la section travail a un filtre
    AGE_GATE = "Age >= 15"


    def ask(col):
        return doc.add_item(
            QuestionConstruct, name=col, question_reference=questions[col].to_reference()
        )


    person = doc.add_item(
        Sequence,
        name="person",
        control_construct_references=[ask(c).to_reference() for c in ("Age", "Gender")],
    )
    labour = doc.add_item(
        Sequence,
        name="labour",
        control_construct_references=[
            ask(c).to_reference()
            for c in ("EmploymentType", "Occupation", "WeeklyHoursWorked")
        ],
    )
    gate = doc.add_item(IfThenElse, name="Working-age gate")
    gate.set_condition(AGE_GATE, description="Persons aged 15 and over")
    gate.then_construct_reference = labour.to_reference()
    main = doc.add_item(
        Sequence,
        name="Census flow",
        control_construct_references=[person.to_reference(), gate.to_reference()],
    )
    instrument = doc.add_item(Instrument, name="Census 2024 questionnaire")
    instrument.control_construct_reference = main.to_reference()

    # La spécification du même flux. Une personne sans âge saute la section travail.
    Path("census.spec.yaml").write_text(
        """\
    spec: census-2024
    version: "1"
    modules:
      - id: person
        questions:
          - id: Age
            domain: {numeric: {min: 0, max: 120, decimals: 0}}
      - id: labour
        gate: Age >= 15
        questions:
          - id: EmploymentType
            domain: {text: {max_length: 40}}
          - id: Occupation
            domain: {text: {max_length: 60}}
          - id: WeeklyHoursWorked
            domain: {numeric: {min: 0, max: 168, decimals: 0}}
    """,
        encoding="utf-8",
    )
    spec = load_spec("census.spec.yaml")
    print(f"Gates agree: {equivalent(spec.module('labour').gate_text, AGE_GATE)}")
    # -> Gates agree: True

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v1: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    doc.save("census-v1.xml")

    # Version 1.1 : une question ajoutée
    q_internet = doc.add_question(
        text="Avez-vous accès à Internet haute vitesse ?", lang="fr"
    )
    doc.add_variable(name="HighSpeedInternet", question=q_internet)
    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(rationale("Added internet access question"))
    study.version_responsibility = "Census Content Team"
    doc.save("census-v1.1.xml")

    # Version 2.0 : cinq questions ajoutées, trois retirées avec leurs variables
    for texte in [
        "Quelle langue parlez-vous le plus souvent à la maison ?",
        "Vous identifiez-vous comme Autochtone ?",
        "Quel est votre plus haut diplôme ?",
        "Avez-vous une incapacité ?",
        "Quel est le revenu annuel de votre ménage ?",
    ]:
        doc.add_question(text=texte, lang="fr")
    for col in ("Province", "MaritalStatus", "HousingType"):
        doc.remove(variables[col].identifier)
        doc.remove(questions[col].identifier)
    study.increment_major_version()
    study.version_rationales = [
        rationale("Major redesign: added equity and income questions")
    ]

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v2: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    # -> v2: 0 validation errors, 0 lint errors
    doc.save("census-v2.xml")
    ```

---

## Présentez votre projet

**(O6)** Terminez par une présentation de 5 minutes à votre groupe. Si vous travaillez seul, rédigez le même contenu dans une note d'une page. Suivez cet ordre :

1. **Les données et leurs lecteurs** (30 secondes) : ce que sont les données, et qui lira les métadonnées.
2. **Le plan** (1 minute) : montrez le tableau de votre plan, et dites de quelles techniques votre piste avait besoin.
3. **La preuve** (1 minute) : exécutez `ddi validate` sur votre dernier fichier. Montrez un endroit du XML où votre technique est consignée, comme une `SourceVariableReference`, une `Comparison`, une `UserAttributePair` ou un `IfThenElse`.
4. **Deux choix de conception** (2 minutes) : pour chacun, dites ce que vous avez choisi, l'option écartée, et pourquoi.
5. **Une chose que vous changeriez** la prochaine fois (30 secondes).

Des choix qui valent la peine d'être justifiés :

- Codé ou texte libre pour une colonne comme Program ou Occupation.
- Quelles colonnes ont une question, et lesquelles sont attribuées ou calculées.
- Une version mineure ou majeure pour votre changement.
- Un champ personnalisé, ou un champ que DDI possède déjà.
- Ce que fait un filtre quand la réponse qu'il teste manque (Piste D).

---

## Liste de vérification du projet de synthèse (pour toutes les pistes)

Utilisez cette liste de vérification pour vous assurer que votre projet est complet :

- [ ] Un plan écrit couvre chaque colonne (Piste C : chaque fichier) et nomme les techniques de votre piste.
- [ ] Le document part d'un fichier CSV ou Excel (Piste C : des fichiers DDI que vous avez reçus).
- [ ] Chaque variable à laquelle un répondant a répondu est liée à sa question.
- [ ] Les colonnes codées utilisent des listes de codes avec catégories.
- [ ] Au moins un concept et un univers sont définis.
- [ ] Des propriétés personnalisées sont définies sur au moins 2 éléments.
- [ ] Flux de questionnaire (Piste D) : un `Instrument` pointe vers une `Sequence` principale qui contient un filtre `IfThenElse`.
- [ ] Traçabilité (Pistes A et B) : chaque variable dérivée liste ses sources dans `source_variable_references`.
- [ ] Couplage (Piste B) : le registre est une seconde étude, la clé est marquée des deux côtés, et une `Comparison` met les clés en correspondance.
- [ ] Champs personnalisés (Piste C) : chaque clé vient de votre catalogue, et l'audit compte les éléments qui en portent une.
- [ ] Spécification (Piste D) : la spécification passe `ddi spec validate`, et son filtre correspond à celui de l'instrument.
- [ ] La version a été augmentée au moins une fois avec une justification et un responsable.
- [ ] Le document passe `doc.validate()` et `doc.lint()` sans erreur.
- [ ] Chaque fichier enregistré passe `ddi validate`.
- [ ] Deux choix de conception sont prêts à être présentés.

---

## Grille d'auto-évaluation

Utilisez ce tableau pour noter votre propre travail, ou celui d'un partenaire. La grille mesure les six objectifs de ce module sur les données de votre piste. Le score maximum est de 100 points.

| Critères | Objectif | Modules | Points |
| --- | --- | --- | ---: |
| Un plan, écrit avant le code, couvre chaque colonne et nomme les techniques de votre piste | O1 | 8 | 10 |
| Chaque colonne demandée est une variable liée à sa question ; les colonnes attribuées et calculées n'en ont pas | O2 | 4, 8 | 10 |
| Au moins un concept et un univers | O2 | 5 | 5 |
| Les colonnes codées utilisent des listes de codes avec catégories | O2 | 9 | 10 |
| Des propriétés personnalisées sur au moins 2 éléments | O2 | 13 | 5 |
| Aucune erreur de `doc.validate()`, `doc.lint()` ou `ddi validate` sur aucun fichier enregistré | O3 | 3, 7, 13 | 15 |
| Les techniques de votre piste (tableau suivant) | O4 | 10, 11, 12, 14, 16 | 20 |
| Un changement de version avec justification et responsable, chaque version dans son propre fichier | O5 | 15 | 10 |
| Une présentation de 5 minutes qui justifie deux choix de conception face aux options écartées | O6 | Tous | 15 |

**Techniques de la piste (20 points).** Notez seulement les lignes de votre piste. Les points de chaque piste totalisent 20. Accordez la moitié des points quand une technique est présente mais incomplète, par exemple une variable dérivée qui ne liste qu'une de ses deux sources.

| Technique | Module | Tous les points quand | A | B | C | D |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Flux de questionnaire | 10 | Un `Instrument` pointe vers une `Sequence` principale, et un filtre `IfThenElse` achemine au moins une section | - | - | - | 10 |
| Traçabilité | 11 | Chaque variable dérivée liste toutes ses variables sources dans `source_variable_references` | 20 | 10 | - | - |
| Couplage | 12 | Les deux sources sont des études dans un même document, la clé est marquée des deux côtés, une `Comparison` met les clés en correspondance, et la méthode est consignée | - | 10 | - | - |
| Champs personnalisés | 14 | Chaque clé vient d'un catalogue écrit avec un seul espace de noms, et un audit compte les éléments qui les portent | - | - | 20 | - |
| Spécification | 16 | La spécification passe `ddi spec validate`, ses filtres correspondent à ceux de l'instrument (`equivalent()`), et le plan dit ce que fait chaque filtre quand une réponse manque | - | - | - | 10 |

**Guide de notation :**

- **90-100 :** Excellent. Vous savez mener des données d'un fichier à un document DDI valide et versionné, consigner ce dont votre piste a besoin et expliquer vos choix. La grille vérifie ces compétences sur un seul jeu de données ; elle ne teste pas toutes les parties de `ddi-l`.
- **70-89 :** Bien. Pour chaque ligne où vous avez perdu des points, revoyez les modules indiqués à côté.
- **50-69 :** Besoin de pratique. Refaites les exercices des modules indiqués à côté de vos lignes les plus faibles, puis réessayez.
- **Moins de 50 :** Commencez par la Piste A et suivez les étapes lentement.

---

## Questions de réflexion

Ce sont des questions ouvertes. Il n'y a pas de bonne ou de mauvaise réponse. Écrivez vos réflexions dans un cahier ou discutez-en avec votre groupe.

1. **Quelle a été la partie la plus difficile de la construction de votre document DDI ? Que feriez-vous différemment la prochaine fois ?**

2. **Comment expliqueriez-vous DDI à un collègue qui n'en a jamais entendu parler ?** Essayez de le décrire en deux ou trois phrases simples.

3. **Quelle partie de l'API `ddi-l` avez-vous utilisée le plus ? Pourquoi ?** Pensez aux méthodes que vous avez appelées encore et encore, et à ce que cela vous dit sur votre façon de travailler.

---

## Faites le point

- [ ] Je peux rédiger un plan qui donne à chaque colonne de mon jeu de données sa question (ou la raison de son absence), son type et sa liste de codes, et qui nomme les techniques dont ma piste a besoin. (O1)
- [ ] Je peux construire le document DDI à partir des données, avec chaque colonne demandée liée à sa question, des listes de codes avec catégories, des concepts et un univers. (O2)
- [ ] Je peux n'obtenir aucune erreur de `doc.validate()`, `doc.lint()` et `ddi validate` sur chaque fichier que j'enregistre. (O3)
- [ ] Je peux consigner le flux, la traçabilité, le couplage, les champs personnalisés ou la spécification dont ma piste a besoin, et montrer où ils se trouvent dans le XML. (O4)
- [ ] Je peux versionner un changement avec une justification et un responsable, et garder chaque version dans son propre fichier. (O5)
- [ ] Je peux présenter mon projet en 5 minutes et justifier deux choix de conception face aux options que j'ai écartées. (O6)

---

!!! tip "Notes pour l'instructeur"
    - **Laissez les apprenants choisir leur piste.** Le choix libre augmente
      l'engagement. Si le groupe est mixte (étudiants, chercheurs,
      archivistes, personnel des INS), encouragez les petits groupes par
      rôle.
    - **Le plan d'abord.** Demandez à voir chaque plan avant que les
      apprenants écrivent du code. Dix minutes sur le plan épargnent une
      demi-heure de reprise.
    - **Gestion du temps.** La Piste A prend environ 60 minutes. Les Pistes
      B et D peuvent prendre 90 minutes ou plus, car elles consignent deux
      techniques chacune. Fixez les attentes au début et laissez les plus
      rapides aider les plus lents.
    - **Évaluation par les pairs.** Après que les apprenants ont terminé,
      mettez-les par deux pour évaluer les livrables de l'autre. Chaque
      évaluateur devrait exécuter `ddi validate` sur les fichiers de l'autre
      personne et les noter avec la grille.
    - **Présentation.** Terminez par les présentations : 2 à 3 apprenants
      partagent leur écran et suivent les cinq parties de « Présentez votre
      projet ». Concentrez-vous sur les choix de conception, pas seulement
      sur ce qu'ils ont construit.
    - **Problèmes courants :** Les apprenants oublient souvent de lier les
      variables aux questions, sautent la justification de version, ou
      ajoutent une seconde justification à une étude qui en a déjà une (une
      version contient une seule justification, et le fichier échoue à la
      validation). La liste de vérification aide à détecter ces oublis.
    - **Extension :** Les apprenants avancés peuvent essayer une deuxième
      piste ou combiner des éléments de deux pistes (par exemple, le
      couplage de la Piste B avec les scripts bash de la Piste D).
    - **Célébration.** C'est le dernier module. Reconnaissez l'effort que
      les apprenants ont fourni. Distribuez des certificats ou des badges
      si votre organisation le permet.
