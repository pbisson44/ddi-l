---
description: >-
  Module 2 du cours ddi-l : installer Python, ddi-l et les paquets utiles,
  puis vérifier que tout fonctionne.
---

# Module 2 : Préparer votre environnement Python

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Exécuter `python --version` et décider si votre Python est
      assez récent pour `ddi-l` (3.11 ou plus récent).
    - **O2.** Installer `ddi-l`, `pandas` et `openpyxl` avec `pip` et lire la
      dernière ligne de la sortie pour confirmer l'installation.
    - **O3.** Exécuter un test Python de deux lignes qui affiche la version
      installée de `ddi-l`.
    - **O4.** Exécuter `ddi --help` et trouver la commande qui fait une tâche
      donnée, comme valider un fichier.
    - **O5.** Choisir un espace de travail (Python REPL, fichier script ou
      notebook) pour une tâche donnée et justifier ce choix en une phrase.

**Prérequis :** [Module 1](module-01-what-is-metadata.fr.md)

**Durée :** 20 min en autonomie / 30 min avec instructeur.

**Nouveau dans ce module :** `python --version`, `pip install`, `ddi --help`,
`import ddi_l as ddi`, `ddi.__version__`

---

## 1. Ce dont vous avez besoin : Python 3.11 ou plus récent

Python est un langage de programmation. `ddi-l` fonctionne dans Python,
vous devez donc avoir Python installé sur votre ordinateur.

Ouvrez un **terminal** (aussi appelé invite de commandes) et tapez :

```bash
python --version
```

Vous devriez voir quelque chose comme :

```text
Python 3.12.3
```

Le numéro de version doit être **3.11 ou supérieur**. Lisez les deux
premiers nombres : `3.12` est plus récent que `3.11`, donc il convient ;
`3.10` ou `3.9` est trop ancien. Si votre version est plus ancienne, visitez
<https://www.python.org/downloads/> et installez une version plus récente.

!!! warning "Problème courant"
    Sur certains systèmes, la commande est `python3` au lieu de `python`. Si
    `python --version` ne fonctionne pas, essayez `python3 --version`.

---

## 2. Installer ddi-l

Dans votre terminal, exécutez :

```bash
pip install ddi-l
```

Cette commande télécharge `ddi-l` depuis Internet et l'installe. Le mot
**pip** est l'installateur de paquets de Python. C'est la façon standard
d'ajouter de nouveaux outils à votre installation Python.

Ensuite, installez deux paquets utilitaires dont vous aurez besoin dans les
modules suivants :

```bash
pip install pandas openpyxl
```

- **pandas** est un outil populaire pour travailler avec des tableaux de données.
- **openpyxl** permet à Python de lire et d'écrire des fichiers Excel.

Vous pouvez tout installer en une seule ligne si vous préférez :

```bash
pip install ddi-l pandas openpyxl
```

La dernière ligne de la sortie vous dit comment cela s'est passé :

- `Successfully installed` suivi de noms de paquets signifie que pip les a
  installés.
- `Requirement already satisfied` signifie qu'un paquet était déjà là : pip
  n'avait rien à faire.
- Une ligne qui commence par `ERROR` signifie que l'installation a échoué.
  Lisez le message, corrigez la cause (souvent la version de Python ou un
  problème de réseau) et relancez la commande.

---

## 3. Vérifier que tout fonctionne

### 3a. Tester l'outil en ligne de commande

`ddi-l` inclut un outil en ligne de commande appelé `ddi`. Exécutez :

```bash
ddi --help
```

Vous devriez voir une liste de commandes disponibles. Cela confirme que
l'outil est installé et prêt à être utilisé. Chaque commande a une
description d'une ligne. Le début de la liste ressemble à ceci :

```text
positional arguments:
    validate            Validate an XML document against the DDI schema.
    to-json             Convert a DDI instance document to JSON.
    ...
```

