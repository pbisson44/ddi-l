---
description: >-
  Calendriers, liste de préparation, conseils d'animation et erreurs
  courantes pour enseigner le programme de formation ddi-l.
---

# Guide de l'instructeur

Ce guide aide les animateurs à donner le programme de formation `ddi-l`
en classe, en atelier ou en ligne. Il est aussi utile pour les apprenants
en auto-formation qui veulent du contexte pédagogique.

## En classe ou en auto-formation

Le programme fonctionne dans les deux modes :

- **En classe** : Un instructeur montre chaque concept en direct, puis
  les apprenants font les exercices. Utilisez les temps et les conseils
  d'animation ci-dessous.
- **Auto-formation** : Les apprenants lisent chaque module, suivent les
  exemples de code et vérifient leur travail avec les
  [corrigés](answer-keys.md).

## Calendriers suggérés

| Format | Modules | Durée totale |
| -------- | --------- | -------------- |
| Atelier d'une demi-journée (3,5 h) | 1-7 | Bases, y compris l'ouverture de fichiers et la validation |
| Atelier d'une journée (6 h) | 1-10 | Bases + CSV vers DDI, listes de codes et flux de questionnaire |
| Formation intensive de deux jours (11 h) | 1-16 | Programme complet avec projet de synthèse |
| Auto-formation | 1 par séance | ~3 semaines à 30-45 min/séance |

## Liste de vérification pour la préparation

Avant la séance, assurez-vous que chaque apprenant dispose de :

- [ ] Python 3.11 ou plus récent installé
- [ ] `ddi-l` installé (`pip install ddi-l`)
- [ ] `pandas` et `openpyxl` installés (`pip install pandas openpyxl`)
- [ ] Un éditeur de texte ou IDE (VS Code, PyCharm, ou même Notepad)
- [ ] Le fichier CSV d'exemple, [`survey_sample.csv`](survey_sample.csv){ download="survey_sample.csv" }
  (les projets de synthèse utilisent aussi [`thesis-data.csv`](thesis-data.csv){ download="thesis-data.csv" },
  [`health-survey.csv`](health-survey.csv){ download="health-survey.csv" } et
  [`census-data.csv`](census-data.csv){ download="census-data.csv" })
- [ ] Un terminal ou une invite de commandes

Prévoyez un plan de secours : un carnet cloud (Google Colab, JupyterHub)
ou un conteneur préconfiguré avec tout installé.

## Conseils d'animation par module

### Module 1 : Qu'est-ce que les métadonnées ?

- Commencez par l'exercice du « tableau mal organisé » *avant* de définir
  les métadonnées. Laissez les apprenants découvrir le problème.
- Pour un public d'INS, utilisez l'exemple du recensement. Pour les
  étudiants, utilisez l'exemple de la thèse.
- **Principes FAIR :** Parcourez l'exemple du Dr. Chen dans la section 4.
  Demandez aux apprenants quel principe FAIR est le plus difficile à
  atteindre sans une norme comme DDI. La plupart diront Interopérable ou
  Trouvable ; utilisez cela pour motiver le reste du programme.
- Durée : 45 min avec la discussion.

### Module 2 : Préparez votre environnement

- Prévoyez 30 min : les problèmes d'environnement sont le principal
  facteur de perte de temps en classe.
- Circulez et aidez avec les problèmes de PATH, les mauvaises versions
  de Python et les environnements virtuels.
- Si l'installation échoue, passez immédiatement à l'environnement de
  secours.

### Module 3 : Créez votre première étude

- C'est le moment « eureka ». Tapez le code en direct et montrez la
  sortie XML.
- Erreur courante : oublier les guillemets autour des chaînes de
  caractères.
- La section 9 présente `doc.validate()` et `doc.lint()`. Demandez aux
  apprenants de les exécuter à la fin de chaque module suivant, avant
  d'enregistrer.
- Durée : 45 min avec la démonstration en direct.

### Module 4 : Variables et questions

- Dessinez le modèle mental au tableau : Question → Variable → Colonne
  de données.
- Erreur courante : passer la chaîne de texte de la question au lieu de
  l'objet question à `question=`.
- Durée : 40 min.

### Module 5 : Concepts et univers

- Utilisez un diagramme : Univers = « qui », Concept = « quoi »,
  Variable = « comment c'est mesure », Question = « comment c'est
  demande ».
- Durée : 40 min.

### Module 6 : Ouvrir et modifier des fichiers

