import glob
import re

agent_files = glob.glob("packages/agents/*.py")

for fpath in agent_files:
    if "__init__" in fpath: continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find state_modifier="..." and replace with state_modifier="""..."""
    # Using regex to capture everything inside the string
    def replacer(match):
        inner = match.group(1)
        # Avoid double escaping or triple quoting if already done
        if inner.startswith('""') or inner.startswith("''"):
            return match.group(0)
        return f'state_modifier="""{inner}""")'

    content = re.sub(r'state_modifier="(.*?)"\)', replacer, content, flags=re.DOTALL)
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)

print("Fixed triple quotes in state_modifier.")
