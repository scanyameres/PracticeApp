# Evaluation notes

Remarkable features and good practices in this project, collected for the tutors' review.

## Good practices

### Shared agent instructions (`AGENTS.md` + `CLAUDE.md`)

- Project guidelines for AI coding agents live in one file, `AGENTS.md`: project context,
  commands, code layout, code style, auth rules, and git conventions.
- `CLAUDE.md` contains only `@AGENTS.md`, so Claude Code and Codex read the same instructions.
  The project is not tied to one agent, and there is a single file to keep up to date.
- Both files are committed, so anyone cloning the repo gets the same agent behaviour.

### Secrets kept out of git

- `config.yaml` (cookie signing key, password hashes) is gitignored; `config.example.yaml` is the
  committed template with placeholder values.
- Passwords are stored only as bcrypt hashes, never in plain text.

### Verifying the agent's library usage against the source

- The agent was given a reference doc (`docs/streamlit-auth.md`) and told to report gaps instead
  of guessing; it listed what the doc did not cover.
- The installed library source was checked against the doc. This found an undocumented 0.7 s
  pause on every page update for guests, now disabled with an explanatory comment.

### App logic separated from the UI

- Preparation logic (`src/practiceapp/prep.py`) contains no Streamlit code, so it is covered by
  unit tests (`tests/test_prep.py`) without running the app.
