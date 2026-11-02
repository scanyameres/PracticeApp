"""Main Streamlit page of Interview Practice Studio.

Run with: uv run streamlit run src\\landing.py

Layout:
- Sidebar: inputs to build a prep brief, plus an optional login at the bottom.
- Main area: the generated prep brief and a tab to practice answers.

Streamlit reruns this whole script on every user interaction, so anything that must survive
between interactions (the current plan, login status) is kept in st.session_state.
"""

from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError

from practiceapp.prep import PreparationPlan, build_preparation_plan

# Auth settings and users (gitignored, contains secrets). Template: config.example.yaml.
AUTH_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

st.set_page_config(page_title="Interview Practice Studio", page_icon="✳️", layout="wide")

# --- Sidebar: brief inputs ---
with st.sidebar:
    st.title("✳️ Practice Studio")
    st.caption("A practical first step toward your next interview.")

    st.header("Build a prep brief")
    input_mode = st.radio("Start with", ("Role title", "Job description"))
    role_title = st.text_input("Role title", value="Software Engineer")
    seniority = st.selectbox(
        "Experience level",
        ("Early career", "Mid-level", "Senior", "Lead / Manager"),
        index=1,
    )
    job_description = ""
    if input_mode == "Job description":
        job_description = st.text_area(
            "Job description",
            placeholder="Paste the role responsibilities and skills here...",
            height=180,
        )

    # Validate inputs, build the plan, store it in session state, then rerun to show it.
    if st.button("Build my prep brief", type="primary", width="stretch"):
        if not role_title.strip():
            st.error("Add a role title to continue.")
        elif input_mode == "Job description" and not job_description.strip():
            st.error("Paste a job description, or switch to starting with a role title.")
        else:
            st.session_state["preparation_plan"] = build_preparation_plan(
                role_title,
                job_description if input_mode == "Job description" else "",
                seniority,
            )
            st.session_state.pop("saved_practice_answer", None)
            st.rerun()

    # --- Sidebar: optional login (streamlit-authenticator, see docs/streamlit-auth.md) ---
    # The app works fully without it; logged-in users will later get saved history.
    st.divider()
    if not AUTH_CONFIG_PATH.exists():
        st.caption("Login unavailable: copy `config.example.yaml` to `config.yaml` to enable it.")
    else:
        # login_sleep_time=0: skip the library's default 0.7 s pause on every rerun while logged out.
        authenticator = stauth.Authenticate(str(AUTH_CONFIG_PATH), login_sleep_time=0)
        auth_status = st.session_state.get("authentication_status")
        if auth_status:
            st.write(f"Signed in as **{st.session_state.get('name')}**")
            authenticator.logout(location="main", key="Logout")
            if not st.session_state.get("authentication_status"):
                st.rerun()  # redraw the sidebar as logged out right away
        else:
            with st.expander("Log in to save your work", expanded=auth_status is False):
                try:
                    authenticator.login(location="main")
                except LoginError as e:
                    st.error(e)
                new_status = st.session_state.get("authentication_status")
                if new_status:
                    st.rerun()  # redraw the sidebar as signed in right away
                elif new_status is False:
                    st.error("Username/password is incorrect")

# --- Main area ---
st.title("Interview Practice Studio")
st.write("Prepare for a role, explore likely interview topics, and practice your answers.")

plan = st.session_state.get("preparation_plan")
if not isinstance(plan, PreparationPlan):
    # No brief yet: show a short introduction.
    st.info("Enter a role title or job description in the sidebar to get started.")
    st.subheader("What you can do")
    first, second = st.columns(2)
    with first:
        st.markdown("**Prepare with focus**")
        st.write("Get role-relevant topics and example questions to explore.")
    with second:
        st.markdown("**Practice an answer**")
        st.write("Draft a response and review its context, actions, and outcome.")
else:
    # A brief exists: show its summary, then the brief and practice tabs.
    st.subheader(f"{plan.role_title} · {plan.seniority}")
    st.write(plan.role_summary)

    metrics = st.columns(2)
    metrics[0].metric("Practice questions", len(plan.questions))
    metrics[1].metric("Focus areas", len(plan.focus_areas))

    brief_tab, practice_tab = st.tabs(("Prep brief", "Practice an answer"))
    with brief_tab:
        st.subheader("Topics worth preparing")
        st.write(" · ".join(plan.focus_areas))
        st.subheader("Questions to explore")
        for index, question in enumerate(plan.questions, start=1):
            with st.expander(f"{index}. {question.prompt}"):
                st.markdown(f"**{question.category}**")
                st.write(question.why_it_matters)

    with practice_tab:
        st.subheader("Rehearse a response")
        question_options = [question.prompt for question in plan.questions]
        selected_prompt = st.selectbox("Choose a question", question_options, key="practice_question")
        selected_question = next(question for question in plan.questions if question.prompt == selected_prompt)
        st.caption(f"{selected_question.category} · {selected_question.why_it_matters}")

        answer = st.text_area(
            "Draft your answer",
            placeholder="What was happening, what did you do, and what changed?",
            height=190,
            key="practice_answer",
        )
        st.markdown("**Quick self-review**")
        checks = (
            st.checkbox("I set the context", key="review_context"),
            st.checkbox("I explained my actions", key="review_actions"),
            st.checkbox("I shared an outcome", key="review_outcome"),
        )
        completed_checks = sum(checks)
        st.progress(
            completed_checks / len(checks),
            text=f"{completed_checks} of {len(checks)} answer elements covered",
        )

        # For now the draft lives only in session state; it will become the per-user history.
        if st.button("Save practice draft", type="primary"):
            if not answer.strip():
                st.warning("Write a few notes before saving your practice draft.")
            else:
                st.session_state["saved_practice_answer"] = {
                    "question": selected_prompt,
                    "answer": answer.strip(),
                    "checks": completed_checks,
                }
                st.success("Draft saved in this browser session.")

        saved_answer = st.session_state.get("saved_practice_answer")
        if saved_answer and saved_answer["question"] == selected_prompt:
            st.caption("Your draft is held in Streamlit session state, not stored permanently.")

st.divider()
st.caption("Early prototype · Prep suggestions are illustrative, not an assessment.")
