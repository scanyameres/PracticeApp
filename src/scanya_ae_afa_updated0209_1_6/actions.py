"""The logic behind the two buttons, connecting core.py (LLM features) with user_store.py (history).

- suggest_questions(): "Suggest interview questions"
- check_fit(): "Check my fit & write a cover letter"

Both work in one of two modes, chosen by the inputs:
- generic mode: role_title + seniority given, job_description empty;
- job-opening mode: job_description given (pasted text or a URL).

For a logged-in user (username given), they also use the history: embed the job, compare it
with the user's past job profiles, use what is similar, and save the new result. Without a
username they only call the LLM.

No Streamlit code here: landing.py validates the inputs, runs the guard, calls these functions
and shows the results. That keeps this flow testable with a plain Python script.
"""

from dataclasses import dataclass

from scanya_ae_afa_updated0209_1_6 import core, user_store


@dataclass(frozen=True)
class QuestionsResult:
    """Everything the "Potential questions" tab shows after suggest_questions()."""

    plan: core.PreparationPlan
    # How many earlier questions (from similar jobs in the history) the LLM was told to avoid.
    avoided_questions: int
    # Up to 3 most similar other job profiles from the history, with their similarity (0-1).
    closest_roles: list[tuple[dict, float]]


@dataclass(frozen=True)
class FitResult:
    """Everything the "Fit check & cover letter" tab shows after check_fit()."""

    fit: core.FitAssessment
    # Up to 3 similar jobs from the history that have a fit check, with their similarity (0-1).
    similar_fits: list[tuple[dict, float]]


def suggest_questions(
    username: str | None,
    role_title: str,
    seniority: str,
    job_description: str,
    difficulty: str,
    model: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> QuestionsResult:
    """Generate interview questions; for a logged-in user, avoid repeats and suggest similar roles.

    Logged in: the job is embedded and compared with the user's past job profiles; questions of
    profiles >= 70% similar are passed to the LLM as "do not repeat", and the result is saved.
    In generic mode a failed LLM call returns the stored backup questions (plan.fallback_reason),
    which are not saved to the history.

    Raises:
        ValueError, openai.OpenAIError: job-opening mode only (unreadable URL, API problems,
            cut-off or refused answer). Generic mode falls back instead of raising.
    """
    generic = _is_generic(job_description)
    history_key = _history_key(role_title, seniority, job_description)

    job_text, embedding, similar, avoid = job_description, None, [], []
    if username:
        job_text = _job_text(role_title, seniority, job_description)  # a URL is downloaded once
        embedding = _embed_for_history(username, role_title, job_text, generic)
        if embedding:
            similar = user_store.find_similar(username, embedding)
            avoid = user_store.questions_to_avoid(similar)

    if generic:
        plan = core.build_preparation_plan_generic(
            role_title, seniority, difficulty, model, temperature, avoid, max_tokens=max_tokens
        )
    else:
        # job_text is the downloaded page if logged in, else the raw input (core then downloads a URL).
        plan = core.build_preparation_plan_opening(
            job_text, difficulty, model, temperature, avoid, max_tokens=max_tokens
        )

    # Only real LLM results go into the history, not the backup questions.
    if embedding and not plan.fallback_reason:
        user_store.save_brief(username, history_key, embedding, plan)
    return QuestionsResult(plan, len(avoid), user_store.closest_other_profiles(similar, history_key))


def check_fit(
    username: str | None,
    cv: str,
    role_title: str,
    seniority: str,
    job_description: str,
    model: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> FitResult:
    """Score the CV against the job and write a cover letter; for a logged-in user, compare and save.

    Logged in: after the LLM call, the job is embedded, earlier fit checks for similar jobs are
    looked up (to compare scores; searched before saving, so the job never matches itself), and
    the new result is saved.

    Raises:
        ValueError, openai.OpenAIError: unreadable URL, API problems, cut-off or refused answer.
    """
    generic = _is_generic(job_description)
    history_key = _history_key(role_title, seniority, job_description)

    # Generic mode has no posting, so a short description of the role stands in for it.
    job_text = _job_text(role_title, seniority, job_description)
    fit = core.assess_fit_and_write_cover_letter(cv, job_text, model, temperature, max_tokens=max_tokens)

    similar_fits = []
    embedding = _embed_for_history(username, role_title, job_text, generic)
    if embedding:
        similar = user_store.find_similar(username, embedding)
        similar_fits = user_store.closest_other_profiles(similar, history_key, only_with_fit=True)
        # A new profile from a fit check is named after the role, or the start of the job text.
        label = history_key if generic else job_description.strip()[:60]
        user_store.save_fit(username, history_key, embedding, fit, label)
    return FitResult(fit, similar_fits)


def _is_generic(job_description: str) -> bool:
    """Generic mode (role title + level) when no job description or URL is given."""
    return not job_description.strip()


def _history_key(role_title: str, seniority: str, job_description: str) -> str:
    """What identifies the job profile in the user's history: role + level, or the job input."""
    if _is_generic(job_description):
        return f"{role_title.strip()} · {seniority}"
    return job_description


def _job_text(role_title: str, seniority: str, job_description: str) -> str:
    """The job text for the LLM: the pasted description, the downloaded page for a URL, or
    (generic mode) a short stand-in description of the role."""
    if _is_generic(job_description):
        return core.describe_generic_role(role_title, seniority)
    return core.resolve_job_text(job_description)


def _embed_for_history(username: str | None, role_title: str, job_text: str, generic: bool) -> list[float] | None:
    """Embedding of the job for the user's history; None if not logged in or the call fails.

    Job-opening mode embeds the job text. Generic mode embeds only the role title: the fixed
    template text of the stand-in description, and even a shared level word like "Mid-level",
    would make unrelated roles look similar. Measured (Data Analyst vs Nurse): 0.73 with the
    template, 0.66 with "Mid-level", 0.46 with the role title only; similar roles stay at
    0.77-0.88, so the 0.7 threshold in user_store.py separates them clearly.
    History is a bonus: if the embedding call fails, the feature still runs, just without it.
    """
    if not username:
        return None
    text = role_title.strip() if generic else job_text
    try:
        return core.embed_text(text)
    except Exception as error:
        print(f"Embedding failed, history skipped: {error}")
        return None
