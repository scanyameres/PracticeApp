"""Streamlit UI (the page itself): login, three input panels with their buttons, results in tabs.

Run with start_app.bat (or `uv run streamlit run src/scanya_ae_afa_updated0209_1_6/landing.py`).
This file only draws the page, validates inputs, and shows results; the work is done by:
actions.py (logic behind the buttons), guard.py (input checks), auth.py (login box),
cv_reader.py (CV PDFs), pricing.py (request costs), user_store.py (history tab).

Page order (Streamlit reruns this script top to bottom on every click):
header + login -> input panels + buttons -> button actions -> costs -> result tabs.
"""

import streamlit as st

import scanya_ae_afa_updated0209_1_6.core as appcore
from scanya_ae_afa_updated0209_1_6 import actions, auth, cv_reader, guard, pricing, user_store

GENERIC_MODE = "Generic role title and experience"
OPENING_MODE = "Specific job opening"

st.set_page_config(page_title="Application Assistant", page_icon="✳️", layout="wide")

# Streamlit only offers "centered" (~730 px) or "wide" (full screen). This small CSS rule keeps
# the wide layout but caps the content at 1200 px and centres it. Change MAX_PAGE_WIDTH to adjust.
MAX_PAGE_WIDTH = 1200
st.html(
    f"<style>[data-testid='stMainBlockContainer'] "
    f"{{ max-width: {MAX_PAGE_WIDTH}px; margin: 0 auto; }}</style>"
)

st.title("✳️ Application Assistant and Interview Practice")
st.caption("By Sergi Canyameres")
st.write("Prepare for a role, explore likely interview questions, check how well you fit an opening, and get a cover letter.")


# --- Optional login (auth.py): logged-in users get their job profiles saved (user_store.py) ---
username = auth.login_area()

# --- Inputs: three equal-height panels side by side (buttons are added below panels 1 and 2) ---
# Fixed-height bordered containers keep the three boxes aligned; content scrolls if it overflows.
SECTION_HEIGHT = 400
role_section, cv_section, settings_section = st.columns(3)

# Left: what the user is preparing for, and the matching inputs.
with role_section.container(border=True, height=SECTION_HEIGHT):
    st.markdown("**1 · What are you preparing?**")
    input_mode = st.radio("Mode", (GENERIC_MODE, OPENING_MODE), label_visibility="collapsed")
    role_title, seniority, job_description = "", "", ""
    if input_mode == GENERIC_MODE:
        role_title = st.text_input("Role title", value="Software Engineer")
        seniority = st.selectbox(
            "Experience level",
            ("Early career", "Mid-level", "Senior", "Lead / Manager"),
            index=1,
        )
    else:
        job_description = st.text_area(
            "Job opening URL or description",
            placeholder="Paste the job posting URL or role description...",
            height=100,
        )
    difficulty = st.select_slider(
        "Question difficulty",
        ("Easy", "Medium", "Hard"),
        value="Medium",
    )

# Middle: the user's CV, as a PDF (drag and drop) or pasted text. An uploaded PDF wins.
with cv_section.container(border=True, height=SECTION_HEIGHT):
    st.markdown("**2 · Your CV / resume**")
    cv_pdf = st.file_uploader("Drop your CV as PDF", type="pdf")
    pasted_cv = st.text_area(
        "...or paste it as text",
        placeholder="Paste your CV or resume here. Needed for the fit check and cover letter.",
        height=90,
        disabled=cv_pdf is not None,
    )
    user_cv = pasted_cv
    if cv_pdf is not None:
        try:
            user_cv = cv_reader.read_pdf_text(cv_pdf)
            st.caption(f"Using the text from {cv_pdf.name} ({len(user_cv):,} characters).")
        except ValueError as error:
            user_cv = ""
            st.error(str(error))

