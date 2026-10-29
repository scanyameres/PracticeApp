"""Local, deterministic interview-preparation content for the Streamlit prototype."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class PracticeQuestion:
    category: str
    prompt: str
    why_it_matters: str


@dataclass(frozen=True)
class PreparationPlan:
    role_title: str
    seniority: str
    role_summary: str
    focus_areas: tuple[str, ...]
    questions: tuple[PracticeQuestion, ...]


@dataclass(frozen=True)
class _RoleProfile:
    key: str
    match_terms: tuple[str, ...]
    summary: str
    focus_areas: tuple[str, ...]
    questions: tuple[PracticeQuestion, ...]


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

_SKILL_TERMS = (
    "Python", "SQL", "TypeScript", "Java", "AWS", "Azure", "Google Cloud",
    "APIs", "Kubernetes", "experimentation", "A/B testing", "analytics",
    "dashboards", "stakeholder management", "roadmap planning", "user research",
    "customer discovery", "SEO", "content strategy", "CRM", "leadership",
    "mentoring", "project management", "data visualization",
)


def _select_profile(role_text: str) -> _RoleProfile:
    normalized_role = role_text.casefold()
    for profile in _ROLE_PROFILES[:-1]:
        if any(term in normalized_role for term in profile.match_terms):
            return profile
    return _ROLE_PROFILES[-1]


def _matching_skills(text: str) -> tuple[str, ...]:
    normalized_text = text.casefold()
    return tuple(
        skill for skill in _SKILL_TERMS
        if re.search(rf"(?<!\w){re.escape(skill.casefold())}(?!\w)", normalized_text)
    )


def build_preparation_plan(
    role_title: str,
    job_description: str = "",
    seniority: str = "Mid-level",
) -> PreparationPlan:
    """Create a transparent role-based prep outline without external services."""
    title = role_title.strip() or "Your next role"
    profile = _select_profile(f"{title} {job_description}")
    matched_skills = _matching_skills(f"{title} {job_description}")
    focus_areas = tuple(dict.fromkeys((*matched_skills[:2], *profile.focus_areas)))[:5]

    questions = list(profile.questions)
    if matched_skills:
        skill = matched_skills[0]
        questions.insert(
            0,
            PracticeQuestion(
                "Role-specific",
                f"How have you used {skill} to solve a problem relevant to this role?",
                f"The role description mentions {skill}; prepare a specific example and its outcome.",
            ),
        )
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
        focus_areas=focus_areas,
        questions=tuple(questions[:7]),
    )
