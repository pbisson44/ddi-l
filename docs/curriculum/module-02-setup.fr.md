# Module 2 : Préparer votre environnement Python

!!! info "Ce que vous apprendrez"
    - Installer Python et vérifier la version.
    - Installer `ddi-l` et les paquets utilitaires.
    - Confirmer que tout fonctionne en exécutant un test rapide.
    - Choisir un espace de travail pour écrire du code Python.

**Prérequis :** [Module 1 : Qu'est-ce que les métadonnées et pourquoi sont-elles importantes ?](module-01-what-is-metadata.md)

**Durée :** 20 min en autonomie / 30 min avec instructeur.

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

Le numéro de version doit être **3.11 ou supérieur**. Si votre version est
plus ancienne, visitez <https://www.python.org/downloads/> et installez une
version plus récente.

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

---

## 3. Vérifier que tout fonctionne

### 3a. Tester l'outil en ligne de commande

`ddi-l` inclut un outil en ligne de commande appelé `ddi`. Exécutez :

```bash
ddi --help
```

Vous devriez voir une liste de commandes disponibles. Cela confirme que
l'outil est installé et prêt à être utilisé.

### 3b. Tester dans Python

Ouvrez une session Python en tapant `python` dans votre terminal. Puis tapez :

```python
import ddi_l as ddi

print(ddi.__version__)
```

Vous devriez voir un numéro de version affiché, comme `0.1.0`. Cela confirme
que Python peut trouver et charger le paquet `ddi-l`.

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
  et résultats dans un seul document.

Pour ce programme de formation, les trois options fonctionnent.

---

## 5. Options d'installation avancées

Pour des configurations avancées (comme l'installation depuis le code
source, l'utilisation de Poetry, ou l'ajout du moteur optionnel `lxml`),
consultez le guide complet d'[Installation](../installation.md).

---

## Exercices

!!! example "Scénario"
    Vous préparez un nouvel ordinateur portable pour un atelier de formation.
    Vous devez vous assurer que Python et `ddi-l` sont prêts avant le
    début de l'atelier.

**Exercice 1.** Exécutez la commande suivante dans votre terminal :

```bash
pip install ddi-l pandas openpyxl
```

Collez la **dernière ligne** de la sortie. Elle dit généralement quelque chose
comme `Successfully installed ...`.

**Exercice 2.** Ouvrez une session Python et exécutez :

```python
import ddi_l as ddi

print(ddi.__version__)
```

Notez le numéro de version que vous voyez.

**Exercice 3.** Exécutez `ddi --help` dans votre terminal. **Combien de
commandes** sont listées dans la sortie ?

---

## Quiz

???+ question "Question 1 : Quelle est la version minimale de Python pour ddi-l ?"
    **A.** Python 2.7

    **B.** Python 3.8

    **C.** Python 3.11

    **D.** Python 3.14

    ??? success "Réponse"
        **C.** `ddi-l` nécessite Python 3.11 ou plus récent.

???+ question "Question 2 : Quelle commande affiche l'aide de l'outil en ligne de commande ddi-l ?"
    **A.** `python --help`

    **B.** `pip --help`

    **C.** `ddi --help`

    **D.** `ddi-l --help`

    ??? success "Réponse"
        **C.** La commande `ddi --help` affiche la liste des commandes
        disponibles dans l'outil en ligne de commande `ddi-l`.

???+ question "Question 3 : Que fait pip install ?"
    **A.** Elle supprime les anciens fichiers Python.

    **B.** Elle télécharge et installe un paquet Python depuis Internet.

    **C.** Elle ouvre un navigateur web.

    **D.** Elle crée un nouveau script Python.

    ??? success "Réponse"
        **B.** `pip install` télécharge un paquet depuis PyPI (le Python
        Package Index) et l'installe sur votre ordinateur pour que vous
        puissiez l'utiliser.

---

!!! tip "Notes pour l'instructeur"
    - **Prévoyez du temps supplémentaire** pour les problèmes d'environnement.
      Les problèmes de version de Python, les erreurs de permissions et les
      problèmes de réseau sont courants lors des ateliers en direct.
    - **Ayez une solution de secours** prête : un notebook en ligne (comme
      Google Colab) ou un conteneur pré-configuré avec tout installé.
    - **Pourquoi installer pandas maintenant ?** L'installer ici évite de
      perturber le Module 6, où les apprenants chargeront des fichiers CSV et
      Excel. Faire l'installation tôt permet aux modules suivants de rester
      concentrés sur DDI.
    - **Mettez en binôme** les apprenants qui finissent tôt avec ceux qui ont
      besoin d'aide. Les problèmes d'installation sont plus faciles à résoudre
      à deux.
