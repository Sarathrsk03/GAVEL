import os
import logging
import warnings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Suppress the "non-text parts" warning from google-genai
warnings.filterwarnings("ignore", message=".*non-text parts.*")
logging.getLogger("google.genai").setLevel(logging.ERROR)

# Import agents and state from agent.py
from agent import root_agent, initialize_precedent_state

load_dotenv("/Users/sarathrajan/Desktop/hackathon/.env")

app = FastAPI(title="GAVEL Precedent Searcher API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session service
session_service = InMemorySessionService()

class SearchRequest(BaseModel):
    facts: str

@app.get("/")
async def health_check():
    return {"status": "alive", "service": "GAVEL Precedent Searcher"}

@app.post("/search")
async def search_precedents(request: SearchRequest):
    """
    Examine facts and search for relevant Indian legal precedents.
    """
    if not request.facts:
        raise HTTPException(status_code=400, detail="Facts are required for searching.")

    try:
        APP_NAME = "GAVEL_PRECEDENT_SEARCHER"
        USER_ID = "fastapi_default_user"
        
        # Initialize state with the provided facts
        initial_state = initialize_precedent_state(request.facts)
        
        # Create an ADK session
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"⚖️ Session Created: {SESSION_ID}")

        # Setup the Runner
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        print(f"🚀 Starting Precedent Search Pipeline...")
        
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=f"Process these facts: {request.facts}")]
        )

        # Run the workflow
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=user_message
        ):
            if hasattr(event, 'agent_name'):
                print(f"  [Active Agent]: {event.agent_name}")
            
            # Log tool calls for transparency
            if hasattr(event, 'tool_calls') and event.tool_calls:
                for tc in event.tool_calls:
                    print(f"    [Tool Call]: {tc.function_call.name}")
            
            if event.is_final_response():
                text = getattr(event, 'text', 'Final execution reached.')
                print(f"✅ Pipeline execution finished: {text[:50]}...")

        # Fetch the updated session to get the result state
        final_session = await session_service.get_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=SESSION_ID
        )

        # Flatten the response to match the React CopilotResponse interface
        return {
            **final_session.state,
            "session_id": SESSION_ID,
            "status": "completed"
        }

    except Exception as e:
        print(f"❌ Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
