---
description: >-
  Module 16 du cours ddi-l : quatre projets de synthèse, pour étudiants,
  chercheurs, archivistes et personnel d'organismes statistiques.
---

# Module 16 : Projets de synthèse

!!! info "Ce que vous apprendrez"
    - Combiner tout ce que vous avez appris dans les modules 1 à 15 en un projet complet.
    - Construire un document DDI à partir d'un fichier CSV ou Excel.
    - Ajouter des variables, des questions, des concepts, des univers et des listes de codes.
    - Définir des propriétés personnalisées sur les éléments.
    - Versionner votre document et enregistrer une justification.
    - Valider et enregistrer le XML final.

**Prérequis :** Tous les modules précédents (1 à 15).

**Durée :** 60 à 90 min en autonomie / 90 min avec instructeur.

---

## Introduction

Vous avez maintenant appris tous les outils. Vous savez comment créer des documents DDI, ajouter des métadonnées, valider des fichiers, gérer les versions et utiliser la ligne de commande. Il est maintenant temps de tout rassembler dans un vrai projet.

Choisissez la **piste** qui correspond à votre rôle. Chaque piste vous guide à travers un processus complet : partir d'un fichier de données, construire les métadonnées DDI, les versionner, les valider et enregistrer le résultat final.

Si vous ne savez pas quelle piste choisir, essayez la **Piste A** (Étudiant universitaire). C'est le point de départ le plus simple.

---

## Piste A : Étudiant universitaire : Documenter le jeu de données de votre mémoire

!!! example "Scénario"
    Vous venez de terminer votre mémoire sur le stress étudiant. Votre jeu
    de données comporte 10 colonnes. Vous devez créer un document DDI pour
    que le dépôt de recherche de votre université puisse cataloguer vos
    données.

### Étapes

1. **Partez d'un fichier CSV** avec au moins 10 colonnes. Téléchargez le jeu de données de mémoire d'exemple (40 étudiants, 12 colonnes) ou utilisez le vôtre.

    [:material-download: Télécharger `thesis-data.csv`](thesis-data.csv){ .md-button download="thesis-data.csv" }

2. **Créez une étude DDI :**

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(
        title="Student Stress Survey 2024",
        agency="university.example.org",
    )
    ```

3. **Ajoutez des variables** à partir de vos colonnes CSV. Créez une variable pour chaque colonne. Liez chaque variable à la question dont elle provient ; un identifiant, comme un numéro d'étudiant, est attribué et non demandé, et n'a pas besoin de question.

    ```python
    q1 = doc.add_question(text="How many hours do you study per day?")
    v1 = doc.add_variable(name="StudyHours", question=q1)
    # Repeat for each column...
    ```

4. **Ajoutez 3 concepts et 1 univers :**

    ```python
    c1 = doc.add_concept(name="Academic Workload")
    c2 = doc.add_concept(name="Mental Health")
    c3 = doc.add_concept(name="Demographics")
    u1 = doc.add_universe(name="Undergraduate students aged 18-25")
    ```

5. **Définissez des propriétés personnalisées** sur au moins 2 éléments. Une propriété personnalisée est une métadonnée supplémentaire que vous définissez vous-même, comme une source de données ou une date de collecte.

    ```python
    v1.set_property("dataSource", "Online survey via Qualtrics")
    v1.set_property("collectionDate", "2024-03-15")
    ```

6. **Enregistrez en version 1.0 :**

    ```python
    doc.save("thesis-v1.xml")
    ```

7. **Mettez à jour le document.** Ajoutez une nouvelle variable d'analyse (par exemple, « StressIndex » qui combine plusieurs colonnes). Augmentez la version à 1.1 et ajoutez une justification.

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    q_new = doc.add_question(text="Computed: overall stress index")
    v_new = doc.add_variable(name="StressIndex", question=q_new)

    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added computed stress index variable")]
        )
    )
    study.version_responsibility = "Thesis Author"
    ```

8. **Validez et enregistrez en version 1.1 :**

    ```python
    errors = doc.validate()
    if not errors:
        doc.save("thesis-v1.1.xml")
        print("Saved thesis-v1.1.xml")
    else:
        print("Errors:", errors)
    ```

### Livrables

- `thesis-v1.xml` : document DDI valide avec 10+ variables.
- `thesis-v1.1.xml` : version mise à jour avec la nouvelle variable et une justification.

