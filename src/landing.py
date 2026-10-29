import streamlit as st

from practiceapp.prep import PreparationPlan, build_preparation_plan


st.set_page_config(page_title="Interview Practice Studio", page_icon="✳️", layout="wide")

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

    if st.button("Build my prep brief", type="primary", use_container_width=True):
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

    st.divider()
    st.caption("Prototype: local role patterns only. No AI, external API, or suitability score.")

st.title("Interview Practice Studio")
st.write("Prepare for a role, explore likely interview topics, and practice your answers.")

plan = st.session_state.get("preparation_plan")
if not isinstance(plan, PreparationPlan):
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
    st.subheader(f"{plan.role_title} · {plan.seniority}")
    st.write(plan.role_summary)

    metrics = st.columns(3)
    metrics[0].metric("Practice questions", len(plan.questions))
    metrics[1].metric("Focus areas", len(plan.focus_areas))
    metrics[2].metric("Suitability estimate", "Not assessed")

    brief_tab, practice_tab = st.tabs(("Prep brief", "Practice an answer"))
    with brief_tab:
        st.subheader("Topics worth preparing")
        st.write(" · ".join(plan.focus_areas))
        st.subheader("Questions to explore")
        st.caption("These are starting points, not predictions of exactly what an interviewer will ask.")
        for index, question in enumerate(plan.questions, start=1):
            with st.expander(f"{index}. {question.prompt}"):
                st.markdown(f"**{question.category}**")
                st.write(question.why_it_matters)

        st.info(
            "A meaningful suitability estimate needs your experience and evidence from the job criteria. "
            "This prototype avoids inventing a score."
        )

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
