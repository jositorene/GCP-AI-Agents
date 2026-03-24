import streamlit as st
from app.app import get_user, logout, update_user_news, now_iso, users_collection, init_state

def render_journalist_page():
    # 1. Session & Auth Check
    user_session = st.session_state.get("logged_user")
    if not user_session:
        st.switch_page("main.py")
        return

    # 2. Fetch fresh data from news_db (Firestore)
    username = user_session.get("username")
    current_user = get_user(username)
    
    if not current_user:
        st.error("Journalist profile not found in database.")
        return

    # 3. Professional Welcoming Header
    st.markdown(f"""
        <div style="background-color: rgba(0,123,255,0.1); padding: 25px; border-radius: 15px; border-left: 8px solid #FFD700; margin-bottom: 25px;">
            <h1 style='margin: 0; color: white;'>Journalist Studio: <span style='color: #FFD700;'>{username.capitalize()}</span></h1>
            <p style='margin: 5px 0 0 0; color: #aaaaaa;'>Verified Press Account | Ready to publish and research.</p>
        </div>
    """, unsafe_allow_html=True)

    # 4. AI AGENTS TOOLBAR (Integrated with Agent Page)
    st.write("### 🛠️ Journalist AI Toolkit")
    agent_cols = st.columns(5)
    
    agents = [
        {"name": "New Research", "icon": "🔍", "page": "pages/agent_page.py"},
        {"name": "Article Gen", "icon": "✍️", "page": None},
        {"name": "Fact Checker", "icon": "🛡️", "page": None},
        {"name": "Read Interact", "icon": "📊", "page": None},
        {"name": "Social Media", "icon": "📢", "page": None}
    ]

    for i, agent in enumerate(agents):
        with agent_cols[i]:
            if st.button(f"{agent['icon']}\n{agent['name']}", key=f"j_btn_{i}", use_container_width=True):
                if agent["page"]:
                    st.switch_page(agent["page"])
                else:
                    st.info(f"The {agent['name']} Agent is currently in development.")

    st.markdown("---")

    # 5. Publishing Form
    st.write("### 📝 Draft New Article")
    with st.expander("Open Publishing Form", expanded=False):
        with st.form("publish_form", clear_on_submit=True):
            pub_topic = st.text_input("Article Topic", placeholder="e.g. AI Ethics")
            pub_title = st.text_input("Headline")
            pub_content = st.text_area("Full Content", height=200)
            
            submit_pub = st.form_submit_button("🚀 Publish to news_db")
            
            if submit_pub:
                if pub_topic and pub_title and pub_content:
                    new_article = {
                        "topic": pub_topic.strip(),
                        "headline": pub_title.strip(),
                        "summary": pub_content.strip(),
                        "published_at": now_iso(),
                        "source": f"Press: {username.capitalize()}"
                    }
                    
                    # Add new article to the top of the news_results list
                    current_news = current_user.get("news_results", [])
                    current_news.insert(0, new_article)
                    
                    try:
                        users_collection().document(username.lower()).update({"news_results": current_news})
                        st.success("Success! Article is now live in your feed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error connecting to Firestore: {e}")
                else:
                    st.warning("Please complete all fields before publishing.")

    # 6. Content Management Feed
    st.write("### 🗞️ Your Managed Feed")
    news_results = current_user.get("news_results", [])
    
    if not news_results:
        st.info("Your news feed is empty. Start publishing or research a topic!")
    else:
        for item in news_results:
            with st.container(border=True):
                st.markdown(f"#### {item.get('topic', 'Topic').upper()}")
                st.markdown(f"**{item.get('headline', 'No Title')}**")
                st.write(item.get("summary", "No content available."))
                st.caption(f"✍️ {item.get('source', 'System')} | 📅 {item.get('published_at', 'N/A')}")

    # 7. Sign Out Logic
    st.write("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        logout()

if __name__ == "__main__":
    init_state()
    render_journalist_page()
