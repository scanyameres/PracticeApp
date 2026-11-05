# Interview Practice App

A Streamlit app that helps you prepare for job interviews with an LLM via the OpenRouter API.
Task description: [115.md](115.md).

## Features

- **Prep brief:** likely interview questions for a role title + experience level, or for a specific job opening (pasted description or URL), at an easy, medium or hard level.
- **Fit check & cover letter:** compares your CV (PDF or pasted text) with the job, gives a 0-10 match score with reasoning, and writes a cover letter.
- **Settings and costs:** choose the model, max tokens, question difficulty and (experimental) temperature; see an estimated maximum cost before sending, and the real cost of each action plus a session total afterwards.
- **Security guard:** every input is checked for misuse (prompt injection, off-topic requests) before any feature runs.
- **Optional login with history:** logged-in users get their job profiles saved, new questions for jobs similar to ones they prepared before, and suggestions of the closest roles they already prepared for.

## Setup

1. Install the dependencies:

   ```bash
   uv sync
   ```

2. Provide your OpenRouter API key ([get one here](https://openrouter.ai/keys)) in **one** of these two ways:

   - **`.env` file (recommended for this project):** copy `.env.example` to `.env` (`cp .env.example .env`, or `copy .env.example .env` in Windows cmd) and fill in `OPENROUTER_API_KEY=sk-or-...`. The file is git-ignored, so the key is never committed.
   - **System environment variable:** set `OPENROUTER_API_KEY` for your user, e.g. in Windows: *Settings → System → About → Advanced system settings → Environment Variables → New*, or in a terminal `setx OPENROUTER_API_KEY "sk-or-..."`. Then open a **new** terminal (or restart VS Code) so the app sees it; already open windows keep the old environment.

   If both are set, the **system variable wins**: the app loads `.env` with `load_dotenv()`, which never overwrites variables that already exist (see `config.get_client()`). If neither is set, the app shows a missing-key error when you use an AI feature.

## Run

Double-click `start_app.bat` (Windows), or:

```bash
uv run streamlit run src/scanya_ae_afa_updated0209_1_6/landing.py
```

The app opens at http://localhost:8501.

**Demo accounts** (to try the history features):

| Username | Password |
|---|---|
| `demo` | `Demo-pass1` |
| `sergi` | `WillGet100%?` |

## Documentation

- [Architecture.md](Architecture.md): components, how they work together, and design decisions.
- [TASKS.md](TASKS.md): status of the mandatory and optional tasks from `115.md`.
