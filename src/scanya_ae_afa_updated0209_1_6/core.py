"""Interview-preparation logic for the app (no Streamlit code).

Builds a PreparationPlan in one of two ways:
- build_preparation_plan_generic(): from a role title and seniority, using fixed role
  profiles and keyword matching. Local and deterministic, no API calls.
- build_preparation_plan_opening(): from a job description or URL, using the LLM via
  OpenRouter with structured output (prompts live in prompts.py).

And, separately:
- assess_fit_and_write_cover_letter(): from the user's CV and a job opening, one LLM call
  returns a FitAssessment (match score, reasoning, cover letter).
"""

from dataclasses import dataclass
import re

from pydantic import BaseModel, Field

from scanya_ae_afa_updated0209_1_6 import prompts, web_fetch
from scanya_ae_afa_updated0209_1_6.config import get_client

# OpenRouter models the user can choose from (all support structured outputs).
# The first one is the default.
AVAILABLE_MODELS = (
    "openai/gpt-6-luna",
    "anthropic/claude-sonnet-5.5",
    "openai/gpt-6.1-sol",
)
DEFAULT_MODEL = AVAILABLE_MODELS[0]

# Models that also accept a `temperature` setting (the models above are reasoning models and
# do not). Must be on the API key's allow-list (OpenRouter guardrail) and support structured
# outputs. Offered only when the user opts in to setting the temperature.
TEMPERATURE_MODELS = (
    "google/gemini-3.1-flash-image",
)


@dataclass(frozen=True)
class PracticeQuestion:
    """One interview question, with its category and why it is worth preparing."""

    category: str
    prompt: str
    why_it_matters: str


@dataclass(frozen=True)
class PreparationPlan:
    """The prep brief shown in the app: role title, seniority, summary and practice questions."""

    role_title: str
    seniority: str
    role_summary: str
    questions: tuple[PracticeQuestion, ...]


class _LLMPlan(BaseModel):
    """Response schema for the LLM: the PreparationPlan fields, with questions as a list.

    Passed as `response_format` to the API, so the model must answer with JSON matching
    this schema and the SDK parses it straight into this object (questions become
    PracticeQuestion instances).
    """

    role_title: str
    seniority: str
    role_summary: str
    questions: list[PracticeQuestion]


class FitAssessment(BaseModel):
    """How well the user's CV matches a job opening, plus a tailored cover letter.

    Used both as the LLM response schema and as the result shown in the app.
    """

    match_score: int = Field(ge=0, le=10, description="0 = no match, 10 = perfect match")
    reasoning: str
    cover_letter: str


@dataclass(frozen=True)
class _RoleProfile:
    """Internal template for one role family; chosen when any match_terms appear in the input."""

    key: str
    match_terms: tuple[str, ...]
    summary: str
    focus_areas: tuple[str, ...]
    questions: tuple[PracticeQuestion, ...]


