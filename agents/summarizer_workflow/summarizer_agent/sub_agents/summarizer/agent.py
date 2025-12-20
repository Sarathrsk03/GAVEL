from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import List

# ===== PART 1: THE STATE UPDATE TOOL =====
def update_case_summary_state(
    tool_context: ToolContext,
    case_name: str,
    neutral_citation: str,
    date_of_judgment: str,
    court_name: str,
    bench: List[str],
    facts: str,
    legal_issues: List[str],
    statutes_cited: List[str],
    precedents_cited: List[str],
    ratio_decidendi: str,
    final_order: str
) -> dict:
    """Updates the internal session state with the legal data extracted."""
    tool_context.state["case_name"] = case_name
    tool_context.state["neutral_citation"] = neutral_citation
    tool_context.state["date_of_judgment"] = date_of_judgment
    tool_context.state["court_name"] = court_name
    tool_context.state["bench"] = bench
    tool_context.state["facts"] = facts
    tool_context.state["legal_issues"] = legal_issues
    tool_context.state["statutes_cited"] = statutes_cited
    tool_context.state["precedents_cited"] = precedents_cited
    tool_context.state["ratio_decidendi"] = ratio_decidendi
    tool_context.state["final_order"] = final_order

    return {
        "status": "success",
        "message": f"STATE_UPDATED: {case_name}"
    }

# ===== PART 2: THE SUMMARIZER AGENT =====
summarizer_agent = Agent(
    name="summarizer_agent",
    model="gemini-2.5-flash",
    description="Strict legal data extractor and state updater.",
    instruction="""
    YOU ARE A PRECISION LEGAL DATA EXTRACTION ENGINE. 
    YOUR SOLE MISSION IS TO ANALYZE THE PROVIDED JUDGMENT AND POPULATE THE SYSTEM STATE.

    ### INPUT DATA:
    <RAW_CASE_TEXT>
    {raw_document_text}
    </RAW_CASE_TEXT>

    <AUDITOR_FEEDBACK>
    {critique_feedback}
    </AUDITOR_FEEDBACK>

    ### EXTRACTION PROTOCOL:
    You must identify and extract exactly 12 data points from the <RAW_CASE_TEXT>:
    1.  **case_name**: Extract Petitioner vs Respondent (e.g. "Devinder Kumar Bansal vs The State Of Punjab").
    2.  **neutral_citation**: Format: YYYY INSC XXX (e.g. "2025 INSC 320").
    3.  **date_of_judgment**: The date the order was signed (e.g. "3rd March, 2025").
    4.  **court_name**: Full name of the court (e.g. "Supreme Court of India").
    5.  **bench**: List judge names (e.g. ["J.B. Pardiwala", "R. Mahadevan"]).
    6.  **facts**: Concise summary of the background and allegations.Give a list of points.
    7.  **legal_issues**: Bullet points of the legal questions being decided.
    8.  **statutes_cited**: Acts/Sections mentioned (e.g. ["Section 7 of PC Act, 1988", "Section 61(2) BNS"]).Give a list of points.
    9.  **precedents_cited**: List names of past cases referred to in the judgment.Give a list of points.
    10. **ratio_decidendi**: The core legal principle or reason for the decision.
    11. **final_order**: The actual ruling (e.g. "Petition Dismissed").

    ### OPERATIONAL CONSTRAINTS:
    - **FEEDBACK PRIORITY**: If <AUDITOR_FEEDBACK> contains corrections, you MUST apply them immediately to the new extraction.
    - **TOOL MANDATE**: You are FORBIDDEN from finishing without calling 'update_case_summary_state'.
    - **DATA INTEGRITY**: Do not hallucinate. If a field like 'neutral_citation' is missing, leave it as an empty string.

    ### EXECUTION STEPS:
    1. Scan the text for the 12 attributes listed above.
    2. Compare findings against any <AUDITOR_FEEDBACK>.
    3. Execute the 'update_case_summary_state' tool with all 12 parameters.
    """,
    tools=[update_case_summary_state],
)