---
description: >-
  Module 7 of the ddi-l course: validate, lint, convert and round-trip DDI
  files with the ddi command, and use exit codes in scripts.
---

# Module 7: Validate from the command line

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Run `ddi validate` on a DDI file and state from its output whether the file is valid.
    - **O2.** Interpret a `ddi validate` error: say what is wrong and where, using the message and the path after `at`, then fix the file so it validates.
    - **O3.** Run `ddi lint` on a file and name one finding by its severity, rule and message.
    - **O4.** Convert a DDI file to JSON with `ddi to-json` and write a normalized copy with `ddi roundtrip`.
    - **O5.** Check the exit code of a command after a valid and an invalid file, and predict the code (0 or 1) a script will get.

**Prerequisites:** [Module 6](module-06-open-modify.en.md).

**Time:** 30 min self-paced / 40 min instructor-led.

**New in this module:** `ddi validate`, `ddi validate --format json`, `ddi lint`, `ddi lint --format table`, `ddi to-json`, `ddi roundtrip`, `echo $?` (and `echo %ERRORLEVEL%` or `$LASTEXITCODE` on Windows).

---

## 1. Why use the command line?

So far you have written Python scripts to work with DDI files. But sometimes
you just want to check a file quickly without writing code. The **command
line** (also called a terminal or shell) lets you do that.

The command line is also useful when you need to:

- **Process many files at once.** You can validate 20 files with one command.
- **Automate checks.** You can add validation to a script that runs every
  night.
- **Plug into CI/CD pipelines.** A **CI/CD pipeline** is an automated system
  that builds and tests software. Many teams use pipelines to catch errors
  early.

`ddi-l` includes a command-line tool called `ddi`. You installed it when
you installed the `ddi-l` package (see [Module 2](module-02-setup.en.md)).

The exercises use `census-2024.xml`, the file you saved in Exercise 1 of
[Module 6](module-06-open-modify.en.md). Run the commands from the folder that
holds it.

---

## 2. Validate a file

The `ddi validate` command checks whether a DDI XML file follows the DDI
schema rules. A **schema** is a set of rules that says which elements are
allowed, what order they must appear in, and which ones are required.

```bash
ddi validate my-study.xml
```

If the file is valid, you see:

```text
Document is valid.
```

If the file has errors, you see one entry per problem. For example, here is
the output for a file in which someone misspelled `<r:Abstract>` as
`<r:Abstrct>`:

```text
error: Unexpected child with tag '{ddi:reusable:3_3}Abstrct' at position 5.
    at /{ddi:instance:3_3}DDIInstance/{ddi:studyunit:3_3}StudyUnit
    context: <s:StudyUnit>
1 issue found.
```

Each error tells you:

- **what went wrong**: the message after `error:`. Here, an element called
  `Abstrct` appears where the schema does not allow it.
- **where**: the path after `at`. Read it from left to right, from the root of
  the file down to the element that holds the problem: `DDIInstance`, then
  `StudyUnit`. You can ignore the parts in curly braces, such as
  `{ddi:reusable:3_3}`: they name the DDI namespace each element belongs to.
  A number in square brackets, such as `QuestionItem[2]`, means "the second
  `QuestionItem`".
- **what was found**: the `context:` line shows the element (and its value,
  when it has one).

The last line counts the problems. For scripts, add `--format json` to get the
same information as a JSON list (an empty list `[]` when the file is valid).

---

## 3. Reading the output

When you see `"Document is valid."`, it means the file follows all the DDI
schema rules. No action is needed.

When you see errors, read each message carefully. The most common messages
are:

| The message says                         | What it means                                                                        |
| ---------------------------------------- | ------------------------------------------------------------------------------------ |
| `Unexpected child with tag '...'`        | An element is in the wrong place, is misspelled, or a required element before it is missing. |
| `value doesn't match any pattern of ...` | A text value breaks a rule, such as a version number that is not made of digits.     |
| `Error: mismatched tag: line N, column M`| The file is not well-formed XML: a tag is not closed. The line and column say where. |

The last kind of error stops `ddi` before the schema check: it cannot read
the file at all.

Fix the errors in your Python script (or in the XML file directly), then run
`ddi validate` again.

---

## 4. Lint a file