# Right: model and generation settings, plus the request costs.
with settings_section.container(border=True, height=SECTION_HEIGHT):
    st.markdown("**3 · Settings**")
    # The temperature toggle is drawn below the model list but decides its options, so read its
    # current value from session state first. Opting in switches to TEMPERATURE_MODELS, the only
    # ones that accept it; otherwise temperature stays None and is not sent at all.
    use_temperature = st.session_state.get("use_temperature", False)
    model = st.selectbox(
        "LLM model",
        appcore.TEMPERATURE_MODELS if use_temperature else appcore.AVAILABLE_MODELS,
        help="OpenRouter model used for all AI features.",
    )       
    max_tokens = st.slider(
        "Max tokens (answer length limit)",
        *appcore.MAX_TOKENS_RANGE,
        appcore.DEFAULT_MAX_TOKENS,
        step=500,
        help="Upper limit for each AI answer (including the model's hidden reasoning). A typical "
        "answer needs ~500-1,000 tokens; if the limit is reached, the answer is cut off and fails. "
        "A higher limit also raises the maximum possible cost.",
    )

    # Request costs, shown here in the Settings panel. Reserved now, filled at the end of
    # the actions below (costs are only known after the buttons have run). st.empty() (not
    # settings_section.empty()) so the placeholder goes inside this bordered container.
    cost_area = st.empty()

    st.toggle(
        "Set temperature (experimental)",
        key="use_temperature",
        help="The default models do not accept a temperature setting, so a different model is used.",
    )
    temperature = None
    if use_temperature:
        temperature = st.slider(
            "Temperature", 0.0, 2.0, 0.7, 0.1,
            help="Low = focused and repeatable answers. High = more varied and creative, but less reliable.",
        )
        st.warning(
            "**Experimental:** a different model may give lower-quality results, fail to return "
            "the expected format, or invent details (especially above 1.0). Review results carefully."
        )

# --- Result tabs: names, "new result" dots and the selected tab (drawn further below) ---
# Tab ids -> visible names. A tab id in st.session_state["new_results"] gets a green dot
# until the user clicks that tab; st.session_state["active_tab"] holds the selected tab id.
RESULT_TABS = {
    "questions": "Potential questions",
    "practice": "Practice interview",
    "fit": "Fit check & cover letter",
    "history": "My history",
}
NEW_RESULT_DOT = " :green[●]"  # Markdown colour directive, supported in tab labels
st.session_state.setdefault("new_results", set())
st.session_state.setdefault("active_tab", "questions")


def _tab_label(tab_id: str) -> str:
    """Visible tab name, plus a green dot if the tab has a result the user hasn't opened yet."""
    dot = NEW_RESULT_DOT if tab_id in st.session_state["new_results"] else ""
    return RESULT_TABS[tab_id] + dot


def _show_new_result(tab_id: str) -> None:
    """After a button produced a result: mark its tab as new and switch to it."""
    st.session_state["new_results"].add(tab_id)
    st.session_state["active_tab"] = tab_id


def _on_tab_click() -> None:
    """When the user clicks a tab: remember it and remove its green dot."""
    clicked_label = st.session_state["results_tabs"]
    tab_id = next(i for i, name in RESULT_TABS.items() if clicked_label.startswith(name))
    st.session_state["active_tab"] = tab_id
    st.session_state["new_results"].discard(tab_id)


def _check_with_guard(role_title: str, seniority: str, job_description: str, cv: str = "") -> str:
    """Run the security guard on the inputs an action uses.

    Returns guard.FAIR_REQUEST if the inputs are fine, otherwise a warning message.

    If something is flagged, the caller shows the warning and skips the action, so the user
    can change the input and click again.
    """
    with st.spinner("Checking your input..."):
        return guard.check_inputs(role_title, seniority, job_description, cv)


# --- Actions: each button runs one feature and stores its result in session state ---
# Each button goes in the column of the panel it uses, so it appears right below that panel
# at the same width: questions under 1 (role/job), fit check under 2 (CV).
build_brief = role_section.button("Suggest interview questions", type="primary", width="stretch")
check_fit = cv_section.button("Check my fit & write a cover letter", type="primary", width="stretch", help="Needs your CV and a role title or job opening.")