??? success "Exemple de solution"
    Un script complet pour toutes les étapes ci-dessus, avec
    [`thesis-data.csv`](thesis-data.csv){ download="thesis-data.csv" }.

    ```python
    import csv
    import ddi_l as ddi
    from ddi_l.models.base import VersionRationale, InternationalString

    # Read CSV
    with open("thesis-data.csv") as f:
        columns = csv.DictReader(f).fieldnames

    # Create v1.0
    doc = ddi.new_study(title="Thesis Dataset", agency="university.edu")
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
    for col in columns:
        libelle = QUESTIONS.get(col)
        q = doc.add_question(text=libelle, lang="fr") if libelle else None
        v = doc.add_variable(name=col, question=q)
        v.set_property("source", "Primary survey data")

    doc.add_concept(name="Demographics")
    doc.add_concept(name="Academic Performance")
    doc.add_concept(name="Well-Being")
    doc.add_universe(name="Undergraduate students at University X")

    doc.save("thesis-v1.xml")
    issues = doc.validate()
    print(f"v1 valid: {not issues}")

    # Update to v1.1
    doc = ddi.open_ddi("thesis-v1.xml")
    q_new = doc.add_question(text="What is the student's GPA?")
    v_new = doc.add_variable(name="GPA", question=q_new)

    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added GPA variable for analysis")]
        )
    )
    study.version_responsibility = "Thesis Author"
    doc.save("thesis-v1.1.xml")
    print(f"v1.1 valid: {not doc.validate()}")
    ```

---

## Piste B : Chercheur : Préparer une enquête de santé pour publication

!!! example "Scénario"
    Vous dirigez une étude de santé multi-pays. Votre fichier Excel comporte
    15 colonnes de données d'enquête. Vous devez préparer les métadonnées
    pour un dépôt de données ouvertes.

### Étapes

1. **Partez d'un fichier de données** avec au moins 15 colonnes. Téléchargez l'enquête de santé d'exemple (40 répondants, 15 colonnes) ou utilisez la vôtre, et lisez le nom de ses colonnes :

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

    Si vos données sont dans un classeur Excel, lisez plutôt le nom des colonnes avec pandas (voir le [Module 8](module-08-csv-to-ddi.md)) :

    <!-- docs-test: skip -- needs pandas and a workbook the reader supplies -->
    ```python
    import pandas as pd

    columns = list(pd.read_excel("health-survey.xlsx").columns)
    ```

2. **Générez automatiquement les variables** à partir des colonnes :

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
    for col in columns:
        q = doc.add_question(text=QUESTIONS[col], lang="fr") if col in QUESTIONS else None
        v = doc.add_variable(name=col, question=q)
    ```

3. **Ajoutez 4 concepts :**

    ```python
    doc.add_concept(name="Physical Health")
    doc.add_concept(name="Mental Health")
    doc.add_concept(name="Access to Healthcare")
    doc.add_concept(name="Demographics")
    ```

4. **Ajoutez 2 listes de codes** générées automatiquement à partir des valeurs uniques des colonnes. Une **liste de codes** est un ensemble de réponses permises (comme « Oui », « Non », « Incertain »).

    ```python
    cl1 = doc.add_code_list(name="SmokingStatus")
    cl2 = doc.add_code_list(name="ExerciseFrequency")
    ```

5. **Validez le document :**

    ```python
    errors = doc.validate()
    print("Valid" if not errors else errors)
    ```

6. **Enregistrez en version 1.0 :**

    ```python
    doc.save("health-survey-v1.xml")
    ```

7. **Exportez en JSON** depuis la ligne de commande :

    ```bash
    ddi to-json health-survey-v1.xml --indent 2 > health-survey-v1.json
    ```

8. **Mettez à jour en version 1.1** avec une justification. Ajoutez une nouvelle variable ou corrigez un libellé.

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    doc.add_question(text="How often do you visit a dentist?")
    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added dental visit frequency question")]
        )
    )
    doc.save("health-survey-v1.1.xml")
    ```

### Livrables

- `health-survey-v1.xml` : document DDI valide.
- `health-survey-v1.json` : export JSON du document.
- `health-survey-v1.1.xml` : version mise à jour avec justification.

---

## Piste C : Archiviste : Enrichir et versionner des fichiers DDI existants

!!! example "Scénario"
    Vous gérez une collection de données dans une bibliothèque nationale.
    Vous recevez 3 fichiers DDI de différentes équipes de recherche. Certains
    fichiers manquent de métadonnées. Vous devez vérifier chaque fichier,
    ajouter ce qui manque et créer de nouvelles versions.

### Étapes