Pour trouver la commande qui fait une tâche, lisez les descriptions, pas
seulement les noms. Par exemple, la commande qui vérifie un fichier par
rapport aux règles DDI est celle dont la description dit « Validate ». Vous
utiliserez ces commandes au [module 7](module-07-cli-validation.fr.md).

### 3b. Tester dans Python

Ouvrez une session Python en tapant `python` dans votre terminal. Puis tapez :

```python
import ddi_l as ddi

print(ddi.__version__)
```

Vous devriez voir un numéro de version affiché, comme `0.1.0` ou plus récent.
Cela confirme que Python peut trouver et charger le paquet `ddi-l`.

Si vous voyez plutôt `ModuleNotFoundError: No module named 'ddi_l'`, `ddi-l`
n'est pas installé dans le Python que vous utilisez. Relancez
`pip install ddi-l` avec la même commande `python` ou `python3` que
ci-dessus (par exemple, `python3 -m pip install ddi-l`).

Tapez `exit()` pour quitter la session Python.

---

## 4. Choisir votre espace de travail

Vous pouvez écrire du code Python de plusieurs façons. Choisissez celle qui
vous semble la plus confortable :

| Espace de travail | Comment démarrer                              | Idéal pour                    |
| ----------------- | --------------------------------------------- | ----------------------------- |
| Python REPL       | Tapez `python` dans le terminal.              | Tests rapides et exploration. |
| Fichier script    | Créez un fichier comme `my_script.py`.        | Sauvegarder votre travail.    |
| Jupyter Notebook  | Exécutez `jupyter notebook` dans le terminal. | Exploration pas à pas.        |

- **REPL** signifie Read-Eval-Print Loop (boucle lire-évaluer-afficher).
  C'est une invite interactive où vous tapez une ligne de Python à la fois et
  voyez le résultat immédiatement.
- Un **fichier script** est un fichier texte simple se terminant par `.py` que
  vous exécutez en une seule fois.
- Un **Jupyter Notebook** est un outil qui vous permet de mélanger texte, code
  et résultats dans un seul document. Il n'est pas installé avec `ddi-l` :
  exécutez d'abord `pip install notebook` si vous voulez en utiliser un.

Comment choisir :

- Utilisez le **REPL** pour une vérification ponctuelle que vous n'avez pas
  besoin de garder, comme afficher la version.
- Utilisez un **fichier script** quand vous voulez garder votre code et le
  réexécuter depuis le début avec une seule commande, comme
  `python my_script.py`.
- Utilisez un **notebook** quand vous voulez voir les notes, le code et les
  résultats ensemble, pas à pas, par exemple pour montrer votre travail à un
  collègue.

Pour ce programme de formation, les trois options fonctionnent.

---

## Exercices

!!! example "Scénario"
    Vous préparez un nouvel ordinateur portable pour un atelier de formation.
    Vous devez vous assurer que Python et `ddi-l` sont prêts avant le
    début de l'atelier.

**Exercice 1 (O1).** Exécutez `python --version` (ou `python3 --version`)
dans votre terminal. Notez la version et dites si elle est assez récente
pour `ddi-l`.

Résultat attendu : une ligne comme `Python 3.12.3`, et un oui ou un non.

??? success "Réponse"
    Par exemple, `Python 3.12.3` : oui, car 3.12 est 3.11 ou plus récent. Si
    vous voyez `Python 3.10.12` ou plus ancien, la réponse est non :
    installez un Python plus récent depuis <https://www.python.org/downloads/>
    avant de continuer.

**Exercice 2 (O2).** Exécutez la commande suivante dans votre terminal :

```bash
pip install ddi-l pandas openpyxl
```

Collez la **dernière ligne** de la sortie et dites ce qu'elle signifie.

Résultat attendu : une ligne qui commence par `Successfully installed` ou
`Requirement already satisfied`.

