---
description: >-
  Optional Module 19 of the ddi-l course: with the server extra, run ddi-l as
  an HTTP service, validate, lint and convert documents over HTTP, read its
  status codes, and choose safe settings for a shared deployment.
---

# Module 19 (optional): Serve ddi-l over HTTP

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Start the service with `ddi serve`, check that it runs with
      `/health`, and find an endpoint's query parameters in the interactive
      documentation at `/schema`.
    - **O2.** Validate and lint a document over HTTP, from the shell and from
      Python, and read `valid`, `schema_issues` and `lint_findings` in the
      answer.
    - **O3.** Convert a document to JSON and back over HTTP, and check that
      the round trip kept every byte.
    - **O4.** Tell from a status code and its `detail` what was wrong with a
      request (400, 405, 413, 503 or 504), and fix the request.
    - **O5.** Choose the settings of a shared deployment (address, largest
      document, origins allowed, interactive documentation) and build the
      service with `create_app(ServerConfig(...))`.

**Prerequisites:** [Module 7](module-07-cli-validation.en.md). This module is
optional: the capstone does not need it.

!!! warning "Install the server extra first"
    The service needs the `server` extra, which adds Litestar (the web
    framework) and uvicorn (the program that serves it). `pip install ddi-l`
    alone installs neither:

    ```bash
    pip install -U "ddi-l[server]"
    ```

**Time:** 45 min self-paced / 60 min instructor-led.

**New in this module:** `ddi serve`, `/health`, `/schema`, `POST
/v1/validate`, `POST /v1/lint`, `POST /v1/convert/json`, `POST
/v1/convert/xml`, `create_app()`, `ServerConfig`, Litestar's `TestClient`.

---

## 1. Why a service?

In Module 7 you ran `ddi validate` and `ddi lint` on your own machine. Other
people and programs may need the same checks: a deposit form on a website, a
pipeline written in Java or R, a CI job in another language. They cannot all
install Python and `ddi-l`.

A **service** answers requests sent over HTTP, the protocol of the web. You
run `ddi-l` once, as a service, and every program that can send an HTTP
request can validate a document. The service calls the same code as the
`ddi` command, so both give the same answer for the same document.

Each request goes to an **endpoint**: a path such as `/v1/validate`, with a
method. `GET` asks for something; `POST` sends something, here a document,
in the request's **body**. The service answers with a **status code** (200
means it worked) and, here, a JSON body.

## 2. Start the service

In a terminal:

```bash
ddi serve
```

```text
Interactive API docs: http://localhost:8000/schema
OpenAPI document:     http://localhost:8000/schema/openapi.json
INFO:     Started server process [1550]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

The service now listens on port 8000 of **this machine only**
(`127.0.0.1`), until you press Ctrl+C. Leave this terminal open and open a
second one for the commands below.

!!! tip "Port 8000 already in use?"
    If `ddi serve` stops with "address already in use" (on Windows: "only one
    usage of each socket address ... is normally permitted"), another program
    already listens on port 8000: `mkdocs serve` does by default, for one.
    Start the service on another port with `ddi serve --port 8001`, and use
    8001 instead of 8000 in this module's addresses. An answer that is a web
    page saying "404 - Not found" means a command still went to port 8000,
    to the other program.

Check that it answers, from the second terminal:

=== "Windows PowerShell"

    ```powershell
    Invoke-RestMethod http://localhost:8000/health
    ```

=== "macOS and Linux"

    ```bash
    curl http://localhost:8000/health
    ```

```text
{"status":"ok","version":"X.Y.Z"}
```

PowerShell shows the same two fields as a small table. In place of `X.Y.Z`
you see the version of `ddi-l` you installed.

!!! warning "Windows PowerShell has its own curl"
    In Windows PowerShell, `curl` is another command, and `@` means something
    else, so the macOS and Linux commands fail there (`The splatting operator
    '@' cannot be used...`). Use the Windows PowerShell tab, or type
    `curl.exe` and put the file name in quotes:
    `curl.exe --data-binary "@pets.xml" http://localhost:8000/v1/validate`.

Now open <http://localhost:8000/schema> in a browser. This is the
**interactive documentation**: every endpoint, what to send, its query
parameters (the `?name=value` part of an address) and what comes back, with
examples. Open `POST /v1/validate`, press **Try it out**, then **Execute**:
the body is filled in with a valid document, and you get a real answer.
`/schema/fr` shows the same page with the descriptions in French.

