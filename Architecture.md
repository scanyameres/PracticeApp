# Architecture

## Components

| Component | Location | Purpose |
|---|---|---|
| Python package | `src/scanya_ae_afa_updated0209_1_6/` | Application code (currently a placeholder). |
| Prompt-log hook | `.claude/hooks/log_prompt.py` | Appends every prompt sent to Claude Code to `.claude/prompt-log/prompts.md`. |

## How they work together

Nothing is connected yet. The planned flow: Streamlit UI → security guard → OpenRouter API → response shown in the UI.

## Decisions

- **uv** for dependency and environment management, with Python 3.15 and a committed `uv.lock`.
- **Streamlit** for the UI, as required by the task.
- **API keys** are read from a git-ignored `.env` file; `.env.example` documents the required variables.
