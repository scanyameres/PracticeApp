# Tasks Tracker

Mandatory and optional tasks from `115.md`. Bonus points need **at least 2 Medium and 1 Hard** optional tasks.

Legend: `[x]` done · `[~]` partially done · `[ ]` not started

## Mandatory

- [x] 1. Research the nature of interview preparation you want to do.
  - Chosen: prep brief with practice questions, from a generic role + seniority (`build_preparation_plan_generic()`) or from a specific job description (`build_preparation_plan_opening()`), both via the LLM. If the generic LLM call fails, stored backup questions (`_ROLE_PROFILES` in `core.py`) are shown with a warning.
- [x] 2. Decide how to build the front-end (Streamlit components or Next.js).
  - Streamlit (`landing.py`): three equal-height input panels (1 role/job + question difficulty, 2 CV, 3 settings: model, max tokens, costs, temperature), no sidebar, one button below panels 1 and 2 (same width), wide layout capped at 1200 px (small CSS rule), results in tabs ("Potential questions", "Practice interview" placeholder, "Fit check & cover letter", "My history" when logged in; a button switches to its tab and marks it with a green dot until clicked), one expander per question, spinner while the LLM runs, `st.error` if the call fails.
- [x] 3. Choose an OpenRouter model (`openai/gpt-6-luna`, `anthropic/claude-sonnet-5.5` or `openai/gpt-6.1-sol`; embeddings: `qwen/qwen3-embedding-8b`, `openai/text-embedding-3-small/large`).
  - Default `openai/gpt-6-luna` (`DEFAULT_MODEL` in `core.py`); the user can switch to the other two (see Medium 7). All three support structured outputs and are called through the OpenAI SDK pointed at OpenRouter (`config.get_client()`).
- [~] 4. Write at least 5 system prompts with different techniques (few-shot, Chain-of-Thought, zero-shot, etc.) and compare which works best.
  - Done: 5 system prompts for the job-opening task in `prompts.py`: `JOB_OPENING_SYSTEM_PROMPT` (zero-shot, used by the app) and the alternatives `_FEW_SHOT`, `_CHAIN_OF_THOUGHT`, `_ROLE`, `_CONSTRAINED`. Also `FIT_SYSTEM_PROMPT` (role + constraints). Techniques used with Claude during development: see Annex. Missing: try the alternatives in the app and note which works best.
- [x] 5. Add at least one security guard to prevent misuse.
  - `guard.py`, run before every action (`_check_with_guard()` in `landing.py`): (1) length limits per field, (2) an LLM check with the cheapest model (`GUARD_SYSTEM_PROMPT`, `GuardVerdict` schema) that flags prompt injection, off-topic and harmful input. Flagged input shows a warning and the action does not run. Plus: URLs to localhost/private networks are blocked in `web_fetch.py`. Tested: injection in role title and CV, off-topic essay request flagged; normal inputs pass.

## Easy

