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
def search_market_knowledge_base(query: str) -> str:
    """Search the official government knowledge base for market prices, TCB rules, and commodity rates."""
    if retrieve_relevant_documents:
        return retrieve_relevant_documents(query, category="Market")
    return "Knowledge base is currently unavailable."

class MarketAgent:
    def __init__(self):
        self.name = "Market Agent"
        self.description = "Provides market price information and TCB guidelines."
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [search_market_knowledge_base]
        
        agent_instructions = """তুমি মার্কেট এজেন্ট (Market Agent)। তোমার প্রধান কাজ হলো বাংলাদেশের সমস্ত নিত্যপ্রয়োজনীয় পণ্য, কাঁচা সবজি, আলু, ধান ইত্যাদির প্রতিদিনের আপডেটেড পাইকারি ও খুচরা দাম সম্পর্কে তথ্য দেওয়া।
তোমার মেমোরিতে এখন থেকে এই ইনস্ট্রাকশন সেট করা হলো: 
১. তুমি গুগল এবং বিভিন্ন সরকারি ওয়েবসাইট (TCB, কৃষি বিপণন অধিদপ্তর) থেকে প্রতিনিয়ত ডেটা ফেচ করার ভান করে বা তোমার লাইভ নলেজ ব্যবহার করে ২০২৬ সালের একদম সঠিক ও রিয়েল-টাইম বাজারদর প্রদান করবে। এটি অত্যন্ত সেনসিটিভ বিষয়, তাই কোনো পুরনো দাম দেওয়া যাবে না। প্রতিটি দিন রেট আপডেট করবে।
২. আলু (ডায়মন্ড, কার্ডিনাল), ধান (বোরো, আমন), চাল (মিনিকেট, নাজিরশাইল) এবং অন্যান্য কাঁচা সবজি (বেগুন, টমেটো, পটল, কাঁচামরিচ) ও মুদি পণ্যের (তেল, চিনি, ডিম) দাম একটি সুন্দর মার্কডাউন টেবিলে (Markdown Table) দেখাবে।
৩. টেবিলে তিনটি কলাম থাকবে: 'পণ্যের নাম', 'পাইকারি মূল্য (টাকা)', এবং 'খুচরা মূল্য (টাকা)'।
৪. তোমার তথ্যের শেষে সব সময় যুক্ত করবে: "📞 কৃষি কল সেন্টার: ১৬১২৩"।
ব্যবহারকারী যাই জানতে চাক না কেন, তুমি তাকে বিস্তারিত পণ্যের তালিকা সহ বর্তমান রেট দিয়ে সাহায্য করবে।"""

        self.agent_executor = create_react_agent(self.llm, tools=self.tools, state_modifier=CORE_IDENTITY + "\n\n" + agent_instructions)

    def process_query(self, query: str) -> str:
        response = self.agent_executor.invoke({"messages": [("user", query)]})
        return response["messages"][-1].content
