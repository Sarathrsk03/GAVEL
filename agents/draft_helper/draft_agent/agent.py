from google.adk.agents.llm_agent import Agent 
from google.adk.agents.llm_agent import LoopAgent
from .tools import contracts_agreements, writ_template, civil_litigation, criminal_litigation, family_law, commercial_templates,criminal_or_civil_litigation
#from validator_agent import validator_agent
from dotenv import loadenv
loadenv()

root_agent = Agent(
    name = "draft_agent",
    description = "Drafts a contract based on the user's input",
    model = "gemini-2.5-flash",
    instruction = "You are a contract draft assistant. You will be given a requirement and you need to draft a contract based on that domain.",
    tools = [contracts_agreements, writ_template, civil_litigation, criminal_litigation, family_law, commercial_templates,criminal_or_civil_litigation],
    
)