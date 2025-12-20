import os
import io
import base64
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pypdf import PdfReader
from dotenv import load_dotenv

# ADK imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Local imports
from agent import root_agent
from tools import set_current_doc_text

load_dotenv()

app = FastAPI(title="GAVEL Forgery Checker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

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

def extract_text(request: VerifyRequest) -> str:
    """Extracts text from PDF or Image."""
    content = base64.b64decode(request.base64_data)
    
    if "pdf" in request.mime_type.lower():
        try:
            reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    else:
        # For images, we could use Gemini to OCR, but for now we'll return a placeholder 
        # or implement a quick OCR if possible. 
        # Actually, let's use a simple OCR approach if we can, or just tell the user 
        # that text extraction from images is handled by the model directly if possible.
        # But our ML tool NEEDS text.
        return "[Image Content - Forensic scanning in progress]"

@app.post("/verify", response_model=VerificationResult)
async def verify_document(request: VerifyRequest):
    try:
        # 1. Extract Text
        doc_text = extract_text(request)
        if not doc_text and "pdf" in request.mime_type.lower():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
        
        
        # 3. Setup ADK Runner
        APP_NAME = "FORGERY_CHECKER"
        USER_ID = "default_user"
        
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )
        
        # 4. Run Analysis
        # We pass the file as well if it's an image so Gemini can see it even if our ML tool only uses text
        parts = [types.Part(text=f"Please analyze this document: {request.file_name}. Use your tools to perform a deep forensic check.")]
        
        # If it's an image, include it in the parts for Gemini's multi-modal capability
        if "image" in request.mime_type.lower() or "pdf" in request.mime_type.lower():
            parts.append(types.Part(inline_data=types.Blob(mime_type=request.mime_type, data=request.base64_data)))

        user_message = types.Content(role="user", parts=parts)
        
        # We'll create a new session for each request with document context
        session = await session_service.create_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            state={"document_text": doc_text}
        )
        
        async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=user_message):
            pass  # Just ensure it runs to completion
        
        
        # 5. Fetch Final State
        final_session = await session_service.get_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=session.id
        )
        
        if "forgery_result" in final_session.state:
            result_data = final_session.state["forgery_result"]
            return VerificationResult(**result_data)
        
        # Fallback if tool wasn't called
        return VerificationResult(
            authenticityScore=50.0,
            anomalies=[Anomaly(id="err", title="Analysis Failure", description="Agent did not finalize analysis.", severity="high")]
        )

    except Exception as e:
        print(f"Verification Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
