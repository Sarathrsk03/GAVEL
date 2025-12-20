import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import your helper functions
from utils import initialize_legal_state, extract_text_from_pdf
from summarizer_agent.agent import root_agent # This should now be the LoopAgent

load_dotenv()

async def main_async():
    # ===== PART 1: SETUP =====
    APP_NAME = "GAVEL_SUMMARIZER"
    USER_ID = "hackathon_user"
    session_service = InMemorySessionService()

    # ===== PART 2: MANUAL EXTRACTION =====
    # Define your path here
    PATH_TO_PDF = r"D:\\Agentathon\\GAVEL-1\\agents\\summarizer_workflow\\data\\test_pdf.pdf"
    
    print(f"⏳ Extracting text from: {PATH_TO_PDF}...")
    pdf_text = extract_text_from_pdf(PATH_TO_PDF)

    if not pdf_text:
        print("❌ Extraction failed or PDF is empty. Exiting.")
        return
    
    print(f"✅ Extracted {len(pdf_text)} characters.")

    # ===== PART 3: INITIALIZE STATE =====
    # We pass the extracted text directly into the state
    initial_state = initialize_legal_state(pdf_text)
    # ===== PART 3: Session Creation =====
    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"⚖️ GAVEL-1: Session Created: {SESSION_ID}")

    # ===== PART 4: Runner Setup =====
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # ===== PART 5: Execution =====
    print("\n🚀 Starting Legal Analysis Workflow...")
    
    user_message = types.Content(
        role="user",
        parts=[types.Part(text="Extract legal data and verify the summary.")]
    )

    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=user_message
        ):
            # Print agent transitions to show progress
            if hasattr(event, 'agent_name'):
                print(f"  [Active Agent]: {event.agent_name}")
            
            if event.is_final_response():
                print("\n✅ Workflow Chain Finished.")
                
    except Exception as e:
        print(f"\n❌ Workflow Error (Likely Rate Limit): {e}")

    # ===== PART 6: Final Results & Loop Count =====
    final_session = await session_service.get_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )

    # # Calculate loop iterations by checking how many times the worker started
    # # In ADK history, each turn is recorded.
    # loop_count = len([t for t in final_session.history if t.role == "model"]) // 2
    # if loop_count == 0: loop_count = 1 # Minimum of 1 pass

    # print("\n" + "="*60)
    # print(f"📊 FINAL LEGAL SUMMARY STATE (Total Loops: {loop_count})")
    # print("="*60)
    
    # All 12 Legal Fields
    all_fields = [
        "case_name", "neutral_citation", "date_of_judgment", 
        "court_name", "bench", "facts", "legal_issues", 
        "statutes_cited", "precedents_cited", "ratio_decidendi", 
        "final_order", "confidence_score"
    ]
    
    for key in all_fields:
        val = final_session.state.get(key)
        # Format list displays for statutes/precedents
        if isinstance(val, list):
            val = ", ".join(val) if val else "NONE"
        
        status = "✅" if (val and val != "EMPTY" and val != 0.0) else "❌"
        print(f"{status} {key.upper():<20}: {val}")
        
    print("="*60)
    print(f"CRITIQUE FEEDBACK: {final_session.state.get('critique_feedback', 'No feedback provided.')}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main_async())