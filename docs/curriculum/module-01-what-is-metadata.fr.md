---
description: >-
  Module 1 du cours ddi-l : ce que sont les métadonnées, pourquoi la
  documentation compte, les principes FAIR et la place du DDI.
---

# Module 1 : Qu'est-ce que les métadonnées et pourquoi sont-elles importantes ?

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Définir les métadonnées en une phrase et désigner deux
      métadonnées qui décrivent un tableau donné.
    - **O2.** Énumérer trois questions auxquelles un lecteur doit répondre
      avant d'utiliser un tableau non documenté.
    - **O3.** Décrire ce qu'est DDI en deux phrases et nommer deux types
      d'organisations qui l'utilisent.
    - **O4.** Associer chaque principe FAIR à une façon dont les métadonnées
      DDI le soutiennent.
    - **O5.** Indiquer ce que fait `ddi-l` et une chose qu'il ne fait pas.

**Prérequis :** Aucun.

**Durée :** 30 min en autonomie / 45 min avec instructeur.

**Nouveau dans ce module :** aucune fonction ni commande pour l'instant. Ce
module pose les idées sur lesquelles s'appuie le reste du cours.

---

## 1. Qu'est-ce que les métadonnées ?

Les métadonnées sont des **informations sur vos données**. Pensez au catalogue
d'une bibliothèque. Le catalogue ne contient pas le texte complet de chaque
livre. Il vous donne le titre, l'auteur, le sujet et l'emplacement de chaque
livre. Les métadonnées font la même chose pour les fichiers de données. Elles
vous disent de quoi parlent les données sans vous montrer toutes les données.

Voici quelques exemples de métadonnées :

- Le titre d'une enquête.
- La date de collecte des données.
- La signification de chaque colonne dans un tableau.

Sans métadonnées, un fichier de données n'est qu'un ensemble de lignes et de
colonnes de chiffres. Personne ne sait ce que ces chiffres veulent dire.

---

## 2. Exemple concret : un tableau d'enquête auprès des ménages

Regardez le tableau ci-dessous. Il provient d'une enquête auprès des ménages.

| Colonne A | Colonne B | Colonne C |
| --------: | --------- | --------: |
|        34 | Female    |    52 000 |
|        28 | Male      |    41 000 |
|        45 | Female    |    67 000 |
|        22 | Male      |    29 000 |
|        51 | Other     |    73 000 |

**Sans documentation**, vous pourriez vous demander :

- Que signifient les chiffres de la colonne A ? Des âges ? Des numéros d'identification ?
- La colonne C est-elle en dollars, en euros ou dans une autre devise ?
- Qui a été interrogé ? Seulement les adultes ? Tout le monde ?
- Quand l'enquête a-t-elle été réalisée ?

**Avec de la documentation**, on ajoute des métadonnées :

| Âge | Genre  | Revenu annuel (CAD) |
| --: | ------ | ------------------: |
|  34 | Female |              52 000 |
|  28 | Male   |              41 000 |
|  45 | Female |              67 000 |
|  22 | Male   |              29 000 |
|  51 | Other  |              73 000 |

- **Titre de l'étude :** Enquête canadienne sur le revenu des ménages 2024
- **Population :** Adultes canadiens de 18 ans et plus.
- **Période de collecte :** Janvier-mars 2024.

Maintenant, les données ont du sens. Les métadonnées font la différence entre
la confusion et la clarté.

---

## 3. Qu'est-ce que DDI ?

**DDI** signifie **Data Documentation Initiative** (Initiative de documentation
des données). C'est une norme internationale (un ensemble de règles convenues)
pour décrire les enquêtes, les recensements et les jeux de données. Les
gouvernements, les universités et les organismes de recherche du monde entier
utilisent DDI pour documenter leurs données afin que d'autres puissent les
trouver, les comprendre et les réutiliser.

Points clés sur DDI :