1. **Préparez 3 fichiers DDI.** Utilisez des fichiers des modules précédents, ou créez 3 petites études maintenant :

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

2. **Pour chaque fichier, vérifiez la complétude.** Ouvrez le fichier et listez ce qu'il contient :

    ```python
    doc = ddi.open_ddi("study-1.xml")
    print(f"Questions:  {len(doc.questions)}")
    print(f"Variables:  {len(doc.variables)}")
    print(f"Concepts:   {len(doc.concepts)}")
    print(f"Universes:  {len(doc.universes)}")
    print(f"Code lists: {len(doc.code_lists)}")
    ```

3. **Ajoutez les métadonnées manquantes.** Si un fichier n'a pas de concepts, ajoutez-en un. S'il n'a pas d'univers, ajoutez-en un. Si les variables n'ont pas de questions liées, ajoutez des questions et recréez les variables.

    ```python
    doc.add_concept(name="Social Sciences")
    doc.add_universe(name="General population")
    cl = doc.add_code_list(name="YesNo")
    ```

4. **Augmentez la version avec une justification :**

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Enriched metadata: added concept, universe, and code list"
                )
            ]
        )
    )
    study.version_responsibility = "Archive Metadata Team"
    ```

5. **Validez et enregistrez :**

    ```python
    errors = doc.validate()
    if not errors:
        doc.save("study-1-enriched.xml")
    ```

6. **Répétez pour les 3 fichiers.**

### Livrables

- 3 fichiers XML mis à jour (`study-1-enriched.xml`, `study-2-enriched.xml`, `study-3-enriched.xml`), tous valides, chacun avec une justification de version.

---

## Piste D : Personnel des INS : Construire un instrument de recensement

!!! example "Scénario"
    Vous travaillez dans un bureau national de statistique. Votre équipe de
    recensement possède un grand fichier CSV avec 20+ colonnes. Vous devez
    construire un document DDI complet, créer des listes de codes à partir
    des données, gérer plusieurs versions et automatiser la validation avec
    un script bash.

### Étapes

1. **Partez d'un grand CSV** avec 20+ colonnes. Téléchargez l'extrait de recensement d'exemple (20 ménages, 22 colonnes, dont les cinq colonnes catégorielles utilisées à l'étape 3) ou utilisez le vôtre.

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

2. **Créez 20+ variables** à partir des colonnes du CSV :

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
    for col in columns:
        q = doc.add_question(text=QUESTIONS[col], lang="fr") if col in QUESTIONS else None
        v = doc.add_variable(name=col, question=q)
    ```

3. **Construisez 5 listes de codes** générées automatiquement à partir des valeurs uniques des colonnes :

    ```python
    categorical_cols = [
        "Province",
        "Gender",
        "MaritalStatus",
        "EmploymentType",
        "HousingType",
    ]
    for col in categorical_cols:
        cl = doc.add_code_list(name=f"{col}Codes")
    ```

4. **Définissez des propriétés personnalisées** pour les codes de classification sur au moins 2 éléments :

    ```python
    v = doc.variables[0]
    v.set_property("classificationCode", "NAICS-2022")
    v.set_property("statisticalProgram", "Census of Population")
    ```

5. **Enregistrez en version 1.0 :**

    ```python
    doc.save("census-v1.xml")
    ```

6. **Mettez à jour en version 1.1** : ajoutez une nouvelle question et variable :

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    doc.add_question(text="Do you have access to high-speed internet?")
    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added internet access question")]
        )
    )
    doc.save("census-v1.1.xml")
    ```

7. **Mettez à jour en version 2.0** : refonte majeure (ajoutez 5 nouvelles questions, retirez-en 3 anciennes). Retirer une question retire aussi les variables qui enregistraient ses réponses ; sinon, elles continueraient de pointer vers une question qui n'est plus dans le fichier (voir le [Module 15](module-15-update-and-version.md)) :

    ```python
    # Add new questions
    for text in [
        "What is your primary language at home?",
        "Do you identify as Indigenous?",
        "What is your highest degree?",
        "Do you have a disability?",
        "What is your annual household income?",
    ]:
        doc.add_question(text=text)

    # Retire 3 old questions, and the variables that recorded their answers
    for q in doc.questions[:3]:
        for v in doc.variables:
            if any(ref.identifier == q.identifier for ref in v.question_references):
                doc.remove(v.identifier)
        doc.remove(q.identifier)

    study.increment_major_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Major redesign: added equity and income questions"
                )
            ]
        )
    )
    errors = [finding for finding in doc.lint() if finding.severity == "error"]
    print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
    doc.save("census-v2.xml")
    ```

8. **Validation par lots** des trois fichiers depuis la ligne de commande :

    ```bash
    ddi validate census-v1.xml
    ddi validate census-v1.1.xml
    ddi validate census-v2.xml
    ```

9. **Écrivez un script bash** qui exécute le pipeline complet :

    ```bash
    #!/bin/bash
    # validate.sh: validate all census DDI files.

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