## 3. Validate and lint

Save a small document to send:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Pet Survey", agency="example.org")
doc.add_question(text="How many pets live here?")
doc.add_variable(name="PetCount")
doc.save("pets.xml")
```

Send it to `/v1/validate` from the second terminal:

=== "Windows PowerShell"

    ```powershell
    Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/validate `
      -InFile pets.xml -ContentType application/xml | ConvertTo-Json -Depth 5
    ```

=== "macOS and Linux"

    ```bash
    curl --data-binary @pets.xml http://localhost:8000/v1/validate
    ```

`--data-binary @pets.xml` and `-InFile pets.xml` both send the file as the
body, byte for byte. The answer has four fields:

| Field | What it holds |
| --- | --- |
| `valid` | `true` when the document has no error, from the schema or from lint |
| `schema_issues` | Each schema error: `message`, `line`, `xpath`, `context` |
| `lint_findings` | Each lint finding: `rule_id`, `severity`, `message`, `location` |
| `messages` | All of them in one list, each marked with its `source` |

Warnings do not make a document invalid, just as `ddi lint` returns 0 when
it reports only warnings.

### The same request from Python

To try the service from Python, you do not need to start it. Litestar, which
the `server` extra installs, has a **test client** that sends requests to
the service inside your own program. It is also how you would test a
deployment's settings:

```python
import logging
from pathlib import Path

from ddi_l.server import create_app
from litestar.testing import TestClient

# The test client logs every request; keep the output to what you print.
logging.getLogger("httpx").setLevel(logging.WARNING)

client = TestClient(app=create_app())
xml = Path("pets.xml").read_bytes()

response = client.post("/v1/validate", content=xml)
print(response.status_code)  # -> 200
report = response.json()
print(report["valid"], len(report["schema_issues"]))  # -> True 0
for finding in report["lint_findings"]:
    print(finding["severity"], finding["rule_id"])
# -> warning ddi.maintainable.labels
```

The question and the variable have no label, hence two warnings. The
document is still valid.

`client.post()` and `client.get()` take the same paths, query parameters and
bodies as `curl`, so everything below works on a running service too.

### Query parameters

The options of `ddi lint` travel as query parameters:

| Parameter | On | Does |
| --- | --- | --- |
| `lint=false` | `/v1/validate` | Schema validation only |
| `version=3.2` | every document endpoint | Validate against that DDI version, not the one the document declares |
| `rule=...` | `/v1/lint` | Run only that rule (repeat it for several) |
| `skip_rule=...` | `/v1/lint` | Leave out that rule's findings |
| `profile=...` | `/v1/lint` | Run a lint profile |
| `lint_config=...` | `/v1/lint`, `/v1/validate` | The JSON that `ddi lint --lint-config` reads |

```python
quiet = client.post(
    "/v1/lint", params={"skip_rule": "ddi.maintainable.labels"}, content=xml
)
print(quiet.json())  # -> {'lint_findings': []}
```

From the shell, put them in the address, in quotes, because `&` and `?` mean
something to the shell:

=== "Windows PowerShell"

    ```powershell
    Invoke-RestMethod -Method Post -InFile pets.xml -ContentType application/xml `
      -Uri "http://localhost:8000/v1/lint?skip_rule=ddi.maintainable.labels"
    ```

=== "macOS and Linux"

    ```bash
    curl --data-binary @pets.xml 'http://localhost:8000/v1/lint?skip_rule=ddi.maintainable.labels'
    ```

## 4. Convert to JSON and back

`/v1/convert/json` turns a document into JSON, as `ddi to-json` does, and
`/v1/convert/xml` turns that JSON back into XML:

```python
as_json = client.post("/v1/convert/json", content=xml)
print(as_json.headers["content-type"])  # -> application/json
back = client.post(
    "/v1/convert/xml",
    content=as_json.content,
    headers={"Content-Type": "application/json"},
)
print(back.content == xml)  # -> True
```

The round trip gave back the same bytes. Send JSON with the header
`Content-Type: application/json`, so the service reads the body as JSON:

=== "Windows PowerShell"

    ```powershell
    Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/convert/json `
      -InFile pets.xml -ContentType application/xml -OutFile pets.json
    Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/convert/xml `
      -InFile pets.json -ContentType application/json -OutFile pets-back.xml
    ```

=== "macOS and Linux"

    ```bash
    curl --data-binary @pets.xml http://localhost:8000/v1/convert/json -o pets.json
    curl -H 'Content-Type: application/json' --data-binary @pets.json \
      http://localhost:8000/v1/convert/xml -o pets-back.xml
    ```

`-o` and `-OutFile` save the answer to a file, with its bytes as sent.

## 5. When a request fails

A status code of 400 or more means the request did not work. The body says
why, in `detail`:

```python
answer = client.post("/v1/validate", params={"version": "4.0"}, content=xml)
print(answer.status_code, answer.json()["detail"])
# -> 400 Unsupported DDI schema version: '4.0'
```

| Code | Means | Fix |
| --- | --- | --- |
| 400 Bad Request | The body or a parameter cannot be read: not XML, not JSON, an unknown `version` | Send the file itself, with `--data-binary`, and check the parameter |
| 405 Method Not Allowed | The wrong method, such as `GET` on `/v1/validate` | Use `POST` for the endpoints that take a document |
| 413 Request Entity Too Large | The body is larger than the service accepts (32 MB by default) | Send a smaller file, or raise the limit when you start the service |
| 422 Unprocessable Content | Metadata tables were read but have problems (`/v1/tables/import`) | Fix the rows listed in `extra` |
| 503 Service Unavailable | The service is already working on as many documents as it may | Wait the seconds in the `Retry-After` header and send it again |
| 504 Gateway Timeout | The answer took longer than 60 seconds | Send a smaller document, or ask whoever runs the service |

A document that is not valid DDI is **not** an error: the answer is 200,
with `valid` false and the schema errors listed. 400 means the service could
not read what you sent at all.

## 6. Run it for other people

`ddi serve` alone listens on this machine only, which is what you want while
you learn. To serve other machines, the person who runs the service chooses
its settings:

| Setting | `ddi serve` option | `ServerConfig` field | Default |
| --- | --- | --- | --- |
| Address to listen on | `--host 0.0.0.0` (all of this machine's networks) | (set by the server program) | `127.0.0.1` |
| Largest body | `--max-body-mb` | `max_body_bytes` | 32 MiB |
| Documents at once | `--max-jobs` | `max_concurrent_jobs` | the number of CPUs |
| Websites whose pages may call it | `--cors-allow-origin` (repeat it) | `cors_allow_origins` | none |
| Interactive documentation | `--no-openapi` turns it off | `enable_openapi` | on |

**CORS** (cross-origin resource sharing) is how a browser decides whether a
web page from one site may call a service on another. Name each site that
needs it; there is no "allow every site" option, on purpose.

For a real deployment, build the service in a Python file, here
`myapp.py`, and run it with uvicorn, which can start several worker
processes:

```python
from ddi_l.server import ServerConfig, create_app