??? success "Réponse"
    La dernière ligne commence par `Successfully installed` et mentionne
    `ddi-l-...` parmi les paquets (la version peut varier). Si les paquets étaient
    déjà installés, pip affiche plutôt `Requirement already satisfied`. Dans les
    deux cas, vous êtes prêt. Une ligne qui commence par `ERROR` signifie que
    l'installation a échoué.

**Exercice 3 (O3).** Ouvrez une session Python et exécutez :

```python
import ddi_l as ddi

print(ddi.__version__)
```

Notez le numéro de version que vous voyez.

Résultat attendu : un numéro de version, comme `0.1.0`.

??? success "Réponse"
    La version installée, par exemple `0.1.0` ou plus récente. Si vous voyez
    plutôt `ModuleNotFoundError`, `ddi-l` n'est pas installé dans ce Python :
    revenez à l'exercice 2.

**Exercice 4 (O4).** Exécutez `ddi --help` dans votre terminal. Lisez les
descriptions et notez la commande que vous utiliseriez pour chaque tâche :

1. Vérifier un fichier DDI par rapport au schéma DDI.
2. Signaler les problèmes de qualité d'un fichier DDI, comme des libellés
   manquants.
3. Lister les versions du schéma DDI que `ddi-l` prend en charge.

Résultat attendu : trois noms de commandes.

??? success "Réponse"
    1. `validate` (« Validate an XML document against the DDI schema. »)
    2. `lint` (« Lint a DDI document and report findings as JSON. »)
    3. `versions` (« List supported DDI schema releases. »)

**Exercice 5 (O5).** Choisissez un espace de travail pour chaque tâche et
justifiez votre choix en une phrase :

1. Vérifier une seule fois que `import ddi_l` fonctionne sur le nouvel
   ordinateur.
2. Écrire l'étude que vous construirez au module 3, pour pouvoir la
   réexécuter la semaine prochaine après l'avoir modifiée.
3. Montrer à un collègue, pas à pas, comment l'étude est construite, avec
   des notes entre les morceaux de code.

Résultat attendu : trois espaces de travail, chacun avec une raison.

??? success "Réponse"
    1. **Python REPL :** c'est le moyen le plus rapide d'exécuter une ligne
       que vous n'avez pas besoin de garder.
    2. **Fichier script :** il garde votre code, et `python my_script.py` le
       réexécute depuis le début.
    3. **Notebook :** il montre les notes, le code et les résultats ensemble,
       pas à pas.

    D'autres choix conviennent si votre raison tient ; par exemple, un
    notebook garde aussi votre code pour la tâche 2.

---

## Quiz

???+ question "Question 1 (O1) : `python --version` affiche `Python 3.10.12`. Que devez-vous faire avant d'installer ddi-l ?"
    **A.** Rien. Toute version de Python 3 fonctionne.

    **B.** Installer Python 3.11 ou plus récent.

    **C.** Exécuter `pip install ddi-l` deux fois.

    **D.** Passer à Python 2.7.

    ??? success "Réponse"
        **B.** `ddi-l` nécessite Python 3.11 ou plus récent, et 3.10 est plus
        ancien. Installez un Python plus récent, puis installez `ddi-l` avec
        celui-ci.

???+ question "Question 2 (O2) : La dernière ligne de `pip install ddi-l pandas openpyxl` indique `Requirement already satisfied`. Qu'est-ce que cela signifie ?"
    **A.** L'installation a échoué et doit être relancée.

    **B.** pip a besoin des droits d'administrateur.

    **C.** Les paquets doivent d'abord être supprimés.

    **D.** Le paquet était déjà installé : pip n'avait rien à faire.

    ??? success "Réponse"
        **D.** `Requirement already satisfied` signifie que le paquet est
        déjà là. Une installation qui échoue se termine par une ligne qui
        commence par `ERROR`.

