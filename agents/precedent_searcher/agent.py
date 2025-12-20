from google.adk.agents.llm_agent import Agent 
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
import requests
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv("/Users/sarathrajan/Desktop/hackathon/.env")


def initialize_precedent_state(facts: str):
    """Initializes the session state for precedent search."""
    return {
        "raw_facts": facts,
        "parties": {"Petitioner": "", "Respondent": ""},
        "chronology": [],
        "legal_issues": [],
        "precedents": [],
        "legal_memo": "",
        "interaction_history": []
    }


def update_precedent_state(
    tool_context: ToolContext,
    petitioner: str = None,
    respondent: str = None,
    chronology: List[str] = None,
    legal_issues: List[str] = None,
    precedents_json: str = None,
    legal_memo: str = None
) -> dict:
    """Updates the internal session state with the legal data extracted."""
    print(f"🛠️ Tool called:")
    if petitioner: print(f"  - pet: {petitioner}")
    if respondent: print(f"  - res: {respondent}")
    if legal_issues: print(f"  - issues: {len(legal_issues)}")
    if precedents_json: print(f"  - precedents_json length: {len(precedents_json)}")
    if legal_memo: print(f"  - legal_memo length: {len(legal_memo)}")
    
    # Use top-level assignment to ensure ADK tracks the state change
    if petitioner or respondent:
        new_parties = tool_context.state.get("parties", {"Petitioner": "", "Respondent": ""}).copy()
        if petitioner:
            new_parties["Petitioner"] = petitioner
        if respondent:
            new_parties["Respondent"] = respondent
        tool_context.state["parties"] = new_parties
        
    if chronology:
        tool_context.state["chronology"] = chronology
    if legal_issues:
        tool_context.state["legal_issues"] = legal_issues
    if precedents_json:
        try:
            tool_context.state["precedents"] = json.loads(precedents_json)
        except Exception as e:
            print(f"Error parsing precedents JSON: {e}")
            return {"status": "error", "message": f"INVALID_JSON: {e}"}
            
    if legal_memo:
        tool_context.state["legal_memo"] = legal_memo

    return {
        "status": "success",
        "message": "STATE_UPDATED"
    }


case_breakdown_agent_description = """
Comprehensive analysis of unstructured information (documents, transcripts, reports) 
to extract factual elements, identify all parties, and pinpoint central legal issues.
"""

case_breakdown_agent_instruction = """
### ROLE: Highly experienced Legal Clerk.

### OBJECTIVE:
Accurately and systematically extract, structure, and present factual information from the input.

### INPUT:
{raw_facts}

### TOOL MANDATE:
You MUST call 'update_precedent_state' before finishing.

### EXECUTION STEPS:
1. **Parties Identification**: Identify Petitioner/Plaintiff and Respondent/Defendant.
2. **Chronological Order**: Extract all dates and events and present them in strict order.
3. **Legal Issue Identification**: Analyze questions of law at the heart of the situation.
4. **STATE UPDATE**: Execute 'update_precedent_state' with the following parameters:
   - petitioner: [Name]
   - respondent: [Name]
   - chronology: [List of strings mapping to the chronology]
   - legal_issues: [List of articulated legal questions]

### DESCRIPTIVE GUIDELINES:
- Focus on Facts. Do not interpret the law or provide opinions.
- Accuracy and Conciseness are paramount.
"""


precedent_searcher_agent_description = """
Generates search queries based on legal facts and retrieves relevant Indian Supreme Court 
and High Court precedents using structured case metadata.
"""

