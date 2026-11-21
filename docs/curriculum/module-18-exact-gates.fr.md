---
description: >-
  Module 18 facultatif du cours ddi-l : avec l'extra logic, décider si deux
  filtres valent pour les mêmes répondants, nommer un répondant sur lequel ils
  divergent, et tester un filtre sur des répondants de votre choix.
---

# Module 18 (facultatif) : Comparer exactement des filtres

!!! info "Objectifs d'apprentissage"
    À la fin de ce module, vous pouvez :

    - **O1.** Vérifier avec `decide()` si deux filtres valent pour les mêmes
      répondants, et lire son verdict : `equivalent`, `different` avec un
      répondant qui les distingue, ou `unknown` avec une raison.
    - **O2.** Donner à `decide()` le type de chaque question, tiré des
      domaines de réponse de la spécification, et expliquer pourquoi une
      question dont la réponse est un nombre entier peut faire concorder deux
      filtres.
    - **O3.** Tester un filtre avec `evaluate()` sur des répondants de votre
      choix : un qui a laissé la question vide, un qui l'a refusée, un qui y a
      répondu sans valeur, et un qui a donné une valeur.
    - **O4.** Relire des filtres traduits d'un document de spécification et,
      pour chaque filtre qui diffère du filtre voulu, nommer un répondant
      qu'il achemine mal.
    - **O5.** Dire ce que l'extra `logic` change dans `equivalent()` et
      `ddi conform`, et ce qu'ils font sans lui.

**Prérequis :** [Module 16](module-16-advanced-questionnaire-spec.fr.md).
Ce module est facultatif : le projet de synthèse n'en a pas besoin.

!!! warning "Installez d'abord les extras spec et logic"
    Ce module demande l'extra `spec` du Module 16 et l'extra `logic`, qui
    ajoute le solveur Z3 (environ 57 Mo). `pip install ddi-l` seul
    n'installe ni l'un ni l'autre :

    ```bash
    pip install -U "ddi-l[spec,logic]"
    ```

**Durée :** 45 min en autonomie / 60 min avec instructeur.

**Nouveau dans ce module :** `decide()`, son verdict (`outcome`, `example`,
`reason`), `Example.describe()`, `evaluate()`, `Answer`, l'argument `types`,
`equivalent(exact=...)` et `ddi conform --semantics`.

---

## 1. Ce qu'une forme normale ne peut pas vous dire

Au Module 16, `normalise()` a mis chaque filtre sous une forme normale, et
`equivalent()` a comparé ces formes. Une forme normale développe ce qui est
abrégé et déplace `not` vers l'intérieur, mais elle ne calcule rien. Deux
filtres qui concordent toujours peuvent donc avoir des formes normales
différentes :

```python
from ddi_l.spec import equivalent

print(equivalent("PetCount > 0", "PetCount >= 1", exact=False))  # -> False
```

`exact=False` ne demande que les formes normales, ce qui est tout ce que fait
`equivalent()` sans l'extra `logic`. `False` veut alors seulement dire
« écrits différemment ». Cela ne veut pas dire qu'un ménage est acheminé
autrement.

L'extra `logic` ajoute un **solveur** : un programme qui cherche, parmi tous
les répondants possibles, un répondant sur lequel deux filtres divergent.
S'il n'en trouve aucun, les filtres sont équivalents. S'il en trouve un, il
vous montre ce répondant.

## 2. Vérifier que l'extra est installé

`decide()` interroge le solveur. Sans l'extra, il lève
`LogicDependencyError`, qui dit quoi installer :

```python
from ddi_l.spec import LogicDependencyError, decide

try:
    print(decide("x > 3", "x >= 4").outcome)  # -> different
except LogicDependencyError as error:
    print(error)
```

Si vous voyez `different`, l'extra fonctionne. Si vous voyez
`Deciding expressions needs z3-solver: pip install "ddi-l[logic]"`, lancez
cette commande.

## 3. Trois verdicts

