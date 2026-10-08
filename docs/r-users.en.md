# Using ddi-l from R

R users can call `ddi-l` directly through
[reticulate](https://rstudio.github.io/reticulate/), the standard R interface
to Python. reticulate runs Python inside your R session and converts values in
both directions, so there is no separate R package to install and every
feature of `ddi-l` is available.

This page shows the R equivalents of the common tasks. The Python
[User guide](user-guide.md) covers each feature in more depth; the calls are
the same, with `$` in place of `.`.

## Setup

Install reticulate once, then create a Python environment for `ddi-l`:

<!-- docs-test: skip -->
```r
install.packages("reticulate")

library(reticulate)
virtualenv_create("ddi-l")
py_install("ddi-l", envname = "ddi-l")   # or "ddi-l[full]" for faster parsing
```

In each session, select that environment before using Python:

<!-- docs-test: skip -->
```r
library(reticulate)
use_virtualenv("ddi-l", required = TRUE)
```

!!! tip "reticulate 1.41 and later"
    `reticulate::py_require("ddi-l")` declares the dependency and lets
    reticulate provision a suitable Python environment automatically, in place
    of the two steps above.

Import the package. The object `ddi` is the Python module `ddi_l`:

```r
library(reticulate)
ddi <- import("ddi_l")
ddi$`__version__`
```

## Create a study

```r
doc <- ddi$new_study(title = "Household Survey", agency = "example.org")

q_age <- doc$add_question(text = "How old are you?", label = "Age question")
age <- doc$add_variable(name = "age", question = q_age, label = "Age in years")
age <- age$set_numeric("Integer", low = 0L, high = 120L)

doc$save("household.xml")
print(doc)
# -> Document(title='Household Survey', agency='example.org', questions=1, variables=1)
```

Model objects stay attached to the document: you can keep editing `age` after
`save()`, and the next save includes the change.

## Build a study from a data frame

Loop over the columns of a data frame and describe each one. The example
reads the curriculum's sample file; save it in your working directory first:

[:material-download: Download `survey_sample.csv`](curriculum/survey_sample.csv){ .md-button download="survey_sample.csv" }

```r
survey <- read.csv("survey_sample.csv", stringsAsFactors = FALSE)

doc <- ddi$new_study(title = "Survey sample", agency = "example.org")
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

## Read a study into a data frame

Python lists arrive in R as lists, so `vapply()` turns them into columns:

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

## Validate and lint

`validate()` returns schema issues and `lint()` returns quality findings; both
are empty for a clean document:

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

## Custom properties and lookups

```r
age <- opened$find(catalogue$identifier[2])
age$set_property("myorg:source_system", "CRM-2024")
age$get_property("myorg:source_system")
# -> "CRM-2024"
opened$save("survey.xml")
```

## Handle errors

A Python exception becomes an R error, so `tryCatch()` works as usual.
`py_last_error()` tells you which `ddi-l` exception it was:

```r
message <- tryCatch(
  ddi$read_ddi("<DDIInstance><Broken></DDIInstance>"),
  error = function(e) conditionMessage(e)
)
py_last_error()$type
# -> "DDIParseError"
```

See [Validation](validation.md) for the full list of exception types.

## JSON and linked data

`ddi_l.jsonld` renders a study as JSON-LD. The result arrives as a named R
list, ready for `jsonlite`:

```r
jsonld <- import("ddi_l.jsonld")
graph <- jsonld$to_jsonld(opened)
names(graph)
json_text <- jsonlite::toJSON(graph, auto_unbox = TRUE, pretty = TRUE)
```

## The command line from R

The `ddi` command is the module `ddi_l.cli`, so it can be run with the same
Python that reticulate uses:

```r
output <- system2(
  py_exe(),
  c("-m", "ddi_l.cli", "validate", "survey.xml"),
  stdout = TRUE
)
output
# -> "Document is valid."
```

## Tips for reticulate

- **Methods and attributes** use `$`: `doc$add_variable(...)`,
  `variable$identifier`.
- **Keyword arguments** are named R arguments: `label = "Age"`.
- **Integers:** R numbers are doubles. Write `120L` where Python expects an
  `int`, or pass a string where `ddi-l` accepts one (`low = "0"`).
- **`NULL`** is converted to Python `None`.
- **Lists** returned by `ddi-l` are ordinary R lists, indexed from 1:
  `doc$variables[[1]]`.
- **Chained calls** such as `set_numeric()` return the object; assign the result
  (`age <- age$set_numeric(...)`) so R does not print it.
- **Special names** need backticks: ``ddi$`__version__` ``.
