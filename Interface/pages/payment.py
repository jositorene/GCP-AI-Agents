import streamlit as st
import base64
from pathlib import Path
from app.app import create_user, init_state

# ----------------------------
# Paths & Aesthetics
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
bg_path = BASE_DIR / "app" / "images" / "bckgnd.jpg"
css_path = BASE_DIR / "app" / "css" / "styles.css"

st.set_page_config(page_title="Secure Payment", layout="centered")

# ----------------------------
# Background
# ----------------------------
if bg_path.exists():
    with open(bg_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------
# CSS
# ----------------------------
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ----------------------------
# Payment Page
# ----------------------------
def render_payment():

    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    payload = st.session_state.get("pending_registration")

    # If user opens page without registration
    if not payload:
        st.warning("⚠️ No pending registration data found.")
        if st.button("Return to Registration"):
            st.switch_page("pages/registration.py")
        st.stop()

    st.markdown('<h2 class="title">💳 Secure Payment</h2>', unsafe_allow_html=True)
    st.write(f"Finalizing subscription for: **{payload.get('username')}**")

    # ----------------------------
    # Order Summary
    # ----------------------------
    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Plan:** {payload.get('user_type', 'Subscriber').capitalize()}")

        with col2:
            st.write(f"**Email:** {payload.get('email')}")

        topics = payload.get("selected_topics", [])
        st.caption(f"Selected Interests: {', '.join(topics) if topics else 'General'}")

    # ----------------------------
    # Payment Form
    # ----------------------------
    st.write("### Card Information")

    with st.form("payment_form"):

        cardholder = st.text_input("Cardholder Name", placeholder="John Doe")
        card_number = st.text_input("Card Number", placeholder="0000 0000 0000 0000")

        c1, c2 = st.columns(2)

        with c1:
            expiry = st.text_input("Expiry Date", placeholder="MM/YY")

        with c2:
            cvv = st.text_input("CVV", type="password", placeholder="***")

        submitted = st.form_submit_button("Pay & Activate Account")

    # ----------------------------
    # Payment Processing
    # ----------------------------
    if submitted:

        if not all([cardholder, card_number, expiry, cvv]):
            st.warning("Please fill all payment fields.")
            st.stop()

        with st.spinner("Processing transaction..."):

            try:
                success = create_user(payload)

            except Exception as e:
                st.error(f"Payment system error: {e}")
                st.stop()

        if success:

            st.success("🎉 Payment successful! Redirecting to login...")
            st.balloons()

            # Clear pending registration
            if "pending_registration" in st.session_state:
                del st.session_state["pending_registration"]

            # Redirect immediately to login
            st.switch_page("main.py")

        else:
            st.error("Account creation failed. Username may already exist.")

    # ----------------------------
    # Cancel
    # ----------------------------
    st.markdown("---")

    if st.button("Cancel & Back to Registration"):
        st.switch_page("pages/registration.py")

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# Page Entry
# ----------------------------
if __name__ == "__main__":
    init_state()
    render_payment()