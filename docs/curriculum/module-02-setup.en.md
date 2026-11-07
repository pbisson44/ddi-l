---
description: >-
  Module 2 of the ddi-l course: install Python, ddi-l and the helper
  packages, and check that everything works.
---

# Module 2: Set up your Python environment

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Run `python --version` and decide whether your Python is new
      enough for `ddi-l` (3.11 or newer).
    - **O2.** Install `ddi-l`, `pandas`, and `openpyxl` with `pip` and read
      the last line of the output to confirm the install.
    - **O3.** Run a two-line Python test that prints the installed `ddi-l`
      version.
    - **O4.** Run `ddi --help` and find the command that does a given task,
      such as validating a file.
    - **O5.** Choose a workspace (Python REPL, script file, or notebook) for
      a given task and give a one-sentence reason.

**Prerequisites:** [Module 1](module-01-what-is-metadata.en.md)

**Time:** 20 min self-paced / 30 min instructor-led.

**New in this module:** `python --version`, `pip install`, `ddi --help`,
`import ddi_l as ddi`, `ddi.__version__`

---

## 1. What you need: Python 3.11 or newer

Python is a programming language. `ddi-l` runs inside Python, so you must
have Python installed on your computer.

Open a **terminal** (also called a command prompt) and type:

```bash
python --version
```

You should see something like:

```text
Python 3.12.3
```

The version number must be **3.11 or higher**. Read the first two numbers:
`3.12` is newer than `3.11`, so it works; `3.10` or `3.9` is too old. If your
version is older, visit <https://www.python.org/downloads/> and install a newer
version.

!!! warning "Common issue"
    On some systems the command is `python3` instead of `python`. If
    `python --version` does not work, try `python3 --version`.

---

## 2. Install ddi-l

In your terminal, run:

```bash
pip install ddi-l
```

This command downloads `ddi-l` from the internet and installs it. The word
**pip** is Python's package installer. It is the standard way to add new
tools to your Python setup.

Next, install two helper packages you will need in later modules:

```bash
pip install pandas openpyxl
```

- **pandas** is a popular tool for working with tables of data.
- **openpyxl** lets Python read and write Excel files.

You can install everything in one line if you prefer:

```bash
pip install ddi-l pandas openpyxl
```

The last line of the output tells you how it went:

- `Successfully installed` followed by package names means pip installed
  them.
- `Requirement already satisfied` means a package was already there, so pip
  had nothing to do.
- A line starting with `ERROR` means the install failed. Read the message,
  fix the cause (often the Python version or a network problem), and run the
  command again.

---

## 3. Check it works

### 3a. Test the command-line tool

`ddi-l` includes a command-line tool called `ddi`. Run:

```bash
ddi --help
```

You should see a list of available commands. This confirms the tool is
installed and ready to use. Each command has a one-line description. The
start of the list looks like this:

```text
positional arguments:
    validate            Validate an XML document against the DDI schema.
    to-json             Convert a DDI instance document to JSON.
    ...
```

To find the command for a task, read the descriptions, not just the names.
For example, the command that checks a file against the DDI rules is the one
whose description says "Validate". You will use these commands in
[Module 7](module-07-cli-validation.en.md).

### 3b. Test in Python

Open a Python session by typing `python` in your terminal. Then type:

```python
import ddi_l as ddi

print(ddi.__version__)
```

You should see a version number printed, such as `0.1.0` or later. This
confirms that Python can find and load the `ddi-l` package.

If you see `ModuleNotFoundError: No module named 'ddi_l'` instead, `ddi-l` is
not installed in the Python you are running. Run `pip install ddi-l` again,
using the same `python` or `python3` command you used above (for example,
`python3 -m pip install ddi-l`).

Type `exit()` to leave the Python session.

---

## 4. Choose your workspace

You can write Python code in several ways. Pick the one that feels most
comfortable:

