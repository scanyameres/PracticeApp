# Architecture

## Components

| Component | Location | Purpose |
|---|---|---|
| UI | `src/scanya_ae_afa_updated0209_1_6/landing.py` | Streamlit app: three equal-height input sections (1 role/job, 2 CV, 3 settings: model, temperature, difficulty), action buttons, results in tabs. Run with `start_app.bat`. |
| Core logic | `src/scanya_ae_afa_updated0209_1_6/core.py` | Builds a `PreparationPlan` (role, seniority, summary, `PracticeQuestion`s) and a `FitAssessment` (score, reasoning, cover letter). All LLM calls go through `_ask_llm()`. No Streamlit code. |
| Prompts | `src/scanya_ae_afa_updated0209_1_6/prompts.py` | All LLM prompt strings as constants (`*_TEMPLATE` ones are filled with `.format()`), the difficulty instructions, and 4 alternative job-opening system prompts (few-shot, Chain-of-Thought, role, constrained) not used by the app yet. |
| Web fetch | `src/scanya_ae_afa_updated0209_1_6/web_fetch.py` | If the job input is a URL, downloads the page (`httpx`) and extracts its text (`beautifulsoup4`). |
| CV reader | `src/scanya_ae_afa_updated0209_1_6/cv_reader.py` | Extracts the text from an uploaded CV PDF (`pypdf`). |
| Config | `src/scanya_ae_afa_updated0209_1_6/config.py` | `get_client()`: OpenAI SDK client for OpenRouter or OpenAI, keys from `.env`. |
| Prompt-log hook | `.claude/hooks/log_prompt.py` | Appends every prompt sent to Claude Code to `.claude/prompt-log/prompts.md`. |
| Task tracker | `TASKS.md` | Status of the mandatory and optional tasks from `115.md`. |

## How they work together

The user fills in the inputs at the top of `landing.py` and clicks one of two buttons. **Build my prep brief** depends on the mode:

- **Generic role title** → `core.build_preparation_plan_generic()` sends the role title, experience level and difficulty to the LLM. If the call fails, it returns stored backup questions instead (with `fallback_reason` set, shown as a warning).
- **Specific job opening** → `core.build_preparation_plan_opening()` sends the job description, with prompts from `prompts.py`, to OpenRouter via `config.get_client()` and gets a structured plan back. If the input is a URL, `web_fetch.py` first replaces it with the page text. Errors are shown in the UI with `st.error`.

Both return a `PreparationPlan`. **Check my fit & write a cover letter** (both modes) calls `core.assess_fit_and_write_cover_letter()` with the CV and the job (in generic mode, a stand-in description from `core.describe_generic_role()`), which returns a `FitAssessment`. Each result is stored in `st.session_state` and shown in its own tab. The third tab, "Practice an answer", is a placeholder (its code is commented out).

## Modules and functions

Imports go one way: `landing.py` → `core.py` → (`prompts.py`, `web_fetch.py`, `config.py`), plus `landing.py` → `cv_reader.py`. Only `landing.py` uses Streamlit.

### `landing.py` (UI)

Streamlit reruns the whole script top to bottom on every click. On each run it:

1. Draws the three input sections (the Settings section holds the model select box, options from `core.AVAILABLE_MODELS`).
2. If a button was clicked, validates the inputs and calls one `core` function inside a spinner; the result goes into `st.session_state` (`"preparation_plan"` or `"fit_assessment"`), errors into `st.error`.
3. Draws the tabs from whatever is in `st.session_state`, so results survive later reruns.

### `core.py` (logic)

| Function / class | Called by | What it does |
|---|---|---|
| `build_preparation_plan_generic(role_title, seniority, difficulty, model, temperature)` | `landing.py` (generic mode) | Fills `GENERIC_ROLE_USER_PROMPT_TEMPLATE` → `_ask_llm(GENERIC_ROLE_SYSTEM_PROMPT, ..., _LLMPlan)` → `PreparationPlan`. On any error: `_fallback_plan()`, where `_select_profile()` picks the first `_ROLE_PROFILES` entry whose keywords match the title and returns its questions plus two general ones, with `fallback_reason` set. |
| `build_preparation_plan_opening(job_description, difficulty, model)` | `landing.py` (job-opening mode) | `_job_text()` → fills `JOB_OPENING_USER_PROMPT_TEMPLATE` with the job text and difficulty instruction → `_ask_llm(JOB_OPENING_SYSTEM_PROMPT, ..., _LLMPlan)` → converts the result into a `PreparationPlan`. |
| `assess_fit_and_write_cover_letter(cv, job_description, model)` | `landing.py` (fit button) | `_job_text()` → fills `FIT_USER_PROMPT_TEMPLATE` → `_ask_llm(FIT_SYSTEM_PROMPT, ..., FitAssessment)`. |
| `describe_generic_role(role_title, seniority)` | `landing.py` (fit button, generic mode) | Fills `GENERIC_ROLE_JOB_TEMPLATE`: a short stand-in job description ("no specific posting, target role: …, don't name a company"). |
| `_job_text(job_input)` | both LLM functions above | Returns the input as is, or, if `web_fetch.is_url()`, the page text from `web_fetch.fetch_job_description()`. |
| `_ask_llm(system_prompt, user_prompt, schema, model)` | both LLM functions above | The only place that talks to the API: `config.get_client("OpenRouter")`, a short connection check (`CONNECTION_CHECK_PROMPT`), then `chat.completions.parse(response_format=schema)`; returns the parsed Pydantic object or raises `ValueError`. |
| `PracticeQuestion`, `PreparationPlan` | — | Dataclasses for one question and the whole brief (what the UI renders). |
| `_LLMPlan`, `FitAssessment` | `_ask_llm()` | Pydantic schemas the LLM must answer in (structured output). |

