import os
from google.adk.agents import LoopAgent, SequentialAgent

# Import your sub-agents
# (Assuming these are defined in their respective sub-folders)
from .sub_agents.summarizer.agent import summarizer_agent
from .sub_agents.critique_agent.agent import critique_agent
from .sub_agents.pdf_reader.agent import pdf_agent

# 1. THE REFINEMENT LOOP
# This loop contains the worker (Summarizer) and the auditor (Critique Agent).
# It will keep running until the Critique Agent calls the 'exit_loop' tool.
refinement_loop = LoopAgent(
    name="LegalRefinementLoop",
    # We do NOT use termination_condition here because we will 
    # use tool_context.actions.escalate = True inside the Critique Agent.
    sub_agents=[
        summarizer_agent, 
        critique_agent
    ],
    max_iterations=3, # Safety limit to prevent infinite loops
    description="Iteratively extracts legal data and critiques it until quality standards are met."
)

# 2. THE ROOT AGENT (The Orchestrator)
# This is the main entry point for your Runner in main.py.
root_agent = SequentialAgent(
    name="GavelLegalSummarizerPipeline",
    sub_agents=[
        pdf_agent,
        refinement_loop, 
    ],
    description="The main pipeline for GAVEL: Legal Document Summarizer."
)