| Workspace       | How to start                          | Best for                  |
| --------------- | ------------------------------------- | ------------------------- |
| Python REPL     | Type `python` in the terminal.        | Quick tests and exploring.|
| Script file     | Create a file like `my_script.py`.    | Saving your work.         |
| Jupyter Notebook| Run `jupyter notebook` in terminal.   | Step-by-step exploration. |

- **REPL** stands for Read-Eval-Print Loop. It is an interactive prompt where
  you type one line of Python at a time and see the result right away.
- A **script file** is a plain text file ending in `.py` that you run all at
  once.
- A **Jupyter Notebook** is a tool that lets you mix text, code, and output in
  one document. It is not installed with `ddi-l`: run `pip install notebook`
  first if you want to use one.

How to choose:

- Use the **REPL** for a one-off check you do not need to keep, such as
  printing the version.
- Use a **script file** when you want to keep your code and run it again
  from the top with one command, such as `python my_script.py`.
- Use a **notebook** when you want to see notes, code, and output together,
  step by step, for example to walk a colleague through your work.

For this curriculum, any of the three options will work.

---

## Exercises

!!! example "Scenario"
    You are setting up a new laptop for a training workshop. You need to make
    sure Python and `ddi-l` are ready to go before the workshop starts.

**Exercise 1 (O1).** Run `python --version` (or `python3 --version`) in your
terminal. Write down the version, and say whether it is new enough for
`ddi-l`.

Expected output: one line such as `Python 3.12.3`, and a yes or no.

??? success "Answer"
    For example, `Python 3.12.3`: yes, because 3.12 is 3.11 or newer. If you
    see `Python 3.10.12` or older, the answer is no: install a newer Python
    from <https://www.python.org/downloads/> before you continue.

**Exercise 2 (O2).** Run the following command in your terminal:

```bash
pip install ddi-l pandas openpyxl
```

Paste the **last line** of the output, and say what it means.

Expected output: a line that starts with `Successfully installed` or
`Requirement already satisfied`.

??? success "Answer"
    The last line starts with `Successfully installed` and lists `ddi-l-...` among
    the packages (the version may vary). If the packages were already installed,
    pip says `Requirement already satisfied` instead. Both mean you are ready. A
    line starting with `ERROR` means the install failed.

**Exercise 3 (O3).** Open a Python session and run:

```python
import ddi_l as ddi

print(ddi.__version__)
```

Write down the version number you see.

Expected output: one version number, such as `0.1.0`.

??? success "Answer"
    The installed version, such as `0.1.0` or later. If you see
    `ModuleNotFoundError` instead, `ddi-l` is not installed in this Python:
    go back to Exercise 2.

**Exercise 4 (O4).** Run `ddi --help` in your terminal. Read the
descriptions and write down the command you would use for each task:

1. Check a DDI file against the DDI schema.
2. Report quality problems in a DDI file, such as missing labels.
3. List the DDI schema releases that `ddi-l` supports.

Expected output: three command names.

??? success "Answer"
    1. `validate` ("Validate an XML document against the DDI schema.")
    2. `lint` ("Lint a DDI document and report findings as JSON.")
    3. `versions` ("List supported DDI schema releases.")

**Exercise 5 (O5).** Choose a workspace for each task, and give a
one-sentence reason:

1. Check once that `import ddi_l` works on the new laptop.
2. Write the study you will build in Module 3, so you can run it again
   next week after you change it.
3. Show a colleague, step by step, how the study is built, with notes
   between the pieces of code.

Expected output: three workspaces, each with a reason.

??? success "Answer"
    1. **Python REPL:** it is the quickest way to run one line you do not
       need to keep.
    2. **Script file:** it saves your code, and `python my_script.py` runs
       it again from the top.
    3. **Notebook:** it shows notes, code, and output together, step by
       step.

    Other choices are fine if your reason holds up; for example, a notebook
    also saves your code for task 2.

---

## Quiz