app = create_app(
    ServerConfig(
        max_body_bytes=8 * 1024 * 1024,
        cors_allow_origins=("https://deposit.example.org",),
        enable_openapi=False,
    )
)
```

Run this from the folder that holds `myapp.py`. `myapp:app` names the file
(without `.py`) and the variable in it, so use your own file's name if it
differs:

```bash
uvicorn myapp:app --host 0.0.0.0 --port 8000 --workers 4
```

The service reads XML with the same protections as the library: no
entities, no network access, nothing written to disk. Validation keeps a
processor busy, so put the service behind a proxy that limits how many
requests each caller sends, and size it for your largest document. The
[HTTP API guide](../server.en.md#running-it-safely) has the details.

---

!!! example "Scenario"
    Your data archive builds a deposit form on its website. When a
    researcher uploads a DDI file, the form must say at once whether it is
    valid, and list the problems. The web team writes JavaScript, not
    Python. You run `ddi-l` as a service for them, show them which requests
    to send and what the answers mean, and choose its settings.

---

## Exercises

1. **(O1)** Start `ddi serve` and check `/health`. Then, in the interactive documentation, find the query parameters that `POST /v1/lint` takes. Check your list from Python by asking the test client for `/v1/versions`, then for the OpenAPI document at `/schema/openapi.json`.

    **Expected output:**

    ```text
    {'default': '3.3', 'supported': ['3.1', '3.2', '3.3']}
    ['version', 'profile', 'rule', 'skip_rule', 'lint_config']
    ```

    ??? success "Answer"

        ```python
        print(client.get("/v1/versions").json())
        openapi = client.get("/schema/openapi.json").json()
        lint = openapi["paths"]["/v1/lint"]["post"]
        print([parameter["name"] for parameter in lint["parameters"]])
        ```

        `/v1/versions` lists the DDI versions the service validates against, and the one it uses when a document does not say. The OpenAPI document is what the interactive documentation is drawn from, so its list matches what you found in the browser.

2. **(O2)** Lint `pets.xml` over HTTP with an allowed-agency list that does not hold `example.org`, using `lint_config`. Print each finding's rule. Then send the same `lint_config` to `/v1/validate` and print `valid`.

    **Expected output:**

    ```text
    ['ddi.agency.allowed', 'ddi.maintainable.labels', 'ddi.maintainable.labels']
    True
    ```

    ??? success "Answer"

        ```python
        config = '{"allowed_agencies": ["ca.statcan"]}'
        found = client.post("/v1/lint", params={"lint_config": config}, content=xml)
        print([finding["rule_id"] for finding in found.json()["lint_findings"]])
        checked = client.post("/v1/validate", params={"lint_config": config}, content=xml)
        print(checked.json()["valid"])
        ```

        `ddi.agency.allowed` reports the agency `example.org`, which the list does not allow. It is a warning, like the two missing labels, so the document is still valid. The configuration applies to this request only: the next request without it gets the default checks.

3. **(O2)** Break `pets.xml` as in Module 7: change `<r:Version>1</r:Version>` to `<r:Version>one</r:Version>`. Send it to `/v1/validate` and print the status code, `valid`, and the line and message of the schema error.

    **Expected output:**

    ```text
    200 False
    5 value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*']
    ```

    ??? success "Answer"

        ```python
        broken = xml.replace(b"<r:Version>1</r:Version>", b"<r:Version>one</r:Version>", 1)
        answer = client.post("/v1/validate", content=broken)
        report = answer.json()
        print(answer.status_code, report["valid"])
        issue = report["schema_issues"][0]
        print(issue["line"], issue["message"])
        ```

        The status code is 200: the service read the document and did its job. The document is what is wrong, so `valid` is false and the error says where.

4. **(O3)** Convert `pets.xml` to JSON over HTTP and back again. Is the XML that comes back the same as the file, byte for byte?

    **Expected output:**

    ```text
    True
    ```

    ??? success "Answer"

        ```python
        as_json = client.post("/v1/convert/json", content=xml)
        back = client.post(
            "/v1/convert/xml",
            content=as_json.content,
            headers={"Content-Type": "application/json"},
        )
        print(back.content == xml)
        ```

        The JSON keeps everything the XML holds, so the round trip is exact. Its keys carry each element's namespace in braces, as in `ddi to-json`: look at `as_json.json()` to see them.

5. **(O4)** For each failed request, say what is wrong and how to fix it. (a) `GET /v1/validate` gives 405. (b) `POST /v1/validate?version=3.4` gives 400. (c) A 50 MB file gives 413 from a service started with `ddi serve`. (d) A request gives 503 at a busy hour.

    ??? success "Answer"

        (a) `/v1/validate` takes a document, so it needs `POST` with the document as the body. (b) The service knows DDI 3.1, 3.2 and 3.3 (see `/v1/versions`): drop `version` or pick one of those. (c) The default limit is 32 MB: whoever runs the service raises it, for example `ddi serve --max-body-mb 64`. (d) The service is working on as many documents as it may: wait the seconds in `Retry-After` and send it again. A client written for a service should do this on its own.

6. **(O5)** The deposit form of the scenario runs at `https://deposit.example.org`. Deposits can reach 100 MB. The archive does not want the interactive documentation on the internet. Build the service with `create_app(ServerConfig(...))`, then check with a test client that `/schema` is gone and that a deposit-form page may call `/v1/validate`. Write the `ddi serve` command with the same settings.

    **Expected output:**

    ```text
    404
    https://deposit.example.org
    ```

    ??? success "Answer"

        ```python
        from ddi_l.server import ServerConfig

        deposit = create_app(
            ServerConfig(
                max_body_bytes=100 * 1024 * 1024,
                cors_allow_origins=("https://deposit.example.org",),
                enable_openapi=False,
            )
        )
        checker = TestClient(app=deposit)
        print(checker.get("/schema").status_code)
        preflight = checker.options(
            "/v1/validate",
            headers={
                "Origin": "https://deposit.example.org",
                "Access-Control-Request-Method": "POST",
            },
        )
        print(preflight.headers["access-control-allow-origin"])
        ```

        A browser asks the service first (this `OPTIONS` request is the "preflight") and sends the deposit only when the answer names the form's site. The command with the same settings:

        ```bash
        ddi serve --host 0.0.0.0 --max-body-mb 100 --cors-allow-origin https://deposit.example.org --no-openapi
        ```