if build_brief:
    pricing.start_tracking()  # add up the cost of every request this click makes
    if input_mode == GENERIC_MODE and not role_title.strip():
        st.error("Add a role title to continue.")
    elif input_mode == OPENING_MODE and not job_description.strip():
        st.error("Paste a job opening URL or description, or switch to a generic role title.")
    elif (guard_message := _check_with_guard(role_title, seniority, job_description)) != guard.FAIR_REQUEST:
        st.warning(guard_message)
    else:
        # The logic (LLM call, history) is in actions.py. Generic mode falls back to stored
        # questions by itself (result.plan.fallback_reason); other errors are shown as a message.
        try:
            with st.spinner("Generating interview questions..."):
                st.session_state["questions_result"] = actions.suggest_questions(
                    username, role_title, seniority, job_description, difficulty, model,
                    temperature, max_tokens,
                )
            _show_new_result("questions")
        except Exception as error:
            st.error(f"Could not generate the brief: {error}")

if check_fit:
    pricing.start_tracking()  # add up the cost of every request this click makes
    if not user_cv.strip():
        st.error("Add your CV (PDF or pasted text) to check your fit and get a cover letter.")
    elif input_mode == GENERIC_MODE and not role_title.strip():
        st.error("Add a role title to compare your CV with.")
    elif input_mode == OPENING_MODE and not job_description.strip():
        st.error("Paste a job opening URL or description to compare your CV with.")
    elif (guard_message := _check_with_guard(role_title, seniority, job_description, user_cv)) != guard.FAIR_REQUEST:
        st.warning(guard_message)
    else:
        try:
            with st.spinner("Comparing your CV with the job and writing a cover letter..."):
                st.session_state["fit_result"] = actions.check_fit(
                    username, user_cv, role_title, seniority, job_description, model,
                    temperature, max_tokens,
                )
            _show_new_result("fit")
        except Exception as error:
            st.error(f"Could not check your fit: {error}")


# --- Request costs (Medium task 3), drawn into cost_area in the Settings panel ---
# Add this click's requests (guard check, embedding, main LLM call: whatever ran) to the totals.
st.session_state.setdefault("session_cost", 0.0)
if build_brief or check_fit:
    action_cost, action_requests = pricing.tracked_cost()
    if action_requests:
        st.session_state["last_cost"] = (action_cost, action_requests)
        st.session_state["session_cost"] += action_cost

with cost_area.container():
    estimate = pricing.estimate_max_cost(model, max_tokens)
    lines = []
    if estimate is not None:
        lines.append(f"Estimated max cost: **{pricing.format_usd(estimate)}**")
    if last := st.session_state.get("last_cost"):
        lines.append(f"Last action: **{pricing.format_usd(last[0])}** ({last[1]} requests)")
        lines.append(f"Session total: **{pricing.format_usd(st.session_state['session_cost'])}**")
    st.caption("  \n".join(lines))

st.divider()

# --- Results: one tab per feature; each shows a hint until its button has been used ---
# Labels can change (green dot on/off), so the selected tab is set through its key before
# drawing: Streamlit then opens that tab, e.g. the one a button just filled.
st.session_state["results_tabs"] = _tab_label(st.session_state["active_tab"])
brief_tab, practice_tab, fit_tab, history_tab = st.tabs(
    [_tab_label(tab_id) for tab_id in RESULT_TABS],
    key="results_tabs",
    on_change=_on_tab_click,
)

with brief_tab:
    questions_result = st.session_state.get("questions_result")
    if not isinstance(questions_result, actions.QuestionsResult):
        st.info("Click **Suggest interview questions** to get likely interview questions for the role.")
    else:
        plan = questions_result.plan
        if plan.fallback_reason:
            st.warning(
                "The AI model could not generate questions, so these are standard backup questions "
                f"for this type of role.  \nReason: {plan.fallback_reason}"
            )
        st.subheader(f"{plan.role_title} · {plan.seniority}")
        st.write(plan.role_summary)
        st.markdown(f"**Questions to explore ({len(plan.questions)})**")
        if questions_result.avoided_questions:
            st.info(
                "You prepared for a similar job before, so these questions avoid the "
                f"{questions_result.avoided_questions} you already got."
            )
        # Both input modes produce PracticeQuestion objects, so they render the same way.
        for index, question in enumerate(plan.questions, start=1):
            with st.expander(f"{index}. {question.prompt}"):
                st.markdown(f"**{question.category}**")
                st.write(question.why_it_matters)

        # Up to 3 most similar past job profiles (logged-in users only).
        if questions_result.closest_roles:
            st.markdown("**Similar roles you prepared for before**")
            for profile, score in questions_result.closest_roles:
                st.markdown(f"- {profile['label']} · {score:.0%} similar · see *My history*")