`decide(left, right)` renvoie un **verdict** en trois parties :

| Partie | Ce qu'elle contient |
| --- | --- |
| `outcome` | `"equivalent"`, `"different"` ou `"unknown"` |
| `example` | Pour `different` : un répondant pour qui un filtre vaut et l'autre non |
| `reason` | Pour `unknown` : pourquoi le solveur n'a pas pu décider |

```python
same = decide("PetAge + 1 > 11", "PetAge > 10")
print(same.outcome)  # -> equivalent

apart = decide("answered(PetKind) and PetAge > 30", "PetAge > 30")
print(apart.outcome)  # -> different
print(apart.example.describe())  # -> PetAge is 31 and PetKind is empty

unsure = decide('PetName = "Rex"', 'PetName < "S"')
print(unsure.outcome)  # -> unknown
print(unsure.reason)  # -> PetName < "S" compares text by order
```

- La première paire fait de l'arithmétique : `PetAge + 1 > 11` est vrai
  exactement quand `PetAge > 10` l'est. La normalisation ne pouvait pas le
  voir ; le solveur, si.
- La deuxième paire diffère pour un animal de 31 ans dont la sorte a été
  laissée vide. Seul le premier filtre demande une réponse à `PetKind`.
- La troisième paire compare du texte par ordre alphabétique, ce que le
  solveur ne modélise pas. `unknown` est honnête : vérifiez un tel filtre à
  la main.

`describe()` décrit le répondant par une phrase, en anglais. Une question que
la phrase ne nomme pas a été laissée vide, sauf si la phrase dit autre chose.

!!! tip "Un répondant suffit"
    Un verdict `different` donne un répondant, pas tous. Corrigez le filtre,
    puis relancez `decide()` : il peut en trouver un autre. Une autre version
    du solveur peut aussi choisir un autre répondant que ceux affichés ici ;
    tout répondant qu'il donne est un répondant sur lequel les deux filtres
    divergent.

## 4. Qu'est-ce qu'un répondant ?

Le solveur essaie toutes les sortes de répondants. Pour chaque question, un
répondant peut :

| Un répondant... | Dans `describe()` | Une comparaison comme `PetAge > 10` |
| --- | --- | --- |
| l'a laissée vide | `PetAge is empty` | est fausse |
| l'a refusée | `PetAge is refused` | est fausse |
| y a répondu sans valeur, comme « ne sait pas » | `PetAge is answered with no value` | est fausse |
| a donné une valeur | `PetAge is 12` | compare la valeur |
| a donné plusieurs valeurs (une question comparée seulement avec `=` et `!=`) | `PetKind is 1 and 2` | `PetKind = 1` est vraie si 1 est parmi elles |

`missing(x)` veut dire vide ou refusée. Une réponse sans valeur est une
réponse : elle ne manque donc pas. Cette troisième ligne est celle qu'on
oublie. Le Module 16 disait ces deux filtres de Q6 presque pareils :

```python
verdict = decide("not PetAge > 10", "PetAge <= 10 or missing(PetAge)")
print(verdict.outcome)  # -> different
print(verdict.example.describe())  # -> PetAge is answered with no value
```

Un répondant qui répond « ne sait pas » voit Q6 avec le premier filtre et la
saute avec le second. L'un comme l'autre peut être ce que veut une enquête ;
le solveur vous oblige à choisir sciemment.

## 5. Dire au solveur ce qu'est chaque question

Sauf indication contraire, le solveur permet à un nombre d'être une fraction :

```python
verdict = decide("PetCount > 0", "PetCount >= 1")
print(verdict.example.describe())  # -> PetCount is 0.25
```

Aucun ménage n'a un quart d'animal. La spécification le dit : `PetCount` a
`decimals: 0`. L'argument `types` transmet cette information. Il associe à
chaque nom `numeric`, `integer`, `date`, `text` ou `code` :

```python
print(decide("PetCount > 0", "PetCount >= 1", types={"PetCount": "integer"}).outcome)
# -> equivalent
```

