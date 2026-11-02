# Agent instructions

Shared guidelines for AI coding agents (Claude Code reads this via `CLAUDE.md`; Codex reads it directly).

## Project

Interview Practice Studio: a Streamlit app for preparing for job interviews.

This is a demo project for a course. The owner has some Python experience, and the app is
built quickly with heavy agent support. Tutors will review it, so the owner must be able to
keep an overview of every part and module and explain it.

The course is about AI Engineering: using LLMs and agents to build things. The goal is to show
the tools are used correctly, not to deliver a perfect frontend or backend. Weigh effort and
proposals accordingly.

## Code style

- Keep code simple. Avoid extra complexity, clever abstractions, and fancy or niche libraries;
  prefer the standard library, Streamlit, and the dependencies already in `pyproject.toml`.
- Document the code so it stays readable:
  - a short module docstring at the top of every file saying what it is for;
  - docstrings on functions and classes;
  - comments explaining *why* a non-obvious line exists (workarounds, library quirks).
- Prefer small, well-named functions over long blocks, but don't split code just for its own sake.

## Evaluation notes

`evaluation.md` collects remarkable features and good practices for the tutors' review.
When a relevant feature or good practice is completed, propose key points to add there.
Do not edit `evaluation.md` without the owner's approval.

Keep it short. Only propose points relevant to the course focus (how LLMs and agents are used,
engineering practices around them, security, testing), not ordinary UI or UX details.

## Commands

Use `uv` for everything:

- Run the app: `uv run streamlit run src\landing.py`
- Run tests: `uv run python -m unittest discover -s tests`
- Add a dependency: `uv add <package>`

## Code layout

- `src/landing.py`: Streamlit page (UI only).
- `src/practiceapp/`: importable package for app logic. No Streamlit code here, so it stays testable.
- `tests/`: unit tests for the package.

`ARCHITECTURE.md` (local only, not in git) is an agent-written overview with diagrams. Use it as
orientation, not as truth: it may be outdated, so check the code before relying on it.

## Authentication

- Built with streamlit-authenticator. Follow `docs/streamlit-auth.md`; if it does not cover
  something, say so instead of guessing.
- Login is optional and lives in the sidebar. Guests must be able to use the whole app.
- `config.yaml` holds secrets (cookie key, password hashes) and must never be committed.
  `config.example.yaml` is the committed template.

## Git

- Commits are authored by the user only. Do not add `Co-Authored-By` lines.
- Commit or push only when asked, and list the commands first.
