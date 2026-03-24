import os
import hashlib
import json
import streamlit as st
from datetime import datetime, timezone
from typing import Dict, List, Optional
from google.cloud import firestore
from dotenv import load_dotenv
from pathlib import Path

# Agent logic
from app.news_agent import create_news_research_agent

load_dotenv()

# ----------------------------
# Constants
# ----------------------------
DEFAULT_TOPICS = [
    "Science", "Technology", "Politics",
    "Health", "Sports", "Economics", "Environment"
]

USERS_FILE = Path("users.json")  # For local subscriber storage

# ----------------------------
# Firestore & Agent Init
# ----------------------------
@st.cache_resource
def get_db() -> firestore.Client:
    project_id = os.getenv("PROJECT_ID", "")
    return firestore.Client(project=project_id) if project_id else firestore.Client()

@st.cache_resource
def get_agent():
    try:
        return create_news_research_agent()
    except Exception as e:
        print(f"CRITICAL: Agent init failed: {e}")
        return None

# ----------------------------
# Collections
# ----------------------------
def users_collection():
    return get_db().collection(os.getenv("FIRESTORE_COLLECTION_USERS", "users"))

def audit_collection():
    return get_db().collection(os.getenv("FIRESTORE_COLLECTION_AUDIT", "login_audit"))

# ----------------------------
# Utils
# ----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# ----------------------------
# Agent
# ----------------------------
def run_agent_search(query: str) -> List[Dict]:
    agent = get_agent()
    if not agent:
        return [{
            "topic": query,
            "headline": "Error",
            "summary": "Agent not initialized.",
            "published_at": now_iso(),
            "source": "System"
        }]
    try:
        result = agent.invoke({"input": query})
        answer = result.get("output", "No news found.")
        return [{
            "topic": query,
            "headline": f"Latest update on {query}",
            "summary": str(answer),
            "published_at": now_iso(),
            "source": "AI Research Agent"
        }]
    except Exception as e:
        st.error(f"Agent error: {e}")
        return []

# ----------------------------
# Firestore User Management
# ----------------------------
def user_exists(username: str) -> bool:
    try:
        return users_collection().document(username.lower()).get().exists
    except Exception:
        return False

def get_user(username: str) -> Optional[Dict]:
    try:
        doc = users_collection().document(username.lower()).get()
        return doc.to_dict() if doc.exists else None
    except Exception:
        return None

def create_user(payload: Dict) -> bool:
    """Create a Firestore user (journalist or post-payment subscriber)."""
    try:
        username_key = payload["username"].lower()
        if user_exists(username_key):
            return False
        users_collection().document(username_key).set(payload)
        return True
    except Exception as e:
        print("Create user error:", e)
        return False

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    user = get_user(username)
    success = False
    if user and user.get("password_hash") == hash_password(password):
        success = True
    try:
        audit_collection().add({
            "username": username,
            "success": success,
            "timestamp": now_iso()
        })
    except Exception:
        pass
    return user if success else None

def update_user_news(username: str, topic: str) -> bool:
    try:
        new_results = run_agent_search(topic)
        if new_results:
            users_collection().document(username.lower()).update({
                "last_search_topic": topic,
                "news_results": new_results,
                "updated_at": now_iso(),
            })
            return True
        return False
    except Exception:
        return False

# ----------------------------
# Local JSON Subscriber Management
# ----------------------------
def create_local_user(payload: Dict) -> bool:
    """
    Save subscriber to local JSON file (used by payment.py).
    Prevents duplicate usernames.
    """
    try:
        if USERS_FILE.exists():
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        else:
            users = []

        if any(u["username"].lower() == payload["username"].lower() for u in users):
            return False

        users.append(payload)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
        return True
    except Exception as e:
        print("Local user creation error:", e)
        return False

# ----------------------------
# Registration / Payment Flow
# ----------------------------
def save_registration(form_data: Dict):
    topics = list(form_data.get("topics", []))
    custom_topic = form_data.get("custom_topic", "").strip()
    if custom_topic:
        topics.append(custom_topic)
    search_query = ", ".join(topics) if topics else "Latest world news"
    initial_news = run_agent_search(search_query)

    payload = {
        "username": form_data["username"].strip(),
        "email": form_data["email"].strip(),
        "password_hash": hash_password(form_data["password"]),
        "user_type": form_data["user_type"].lower(),
        "selected_topics": topics,
        "news_results": initial_news,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    if payload["user_type"] == "journalist":
        create_user(payload)  # Firestore
        st.switch_page("main.py")
    else:
        st.session_state["pending_registration"] = payload  # Subscriber
        st.switch_page("pages/payment.py")

# ----------------------------
# Session State
# ----------------------------
def init_state():
    if "logged_user" not in st.session_state:
        st.session_state["logged_user"] = None
    if "pending_registration" not in st.session_state:
        st.session_state["pending_registration"] = {}

def logout():
    st.session_state.clear()
    st.rerun()