# Fixed role templates. Order matters: the first profile whose match_terms appear wins,
# and the last one ("General") is the fallback.
_ROLE_PROFILES = (
    _RoleProfile(
        key="Software engineering",
        match_terms=("software", "engineer", "developer", "backend", "front end", "frontend"),
        summary="Explore how you design, build, and improve reliable software with a team.",
        focus_areas=("Technical problem-solving", "System design", "Code quality", "Collaboration"),
        questions=(
            PracticeQuestion(
                "Technical", "How do you break an ambiguous engineering problem into a practical plan?",
                "Shows how you reason, make trade-offs, and move from uncertainty to delivery.",
            ),
            PracticeQuestion(
                "Technical", "Tell me about a technical decision you would make differently today.",
                "Reveals technical judgment, reflection, and how you learn from outcomes.",
            ),
            PracticeQuestion(
                "Technical", "How do you balance delivery speed with maintainability and reliability?",
                "Connects engineering choices to the needs of the product and team.",
            ),
            PracticeQuestion(
                "Collaboration", "Describe a time you worked through a disagreement about an implementation.",
                "Highlights communication and constructive technical collaboration.",
            ),
        ),
    ),
    _RoleProfile(
        key="Product management",
        match_terms=("product manager", "product management", "product lead"),
        summary="Prepare to connect customer needs, product strategy, and measurable outcomes.",
        focus_areas=("Product strategy", "Prioritization", "Customer insight", "Stakeholder alignment"),
        questions=(
            PracticeQuestion(
                "Product sense", "How would you decide which customer problem to solve next?",
                "Shows how you combine customer evidence, strategy, and opportunity size.",
            ),
            PracticeQuestion(
                "Prioritization", "Tell me about a time you had to say no to a valuable request.",
                "Tests how you explain trade-offs and align stakeholders around a decision.",
            ),
            PracticeQuestion(
                "Execution", "How do you know whether a product launch has been successful?",
                "Reveals how you define outcomes and learn from product performance.",
            ),
            PracticeQuestion(
                "Collaboration", "Describe a difficult product decision you made with incomplete information.",
                "Highlights decision-making, influence, and comfort with uncertainty.",
            ),
        ),
    ),
    _RoleProfile(
        key="Data analysis",
        match_terms=("data analyst", "data analytics", "business intelligence", "analytics"),
        summary="Focus on turning trustworthy analysis into clear, useful decisions.",
        focus_areas=("Analytical thinking", "Data quality", "Communication", "Business impact"),
        questions=(
            PracticeQuestion(
                "Analysis", "Walk me through how you would investigate an unexpected change in a key metric.",
                "Shows whether you validate the signal before explaining the cause.",
            ),
            PracticeQuestion(
                "Data quality", "Tell me about a time the data did not match what you expected.",
                "Reveals your approach to data validation and responsible conclusions.",
            ),
            PracticeQuestion(
                "Communication", "How have you made a complex analysis useful to a non-technical audience?",
                "Tests whether your findings lead to shared understanding and action.",
            ),
            PracticeQuestion(
                "Impact", "Describe an analysis that changed a business decision.",
                "Connects your technical work to a concrete outcome.",
            ),
        ),
    ),
    _RoleProfile(
        key="Marketing",
        match_terms=("marketing", "growth", "brand", "communications"),
        summary="Prepare to discuss audience insight, campaign choices, and measurable growth.",
        focus_areas=("Audience insight", "Campaign strategy", "Experimentation", "Measurement"),
        questions=(
            PracticeQuestion(
                "Strategy", "How would you build a marketing plan for a new audience?",
                "Shows how you connect audience research, positioning, channels, and goals.",
            ),
            PracticeQuestion(
                "Experimentation", "Tell me about a campaign experiment that changed your approach.",
                "Reveals how you learn from tests rather than relying on assumptions.",
            ),
            PracticeQuestion(
                "Measurement", "Which metrics would you use to evaluate a campaign and why?",
                "Tests your ability to connect measurement to the actual objective.",
            ),
            PracticeQuestion(
                "Collaboration", "Describe a time you aligned creative and commercial priorities.",
                "Highlights communication and sound judgment across teams.",
            ),
        ),
    ),
    _RoleProfile(
        key="Customer success",
        match_terms=("customer success", "account manager", "customer experience"),
        summary="Explore how you build customer trust, solve problems, and support lasting value.",
        focus_areas=("Customer relationships", "Problem-solving", "Retention", "Communication"),
        questions=(
            PracticeQuestion(
                "Customer focus", "Tell me about a time you turned around a difficult customer relationship.",
                "Shows empathy, ownership, and how you rebuild trust.",
            ),
            PracticeQuestion(
                "Problem-solving", "How do you respond when a customer is at risk of leaving?",
                "Tests how you diagnose the issue and coordinate a useful response.",
            ),
            PracticeQuestion(
                "Prioritization", "How do you balance urgent customer needs across multiple accounts?",
                "Reveals how you manage commitments while communicating clearly.",
            ),
            PracticeQuestion(
                "Impact", "How have you helped a customer get more value from a product or service?",
                "Connects your work to customer outcomes and long-term relationships.",
            ),
        ),
    ),
    _RoleProfile(
        key="General",
        match_terms=(),
        summary="Build clear examples around role expertise, problem-solving, and collaboration.",
        focus_areas=("Role expertise", "Problem-solving", "Communication", "Collaboration"),
        questions=(
            PracticeQuestion(
                "Problem-solving", "Tell me about a challenging problem you solved at work.",
                "A strong example makes your reasoning and contribution easy to follow.",
            ),
            PracticeQuestion(
                "Ownership", "Describe a piece of work you are proud of and the impact it had.",
                "Helps the interviewer understand your role and the outcome you created.",
            ),
            PracticeQuestion(
                "Adaptability", "Tell me about a time you had to adapt your approach.",
                "Shows how you respond when the original plan no longer fits.",
            ),
            PracticeQuestion(
                "Collaboration", "How do you handle competing priorities with other people?",
                "Highlights communication, judgment, and how you reach alignment.",
            ),
        ),
    ),
)


def _select_profile(role_text: str) -> _RoleProfile:
    """Return the first profile whose match terms appear in the text, else the General one."""
    normalized_role = role_text.casefold()
    for profile in _ROLE_PROFILES[:-1]:
        if any(term in normalized_role for term in profile.match_terms):
            return profile
    return _ROLE_PROFILES[-1]


def build_preparation_plan_generic(
    role_title: str,
    seniority: str = "Mid-level",
) -> PreparationPlan:
    """Build a generic prep plan from a role title, without calling the LLM.

    Picks the matching role profile (or the General one) and returns its summary and
    questions, plus a behavioral and a motivation question.
    """
    title = role_title.strip() or "Your next role"
    profile = _select_profile(f"{title}")

    questions = list(profile.questions)
    questions.extend(
        (
            PracticeQuestion(
                "Behavioral", "Tell me about a time you received feedback and what you did with it.",
                "Shows self-awareness and how you turn feedback into action.",
            ),
            PracticeQuestion(
                "Motivation", f"Why does this {seniority.lower()} {title} role interest you?",
                "Connects your experience and interests to the opportunity.",
            ),
        )
    )
    return PreparationPlan(
        role_title=title,
        seniority=seniority,
        role_summary=profile.summary,
        questions=tuple(questions[:7]),
    )

