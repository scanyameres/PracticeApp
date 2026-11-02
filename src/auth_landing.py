"""Authenticated landing page for Interview Practice Studio.

Uses streamlit-authenticator in "path mode": the Authenticate object reads
credentials and cookie settings from config.yaml and writes changes (hashed
passwords, login state) back to that file automatically.
"""

from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import DeprecationError, LoginError

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

st.set_page_config(page_title="Interview Practice Studio", page_icon="✳️", layout="centered")

if not CONFIG_PATH.exists():
    st.error(
        f"Missing auth config at `{CONFIG_PATH.name}`. "
        "Copy `config.example.yaml` to `config.yaml` and fill in the cookie and credentials."
    )
    st.stop()

try:
    authenticator = stauth.Authenticate(str(CONFIG_PATH))
except DeprecationError as e:
    st.error(e)
    st.stop()

st.title("✳️ Interview Practice Studio")

try:
    authenticator.login(location="main")
except LoginError as e:
    st.error(e)

if st.session_state.get("authentication_status"):
    with st.sidebar:
        st.write(f"Signed in as **{st.session_state.get('name')}**")
        authenticator.logout(location="sidebar", key="Logout")

    st.success(f"Welcome *{st.session_state.get('name')}*")
    st.write("Prepare for a role, explore likely interview topics, and practice your answers.")

    st.subheader("What you can do")
    first, second = st.columns(2)
    with first:
        st.markdown("**Prepare with focus**")
        st.write("Get role-relevant topics and example questions to explore.")
    with second:
        st.markdown("**Practice an answer**")
        st.write("Draft a response and review its context, actions, and outcome.")
elif st.session_state.get("authentication_status") is False:
    st.error("Username/password is incorrect")
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password")

st.divider()
st.caption("Early prototype · Prep suggestions are illustrative, not an assessment.")
