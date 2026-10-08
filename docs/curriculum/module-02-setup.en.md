---
description: >-
  Module 2 of the ddi-l course: install Python, ddi-l and the helper
  packages, and check that everything works.
---

# Module 2: Set up your Python environment

!!! info "What you will learn"
    - Install Python and verify the version.
    - Install `ddi-l` and helper packages.
    - Confirm everything works by running a quick test.
    - Choose a workspace for writing Python code.

**Prerequisites:** [Module 1: What is metadata and why does it matter?](module-01-what-is-metadata.md)

**Time:** 20 min self-paced / 30 min instructor-led.

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

The version number must be **3.11 or higher**. If your version is older, visit
<https://www.python.org/downloads/> and install a newer version.

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

---

## 3. Check it works

### 3a. Test the command-line tool

`ddi-l` includes a command-line tool called `ddi`. Run:

```bash
ddi --help
```

You should see a list of available commands. This confirms the tool is
installed and ready to use.

### 3b. Test in Python

Open a Python session by typing `python` in your terminal. Then type:

```python
import ddi_l as ddi

print(ddi.__version__)
```

You should see a version number printed, such as `0.1.0`. This confirms that
Python can find and load the `ddi-l` package.

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
  one document.

For this curriculum, any of the three options will work.

---

## 5. More installation options

For advanced setups (such as installing from source code, using Poetry, or
adding the optional `lxml` backend), see the full
[Installation guide](../installation.md).

---

## Exercises

!!! example "Scenario"
    You are setting up a new laptop for a training workshop. You need to make
    sure Python and `ddi-l` are ready to go before the workshop starts.

**Exercise 1.** Run the following command in your terminal:

```bash
pip install ddi-l pandas openpyxl
```

Paste the **last line** of the output. It usually says something like
`Successfully installed ...`.

??? success "Answer"
    The last line starts with `Successfully installed` and lists `ddi-l-...` among
    the packages (the version may vary). If the packages were already installed,
    pip says `Requirement already satisfied` instead.

**Exercise 2.** Open a Python session and run:

```python
import ddi_l as ddi

print(ddi.__version__)
```

Write down the version number you see.

??? success "Answer"
    The installed version, such as `0.1.0` or later.

**Exercise 3.** Run `ddi --help` in your terminal. **How many commands** are
listed in the output?

??? success "Answer"
    Eight in `ddi-l` 0.1.0: `validate`, `to-json`, `from-json`, `roundtrip`,
    `lint`, `versions`, `to-jsonld` and `serve`. Later versions may add more.

---

## Quiz

???+ question "Question 1: What is the minimum Python version for ddi-l?"
    **A.** Python 2.7

    **B.** Python 3.8

    **C.** Python 3.11

    **D.** Python 3.14

    ??? success "Answer"
        **C.** `ddi-l` requires Python 3.11 or newer.

???+ question "Question 2: Which command shows the ddi-l CLI help?"
    **A.** `python --help`

    **B.** `pip --help`

    **C.** `ddi --help`

    **D.** `ddi-l --help`

    ??? success "Answer"
        **C.** The command `ddi --help` shows the list of commands available
        in the `ddi-l` command-line tool.

???+ question "Question 3: What does pip install do?"
    **A.** It deletes old Python files.

    **B.** It downloads and installs a Python package from the internet.

    **C.** It opens a web browser.

    **D.** It creates a new Python script.

    ??? success "Answer"
        **B.** `pip install` downloads a package from PyPI (the Python
        Package Index) and installs it on your computer so you can use it.

---

!!! tip "Instructor notes"
    - **Budget extra time** for environment issues. Python version problems,
      permission errors, and network issues are common in live workshops.
    - **Have a fallback** ready: a cloud notebook (such as Google Colab) or a
      pre-built container with everything installed.
    - **Why install pandas now?** Installing it here avoids disruption in
      Module 8, where learners will load CSV and Excel files. Getting the
      install out of the way early keeps later modules focused on DDI.
    - **Pair up** learners who finish early with those who need help. Setup
      problems are easier to solve with a partner.
