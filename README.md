# Interview Practice Studio

A Streamlit proof of concept for preparing for job interviews.

## Run locally

From the project root, run the open landing page (or double-click `run_app.bat`):

```powershell
uv run streamlit run src\landing.py
```

Use the sidebar to enter a role title or paste a job description. The app builds
a local preparation brief with focus areas and practice questions, then lets you
draft and self-review an answer.

## Optional login

Everything works without an account. Users can optionally log in from the bottom
of the sidebar, built with
[streamlit-authenticator](https://github.com/mkhorasani/streamlit-authenticator)
(API reference: `docs\streamlit-auth.md`). Logging in or out keeps the current brief.

To enable it:

1. Copy `config.example.yaml` to `config.yaml` (gitignored).
2. Set `cookie.key` to a long random string and add users under `credentials`.
   Plain-text passwords are hashed into `config.yaml` on first login.

Without `config.yaml`, the sidebar shows a note and the rest of the app runs normally.

## Prototype scope

- Role prompts are selected using simple, deterministic local rules.
- Job-description text can surface a small set of recognized skills.
- Drafts and selections live only in the current Streamlit browser session.
- The app does not call an AI service or estimate role suitability.

## Tests

```powershell
uv run python -m unittest discover -s tests
```
