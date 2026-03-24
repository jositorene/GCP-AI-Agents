import streamlit as st
from app.app import DEFAULT_TOPICS, user_exists, save_registration, init_state

def render_registration_page():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="title">User Registration</h1>', unsafe_allow_html=True)
    st.write("Join Flash Newspaper and personalize your AI experience.")

    # Registration Form
    with st.form("reg_form", clear_on_submit=False):
        username = st.text_input("Username").strip()
        email = st.text_input("Email Address").strip()
        password = st.text_input("Password", type="password")
        verify_password = st.text_input("Confirm Password", type="password")
        user_type = st.selectbox("Role", ["Subscriber", "Journalist"])
        
        st.markdown("---")
        st.subheader("Personalize Your Feed")
        topics = st.multiselect("Choose your interests:", DEFAULT_TOPICS)
        custom_topic = st.text_input("Is a topic missing? Add it here:", placeholder="e.g. Quantum Computing")

        submitted = st.form_submit_button("Complete Registration")

    # Logic Handling
    if submitted:
        if not (username and email and password):
            st.error("Please fill in all required fields.")
        elif password != verify_password:
            st.error("Passwords do not match.")
        elif user_exists(username):
            st.error(f"The username '{username}' is already taken. Please choose another.")
        else:
            with st.spinner("🤖 AI Agent is researching your initial topics..."):
                try:
                    save_registration({
                        "username": username,
                        "email": email,
                        "password": password,
                        "user_type": user_type,
                        "topics": topics,
                        "custom_topic": custom_topic
                    })
                except Exception as e:
                    st.error(f"Error during registration: {e}")

    st.markdown("---")
    if st.button("⬅️ Back to Login"):
        st.switch_page("main.py")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    init_state()
    render_registration_page()