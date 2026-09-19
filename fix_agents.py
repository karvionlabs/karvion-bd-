import os
import glob
import re

agent_files = glob.glob("packages/agents/*.py")

for fpath in agent_files:
    if "__init__" in fpath: continue
    
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace imports
    content = content.replace("from langchain.agents import create_tool_calling_agent, AgentExecutor", "from langgraph.prebuilt import create_react_agent")
    content = content.replace("from langchain_core.prompts import ChatPromptTemplate\n", "")
    
    # We need to extract the system prompt to use it as state_modifier
    sys_prompt_match = re.search(r'\("system", "(.*?)"\),', content, re.DOTALL)
    if not sys_prompt_match:
        continue
    system_prompt = sys_prompt_match.group(1)
    
    # Replace the init body from `prompt = ...` down to `self.agent_executor = ...`
    init_replace_regex = r'prompt = ChatPromptTemplate.*?self\.agent_executor = AgentExecutor\(agent=agent, tools=self\.tools, verbose=True\)'
    
    new_init = f'self.agent_executor = create_react_agent(self.llm, tools=self.tools, state_modifier="{system_prompt}")'
    content = re.sub(init_replace_regex, new_init, content, flags=re.DOTALL)
    
    # Replace process_query method body
    process_regex = r'response = self\.agent_executor\.invoke\(\{"input": query\}\)\s*return response\["output"\]'
    new_process = 'response = self.agent_executor.invoke({"messages": [("user", query)]})\n        return response["messages"][-1].content'
    content = re.sub(process_regex, new_process, content)
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Fixed all agent files.")
