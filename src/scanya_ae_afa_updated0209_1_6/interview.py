"""Practice interview: a chat with an LLM hiring manager about the questions of a brief.

Flow (landing.py draws the chat; no Streamlit code here):
1. start_interview(): builds an InterviewState with the opening message and question 1.
   No LLM call: the greeting and the main questions are written by the app.
2. reply(): for each candidate answer, the LLM (as hiring manager) returns an InterviewerTurn:
   a short message and `next_step` ("follow_up" or "next_question").
3. final_feedback(): after the last question, a separate LLM call scores the transcript
   (InterviewFeedback: answer quality and job fit, per question and overall).
   actions.finish_interview() calls it and saves the result for logged-in users.

Also: end_early() stops before the last question (the feedback then covers only
answered_questions()), and export_markdown() gives the transcript + feedback for the
download button and the history.

The LLM decides *whether* an answer needs a follow-up; the app keeps control of the flow:
it counts the answers per question, forces the move to the next question after
MAX_ANSWERS_PER_QUESTION answers, shows each main question itself and ends the interview
after the last one. So the interview always ends after at most
MAX_ANSWERS_PER_QUESTION x (number of questions) answers.
"""

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

from scanya_ae_afa_updated0209_1_6 import core, prompts

# Answers allowed per main question (the first answer + up to 3 follow-ups).
MAX_ANSWERS_PER_QUESTION = 4
# Longest answer accepted (characters): keeps requests small and limits prompt-injection room.
MAX_ANSWER_LENGTH = 3_000
# Default number of main questions (the user can choose fewer or more in the UI).
DEFAULT_QUESTION_COUNT = 5


class InterviewerTurn(BaseModel):
    """Response schema for one interviewer turn (structured output)."""

    message: str = Field(description="What the interviewer says to the candidate")
    next_step: Literal["follow_up", "next_question"]


class QuestionFeedback(BaseModel):
    """Feedback for one main question."""

    question: str
    answer_score: int = Field(ge=1, le=5, description="Quality of the answer, 1-5")
    fit_score: int = Field(ge=1, le=5, description="Evidence of what this job needs, 1-5")
    strengths: str
    improvements: str


class InterviewFeedback(BaseModel):
    """Response schema for the final feedback, also shown as is in the app."""

    overall_answer_score: int = Field(ge=1, le=5)
    overall_fit_score: int = Field(ge=1, le=5)
    summary: str
    per_question: list[QuestionFeedback]


@dataclass
class InterviewState:
    """Everything about one practice interview; kept in st.session_state by landing.py."""

    role_title: str
    seniority: str
    job_text: str  # job description (or a stand-in for a generic role)
    cv: str  # "" if the user gave no CV
    questions: list[str]  # the main questions, in order
    # The chat so far: {"role": "assistant" | "user", "content": str}. Shown in the UI and
    # sent to the LLM on every turn.
    messages: list[dict[str, str]] = field(default_factory=list)
    question_index: int = 0  # current main question (0-based)
    answers_on_question: int = 0  # candidate answers to the current main question so far
    finished: bool = False  # True after the last main question (or end_early()): time for the feedback
    ended_early: bool = False  # True if the user ended the interview before the last question
    feedback: InterviewFeedback | None = None


def start_interview(
    plan: core.PreparationPlan,
    job_text: str | None,
    cv: str = "",
    question_count: int = DEFAULT_QUESTION_COUNT,
) -> InterviewState:
    """Start an interview on the first `question_count` questions of the brief.

    `job_text`: the job description used for the brief, or None in generic mode (then a
    short stand-in description of the role is used). No LLM call.
    """
    questions = [question.prompt for question in plan.questions[:question_count]]
    if not questions:
        raise ValueError("The brief has no questions to practise.")
    state = InterviewState(
        role_title=plan.role_title,
        seniority=plan.seniority,
        job_text=job_text or prompts.GENERIC_ROLE_INTERVIEW_JOB_TEMPLATE.format(
            seniority=plan.seniority, role_title=plan.role_title
        ),
        cv=cv.strip(),
        questions=questions,
    )
    greeting = (
        f"Hello, and thanks for joining. I'm the hiring manager for this "
        f"{_role_label(state)} role. We'll go through {len(questions)} "
        "questions; answer as you would in a real interview, and I may ask you to go deeper."
    )
    state.messages.append({"role": "assistant", "content": f"{greeting}\n\n{_question_text(state, 0)}"})
    return state


