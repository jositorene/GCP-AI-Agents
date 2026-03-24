import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Internal Import - Using a try-except to handle different path resolutions in Docker
try:
    from app.news_tool import news_search_tool
except ImportError:
    from news_tool import news_search_tool

load_dotenv()

# Ensure results directory exists - using /tmp for Cloud Run compatibility
# Cloud Run file systems are read-only except for /tmp
RESULT_DIR = "/tmp/agent_results" if os.environ.get("K_SERVICE") else "agent_results"
os.makedirs(RESULT_DIR, exist_ok=True)


def create_news_research_agent():
    """
    Logic to initialize the LangChain Agent with Google Gemini.
    """
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("GOOGLE_API_KEY not found in environment.")
        return None

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    tools = [news_search_tool]

    # ReAct Prompt Template
    template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""

    prompt = PromptTemplate.from_template(template)

    # Construct the ReAct agent
    agent = create_react_agent(llm, tools, prompt)

    # Create the executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )


@st.cache_resource
def load_agent():
    """
    Initializes and caches the agent for Streamlit.
    """
    try:
        return create_news_research_agent()
    except Exception as e:
        st.error(f"Agent initialization failed: {e}")
        return None


def run_research(query: str):
    """
    Main function to be called from app/app.py or UI pages.
    """
    agent_executor = load_agent()

    if not agent_executor:
        return "Agent system is currently unavailable. Check system logs."

    try:
        # Run the agent
        result = agent_executor.invoke({"input": query})

        output = result.get(
            "output",
            "The agent could not determine a final answer."
        )

        # Log results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(RESULT_DIR, f"research_{timestamp}.json")

        log_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "output": output
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=4, ensure_ascii=False)

        return output

    except Exception as e:
        return f"Agent Error: {str(e)}"