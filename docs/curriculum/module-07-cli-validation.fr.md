---
description: >-
  Module 7 du cours ddi-l : valider, analyser, convertir et faire l'aller-
  retour de fichiers DDI avec la commande ddi, et utiliser les codes de
  sortie.
---

# Module 7 : Valider depuis la ligne de commande

!!! info "Ce que vous apprendrez"
    - Exécuter `ddi validate` pour vérifier un fichier DDI.
    - Lire et comprendre le résultat de la validation.
    - Utiliser `ddi lint` pour vérifier les règles de qualité au-delà du schéma.
    - Exporter un fichier DDI en JSON avec `ddi to-json`.
    - Normaliser un fichier avec `ddi roundtrip`.
    - Comprendre les codes de sortie et pourquoi ils sont importants pour les scripts.

**Prérequis :** [Module 6 : Ouvrir, modifier et ré-enregistrer des fichiers DDI existants](module-06-open-modify.md).

**Durée :** 30 min en autonomie / 40 min avec instructeur.

---

## 1. Pourquoi utiliser la ligne de commande ?

Jusqu'ici, vous avez écrit des scripts Python pour travailler avec des fichiers DDI. Mais parfois vous voulez juste vérifier un fichier rapidement sans écrire de code. La **ligne de commande** (aussi appelée terminal ou shell) vous permet de faire cela.

La ligne de commande est aussi utile quand vous devez :

- **Traiter plusieurs fichiers à la fois.** Vous pouvez valider 20 fichiers avec une seule commande.
- **Automatiser les vérifications.** Vous pouvez ajouter la validation à un script qui s'exécute chaque nuit.
- **Intégrer dans des pipelines CI/CD.** Un **pipeline CI/CD** est un système automatisé qui construit et teste les logiciels. Beaucoup d'équipes utilisent des pipelines pour détecter les erreurs tôt.

`ddi-l` inclut un outil en ligne de commande appelé `ddi`. Vous l'avez installé quand vous avez installé le paquet `ddi-l` (voir Module 2).

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

Si le fichier contient des erreurs, vous voyez une entrée par problème. Par exemple :

```text
error: Element 'BadElement': This element is not expected. (line 42, column 12)
    at /DDIInstance/s:StudyUnit
1 issue found.
```

Chaque erreur vous dit :

- **ce qui ne va pas** : le message après `error:`.
- **où** : la ligne et la colonne dans le fichier XML, et l'XPath après `at`.

Vous pouvez utiliser cette information pour trouver et corriger l'erreur. Pour
les scripts, ajoutez `--format json` afin d'obtenir les mêmes informations sous
forme de liste JSON (une liste vide `[]` lorsque le fichier est valide).

---

## 3. Lire le résultat

Quand vous voyez `"Document is valid."`, cela signifie que le fichier suit toutes les règles du schéma DDI. Aucune action n'est nécessaire.

Quand vous voyez des erreurs, lisez chaque message attentivement. Les erreurs les plus courantes sont :

| Type d'erreur              | Ce que cela signifie                          |
| -------------------------- | --------------------------------------------- |
| Element not expected       | Un élément XML est au mauvais endroit.        |
| Missing child element      | Un élément obligatoire est manquant.          |
| Invalid value              | Une valeur texte ne respecte pas les règles.  |

Corrigez les erreurs dans votre script Python (ou directement dans le fichier XML), puis exécutez `ddi validate` à nouveau.

---

## 4. Vérifier la qualité d'un fichier