- C'est le flux de travail de l'archiviste : recevoir → inspecter →
  enrichir → valider → enregistrer.
- Durée : 40 min.

### Module 7 : Validation en ligne de commande

- Pour les publics d'INS, passez plus de temps sur la validation par lot
  et les codes de sortie.
- Durée : 40 min.

### Module 8 : Du CSV/Excel au DDI

- C'est le module le plus important pour les chercheurs et le personnel
  d'INS. Montrez le flux complet : ouvrir un CSV, exécuter le script,
  montrer la sortie DDI XML.
- Insistez : le CSV est les données. Le fichier DDI XML est la
  documentation *sur* les données. Ce sont deux fichiers différents.
- Passez la section SQL pour les publics non techniques.
- Durée : 60 min avec les exercices.

### Module 9 : Listes de codes

- Montrez une liste de codes réelle (codes pays ISO, classifications
  d'emploi).
- Erreur courante : oublier d'importer Category.
- Durée : 50 min.

### Module 10 : Flux de questionnaire

- Commencez avec un devis papier à l'écran. Demandez aux apprenants
  d'encercler les questions, souligner les sauts et encadrer les
  répétitions avant de coder.
- Dessinez l'organigramme au tableau. Associez chaque boîte à une
  construction DDI.
- Confusion courante : « Pourquoi une Question ET un QuestionConstruct ? »
  Expliquez la séparation contenu / flux.
- Durée : 60 min.

### Module 11 : Traçabilité des données

- Utilisez l'analogie de la recette : ingrédients bruts (collecte),
  cuisson (production), plat servi (maître). La provenance est la recette.
- Dessinez le pipeline à trois fichiers. Pour chaque variable, demandez
  de retracer la source jusqu'à la question originale.
- Clarifiez : `question_references` = « qu'est-ce qui a été demandé »,
  `source_variable_references` = « quelles données ont été utilisées ».
- La dérivation numérique-vers-code (âge → age_group) est l'exemple le
  plus parlant pour tous les publics.
- Pour le personnel des INS : c'est la documentation de la piste d'audit.
- Durée : 75 min.

### Module 12 : Couplage de données

- Ancrez avec l'argument du fardeau : réutiliser le fichier fiscal plutôt
  que de redemander le revenu. Le couplage crée de nouveaux renseignements
  à partir de données existantes.
- Dessinez deux fichiers partageant une colonne (`anon_id`) : la clé de
  couplage.
- Opposez le déterministe (une clé fiable) au probabiliste (plusieurs champs
  bruités, accord pondéré, révision manuelle).
- Soulignez que `source_variable_references` traversant les frontières
  d'étude est le coeur technique du couplage ; l'avertissement à
  l'enregistrement est attendu.
- Pour le personnel des INS : reliez à ECDS/SDLE, B-LFE et LEBAF, et à la
  gouvernance (couplages pré-approuvés vs examinés sous la Directive sur le
  couplage de microdonnées).
- Terminez toujours un couplage par une dépersonnalisation et, souvent, des
  données synthétiques.
- Durée : 75 min.

### Module 13 : Propriétés, recherche et validation

- Montrez que les propriétés personnalisées survivent aux allers-retours
  XML.
- Montrez le passage d'un objet liste de codes comme valeur de propriété
  (stocke l'URN).
- Erreur courante : essayer de faire un `find()` par nom au lieu de par
  identifiant.
- Durée : 50 min.

### Module 14 : Champs personnalisés

- Commencez par le problème du « chiffrier parallèle » : les métadonnées
  locales gardées hors du fichier se désynchronisent toujours. Les champs
  personnalisés les gardent dans le DDI.
- Rendez le point d'ouverture explicite : DDI fournit un point d'extension
  *normalisé*. Montrez le XML `UserAttributePair` pour que les apprenants
  voient que c'est toujours du DDI valide.
- Opposez au Module 13 : ce module enseignait la mécanique de `set_property` ;
  celui-ci gouverne les extensions : espaces de noms, catalogues, valeurs
  contrôlées, audit.
- Clarifiez `UserID` vs propriété personnalisée : identifier vs décrire.
- Pour le personnel des INS/archives : reliez à la gouvernance réelle
  (calendriers de conservation, classifications de sécurité, gestionnaires de
  données), et à la boucle d'audit de la section 9.
- Mise en garde : ne réinventez pas le DDI intégré ; les champs personnalisés
  sont pour de véritables lacunes.
- Durée : 55 min.

### Module 15 : Mise à jour et versionnage

- Module clé pour les archivistes et le personnel d'INS qui gèrent des
  enquêtes de longue durée.
- Montrez le XML avant et après le versionnage pour que les apprenants
  voient le numéro de version et la justification dans le fichier.
- Durée : 50 min.

### Module 16 : Projets de synthèse

- Laissez les apprenants choisir leur parcours par profil. Dans un groupe
  mixte, formez des équipes par rôle.
- Prévoyez 90 min avec une courte présentation à la fin.
- Évaluez avec la grille d'auto-évaluation du module.

## Erreurs courantes dans tous les modules

| Erreur | Module | Correction |
| -------- | -------- | ------------ |
| Oublier les guillemets autour des chaînes | 3 | Montrez le message d'erreur et expliquez |
| Passer du texte au lieu d'un objet à `question=` | 4 | Montrez la différence entre `"age"` et `q1` |
| Oublier d'importer Category/Instrument | 9 | Montrez la ligne d'import explicitement |
| Confondre Question et QuestionConstruct | 10 | Question = contenu, QuestionConstruct = étape du flux |
| Confondre question_references et source_variable_references | 11 | question_ref = ce qui a été demandé, source_var_ref = quelles données ont été utilisées |
| Utiliser `find()` avec un nom au lieu d'un identifiant | 13 | Affichez `item.identifier` d'abord |
| Ne pas valider avant d'enregistrer | À partir du 3 | Faites de la validation une habitude : toujours valider avant d'enregistrer |

## Adapter le cours à chaque public

| Public | Insister sur | Passer ou survoler |
| -------- | ------------- | ------------------- |
| Étudiants universitaires | Modules 1 (motivation), 3-7 (bases et vérification du travail) | Section SQL du Module 8 |
| Chercheurs | Modules 1, 4 et 5 (vocabulaire du DDI), 8 (flux CSV), 9-13 (listes de codes, flux, traçabilité, couplage, propriétés) | Module 2 s'ils utilisent déjà Python |
| Archivistes | Modules 2-7 (Python, ouvrir/modifier, validation), 14 (champs personnalisés), 15 (versionnage) | Module 1 s'ils ont de l'expérience DDI |
| Personnel d'INS | Modules 8-15 (flux complet), en particulier 10 (flux), 11 (traçabilité), 12 (couplage), 14 (champs personnalisés) | Modules 1 et 3 |
| Développeurs qui automatisent les contrôles DDI | Modules 3 et 7, puis le [parcours automatisation](index.md#parcours-automatisation) | Modules 1, 4 et 5 |

## Approche d'évaluation

- **Quiz** (Modules 1-15) : Formatifs, pour vérifier la compréhension.
  Passez les réponses en revue en groupe dans un cadre en classe.
- **Projet de synthèse** (Module 16) : Sommatif, pour évaluer
  l'ensemble des compétences. Utilisez la grille du module.
- **Questions de réflexion** (Module 16) : Pas de bonne ou mauvaise
  réponse. Utilisez-les pour la discussion ou les commentaires écrits.

## Glossaire terminologique (EN / FR)

| Anglais | Français |
| --------- | ---------- |
| Metadata | Métadonnées |
| Study | Étude |
| Survey | Enquête |
| Variable | Variable |
| Question | Question |
| Concept | Concept |
| Universe | Univers |
| Code list | Liste de codes |
| Category | Catégorie |
| Validate | Valider |
| Version | Version |
| Custom property | Propriété personnalisée |
| Agency | Agence |
| Identifier | Identifiant |
| Save | Enregistrer |
| Open | Ouvrir |
| Data linkage | Couplage de données |
| Linkage key | Clé de couplage |
| Custom field | Champ personnalisé |
| Extension point | Point d'extension |

## Recueillir les commentaires

Après la dernière séance :

1. Demandez aux apprenants de remplir un court formulaire de commentaires
   (3 à 5 questions).
2. Conservez les transcriptions du terminal ou les points de contrôle des
   carnets comme références d'intégration pour les futures cohortes.
3. Faites une rétrospective de 10 minutes : ce qui a fonctionné, ce qui
   n'a pas fonctionné, ce qu'il faut changer la prochaine fois.

## Ressources supplémentaires

- [Parcours automatisation](index.md#parcours-automatisation) : Un plan
  d'atelier pour les équipes qui automatisent la validation
- [Corrigés](answer-keys.md) : Toutes les solutions et réponses aux quiz sur
  une seule page
