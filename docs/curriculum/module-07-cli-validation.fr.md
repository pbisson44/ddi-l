---
description: >-
  Module 7 du cours ddi-l : valider, analyser, convertir et faire l'aller-
  retour de fichiers DDI avec la commande ddi, et utiliser les codes de
  sortie.
---

# Module 7 : Valider depuis la ligne de commande

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Exécuter `ddi validate` sur un fichier DDI et dire, d'après le résultat, si le fichier est valide.
    - **O2.** Interpréter une erreur de `ddi validate` : dire ce qui ne va pas et où, à l'aide du message et du chemin après `at`, puis corriger le fichier pour qu'il soit valide.
    - **O3.** Exécuter `ddi lint` sur un fichier et nommer un constat par sa gravité, sa règle et son message.
    - **O4.** Convertir un fichier DDI en JSON avec `ddi to-json` et écrire une copie normalisée avec `ddi roundtrip`.
    - **O5.** Vérifier le code de sortie d'une commande après un fichier valide et un fichier invalide, et prédire le code (0 ou 1) que recevra un script.

**Prérequis :** [Module 6](module-06-open-modify.fr.md).

**Durée :** 30 min en autonomie / 40 min avec instructeur.

**Nouveau dans ce module :** `ddi validate`, `ddi validate --format json`, `ddi lint`, `ddi lint --format table`, `ddi to-json`, `ddi roundtrip`, `echo $?` (et `echo %ERRORLEVEL%` ou `$LASTEXITCODE` sous Windows).

---

## 1. Pourquoi utiliser la ligne de commande ?

Jusqu'ici, vous avez écrit des scripts Python pour travailler avec des fichiers DDI. Mais parfois vous voulez juste vérifier un fichier rapidement sans écrire de code. La **ligne de commande** (aussi appelée terminal ou shell) vous permet de faire cela.

La ligne de commande est aussi utile quand vous devez :

- **Traiter plusieurs fichiers à la fois.** Vous pouvez valider 20 fichiers avec une seule commande.
- **Automatiser les vérifications.** Vous pouvez ajouter la validation à un script qui s'exécute chaque nuit.
- **Intégrer dans des pipelines CI/CD.** Un **pipeline CI/CD** est un système automatisé qui construit et teste les logiciels. Beaucoup d'équipes utilisent des pipelines pour détecter les erreurs tôt.

`ddi-l` inclut un outil en ligne de commande appelé `ddi`. Vous l'avez installé quand vous avez installé le paquet `ddi-l` (voir le [module 2](module-02-setup.fr.md)).

Les exercices utilisent `census-2024.xml`, le fichier enregistré à l'exercice 1 du [module 6](module-06-open-modify.fr.md). Exécutez les commandes depuis le dossier qui le contient.

---

## 2. Valider un fichier

La commande `ddi validate` vérifie si un fichier DDI XML suit les règles du schéma DDI. Un **schéma** est un ensemble de règles qui dit quels éléments sont permis, dans quel ordre ils doivent apparaître et lesquels sont obligatoires.

```bash
ddi validate my-study.xml
```

Si le fichier est valide, vous voyez :

```text
Document is valid.
```

Si le fichier contient des erreurs, vous voyez une entrée par problème. Par exemple, voici le résultat pour un fichier dans lequel quelqu'un a écrit `<r:Abstrct>` au lieu de `<r:Abstract>` :

```text
error: Unexpected child with tag '{ddi:reusable:3_3}Abstrct' at position 5.
    at /{ddi:instance:3_3}DDIInstance/{ddi:studyunit:3_3}StudyUnit
    context: <s:StudyUnit>
1 issue found.
```

Chaque erreur vous dit :