La commande `ddi lint` vérifie les **règles de qualité** qui vont au-delà du schéma. Elle applique les mêmes règles que `doc.lint()`, utilisé au [module 3](module-03-first-study.md#9-verifier-votre-travail). Le **linting** consiste à chercher des problèmes qui sont techniquement permis par le schéma mais qui sont généralement des erreurs ou des mauvaises pratiques.

```bash
ddi lint my-study.xml
```

Par exemple, une règle de linting peut vous avertir qu'une variable n'a pas de question liée, ou qu'un concept n'a pas de description. Le fichier est toujours du XML valide, mais les métadonnées sont incomplètes.

Le résultat est une liste de constats, chacun avec un niveau de gravité (comme « warning » ou « info ») et un court message.

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

Pourquoi est-ce important ? Parce que les scripts et les pipelines peuvent vérifier le code de sortie pour décider quoi faire ensuite. Par exemple :

```bash
ddi validate my-study.xml && echo "All good!" || echo "Fix the errors."
```

Cette ligne dit : « Exécutez `ddi validate`. Si la commande réussit (code de sortie 0), affichez 'All good!'. Si elle échoue (code de sortie 1), affichez 'Fix the errors.' »

Vous pouvez aussi vérifier le code de sortie de la dernière commande avec `$?` :

```bash
ddi validate my-study.xml
echo $?
```

Si le fichier est valide, `echo $?` affiche `0`. Sinon, il affiche `1`.

---

## Exercices

!!! example "Scénario"
    Un bureau national de statistique possède 20 fichiers DDI XML provenant
    de différentes équipes d'enquête. Il doit tous les valider, en exporter
    un en JSON et produire une copie normalisée.

**Exercice 1.** Validez `census-2024-updated.xml`, issu des exercices du module 6 (ou tout fichier d'un module précédent), avec `ddi validate`. Copiez le résultat.

Résultat attendu (si valide) :

```text
Document is valid.
```

??? success "Réponse"
    ```bash
    ddi validate census-2024-updated.xml
    ```

**Exercice 2.** Exportez le fichier en JSON avec `ddi to-json`. Comptez le nombre de lignes du JSON.

??? success "Réponse"
    ```bash
    ddi to-json census-2024-updated.xml --indent 2 > census-2024-updated.json
    wc -l census-2024-updated.json
    ```

    La commande `wc -l` compte le nombre de lignes dans un fichier. Votre nombre dépendra de la quantité de contenu dans le fichier.

**Exercice 3.** Faites un aller-retour du fichier. Comparez les tailles de l'entrée et de la sortie.

??? success "Réponse"
    ```bash
    ddi roundtrip census-2024-updated.xml --output census-2024-roundtrip.xml
    ls -l census-2024-updated.xml census-2024-roundtrip.xml
    ```

    La commande `ls -l` affiche les tailles des fichiers. Les deux fichiers devraient être proches en taille. De petites différences d'espacement sont normales.

---

## Quiz

???+ question "Question 1 : Que fait la commande ddi validate ?"
    **A.** Elle crée un nouveau fichier DDI à partir de zéro.

    **B.** Elle vérifie si un fichier DDI XML suit les règles du schéma DDI.

    **C.** Elle convertit un fichier DDI en tableur.

    **D.** Elle téléverse un fichier DDI vers un serveur.

    ??? success "Réponse"
        **B.** `ddi validate` vérifie le fichier par rapport au schéma DDI.
        Si le fichier suit toutes les règles, elle affiche « Document is
        valid. » Sinon, elle affiche une liste d'erreurs au format JSON.

???+ question "Question 2 : Que signifie le code de sortie 0 ?"
    **A.** La commande a trouvé 0 question dans le fichier.

    **B.** La commande a échoué et produit 0 résultat.

    **C.** La commande a réussi : tout va bien.

    **D.** Le fichier fait 0 octet.

    ??? success "Réponse"
        **C.** Le code de sortie 0 signifie succès. La commande s'est
        terminée sans erreur. Les scripts et les pipelines utilisent les
        codes de sortie pour décider quoi faire ensuite.

???+ question "Question 3 : Que produit ddi to-json ?"
    **A.** Un script Python.

    **B.** Un fichier JSON qui contient les mêmes données que le fichier DDI XML.

    **C.** Un tableur CSV.

    **D.** Un rapport PDF.

    ??? success "Réponse"
        **B.** `ddi to-json` convertit un fichier DDI XML au format JSON.
        Le JSON est un format texte que beaucoup d'outils et de langages
        de programmation peuvent lire.

---

**Voir aussi :**

- [Recettes CLI](../cli-recipes.md)
- [Guide d'automatisation](../tutorials/automation-playbook.md)

---

!!! tip "Notes pour l'instructeur"
    - **Démo en direct.** Exécutez `ddi validate`, `ddi lint`, `ddi to-json`
      et `ddi roundtrip` sur un projecteur pour que les apprenants puissent
      voir le résultat en temps réel. Utilisez des fichiers des modules
      précédents.
    - **Cassez un fichier exprès.** Ouvrez un fichier XML valide dans un
      éditeur de texte. Supprimez une balise fermante ou ajoutez un élément
      inconnu. Puis exécutez `ddi validate` pour montrer à quoi ressemble
      une erreur. Corrigez-la et revalidez.
    - **Validation par lots.** Montrez comment valider plusieurs fichiers
      à la fois :
      `for f in *.xml; do echo "--- $f ---"; ddi validate "$f"; done`
    - **Codes de sortie en pratique.** Écrivez un court script bash qui
      valide un fichier et affiche un message selon le code de sortie.
      Cela prépare les apprenants à l'intégration CI/CD.
    - **JSON comme passerelle.** Expliquez que le résultat JSON peut être
      chargé par d'autres outils (R, JavaScript, catalogues de données).
      C'est utile pour les équipes qui n'utilisent pas Python.
    - **Note de durée.** Ce module contient moins de code Python et plus de
      compétences en ligne de commande. Si votre public est moins à l'aise
      avec le terminal, passez plus de temps sur la section 1 et les
      exercices.
