# Interview Practice Studio

A Streamlit proof of concept for preparing for job interviews.

## Run locally

From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\src\landing.py
```

Use the sidebar to enter a role title or paste a job description. The app builds
a local preparation brief with focus areas and practice questions, then lets you
draft and self-review an answer.

## Prototype scope

- Role prompts are selected using simple, deterministic local rules.
- Job-description text can surface a small set of recognized skills.
- Drafts and selections live only in the current Streamlit browser session.
- The app does not call an AI service, persist data, or estimate role suitability.

Run the focused tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```