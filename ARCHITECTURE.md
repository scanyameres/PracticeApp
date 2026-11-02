# Architecture

How Interview Practice Studio is put together: files, libraries, runtime behaviour and data.
Read this before adding a feature or user flow. Agent rules live in `AGENTS.md`; the review
notes for tutors live in `evaluation.md`.

Diagrams are written in [Mermaid](https://mermaid.js.org/), so they are plain text, versioned
with the code and rendered by GitHub and by VS Code (built-in preview, or the
"Markdown Preview Mermaid Support" extension). **Update the matching diagram in the same change
as the code.**

## 1. Overview

A single-page Streamlit app, run locally. It has two layers and one optional local file:

```mermaid
flowchart LR
    user(["User (browser)"])

    subgraph ui["UI layer: src/landing.py"]
        sidebar["Sidebar<br/>brief inputs + login"]
        main["Main area<br/>brief tab + practice tab"]
    end

    subgraph logic["Logic layer: src/practiceapp/"]
        prep["prep.py<br/>build_preparation_plan()"]
    end

    state[("st.session_state<br/>(per browser session, in memory)")]
    auth["streamlit-authenticator"]
    config[("config.yaml<br/>(gitignored secrets)")]
    tests["tests/test_prep.py"]

    user <-->|"HTTP / websocket<br/>localhost:8501"| ui
    sidebar -->|"role, job description, seniority"| prep
    prep -->|"PreparationPlan"| state
    state --> main
    sidebar --> auth
    auth <-->|"read users, write hashes + login flags"| config
    auth --> state
    tests -.->|"unit tests, no Streamlit"| prep
```

Key design decisions:

| Decision | Why |
|---|---|
| UI (`landing.py`) and logic (`practiceapp/`) are separate; no Streamlit imports in the package | Logic can be unit tested without running the app. |
| Prep content is deterministic (fixed role profiles + keyword matching) | Transparent, testable prototype; no AI service is called yet. |
| State lives only in `st.session_state` | No database needed for the prototype; nothing persists after the session ends. |
| Login is optional and isolated in the sidebar | Guests can use the whole app; the app still runs if `config.yaml` is missing. |
| Secrets in gitignored `config.yaml`, template in `config.example.yaml` | Cookie key and password hashes never reach git. |

## 2. File map

```text
PracticeApp/
├── src/
│   ├── landing.py            UI: the Streamlit page (sidebar, tabs, login). Entry point.
│   └── practiceapp/          Importable package with app logic (no Streamlit code).
│       ├── __init__.py       Empty; marks the package.
│       └── prep.py           Data classes + build_preparation_plan(). Role profiles, skill terms.
├── tests/
│   └── test_prep.py          unittest cases for build_preparation_plan().
├── docs/
│   └── streamlit-auth.md     Reference extract of the streamlit-authenticator API, given to agents.
├── config.example.yaml       Committed template for auth settings and users.
├── config.yaml               Real auth config (gitignored; created by copying the template).
├── pyproject.toml            Project metadata and dependencies (managed with uv).
├── uv.lock                   Exact locked dependency versions.
├── .python-version           Python version used by uv (3.15).
├── run_app.bat               Double-click launcher for Windows (runs the Streamlit command).
├── README.md                 What the app does and how to run it.
├── ARCHITECTURE.md           This file.
├── AGENTS.md                 Instructions shared by all AI coding agents.
├── CLAUDE.md                 Only "@AGENTS.md", so Claude Code reads the same instructions.
└── evaluation.md             Good practices collected for the tutors' review.
```

## 3. Technology stack

| Area | Technology | Used for | Where |
|---|---|---|---|
| Language | Python 3.15 | Everything | `.python-version`, `pyproject.toml` |
| Package / env manager | [uv](https://docs.astral.sh/uv/) (build backend `uv_build`) | Virtualenv, dependencies, running commands | `pyproject.toml`, `uv.lock` |
| UI framework | [Streamlit](https://streamlit.io/) | Page layout, widgets, session state, local web server | `src/landing.py` |
| Authentication | [streamlit-authenticator](https://github.com/mkhorasani/streamlit-authenticator) ≥ 0.4.2 | Login/logout widgets, bcrypt password hashing, auth cookie | `src/landing.py`, `config.yaml` |
| Config format | YAML | Auth cookie settings and users | `config.example.yaml`, `config.yaml` |
| Standard library | `dataclasses`, `re`, `pathlib` | Immutable plan objects, skill matching, config path | `prep.py`, `landing.py` |
| Testing | `unittest` (standard library) | Unit tests of the logic layer | `tests/` |
| Declared, not used yet | `openai`, `tiktoken`, `IPython` | Reserved for upcoming LLM features | `pyproject.toml` only |

## 4. How a page run works

Streamlit re-executes `landing.py` from top to bottom on **every** interaction (click, typing,
tab change). Local variables are lost between runs; only `st.session_state` survives. That is
why the plan and login status are stored there, and why the code calls `st.rerun()` right after
changing them (to redraw the page with the new state immediately).

```mermaid
sequenceDiagram
    actor U as User
    participant S as Streamlit server
    participant L as landing.py
    participant P as practiceapp.prep
    participant SS as st.session_state

    U->>S: Click "Build my prep brief"
    S->>L: Rerun whole script
    L->>L: Validate inputs (role title, job description)
    L->>P: build_preparation_plan(role, job_description, seniority)
    P-->>L: PreparationPlan
    L->>SS: preparation_plan = plan<br/>remove saved_practice_answer
    L->>S: st.rerun()
    S->>L: Rerun whole script
    L->>SS: get preparation_plan
    L-->>U: Render summary, metrics, brief tab, practice tab
```

### Session state keys

| Key | Set by | Contents |
|---|---|---|
| `preparation_plan` | "Build my prep brief" button | The current `PreparationPlan` |
| `saved_practice_answer` | "Save practice draft" button | `{"question", "answer", "checks"}`; cleared when a new brief is built |
| `practice_question`, `practice_answer` | Widgets (via `key=`) | Selected question, draft text |
| `review_context`, `review_actions`, `review_outcome` | Checkbox widgets | Self-review ticks |
| `authentication_status`, `name`, `username`, … | streamlit-authenticator | `None` = not tried, `False` = wrong credentials, `True` = logged in |

Because login only adds auth keys and never clears the others, logging in or out keeps the brief.

## 5. User flows

```mermaid
flowchart TD
    start(["Open app"]) --> intro["Main area: intro<br/>(no brief yet)"]
    intro --> mode{"Start with?"}
    mode -->|"Role title"| role["Enter role title + experience level"]
    mode -->|"Job description"| jd["Enter role title, level<br/>and paste job description"]
    role --> build["Click 'Build my prep brief'"]
    jd --> build
    build --> valid{"Inputs valid?"}
    valid -->|"No"| err["Error in sidebar"] --> mode
    valid -->|"Yes"| brief["Brief shown:<br/>summary, focus areas, questions"]
    brief --> tab{"Tab"}
    tab -->|"Prep brief"| explore["Expand questions,<br/>read why they matter"]
    tab -->|"Practice an answer"| practice["Pick question, draft answer,<br/>tick self-review checks"]
    practice --> save["Click 'Save practice draft'"]
    save --> empty{"Answer empty?"}
    empty -->|"Yes"| warn["Warning"] --> practice
    empty -->|"No"| saved["Draft kept in session state"]
    brief -.->|"Rebuild with new inputs"| mode
```

### Optional login

```mermaid
stateDiagram-v2
    [*] --> NoConfig: config.yaml missing
    [*] --> Guest: config.yaml present
    NoConfig: Sidebar shows "Login unavailable" note
    Guest: Login form in collapsed expander
    Failed: Error shown, expander open
    LoggedIn: "Signed in as ..." + Logout button
    Guest --> LoggedIn: correct credentials (st.rerun)
    Guest --> Failed: wrong credentials
    Failed --> LoggedIn: correct credentials (st.rerun)
    Failed --> Failed: wrong credentials
    LoggedIn --> Guest: Logout (st.rerun)
```

The authenticator also **writes** to `config.yaml`: it hashes plain-text passwords on first
login (`auto_hash`) and updates `logged_in` and `failed_login_attempts`. It sets a signed cookie
(name, key and expiry from `config.yaml`) so a returning user stays logged in.
`login_sleep_time=0` disables the library's 0.7 s pause on every rerun for guests.

## 6. Logic layer: data model

```mermaid
classDiagram
    class PreparationPlan {
        <<frozen dataclass>>
        role_title: str
        seniority: str
        role_summary: str
        focus_areas: tuple~str~
        questions: tuple~PracticeQuestion~
    }
    class PracticeQuestion {
        <<frozen dataclass>>
        category: str
        prompt: str
        why_it_matters: str
    }
    class _RoleProfile {
        <<frozen dataclass, internal>>
        key: str
        match_terms: tuple~str~
        summary: str
        focus_areas: tuple~str~
        questions: tuple~PracticeQuestion~
    }
    PreparationPlan "1" *-- "1..7" PracticeQuestion
    _RoleProfile "1" *-- "4" PracticeQuestion
```

`build_preparation_plan(role_title, job_description="", seniority="Mid-level")` is the only public
function:

```mermaid
flowchart LR
    in["role_title + job_description"] --> sel["_select_profile()<br/>first profile whose match_terms<br/>appear; else General"]
    in --> sk["_matching_skills()<br/>whole-word match against<br/>_SKILL_TERMS"]
    sel --> fa["focus_areas =<br/>top 2 skills + profile areas<br/>(deduplicated, max 5)"]
    sk --> fa
    sel --> q["questions =<br/>skill question (if any)<br/>+ 4 profile questions<br/>+ Behavioral + Motivation<br/>(max 7)"]
    sk --> q
    fa --> out["PreparationPlan"]
    q --> out
```

Role profiles (in match order): Software engineering, Product management, Data analysis,
Marketing, Customer success, General (fallback).

## 7. Extending the app

| To add… | Change | Keep in mind |
|---|---|---|
| A new role family | Add a `_RoleProfile` to `_ROLE_PROFILES` in `prep.py`, **before** "General" | Order matters: the first match wins. Add a test. |
| A recognised skill | Add it to `_SKILL_TERMS` | Matched as a whole word, case-insensitive. |
| New logic (e.g. LLM-generated questions or answer feedback) | New module in `src/practiceapp/` (e.g. `llm.py`) returning the existing dataclasses | No Streamlit code there; mock the API in tests; API key in a gitignored file or env var, never in git. |
| A new UI section or flow | `src/landing.py` (new tab, or a new page) | Store anything that must survive a rerun in `st.session_state`. Update the flow diagram in section 5. |
| Saved history for logged-in users | Persist `saved_practice_answer` keyed by `st.session_state["username"]` | Guests must keep working without it. Needs a storage choice (e.g. a local JSON/SQLite file, gitignored). |
| A dependency | `uv add <package>` | Updates `pyproject.toml` and `uv.lock`; add it to section 3. |

Commands: run `uv run streamlit run src\landing.py`; test `uv run python -m unittest discover -s tests`.
