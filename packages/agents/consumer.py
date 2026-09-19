import os
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api")))
try:
    from rag.retrieve import retrieve_relevant_documents
except ImportError:
    retrieve_relevant_documents = None

from agents.core_identity import CORE_IDENTITY

# Setup Jinja2 Environment
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

@tool
def search_consumer_guidelines(query: str) -> str:
    """Search the official government knowledge base for consumer rights (DNCRP) guidelines, rules, and procedures."""
    if retrieve_relevant_documents:
        return retrieve_relevant_documents(query, category="Consumer")
    return "Knowledge base is currently unavailable."

class ConsumerAgent:
    def __init__(self):
        self.name = "Consumer Agent"
        self.description = "Assists consumers with filing complaints to DNCRP regarding fraud, adulteration, or overpricing."
        
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [search_consumer_guidelines]
        
        agent_instructions = """তুমি কনজিউমার এজেন্ট (Consumer Agent)। 
তোমার প্রধান কাজ হলো ভোক্তা অধিকার সংরক্ষণ অধিদপ্তরে (DNCRP) অভিযোগ করার বিষয়ে সঠিক তথ্য প্রদান করা।
যদি কেউ প্রতারণা, অতিরিক্ত মূল্য বা ভেজাল পণ্য সম্পর্কে অভিযোগ করতে চায়, তুমি সরাসরি তাকে অভিযোগ করার নিয়ম এবং ড্রাফট সম্পর্কে জানাবে।
অবশ্যই তোমার গাইডেন্সের শেষে উল্লেখ করবে: "📞 ভোক্তা অধিকার সংরক্ষণ: ১৬১২১"
"""
        
        self.agent_executor = create_react_agent(self.llm, tools=self.tools, state_modifier=CORE_IDENTITY + "\n\n" + agent_instructions)

    def process_query(self, query: str) -> str:
        response = self.agent_executor.invoke({"messages": [("user", query)]})
        return response["messages"][-1].content
