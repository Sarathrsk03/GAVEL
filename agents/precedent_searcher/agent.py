from google.adk.agents.llm_agent import Agent 
from google.adk.agents import SequentialAgent
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv("/Users/sarathrajan/Desktop/hackathon/.env")

def serpSearch(searchQuery: str) -> dict:
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": searchQuery})
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()



case_breakdown_agent = Agent(
    name="Case_Breakdown_Agent",
    # Description: Focus on the output this agent produces for the next agent.
    description="Analyzes raw facts of an case to extract structured legal facts, parties involved, and core legal issues.",
    # Instruction: Step-by-step logic on how to process the input.
    instruction="""
    You are an expert Legal Clerk. Your task is to digest a natural language description of a legal situation.
    
    1. **Identify Parties**: clearly identify the Petitioner/Plaintiff and the Respondent/Defendant.
    2. **Chronology**: Extract key dates and events in chronological order.
    3. **Legal Issues**: Isolate the specific questions of law (e.g., "Violation of Article 21", "Breach of Contract under Section 73").
    4. **Output Format**: Present the extracted data in a clean, bulleted list. Do not attempt to solve the case; only structure the facts.
    """,
    model="gemini-2.5-flash", 
)   

precedent_searcher_agent = Agent(
    name="Precedent_Searcher",
    # Description: Explicitly mention the jurisdiction (India) and the tool usage.
    description="Generates search queries based on legal facts and retrieves relevant Indian Supreme Court and High Court precedents.",
    # Instruction: Teach the agent how to use the 'serpSearch' tool effectively.
    instruction="""
    You are a Legal Researcher specializing in Indian Law. You will receive a set of structured facts.
    
    1. **Formulate Queries**: Create specific search queries combining the legal issues with keywords like "Supreme Court of India", "High Court judgment", "landmark case", or "v."
    2. **Tool Usage**: Use the `serpSearch` tool to execute these queries. 
    3. **Filter**: Prioritize results from reputable sources (e.g., indiankanoon.org, casemine.com, sci.gov.in).
    4. **Output**: List the case names and a 1-sentence summary of the holding (ratio decidendi) for each found case.
    """,
    tools=[serpSearch],
    model="gemini-2.5-flash",
)

precedent_verifier_agent = Agent(
    name="Precedent_Verifier",
    # Description: Focus on quality control and citation formatting.
    description="Validates the relevance of search results against the facts and formats citations according to legal standards.",
    # Instruction: The 'Judge' persona—critical and precise.
    instruction="""
    You are a Senior Legal Associate. Your goal is quality control.
    
    1. **Verify Relevance**: Look at the cases provided by the Searcher. Do they actually apply to the facts extracted by the Breakdown Agent?
    2. **Check Overruling**: If possible, use the search tool to ensure the judgment hasn't been overruled.
    3. **Formatting**: formatting the final output. Ensure every case includes a proper citation (e.g., "AIR 1973 SC 1461").
    4. **Final Deliverable**: Produce a final memo summarizing the best 3 precedents that support the user's case.
    """,
    tools=[serpSearch],
    model="gemini-2.5-flash", 
)

root_agent = SequentialAgent(
    name = "precedent_searcher_agent",
    sub_agents= [case_breakdown_agent, precedent_searcher_agent, precedent_verifier_agent],
)