def build_preparation_plan_opening(
    job_description: str = "",
    difficulty: str = "Medium",
    model: str = DEFAULT_MODEL,
    temperature: float | None = None,
) -> PreparationPlan:
    """Build a personalized prep plan from a job description or URL using the LLM.

    Sends the description to the model with the _LLMPlan schema as structured output, so
    role title, seniority, summary and questions come back already parsed.

    If the input is a URL, the page is downloaded first (web_fetch.py) and its text is sent.
    `difficulty` is a key of prompts.DIFFICULTY_INSTRUCTIONS ("Easy", "Medium", "Hard"); its
    instruction is added to the user message, so the system prompt stays the same.
    `temperature` is only sent if given (use with TEMPERATURE_MODELS, see _ask_llm).

    Raises:
        ValueError: if the URL cannot be read, or the model refuses or returns no usable plan.
        openai.OpenAIError: on API problems (network, invalid key, no provider, ...).
    """

    user_prompt = prompts.JOB_OPENING_USER_PROMPT_TEMPLATE.format(
        job_description=_job_text(job_description),
        difficulty_instruction=prompts.DIFFICULTY_INSTRUCTIONS[difficulty],
    )
    llm_plan = _ask_llm(prompts.JOB_OPENING_SYSTEM_PROMPT, user_prompt, _LLMPlan, model, temperature)

    return PreparationPlan(
        role_title=llm_plan.role_title,
        seniority=llm_plan.seniority,
        role_summary=llm_plan.role_summary,
        questions=tuple(llm_plan.questions),
    )


def assess_fit_and_write_cover_letter(
    cv: str,
    job_description: str,
    model: str = DEFAULT_MODEL,
    temperature: float | None = None,
) -> FitAssessment:
    """Compare the user's CV with a job opening and write a cover letter, in one LLM call.

    The job input can be a description or a URL (fetched like in build_preparation_plan_opening).
    Returns a FitAssessment with a 0-10 match score, the reasoning and the cover letter.

    Raises:
        ValueError: if the URL cannot be read, or the model refuses or returns nothing usable.
        openai.OpenAIError: on API problems (network, invalid key, no provider, ...).
    """
    user_prompt = prompts.FIT_USER_PROMPT_TEMPLATE.format(
        cv=cv, job_description=_job_text(job_description)
    )
    return _ask_llm(prompts.FIT_SYSTEM_PROMPT, user_prompt, FitAssessment, model, temperature)


def _job_text(job_input: str) -> str:
    """Return the job description text; if the input is a URL, download the page first.

    The LLM cannot open links, so the app fetches the page itself (see web_fetch.py).
    """
    if web_fetch.is_url(job_input):
        return web_fetch.fetch_job_description(job_input)
    return job_input


def _ask_llm[T: BaseModel](
    system_prompt: str,
    user_prompt: str,
    schema: type[T],
    model: str = DEFAULT_MODEL,
    temperature: float | None = None,
) -> T:
    """Send one system + user message to `model` and return the answer parsed into `schema`.

    Shared by all LLM features. Uses structured output: .parse() sends `schema` as a JSON
    schema and returns the validated object in .parsed (instead of free text in .content).

    `temperature` is only sent when given: models that do not support it (AVAILABLE_MODELS)
    would otherwise fail, because require_parameters only accepts providers supporting it.
    """
    # Optional settings: only include the ones the user actually set.
    settings = {} if temperature is None else {"temperature": temperature}

    client = get_client("OpenRouter")

    # Verify the application-model connection
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompts.CONNECTION_CHECK_PROMPT}],
    )
    print("API check:", response.choices[0].message.content)

    response = client.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=schema,
        **settings,
        # OpenRouter-specific: only route to providers that support every parameter we
        # send (structured outputs, temperature), instead of silently ignoring them.
        extra_body={"provider": {"require_parameters": True}},
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:  # The model refused or returned nothing usable.
        raise ValueError(f"LLM did not return a usable answer: {response.choices[0].message.refusal}")
    return parsed
    # questions.extend(
    #     (
    #         PracticeQuestion(
    #             "Behavioral", "Tell me about a time you received feedback and what you did with it.",
    #             "Shows self-awareness and how you turn feedback into action.",
    #         ),
    #         PracticeQuestion(
    #             "Motivation", f"Why does this {seniority.lower()} {title} role interest you?",
    #             "Connects your experience and interests to the opportunity.",
    #         ),
    #     )
    # )
    # return PreparationPlan(
    #     role_title=title,
    #     seniority=seniority,
    #     role_summary=profile.summary,
    #     questions=tuple(questions[:7]),
    # )
