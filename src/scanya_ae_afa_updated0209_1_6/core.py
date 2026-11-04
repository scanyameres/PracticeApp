"""Local, deterministic interview-preparation content for the Streamlit prototype.

Builds a PreparationPlan from a role title (and optional job description) using fixed
role profiles and keyword matching. No Streamlit code and no external services, so it can
be unit tested on its own (see tests/test_prep.py).

Public entry point: build_preparation_plan().
"""

from dataclasses import dataclass
import re
from scanya_ae_afa_updated0209_1_6.config import get_client


@dataclass(frozen=True)
class PracticeQuestion:
    """One interview question, with its category and why it is worth preparing."""

    category: str
    prompt: str
    why_it_matters: str


@dataclass(frozen=True)
class PreparationPlan:
    """The prep brief shown in the app: role summary, focus areas and practice questions."""

    role_title: str
    seniority: str
    role_summary: str
    questions: tuple[PracticeQuestion, ...]


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
    """Create a transparent role-based prep outline without external services.

    Picks a role profile, puts up to two detected skills first in the focus areas, adds a
    skill question (if any) plus two general questions, and keeps at most 7 questions.
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
) -> PreparationPlan:
    """Create a transparent role-based prep outline without external services.

    Picks a role profile, puts up to two detected skills first in the focus areas, adds a
    skill question (if any) plus two general questions, and keeps at most 7 questions.
    """

    client = get_client("OpenRouter")
    APP_MODEL = "openai/gpt-6-luna"
    #system_prompt = ("You are an expert at analyzing job descriptions and extracting relevant information for interview preparation. Your task is to read the provided job description and generate a concise summary of the role, including the role title, seniority level, key responsibilities, and any specific skills or qualifications mentioned. Additionally, identify up to 5 potential interview questions that a candidate might be asked based on the job description. Format your response in JSON with the following structure:\n\n{\n  \"role_title\": \"\",\n  \"seniority\": \"\",\n  \"role_summary\": \"\",\n  \"questions\": [\"\", \"\", \"\", \"\", \"\"]\n}\n\nEnsure that the JSON is valid and properly formatted.")
    system_prompt = "Open this job description, read about the job description, and extract the role title. Then prepare 5 questions"
    user_prompt = f"Job description: {job_description}"
    #JUDGE_MODEL = "openai/gpt-5.4-mini"

    # Verify the application-model connection
    response = client.chat.completions.create(
        model=APP_MODEL,
        messages=[{"role": "user", "content": "Say 'connection OK' in exactly two words."}],
    )
    print("API check:", response.choices[0].message.content)
  
    response = client.chat.completions.create(
        model=APP_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    llm_questions = response.choices[0].message.content
    return PreparationPlan(
        role_title="Placeholder role",
        seniority="Placeholder exp",
        role_summary="Placeholder summary",
        questions=llm_questions
    )
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
