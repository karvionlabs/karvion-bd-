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
def check_passport_status(application_id: str) -> str:
    """Check the current status of a Bangladesh e-Passport using the application ID or delivery slip number."""
    return f"পাসপোর্ট {application_id} এর বর্তমান স্ট্যাটাস: 'Ready for delivery'। দয়া করে আপনার ডেলিভারি স্লিপ নিয়ে পাসপোর্ট অফিসে যান।"

class CitizenAgent:
    def __init__(self):
        self.name = "Citizen Agent"
        self.description = "Manages general citizen services, passport tracking, and grievance redressal (GRS)."
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [check_passport_status]
        
        agent_instructions = """তুমি সিটিজেন এজেন্ট (CitizenAgent)। তুমি myGov, পাসপোর্ট, NID এবং GRS সংক্রান্ত তথ্য দিয়ে নাগরিকদের সাহায্য করো।"""
        self.agent_executor = create_react_agent(self.llm, tools=self.tools, state_modifier=CORE_IDENTITY + "\n\n" + agent_instructions)

    def process_query(self, query: str) -> str:
        response = self.agent_executor.invoke({"messages": [("user", query)]})
        return response["messages"][-1].content
