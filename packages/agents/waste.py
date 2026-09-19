import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api")))
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
try:
    from rag.retrieve import retrieve_relevant_documents
except ImportError:
    retrieve_relevant_documents = None

from agents.core_identity import CORE_IDENTITY

@tool
def search_waste_knowledge_base(query: str) -> str:
    """Search the official government knowledge base for waste management, recycling, and scrap collection."""
    if retrieve_relevant_documents:
        return retrieve_relevant_documents(query, category="Waste")
    return "Knowledge base is currently unavailable."

class WasteAgent:
    def __init__(self):
        self.name = "Waste Management Agent"
        self.description = "Orchestrates local waste management and plastic recycling requests."
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [search_waste_knowledge_base]
        
        agent_instructions = """তুমি বর্জ্য ব্যবস্থাপনা এজেন্ট (WasteAgent)। পরিবেশ পরিচ্ছন্ন রাখতে এবং বর্জ্য ব্যবস্থাপনায় সাহায্য করার জন্য তুমি কাজ করো। 
"""
        self.agent_executor = create_react_agent(self.llm, tools=self.tools, state_modifier=CORE_IDENTITY + "\n\n" + agent_instructions)

    def process_query(self, query: str) -> str:
        response = self.agent_executor.invoke({"messages": [("user", query)]})
        return response["messages"][-1].content
