import streamlit as st
from app.app import get_user, logout, update_user_news, init_state

def render_subscriber_page():
    # ----------------------------
    # 1. Session & Auth Check
    # ----------------------------
    user_session = st.session_state.get("logged_user")
    if not user_session:
        st.switch_page("main.py")
        return

    # ----------------------------
    # 2. Fetch fresh user data
    # ----------------------------
    username = user_session.get("username")
    current_user = get_user(username)
    
    if not current_user:
        st.error("User data not found in database.")
        return

    # ----------------------------
    # 3. Welcome Message
    # ----------------------------
    st.markdown(f"""
        <div style="background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px;">
            <h1 style='margin: 0; color: white;'>Welcome back, <span style='color: #007bff;'>{username.capitalize()}</span>!</h1>
            <p style='margin: 5px 0 0 0; color: #cccccc;'>Your personalized AI News Dashboard is ready.</p>
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------
    # 4. AI Agents Toolbar
    # ----------------------------
    st.write("### 🤖 AI Research Tools")
    agent_cols = st.columns(5)
    
    agents = [
        {"name": "New\nResearch", "icon": "🔍", "page": "pages/agent_page.py"},
        {"name": "Article\nGeneration", "icon": "📝", "page": None},
        {"name": "Fact\nChecker", "icon": "✅", "page": None},
        {"name": "Read\nInteract", "icon": "📖", "page": None},
        {"name": "Social\nMedia", "icon": "📱", "page": None}
    ]

    for i, agent in enumerate(agents):
        with agent_cols[i]:
            if st.button(f"{agent['icon']}\n{agent['name']}", key=f"btn_{i}", use_container_width=True):
                if agent["page"]:
                    st.switch_page(agent["page"])
                else:
                    st.info(f"The {agent['name']} Agent is currently being calibrated.")

    st.markdown("---")

    # ----------------------------
    # 5. User Topics & Custom Search
    # ----------------------------
    col_info, col_search = st.columns([1, 1])
    
    with col_info:
        st.write("#### 🎯 Your Registered Topics")
        topics = current_user.get("selected_topics", [])
        if topics:
            st.info(" • ".join(topics))
        else:
            st.warning("No topics selected yet.")

    with col_search:
        st.write("#### 🆕 Custom Search")
        topic_input = st.text_input("Choose the latest news of:", placeholder="e.g. Quantum Computing")
        if st.button("Get the News", use_container_width=True):
            if topic_input.strip():
                with st.spinner("🤖 AI Agent is researching..."):
                    if update_user_news(username, topic_input.strip()):
                        st.success(f"Database updated with news for: {topic_input}")
                        st.rerun()
                    else:
                        st.error("The Search Agent failed to retrieve news. Check API logs.")
            else:
                st.warning("Please enter a topic.")

    # ----------------------------
    # 6. Display News Results
    # ----------------------------
    st.write("### 📰 Latest News from your DB")
    news_results = current_user.get("news_results", [])
    
    if not news_results:
        st.info("No news results found. Try the search field above!")
    else:
        for item in news_results:
            with st.container(border=True):
                st.markdown(f"#### {item.get('topic', 'General').upper()}")
                st.markdown(f"**{item.get('headline', 'No Headline Available')}**")
                st.write(item.get("summary", "No summary found for this topic."))
                st.caption(f"📅 {item.get('published_at', 'Unknown')} | 🌐 {item.get('source', 'System Agent')}")

    # ----------------------------
    # 7. Footer Logout
    # ----------------------------
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
    with f_col3:
        if st.button("🚪 Logout", use_container_width=True):
            logout()


# ----------------------------
# Page Entry
# ----------------------------
if __name__ == "__main__":
    init_state()
    render_subscriber_page()