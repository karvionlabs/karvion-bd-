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
def search_scholarship_knowledge_base(query: str) -> str:
    """Search the official government knowledge base for scholarship information."""
    if retrieve_relevant_documents:
        return retrieve_relevant_documents(query, category="Scholarship")
    return "Knowledge base is currently unavailable."

class StudentAgent:
    def __init__(self):
        self.name = "Student Agent"
        self.description = "Assists students with scholarships, university admissions, IT skill training, and SOP guidelines."
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [search_scholarship_knowledge_base]
        
        agent_instructions = """তুমি স্টুডেন্ট এজেন্ট (Student Agent)। তোমার কাজ হলো শিক্ষার্থীদের উপবৃত্তি (যেমন: PMEAT), স্কলারশিপ, ভর্তি এবং ক্যারিয়ার গাইডেন্স দেওয়া।
আবেদনের যোগ্যতা, প্রয়োজনীয় ডকুমেন্টস, শেষ তারিখ এবং পোর্টালের লিংক স্পষ্টভাবে উল্লেখ করবে।
"""

        self.agent_executor = create_react_agent(self.llm, tools=self.tools, state_modifier=CORE_IDENTITY + "\n\n" + agent_instructions)

    def process_query(self, query: str) -> str:
        response = self.agent_executor.invoke({"messages": [("user", query)]})
        return response["messages"][-1].content
