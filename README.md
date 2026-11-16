# Northside Dental RAG CLI

A beginner-friendly Retrieval-Augmented Generation (RAG) demo. Ask questions in plain English; the application searches a local Northside Dental knowledge base, sends the most relevant passages to Google Gemini, and returns a structured JSON answer with source citations.

> **Fictional demonstration only.** Northside Dental Clinic and all clinic details in this repository are invented. This project is not a real clinic service, not medical or dental advice, and is not approved for use with real patients. Do not enter patient names, contact details, health records, or other personal information.

## What it does

1. Loads a local JSON knowledge base (31 prepared topic chunks).
2. Finds relevant passages with a local BM25 keyword retriever.
3. Sends only the selected passages and the question to Gemini.
4. Requests a typed JSON response from Gemini.
5. Validates the answer and attaches citations from the local knowledge base (the model cannot invent source-page metadata).
6. Returns an answer, source IDs, section/page details, a retrieval relevance score, and an `answerable` flag.

The CLI is the main interface. A small FastAPI endpoint is also available as an optional secondary interface. No GUI or hosted backend is required.

## Requirements

- Windows 10/11, macOS, or Linux.
- Python 3.11 or newer. The automated test matrix covers Python 3.11 through 3.15.
- An internet connection for Gemini requests.
- A Google Gemini API key. You can create one in [Google AI Studio](https://aistudio.google.com/app/apikey).

The default model is `gemini-3.5-flash-lite`. The Google Gen AI SDK is pinned to the maintained 2.x line, and `httpx2` is used for Starlette's current test client. Free-tier access and rate limits depend on Google's current availability, your project, region, and account. Check the [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite), [pricing/free-tier information](https://ai.google.dev/gemini-api/docs/pricing), and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) before use. Free access is not an unlimited-use guarantee.

## Quick start — Windows PowerShell

These instructions deliberately use the virtual environment's Python executable directly. **You do not need to activate the virtual environment**, so PowerShell's script-execution policy will not block setup.

### 1. Install Python and Git

Install Python 3.11+ from [python.org](https://www.python.org/downloads/) and Git from [git-scm.com](https://git-scm.com/downloads). During Python installation, enable the Python Launcher if the installer offers that option.

Open a new PowerShell window and check:

```powershell
py --version
git --version
```

### 2. Choose a writable folder, then download the project

**Important for Windows users:** PowerShell may open in `C:\Windows\System32` (you can see this after `PS` in the prompt). This is a protected Windows system folder. Do not clone projects there. Git will usually report `could not create work tree dir ... Permission denied`.

The commands below work even when PowerShell starts in `C:\Windows\System32`. They create a `Projects` folder inside your own Windows user profile and move into it before cloning:

```powershell
$projectRoot = Join-Path $HOME "Projects"
New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null
Set-Location $projectRoot
git clone https://github.com/rahil565665-afk/RAG-CLI2.git
Set-Location .\RAG-CLI2
```

Your project will be located at:

```text
C:\Users\<your-Windows-username>\Projects\RAG-CLI2
```

You can use a different writable location, such as Downloads, by changing the first command to:

```powershell
$projectRoot = Join-Path $HOME "Downloads"
```

After cloning, verify that PowerShell is inside the repository and that the project files are present:

```powershell
Get-Location
Get-ChildItem
```

You should see `requirements.txt`, `.env.example`, the `app` folder, and the `data` folder. Continue with step 3 only after these files are visible.

**If you see “destination path 'RAG-CLI2' already exists”:** the repository may already have been cloned. Move into the existing folder instead of cloning it again:

```powershell
Set-Location (Join-Path $HOME "Projects\RAG-CLI2")
```

### 3. Create a virtual environment

```powershell
py -3 -m venv .venv
```

This creates an isolated Python environment in the project's `.venv` folder.

### 4. Install the dependencies

Run these commands exactly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Wait until pip reports that the packages were installed successfully. This project intentionally uses plain `uvicorn`, not `uvicorn[standard]`, to avoid optional native build dependencies that can cause installation failures on some Python/Windows combinations.

### 5. Create your local environment file

```powershell
Copy-Item .env.example .env
notepad .env
```

In Notepad, replace the placeholder with your own Gemini API key:

```dotenv
GEMINI_API_KEY=PASTE_YOUR_OWN_KEY_HERE
GEMINI_MODEL=gemini-3.5-flash-lite
TOP_K=4
MIN_RELEVANCE=0.22
RATE_LIMIT_PER_MINUTE=30
```

Save the file and close Notepad.

**Keep your key private.** The real `.env` file is ignored by Git. Never paste your key into source code, README files, screenshots, issue reports, or chat messages. Do not commit `.env`. If a key is exposed, revoke it in Google AI Studio and create a replacement.

### 6. Run your first question

```powershell
.\.venv\Scripts\python.exe -m app.cli "What are the clinic hours?"
```

A successful response is JSON shaped like this (wording and scores vary):

```json
{
  "answer": "The clinic is open ...",
  "sources": [
    {
      "chunk_id": "NSDC-01-003",
      "section_id": "01",
      "section_title": "Clinic profile",
      "subsection": "Opening hours and holiday/weather closures",
      "source_document": "Northside_Dental_Clinic_Knowledge_Base.pdf",
      "source_pages": [2],
      "relevance_score": 0.46
    }
  ],
  "confidence_score": 95.0,
  "answerable": true
}
```

The exact values above are illustrative. The response is generated from the fictional local data. The `confidence_score` is a 0–100 retrieval-support score based on how many meaningful query terms match the cited knowledge-base passage and the strength of the BM25 match. It is a ranking/support indicator, not a calibrated probability that an answer is factually correct.

## Updating an existing Windows checkout

If you already cloned the repository earlier, update the code and dependencies from the latest `main` branch. Run these commands from inside the `RAG-CLI2` folder:

```powershell
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m pip uninstall -y httpx
.\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
```

The uninstall step removes the legacy `httpx` package from older virtual environments; this project now uses `httpx2` for Starlette's test client and the Google Gen AI SDK. The dependency update also upgrades the older Google Gen AI SDK to the 2.x version used by this project. Keep using the same virtual-environment interpreter for tests and CLI commands.

## Asking questions

### One question at a time

In Windows PowerShell, you can enter a question **without quotation marks**. This also avoids PowerShell's `>>` continuation prompt when an opening quote is accidentally left unclosed.

```powershell
.\.venv\Scripts\python.exe -m app.cli What is the clinic name?
.\.venv\Scripts\python.exe -m app.cli What does the clinic do?
.\.venv\Scripts\python.exe -m app.cli Does the clinic accept insurance?
.\.venv\Scripts\python.exe -m app.cli What is your adress?
```

Quoted questions are still supported, but opening a quote without closing it keeps PowerShell waiting and the Python application will not start. Run each question through `python -m app.cli`; do not type a plain-English question by itself at the PowerShell prompt.

### Interactive mode

Start the CLI without a question:

```powershell
.\.venv\Scripts\python.exe -m app.cli
```

At the `Question>` prompt, type a question and press Enter. Type `exit` or `quit` to leave.

### Useful options

```powershell
# Compact, one-line JSON
.\.venv\Scripts\python.exe -m app.cli --compact "What are the clinic hours?"

# Retrieve up to five knowledge-base passages
.\.venv\Scripts\python.exe -m app.cli --top-k 5 "What services are available?"

# See command-line help
.\.venv\Scripts\python.exe -m app.cli --help
```

The number of chunks can be set from 1 to 5. The `TOP_K` and `MIN_RELEVANCE` defaults can also be changed in your local `.env` file. If no passage clears the relevance threshold, Gemini is still called without weak or unrelated evidence so it can give a safe fallback.

## Run automated tests

Tests do not call Gemini and do not require an API key. They use local test data and mocked model responses.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The test suite covers retrieval, knowledge-base integrity, abstention, emergency phrase handling, citation filtering, the API endpoint, and the Gemini structured-output schema. GitHub Actions runs the same suite automatically on pushes and pull requests for Python 3.11, 3.12, 3.13, 3.14, and 3.15. The first CI run for this repository completed successfully on all three versions.

## Questions outside the knowledge base

The assistant is not limited to returning the same fixed abstention message when retrieval finds no relevant passage. It uses two different fallback behaviours:

- **Clinic-specific questions:** If the knowledge base does not say whether Northside Dental offers a service, accepts a plan, charges a fee, or follows a policy, the assistant says that the information is not specified and recommends checking with the front desk. Missing information is not treated as a "no" or a "yes". For example, asking "Do you do tooth replacement?" should produce an unconfirmed/not-documented response—not a claim that the clinic does or does not offer it.
- **General educational questions:** For broad dental-information questions, the assistant may provide a concise general explanation using model knowledge. It labels that content as general information and does not present it as a Northside Dental service, policy, or clinical assessment.

When there is no cited knowledge-base evidence, the response still contains a helpful `answer`, but `sources` is empty, `confidence_score` is `0.0`, and `answerable` is `false`. In this API, `answerable` means that the response is supported by the local clinic knowledge base; it does not mean that the assistant returned no text. The zero score makes clear that the answer has no retrieval support from this clinic database.

The model must still avoid diagnoses, prescriptions, treatment decisions, and individualised clinical advice. Questions about a person's symptoms or care should be referred to a licensed dental professional.

## Gemini reliability and retries

The application reuses one Google Gen AI SDK client instead of creating a new HTTP connection pool for each question. It explicitly configures one initial request plus up to four retries for transient HTTP/network failures, using exponential backoff. Retryable HTTP statuses include 408, 429, 500, 502, 503, and 504.

The CLI now distinguishes quota/rate-limit errors, authentication errors, unavailable models, invalid requests, and temporary provider/network failures. Persistent quota limits, invalid credentials, disabled models, or malformed requests cannot be fixed by retrying; the message explains what to check. A 429 may still require waiting for quota to reset.

This improves resilience to temporary provider/network interruptions, but no client can guarantee that an external API is always available. For a real service, add operational monitoring, request limits, and a documented outage/fallback policy.

## Optional: run the HTTP API

The command-line interface is the primary way to use this project. To start the optional local FastAPI server:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Then open:

- API documentation: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

This server is local to your computer by default. It is not deployed to the internet.

## macOS and Linux

From Terminal, install Python 3.11+ and Git, then run:

```bash
git clone https://github.com/rahil565665-afk/RAG-CLI2.git
cd RAG-CLI2
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Open `.env` in a text editor, add your own Gemini API key, and save it. Then run:

```bash
./.venv/bin/python -m app.cli "What are the clinic hours?"
./.venv/bin/python -m pytest -q
```

## Project structure

```text
RAG-CLI2/
├── app/
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Reads local .env settings
│   ├── gemini_client.py    # Gemini API and structured JSON generation
│   ├── main.py             # Optional FastAPI interface
│   ├── rag_service.py      # Orchestrates retrieval, generation and citations
│   ├── retrieval.py        # Local BM25 retrieval
│   └── schemas.py          # Pydantic response schemas
├── data/
│   ├── northside_dental_knowledge_base.json
│   └── northside_dental_knowledge_base_section_index.md
├── tests/                  # Offline automated tests, including schema regression coverage
├── .github/workflows/
│   └── tests.yml           # CI tests on Python 3.11, 3.12 and 3.13
├── .env.example            # Safe configuration template (no real key)
├── .gitignore              # Excludes .env and local environment files
├── requirements.txt
└── README.md
```


## Architecture and design decisions

The project uses a deliberately small, CLI-first RAG architecture:

1. **Local knowledge source:** the fictional clinic handbook is represented as a JSON file containing 31 topic-based chunks. Each chunk carries its own stable ID, section information, source page, keywords, and content.
2. **Local retrieval before generation:** a BM25 keyword retriever ranks the chunks on the user's machine. The project does not require a hosted vector database, embedding service, or separate retrieval server.
3. **Relevance gate and top-k selection:** only the highest-ranked chunks that meet the configured minimum relevance threshold and cover at least 60% of the meaningful query terms are sent as evidence. The number of chunks is limited to five. This prevents a single shared word (for example, “tooth”) from being treated as proof of a specific service such as tooth replacement.
4. **Grounded answer generation:** the application sends the question and selected evidence to Google Gemini. The model is instructed to answer from those passages only and to abstain when the supplied evidence is insufficient.
5. **Structured response validation:** Pydantic validates the model's small response schema. The application then maps cited chunk IDs back to the original local records and builds the source citations itself, rather than trusting the model to invent section or page metadata.
6. **Safety-first deterministic handling:** a narrow emergency-phrase rule runs before a Gemini call. It is only a limited backstop, not a diagnostic system or a replacement for local emergency services.
7. **Two ways to use the same service:** the command-line interface is the primary user interface. FastAPI exposes the same RAG service through a small optional local HTTP API.

These decisions keep the demo understandable, inexpensive to run, and straightforward for a new developer to inspect. The lexical BM25 approach is intentionally transparent, although it can miss synonyms and paraphrases.

## Libraries and frameworks used

| Library / tool | How it is used |
|---|---|
| Python standard library | CLI argument handling, JSON processing, file paths, tokenization, BM25 scoring, and regular-expression safety checks |
| `google-genai` | Calls the Gemini Developer API and requests structured JSON output |
| Pydantic | Defines and validates the model draft and application response schemas |
| `python-dotenv` | Loads the developer's local `.env` configuration without hard-coding API keys |
| FastAPI | Provides the optional HTTP API on top of the same RAG service |
| Uvicorn | Runs the optional FastAPI application locally |
| pytest | Runs automated tests for retrieval, service behavior, API behavior, and Gemini schema compatibility |
| HTTPX2 | Provides the supported transport for Starlette's current test client |

No separate vector database, embeddings framework, LangChain, or frontend framework is required by the current implementation.

## AI-assisted development

AI coding assistants were used to write most of the code, including much of the CLI, retrieval and RAG service implementation, Gemini integration, schemas, tests, and documentation.

My main contribution was deciding what the application should look like architecturally and specifying that design in a detailed implementation prompt. I defined the intended CLI-first workflow, local knowledge-base retrieval, Gemini-powered grounded response generation, structured JSON output, source citations, and the supporting technology choices before the implementation was generated.

After that, my hands-on coding involvement was mainly in running the project, identifying errors during installation and testing, and correcting those issues. I tested the working application with real Gemini requests and iterated on problems such as Windows dependency installation and Gemini's structured-output schema compatibility.

In other words, AI coding assistants produced most of the actual code; I directed the architecture and requirements, then focused on troubleshooting and validating the result.

## Configuration

| Setting | Default | Purpose |
|---|---:|---|
| `GEMINI_API_KEY` | required | Your private Google Gemini API key |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Gemini model used to generate answers |
| `TOP_K` | `4` | Maximum number of retrieved passages (1–5) |
| `MIN_RELEVANCE` | `0.22` | Minimum retrieval relevance required for a passage to be sent as supporting evidence |
| `RATE_LIMIT_PER_MINUTE` | `30` | Local application request limit |

The app loads `.env` from the project root. Environment variables already set in the shell take precedence over `.env`.

## Troubleshooting

### PowerShell says running scripts is disabled

You do not need to activate the virtual environment. Use the explicit interpreter path in the commands above, for example:

```powershell
.\.venv\Scripts\python.exe -m app.cli --help
```

This avoids running `Activate.ps1` and avoids changing your machine's execution policy.

### Git says `could not create work tree dir 'RAG-CLI': Permission denied`

This usually means PowerShell is currently in a protected folder such as `C:\Windows\System32`. It is not a Python or Git installation problem. Do not run PowerShell as Administrator and do not change Windows folder permissions. Instead, clone the project into a folder you own:

```powershell
$projectRoot = Join-Path $HOME "Projects"
New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null
Set-Location $projectRoot
git clone https://github.com/rahil565665-afk/RAG-CLI2.git
Set-Location .\RAG-CLI2
```

If cloning already failed, no repository folder was created in the protected location; run the commands above. If the project has already been cloned under another folder, use `Set-Location` with that full folder path rather than cloning it again.

### `requirements.txt` cannot be found

Make sure the PowerShell working directory is the repository root (the folder named `RAG-CLI2`), not its parent folder:

```powershell
Get-Location
Get-ChildItem requirements.txt
```

### API key is missing

- Confirm the file is named exactly `.env`, not `.env.txt`.
- Confirm `.env` is in the same folder as `requirements.txt`.
- Confirm the line starts with `GEMINI_API_KEY=` and contains your own key.
- Do not include angle brackets or the words `PASTE_YOUR_OWN_KEY_HERE`.

### Gemini returns 400 with `additional_properties`

The `GeminiDraft` schema in `app/schemas.py` must keep `ConfigDict(extra="ignore")`. Gemini's response-schema endpoint does not accept the extra `additionalProperties` field generated by a strict Pydantic schema. Do not change that setting back to `extra="forbid"`.

### Gemini returns 401 or 403

Check that the key is valid, the corresponding Google AI Studio project can use the Gemini API, and the selected model is enabled for the project. If the key was exposed, revoke it and create a new one.

### Gemini returns 404 or says the model is unavailable

Check the current [Gemini model list](https://ai.google.dev/gemini-api/docs/models) and confirm the model ID is available to your project. You can change `GEMINI_MODEL` in `.env`. Model availability can change over time and may vary by account or region.

### Gemini reports a temporary provider or network error

The SDK automatically retries common transient HTTP/network failures with exponential backoff. The CLI now prints an actionable error code after those retries are exhausted. For `GEMINI_TEMPORARILY_UNAVAILABLE` or `GEMINI_NETWORK_ERROR`, check connectivity and try again after a short interval. Persistent quota exhaustion requires the quota window to reset or the project limit to be increased.

### Gemini returns 429 / quota exceeded

This means a rate or usage limit was reached. Check the project's current [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and usage in Google AI Studio. Wait for the relevant quota window to reset or use a project/model with available quota. Do not assume free tier means unlimited requests.

### The answer says the knowledge base does not contain enough information

The local retriever uses BM25 keyword matching, not semantic embeddings. Try a more specific question using terms likely to appear in the clinic document, or try `--top-k 5`. A very low relevance threshold can introduce unrelated passages, so change `MIN_RELEVANCE` carefully.

### The model responds but the CLI reports a provider error

Check the model ID, network connection, key, and quota. The app intentionally hides low-level provider errors in normal CLI output so it does not accidentally expose request details or credentials. Run the automated tests to verify the local installation separately:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Fictional address in the sample knowledge base

The Northside Dental sample profile uses this invented demonstration address: **18 Cedar Lane, Northside District, Riverton, Example State 00018, USA**. It is stored in the existing clinic-profile knowledge-base chunk so questions such as "What is the clinic address?" or the common typo "What is your adress?" can retrieve the profile. The district, state and postal code are fictional additions for this demo, not a real location.

## Safety and limitations

- All Northside Dental content is fictional demonstration data.
- Do not use this project to answer real patient questions or make treatment decisions.
- Do not enter or upload real patient information.
- The app does not diagnose, prescribe, interpret X-rays, or provide individualized clinical advice.
- Its emergency phrase check is a narrow deterministic backstop, not a diagnostic tool and not a substitute for local emergency services.
- BM25 is lexical retrieval; it can miss synonyms and paraphrases.
- No appointment booking, live insurance verification, or patient-record integration is included.
- Google Gemini API usage is subject to Google's terms, privacy practices, model availability, and rate limits.