The `ddi lint` command checks **quality rules** that go beyond the schema. It
runs the same rules as `doc.lint()`, which you used in
[Module 3](module-03-first-study.en.md#9-check-your-work).
**Linting** means looking for problems that are technically allowed by the
schema but are usually mistakes or bad practice.

```bash
ddi lint my-study.xml
```

For example, a lint rule might warn you that an item has no label, or that a
reference points to an item that is not in the file. The file can still be
valid XML, but the metadata is incomplete.

By default the output is JSON, for scripts. Add `--format table` for a table
that is easier to read:

```bash
ddi lint my-study.xml --format table
```

```text
severity  rule                     message
--------  -----------------------  ----------------------------------------
warning   ddi.maintainable.labels  Maintainable element is missing a label.
warning   ddi.maintainable.labels  Maintainable element is missing a label.
```

Each row is one **finding**, with three columns:

- **severity**: how serious it is: `error`, `warning` or `info`.
- **rule**: the name of the rule that found it, such as
  `ddi.maintainable.labels`. The [lint rules](../lint-rules.en.md) page explains
  each rule.
- **message**: what the rule found. Here, two items have no label.

---

## 5. Export to JSON

The `ddi to-json` command converts a DDI XML file into JSON format. **JSON**
(JavaScript Object Notation) is a text format that many tools and programming
languages can read. It is easier for some people to read than XML.

```bash
ddi to-json my-study.xml --indent 2
```

The `--indent 2` option adds spaces to make the output easier to read. Without
it, the JSON is printed on one long line.

You can save the output to a file by using the `>` symbol:

```bash
ddi to-json my-study.xml --indent 2 > my-study.json
```

This creates a new file called `my-study.json` with the JSON content.

---

## 6. Round-trip

The `ddi roundtrip` command reads a DDI XML file and writes it back out. This
is called a **round-trip** because the data travels in a circle: file to
memory and back to file.

```bash
ddi roundtrip input.xml --output output.xml
```

Why is this useful?

- **Normalize formatting.** Different tools may write XML with different
  spacing and ordering. A round-trip produces a clean, consistent format.
- **Test for data loss.** If the output file is the same as the input,
  nothing was lost. You can compare the two files to check.

---

## 7. Exit codes

Every command-line tool returns an **exit code** when it finishes. An exit
code is a number that tells you whether the command succeeded or failed.

| Exit code | Meaning                                |
| --------- | -------------------------------------- |
| 0         | Success: everything is fine.        |
| 1         | Failure: something went wrong.      |

`ddi validate` returns 1 when the file has at least one schema error.
`ddi lint` returns 1 only when a finding has the severity `error`: warnings
alone return 0. (Add `--fail-severity warning` to make warnings fail too.)

Why does this matter? Because scripts and pipelines can check the exit code
to decide what to do next. For example:

```bash
ddi validate my-study.xml && echo "All good!" || echo "Fix the errors."
```

This line says: "Run `ddi validate`. If it succeeds (exit code 0), print
'All good!'. If it fails (exit code 1), print 'Fix the errors.'"

You can also print the exit code of the last command. On macOS and Linux, use
`$?`:

```bash
ddi validate my-study.xml
echo $?
```

On Windows, use `echo %ERRORLEVEL%` in the Command Prompt, or
`$LASTEXITCODE` in PowerShell.

If the file is valid, `echo $?` prints `0`. If not, it prints `1`.

---

## Exercises

!!! example "Scenario"
    A national statistics office has 20 DDI XML files from different survey
    teams. They need to validate them all, check their quality, export one to
    JSON, and produce a normalized copy.

**Exercise 1 (O1).** Validate `census-2024.xml` from the Module 6 exercises
(or any file from an earlier module) using `ddi validate`. Is the file valid?

Expected output:

```text
Document is valid.
```

??? success "Answer"
    ```bash
    ddi validate census-2024.xml
    ```

    The output says `Document is valid.`, so the file follows all the DDI
    schema rules.

**Exercise 2 (O2).** Break a file on purpose and read the error.

1. Make a copy of `census-2024.xml` called `broken.xml`
   (`cp census-2024.xml broken.xml` on macOS and Linux,
   `copy census-2024.xml broken.xml` on Windows).
2. Open `broken.xml` in a text editor. On line 5, change
   `<r:Version>1</r:Version>` to `<r:Version>one</r:Version>`. Save the file.
3. Run `ddi validate broken.xml`.
4. Write down what is wrong and where.

Keep `broken.xml` as it is: you fix it in Exercise 6.

Expected output:

```text
error: value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*']
    at /{ddi:instance:3_3}DDIInstance/{ddi:reusable:3_3}Version
    context: <r:Version> one
1 issue found.
```

??? success "Answer"
    ```bash
    cp census-2024.xml broken.xml
    # edit line 5 of broken.xml, then:
    ddi validate broken.xml
    ```

    - **What:** the value `one` does not match the pattern for versions.
      `[0-9]+(\.[0-9]+)*` means digits, optionally followed by more groups of
      a dot and digits, such as `1` or `1.0.0`.
    - **Where:** the path after `at` ends with `DDIInstance`, then `Version`:
      the `Version` element directly under the root, which is the one on
      line 5. The `context:` line confirms the value found: `one`.

**Exercise 3 (O3).** Run `ddi lint` on `census-2024.xml` with
`--format table`. Pick one finding and name its severity, its rule and its
message. What would you change to make it go away?

Expected output:

```text
severity  rule                     message
--------  -----------------------  ----------------------------------------
warning   ddi.maintainable.labels  Maintainable element is missing a label.
warning   ddi.maintainable.labels  Maintainable element is missing a label.
warning   ddi.maintainable.labels  Maintainable element is missing a label.
warning   ddi.maintainable.labels  Maintainable element is missing a label.
```

??? success "Answer"
    ```bash
    ddi lint census-2024.xml --format table
    ```

    One finding: severity `warning`, rule `ddi.maintainable.labels`, message
    "Maintainable element is missing a label." The file has four of them:
    its two questions and two variables have no label. To fix them, pass
    `label=` when you add each item, as in Section 9 of Module 3. The file is
    still valid: warnings point to quality, not to schema errors.

**Exercise 4 (O4).** Export `census-2024.xml` to JSON with `ddi to-json`. Count
how many lines the JSON has.

Expected output: about 200 lines (`wc -l` prints the count followed by the
filename).

??? success "Answer"
    ```bash
    ddi to-json census-2024.xml --indent 2 > census-2024.json
    wc -l census-2024.json
    ```

    The `wc -l` command counts the number of lines in a file (on Windows
    PowerShell, use `(Get-Content census-2024.json).Count`). A file with two
    questions and two variables gives about 200 lines; more content gives
    more lines.

**Exercise 5 (O4).** Round-trip `census-2024.xml`. Compare the input and output
sizes.

Expected output: two files of the same size, about 4 KB each.

??? success "Answer"
    ```bash
    ddi roundtrip census-2024.xml --output census-2024-roundtrip.xml
    ls -l census-2024.xml census-2024-roundtrip.xml
    ```

    The `ls -l` command shows the file sizes (use `dir` on Windows). A file
    that `ddi-l` wrote itself comes back with exactly the same size. A file
    from another tool may differ a little, because of spacing; that is the
    normalization at work.

**Exercise 6 (O5, O2).** Check the exit codes.

1. Run `ddi validate census-2024.xml`, then print the exit code
   (`echo $?` on macOS and Linux, `echo %ERRORLEVEL%` in the Windows Command
   Prompt, `$LASTEXITCODE` in PowerShell).
2. Do the same with `broken.xml` from Exercise 2.
3. Fix `broken.xml` (change `one` back to `1`), validate it again, and print
   the exit code once more.

Expected output (the exit codes, in order):

```text
0
1
0
```

??? success "Answer"
    ```bash
    ddi validate census-2024.xml
    echo $?
    ddi validate broken.xml
    echo $?
    # edit line 5 of broken.xml back to <r:Version>1</r:Version>, then:
    ddi validate broken.xml
    echo $?
    ```

    A valid file gives exit code 0. A file with a schema error gives 1, and
    the fixed file gives 0 again, with `Document is valid.` above it. A
    script that runs `ddi validate` can use these codes to stop before it
    publishes a broken file.

---

## Quiz

???+ question "Question 1 (O1): What does this output tell you?"
    You run `ddi validate study.xml` and see `Document is valid.`

    **A.** The file follows all the DDI schema rules; no action is needed.

    **B.** The file has no lint findings either.

    **C.** The file was converted to JSON.

    **D.** The file was saved in a new, normalized format.

    ??? success "Answer"
        **A.** `ddi validate` checks the schema only. Lint findings are a
        separate check (`ddi lint`), so option B does not follow.

???+ question "Question 2 (O2): Where is the problem in this output?"
    ```text
    error: Unexpected child with tag '{ddi:datacollection:3_3}QuestionTxt' at position 4.
        at /{ddi:instance:3_3}DDIInstance/{ddi:studyunit:3_3}StudyUnit/{ddi:datacollection:3_3}DataCollection/{ddi:datacollection:3_3}QuestionScheme/{ddi:datacollection:3_3}QuestionItem[1]
        context: <d:QuestionItem>
    1 issue found.
    ```

    **A.** In the title of the study.

    **B.** The file is not well-formed XML.

    **C.** Inside the first `QuestionItem`: it holds an element called
    `QuestionTxt`, which the schema does not allow there (it looks like a
    misspelled `QuestionText`).

    **D.** On line 1 of the file.

    ??? success "Answer"
        **C.** The path after `at` ends with `QuestionItem[1]`, the first
        question item, which holds the problem; the message names the
        unexpected element. A file that is not well-formed gives a
        `mismatched tag` error instead.

???+ question "Question 3 (O3): What do these two results tell you about the file?"
    `ddi validate data.xml` prints `Document is valid.`, and
    `ddi lint data.xml --format table` prints one row:
    `warning  ddi.maintainable.labels  Maintainable element is missing a label.`

    **A.** The file breaks a schema rule.

    **B.** The file is valid, but lint found a quality problem: an item has
    no label.

    **C.** `ddi lint` and `ddi validate` check the same rules, so one of them
    is wrong.

    **D.** The warning makes `ddi lint` return exit code 1.

    ??? success "Answer"
        **B.** Validation checks the schema; lint checks quality rules beyond
        it. A warning alone does not fail `ddi lint`: it returns 0 unless you
        pass `--fail-severity warning`.

???+ question "Question 4 (O4): Which command writes a JSON copy of my-study.xml to my-study.json?"
    **A.** `ddi roundtrip my-study.xml --output my-study.json`

    **B.** `ddi validate my-study.xml > my-study.json`

    **C.** `ddi lint my-study.json`

    **D.** `ddi to-json my-study.xml --indent 2 > my-study.json`

    ??? success "Answer"
        **D.** `ddi to-json` converts DDI XML to JSON, and `>` saves the output
        in a file. `ddi roundtrip` writes XML, and the `ddi validate` command
        in option B saves the validation report, not the document.

???+ question "Question 5 (O4): Why would you run ddi roundtrip on a file from another tool?"
    **A.** To delete the elements that `ddi-l` does not model.

    **B.** To write a copy with clean, consistent formatting, and to check
    that nothing is lost on the way.

    **C.** To validate the file against the schema.

    **D.** To convert the file to JSON.

    ??? success "Answer"
        **B.** A round-trip reads the file and writes it back out in a
        normalized format. `ddi-l` keeps the elements it does not model, so
        nothing is deleted.

???+ question "Question 6 (O5): What does this script print?"
    `broken.xml` has three schema errors. A script runs:

    ```bash
    ddi validate broken.xml
    echo $?
    ```

    **A.** `0`

    **B.** `3`

    **C.** `1` (after the list of errors)

    **D.** `-1`

    ??? success "Answer"
        **C.** `ddi validate` returns 1 when the file has any schema error,
        however many there are. The exit code says "failed", not how many
        problems were found.

---

## Check yourself

- [ ] I can run `ddi validate` on a file and say from the output whether it is valid. (O1)
- [ ] I can read a `ddi validate` error, say what is wrong and where, and fix the file so it validates. (O2)
- [ ] I can run `ddi lint` and name one finding by its severity, rule and message. (O3)
- [ ] I can convert a file to JSON with `ddi to-json` and write a normalized copy with `ddi roundtrip`. (O4)
- [ ] I can check the exit code after a valid and an invalid file, and predict what a script will get. (O5)

---

**See also:**

- [CLI recipes](../cli-recipes.en.md)
- [Automation playbook](../tutorials/automation-playbook.en.md)
- [Lint rules](../lint-rules.en.md)

---

!!! tip "Instructor notes"
    - **Live demo.** Run `ddi validate`, `ddi lint`, `ddi to-json`, and
      `ddi roundtrip` on a projector so learners can see the output in real
      time. Use files from previous modules.
    - **Break a file on purpose.** Exercise 2 changes a version number to a
      word, which gives a schema error. Also show a different break: delete a
      closing tag in a text editor and run `ddi validate` again. That gives
      `Error: mismatched tag: line N, column M`, because the file is no longer
      well-formed XML. Fix it and re-validate.
    - **Batch validation.** Show how to validate many files at once:
      `for f in *.xml; do echo "--- $f ---"; ddi validate "$f"; done`
    - **Exit codes in practice.** Write a short bash script that validates a
      file and prints a message based on the exit code. This prepares learners
      for CI/CD integration. Windows users print the code with
      `echo %ERRORLEVEL%` (Command Prompt) or `$LASTEXITCODE` (PowerShell).
    - **Lint is not validation.** Learners often expect lint warnings to make
      a file invalid. Use Exercise 3 and Question 3 to separate the two
      checks.
    - **JSON as a bridge.** Explain that JSON output can be loaded by other
      tools (R, JavaScript, data catalogs). This is useful for teams that do
      not use Python.
    - **Timing note.** This module is lighter on Python code and heavier on
      command-line skills. If your audience is less comfortable with the
      terminal, spend extra time on Section 1 and the exercises.
