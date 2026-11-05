"""Streamlit UI: three input sections (role/job, CV, settings), action buttons, results in tabs.

Run with start_app.bat (or `uv run streamlit run src/scanya_ae_afa_updated0209_1_6/landing.py`).
All logic lives in core.py; this file only collects inputs, calls core and shows results.
"""

from pathlib import Path
import streamlit as st

#import streamlit_authenticator as stauth
#from streamlit_authenticator.utilities import LoginError

import scanya_ae_afa_updated0209_1_6.core as appcore
from scanya_ae_afa_updated0209_1_6 import cv_reader

# Auth settings and users (gitignored, contains secrets). Template: config.example.yaml.
# AUTH_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

GENERIC_MODE = "Generic role title and experience"
OPENING_MODE = "Specific job opening"

st.set_page_config(page_title="Application Assistant", page_icon="✳️", layout="wide")

st.title("✳️ Application Assistant and Interview Practice")
st.caption("By Sergi Canyameres")
st.write("Prepare for a role, explore likely interview questions, check how well you fit an opening, and get a cover letter.")

# --- Inputs: three equal-height sections side by side ---
# Fixed-height bordered containers keep the three boxes aligned; content scrolls if it overflows.
SECTION_HEIGHT = 420
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
            height=220,
        )

# Middle: the user's CV, as a PDF (drag and drop) or pasted text. An uploaded PDF wins.
with cv_section.container(border=True, height=SECTION_HEIGHT):
    st.markdown("**2 · Your CV / resume**")
    cv_pdf = st.file_uploader("Drop your CV as PDF", type="pdf")
    pasted_cv = st.text_area(
        "...or paste it as text",
        placeholder="Paste your CV or resume here. Needed for the fit check and cover letter.",
        height=130,
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

# Right: model and generation settings.
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
    difficulty = st.select_slider(
        "Question difficulty",
        ("Easy", "Medium", "Hard"),
        value="Medium",
    )
    if use_temperature:
        st.warning(
            "**Experimental:** a different model may give lower-quality results, fail to return "
            "the expected format, or invent details (especially above 1.0). Review results carefully."
        )

# --- Actions: each button runs one feature and stores its result in session state ---
brief_column, fit_column = st.columns(2)
build_brief = brief_column.button("Build my prep brief", type="primary", width="stretch")
check_fit = fit_column.button(
    "Check my fit & write a cover letter",
    width="stretch",
    help="Needs your CV and a role title or job opening.",
)

if build_brief:
    if input_mode == GENERIC_MODE and not role_title.strip():
        st.error("Add a role title to continue.")
    elif input_mode == OPENING_MODE and not job_description.strip():
        st.error("Paste a job opening URL or description, or switch to a generic role title.")
    else:
        # Both modes call the LLM. The generic one falls back to stored questions by itself
        # (see plan.fallback_reason); other errors are shown as a message instead of a traceback.
        try:
            with st.spinner("Generating your prep brief..."):
                if input_mode == GENERIC_MODE:
                    st.session_state["preparation_plan"] = appcore.build_preparation_plan_generic(
                        role_title, seniority, difficulty, model, temperature
                    )
                else:
                    st.session_state["preparation_plan"] = appcore.build_preparation_plan_opening(
                        job_description, difficulty, model, temperature
                    )
        except Exception as error:
            st.error(f"Could not generate the brief: {error}")

if check_fit:
    if not user_cv.strip():
        st.error("Paste your CV to check your fit and get a cover letter.")
    elif input_mode == GENERIC_MODE and not role_title.strip():
        st.error("Add a role title to compare your CV with.")
    elif input_mode == OPENING_MODE and not job_description.strip():
        st.error("Paste a job opening URL or description to compare your CV with.")
    else:
        # Generic mode has no posting, so a short description of the role stands in for it.
        if input_mode == GENERIC_MODE:
            job_for_fit = appcore.describe_generic_role(role_title, seniority)
        else:
            job_for_fit = job_description
        try:
            with st.spinner("Comparing your CV with the job and writing a cover letter..."):
                st.session_state["fit_assessment"] = appcore.assess_fit_and_write_cover_letter(
                    user_cv, job_for_fit, model, temperature
                )
        except Exception as error:
            st.error(f"Could not check your fit: {error}")

st.divider()

# --- Results: one tab per feature; each shows a hint until its button has been used ---
brief_tab, fit_tab, practice_tab = st.tabs(("Prep brief", "Fit check & cover letter", "Practice an answer"))

with brief_tab:
    plan = st.session_state.get("preparation_plan")
    if not isinstance(plan, appcore.PreparationPlan):
        st.info("Click **Build my prep brief** to get likely interview questions for the role.")
    else:
        if plan.fallback_reason:
            st.warning(
                "The AI model could not generate questions, so these are standard backup questions "
                f"for this type of role.  \nReason: {plan.fallback_reason}"
            )
        st.subheader(f"{plan.role_title} · {plan.seniority}")
        st.write(plan.role_summary)
        st.markdown(f"**Questions to explore ({len(plan.questions)})**")
        # Both input modes produce PracticeQuestion objects, so they render the same way.
        for index, question in enumerate(plan.questions, start=1):
            with st.expander(f"{index}. {question.prompt}"):
                st.markdown(f"**{question.category}**")
                st.write(question.why_it_matters)

with fit_tab:
    fit = st.session_state.get("fit_assessment")
    if not isinstance(fit, appcore.FitAssessment):
        st.info("Add your CV and a role title or job opening, then click **Check my fit & write a cover letter**.")
    else:
        st.metric("Match score", f"{fit.match_score} / 10")
        st.progress(fit.match_score / 10)
        st.write(fit.reasoning)

        st.subheader("Cover letter")
        with st.container(border=True):
            st.write(fit.cover_letter)
        st.download_button("Download cover letter (.txt)", fit.cover_letter, file_name="cover_letter.txt")

with practice_tab:
    st.info("Coming soon: rehearse an answer to one of your prep questions.")
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


# --- Not active yet: kept for later features ---

# Optional login (streamlit-authenticator, see docs/streamlit-auth.md).
# with st.sidebar:
#     # The app works fully without it; logged-in users will later get saved history.
#     st.divider()
#     if not AUTH_CONFIG_PATH.exists():
#         st.caption("Login unavailable: copy `config.example.yaml` to `config.yaml` to enable it.")
#     else:
#         # login_sleep_time=0: skip the library's default 0.7 s pause on every rerun while logged out.
#         authenticator = stauth.Authenticate(str(AUTH_CONFIG_PATH), login_sleep_time=0)
#         auth_status = st.session_state.get("authentication_status")
#         if auth_status:
#             st.write(f"Signed in as **{st.session_state.get('name')}**")
#             authenticator.logout(location="main", key="Logout")
#             if not st.session_state.get("authentication_status"):
#                 st.rerun()  # redraw the sidebar as logged out right away
#         else:
#             with st.expander("Log in to save your work", expanded=auth_status is False):
#                 try:
#                     authenticator.login(location="main")
#                 except LoginError as e:
#                     st.error(e)
#                 new_status = st.session_state.get("authentication_status")
#                 if new_status:
#                     st.rerun()  # redraw the sidebar as signed in right away
#                 elif new_status is False:
#                     st.error("Username/password is incorrect")
