# Tasks Tracker

Mandatory and optional tasks from `115.md`. Bonus points need **at least 2 Medium and 1 Hard** optional tasks.

Legend: `[x]` done · `[~]` partially done · `[ ]` not started

**Bonus progress:** Medium 2 done (2 partial) · Hard 0 done.

## Mandatory

- [x] 1. Research the nature of interview preparation you want to do.
  - Chosen: prep brief with practice questions, from a generic role + seniority (stored role profiles, `_ROLE_PROFILES` in `core.py`) or from a specific job description (LLM, `build_preparation_plan_opening()` in `core.py`).
- [x] 2. Decide how to build the front-end (Streamlit components or Next.js).
  - Streamlit (`landing.py`): input dashboard on the main page (CV + role/job side by side, difficulty slider), sidebar Settings for the model, one button per action, results in tabs (incl. a "Practice an answer" placeholder), one expander per question, spinner while the LLM runs, `st.error` if the call fails.
- [x] 3. Choose an OpenRouter model (`openai/gpt-6-luna`, `anthropic/claude-sonnet-5.5` or `openai/gpt-6.1-sol`; embeddings: `qwen/qwen3-embedding-8b`, `openai/text-embedding-3-small/large`).
  - Default `openai/gpt-6-luna` (`DEFAULT_MODEL` in `core.py`); the user can switch to the other two (see Medium 7). All three support structured outputs and are called through the OpenAI SDK pointed at OpenRouter (`config.get_client()`).
- [~] 4. Write at least 5 system prompts with different techniques (few-shot, Chain-of-Thought, zero-shot, etc.) and compare which works best.
  - Done: 5 system prompts for the job-opening task in `prompts.py`: `JOB_OPENING_SYSTEM_PROMPT` (zero-shot, used by the app) and the alternatives `_FEW_SHOT`, `_CHAIN_OF_THOUGHT`, `_ROLE`, `_CONSTRAINED`. Also `FIT_SYSTEM_PROMPT` (role + constraints). Techniques used with Claude during development: see Annex. Missing: try the alternatives in the app and note which works best.
- [ ] 5. Add at least one security guard to prevent misuse.
  - Only empty-input checks in `landing.py` so far; that is validation, not a guard against misuse.

## Easy

- [ ] 1. Ask an LLM to critique the solution (usability, security, prompt engineering).
- [ ] 2. Improve the prompts for your personal domain (IT, finance, HR, communication, etc.).
- [ ] 3. More security constraints: user input validation and system prompt validation (possibly LLM-checked).
- [x] 4. Simulate difficulty levels (easy, medium, hard questions).
  - "Question difficulty" slider (job-opening mode). The chosen instruction from `DIFFICULTY_INSTRUCTIONS` (`prompts.py`) is added to the user message; the system prompt stays unchanged.
- [ ] 5. Optimise prompts for concise vs. detailed responses.
- [ ] 6. Generate interviewer guidelines (structured evaluation criteria for technical and behavioural interviews).
- [ ] 7. Mock interview with AI personas (strict, neutral, friendly interviewer).
- [~] 8. Tune at least one model setting (temperature, max tokens, reasoning effort, etc.) and compare outputs.
  - Temperature can be set via the sidebar toggle "Set temperature (experimental)" (slider 0-2), which switches to `TEMPERATURE_MODELS` in `core.py` (`google/gemini-3.1-flash-image`): none of the 3 course models accept `temperature`. A warning explains the risks. `temperature` is only sent when set (`_ask_llm()`). Missing: compare outputs at low vs high temperature and note the differences.

## Medium

- [ ] 1. Expose all model settings (model, temperature, max tokens, etc.) as sliders/fields.
- [x] 2. At least two structured JSON output formats.
  - `_LLMPlan` (role title, seniority, summary, list of `PracticeQuestion`) and `FitAssessment` (match score 0-10, reasoning, cover letter), both in `core.py`, requested with `chat.completions.parse(response_format=...)` in `_ask_llm()`.
- [ ] 3. Calculate and show the price of the prompt (OpenRouter models endpoint).
- [~] 4. Read the OpenRouter docs, think of your own improvement, and implement it.
  - Uses `provider.require_parameters` (`extra_body` in the `.parse()` call) so only providers supporting structured outputs are used. Probably too small to count on its own.
- [ ] 5. Jailbreak your own app; record the results in an Excel sheet.
- [~] 6. Job description field to get prep for that specific position (RAG).
  - Done: "Specific job opening" text area in `landing.py`, inserted into the user prompt (`JOB_OPENING_USER_PROMPT_TEMPLATE`). If a URL is pasted, the page is downloaded and its text sent instead (`web_fetch.py`). Missing: no retrieval (RAG).
- [x] 7. Let the user choose from a list of LLMs.
  - "LLM model" select box in the sidebar Settings (`landing.py`), options from `AVAILABLE_MODELS` in `core.py` (the 3 course models, all support structured outputs); passed down to `_ask_llm()`.
- [ ] 8. Creative use of image generation (`google/gemini-3.1-flash-image`).
- [ ] 9. Security guard + keep developer settings (model, system prompts) separate from the user experience.
  - Prompts are separated from the UI (`prompts.py`) and the model choice sits in a separate sidebar Settings panel, but there is no guard yet.

## Hard

- [ ] 1. Full chatbot application instead of a one-time API call.
- [ ] 2. Use LangChain (chains or agents).
- [ ] 3. Vector database to detect previously seen prep data and generate new data.
- [ ] 4. Use open-source LLMs.
  - Not possible with the current API key: open-source models (e.g. `openai/gpt-oss-120b`) are blocked by the OpenRouter workspace guardrail (allow-list). Parked.
- [ ] 5. Assess prompt/model performance (LLM-as-a-judge or other methods).

## Other work (not in `115.md`)

- Project setup with uv, API keys in `.env` (`config.py`), `start_app.bat` to launch the app.
- Prompts in their own file (`prompts.py`) for easy editing and comparison.
- LLM errors are caught in `landing.py` and shown with `st.error` instead of a traceback.
- CV fit check + cover letter: "Check my fit & write a cover letter" button, one LLM call (`assess_fit_and_write_cover_letter()` in `core.py`), shown with score bar, reasoning and a download button.
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
