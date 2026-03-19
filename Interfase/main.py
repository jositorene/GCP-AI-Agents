import streamlit as st
from pathlib import Path
import base64
from app.text.messages import LOGIN_INFO
import firebase_admin
from firebase_admin import auth, credentials

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent
SERVICE_ACCOUNT_PATH = BASE_DIR / "firebase_sa.json"
logo_path = BASE_DIR / "app" / "images" / "logo.png"
bg_path = BASE_DIR / "app" / "images" / "bckgnd.jpg"
css_path = BASE_DIR / "app" / "css" / "styles.css"

# ----------------------------
# Firebase setup
# ----------------------------
try:
    if not firebase_admin._apps:
        if not SERVICE_ACCOUNT_PATH.exists():
            st.error(f"Firebase service account not found: {SERVICE_ACCOUNT_PATH}")
            st.stop()
        cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
        firebase_admin.initialize_app(cred)
except Exception as e:
    st.error(f"Error initializing Firebase: {e}")
    st.stop()

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Login", layout="centered")

# Hide sidebar completely
st.markdown("""
<style>
section[data-testid="stSidebar"] {display: none !important;}
div[data-testid="collapsedControl"] {display: none !important;}
.appview-container .main .block-container {
    padding-left:0rem;
    padding-right:0rem;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Background & CSS
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

if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ----------------------------
# Session state defaults
# ----------------------------
if "user_type" not in st.session_state:
    st.session_state.user_type = "Subscriber"
if "email" not in st.session_state:
    st.session_state.email = None

# ----------------------------
# Container
# ----------------------------
st.markdown('<div class="login-container">', unsafe_allow_html=True)

# Logo
if logo_path.exists():
    st.image(str(logo_path), width=580)
else:
    st.error(f"Logo not found: {logo_path}")

# Title & info
st.markdown('<h1 class="title">Welcome</h1>', unsafe_allow_html=True)
st.markdown(f'<div class="info-text">{LOGIN_INFO}</div>', unsafe_allow_html=True)

# ----------------------------
# Login form
# ----------------------------
with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    user_type = st.radio("Select user type:", ["Subscriber", "Journalist"])
    submitted = st.form_submit_button("Login")

    if submitted:
        st.session_state.user_type = user_type
        if email and password:
            try:
                # Firebase Auth: check if user exists
                user = auth.get_user_by_email(email)
                st.session_state.email = email
                st.success(f"Logged in as {email} ({user_type})")

                # ----------------------------
                # Redirect based on user type
                # ----------------------------
                if user_type == "Journalist":
                    # st.rerun()
                    st.switch_page("pages/journalist_page.py")
                else:
                    # st.rerun()
                    st.switch_page("pages/subscriber_page.py")

            except auth.UserNotFoundError:
                st.error("User not found. Please register first.")
            except Exception as e:
                st.error(f"Firebase error: {e}")
        else:
            st.error("Please enter both email and password")

# ----------------------------
# Go to Registration button
# ----------------------------
col1, col2 = st.columns([3,2])
with col1:
    st.write("For new user:")
with col2:
    if st.button("Go to Registration"):
        st.session_state.user_type = user_type
        st.switch_page("pages/registration.py")  # must match pages/registration.py

st.markdown('</div>', unsafe_allow_html=True)