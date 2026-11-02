"""Authenticated landing page for Interview Practice Studio.

Uses streamlit-authenticator in "path mode": the Authenticate object reads
credentials and cookie settings from config.yaml and writes changes (hashed
passwords, login state) back to that file automatically.
"""

from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

st.set_page_config(page_title="Interview Practice Studio", page_icon="✳️", layout="centered")

if not CONFIG_PATH.exists():
    st.error(
        f"Missing auth config at `{CONFIG_PATH.name}`. "
        "Copy `config.example.yaml` to `config.yaml` and fill in the cookie and credentials."
    )
    st.stop()

authenticator = stauth.Authenticate(str(CONFIG_PATH))

st.title("✳️ Interview Practice Studio")

try:
    authenticator.login(location="main")
except LoginError as e:
    st.error(e)

if st.session_state.get("authentication_status"):
    with st.sidebar:
        st.write(f"Signed in as **{st.session_state.get('name')}**")
        authenticator.logout(location="sidebar", key="Logout")

    st.write("Your app starts here.")
elif st.session_state.get("authentication_status") is False:
    st.error("Username/password is incorrect")
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password")

st.divider()
st.caption("Early prototype · Prep suggestions are illustrative, not an assessment.")