- **ce qui ne va pas** : le message après `error:`. Ici, un élément appelé `Abstrct` apparaît là où le schéma ne le permet pas.
- **où** : le chemin après `at`. Lisez-le de gauche à droite, de la racine du fichier jusqu'à l'élément qui contient le problème : `DDIInstance`, puis `StudyUnit`. Vous pouvez ignorer les parties entre accolades, comme `{ddi:reusable:3_3}` : elles nomment l'espace de noms DDI auquel appartient chaque élément. Un nombre entre crochets, comme `QuestionItem[2]`, signifie « le deuxième `QuestionItem` ».
- **ce qui a été trouvé** : la ligne `context:` montre l'élément (et sa valeur, quand il en a une).

La dernière ligne compte les problèmes. Pour les scripts, ajoutez `--format json` afin d'obtenir les mêmes informations sous forme de liste JSON (une liste vide `[]` lorsque le fichier est valide).

---

## 3. Lire le résultat

Quand vous voyez `"Document is valid."`, cela signifie que le fichier suit toutes les règles du schéma DDI. Aucune action n'est nécessaire.

Quand vous voyez des erreurs, lisez chaque message attentivement. Les messages les plus courants sont :

| Le message dit                           | Ce que cela signifie                                                                              |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `Unexpected child with tag '...'`        | Un élément est au mauvais endroit, est mal orthographié, ou un élément obligatoire avant lui manque. |
| `value doesn't match any pattern of ...` | Une valeur texte enfreint une règle, comme un numéro de version qui n'est pas fait de chiffres.   |
| `Error: mismatched tag: line N, column M`| Le fichier n'est pas du XML bien formé : une balise n'est pas fermée. La ligne et la colonne disent où. |

Le dernier type d'erreur arrête `ddi` avant la vérification du schéma : il ne peut pas lire le fichier du tout.

Corrigez les erreurs dans votre script Python (ou directement dans le fichier XML), puis exécutez `ddi validate` à nouveau.

---

## 4. Vérifier la qualité d'un fichier