precedent_searcher_agent_instruction = """
### ROLE: Expert Legal Researcher specializing in Indian Jurisprudence.

### OBJECTIVE:
Retrieve authoritative Indian legal precedents addressing the core legal issues.

### INPUT:
Facts: {raw_facts}
Parties: {parties}
Issues: {legal_issues}

### TOOL MANDATE:
You MUST call 'update_precedent_state' before finishing.

### EXECUTION STEPS:
1. **Query Construction**: Construct queries using keywords like "Supreme Court of India", "v.", and the specific issues.
2. **Search**: Use 'serpSearch' to find judgments on indiankanoon.org, casemine.com, etc.
3. **Case Selection**: Identify cases where the ratio decidendi is directly applicable.
4. **Summarization**: For top 3-5 cases, create structured objects:
   - title: [Case Name]
   - citation: [Legal Citation, e.g., AIR 2023 SC 1]
   - matchScore: [Integer 0-100]
   - summary: [Brief legal core/ratio]
   - tags: [List of keywords]
5. **STATE UPDATE**: Convert the list of objects into a JSON string and execute 'update_precedent_state' using the 'precedents_json' parameter.
"""

precedent_verifier_agent_description = """
Validates search results against facts, formats citations according to legal standards (AIR, SCC, SCR), 
and drafts a formal research memorandum.
"""

precedent_verifier_agent_instruction = """
### ROLE: Senior Legal Associate specializing in Indian Jurisprudence.

### OBJECTIVE:
Validate, verify, and format precedents to ensure they are relevant and accurately cited.

### INPUT:
Facts: {raw_facts}
Parties: {parties}
Issues: {legal_issues}
Precedents: {precedents}

### SYSTEM MANDATE:
You MUST call 'update_precedent_state' to save the final memo and refined precedents.

### EXECUTION STEPS:
1. **Relevance Assessment**: Critically evaluate cases against "Core Legal Issues". Discard irrelevant ones.
2. **Validity Verification**: Use 'serpSearch' to ensure judgments haven't been overruled ("good law").
3. **Citation Standardization**: Format citations (e.g., AIR 1973 SC 1461).
4. **Memo Drafting**: Produce a formal "Legal Research Memo" summarizing the top 3 precedents.
5. **STATE UPDATE**: Execute 'update_precedent_state' with:
   - precedents_json: [The refined JSON list of cases]
   - legal_memo: [The full text of the Research Memo]

### CONSTRAINTS:
- Focus exclusively on Indian Law.
- Maintain a professional, analytical tone.
"""


legal_memo_agent_description = """
Generates a legal research memorandum based on the provided precedents.
"""

legal_memo_agent_instruction = """
### ROLE: Senior Legal Associate specializing in Indian Jurisprudence.

### OBJECTIVE:
Generate a legal research memorandum based on the provided precedents.

### INPUT:
Facts: {raw_facts}
Parties: {parties}
Issues: {legal_issues}
Precedents: {precedents}

### SYSTEM MANDATE:
You MUST call 'update_precedent_state' to save the final memo and refined precedents.

### EXECUTION STEPS:
1. **Memo Drafting**: Produce a formal "Legal Research Memo" summarizing the top 3 precedents.
2. **STATE UPDATE**: Execute 'update_precedent_state' with:
   - legal_memo: [The full text of the Research Memo]
"""

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
    description=case_breakdown_agent_description,
    instruction=case_breakdown_agent_instruction,
    tools=[update_precedent_state],
    model="gemini-2.5-flash", 
)   

precedent_searcher_agent = Agent(
    name="Precedent_Searcher",
    description=precedent_searcher_agent_description,
    instruction=precedent_searcher_agent_instruction,
    tools=[serpSearch, update_precedent_state],
    model="gemini-2.5-flash", 
)

precedent_verifier_agent = Agent(
    name="Precedent_Verifier",
    description=precedent_verifier_agent_description,
    instruction=precedent_verifier_agent_instruction,
    tools=[serpSearch, update_precedent_state],
    model="gemini-2.5-flash", 
)

legal_memo_agent = Agent(
    name="Legal_Memo_Agent",
    description=legal_memo_agent_description,
    instruction=legal_memo_agent_instruction,
    tools=[update_precedent_state],
    model="gemini-2.5-flash", 
)  

root_agent = SequentialAgent(
    name = "precedent_searcher_agent",
    sub_agents= [case_breakdown_agent, precedent_searcher_agent, precedent_verifier_agent, legal_memo_agent],
)