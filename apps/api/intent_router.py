import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from schemas import OrchestrationResponse
from agents.core_identity import CORE_IDENTITY

ROUTER_PROMPT = """তুমি KARVION BD-এর মাস্টার ইন্টেন্ট রাউটার (AI Assistant)। তোমার কাজ হলো ব্যবহারকারীর প্রশ্ন বা ইনটেন্ট (Intent) বুঝে সঠিক সাব-এজেন্টের কাছে রিকোয়েস্টটি পাঠানো।

এভেইলেবল সাব-এজেন্টগুলো হলো:
1. StudentAgent: স্কলারশিপ, উপবৃত্তি, এডমিশন, ক্যারিয়ার গাইডেন্স
2. ConsumerAgent: ভোক্তা অধিকার অভিযোগ (DNCRP ফরম্যাট), পণ্যের অতিরিক্ত দাম
3. CitizenAgent: সাধারণ নাগরিক সেবা, পাসপোর্ট, হটলাইন, myGov ও GRS
4. FarmerAgent: ফসল, রোগবালাই, সার ব্যবস্থাপনা, কৃষি প্রযুক্তি
5. MarketAgent: বাজারদর, টিসিবি রেট, পণ্যের দাম
6. WasteAgent: বর্জ্য ব্যবস্থাপনা, রিসাইক্লিং

নির্দেশনা:
- ব্যবহারকারীর প্রশ্নের ওপর ভিত্তি করে `agent_name` নির্বাচন করো।
- যদি intent পরিষ্কার হয় (confidence score 0.7 এর বেশি), তবে `requires_clarification` false রাখো এবং `next_action`-এ "Routing to {agent_name}" লেখো।
- যদি প্রশ্নটি অস্পষ্ট হয়, তবে `agent_name` "None" রাখো, `confidence_score` কমাও, `requires_clarification` true করো এবং `next_action`-এ ব্যবহারকারীকে পরিষ্কার করে প্রশ্ন করতে বলো।
- ব্যবহারকারীর প্রশ্ন থেকে প্রাসঙ্গিক তথ্য (যেমন: ঠিকানা, পণ্যের নাম, সার্ভিসের ধরন) `extracted_entities`-এ যুক্ত করো।
"""

def get_intent_router_chain():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    structured_llm = llm.with_structured_output(OrchestrationResponse)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", CORE_IDENTITY + "\n\n" + ROUTER_PROMPT),
        ("human", "User Query: {user_query}\nLocation: {location}")
    ])

    return prompt_template | structured_llm

def analyze_intent(user_query: str, location: str = None) -> OrchestrationResponse:
    chain = get_intent_router_chain()
    response = chain.invoke({
        "user_query": user_query,
        "location": location or "Unknown"
    })
    return response