Plutôt que d'écrire ces types à la main, lisez-les dans la spécification.
Cette fonction fait ce que fait `ddi conform` avec les domaines de réponse de
la spécification :

```python
from pathlib import Path

from ddi_l.spec import example_spec, load_spec

Path("pet-survey.spec.yaml").write_text(example_spec(), encoding="utf-8")
spec = load_spec("pet-survey.spec.yaml")


def spec_types(spec):
    """Ce que la spécification dit de chaque question, sous la forme que prend decide()."""
    types = {}
    for question in spec.questions:
        domain = question.domain
        if domain is None:
            continue
        if domain.kind == "numeric":
            types[question.id] = "integer" if domain.decimals == 0 else "numeric"
        else:
            types[question.id] = domain.kind
    return types


types = spec_types(spec)
print(types["PetCount"], types["PetKind"], types["VisitDate"])  # -> integer code date
```

Avec l'extra, `equivalent()` utilise lui aussi le solveur, et prend les mêmes
`types` :

```python
print(equivalent("PetCount > 0", "PetCount >= 1", types=types))  # -> True
```

## 6. Tester un filtre sur des répondants de votre choix

`decide()` cherche un répondant. `evaluate()` fait l'inverse : vous lui
donnez un répondant, et il dit si un filtre vaut pour lui. Un répondant est
un dictionnaire qui associe des noms de questions à des objets `Answer`. Un
`Answer` a un état (`"empty"`, `"refused"` ou `"answered"`) et, quand la
question a une réponse, un ensemble de valeurs. Les nombres sont des
`Fraction`, pour que `0.1` reste exact :

```python
from fractions import Fraction

from ddi_l.spec import Answer, evaluate

respondents = {
    "laissée vide": {},
    "refusée": {"PetAge": Answer("refused")},
    "ne sait pas": {"PetAge": Answer("answered")},
    "8 ans": {"PetAge": Answer("answered", frozenset({Fraction(8)}))},
    "12 ans": {"PetAge": Answer("answered", frozenset({Fraction(12)}))},
}
for gate in ("not PetAge > 10", "PetAge <= 10 or missing(PetAge)"):
    print(gate, [evaluate(gate, answers) for answers in respondents.values()])
# -> not PetAge > 10 [True, True, True, True, False]
# -> PetAge <= 10 or missing(PetAge) [True, True, False, True, False]
```

Les deux lignes ne diffèrent que dans une colonne, « ne sait pas », comme
l'a dit `decide()`. Un tableau comme celui-ci est un test du filtre : écrivez
d'abord les répondants, dites ce que le filtre doit faire pour chacun, puis
vérifiez.

Un verdict `different` se vérifie de la même façon : son `example` contient
des réponses que prend `evaluate()`. Reprenez le verdict de la section 5,
sans types :

```python
verdict = decide("PetCount > 0", "PetCount >= 1")
print(evaluate("PetCount > 0", verdict.example.answers))  # -> True
print(evaluate("PetCount >= 1", verdict.example.answers))  # -> False
```

## 7. Relire des filtres traduits

Un collègue a traduit en filtres les consignes « aller à » d'un document de
spécification. Vous avez les filtres que veut le responsable de l'enquête.
Vérifiez-les tous dans une seule boucle :

```python
intended = {
    "PetName": "answered(PetKind)",
    "VetVisits": "PetAge > 10",
    "Toys": "not PetAge > 10",
}
translated = {
    "PetName": "not empty(PetKind) and not refused(PetKind)",
    "VetVisits": "PetAge >= 11",
    "Toys": "PetAge <= 10",
}
for question, gate in intended.items():
    verdict = decide(gate, translated[question], types=types)
    if verdict.outcome == "different":
        print(f"{question}: differs when {verdict.example.describe()}")
    else:
        print(f"{question}: {verdict.outcome}")
# -> PetName: equivalent
# -> VetVisits: equivalent
# -> Toys: differs when PetAge is answered with no value
```

