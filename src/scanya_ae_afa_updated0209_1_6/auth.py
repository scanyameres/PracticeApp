"""Optional user login with streamlit-authenticator, configured from config.yaml in the project root.

config.yaml holds the user accounts, with passwords stored as bcrypt hashes, and the key that
signs the login cookie. It is committed to git on purpose (demo accounts with dummy passwords,
for reviewers); a real deployment would keep it out of git. If it does not exist, it is created
on first start with no users and a random cookie key; users then sign up with the "Create
account" form, which streamlit-authenticator writes back to the same file.

Public function: login_area() (draws the login box; the only Streamlit UI outside landing.py).
"""

from pathlib import Path
import secrets

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError
import yaml

AUTH_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"


def login_area() -> str | None:
    """Draw the login / create-account box, or "signed in as" + logout. Returns the username or None.

    streamlit-authenticator keeps the login state in st.session_state ("authentication_status",
    "username", "name"). After logging in or out, the page is redrawn right away (st.rerun).
    """
    authenticator = _get_authenticator()
    if st.session_state.get("authentication_status"):
        name_column, logout_column = st.columns((4, 1))
        name_column.caption(
            f"Signed in as **{st.session_state['name']}** · your job profiles are saved in *My history*."
        )
        with logout_column:
            authenticator.logout(location="main", key="Logout")
        if not st.session_state.get("authentication_status"):
            st.rerun()  # redraw as logged out right away
        return st.session_state["username"]

    # Not logged in. login() also restores a session from the login cookie, so it must run on
    # every page load; it is drawn inside the (collapsed) expander.
    with st.expander("🔐 Log in or create an account to save your history (optional)"):
        login_tab, signup_tab = st.tabs(("Log in", "Create account"))
        with login_tab:
            try:
                authenticator.login(location="main", key="Login")
            except LoginError as error:
                st.error(str(error))
            if st.session_state.get("authentication_status") is False:
                st.error("Username or password is incorrect.")
        with signup_tab:
            try:
                _, new_username, _ = authenticator.register_user(
                    location="main", captcha=False, password_hint=False
                )
                if new_username:
                    st.success(f"Account **{new_username}** created. You can now log in.")
            except Exception as error:  # e.g. username taken, passwords don't match, weak password
                st.error(str(error))
    if st.session_state.get("authentication_status"):
        st.rerun()  # just logged in: redraw with the "signed in" header
    return None


def _get_authenticator() -> stauth.Authenticate:
    """Return the authenticator for this page run, creating config.yaml first if needed."""
    if not AUTH_CONFIG_PATH.exists():
        _create_config()
    config = yaml.safe_load(AUTH_CONFIG_PATH.read_text(encoding="utf-8"))
    # Passing the file path (not a dict) lets the library save new accounts to the file itself.
    return stauth.Authenticate(
        str(AUTH_CONFIG_PATH),
        cookie_name=config["cookie"]["name"],
        cookie_key=config["cookie"]["key"],
        cookie_expiry_days=config["cookie"]["expiry_days"],
    )


def _create_config() -> None:
    """Write a starting config.yaml: no users yet and a random secret for the login cookie."""
    config = {
        "credentials": {"usernames": {}},
        "cookie": {
            "name": "interview_practice_login",
            "key": secrets.token_hex(32),
            "expiry_days": 30,
        },
    }
    AUTH_CONFIG_PATH.write_text(yaml.safe_dump(config), encoding="utf-8")
