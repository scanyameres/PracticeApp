# Agent instructions

Shared guidelines for AI coding agents (Claude Code reads this via `CLAUDE.md`; Codex reads it directly).

## Project

Interview Practice Studio: a Streamlit app for preparing for job interviews. It is an early
backbone to build on, so prefer simple, readable code over abstractions.

## Commands

Use `uv` for everything:

- Run the app: `uv run streamlit run src\landing.py`
- Run tests: `uv run python -m unittest discover -s tests`
- Add a dependency: `uv add <package>`

## Code layout

- `src/landing.py`: Streamlit page (UI only).
- `src/practiceapp/`: importable package for app logic. No Streamlit code here, so it stays testable.
- `tests/`: unit tests for the package.

## Authentication

- Built with streamlit-authenticator. Follow `docs/streamlit-auth.md`; if it does not cover
  something, say so instead of guessing.
- Login is optional and lives in the sidebar. Guests must be able to use the whole app.
- `config.yaml` holds secrets (cookie key, password hashes) and must never be committed.
  `config.example.yaml` is the committed template.

## Git

- Commits are authored by the user only. Do not add `Co-Authored-By` lines.
- Commit or push only when asked, and list the commands first.
