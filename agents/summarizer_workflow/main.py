import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import your helper functions
from utils import initialize_legal_state, extract_text_from_pdf
from summarizer_agent.agent import root_agent

load_dotenv()

app = FastAPI(title="GAVEL Summarizer API")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session service
session_service = InMemorySessionService()

# Pydantic models for Verification
class Anomaly(BaseModel):
    id: str
    title: str
    description: str
    severity: str

class VerificationResult(BaseModel):
    authenticityScore: float
    anomalies: List[Anomaly]

class VerifyRequest(BaseModel):
    file_name: str
    mime_type: str
    base64_data: str


@app.get("/")
async def health_check():
    return {"status": "alive", "service": "GAVEL Summarizer"}

@app.post("/verify", response_model=VerificationResult)
async def verify_document(request: VerifyRequest):
    """
    Analyze document for forensic authenticity and potential fraud.
    """
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = """Analyze the attached legal document for forensic authenticity and potential fraud. 
        Perform the following checks:
        1. Look for logical inconsistencies in dates, names, or addresses.
        2. Examine the document for unusual phrasing, grammatical anomalies, or signs of "copy-paste" template mixing.
        3. Identify any contradictory clauses or legal loopholes.
        4. If it's an image, look for visual artifacts that might suggest digital alteration of text or signatures.
        
        Provide a JSON response with an "authenticityScore" (0-100) and an array of "anomalies" each with "id", "title", "description", and "severity" (high, medium, low)."""

        response = model.generate_content([
            {'mime_type': request.mime_type, 'data': request.base64_data},
            prompt
        ], generation_config={"response_mime_type": "application/json"})
        
        import json
        return json.loads(response.text)

    except Exception as e:
        print(f"❌ Error during verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")

async def summarize_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and get a legal summary.
    This endpoint processes the document using ADK agents.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save uploaded file to a temporary location to pass to the extractor
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # ===== PART 1: EXTRACT TEXT =====
        print(f"⏳ Processing upload: {file.filename}...")
        pdf_text = extract_text_from_pdf(tmp_path)

        if not pdf_text:
            raise HTTPException(status_code=400, detail="PDF extraction failed or document is empty.")
        
        print(f"✅ Extracted {len(pdf_text)} characters.")

        # ===== PART 2: SETUP ADK SESSION =====
        APP_NAME = "GAVEL_SUMMARIZER"
        USER_ID = "fastapi_default_user"
        
        initial_state = initialize_legal_state(pdf_text)
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"⚖️ Session Created: {SESSION_ID}")

        # ===== PART 3: RUN WORKFLOW =====
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        print("🚀 Starting Legal Analysis Workflow...")
        
        user_message = types.Content(
            role="user",
            parts=[types.Part(text="Extract legal data and verify the summary.")]
        )

        # Run the workflow to completion
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=user_message
        ):
            # (Optional) Log events or transitions
            if hasattr(event, 'agent_name'):
                print(f"  [Agent]: {event.agent_name}")
            
            if event.is_final_response():
                print("✅ Workflow Finished.")

        # ===== PART 4: FETCH & RETURN RESULTS =====
        final_session = await session_service.get_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=SESSION_ID
        )

        # Remove the raw text from response if it's too large, or keep it as per requirement
        # Here we return the full status for the frontend
        return {
            "session_id": SESSION_ID,
            "summary": final_session.state
        }

    except Exception as e:
        print(f"❌ Error during summarize: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    # Use standard uvicorn entry point
    uvicorn.run(app, host="0.0.0.0", port=8010)