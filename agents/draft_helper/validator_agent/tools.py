import os
import glob
from typing import Optional, Dict, List
from fuzzywuzzy import fuzz 
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

import os
from datetime import datetime
import re


# Suppress tokenizer parallelism warning (must be set before loading transformers)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def extract_username_from_document(markdown_text: str) -> str:
    """
    Extract a primary party/entity name from the legal document
    to be used as 'user_name' in filenames.
    """

    patterns = [
        # Between X and Y
        r"between\s+([A-Z][a-zA-Z\s]+?)\s+and\s+[A-Z][a-zA-Z\s]+",

        # Party A
        r"Party\s*A\s*[:\-]\s*([A-Z][a-zA-Z\s]+)",

        # Plaintiff / Petitioner
        r"(?:Plaintiff|Petitioner)\s*[:\-]\s*([A-Z][a-zA-Z\s]+)",

        # Client
        r"Client\s*[:\-]\s*([A-Z][a-zA-Z\s]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, markdown_text, re.IGNORECASE)
        if match:
            return sanitize_filename(match.group(1).strip().replace(" ", "_"))

    return "Unknown_Party"

def sanitize_filename(s: str) -> str:
    """Remove invalid filename characters"""
    return re.sub(r'[\\/*?:"<>|]', "_", s)

def generate_draft_filename(output_dir: str, user_name: str, template_name: str) -> str:
    """
    Generate a descriptive filename like:
    2025-12-20_19-50-45_John_Doe_Marital_Settlement_Agreement.docx
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    user_name_clean = sanitize_filename(user_name.replace(" ", "_"))
    template_clean = sanitize_filename(template_name.replace(" ", "_"))

    filename = f"{timestamp}_{user_name_clean}_{template_clean}.docx"
    return os.path.join(output_dir, filename)




# Global variables for caching model and index
_model = None
_index = None
_metadata = None

def _load_resources():
    """Lazily load resources."""
    global _model, _index, _metadata
    
    # __file__ is inside validator_agent
    # dirname -> validator_agent
    # dirname -> draft_helper
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    index_path = os.path.join(base_dir, "kanoon_faiss_index.bin")
    metadata_path = os.path.join(base_dir, "kanoon_metadata.json")

    if _model is None:
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')

    if _index is None or _metadata is None:
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            print("Loading FAISS index and metadata...")
            _index = faiss.read_index(index_path)
            with open(metadata_path, 'r') as f:
                # Keys in JSON are strings, convert to int for faiss mapping if needed
                # But here we just need to look up by ID
                _metadata = json.load(f)
        else:
            print(f"Index or metadata not found at {base_dir}")
            return False
            
    return True

def RAG_tool(query_text: str,_called=False) -> Optional[Dict]:
    """
    This tool leverages Retrieval-Augmented Generation (RAG) to analyze precedent cases
    that are contextually similar to the current draft.

    Based on the identified precedents, it evaluates the draft to determine whether
    any sections require refinement, correction, or enhancement.

    Where necessary, the draft is revised to align with the language, structure,
    and legal formulation commonly used in comparable precedent cases.
    Explicit references to the precedent cases are not included in the final output.
    
    Args:
        query_text (str): The text to search for similar cases.
        top_k (int): Number of top results to return.
    
    Returns:
        Dict: A dictionary containing the top similar cases and their text.
    """
    top_k= 2
    print("IN RAG")
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    if not _load_resources():
        return {"error": "RAG resources not found."}

    try:
        query_embedding = _model.encode([query_text])
        distances, indices = _index.search(np.array(query_embedding).astype('float32'), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                # Convert idx to string for finding in metadata json keys
                meta = _metadata.get(str(idx))
                if meta:
                    results.append({
                        "id": meta["id"],
                        "source": meta["source"],
                        "text": meta["text"],
                        "distance": float(distances[0][i])
                    })
        
        return {"results": results}
        
    except Exception as e:
        print("Error in RAG: ",e)
        return {"error": str(e)}

from google.adk.tools.tool_context import ToolContext



def termination_condition(tool_context: ToolContext) -> Optional[Dict]:
    """
    Determines whether the loop agent should terminate execution.

    The loop terminates when the draft has been validated successfully
    and no further revisions are required. This function is evaluated
    at the end of each iteration by the LoopAgent.

    Termination Criteria:
    - A validated draft exists
    - The validator has explicitly marked the draft as final
    - No pending issues, corrections, or feedback remain

    Args:
        state (Dict): The shared loop state containing intermediate
                      drafts, validation results, and flags set by agents.

    Returns:
        Optional[Dict]:
            - If termination conditions are met, returns a dictionary
              indicating successful completion and the final draft.
            - If not met, returns None to continue looping.
    """
    print("IN TERMINATION CONDITION")
    tool_context.actions.escalate = True

    return None



def extract_template_name_from_markdown(markdown_text: str) -> str:
    """
    Extracts the document title (template name) from Markdown.
    Falls back to 'Legal_Draft' if no title is found.
    """
    # Match first Markdown H1 heading
    match = re.search(r'^#\s+(.+)', markdown_text, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return "Legal_Draft"


import os
import base64
from typing import Optional, Dict
import pypandoc


from google.adk.tools.tool_context import ToolContext

def markdown_to_docx(tool_context: ToolContext, markdown_text: str) -> Optional[Dict]:
    """
    Converts Markdown content into a Word (.docx) document stored in the
    agent\draft_helper\output folder and returns the document content as Base64.

    Args:
        markdown_text (str): Markdown formatted content.

    Returns:
        Optional[Dict]: Base64-encoded Word document and metadata.
    """
    # Fixed output folder inside the agent structure
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "output"
    )

    os.makedirs(output_dir, exist_ok=True)

    # Create a unique file name
    user_name = extract_username_from_document(markdown_text)
    template_name = extract_template_name_from_markdown(markdown_text)
    output_path = generate_draft_filename(output_dir, user_name, template_name)

    # Convert Markdown → DOCX
    # Note: Ensure pandoc is installed. If pypandoc fails, this will raise error.
    try:
        pypandoc.convert_text(
            markdown_text,
            to="docx",
            format="md",
            outputfile=output_path,
            extra_args=["--standalone"]
        )
    except OSError:
        # Check if it's a missing binary issue and try to download
        print("Pandoc not found. Attempting to download...")
        try:
            #pypandoc.download_pandoc()
            # Retry conversion
            pypandoc.convert_text(
                markdown_text,
                to="docx",
                format="md",
                outputfile=output_path,
                extra_args=["--standalone"]
            )
        except Exception as e:
            print(f"Pandoc download/retry failed: {e}")
            return {"error": f"Pandoc missing and download failed: {str(e)}"}
    except Exception as e:
        print(f"Pandoc conversion failed: {e}")
        return {"error": str(e)}

    # Check if file exists and encode
    if not os.path.exists(output_path):
        return None

    with open(output_path, "rb") as f:
        encoded_doc = base64.b64encode(f.read()).decode("utf-8")

    result = {
        "type": "docx",
        "file_name": os.path.basename(output_path),
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "base64_content": encoded_doc
    }
    
    # Save to state for retrieval by main.py
    tool_context.state["draft_result"] = result
    print("Got result from markdown: ",result)
    
    return result

