import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun  # ✅ Corrected import

# Set Gemini API key (for demo; use env var in real apps)
os.environ["GOOGLE_API_KEY"] = "AIzaSyD4JbmGIIsB02nfJWODw8OgBL9rcJenjcw"

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# Setup DuckDuckGo tool
search = DuckDuckGoSearchRun()
tools = [
    Tool(
        name="DuckDuckGo Search",
        func=search.run,
        description="Searches the internet using DuckDuckGo."
    )
]

# Initialize agent with tool
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Streamlit UI
st.set_page_config(page_title="Gemini + DuckDuckGo", page_icon="🧠")
st.title("🔎 Gemini Chatbot + DuckDuckGo Search")

query = st.text_input("Ask anything:")

if query:
    with st.spinner("Thinking + Searching..."):
        result = agent.run(query)
        st.success(result)
