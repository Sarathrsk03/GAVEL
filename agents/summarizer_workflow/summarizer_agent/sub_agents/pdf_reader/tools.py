import os
from pypdf import PdfReader
from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext

def extract_pdf_with_pypdf(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Extracts text from a PDF file using the pypdf library.
    """
    # 1. Get path from state
    file_path = tool_context.state.get("file_path")
    print(f"\n🔍 [pypdf] Attempting extraction from: {file_path}")
    
    if not file_path or not os.path.exists(file_path):
        return {"status": "error", "message": f"File not found: {file_path}"}

    try:
        # 2. Initialize Reader
        reader = PdfReader(file_path)
        full_text = ""
        number_of_pages = len(reader.pages)
        page = reader.pages[0]
        text = page.extract_text()
        # # 3. Loop through pages and extract
        # for i, page in enumerate(reader.pages):
        #     page_content = page.extract_text()
        #     if page_content:
        #         full_text += f"\n{page_content}"
        
        # clean_text = full_text.strip()
        clean_text = text


        # 4. Check if we actually got anything
        if not clean_text:
            print("⚠️ [pypdf] No text found. PDF might be a scan/image.")
            return {"status": "error", "message": "pypdf could not find any text layers."}

        # 5. COMMIT TO STATE
        tool_context.state["raw_document_text"] = clean_text
        
        print(f"✅ [pypdf] Success! Extracted {len(clean_text)} characters.")
        
        return {
            "status": "success",
            "message": f"Extracted {len(clean_text)} characters from {len(reader.pages)} pages.",
            "preview": clean_text[:100]
        }

    except Exception as e:
        print(f"❌ [pypdf] Error: {str(e)}")
        return {"status": "error", "message": f"pypdf failed: {str(e)}"}