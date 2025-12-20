import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# ADK imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import SequentialAgent
from google.genai import types

# Add current directory to sys.path to ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Agents
from draft_agent.agent import drafting_agent
from validator_agent.agent import validator_agent

load_dotenv()

app = FastAPI(title="GAVEL Draft Helper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

# Define the workflow
# The drafting agent produces a draft, then the validator agent refines it.
# We use a SequentialAgent to enforce this flow.
root_agent = SequentialAgent(
    name="draft_helper_workflow",
    description="Orchestrates the drafting and validation of legal documents.",
    sub_agents=[drafting_agent, validator_agent]
)

class DraftRequest(BaseModel):
    requirements: str
    user_context: Optional[str] = ""

from fastapi.staticfiles import StaticFiles

# ... (existing imports)

class DraftResponse(BaseModel):
    status: str
    message: str
    document_base64: Optional[str] = None
    file_name: Optional[str] = None
    download_url: Optional[str] = None

# Ensure output directory exists before mounting
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validator_agent", "output")
os.makedirs(output_dir, exist_ok=True)

# Mount the output directory to serve files
app.mount("/downloads", StaticFiles(directory=output_dir), name="downloads")

@app.get("/")
async def health_check():
    return {"status": "alive", "service": "GAVEL Draft Helper"}

@app.post("/draft", response_model=DraftResponse)
async def generate_draft(request: DraftRequest):
    try:
        APP_NAME = "DRAFT_HELPER"
        USER_ID = "default_user"
        print("running workflow")
        # Create session
        session = await session_service.create_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            state={
                "requirements": request.requirements,
                "user_context": request.user_context
            }
        )
        
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )
        
        print(f"🚀 Starting Drafting Workflow for: {request.requirements[:50]}...")
        
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=f"Draft a document with these requirements: {request.requirements}. Context: {request.user_context}")]
        )
        
        async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=user_message):
            if hasattr(event, "tool_calls"):
                for tc in event.tool_calls:
                    print(f"  [Tool]: {tc.function_call.name}")
            pass

        # Retrieve final state to check for document
        final_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session.id)
        
        if "draft_result" in final_session.state:
            result = final_session.state["draft_result"]
            file_name = result.get("file_name")
            
            # Construct download URL
            download_url = None
            if file_name:
                download_url = f"http://localhost:8013/downloads/{file_name}"

            return DraftResponse(
                status="completed",
                message="Draft generated successfully.",
                document_base64=result.get("base64_content"),
                file_name=file_name,
                download_url=download_url
            )
        
        return DraftResponse(
            status="completed", 
            message="Drafting process finished but no final document was found in state.",
            document_base64=None
        )

    except Exception as e:
        print(f"❌ Error during drafting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use a new port for this service
    uvicorn.run(app, host="0.0.0.0", port=8013)