def reply(
    state: InterviewState,
    answer: str,
    model: str = core.DEFAULT_MODEL,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> None:
    """Add the candidate's answer and the interviewer's reply to `state` (one LLM call).

    The state only changes if the call succeeds, so after an error the user can resend.

    Raises:
        ValueError: empty or too long answer, interview already finished, or LLM problems
            (cut-off or refused answer).
        openai.OpenAIError: on API problems (network, invalid key, ...).
    """
    answer = answer.strip()
    if state.finished:
        raise ValueError("The interview is over. Start a new one to practise again.")
    if not answer:
        raise ValueError("Write an answer first.")
    if len(answer) > MAX_ANSWER_LENGTH:
        raise ValueError(
            f"Your answer is too long ({len(answer):,} characters, maximum {MAX_ANSWER_LENGTH:,}). "
            "Keep it shorter, as you would in a real interview."
        )

    answers = state.answers_on_question + 1
    must_move_on = answers >= MAX_ANSWERS_PER_QUESTION
    is_last_question = state.question_index == len(state.questions) - 1
    conversation = state.messages + [{"role": "user", "content": answer}]

    turn = core._ask_llm_messages(
        _llm_messages(state, conversation, answers, must_move_on, is_last_question),
        InterviewerTurn, model, temperature, max_tokens,
    )

    # The app decides: the LLM's choice, unless the answer limit is reached.
    move_on = must_move_on or turn.next_step == "next_question"
    message = turn.message.strip()
    if move_on and turn.next_step == "follow_up":
        # Forced to move on, but the LLM asked a follow-up anyway: don't show it.
        message = "Thank you, that's all my questions." if is_last_question else "Thank you, let's move on."

    # Apply the changes only now that the call has succeeded.
    state.messages = conversation
    if not move_on:
        state.answers_on_question = answers
    elif is_last_question:
        state.finished = True
    else:
        state.question_index += 1
        state.answers_on_question = 0
        message = f"{message}\n\n{_question_text(state, state.question_index)}"
    state.messages.append({"role": "assistant", "content": message})


def final_feedback(
    state: InterviewState,
    model: str = core.DEFAULT_MODEL,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> InterviewFeedback:
    """Score the finished interview (one LLM call) and store the result in `state.feedback`.

    Only the answered questions are scored (all of them, unless the interview was ended early).

    Raises:
        ValueError, openai.OpenAIError: like reply().
    """
    user_prompt = prompts.INTERVIEW_FEEDBACK_USER_PROMPT_TEMPLATE.format(
        job_text=state.job_text,
        cv=state.cv or "(not provided)",
        questions="\n".join(f"{n}. {q}" for n, q in enumerate(answered_questions(state), start=1)),
        transcript=_transcript(state),
    )
    state.feedback = core._ask_llm(
        prompts.INTERVIEW_FEEDBACK_SYSTEM_PROMPT, user_prompt, InterviewFeedback,
        model, temperature, max_tokens,
    )
    return state.feedback


def answered_questions(state: InterviewState) -> list[str]:
    """The main questions the candidate answered at least once, in order."""
    if state.finished and not state.ended_early:
        return state.questions  # completed interview: all of them
    # Questions before the current one are answered; the current one only if it has an answer.
    answered = state.question_index + (1 if state.answers_on_question > 0 else 0)
    return state.questions[:answered]


def end_early(state: InterviewState) -> None:
    """End the interview before the last question; the feedback then covers the answered ones.

    No LLM call: the closing message is written by the app.

    Raises:
        ValueError: if no question has been answered yet (nothing to give feedback on).
    """
    if state.finished:
        return
    if not answered_questions(state):
        raise ValueError("Answer at least one question before ending the interview.")
    state.finished = True
    state.ended_early = True
    state.messages.append({
        "role": "assistant",
        "content": "Let's stop here. Thank you for your time; your feedback follows.",
    })


def export_markdown(state: InterviewState) -> str:
    """The interview as a Markdown document: transcript, plus the feedback if there is one.

    Used for the download button and saved in the user's history (user_store.save_interview).
    """
    speaker = {"assistant": "**Interviewer:**", "user": "**You:**"}
    lines = [f"# Practice interview: {_role_label(state)}", ""]
    if state.ended_early:
        lines += [f"_Ended early, after {len(answered_questions(state))} of {len(state.questions)} questions._", ""]
    lines += ["## Transcript", ""]
    lines += [f"{speaker[m['role']]} {m['content']}\n" for m in state.messages]
    if state.feedback is not None:
        feedback = state.feedback
        lines += [
            "## Feedback", "",
            f"- Answer quality: **{feedback.overall_answer_score} / 5**",
            f"- Role fit: **{feedback.overall_fit_score} / 5**", "",
            feedback.summary, "",
        ]
        for number, item in enumerate(feedback.per_question, start=1):
            lines += [
                f"### {number}. {item.question}", "",
                f"Answer {item.answer_score}/5 · fit {item.fit_score}/5", "",
                f"- Strengths: {item.strengths}",
                f"- To improve: {item.improvements}", "",
            ]
    return "\n".join(lines)


def _llm_messages(
    state: InterviewState,
    conversation: list[dict[str, str]],
    answers: int,
    must_move_on: bool,
    is_last_question: bool,
) -> list[dict[str, str]]:
    """Messages for one interviewer turn: persona prompt, the conversation, a status note."""
    system_prompt = prompts.INTERVIEWER_SYSTEM_PROMPT_TEMPLATE.format(
        role=_role_label(state),
        job_text=state.job_text,
        cv=state.cv or "(not provided)",
        questions="\n".join(f"{n}. {q}" for n, q in enumerate(state.questions, start=1)),
    )
    instruction = ""
    if must_move_on:
        instruction += prompts.INTERVIEWER_LAST_ANSWER_INSTRUCTION
    if is_last_question:
        instruction += prompts.INTERVIEWER_LAST_QUESTION_INSTRUCTION
    status = prompts.INTERVIEWER_STATUS_TEMPLATE.format(
        number=state.question_index + 1,
        total=len(state.questions),
        question=state.questions[state.question_index],
        answers=answers,
        max_answers=MAX_ANSWERS_PER_QUESTION,
        last_instruction=instruction,
    )
    # The status note is a system message (not a user message), so the candidate's own text
    # cannot pretend to be it.
    return (
        [{"role": "system", "content": system_prompt}]
        + conversation
        + [{"role": "system", "content": status}]
    )


def _question_text(state: InterviewState, index: int) -> str:
    """A main question as shown in the chat, e.g. '**Question 2 of 5:** ...'."""
    return f"**Question {index + 1} of {len(state.questions)}:** {state.questions[index]}"


def _transcript(state: InterviewState) -> str:
    """The chat as plain text for the feedback call ('Interviewer: ...' / 'Candidate: ...')."""
    speaker = {"assistant": "Interviewer", "user": "Candidate"}
    return "\n\n".join(f"{speaker[m['role']]}: {m['content']}" for m in state.messages)


def _role_label(state: InterviewState) -> str:
    """Role with its level, e.g. 'Senior Data Analyst'.

    Just the title if the level is unknown or already part of it (the LLM sometimes returns
    the title 'Senior Data Analyst' with the level 'Senior').
    """
    seniority = state.seniority.strip()
    if seniority.casefold() in ("", "not specified") or seniority.casefold() in state.role_title.casefold():
        return state.role_title
    return f"{seniority} {state.role_title}"
