import streamlit as st
from app.app import get_user, run_agent_search, logout, init_state


def render_agent_page():
    # ----------------------------
    # 1. Access Control
    # ----------------------------
    if "logged_user" not in st.session_state or st.session_state["logged_user"] is None:
        st.switch_page("main.py")
        return

    user = st.session_state["logged_user"]
    username = user.get("username", "User")

    # ----------------------------
    # 2. Initialize Session State
    # ----------------------------
    if "agent_history" not in st.session_state:
        st.session_state.agent_history = []

    if "last_agent_result" not in st.session_state:
        st.session_state.last_agent_result = None

    # ----------------------------
    # 3. Page Header
    # ----------------------------
    st.title("🤖 AI Research Agent")
    st.markdown(
        f"Welcome, **{username.capitalize()}**. Use this specialized tool to perform deep research on any topic."
    )

    # ----------------------------
    # 4. Sidebar Status
    # ----------------------------
    with st.sidebar:
        st.write(f"Logged in as: **{username}**")

        if st.button("🚪 Logout"):
            logout()

        if st.button("🏠 Back to Dashboard"):
            if user.get("user_type") == "subscriber":
                st.switch_page("pages/subscriber_page.py")
            else:
                st.switch_page("pages/journalist_page.py")

    # ----------------------------
    # 5. Research Interaction
    # ----------------------------
    st.markdown("---")

    query = st.text_input(
        "Enter your research topic:",
        placeholder="e.g., Impact of AI in modern healthcare 2025",
    )

    if st.button("Start AI Research", use_container_width=True):

        if not query:
            st.warning("Please enter a topic first.")
            return

        try:
            with st.spinner(f"Agent is analyzing '{query}'..."):
                results = run_agent_search(query)

        except Exception as e:
            st.error(f"Agent error: {e}")
            return

        # ----------------------------
        # Safe Result Handling
        # ----------------------------
        if isinstance(results, list) and len(results) > 0:

            report = results[0]

            topic = report.get("topic", query)
            headline = report.get("headline", "AI Research Result")
            summary = report.get("summary", "No summary available.")
            published = report.get("published_at", "Unknown time")
            source = report.get("source", "AI Agent")

            st.success("✅ Research Completed")
            st.subheader(f"Report: {topic}")

            with st.container(border=True):
                st.markdown(f"### {headline}")
                st.write(summary)
                st.caption(f"Generated at: {published} | Source: {source}")

            # Save last result
            st.session_state.last_agent_result = report

            # Save to history if not duplicate
            if report not in st.session_state.agent_history:
                st.session_state.agent_history.insert(0, report)

        else:
            st.error("The agent could not generate a report. Please try again.")

    # ----------------------------
    # 6. History Section
    # ----------------------------
    st.markdown("---")
    st.write("### 📜 Session History")

    if not st.session_state.agent_history:
        st.info("No research performed yet.")
    else:
        for entry in st.session_state.agent_history:
            topic = entry.get("topic", "Unknown Topic")
            summary = entry.get("summary", "No summary available.")

            with st.expander(f"Previous Research: {topic}"):
                st.write(summary)


# ----------------------------
# Page Entry
# ----------------------------
if __name__ == "__main__":
    init_state()
    render_agent_page()