Deux traductions sont écrites autrement et sont justes. La troisième fait
sauter `Toys` à un répondant qui dit « ne sait pas ». C'est cette ligne qu'il
faut discuter avec votre collègue, pas les deux autres.

## 8. Dans `ddi conform`

Quand l'extra est installé, `ddi conform` compare les filtres et les
contrôles de saisie comme le fait `decide()`, dès que leurs formes normales
diffèrent. Il tire les types des domaines de la spécification, comme
`spec_types()`. Ainsi :

- un filtre écrit autrement qui concorde toujours avec celui de la
  spécification n'est pas signalé : `PetCount >= 1` passe pour une
  spécification qui dit `PetCount > 0` ;
- un filtre qui diffère nomme un répondant dans son message :

```text
Module pets is gated by PetCount > 1; the spec says PetCount > 0 (they differ when PetCount is 1).
```

`--semantics syntactic` ne compare que les formes normales, comme sans
l'extra ; `--semantics smt` échoue quand l'extra n'est pas installé. Depuis
Python, passez `semantics="syntactic"` ou `semantics="smt"` à `conform()`.

| | Sans l'extra `logic` | Avec lui |
| --- | --- | --- |
| `equivalent()` | Compare les formes normales : `False` peut être une fausse alerte | Décide : `False` veut dire qu'un répondant est acheminé autrement |
| `decide()` | Lève `LogicDependencyError` | Renvoie un verdict |
| `ddi conform` | Signale chaque filtre écrit autrement | Ne signale que les filtres qui diffèrent, avec un répondant |

## 9. Limites

- **Certaines comparaisons ne sont pas modélisées.** Du texte comparé par
  ordre, un nom comparé à la fois à des nombres et à du texte, et une valeur
  utilisée comme condition donnent `unknown`. Vérifiez ces filtres à la main.
- **La liste de codes n'est pas lue.** `decide()` sait que `PetKind` est un
  code, mais pas quels codes il a : un répondant peut donc répondre par un
  code absent de votre liste.
- **Une limite de travail borne le solveur**, et non une horloge : la même
  paire de filtres reçoit donc le même verdict à chaque exécution, quelle que
  soit la charge de la machine. Une paire trop difficile à décider dans cette
  limite est `unknown`.

---

!!! example "Scénario"
    L'équipe de l'enquête sur les animaux relit une nouvelle version du
    questionnaire. Un collègue a traduit en filtres les sauts du document de
    spécification, et l'équipe de développement a changé quelques filtres
    « pour les simplifier ». Avant que quoi que ce soit parte sur le terrain,
    vous comparez chaque filtre changé à la spécification et dressez la liste
    de chaque répondant qui verrait maintenant d'autres questions.

---

## Exercices

1. **(O1)** Prédisez le verdict de chaque paire, puis vérifiez-le avec `decide()`. Pour chaque `different`, affichez le répondant ; pour chaque `unknown`, la raison. (a) `missing(PetKind)` et `empty(PetKind) or refused(PetKind)`. (b) `PetAge > 10` et `PetAge * 2 > 20`. (c) `PetKind = 1 or PetKind = 2` et `PetKind != 3`. (d) `PetName = "Rex"` et `PetName < "S"`.

    **Résultat attendu :**

    ```text
    equivalent
    equivalent
    different: PetKind is another value
    unknown: PetName < "S" compares text by order
    ```

    ??? success "Réponse"

        ```python
        pairs = [
            ("missing(PetKind)", "empty(PetKind) or refused(PetKind)"),
            ("PetAge > 10", "PetAge * 2 > 20"),
            ("PetKind = 1 or PetKind = 2", "PetKind != 3"),
            ('PetName = "Rex"', 'PetName < "S"'),
        ]
        for left, right in pairs:
            verdict = decide(left, right, types=types)
            if verdict.outcome == "different":
                print(f"different: {verdict.example.describe()}")
            elif verdict.outcome == "unknown":
                print(f"unknown: {verdict.reason}")
            else:
                print(verdict.outcome)
        ```

        (a) est la définition de `missing()`. (b) est de l'arithmétique. (c) diffère pour un code qu'aucun des deux filtres ne nomme : le solveur ne lit pas la liste `Species`, si bien que pour lui un quatrième code existe. Un répondant qui a deux codes, 1 et 3, les distingue aussi. (d) compare du texte par ordre, ce que le solveur ne modélise pas.