---

## Quiz

???+ question "Question 1 (O1): You start ddi serve on your laptop. A colleague on another machine cannot reach it. Why?"
    **A.** The service needs a password.

    **B.** By default it listens on `127.0.0.1`, this machine only. Start it with `--host 0.0.0.0` to accept other machines.

    **C.** Port 8000 is reserved for browsers.

    **D.** The colleague must install `ddi-l` first.

    ??? success "Answer"
        **B.** The default keeps a service you are trying out private to
        your machine.

???+ question "Question 2 (O2): /v1/validate answers 200 with valid false. What does it mean?"
    **A.** The service failed.

    **B.** The request was wrong.

    **C.** The service read the document, and the document has at least one error, listed in `schema_issues` or `lint_findings`.

    **D.** The document has warnings.

    ??? success "Answer"
        **C.** 200 says the request worked. `valid` is about the document,
        and only errors make it false.

???+ question "Question 3 (O4): Which status code says that the service could not read the body at all?"
    **A.** 200

    **B.** 400

    **C.** 413

    **D.** 503

    ??? success "Answer"
        **B.** 400 Bad Request: not XML, not JSON, or a parameter it does
        not know. 413 means the body was too large to read.

???+ question "Question 4 (O3): Which header do you send with a JSON body to /v1/convert/xml?"
    **A.** `Accept: application/xml`

    **B.** `Content-Type: application/json`

    **C.** `Content-Length: json`

    **D.** None: the service guesses.

    ??? success "Answer"
        **B.** `Content-Type` says what the body is. Without it, the service
        cannot tell JSON from anything else.

???+ question "Question 5 (O5): A web page on the site forms.example.org must call the service from the browser. What do you set?"
    **A.** `--cors-allow-origin https://forms.example.org`

    **B.** `--cors-allow-origin '*'`

    **C.** `--no-openapi`

    **D.** `--max-jobs 1`

    ??? success "Answer"
        **A.** Name each site that may call the service. There is no
        wildcard, so that a deployment never opens to every site by
        mistake.

---

## Check yourself

- [ ] I can start `ddi serve`, check `/health`, and find an endpoint's query parameters at `/schema`. (O1)
- [ ] I can validate and lint a document over HTTP and read `valid`, `schema_issues` and `lint_findings`. (O2)
- [ ] I can convert a document to JSON and back over HTTP and check that nothing was lost. (O3)
- [ ] I can tell from a status code and its `detail` what was wrong with a request, and fix it. (O4)
- [ ] I can choose the settings of a shared deployment and build it with `create_app(ServerConfig(...))`. (O5)

---

!!! tip "Instructor notes"
    - Start the service on the projector and do section 2 live: `/health`,
      then **Try it out** in `/schema`. Seeing a real answer in the browser
      makes the rest concrete.
    - Windows learners: `curl` in Windows PowerShell 5.1 is another command
      with the same name. Use `Invoke-RestMethod` as shown, or type
      `curl.exe`.
    - The most common confusion is between "the request failed" (400 and
      up) and "the document is not valid" (200 with `valid` false). Ask the
      room which one a deposit form should show to the researcher.
    - Exercise 6 is the one to discuss with anyone who will run the service:
      who may call it, how large a document can be, and whether the
      documentation pages should be public.

---

**See also:** [Module 7: Validate from the command line](module-07-cli-validation.en.md) | [HTTP API](../server.en.md)
