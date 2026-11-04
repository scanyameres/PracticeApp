from pathlib import Path
import streamlit as st

#import streamlit_authenticator as stauth
#from streamlit_authenticator.utilities import LoginError

# from practiceapp.prep import PreparationPlan, build_preparation_plan

# Auth settings and users (gitignored, contains secrets). Template: config.example.yaml.
# AUTH_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

st.set_page_config(page_title="Application Assistant", page_icon="✳️", layout="wide")

# --- Sidebar: brief inputs ---
with st.sidebar:
    st.title("✳️ Application Assistant and Interview Practice")
    st.caption("By Sergi Canyameres")

    st.header("Build a prep brief")
    input_mode = st.radio("Start with", ("Role title and experience", "Job opening"))
    if input_mode == "Role title and experience":
        role_title = st.text_input("Role title", value="Software Engineer")
        seniority = st.selectbox(
            "Experience level",
            ("Early career", "Mid-level", "Senior", "Lead / Manager"),
            index=1,
        )
    job_description = ""
    if input_mode == "Job opening":
        job_description = st.text_area(
            "Job opening URL or description",
            placeholder="Paste the job posting URL or role description...",
            height=180,
        )

    # Validate inputs, build the plan, store it in session state, then rerun to show it.
    if st.button("Build my prep brief", type="primary", width="stretch"):
        if input_mode == "Role title and experience" and not role_title.strip():
            st.error("Add a role title to continue.")
        elif input_mode == "Job description" and not job_description.strip():
            st.error("Paste a job opening URL or description, or switch to starting with a role title.")
        else:
            st.session_state["preparation_plan"] = build_preparation_plan(
                role_title,
                job_description if input_mode == "Job description" else "",
                seniority,
            )
            st.session_state.pop("saved_practice_answer", None)
            st.rerun()


    # --- Sidebar: optional login (streamlit-authenticator, see docs/streamlit-auth.md) ---
"""
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
"""