2. **(O2)** Sans `types`, `decide("PetAge > 30", "PetAge >= 31")` répond `different`. Affichez le répondant. Décidez ensuite la paire à nouveau avec les types de la spécification, et expliquez le changement.

    **Résultat attendu :**

    ```text
    PetAge is 30.25
    equivalent
    ```

    ??? success "Réponse"

        ```python
        print(decide("PetAge > 30", "PetAge >= 31").example.describe())  # -> PetAge is 30.25
        print(decide("PetAge > 30", "PetAge >= 31", types=types).outcome)  # -> equivalent
        ```

        Sans types, un animal peut avoir 30,25 ans, ce que `PetAge > 30` accepte et `PetAge >= 31` refuse. La spécification donne à `PetAge` `decimals: 0` : `spec_types()` en fait donc un `integer`, et aucun nombre entier ne se trouve entre 30 et 31.

3. **(O3)** Le contrôle `age_range` de la spécification se déclenche quand `PetAge > 30`. Un second contrôle devrait se déclencher quand l'âge manque. Avec les `respondents` de la section 6 et un animal de 31 ans en plus, affichez pour chaque répondant si `PetAge > 30` se déclenche, puis si `missing(PetAge)` se déclenche. Quel répondant sans âge utilisable n'est attrapé par aucun des deux ? Écrivez un troisième contrôle qui n'attrape que ce répondant.

    **Résultat attendu :**

    ```text
    [False, False, False, False, False, True]
    [True, True, False, False, False, False]
    [False, False, True, False, False, False]
    ```

    ??? success "Réponse"

        ```python
        aged_31 = {"PetAge": Answer("answered", frozenset({Fraction(31)}))}
        everyone = [*respondents.values(), aged_31]
        print([evaluate("PetAge > 30", answers) for answers in everyone])
        print([evaluate("missing(PetAge)", answers) for answers in everyone])
        dont_know = "answered(PetAge) and not (PetAge > 30 or PetAge <= 30)"
        print([evaluate(dont_know, answers) for answers in everyone])
        ```

        Le répondant « ne sait pas » n'est attrapé par aucun des deux : sa réponse n'a pas de valeur, donc la comparaison est fausse, et c'est une réponse, donc elle ne manque pas. Les expressions n'ont pas de mot pour « ne sait pas », mais le troisième contrôle le dit : l'âge est répondu, et pourtant ni `PetAge > 30` ni `PetAge <= 30` n'est vrai, ce qui n'arrive que s'il n'y a aucune valeur à comparer.

4. **(O4)** L'enquête sur le logement du Module 16 pose `Own` (1 Oui, 2 Non), puis `YearsOwned` et `Mortgage` à tous ceux qui ne répondent pas « Non », puis `Refinanced` aux propriétaires depuis plus de 5 ans. Un collègue a écrit les filtres ci-dessous. Comparez chacun au filtre voulu, avec `Own` un code et `YearsOwned` un nombre entier, et affichez une ligne par question.

    ```python
    intended = {
        "YearsOwned": "not Own = 2",
        "Mortgage": "not Own = 2",
        "Refinanced": "YearsOwned > 5",
    }
    translated = {
        "YearsOwned": "not Own = 2",
        "Mortgage": "Own = 1",
        "Refinanced": "YearsOwned >= 6",
    }
    ```

    **Résultat attendu :**

    ```text
    YearsOwned: equivalent
    Mortgage: differs when Own is answered with no value
    Refinanced: equivalent
    ```

    ??? success "Réponse"

        ```python
        housing = {"Own": "code", "YearsOwned": "integer"}
        for question, gate in intended.items():
            verdict = decide(gate, translated[question], types=housing)
            if verdict.outcome == "different":
                print(f"{question}: differs when {verdict.example.describe()}")
            else:
                print(f"{question}: {verdict.outcome}")
        ```

        C'est `Mortgage` qu'il faut soulever. Avec `Own = 1`, un répondant qui répond « ne sait pas » à `Own`, ou qui la laisse vide ou la refuse, saute la question sur le prêt hypothécaire mais voit quand même `YearsOwned`. Soit les deux questions utilisent `not Own = 2`, soit le responsable de l'enquête décide qu'elles ne sont que pour les propriétaires, et les deux utilisent `Own = 1`. Les deux filtres écrits différemment pour `Refinanced` concordent pour tout nombre entier d'années.

