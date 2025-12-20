from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext

def record_audit_and_check_exit(
    tool_context: ToolContext, 
    confidence_score: float, 
    critique_feedback: str
) -> dict:
    """
    Saves the audit results. If the score is 85 or above, it exits the loop.
    """
    # [DEBUG] count of loop
    print("Loop is running ")
    # 1. Update the state
    tool_context.state["confidence_score"] = confidence_score
    tool_context.state["critique_feedback"] = critique_feedback

    # 2. Hardcoded logic to exit loop based on your constraint
    if confidence_score >= 85.0:
        print(f"--- SCORE {confidence_score} PASSED. EXITING LOOP. ---")
        tool_context.actions.escalate = True
        return {"status": "success", "message": "Threshold met. Exiting."}
    
    print(f"--- SCORE {confidence_score} FAILED. CONTINUING LOOP. ---")
    return {"status": "retry", "message": "Threshold not met. Summarizer must retry."}