import os
import base64
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from app.app import init_state, authenticate_user
from app.text.messages import LOGIN_INFO

load_dotenv()

# ----------------------------
# Paths & Aesthetics
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
logo_path = BASE_DIR / "app" / "images" / "logo.png"
bg_path = BASE_DIR / "app" / "images" / "bckgnd.jpg"
css_path = BASE_DIR / "app" / "css" / "styles.css"

st.set_page_config(
    page_title=os.getenv("APP_TITLE", "Flash Newspaper"),
    page_icon="📰",
    layout="centered",
)

# ----------------------------
# Hide Sidebar
# ----------------------------
st.markdown("""
<style>
section[data-testid="stSidebar"] {display: none !important;}
div[data-testid="collapsedControl"] {display: none !important;}
.appview-container .main .block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Background
# ----------------------------
if bg_path.exists():
    with open(bg_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

# ----------------------------
# CSS
# ----------------------------
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ----------------------------
# Login Page
# ----------------------------
def render_login_page():

    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    if logo_path.exists():
        st.image(str(logo_path), width=580)

    st.markdown('<h1 class="title">Welcome</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-text">{LOGIN_INFO}</div>', unsafe_allow_html=True)

    with st.form("login_form"):

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:

            if not username or not password:
                st.error("Please fill all fields.")
                st.stop()

            user = authenticate_user(username.strip(), password)

            if not user:
                st.error("Invalid credentials. Please check your username/password.")
                st.stop()

            # Save session
            st.session_state["logged_user"] = user

            user_type = user.get("user_type", "subscriber").lower()

            if user_type == "subscriber":
                st.switch_page("pages/subscriber_page.py")
            else:
                st.switch_page("pages/journalist_page.py")

    # ----------------------------
    # Registration Link
    # ----------------------------
    st.markdown("---")

    col1, col2 = st.columns([3,2])

    with col1:
        st.write("New to Flash Newspaper?")

    with col2:
        if st.button("Register Here"):
            st.switch_page("pages/registration.py")

    st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------
# App Entry
# ----------------------------
def main():

    init_state()

    # If already logged in redirect automatically
    if st.session_state.get("logged_user"):

        user = st.session_state["logged_user"]
        user_type = user.get("user_type", "subscriber").lower()

        if user_type == "subscriber":
            st.switch_page("pages/subscriber_page.py")
        else:
            st.switch_page("pages/journalist_page.py")

    render_login_page()


if __name__ == "__main__":
    main()