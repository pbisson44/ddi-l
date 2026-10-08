# Utiliser ddi-l depuis R

Les utilisateurs de R peuvent appeler `ddi-l` directement grâce à
[reticulate](https://rstudio.github.io/reticulate/), l'interface standard entre
R et Python. reticulate exécute Python dans votre session R et convertit les
valeurs dans les deux sens : aucun paquet R distinct n'est nécessaire, et toutes
les fonctionnalités de `ddi-l` sont disponibles.

Cette page présente les équivalents R des tâches courantes. Le
[Guide de l'utilisateur](user-guide.md) Python détaille chaque fonctionnalité ;
les appels sont les mêmes, avec `$` à la place de `.`.

## Installation

Installez reticulate une fois, puis créez un environnement Python pour `ddi-l` :

<!-- docs-test: skip -->
```r
install.packages("reticulate")

library(reticulate)
virtualenv_create("ddi-l")
py_install("ddi-l", envname = "ddi-l")   # ou "ddi-l[full]" pour une analyse plus rapide
```

À chaque session, sélectionnez cet environnement avant d'utiliser Python :

<!-- docs-test: skip -->
```r
library(reticulate)
use_virtualenv("ddi-l", required = TRUE)
```

!!! tip "reticulate 1.41 et versions ultérieures"
    `reticulate::py_require("ddi-l")` déclare la dépendance et laisse
    reticulate préparer automatiquement un environnement Python adapté, à la
    place des deux étapes ci-dessus.

Importez le paquet. L'objet `ddi` est le module Python `ddi_l` :

```r
library(reticulate)
ddi <- import("ddi_l")
ddi$`__version__`
```

## Créer une étude

```r
doc <- ddi$new_study(title = "Enquête ménages", agency = "example.org")

q_age <- doc$add_question(text = "Quel âge avez-vous ?", label = "Question sur l'âge", lang = "fr")
age <- doc$add_variable(name = "age", question = q_age, label = "Âge en années", lang = "fr")
age <- age$set_numeric("Integer", low = 0L, high = 120L)

doc$save("menages.xml")
print(doc)
# -> Document(title='Enquête ménages', agency='example.org', questions=1, variables=1)
```

Les objets du modèle restent attachés au document : vous pouvez continuer à
modifier `age` après `save()`, et l'enregistrement suivant inclut le changement.

## Construire une étude à partir d'un data frame

Parcourez les colonnes d'un data frame et décrivez chacune d'elles. L'exemple
lit le fichier d'exemple du programme ; enregistrez-le d'abord dans votre
répertoire de travail :

[:material-download: Télécharger `survey_sample.csv`](curriculum/survey_sample.csv){ .md-button download="survey_sample.csv" }

```r
survey <- read.csv("survey_sample.csv", stringsAsFactors = FALSE)

doc <- ddi$new_study(title = "Échantillon d'enquête", agency = "example.org")
for (column in names(survey)) {
  values <- survey[[column]]
  variable <- doc$add_variable(name = column, label = column)
  if (is.numeric(values)) {
    type <- if (all(values == round(values))) "Integer" else "Decimal"
    variable <- variable$set_numeric(
      type,
      low = as.character(min(values)),
      high = as.character(max(values))
    )
  } else {
    variable <- variable$set_text()
  }
}
doc$save("survey.xml")
length(doc$variables)
# -> 5
```

## Lire une étude dans un data frame

Les listes Python arrivent en R sous forme de listes : `vapply()` les
transforme en colonnes :

```r
opened <- ddi$open_ddi("survey.xml")
variables <- opened$variables

catalogue <- data.frame(
  name = vapply(variables, function(v) v$names[[1]]$text, character(1)),
  label = vapply(variables, function(v) v$labels[[1]]$text, character(1)),
  identifier = vapply(variables, function(v) v$identifier, character(1))
)
catalogue[, c("name", "label")]
```

## Valider et analyser (lint)

`validate()` renvoie les problèmes de schéma et `lint()` les signalements de
qualité ; les deux sont vides pour un document propre :

```r
issues <- opened$validate()
length(issues)
# -> 0

findings <- opened$lint()
lint_table <- data.frame(
  rule = vapply(findings, function(f) f$rule_id, character(1)),
  severity = vapply(findings, function(f) f$severity, character(1))
)
nrow(lint_table)
# -> 0
```

## Propriétés personnalisées et recherche

```r
age <- opened$find(catalogue$identifier[2])
age$set_property("myorg:source_system", "CRM-2024")
age$get_property("myorg:source_system")
# -> "CRM-2024"
opened$save("survey.xml")
```

## Gérer les erreurs

Une exception Python devient une erreur R : `tryCatch()` fonctionne comme
d'habitude. `py_last_error()` indique de quelle exception `ddi-l` il s'agit :

```r
message <- tryCatch(
  ddi$read_ddi("<DDIInstance><Broken></DDIInstance>"),
  error = function(e) conditionMessage(e)
)
py_last_error()$type
# -> "DDIParseError"
```

Voir [Validation](validation.md) pour la liste complète des types d'exceptions.

## JSON et données liées

`ddi_l.jsonld` restitue une étude en JSON-LD. Le résultat arrive sous forme de
liste R nommée, prête pour `jsonlite` :

```r
jsonld <- import("ddi_l.jsonld")
graph <- jsonld$to_jsonld(opened)
names(graph)
json_text <- jsonlite::toJSON(graph, auto_unbox = TRUE, pretty = TRUE)
```

## La ligne de commande depuis R

La commande `ddi` correspond au module `ddi_l.cli` : on peut donc la lancer avec
le Python qu'utilise reticulate :

```r
output <- system2(
  py_exe(),
  c("-m", "ddi_l.cli", "validate", "survey.xml"),
  stdout = TRUE
)
output
# -> "Document is valid."
```

## Conseils pour reticulate

- **Méthodes et attributs** s'utilisent avec `$` : `doc$add_variable(...)`,
  `variable$identifier`.
- **Les arguments nommés** sont des arguments R nommés : `label = "Âge"`.
- **Entiers :** les nombres R sont des doubles. Écrivez `120L` là où Python
  attend un `int`, ou passez une chaîne lorsque `ddi-l` l'accepte (`low = "0"`).
- **`NULL`** est converti en `None` Python.
- **Les listes** renvoyées par `ddi-l` sont des listes R ordinaires, indexées à
  partir de 1 : `doc$variables[[1]]`.
- **Les appels chaînés** comme `set_numeric()` renvoient l'objet ; affectez le
  résultat (`age <- age$set_numeric(...)`) pour que R ne l'affiche pas.
- **Les noms spéciaux** demandent des accents graves : ``ddi$`__version__` ``.
