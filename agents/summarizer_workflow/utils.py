from datetime import datetime
from google.genai import types


def initialize_legal_state(raw_text:str):
    """Initializes the session state with placeholders for the judgment schema."""
    return {
        "file_path":"",
        "raw_document_text": raw_text,
        "interaction_history": [],
        # Schema Fields
        "case_name": "",
        "neutral_citation": "",
        "date_of_judgment": "",
        "court_name": "",
        "bench": [],
        "facts": [],
        "legal_issues": [],
        "statutes_cited": [],
        "precedents_cited": [],
        "ratio_decidendi": "",
        "final_order": "",
        # Control Fields
        "confidence_score": 0.0,
        "critique_feedback": ""
    }


# Note: In 'display_state', update the print logic to show 'case_name' instead of 'user_name'.

import os
from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """
    Standard Python function to extract text using pypdf.
    No agents involved here, just direct extraction.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return ""

    try:
        reader = PdfReader(file_path)
        extracted_text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                extracted_text += content + "\n"
        
        return extracted_text.strip()
    except Exception as e:
        print(f"❌ pypdf Error: {e}")
        return ""