???+ question "Question 3 (O3) : Vous exécutez `import ddi_l as ddi` et obtenez `ModuleNotFoundError: No module named 'ddi_l'`. Quelle est la cause la plus probable ?"
    **A.** `ddi-l` n'est pas installé dans le Python que vous utilisez.

    **B.** L'import doit s'écrire `import ddi-l`.

    **C.** Vous devez appeler `ddi.__version__` avant l'import.

    **D.** Le paquet ne fonctionne que dans un notebook.

    ??? success "Réponse"
        **A.** Python ne trouve pas le paquet : il n'est donc pas installé
        pour ce Python. Relancez `pip install ddi-l`, ou
        `python3 -m pip install ddi-l` si vous démarrez Python avec
        `python3`. L'option B n'est pas du Python valide : un trait d'union
        ne peut pas figurer dans un nom d'import, c'est pourquoi le module
        s'appelle `ddi_l`.

???+ question "Question 4 (O4) : Vous voulez vérifier un fichier par rapport au schéma DDI depuis le terminal. Quelle commande de la liste `ddi --help` utilisez-vous ?"
    **A.** `roundtrip`

    **B.** `to-json`

    **C.** `validate`

    **D.** `serve`

    ??? success "Réponse"
        **C.** Sa description dit « Validate an XML document against the DDI
        schema. » `roundtrip` réécrit un fichier, `to-json` le convertit et
        `serve` lance l'API HTTP.

???+ question "Question 5 (O5) : Vous allez construire une étude sur plusieurs jours et voulez tout réexécuter depuis le début avec une seule commande après chaque modification. Quel espace de travail convient le mieux ?"
    **A.** Le Python REPL, en retapant chaque ligne.

    **B.** Un fichier script, comme `build_study.py`, exécuté avec
    `python build_study.py`.

    **C.** Un document texte que vous copiez-collez dans le REPL.

    **D.** Le terminal, en exécutant `ddi --help`.

    ??? success "Réponse"
        **B.** Un fichier script garde votre code, et une seule commande le
        réexécute en entier. Le REPL oublie ce que vous avez tapé quand vous
        le fermez.

---

## Pour aller plus loin (facultatif)

Pour des configurations avancées (comme l'installation avec uv ou Poetry, ou
l'ajout du moteur optionnel `lxml` pour une lecture plus rapide), consultez le
guide complet d'[Installation](../installation.fr.md).

---

## Faites le point

- [ ] Je peux exécuter `python --version` et décider si mon Python est assez
  récent pour `ddi-l`. (O1)
- [ ] Je peux installer `ddi-l`, `pandas` et `openpyxl` avec `pip` et lire
  la dernière ligne de la sortie. (O2)
- [ ] Je peux exécuter un test Python de deux lignes qui affiche la version
  de `ddi-l`. (O3)
- [ ] Je peux exécuter `ddi --help` et trouver la commande qui fait une
  tâche donnée. (O4)
- [ ] Je peux choisir un espace de travail pour une tâche et justifier ce
  choix en une phrase. (O5)

---

!!! tip "Notes pour l'instructeur"
    - **Prévoyez du temps supplémentaire** pour les problèmes d'environnement.
      Les problèmes de version de Python, les erreurs de permissions et les
      problèmes de réseau sont courants lors des ateliers en direct.
    - **Ayez une solution de secours** prête : un notebook en ligne (comme
      Google Colab) ou un conteneur pré-configuré avec tout installé.
    - **Pourquoi installer pandas maintenant ?** L'installer ici évite de
      perturber le Module 8, où les apprenants chargeront des fichiers CSV et
      Excel. Faire l'installation tôt permet aux modules suivants de rester
      concentrés sur DDI.
    - **Exercice 4 :** Le nombre de commandes augmente d'une version à
      l'autre ; demandez donc aux apprenants de trouver les commandes par
      leur description plutôt que de les compter.
    - **Mettez en binôme** les apprenants qui finissent tôt avec ceux qui ont
      besoin d'aide. Les problèmes d'installation sont plus faciles à résoudre
      à deux.
