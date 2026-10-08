# Module 15: Validate From the Command Line

!!! info "What you will learn"
    - Run `ddi validate` to check a DDI file for errors.
    - Read and understand the validation output.
    - Use `ddi lint` to check quality rules beyond the schema.
    - Export a DDI file to JSON with `ddi to-json`.
    - Normalize a file with `ddi roundtrip`.
    - Understand exit codes and why they matter for scripts.

**Prerequisites:** [Module 14: Open, Modify, and Re-Save Existing DDI Files](module-14-open-modify.md).

**Time:** 30 min self-paced / 40 min instructor-led.

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
you installed the `ddi-l` package (see Module 2).

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

If the file has errors, you see one entry per problem. For example:

```text
error: Element 'BadElement': This element is not expected. (line 42, column 12)
    at /DDIInstance/s:StudyUnit
1 issue found.
```

Each error tells you:

- **what went wrong**: the message after `error:`.
- **where**: the line and column in the XML file, and the XPath after `at`.

You can use this information to find and fix the error. For scripts, add
`--format json` to get the same information as a JSON list (an empty list `[]`
when the file is valid).

---

## 3. Reading the output

When you see `"Document is valid."`, it means the file follows all the DDI
schema rules. No action is needed.

When you see errors, read each message carefully. The most common errors are:

| Error type              | What it means                              |
| ----------------------- | ------------------------------------------ |
| Element not expected    | An XML element is in the wrong place.      |
| Missing child element   | A required element is missing.             |
| Invalid value           | A text value does not match the rules.     |

Fix the errors in your Python script (or in the XML file directly), then run
`ddi validate` again.

---

## 4. Lint a file

The `ddi lint` command checks **quality rules** that go beyond the schema.
**Linting** means looking for problems that are technically allowed by the
schema but are usually mistakes or bad practice.

```bash
ddi lint my-study.xml
```

For example, a lint rule might warn you that a variable has no linked question,
or that a concept has no description. The file is still valid XML, but the
metadata is incomplete.

The output is a list of findings, each with a severity level (like "warning"
or "info") and a short message.

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

Why does this matter? Because scripts and pipelines can check the exit code
to decide what to do next. For example:

```bash
ddi validate my-study.xml && echo "All good!" || echo "Fix the errors."
```

This line says: "Run `ddi validate`. If it succeeds (exit code 0), print
'All good!'. If it fails (exit code 1), print 'Fix the errors.'"

You can also check the exit code of the last command with `$?`:

```bash
ddi validate my-study.xml
echo $?
```

If the file is valid, `echo $?` prints `0`. If not, it prints `1`.

---

## Exercises

!!! example "Scenario"
    A national statistics office has 20 DDI XML files from different survey
    teams. They need to validate them all, export one to JSON, and produce a
    normalized copy.

**Exercise 1.** Validate a file from an earlier module using `ddi validate`.
Copy the output.

```bash
ddi validate survey-v2.xml
```

Expected output (if valid):

```text
Document is valid.
```

**Exercise 2.** Export the file to JSON with `ddi to-json`. Count how many
lines the JSON has.

```bash
ddi to-json survey-v2.xml --indent 2 > survey-v2.json
wc -l survey-v2.json
```

The `wc -l` command counts the number of lines in a file. Your number will
depend on how much content the file has.

**Exercise 3.** Round-trip the file. Compare the input and output sizes.

```bash
ddi roundtrip survey-v2.xml --output survey-v2-roundtrip.xml
ls -l survey-v2.xml survey-v2-roundtrip.xml
```

The `ls -l` command shows the file sizes. The two files should be close in
size. Small differences in whitespace are normal.

---

## Quiz

???+ question "Question 1: What does the ddi validate command do?"
    **A.** It creates a new DDI file from scratch.

    **B.** It checks whether a DDI XML file follows the DDI schema rules.

    **C.** It converts a DDI file to a spreadsheet.

    **D.** It uploads a DDI file to a server.

    ??? success "Answer"
        **B.** `ddi validate` checks the file against the DDI schema. If the
        file follows all the rules, it prints "Document is valid." If not, it
        prints a list of errors in JSON format.

???+ question "Question 2: What does exit code 0 mean?"
    **A.** The command found 0 questions in the file.

    **B.** The command failed and produced 0 output.

    **C.** The command succeeded: everything is fine.

    **D.** The file has 0 bytes.

    ??? success "Answer"
        **C.** Exit code 0 means success. The command finished without errors.
        Scripts and pipelines use exit codes to decide what to do next.

???+ question "Question 3: What does ddi to-json produce?"
    **A.** A Python script.

    **B.** A JSON file that contains the same data as the DDI XML file.

    **C.** A CSV spreadsheet.

    **D.** A PDF report.

    ??? success "Answer"
        **B.** `ddi to-json` converts a DDI XML file into JSON format. JSON is
        a text format that many tools and programming languages can read.

---

**See also:**

- [CLI recipes](../cli-recipes.md)
- [Automation playbook](../tutorials/automation-playbook.md)

---

!!! tip "Instructor notes"
    - **Live demo.** Run `ddi validate`, `ddi lint`, `ddi to-json`, and
      `ddi roundtrip` on a projector so learners can see the output in real
      time. Use files from previous modules.
    - **Break a file on purpose.** Open a valid XML file in a text editor.
      Delete a closing tag or add an unknown element. Then run
      `ddi validate` to show what an error looks like. Fix it and re-validate.
    - **Batch validation.** Show how to validate many files at once:
      `for f in *.xml; do echo "--- $f ---"; ddi validate "$f"; done`
    - **Exit codes in practice.** Write a short bash script that validates a
      file and prints a message based on the exit code. This prepares learners
      for CI/CD integration.
    - **JSON as a bridge.** Explain that JSON output can be loaded by other
      tools (R, JavaScript, data catalogs). This is useful for teams that do
      not use Python.
    - **Timing note.** This module is lighter on Python code and heavier on
      command-line skills. If your audience is less comfortable with the
      terminal, spend extra time on Section 1 and the exercises.