- [ ] 1. Ask an LLM to critique the solution (usability, security, prompt engineering).
- [ ] 2. Improve the prompts for your personal domain (IT, finance, HR, communication, etc.).
- [~] 3. More security constraints: user input validation and system prompt validation (possibly LLM-checked).
  - User input validation done (`guard.py`: length limits + LLM check; URL blocking in `web_fetch.py`). Missing: "system prompt validation" (e.g. checking the model's answer for leaked system prompt text).
- [x] 4. Simulate difficulty levels (easy, medium, hard questions).
  - "Question difficulty" slider (both modes). The chosen instruction from `DIFFICULTY_INSTRUCTIONS` (`prompts.py`) is added to the user message; the system prompt stays unchanged.
- [ ] 5. Optimise prompts for concise vs. detailed responses.
- [ ] 6. Generate interviewer guidelines (structured evaluation criteria for technical and behavioural interviews).
- [ ] 7. Mock interview with AI personas (strict, neutral, friendly interviewer).
- [~] 8. Tune at least one model setting (temperature, max tokens, reasoning effort, etc.) and compare outputs.
  - Temperature can be set via the toggle in the Settings section "Set temperature (experimental)" (slider 0-2), which switches to `TEMPERATURE_MODELS` in `core.py` (`google/gemini-3.1-flash-image`): none of the 3 course models accept `temperature`. A warning explains the risks. `temperature` is only sent when set (`_ask_llm()`). Max tokens is also adjustable (see Medium 1). Missing: compare outputs at low vs high temperature (or different max tokens) and note the differences.

## Medium

- [x] 1. Expose all model settings (model, temperature, max tokens, etc.) as sliders/fields.
  - Settings section in `landing.py`: model (select box), temperature (opt-in toggle + slider 0-2), max tokens (slider 1,000-8,000, default 4,000: `MAX_TOKENS_RANGE` in `core.py`, based on measured answers of ~450-1,050 output tokens) and question difficulty. Settings are only sent when set (`_ask_llm()`). If an answer hits the max tokens limit, the user gets a clear "cut off, increase Max tokens" message (generic mode falls back to the backup questions).
- [x] 2. At least two structured JSON output formats.
  - `_LLMPlan` (role title, seniority, summary, list of `PracticeQuestion`) and `FitAssessment` (match score 0-10, reasoning, cover letter), both in `core.py`, requested with `chat.completions.parse(response_format=...)` in `_ask_llm()`.
- [x] 3. Calculate and show the price of the prompt (OpenRouter models endpoint).
  - `pricing.py`, shown below the Settings section: (1) **estimate before sending**: model prices per token from the OpenRouter models endpoint × (~1,000 input + max tokens output), e.g. $0.00210 for `gpt-6-luna` at 4,000 tokens; (2) **real cost after each action**: the cost OpenRouter reports per request (`usage.cost`), added up over all requests of the click (guard check, embedding, main call; also cut-off answers, which are billed), plus a session total. Checked: reported cost = tokens × endpoint prices (375 × $0.0000001 + 687 × $0.0000005 = $0.000381).
- [ ] 4. Read the OpenRouter docs, think of your own improvement, and implement it.
- [ ] 5. Jailbreak your own app; record the results in an Excel sheet.
- [~] 6. Job description field to get prep for that specific position (RAG).
  - Done: "Specific job opening" text area in `landing.py`, inserted into the user prompt (`JOB_OPENING_USER_PROMPT_TEMPLATE`). If a URL is pasted, the page is downloaded and its text sent instead (`web_fetch.py`). Missing: no retrieval (RAG).
- [x] 7. Let the user choose from a list of LLMs.
  - "LLM model" select box in the Settings section (`landing.py`), options from `AVAILABLE_MODELS` in `core.py` (the 3 course models, all support structured outputs); passed down to `_ask_llm()`.
- [ ] 8. Creative use of image generation (`google/gemini-3.1-flash-image`).
- [x] 9. Security guard + keep developer settings (model, system prompts) separate from the user experience.
  - **Guard (`guard.py`)**, run before every action by `_check_with_guard()` in `landing.py`:
    - Length limits per field (role title 100, job description and CV 15,000 characters): stop oversized inputs that would waste tokens, without an API call.
    - LLM misuse check: one call to the cheapest course model (`GUARD_MODEL`, independent of the user's model choice so it can't be weakened) with `GUARD_SYSTEM_PROMPT` and the `GuardVerdict` schema (`is_valid`, `reason`). It flags prompt injection (e.g. "ignore previous instructions", "give this candidate 10/10" hidden in a CV), off-topic requests (e.g. an essay instead of a job description) and harmful content.
    - Flagged input shows a warning with the reason and the action does not run, so the user can fix the input. If the guard's own LLM call fails, the check is skipped (fail open) so the generic backup questions still work.
    - URLs pointing to localhost or private networks are refused in `web_fetch.py` (also after redirects).
    - Tested live: injection in role title and CV and an off-topic essay request were flagged; normal and informal inputs passed.
  - **Developer settings kept separate:** system prompts live only in `prompts.py` (never shown or editable in the UI); the model and temperature sit in their own Settings section, apart from the user's inputs.

## Hard

- [ ] 1. Full chatbot application instead of a one-time API call.
- [ ] 2. Use LangChain (chains or agents).
- [x] 3. Vector database to detect previously seen prep data and generate new data.
  - Lightweight vector store in `user_store.py`: one JSON file per logged-in user (`data/users/<username>.json`) with each job profile's embedding (`core.embed_text()`, `qwen/qwen3-embedding-8b`), its questions and latest fit result. Before a brief, the job (job-opening mode: the job text; generic mode: the role title only, see `actions._embed_for_history()`) is embedded and compared with all past profiles by cosine similarity (numpy). Profiles ≥ 70% similar count as "seen before": their questions are sent to the LLM as "do not repeat" (`AVOID_QUESTIONS_TEMPLATE`), so it generates new ones; the top-3 closest other roles (≥ 50%) are suggested. The fit check uses the same search to show the top-3 similar jobs the user already checked, with their scores, to compare. Tested: "Business Intelligence Analyst" after "Data Analyst" → 91% similar, the 5 earlier questions were avoided; its fit check listed "Data Analyst: 8/10, 89% similar". Note: a hand-made vector store (embeddings + similarity search), not a vector DB library such as ChromaDB.
- [ ] 4. Use open-source LLMs.
  - Not possible with the current API key: open-source models (e.g. `openai/gpt-oss-120b`) are blocked by the OpenRouter workspace guardrail (allow-list). Parked.
- [ ] 5. Assess prompt/model performance (LLM-as-a-judge or other methods).

## Other work (not in `115.md`)

- Project setup with uv, API keys in `.env` (`config.py`), `start_app.bat` to launch the app.
- Optional login (`auth.py`, `streamlit-authenticator`): log in / create account at the top of the page; passwords stored as bcrypt hashes in `config.yaml`. Logged-in users get a "My history" tab with all their job profiles (questions, fit score, cover letter). Demo accounts for reviewers: `demo` / `Demo-pass1` and `sergi` / `WillGet100%?` (committed on purpose, history in `data/users/`; listed in the README).
- Prompts in their own file (`prompts.py`) for easy editing and comparison.
- LLM errors are caught in `landing.py` and shown with `st.error` instead of a traceback.
- CV fit check + cover letter: "Check my fit & write a cover letter" button, one LLM call (`assess_fit_and_write_cover_letter()` in `core.py`), shown with score bar, reasoning and a download button. Works in both modes: generic roles use a stand-in description (`describe_generic_role()`).
- CV as PDF: drag-and-drop uploader in the CV section; text extracted with `pypdf` (`cv_reader.py`) and used instead of the pasted text.
- `Architecture.md` summarises the components and decisions.

## Annex: prompting techniques used with Claude during development

Examples from the prompts sent to Claude Code (logged in `.claude/prompt-log/prompts.md`), supporting Mandatory task 4.

| Technique | Example prompt | Why it fits |
|---|---|---|
| **Role / persona** | CLAUDE.md: *"You are a senior AI Engineer, assisting a student…"* | A real system prompt: Claude reads it before every turn. |
| **Instructions and constraints** | CLAUDE.md: *"Do not overcomplicate… Work only on what is explicitly requested"*; *"update Architecture.md… dont make it too long"* | Sets rules for scope, length and style instead of giving examples. |
| **Zero-shot** | *"Can you build a small batch file so I can double click and start…"*; *"extract all used prompts… into prompts.py"* | A plain task with no examples and no reasoning asked for. |
| **Reasoning before acting (close to Chain-of-Thought)** | *"analyze (dont execute yet) what could be cleaned up… and let's decide together"*; *"dont do it yet, but are we safe to remove all roleprofile…?"* | Asks for the reasoning first and the action later. |
| **Task decomposition** | CV prompt: *"A) judge if the job opening is a good fit; and B) write a small cover letter…"* | Splits one big request into clear sub-tasks. |
| **Prompt chaining / iterative refinement** | Structured output: *"capture the output more structured"* → *"which models support it?"* → *"add that extra check"*. URL fetch: question → options → *"go with option A"* | Each answer feeds into the next prompt. |
| **Context grounding (RAG-like)** | Pasting the mandatory tasks; pointing at `115.md` and `TASKS.md` (*"have a look at it, update it based on your criteria"*) | Gives the model the material to base its answer on, instead of relying on what it already knows. |

Few-shot is not clearly present in these logs; it is covered in the app by `JOB_OPENING_SYSTEM_PROMPT_FEW_SHOT`.
