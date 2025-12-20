from google.adk.agents.llm_agent import LlmAgent
from .tools import extract_pdf_with_pypdf

pdf_agent = LlmAgent(
    name="PdfReaderAgent",
    model="gemini-2.5-flash",
    instruction="""
    You are a Legal Document Transcriber.
    
    1. Call 'extract_pdf_with_pypdf' immediately.
    2. Once the tool returns 'success', verify that you can see the text in the 'raw_document_text' state.
    3. Say 'TEXT_LOADED' and stop. 
    
    Wait for the tool response before doing anything else.
    """,
    tools=[extract_pdf_with_pypdf]
)