- `census-v1.xml` : version 1.0, valide.
- `census-v1.1.xml` : version 1.1, valide, avec justification.
- `census-v2.xml` : version 2.0, valide, avec justification.
- `validate.sh` : script bash qui valide tous les fichiers.

---

## Liste de vérification du projet de synthèse (pour toutes les pistes)

Utilisez cette liste de vérification pour vous assurer que votre projet est complet :

- [ ] Le document part d'un fichier CSV ou Excel.
- [ ] Chaque variable à laquelle un répondant a répondu est liée à sa question.
- [ ] Au moins un concept et un univers sont définis.
- [ ] Des propriétés personnalisées sont définies sur au moins 2 éléments.
- [ ] La version a été augmentée au moins une fois avec une justification.
- [ ] Le document passe `doc.validate()` sans erreur.
- [ ] Le XML final est enregistré sur le disque.

---

## Grille d'auto-évaluation

Utilisez ce tableau pour noter votre propre travail. Le score maximum est de 100 points (plus 10 points bonus).

| Critères                              | Points |
| ------------------------------------- | -----: |
| XML valide en sortie                  |     20 |
| Variables liées aux questions         |     15 |
| Concepts et univers présents          |     15 |
| Listes de codes avec catégories       |     15 |
| Propriétés personnalisées utilisées   |     10 |
| Gestion de version avec justification |     15 |
| Bonus : validation CLI ou export JSON |     10 |

**Guide de notation :**

- **90-110 :** Excellent. Vous maîtrisez `ddi-l`.
- **70-89 :** Bien. Revoyez les domaines où vous avez perdu des points.
- **50-69 :** Besoin de pratique. Retournez aux modules concernés et réessayez.
- **Moins de 50 :** Commencez par la Piste A et suivez les étapes lentement.

---

## Questions de réflexion

Ce sont des questions ouvertes. Il n'y a pas de bonne ou de mauvaise réponse. Écrivez vos réflexions dans un cahier ou discutez-en avec votre groupe.

1. **Quelle a été la partie la plus difficile de la construction de votre document DDI ? Que feriez-vous différemment la prochaine fois ?**

2. **Comment expliqueriez-vous DDI à un collègue qui n'en a jamais entendu parler ?** Essayez de le décrire en deux ou trois phrases simples.

3. **Quelle partie de l'API `ddi-l` avez-vous utilisée le plus ? Pourquoi ?** Pensez aux méthodes que vous avez appelées encore et encore, et à ce que cela vous dit sur votre façon de travailler.

---

!!! tip "Notes pour l'instructeur"
    - **Laissez les apprenants choisir leur piste.** Le choix libre augmente
      l'engagement. Si le groupe est mixte (étudiants, chercheurs,
      archivistes, personnel des INS), encouragez les petits groupes par
      rôle.
    - **Gestion du temps.** La Piste A prend environ 60 minutes. La Piste D
      peut prendre 90 minutes ou plus. Fixez les attentes au début et
      laissez les plus rapides aider les plus lents.
    - **Évaluation par les pairs.** Après que les apprenants ont terminé,
      mettez-les par deux pour évaluer les livrables de l'autre. Chaque
      évaluateur devrait exécuter `ddi validate` sur les fichiers de l'autre
      personne et vérifier la grille.
    - **Présentation.** Terminez par une présentation de 5 minutes où 2 à 3
      apprenants partagent leur écran et expliquent leur projet. Concentrez-vous
      sur ce qu'ils ont appris, pas seulement sur ce qu'ils ont construit.
    - **Problèmes courants :** Les apprenants oublient souvent de lier les
      variables aux questions, ou sautent la justification de version. La
      liste de vérification aide à détecter ces oublis.
    - **Extension :** Les apprenants avancés peuvent essayer une deuxième
      piste ou combiner des éléments de deux pistes (par exemple, la
      génération automatique de la Piste B avec les scripts bash de la
      Piste D).
    - **Célébration.** C'est le dernier module. Reconnaissez l'effort que
      les apprenants ont fourni. Distribuez des certificats ou des badges
      si votre organisation le permet.