La commande `ddi lint` vérifie les **règles de qualité** qui vont au-delà du schéma. Elle applique les mêmes règles que `doc.lint()`, utilisé au [module 3](module-03-first-study.fr.md#9-verifier-votre-travail). Le **linting** consiste à chercher des problèmes qui sont techniquement permis par le schéma mais qui sont généralement des erreurs ou des mauvaises pratiques.

```bash
ddi lint my-study.xml
```

Par exemple, une règle de linting peut vous avertir qu'un élément n'a pas d'étiquette, ou qu'une référence pointe vers un élément absent du fichier. Le fichier peut quand même être du XML valide, mais les métadonnées sont incomplètes.

Par défaut, le résultat est en JSON, pour les scripts. Ajoutez `--format table` pour obtenir un tableau plus facile à lire :

```bash
ddi lint my-study.xml --format table
```

```text
severity  rule                     message
--------  -----------------------  ----------------------------------------
warning   ddi.maintainable.labels  Maintainable element is missing a label.
warning   ddi.maintainable.labels  Maintainable element is missing a label.
```

Chaque ligne est un **constat**, avec trois colonnes :

- **severity** : sa gravité : `error`, `warning` ou `info`.
- **rule** : le nom de la règle qui l'a trouvé, comme `ddi.maintainable.labels`. La page [Règles de lint](../lint-rules.fr.md) explique chaque règle.
- **message** : ce que la règle a trouvé. Ici, deux éléments n'ont pas d'étiquette.

---

## 5. Exporter en JSON

La commande `ddi to-json` convertit un fichier DDI XML au format JSON. Le **JSON** (JavaScript Object Notation) est un format texte que beaucoup d'outils et de langages de programmation peuvent lire. Il est plus facile à lire que le XML pour certaines personnes.

```bash
ddi to-json my-study.xml --indent 2
```

L'option `--indent 2` ajoute des espaces pour rendre le résultat plus facile à lire. Sans elle, le JSON est affiché sur une seule longue ligne.

Vous pouvez enregistrer le résultat dans un fichier en utilisant le symbole `>` :

```bash
ddi to-json my-study.xml --indent 2 > my-study.json
```

Cela crée un nouveau fichier appelé `my-study.json` avec le contenu JSON.

---

## 6. Aller-retour

La commande `ddi roundtrip` lit un fichier DDI XML et le réécrit. C'est ce qu'on appelle un **aller-retour** parce que les données voyagent en cercle : du fichier à la mémoire et retour au fichier.

```bash
ddi roundtrip input.xml --output output.xml
```

Pourquoi est-ce utile ?

- **Normaliser le format.** Différents outils peuvent écrire le XML avec des espacements et des ordres différents. Un aller-retour produit un format propre et cohérent.
- **Tester la perte de données.** Si le fichier de sortie est le même que l'entrée, rien n'a été perdu. Vous pouvez comparer les deux fichiers pour vérifier.

---

## 7. Codes de sortie

Chaque outil en ligne de commande retourne un **code de sortie** quand il termine. Un code de sortie est un nombre qui vous dit si la commande a réussi ou échoué.

| Code de sortie | Signification                          |
| -------------- | -------------------------------------- |
| 0              | Succès : tout va bien.               |
| 1              | Échec : quelque chose a mal tourné.  |

`ddi validate` retourne 1 quand le fichier a au moins une erreur de schéma. `ddi lint` retourne 1 seulement quand un constat a la gravité `error` : des avertissements seuls retournent 0. (Ajoutez `--fail-severity warning` pour que les avertissements fassent aussi échouer la commande.)

Pourquoi est-ce important ? Parce que les scripts et les pipelines peuvent vérifier le code de sortie pour décider quoi faire ensuite. Par exemple :

```bash
ddi validate my-study.xml && echo "All good!" || echo "Fix the errors."
```

Cette ligne dit : « Exécutez `ddi validate`. Si la commande réussit (code de sortie 0), affichez 'All good!'. Si elle échoue (code de sortie 1), affichez 'Fix the errors.' »

Vous pouvez aussi afficher le code de sortie de la dernière commande. Sous macOS et Linux, utilisez `$?` :

```bash
ddi validate my-study.xml
echo $?
```

Sous Windows, utilisez `echo %ERRORLEVEL%` dans l'invite de commandes, ou `$LASTEXITCODE` dans PowerShell.

Si le fichier est valide, `echo $?` affiche `0`. Sinon, il affiche `1`.

---

## Exercices

!!! example "Scénario"
    Un bureau national de statistique possède 20 fichiers DDI XML provenant
    de différentes équipes d'enquête. Il doit tous les valider, vérifier leur
    qualité, en exporter un en JSON et produire une copie normalisée.

**Exercice 1 (O1).** Validez `census-2024.xml`, issu des exercices du module 6 (ou tout fichier d'un module précédent), avec `ddi validate`. Le fichier est-il valide ?

Résultat attendu :

```text
Document is valid.
```

??? success "Réponse"
    ```bash
    ddi validate census-2024.xml
    ```

    Le résultat dit `Document is valid.` : le fichier suit donc toutes les
    règles du schéma DDI.

**Exercice 2 (O2).** Cassez un fichier exprès et lisez l'erreur.

1. Faites une copie de `census-2024.xml` appelée `broken.xml` (`cp census-2024.xml broken.xml` sous macOS et Linux, `copy census-2024.xml broken.xml` sous Windows).
2. Ouvrez `broken.xml` dans un éditeur de texte. À la ligne 5, remplacez `<r:Version>1</r:Version>` par `<r:Version>one</r:Version>`. Enregistrez le fichier.
3. Exécutez `ddi validate broken.xml`.
4. Notez ce qui ne va pas et où.

Gardez `broken.xml` tel quel : vous le corrigerez à l'exercice 6.

Résultat attendu :

```text
error: value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*']
    at /{ddi:instance:3_3}DDIInstance/{ddi:reusable:3_3}Version
    context: <r:Version> one
1 issue found.
```

??? success "Réponse"
    ```bash
    cp census-2024.xml broken.xml
    # edit line 5 of broken.xml, then:
    ddi validate broken.xml
    ```

    - **Quoi :** la valeur `one` ne correspond pas au motif des versions.
      `[0-9]+(\.[0-9]+)*` signifie des chiffres, suivis éventuellement
      d'autres groupes formés d'un point et de chiffres, comme `1` ou
      `1.0.0`.
    - **Où :** le chemin après `at` se termine par `DDIInstance`, puis
      `Version` : l'élément `Version` situé directement sous la racine,
      celui de la ligne 5. La ligne `context:` confirme la valeur trouvée :
      `one`.

**Exercice 3 (O3).** Exécutez `ddi lint` sur `census-2024.xml` avec `--format table`. Choisissez un constat et nommez sa gravité, sa règle et son message. Que changeriez-vous pour le faire disparaître ?

Résultat attendu :

```text
severity  rule                     message
--------  -----------------------  ----------------------------------------
warning   ddi.maintainable.labels  Maintainable element is missing a label.
warning   ddi.maintainable.labels  Maintainable element is missing a label.
warning   ddi.maintainable.labels  Maintainable element is missing a label.
warning   ddi.maintainable.labels  Maintainable element is missing a label.
```

??? success "Réponse"
    ```bash
    ddi lint census-2024.xml --format table
    ```

    Un constat : gravité `warning`, règle `ddi.maintainable.labels`, message
    « Maintainable element is missing a label. » Le fichier en a quatre :
    ses deux questions et ses deux variables n'ont pas d'étiquette. Pour les
    corriger, passez `label=` quand vous ajoutez chaque élément, comme à la
    section 9 du module 3. Le fichier reste valide : les avertissements
    concernent la qualité, pas des erreurs de schéma.

**Exercice 4 (O4).** Exportez `census-2024.xml` en JSON avec `ddi to-json`. Comptez le nombre de lignes du JSON.

Résultat attendu : environ 200 lignes (`wc -l` affiche le nombre suivi du nom du fichier).

??? success "Réponse"
    ```bash
    ddi to-json census-2024.xml --indent 2 > census-2024.json
    wc -l census-2024.json
    ```

    La commande `wc -l` compte le nombre de lignes dans un fichier (dans
    PowerShell sous Windows, utilisez `(Get-Content census-2024.json).Count`).
    Un fichier de deux questions et deux variables donne environ 200 lignes ;
    plus de contenu donne plus de lignes.

**Exercice 5 (O4).** Faites un aller-retour de `census-2024.xml`. Comparez les tailles de l'entrée et de la sortie.

Résultat attendu : deux fichiers de même taille, environ 4 Ko chacun.

??? success "Réponse"
    ```bash
    ddi roundtrip census-2024.xml --output census-2024-roundtrip.xml
    ls -l census-2024.xml census-2024-roundtrip.xml
    ```

    La commande `ls -l` affiche les tailles des fichiers (utilisez `dir`
    sous Windows). Un fichier que `ddi-l` a lui-même écrit revient
    exactement à la même taille. Un fichier issu d'un autre outil peut
    différer un peu, à cause de l'espacement : c'est la normalisation à
    l'œuvre.

**Exercice 6 (O5, O2).** Vérifiez les codes de sortie.

1. Exécutez `ddi validate census-2024.xml`, puis affichez le code de sortie (`echo $?` sous macOS et Linux, `echo %ERRORLEVEL%` dans l'invite de commandes Windows, `$LASTEXITCODE` dans PowerShell).
2. Faites de même avec `broken.xml` de l'exercice 2.
3. Corrigez `broken.xml` (remettez `1` à la place de `one`), validez-le à nouveau et affichez encore le code de sortie.

Résultat attendu (les codes de sortie, dans l'ordre) :

```text
0
1
0
```

??? success "Réponse"
    ```bash
    ddi validate census-2024.xml
    echo $?
    ddi validate broken.xml
    echo $?
    # edit line 5 of broken.xml back to <r:Version>1</r:Version>, then:
    ddi validate broken.xml
    echo $?
    ```

    Un fichier valide donne le code de sortie 0. Un fichier avec une erreur
    de schéma donne 1, et le fichier corrigé donne de nouveau 0, avec
    `Document is valid.` au-dessus. Un script qui exécute `ddi validate` peut
    se servir de ces codes pour s'arrêter avant de publier un fichier cassé.

---

## Quiz

???+ question "Question 1 (O1) : Que vous apprend ce résultat ?"
    Vous exécutez `ddi validate study.xml` et voyez `Document is valid.`

    **A.** Le fichier suit toutes les règles du schéma DDI ; aucune action
    n'est nécessaire.

    **B.** Le fichier n'a pas non plus de constats de lint.

    **C.** Le fichier a été converti en JSON.

    **D.** Le fichier a été enregistré dans un nouveau format normalisé.

    ??? success "Réponse"
        **A.** `ddi validate` vérifie seulement le schéma. Les constats de
        lint sont une vérification distincte (`ddi lint`) : l'option B ne
        découle donc pas de ce résultat.

???+ question "Question 2 (O2) : Où est le problème dans ce résultat ?"
    ```text
    error: Unexpected child with tag '{ddi:datacollection:3_3}QuestionTxt' at position 4.
        at /{ddi:instance:3_3}DDIInstance/{ddi:studyunit:3_3}StudyUnit/{ddi:datacollection:3_3}DataCollection/{ddi:datacollection:3_3}QuestionScheme/{ddi:datacollection:3_3}QuestionItem[1]
        context: <d:QuestionItem>
    1 issue found.
    ```

    **A.** Dans le titre de l'étude.

    **B.** Le fichier n'est pas du XML bien formé.

    **C.** Dans le premier `QuestionItem` : il contient un élément appelé
    `QuestionTxt`, que le schéma ne permet pas à cet endroit (on dirait un
    `QuestionText` mal orthographié).

    **D.** À la ligne 1 du fichier.

    ??? success "Réponse"
        **C.** Le chemin après `at` se termine par `QuestionItem[1]`, le
        premier élément de question, qui contient le problème ; le message
        nomme l'élément inattendu. Un fichier mal formé donne plutôt une
        erreur `mismatched tag`.

???+ question "Question 3 (O3) : Que vous apprennent ces deux résultats sur le fichier ?"
    `ddi validate data.xml` affiche `Document is valid.`, et
    `ddi lint data.xml --format table` affiche une ligne :
    `warning  ddi.maintainable.labels  Maintainable element is missing a label.`

    **A.** Le fichier enfreint une règle du schéma.

    **B.** Le fichier est valide, mais le lint a trouvé un problème de
    qualité : un élément n'a pas d'étiquette.

    **C.** `ddi lint` et `ddi validate` vérifient les mêmes règles : l'un des
    deux se trompe.

    **D.** L'avertissement fait retourner le code de sortie 1 à `ddi lint`.

    ??? success "Réponse"
        **B.** La validation vérifie le schéma ; le lint vérifie des règles de
        qualité au-delà du schéma. Un avertissement seul ne fait pas échouer
        `ddi lint` : il retourne 0, sauf si vous passez
        `--fail-severity warning`.

???+ question "Question 4 (O4) : Quelle commande écrit une copie JSON de my-study.xml dans my-study.json ?"
    **A.** `ddi roundtrip my-study.xml --output my-study.json`

    **B.** `ddi validate my-study.xml > my-study.json`

    **C.** `ddi lint my-study.json`

    **D.** `ddi to-json my-study.xml --indent 2 > my-study.json`

    ??? success "Réponse"
        **D.** `ddi to-json` convertit le DDI XML en JSON, et `>` enregistre
        le résultat dans un fichier. `ddi roundtrip` écrit du XML, et la
        commande `ddi validate` de l'option B enregistre le rapport de
        validation, pas le document.

???+ question "Question 5 (O4) : Pourquoi exécuter ddi roundtrip sur un fichier issu d'un autre outil ?"
    **A.** Pour supprimer les éléments que `ddi-l` ne modélise pas.

    **B.** Pour écrire une copie au format propre et cohérent, et vérifier
    que rien ne se perd en route.

    **C.** Pour valider le fichier par rapport au schéma.

    **D.** Pour convertir le fichier en JSON.

    ??? success "Réponse"
        **B.** Un aller-retour lit le fichier et le réécrit dans un format
        normalisé. `ddi-l` conserve les éléments qu'il ne modélise pas : rien
        n'est supprimé.

???+ question "Question 6 (O5) : Qu'affiche ce script ?"
    `broken.xml` a trois erreurs de schéma. Un script exécute :

    ```bash
    ddi validate broken.xml
    echo $?
    ```

    **A.** `0`

    **B.** `3`

    **C.** `1` (après la liste des erreurs)

    **D.** `-1`

    ??? success "Réponse"
        **C.** `ddi validate` retourne 1 quand le fichier a une erreur de
        schéma, quel que soit leur nombre. Le code de sortie dit « échec »,
        pas combien de problèmes ont été trouvés.

---

## Faites le point

- [ ] Je peux exécuter `ddi validate` sur un fichier et dire, d'après le résultat, s'il est valide. (O1)
- [ ] Je peux lire une erreur de `ddi validate`, dire ce qui ne va pas et où, et corriger le fichier pour qu'il soit valide. (O2)
- [ ] Je peux exécuter `ddi lint` et nommer un constat par sa gravité, sa règle et son message. (O3)
- [ ] Je peux convertir un fichier en JSON avec `ddi to-json` et écrire une copie normalisée avec `ddi roundtrip`. (O4)
- [ ] Je peux vérifier le code de sortie après un fichier valide et un fichier invalide, et prédire ce que recevra un script. (O5)

---

**Voir aussi :**

- [Recettes CLI](../cli-recipes.fr.md)
- [Guide d'automatisation](../tutorials/automation-playbook.fr.md)
- [Règles de lint](../lint-rules.fr.md)

---

!!! tip "Notes pour l'instructeur"
    - **Démo en direct.** Exécutez `ddi validate`, `ddi lint`, `ddi to-json`
      et `ddi roundtrip` sur un projecteur pour que les apprenants puissent
      voir le résultat en temps réel. Utilisez des fichiers des modules
      précédents.
    - **Cassez un fichier exprès.** L'exercice 2 remplace un numéro de
      version par un mot, ce qui donne une erreur de schéma. Montrez aussi
      un autre bris : supprimez une balise fermante dans un éditeur de texte
      et exécutez de nouveau `ddi validate`. Cela donne
      `Error: mismatched tag: line N, column M`, parce que le fichier n'est
      plus du XML bien formé. Corrigez-le et revalidez.
    - **Validation par lots.** Montrez comment valider plusieurs fichiers
      à la fois :
      `for f in *.xml; do echo "--- $f ---"; ddi validate "$f"; done`
    - **Codes de sortie en pratique.** Écrivez un court script bash qui
      valide un fichier et affiche un message selon le code de sortie.
      Cela prépare les apprenants à l'intégration CI/CD. Sous Windows, les
      apprenants affichent le code avec `echo %ERRORLEVEL%` (invite de
      commandes) ou `$LASTEXITCODE` (PowerShell).
    - **Le lint n'est pas la validation.** Les apprenants s'attendent
      souvent à ce que des avertissements de lint rendent un fichier
      invalide. Servez-vous de l'exercice 3 et de la question 3 pour bien
      séparer les deux vérifications.
    - **JSON comme passerelle.** Expliquez que le résultat JSON peut être
      chargé par d'autres outils (R, JavaScript, catalogues de données).
      C'est utile pour les équipes qui n'utilisent pas Python.
    - **Note de durée.** Ce module contient moins de code Python et plus de
      compétences en ligne de commande. Si votre public est moins à l'aise
      avec le terminal, passez plus de temps sur la section 1 et les
      exercices.
