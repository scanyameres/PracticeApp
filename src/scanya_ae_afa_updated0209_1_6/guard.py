"""Security guard: checks the user's inputs before any LLM feature runs.

Two layers, both run by check_inputs():
1. Length limits (plain Python, free): stop oversized inputs that would waste tokens/money.
2. LLM check (one cheap call to GUARD_MODEL): flags prompt injection, off-topic requests
   and harmful content, using structured output (GuardVerdict).

If something is flagged, the app shows the message as a warning and does not run the
feature, so the user can change the input and try again. Unsafe URLs (localhost, private
networks) are blocked separately in web_fetch.py, where the page is downloaded.

Public: check_inputs(), FAIR_REQUEST.
"""

from pydantic import BaseModel

from scanya_ae_afa_updated0209_1_6 import prompts
from scanya_ae_afa_updated0209_1_6.core import _ask_llm

# Cheapest course model: the check is simple, and the user's model choice should not weaken it.
GUARD_MODEL = "openai/gpt-6-luna"

# What check_inputs() returns when nothing is flagged. Callers compare against this constant.
FAIR_REQUEST = "Fair request"

# Maximum characters per input field.
MAX_LENGTHS = {
    "Role title": 100,
    "Job description": 15_000,
    "CV": 15_000,
}


class GuardVerdict(BaseModel):
    """LLM response schema: are the inputs genuine for interview prep, and why (not)."""

    is_valid: bool
    reason: str


def check_inputs(role_title: str = "", seniority: str = "", job_description: str = "", cv: str = "") -> str:
    """Check the inputs a feature is about to use. Pass only the fields that feature sends.

    Returns FAIR_REQUEST ("Fair request") if everything is fine, otherwise a message to show the user.
    If the guard's own LLM call fails (e.g. API down), the check is skipped ("fail open"),
    so the feature can still run and, in generic mode, fall back to the stored questions.
    """
    # Layer 1: length limits.
    fields = {"Role title": role_title, "Job description": job_description, "CV": cv}
    for name, text in fields.items():
        if len(text) > MAX_LENGTHS[name]:
            return f"{name} is too long ({len(text):,} characters, maximum {MAX_LENGTHS[name]:,}). Please shorten it."

    # Layer 2: LLM check of the meaning.
    user_prompt = prompts.GUARD_USER_PROMPT_TEMPLATE.format(
        role_title=role_title.strip() or "(not provided)",
        seniority=seniority or "(not provided)",
        job_description=job_description.strip() or "(not provided)",
        cv=cv.strip() or "(not provided)",
    )
    try:
        verdict = _ask_llm(prompts.GUARD_SYSTEM_PROMPT, user_prompt, GuardVerdict, GUARD_MODEL)
    except Exception as error:
        print(f"Guard check skipped, LLM call failed: {error}")
        return FAIR_REQUEST

    if not verdict.is_valid:
        return f"Your input was flagged by the safety check: {verdict.reason} Please change it and try again."
    return FAIR_REQUEST
