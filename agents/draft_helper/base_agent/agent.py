from google.adk.agents.llm_agent import Agent 
#from google.adk.agents import LoopAgent
from google.adk.agents import SequentialAgent
#from .tools import contracts_agreements, writ_template, civil_litigation, criminal_litigation, family_law, commercial_templates,criminal_or_civil_litigation
# Correct import
from validator_agent import validator_agent as validator_agent
from draft_agent import drafting_agent as drafting_agent
from dotenv import load_dotenv
load_dotenv()



root_agent = SequentialAgent(
    name="draft_agent",
    description="Drafts legal documents using the drafting_agent and validator_agent",
    #max_iterations=1,
    sub_agents=[drafting_agent, validator_agent],
    #termination_condition=termination_condition
)