5. **(O1, O3)** Montrez qu'un verdict `different` est juste : décidez `not PetAge > 10` contre `PetAge <= 10`, puis évaluez les deux filtres sur le répondant du verdict.

    **Résultat attendu :**

    ```text
    True
    False
    ```

    ??? success "Réponse"

        ```python
        verdict = decide("not PetAge > 10", "PetAge <= 10", types=types)
        print(evaluate("not PetAge > 10", verdict.example.answers))  # -> True
        print(evaluate("PetAge <= 10", verdict.example.answers))  # -> False
        ```

        Quel que soit le répondant que donne le solveur (un âge vide, refusé ou « ne sait pas »), un filtre vaut et l'autre non. `ddi-l` fait la même vérification sur chaque verdict `different` avant de le signaler.

6. **(O5)** Avec l'extra `logic`, `ddi conform` signale : `Module pets is gated by PetCount > 1; the spec says PetCount > 0 (they differ when PetCount is 1).` (a) Qui est mal acheminé, et quel côté corrigez-vous ? (b) L'instrument avait plutôt `PetCount >= 1`. Que signale `ddi conform` avec l'extra, et que signale-t-il sans lui ?

    ??? success "Réponse"

        (a) Un ménage qui a exactement un animal saute le module `pets`, alors que la spécification l'interroge sur son animal. La spécification est la référence : corrigez donc le filtre de l'instrument, à moins que le responsable de l'enquête ne dise que les ménages à un seul animal devaient sauter le module ; corrigez alors la spécification et donnez-lui une nouvelle version.

        (b) Avec l'extra, rien : la spécification dit que `PetCount` est un nombre entier, et pour les nombres entiers `PetCount >= 1` et `PetCount > 0` concordent. Sans lui, `spec.gate.different`, parce que les formes normales diffèrent. Ce constat est une fausse alerte, et c'est pourquoi le rapport montre les deux formes normales.

---

## Quiz

???+ question "Question 1 (O1) : decide() renvoie different. Que savez-vous ?"
    **A.** Les deux filtres sont écrits différemment.

    **B.** Au moins un répondant voit l'élément avec un filtre et pas avec l'autre, et `example` en contient un.

    **C.** Chaque répondant est acheminé autrement.

    **D.** Les filtres utilisent des questions différentes.

    ??? success "Réponse"
        **B.** Un verdict `different` vient avec un répondant sur lequel les
        filtres divergent. A est vrai, mais en dit moins : des filtres écrits
        différemment peuvent tout de même être équivalents. C et D ne
        s'ensuivent pas.

???+ question "Question 2 (O3) : Un répondant répond « ne sait pas » à PetAge. L'expression missing(PetAge) est-elle vraie ?"
    **A.** Oui : il n'y a pas d'âge.

    **B.** Non : la question a une réponse, sans valeur, et `missing()` veut dire vide ou refusée.

    **C.** Seulement avec l'extra `logic`.

    **D.** Seulement si `PetAge` est un nombre entier.

    ??? success "Réponse"
        **B.** `missing(x)` vaut `empty(x) or refused(x)`. Une réponse sans
        valeur n'est ni l'un ni l'autre, et toute comparaison qui la lit est
        fausse.

