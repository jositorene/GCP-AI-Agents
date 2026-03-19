import streamlit as st 
from pathlib import Path
import base64
import firebase_admin
from firebase_admin import auth, credentials

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
SERVICE_ACCOUNT_PATH = BASE_DIR / "firebase_sa.json"
logo_path = BASE_DIR / "app" / "images" / "logo.png"
bg_path = BASE_DIR / "app" / "images" / "bckgnd.jpg"
css_path = BASE_DIR / "app" / "css" / "styles.css"

# ----------------------------
# Firebase initializer
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
    firebase_admin.initialize_app(cred)

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
st.set_page_config(page_title="Registration", layout="centered")

# Hide sidebar completely
st.markdown("""
<style>
section[data-testid="stSidebar"] {display: none !important;}
div[data-testid="collapsedControl"] {display: none !important;}
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
# User type
# ----------------------------
user_type = st.session_state.get("user_type", "Subscriber")

# ----------------------------
# Container
# ----------------------------
st.markdown('<div class="login-container">', unsafe_allow_html=True)

# Logo
if logo_path.exists():
    st.image(str(logo_path), width=640)
else:
    st.error(f"Logo not found: {logo_path}")

# Title
st.markdown('<h1 class="title">Registration</h1>', unsafe_allow_html=True)

# Role message
if user_type == "Journalist":
    st.warning("You are registering as a Journalist")
else:
    st.info("You are registering as a Subscriber")

# ----------------------------
# Journalist form
# ----------------------------
if user_type == "Journalist":
    with st.form("journalist_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        username = st.text_input("Username")
        submit = st.form_submit_button("Register")
        if submit:
            if email and password and username:
                try:
                    user = auth.create_user(
                        email=email,
                        password=password,
                        display_name=username
                    )
                    st.success(f"Journalist '{username}' registered successfully!")
                except auth.EmailAlreadyExistsError:
                    st.error("Email already registered. Try logging in.")
                except Exception as e:
                    st.error(f"Registration failed: {e}")
            else:
                st.error("Please fill all fields")

# ----------------------------
# Subscriber form
# ----------------------------
else:
    if "payment_step" not in st.session_state:
        st.session_state.payment_step = False

    if not st.session_state.payment_step:
        with st.form("subscriber_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            username = st.text_input("Username")
            submit = st.form_submit_button("Continue to Payment")
            if submit:
                if email and password and username:
                    st.session_state.subscriber_info = {
                        "email": email,
                        "password": password,
                        "username": username
                    }
                    st.session_state.payment_step = True
                    st.rerun()
                else:
                    st.error("Please fill all fields")
    else:
        st.subheader("💳 Payment (Mock)")
        st.text_input("Card Number", "1234 5678 9012 3456")
        st.text_input("Card Holder", "John Doe")
        st.text_input("Expiry Date", "12/30")
        st.text_input("CVV", "123")
        if st.button("Pay Now"):
            #initialize_firebase()  # Ensure Firebase is initialized
            info = st.session_state.subscriber_info
            try:
                user = auth.create_user(
                    email=info["email"],
                    password=info["password"],
                    display_name=info["username"]
                )
                st.success(f"Subscriber '{info['username']}' registered successfully!")
                st.session_state.payment_step = False
                st.session_state.subscriber_info = None
            except auth.EmailAlreadyExistsError:
                st.error("Email already registered. Try logging in.")
            except Exception as e:
                st.error(f"Registration failed: {e}")

# ----------------------------
# Back to Login
# ----------------------------
col1, col2 = st.columns([3,2])
with col1:
    st.write("Already have an account?")
with col2:
    if st.button("Back to Login"):
        st.switch_page("main.py")

st.markdown('</div>', unsafe_allow_html=True)