with fit_tab:
    fit_result = st.session_state.get("fit_result")
    if not isinstance(fit_result, actions.FitResult):
        st.info("Add your CV and a role title or job opening, then click **Check my fit & write a cover letter**.")
    else:
        fit = fit_result.fit
        st.metric("Match score", f"{fit.match_score} / 10")
        st.progress(fit.match_score / 10)
        st.write(fit.reasoning)

        # Up to 3 similar jobs the user checked before, to compare scores (logged-in users only).
        if fit_result.similar_fits:
            st.markdown("**Similar jobs you checked before**")
            for profile, score in fit_result.similar_fits:
                st.markdown(
                    f"- {profile['label']}: **{profile['fit']['match_score']} / 10** "
                    f"· {score:.0%} similar · see *My history*"
                )

        st.subheader("Cover letter")
        with st.container(border=True):
            st.write(fit.cover_letter)
        st.download_button("Download cover letter (.txt)", fit.cover_letter, file_name="cover_letter.txt")

with history_tab:
    if not username:
        st.info("Log in (top of the page) to save every job profile you prepare for and see it here.")
    elif not (profiles := user_store.load_profiles(username)):
        st.info("No saved job profiles yet. Get interview questions or check your fit to start your history.")
    else:
        st.caption(f"{len(profiles)} job profiles, most recent first.")
        for profile in profiles:
            with st.expander(f"{profile['label']} · {profile['updated'][:10]}"):
                st.caption(f"Input: {profile['job_input'][:200]}")
                if profile["questions"]:
                    st.markdown(f"**Questions ({len(profile['questions'])})**")
                    for question in profile["questions"]:
                        st.markdown(f"- *{question['category']}:* {question['prompt']}")
                if profile["fit"]:
                    st.markdown(f"**Fit: {profile['fit']['match_score']} / 10**")
                    st.write(profile["fit"]["reasoning"])
                    st.text_area("Cover letter", profile["fit"]["cover_letter"], height=150, key=f"letter_{profile['key']}")

with practice_tab:
    st.info("Coming soon: practice an interview with your potential questions.")
    # Draft implementation, commented out until the feature is built:
    # st.subheader("Rehearse a response")
    # question_options = [question.prompt for question in plan.questions]
    # selected_prompt = st.selectbox("Choose a question", question_options, key="practice_question")
    # selected_question = next(question for question in plan.questions if question.prompt == selected_prompt)
    # st.caption(f"{selected_question.category} · {selected_question.why_it_matters}")
    #
    # answer = st.text_area(
    #     "Draft your answer",
    #     placeholder="What was happening, what did you do, and what changed?",
    #     height=190,
    #     key="practice_answer",
    # )
    # st.markdown("**Quick self-review**")
    # checks = (
    #     st.checkbox("I set the context", key="review_context"),
    #     st.checkbox("I explained my actions", key="review_actions"),
    #     st.checkbox("I shared an outcome", key="review_outcome"),
    # )
    # completed_checks = sum(checks)
    # st.progress(
    #     completed_checks / len(checks),
    #     text=f"{completed_checks} of {len(checks)} answer elements covered",
    # )
    #
    # # For now the draft lives only in session state; it will become the per-user history.
    # if st.button("Save practice draft", type="primary"):
    #     if not answer.strip():
    #         st.warning("Write a few notes before saving your practice draft.")
    #     else:
    #         st.session_state["saved_practice_answer"] = {
    #             "question": selected_prompt,
    #             "answer": answer.strip(),
    #             "checks": completed_checks,
    #         }
    #         st.success("Draft saved in this browser session.")
    #
    # saved_answer = st.session_state.get("saved_practice_answer")
    # if saved_answer and saved_answer["question"] == selected_prompt:
    #     st.caption("Your draft is held in Streamlit session state, not stored permanently.")

st.divider()
st.caption("Early prototype · Prep suggestions are illustrative, not an assessment.")