???+ question "Question 3 (O2) : Pourquoi decide() dit-il que PetCount > 0 et PetCount >= 1 diffèrent, tant que vous ne passez pas types ?"
    **A.** Parce que le solveur a un bogue avec `>=`.

    **B.** Parce que sans types un nombre peut être une fraction, comme 0,25, que le premier filtre accepte et que le second refuse.

    **C.** Parce que `PetCount` pourrait être du texte.

    **D.** Parce que l'un des deux lit une réponse vide comme 0.

    ??? success "Réponse"
        **B.** `types={"PetCount": "integer"}`, que `spec_types()` lit dans
        `decimals: 0`, exclut les fractions, et les deux concordent.

???+ question "Question 4 (O1) : decide() renvoie unknown. Que faites-vous ?"
    **A.** Traiter les filtres comme équivalents.

    **B.** Les traiter comme différents.

    **C.** Lire `reason`, puis vérifier cette paire de filtres à la main ou la réécrire sous une forme que le solveur modélise.

    **D.** Le relancer jusqu'à ce qu'il décide.

    ??? success "Réponse"
        **C.** `unknown` veut dire que le solveur n'a pas pu décider, pour la
        raison donnée. Le verdict est le même à chaque exécution : D n'aide
        donc pas.

???+ question "Question 5 (O5) : Sans l'extra logic, ddi conform signale spec.gate.different pour un filtre. Que pouvez-vous conclure ?"
    **A.** Un répondant est acheminé autrement.

    **B.** Les formes normales diffèrent. Les filtres peuvent quand même toujours concorder : comparez donc les deux formes normales du rapport, ou installez l'extra et relancez la vérification.

    **C.** L'instrument n'est pas du DDI valide.

    **D.** La spécification a tort.

    ??? success "Réponse"
        **B.** Sans l'extra, rien n'est calculé : `PetCount >= 1` contre
        `PetCount > 0` est signalé, bien qu'aucun ménage ne soit acheminé
        autrement.

---

## Faites le point

- [ ] Je peux vérifier deux filtres avec `decide()` et lire son verdict, son répondant ou sa raison. (O1)
- [ ] Je peux lire le type de chaque question dans la spécification, le passer dans `types`, et expliquer pourquoi un nombre entier change le verdict. (O2)
- [ ] Je peux tester un filtre avec `evaluate()` sur une question vide, refusée, répondue « ne sait pas » et répondue avec une valeur. (O3)
- [ ] Je peux relire des filtres traduits et nommer, pour chaque filtre faux, un répondant qu'il achemine autrement. (O4)
- [ ] Je peux dire ce que l'extra `logic` change dans `equivalent()` et `ddi conform`. (O5)

---

!!! tip "Notes pour l'instructeur"
    - Partez des deux filtres de Q6 du Module 16 (section 4). Demandez au
      groupe s'ils sont pareils avant de lancer `decide()`. La plupart
      disent oui.
    - La ligne « répondu sans valeur » de la section 4 surprend tout le
      monde. Demandez une vraie question où un « ne sait pas » devrait voir
      la question de suivi, et une où il ne le devrait pas.
    - La section 6 donne une habitude qui vaut plus que le solveur : écrivez
      les répondants et le résultat attendu avant de vérifier un filtre. Les
      testeurs font de même.
    - Si Z3 ne peut pas être installé sur les postes de formation, la
      section 1 et le premier exemple de la section 6 fonctionnent quand
      même : `equivalent(exact=False)` et `evaluate()` n'ont pas besoin de
      solveur. Montrez le reste au projecteur.

---

**Voir aussi :** [Module 16 : Spécification avancée de questionnaires](module-16-advanced-questionnaire-spec.fr.md) | [Vérifier un questionnaire par rapport à une spécification](../spec-conformance.fr.md)
