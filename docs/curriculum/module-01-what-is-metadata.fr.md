# Module 1 : Qu'est-ce que les métadonnées et pourquoi sont-elles importantes ?

!!! info "Ce que vous apprendrez"
    - Définir les métadonnées dans vos propres mots.
    - Expliquer pourquoi des données sans documentation sont difficiles à utiliser.
    - Décrire ce qu'est DDI et qui l'utilise.
    - Expliquer comment DDI aide à rendre les données FAIR (Trouvables,
      Accessibles, Interopérables, Réutilisables).
    - Décrire ce que fait `ddi-l`.

**Prérequis :** Aucun.

**Durée :** 30 min en autonomie / 45 min avec instructeur.

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

**Exercice 1.** Regardez le tableau ci-dessous.

| A  | B      |     C |
| -: | ------ | ----: |
| 34 | Female | 52000 |
| 28 | Male   | 41000 |
| 45 | Female | 67000 |
| 22 | Male   | 29000 |
| 51 | Other  | 73000 |

Notez **3 choses** qu'une nouvelle personne aurait besoin de savoir avant de
pouvoir utiliser ces données. Par exemple : que mesure la colonne A ?

**Exercice 2.** Visitez <https://ddialliance.org> et trouvez une phrase sur le
site qui décrit ce que fait DDI. Notez cette phrase.

---

## Quiz

???+ question "Question 1 : Qu'est-ce que les métadonnées ?"
    **A.** Les données brutes dans un tableur.

    **B.** Des informations sur les données, comme une étiquette ou une
    description qui vous dit ce que les données signifient.

    **C.** Un type de langage de programmation.

    **D.** Un format de fichier utilisé uniquement par les gouvernements.

    ??? success "Réponse"
        **B.** Les métadonnées sont des informations sur les données. Elles
        décrivent ce que les données signifient, d'où elles viennent et comment
        elles ont été collectées.

???+ question "Question 2 : Pourquoi la documentation est-elle importante ?"
    **A.** Elle réduit la taille du fichier de données.

    **B.** Elle est exigée par Python.

    **C.** Sans elle, les gens ne peuvent pas comprendre ce que les données
    signifient ni comment les utiliser correctement.

    **D.** Elle modifie les valeurs dans le jeu de données.

    ??? success "Réponse"
        **C.** Sans documentation, les données ne sont que des chiffres et des
        étiquettes sans contexte. Les gens risquent de mal interpréter ou de
        mal utiliser les données.

???+ question "Question 3 : Que signifie FAIR ?"
    **A.** Fast, Automated, Indexed, Reliable.

    **B.** Findable, Accessible, Interoperable, Re-usable.

    **C.** File, Archive, Import, Report.

    **D.** Format, Align, Inspect, Review.

    ??? success "Réponse"
        **B.** FAIR signifie Findable (Trouvable), Accessible, Interoperable
        (Interopérable) et Re-usable (Réutilisable). Ces quatre principes
        guident la façon dont les données devraient être partagées pour que
        d'autres puissent les découvrir, les comprendre et les réutiliser.
        Les métadonnées DDI vous aident à respecter les quatre.

???+ question "Question 4 : Que fait ddi-l ?"
    **A.** Il collecte les réponses d'enquête auprès des gens.

    **B.** C'est un outil Python qui crée, lit, modifie et valide des documents
    DDI.

    **C.** Il convertit du code Python en fichiers Excel.

    **D.** Il remplace Microsoft Word pour rédiger des rapports.

    ??? success "Réponse"
        **B.** `ddi-l` est un paquet Python pour travailler avec les
        documents de métadonnées DDI. Il gère le XML pour que vous puissiez
        vous concentrer sur vos données.

---

!!! tip "Notes pour l'instructeur"
    - **Activité d'ouverture :** Commencez par l'exercice du « tableau
      désordonné » (exercice 1). Donnez aux apprenants le tableau sans
      étiquettes et demandez-leur de deviner ce que les données signifient.
      Cela crée la motivation pour le reste du module.
    - **Adaptation au public :** Utilisez l'exemple du recensement pour les
      publics des INS. Utilisez l'exemple de la thèse pour les étudiants
      universitaires.
    - **Question de discussion :** Demandez aux apprenants de raconter une
      fois où ils ont reçu un fichier sans documentation. Quelles questions
      avaient-ils ?
    - **Conclusion :** Insistez sur le fait que `ddi-l` rend la
      documentation facile : vous écrivez du Python, et l'outil crée le XML
      standard pour vous.