- Il est maintenu par la [DDI Alliance](https://ddialliance.org).
- Il utilise le XML (un format de texte structuré) pour stocker la documentation.
- Il couvre toute la vie d'un jeu de données, de la planification et la
  collecte jusqu'à l'archivage et le partage.

---

## 4. Comment DDI rend les données FAIR

**FAIR** est un ensemble de quatre principes qui aident les gens à partager et
réutiliser les données. Les lettres signifient **Findable** (Trouvable),
**Accessible**, **Interoperable** (Interopérable) et **Re-usable**
(Réutilisable). De bonnes données devraient respecter les quatre principes.
DDI-Lifecycle vous aide à atteindre chacun d'entre eux.

| Principe | Ce que cela signifie | Comment DDI aide |
| ---------- | --------------------- | ----------------- |
| **Trouvable** | Les gens peuvent chercher et découvrir les données. | DDI donne à chaque élément un identifiant unique et stocke des champs structurés comme le titre, l'agence et les concepts. Les catalogues de données peuvent indexer ces champs pour que les utilisateurs trouvent votre jeu de données dans une recherche. |
| **Accessible** | Les gens peuvent obtenir les données et leur documentation. | Les fichiers DDI sont du XML standard. Tout outil capable de lire le XML peut les ouvrir. Aucun logiciel spécial n'est nécessaire. |
| **Interopérable** | Les données fonctionnent avec d'autres données et outils. | DDI utilise des listes de codes partagées et des vocabulaires contrôlés. Quand deux enquêtes utilisent la même liste de codes pour le genre ou le statut d'emploi, leurs données peuvent être combinées et comparées. |
| **Réutilisable** | Les gens comprennent assez bien les données pour les utiliser correctement. | DDI enregistre qui a collecté les données, quand, comment et ce que chaque variable signifie. Un chercheur dans un autre pays peut lire le fichier DDI et savoir exactement ce que les données contiennent. |

### Exemple : FAIR en action

Imaginez que le Dr. Chen publie une enquête sur la santé dans un dépôt de
données ouvert. Sans métadonnées DDI, un visiteur voit un fichier appelé
`health-2024.csv` et n'a aucune idée de ce qu'il contient.

Avec des métadonnées DDI :

- **Trouvable** : Le dépôt indexe le titre DDI, les concepts (« Santé
  physique », « Santé mentale ») et l'agence (« health-research.example.org »).
  Un étudiant qui cherche « données d'enquête sur la santé mentale » le trouve.
- **Accessible** : Le fichier DDI XML est publié à côté du CSV. N'importe qui
  peut télécharger les deux fichiers sans connexion ni outil spécial.
- **Interopérable** : Le fichier DDI utilise une liste de codes standard pour
  le genre (Male / Female / Other). Une autre équipe en France utilise la même
  liste de codes, ce qui permet de fusionner les deux jeux de données pour une
  analyse entre pays.
- **Réutilisable** : Le fichier DDI indique que les données ont été collectées
  auprès d'adultes de 18 ans et plus en 2024, que « bmi » est l'indice de masse
  corporelle en kg/m², et que le revenu est en dollars canadiens. Un nouveau
  chercheur peut utiliser les données correctement sans contacter l'équipe
  d'origine.

Sans DDI, les données restent dans un fichier que personne ne trouve, personne
ne comprend et personne ne réutilise. Avec DDI, les données deviennent une
ressource partagée.

---

## 5. Qu'est-ce que ddi-l ?

`ddi-l` est un **paquet Python** (un outil que vous installez et utilisez
dans le langage de programmation Python) qui vous permet de **créer, lire,
modifier et valider** des documents DDI. Vous n'avez pas besoin de connaître
le XML pour l'utiliser. Vous écrivez quelques lignes de Python, et `ddi-l`
s'occupe du XML pour vous.

Ce que `ddi-l` peut faire :

- **Créer** une nouvelle étude DDI avec des questions et des variables.
- **Lire** un fichier DDI existant et examiner son contenu.
- **Modifier** un document DDI en ajoutant ou en supprimant des éléments.
- **Valider** un document pour vérifier qu'il respecte les règles DDI.

Ce que `ddi-l` ne fait pas :

- Il ne **collecte** pas de réponses. Vous menez toujours votre enquête avec
  votre propre outil d'enquête ; `ddi-l` décrit l'enquête et ses données.
- Il n'**analyse** pas vos données. Il ne calcule ni moyennes ni tableaux à
  partir des valeurs de votre fichier de données. Il enregistre ce que ces
  valeurs signifient.

---

## 6. La vue d'ensemble

Voici le flux de travail habituel quand vous utilisez `ddi-l` :

```mermaid
flowchart LR
    A["Vos données\n(CSV / Excel)"] --> B["Votre script\n(Python + ddi-l)"]
    B --> C["Fichier DDI XML"]
    C --> D["Validation"]
    D --> E["Archivage / Publication"]
```

1. Vous partez d'un fichier de données (par exemple, un fichier CSV ou un tableur Excel).
2. Vous écrivez un court script Python qui utilise `ddi-l` pour décrire les données.
3. `ddi-l` crée un fichier DDI XML.
4. Vous validez le fichier pour vous assurer que tout est correct.
5. Vous archivez ou publiez le fichier pour que d'autres puissent trouver et comprendre vos données.

---

## 7. Qui utilise DDI ? Quatre histoires

**Maya, étudiante universitaire.**
Maya vient de terminer sa thèse sur le stress des étudiants. Elle doit déposer
ses données d'enquête dans le dépôt de recherche de son université. Les
métadonnées DDI aident les futurs étudiants à trouver et comprendre son jeu
de données.

**Dr. Chen, chercheur.**
Le Dr. Chen dirige une étude sur la santé dans plusieurs pays. Il publie ses
données dans un dépôt ouvert. DDI rend ses jeux de données faciles à trouver
et comparables d'un pays à l'autre.

**Fatima, archiviste.**
Fatima gère une collection de données dans une bibliothèque nationale. Elle
utilise DDI pour cataloguer des milliers de jeux de données afin que les
chercheurs puissent chercher et parcourir la collection.

**Jean-Pierre, personnel de l'institut national de statistique (INS).**
Jean-Pierre travaille dans un bureau de statistiques gouvernemental. Son
équipe documente chaque recensement et chaque enquête avec DDI pour que le
public puisse accéder à des données fiables et bien documentées.

---

## Exercices

!!! example "Scénario"
    Vous recevez un fichier de données sans documentation. Le fichier contient
    cinq lignes et les colonnes sont nommées A, B et C. Les valeurs ressemblent
    à des chiffres et des mots courts.

**Exercice 1 (O2).** Regardez le tableau ci-dessous.

| A  | B      |     C |
| -: | ------ | ----: |
| 34 | Female | 52000 |
| 28 | Male   | 41000 |
| 45 | Female | 67000 |
| 22 | Male   | 29000 |
| 51 | Other  | 73000 |

Notez **3 questions** auxquelles une nouvelle personne aurait besoin d'une
réponse avant de pouvoir utiliser ces données. Par exemple : que mesure la
colonne A ?

Résultat attendu : une liste de trois questions.

??? success "Réponse"
    Trois de ces questions, ou d'autres semblables :

    1. Que signifie chaque colonne ? (A est-elle un âge ? En années ou en mois ?)
    2. Dans quelle unité est la colonne C ? (Dollars ? Euros ? Par année ou par mois ?)
    3. Qui a été interrogé ? (Des étudiants ? Des adultes ? Tout le monde ?)
    4. Quand les données ont-elles été collectées ?

**Exercice 2 (O1).** La même chercheuse vous envoie maintenant la version
documentée d'un autre fichier :

> **Campus Sleep Study 2025.** Données collectées en septembre 2025 auprès
> d'étudiants de première année. `sleep_hrs` est le nombre d'heures de sommeil
> lors d'une soirée de cours typique.

| sleep_hrs |
| --------: |
|         7 |
|         6 |
|         8 |

1. Écrivez une définition des métadonnées en une phrase.
2. Nommez **deux métadonnées** de ce fichier, et **une donnée**.

Résultat attendu : une phrase, puis trois éléments courts.

??? success "Réponse"
    1. Les métadonnées sont des informations qui décrivent des données : ce
       qu'elles signifient, d'où elles viennent et comment elles ont été
       collectées.
    2. Métadonnées : deux éléments parmi le titre « Campus Sleep Study 2025 »,
       la date de collecte (septembre 2025), la population (étudiants de
       première année), le nom de colonne `sleep_hrs` ou sa signification
       (heures de sommeil lors d'une soirée de cours typique). Donnée : l'une
       des valeurs 7, 6 ou 8.

**Exercice 3 (O4).** Associez chaque principe FAIR (1 à 4) à la
caractéristique DDI (a à d) qui le soutient.

| Principe FAIR     | Caractéristique DDI |
| ----------------- | ------------------- |
| 1. Trouvable      | a. Le fichier DDI indique qui a été interrogé, quand, et ce que chaque variable signifie. |
| 2. Accessible     | b. Deux enquêtes utilisent la même liste de codes DDI pour le statut d'emploi. |
| 3. Interopérable  | c. Un catalogue de données indexe le titre, l'agence et les concepts stockés dans le fichier DDI. |
| 4. Réutilisable   | d. Le fichier DDI est du XML simple, publié à côté des données, que tout outil XML peut ouvrir. |

Résultat attendu : quatre paires, comme `1-?`.

??? success "Réponse"
    `1-c`, `2-d`, `3-b`, `4-a`.

    - **Trouvable (c) :** le catalogue ne peut trouver que ce qui est décrit
      dans des champs structurés.
    - **Accessible (d) :** un format standard et ouvert ne demande aucun
      logiciel spécial.
    - **Interopérable (b) :** une liste de codes partagée donne le même sens
      au même code dans les deux enquêtes, ce qui permet de combiner les
      données.
    - **Réutilisable (a) :** un nouvel utilisateur sait exactement ce que
      contiennent les données.

**Exercice 4 (O3).** Un nouveau collègue vous demande : « Qu'est-ce que
DDI ? » Écrivez une réponse en **deux phrases**. Nommez **deux types
d'organisations** qui l'utilisent.

Résultat attendu : deux phrases.

??? success "Réponse"
    Par exemple : « DDI, la Data Documentation Initiative, est une norme
    internationale pour décrire les enquêtes, les recensements et les jeux de
    données en XML. Les instituts nationaux de statistique, les archives de
    données, les universités et les équipes de recherche l'utilisent pour que
    d'autres puissent trouver, comprendre et réutiliser leurs données. »

    Deux de ces types d'organisations suffisent : instituts nationaux de
    statistique, archives de données ou bibliothèques nationales, universités
    et leurs dépôts de recherche, équipes de recherche.

**Exercice 5 (O5).** Pour chaque tâche ci-dessous, écrivez **oui** si
`ddi-l` la fait, ou **non** s'il ne la fait pas.

1. Écrire un fichier DDI XML à partir d'un court script Python.
2. Envoyer un questionnaire aux répondants et recueillir leurs réponses.
3. Vérifier un document DDI par rapport aux règles DDI.
4. Calculer le revenu moyen à partir des valeurs d'un fichier CSV.
5. Ouvrir un fichier DDI existant et lister ses questions.

Écrivez ensuite une phrase qui dit ce que fait `ddi-l` et une chose qu'il ne
fait pas.

Résultat attendu : cinq réponses, puis une phrase.

??? success "Réponse"
    Oui : 1, 3 et 5. Non : 2 et 4.

    Par exemple : « `ddi-l` crée, lit, modifie et valide des métadonnées DDI
    à partir de Python, mais il ne recueille pas les réponses d'enquête. »

---

## Quiz

???+ question "Question 1 (O1) : Un tableur contient une colonne intitulée `Age (years)` avec les valeurs 34, 28 et 45. Lequel de ces éléments est une métadonnée ?"
    **A.** La valeur 34.

    **B.** L'en-tête `Age (years)`, qui dit ce que les valeurs signifient et
    dans quelle unité elles sont exprimées.

    **C.** La somme des trois valeurs.

    **D.** La deuxième ligne.

    ??? success "Réponse"
        **B.** Les métadonnées sont des informations sur les données.
        L'en-tête vous dit ce que les chiffres signifient et comment ils sont
        mesurés. Les valeurs elles-mêmes, et tout ce qu'on en calcule, sont
        des données.

???+ question "Question 2 (O2) : Un collègue vous envoie un tableau avec les colonnes A, B et C, sans aucune note. La colonne C contient des valeurs comme 52000. Vous voulez publier le revenu moyen. À quelle question devez-vous d'abord répondre ?"
    **A.** Quelle police a servi à saisir le tableau ?

    **B.** Combien de lignes le fichier contient-il ?

    **C.** Quel est le nom du fichier ?

    **D.** Que mesure la colonne C, dans quelle devise et pour quelle période ?

    ??? success "Réponse"
        **D.** Sans savoir que C est un revenu, et s'il est en dollars ou en
        euros, par année ou par mois, toute moyenne publiée pourrait être
        fausse. Les autres questions ne changent pas le sens des chiffres.

???+ question "Question 3 (O3) : Quelle phrase décrit le mieux DDI ?"
    **A.** Une norme internationale pour décrire les enquêtes, les
    recensements et les jeux de données, utilisée par les instituts
    nationaux de statistique, les archives de données et les universités.

    **B.** Un outil d'enquête qui envoie des questionnaires aux répondants.

    **C.** Un paquet Python qui calcule des statistiques à partir de fichiers
    de données.

    **D.** Une base de données qui stocke les réponses d'enquête.

    ??? success "Réponse"
        **A.** DDI est une norme : un ensemble de règles convenues pour la
        documentation. L'option C confond DDI avec les outils ; `ddi-l` est
        un paquet Python qui travaille avec DDI, et il ne calcule pas de
        statistiques.

???+ question "Question 4 (O4) : Votre enquête et une enquête française utilisent la même liste de codes DDI pour le genre, ce qui permet de fusionner les deux jeux de données. Quel principe FAIR cela soutient-il le plus directement ?"
    **A.** Trouvable

    **B.** Accessible

    **C.** Interopérable

    **D.** Réutilisable

    ??? success "Réponse"
        **C.** Interopérable signifie que les données fonctionnent avec
        d'autres données. Une liste de codes partagée donne à chaque code le
        même sens dans les deux jeux de données, qui peuvent alors être
        combinés et comparés.

???+ question "Question 5 (O4) : Un catalogue de données lit le titre, l'agence et les concepts de votre fichier DDI, si bien qu'une recherche sur 'enquête santé mentale' affiche votre jeu de données. Quel principe FAIR cela soutient-il ?"
    **A.** Trouvable

    **B.** Accessible

    **C.** Interopérable

    **D.** Réutilisable

    ??? success "Réponse"
        **A.** Trouvable signifie que les gens peuvent découvrir les données.
        Les champs DDI structurés donnent aux catalogues une base fiable à
        indexer et à interroger.

???+ question "Question 6 (O5) : Laquelle de ces tâches ddi-l NE fait-il PAS ?"
    **A.** Créer une étude DDI à partir d'un script Python.

    **B.** Recueillir les réponses des répondants à une enquête.

    **C.** Valider un document DDI par rapport aux règles DDI.

    **D.** Ouvrir un fichier DDI existant et examiner son contenu.

    ??? success "Réponse"
        **B.** `ddi-l` travaille avec des métadonnées : il crée, lit, modifie
        et valide des documents DDI. Recueillir des réponses est le rôle d'un
        outil d'enquête.

---

## Faites le point

- [ ] Je peux définir les métadonnées en une phrase et désigner deux
  métadonnées qui décrivent un tableau. (O1)
- [ ] Je peux énumérer trois questions auxquelles un lecteur doit répondre
  avant d'utiliser un tableau non documenté. (O2)
- [ ] Je peux décrire DDI en deux phrases et nommer deux types
  d'organisations qui l'utilisent. (O3)
- [ ] Je peux associer chaque principe FAIR à une façon dont les métadonnées
  DDI le soutiennent. (O4)
- [ ] Je peux indiquer ce que fait `ddi-l` et une chose qu'il ne fait pas.
  (O5)

---

!!! tip "Notes pour l'instructeur"
    - **Activité d'ouverture :** Commencez par l'exercice du « tableau
      désordonné » (exercice 1). Donnez aux apprenants le tableau sans
      étiquettes et demandez-leur de deviner ce que les données signifient.
      Cela crée la motivation pour le reste du module.
    - **Adaptation au public :** Pour le tableau désordonné, vous pouvez
      montrer quelques lignes des jeux de données d'exemple du cours, sans
      les en-têtes : [`census-data.csv`](census-data.csv) pour les
      publics des INS et [`thesis-data.csv`](thesis-data.csv) pour les
      étudiants universitaires. Les deux reviennent dans le projet final du
      module 17.
    - **Question de discussion :** Demandez aux apprenants de raconter une
      fois où ils ont reçu un fichier sans documentation. Quelles questions
      avaient-ils ?
    - **Associations FAIR (exercice 3) :** Demandez quelle lettre FAIR est la
      plus difficile à atteindre sans une norme comme DDI. La plupart
      répondront Interopérable ou Trouvable.
    - **Conclusion :** Insistez sur le fait que `ddi-l` rend la
      documentation facile : vous écrivez du Python, et l'outil crée le XML
      standard pour vous.