???+ question "Question 1 (O1): `python --version` prints `Python 3.10.12`. What should you do before you install ddi-l?"
    **A.** Nothing. Any Python 3 version works.

    **B.** Install Python 3.11 or newer.

    **C.** Run `pip install ddi-l` twice.

    **D.** Switch to Python 2.7.

    ??? success "Answer"
        **B.** `ddi-l` requires Python 3.11 or newer, and 3.10 is older.
        Install a newer Python, then install `ddi-l` with it.

???+ question "Question 2 (O2): The last line of `pip install ddi-l pandas openpyxl` reads `Requirement already satisfied`. What does this mean?"
    **A.** The install failed and must be run again.

    **B.** pip needs administrator rights.

    **C.** The packages must be removed first.

    **D.** The package was already installed, so pip had nothing to do.

    ??? success "Answer"
        **D.** `Requirement already satisfied` means the package is already
        there. A failed install ends with a line that starts with `ERROR`.

???+ question "Question 3 (O3): You run `import ddi_l as ddi` and get `ModuleNotFoundError: No module named 'ddi_l'`. What is the most likely cause?"
    **A.** `ddi-l` is not installed in the Python you are running.

    **B.** The import must be written `import ddi-l`.

    **C.** You must call `ddi.__version__` before the import.

    **D.** The package only works in a notebook.

    ??? success "Answer"
        **A.** Python cannot find the package, so it is not installed for
        this Python. Run `pip install ddi-l` again, or
        `python3 -m pip install ddi-l` if you start Python with `python3`.
        Option B is not valid Python: a hyphen cannot appear in an import
        name, which is why the module is called `ddi_l`.

???+ question "Question 4 (O4): You want to check a file against the DDI schema from the terminal. Which command from the `ddi --help` list do you use?"
    **A.** `roundtrip`

    **B.** `to-json`

    **C.** `validate`

    **D.** `serve`

    ??? success "Answer"
        **C.** Its description reads "Validate an XML document against the
        DDI schema." `roundtrip` re-writes a file, `to-json` converts it,
        and `serve` runs the HTTP API.

???+ question "Question 5 (O5): You will build a study over several days and want to run the whole thing again from the top with one command after each change. Which workspace fits best?"
    **A.** The Python REPL, typing each line again.

    **B.** A script file, such as `build_study.py`, run with
    `python build_study.py`.

    **C.** A text document that you copy and paste into the REPL.

    **D.** The terminal, running `ddi --help`.

    ??? success "Answer"
        **B.** A script file keeps your code, and one command runs all of it
        again. The REPL forgets what you typed when you close it.

---

## Going further (optional)

For advanced setups (such as installing with uv or Poetry, or adding the
optional `lxml` backend for faster parsing), see the full
[Installation guide](../installation.en.md).

---

## Check yourself

- [ ] I can run `python --version` and decide whether my Python is new
  enough for `ddi-l`. (O1)
- [ ] I can install `ddi-l`, `pandas`, and `openpyxl` with `pip` and read
  the last line of the output. (O2)
- [ ] I can run a two-line Python test that prints the `ddi-l` version. (O3)
- [ ] I can run `ddi --help` and find the command for a given task. (O4)
- [ ] I can choose a workspace for a task and give a one-sentence reason.
  (O5)

---

!!! tip "Instructor notes"
    - **Budget extra time** for environment issues. Python version problems,
      permission errors, and network issues are common in live workshops.
    - **Have a fallback** ready: a cloud notebook (such as Google Colab) or a
      pre-built container with everything installed.
    - **Why install pandas now?** Installing it here avoids disruption in
      Module 8, where learners will load CSV and Excel files. Getting the
      install out of the way early keeps later modules focused on DDI.
    - **Exercise 4:** The number of commands grows from one release to the
      next, so ask learners to find commands by their description rather
      than count them.
    - **Pair up** learners who finish early with those who need help. Setup
      problems are easier to solve with a partner.
