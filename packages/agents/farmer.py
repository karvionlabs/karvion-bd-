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
def search_farmer_knowledge_base(query: str) -> str:
    """Search the official government knowledge base for agricultural information, crop diseases, and farming guidelines."""
    if retrieve_relevant_documents:
        return retrieve_relevant_documents(query, category="Farmer")
    return "Knowledge base is currently unavailable."

class FarmerAgent:
    def __init__(self):
        self.name = "Farmer Agent"
        self.description = "Assists farmers with crop diseases, fertilizers, and agricultural technology."
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [search_farmer_knowledge_base]
        
        agent_instructions = """তুমি ফার্মার এজেন্ট (Farmer Agent)। তোমার কাজ হলো বাংলাদেশের কৃষকদের ফসলের রোগবালাই, সার ব্যবস্থাপনা এবং আধুনিক কৃষি প্রযুক্তি সম্পর্কে সঠিক তথ্য দেওয়া।
সর্বদা IPM (Integrated Pest Management) পদ্ধতিকে অগ্রাধিকার দেবে এবং ক্ষতিকর কীটনাশকের ব্যবহার কমানোর পরামর্শ দেবে।
তোমার প্রতিটি গাইডেন্সের শেষে এই লাইনটি যুক্ত করবে: "📞 কৃষি কল সেন্টার: ১৬১২৩"
"""

        self.agent_executor = create_react_agent(self.llm, tools=self.tools, state_modifier=CORE_IDENTITY + "\n\n" + agent_instructions)

    def process_query(self, query: str) -> str:
        response = self.agent_executor.invoke({"messages": [("user", query)]})
        return response["messages"][-1].content
