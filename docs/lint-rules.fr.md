---
description: >-
  Toutes les règles lint de ddi-l, générées à partir du registre des règles :
  ce que chacune signale, sa gravité, les profils qui l'exécutent et un
  exemple de constat.
---

# Référence des règles lint

`ddi lint` et `ddi_l.lint.run_lint()` vérifient un document selon des règles
lint, regroupées en profils. Cette page est générée à partir du registre des
règles : elle énumère toutes les règles de la version installée, avec un
exemple de ce que chacune signale.

!!! note "Descriptions en anglais"
    La description de chaque règle provient de sa docstring, rédigée en
    anglais ; les intitulés autour sont traduits.

Exécuter le profil par défaut, un profil nommé ou des règles choisies :

```bash
ddi lint etude.xml
ddi lint export.xml --profile colectica-questionnaire --format table
ddi lint export.xml --rules colectica.condition.empty,text.pipe-malformed
ddi lint --list-rules --list-format table
```

Un constat est une `error`, un `warning` ou une `info`. Seules les erreurs
font échouer `ddi lint`, sauf si `--fail-severity warning` ou
`--fail-severity info` demande un contrôle plus strict. Ignorez une règle avec
`--skip-rule RÈGLE`.

## Configurer les règles

Les règles marquées *heuristic* devinent l'intention d'après la formulation
ou la mise en page, et signalent au plus un avertissement. Certaines règles
dépendent de conventions qui varient d'un organisme à l'autre ; leurs options
sont vides au départ, si bien que la règle ne fait rien tant que vous ne la
configurez pas.

| Option | Utilisée par | Valeur par défaut |
| --- | --- | --- |
| `required_languages` | `i18n.missing-language` | aucune : la règle est inactive |
| `placeholder_patterns` | `text.placeholder-unresolved` | `‹‹…››`, `<<…>>`, `«insert…»`, `[insert …]`, « insert survey-specific » |
| `ui_chrome_tokens` | `text.ui-chrome` | aucune : la règle est inactive |
| `logic_note_patterns` | `colectica.statement.logic-note` | « Flow condition », « Display condition », « Logic: » et leurs équivalents français |
| `gate_description_patterns` | `colectica.ifthenelse.partial-gate` | « go to … page », « aller à la page », « passer à la page » |
| `known_names` | `text.pipe-undeclared` | aucune |
| `variable_code_pattern` | `colectica.domain.label-mismatch` | aucune : la règle est inactive |
| `pipe_prefixes` | `text.pipe-malformed` | aucune |
| `pipe_suffixes` | `text.pipe-undeclared` | aucune |

En ligne de commande, `--required-language` (répété) et `--known-names
FICHIER` (un nom par ligne) fixent les deux options dont la plupart des projets
ont besoin, et `--lint-config FICHIER` fixe n'importe quelle option à partir
d'un objet JSON :

```json
{
  "required_languages": ["en-CA", "fr-CA"],
  "ui_chrome_tokens": ["Précédent", "Suivant", "Enregistrer et terminer plus tard"],
  "variable_code_pattern": "Q\\d{3}",
  "pipe_suffixes": ["_E", "_F"]
}
```

En Python, `lint_configuration()` accepte les mêmes options et donne une
configuration pour un seul appel, sans changer les autres :

```python
from ddi_l import read_ddi
from ddi_l.lint import lint_configuration, run_lint

document = read_ddi("mon-etude.xml")
bilingue = lint_configuration(required_languages=["en-CA", "fr-CA"])
constats = run_lint(document, configuration=bilingue)
```

`run_profile()`, `document.lint()` et les fonctions `validate_*()`
l'acceptent aussi. `configure_lint()` fixe les mêmes options comme valeur
par défaut de tous les appels du processus qui n'en reçoivent pas.

<!-- lint-rules -->