### `web_fetch.py`, `cv_reader.py`, `config.py`, `prompts.py`

- `web_fetch.is_url(text)`: true for a single `http(s)://` link. `fetch_job_description(url)`: downloads the page, strips scripts/menus, returns at most 15,000 characters; raises `ValueError` if unreachable or almost empty.
- `cv_reader.read_pdf_text(file)`: called by `landing.py` when a PDF is dropped on the CV uploader; returns the text of all pages, or raises `ValueError` for unreadable or scanned (text-less) PDFs. The result replaces the pasted CV text.
- `config.get_client(provider)`: loads `.env` and returns an `OpenAI` client pointed at OpenRouter (or OpenAI).
- `prompts.py`: only constants, no logic.

### Example: "Build my prep brief" with a job URL

`landing.py` → `core.build_preparation_plan_opening()` → `_job_text()` → `web_fetch.fetch_job_description()` → back in `core`, prompt filled from `prompts.py` → `_ask_llm()` → `config.get_client()` → OpenRouter (2 requests: connection check + structured answer) → `_LLMPlan` → `PreparationPlan` → `st.session_state` → "Prep brief" tab.

## Decisions

- **uv** for dependency and environment management, with Python 3.15 and a committed `uv.lock`.
- **Streamlit** for the UI, as required by the task.
- **API keys** are read from a git-ignored `.env` file; `.env.example` documents the required variables.
- **Both modes use the LLM, stored questions are the backup**: the generic mode sends role + seniority instead of a job description. If its LLM call fails, the stored role-profile questions are shown with a warning, so the user always gets a brief. (The job-opening mode has no backup: without a role title there is no profile to pick, so it shows an error.)
- **Structured LLM output**: `client.chat.completions.parse(response_format=_LLMPlan)` makes the model return JSON matching a Pydantic schema, which is parsed straight into `PracticeQuestion` objects. `provider.require_parameters = true` makes OpenRouter use only providers that support this.
- **One shared LLM helper** (`_ask_llm()`): every feature sends one system + user message and gets a parsed schema back, so API code, error handling and OpenRouter options live in one place.
- **CV PDFs are read by the app with `pypdf`**, like URLs: the LLM only receives text. Cheaper and simpler than sending the PDF to the model; scanned PDFs are not supported (the user is asked to paste the text).
- **URLs are fetched by the app, not the LLM**: the chat API cannot open links, so the app downloads the page itself and sends the text (capped at 15,000 characters). Chosen over OpenRouter's web plugin because it reads the exact page, costs nothing extra and is easy to test. Pages that need a login or JavaScript (e.g. LinkedIn) give an error asking the user to paste the description.
- **Fit check and cover letter in one LLM call**: one JSON object with three fields (score, reasoning, cover letter) keeps the parts separate while costing a single request. In generic mode a stand-in job description is sent instead of a posting, so the same function and prompt serve both modes.
- **Model choice**: the user picks one of `core.AVAILABLE_MODELS` (the 3 course models, all with structured-output support) in the Settings section; it is passed to every LLM call.
- **Temperature is opt-in**: the course models are reasoning models and reject `temperature`. A toggle in the Settings section switches to `core.TEMPERATURE_MODELS` (models on the key's allow-list that accept it) and shows a warning; `temperature` is only sent when set, because `require_parameters` would otherwise reject the call.
- **Difficulty in the user message, not the system prompt**: the system prompt holds the fixed task and format; per-request choices (job, difficulty) go in the user message. This keeps system prompts stable and comparable.
- **Prompts in one file** (`prompts.py`), so they are easy to find, compare and replace. Alternative system prompts share the same output fields, so they can be swapped without code changes.
